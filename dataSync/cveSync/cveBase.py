import re
import html
import json
import requests
import zipfile
import tempfile
from urllib.parse import unquote
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CVEConfig:
    """Configuration for CVE sync system"""
    # GitHub URLs
    github_base_url: str = "https://api.github.com/repos/CVEProject/cvelistV5"
    github_raw_base: str = "https://raw.githubusercontent.com/CVEProject/cvelistV5/main"
    delta_log_url: str = f"{github_raw_base}/cves/deltaLog.json"
    
    # Model path
    model_path: str = "/Users/ar2024/Projects/rhel_cve_embed/redhat_advisories/model/cve_attackbert_lora_contrastive"
    
    # Database configs
    elasticsearch_host: str = "localhost:9200"
    elasticsearch_index: str = "cve_data"
    sqlite_db_path: str = "db.sqlite3"
    
    # Sync settings
    batch_size: int = 100
    start_year: int = 2025

class CVEEmbeddingModel:
    """Wrapper for the sentence transformer model"""
    
    def __init__(self, model_path: str):
        try:
            self.model = SentenceTransformer(model_path)
            logger.info(f"Loaded embedding model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            # Fallback to a default model
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.warning("Using fallback model: all-MiniLM-L6-v2")
    
    def encode(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            return []

class CVEParser:
    """Parse CVE JSON data"""
    
    @staticmethod
    def parse_cpe(cpe_uri: str) -> Dict[str, str]:
        """Parse a CPE 2.3 URI and return a dictionary of components."""
        parts = cpe_uri.split(":")
        if len(parts) >= 7:
            return {
                "type": parts[2],
                "vendor": unquote(parts[3]),
                "product": unquote(parts[4]),
                "version": unquote(parts[5])
            }
        return {}
    
    @staticmethod
    def extract_cve_data(json_data: Dict[str, Any], embed_model: CVEEmbeddingModel) -> Dict[str, Any]:
        """Extract and process CVE data from JSON"""
        try:
            cve_id = json_data.get("cveMetadata", {}).get("cveId", "")
            containers = json_data.get("containers", {})
            cna = containers.get("cna", {})

            # Check if CVE is rejected
            state = json_data.get("cveMetadata", {}).get("state", "").upper()
            if state == "REJECTED":
                return {"state": state, "id": cve_id}

            # Description
            description = next(
                (d.get("value") for d in cna.get("descriptions", []) if d.get("lang") == "en"),
                ""
            )
            description = html.unescape(description.strip())

            # CVSS metrics
            metrics = cna.get("metrics", [])
            cvss = {}
            for m in metrics:
                if "cvssV3_1" in m:
                    cvss = m["cvssV3_1"]
                    break

            # CWE
            cwes = []
            for pt in cna.get("problemTypes", []):
                for desc in pt.get("descriptions", []):
                    if desc.get("lang") == "en":
                        cwes.append({
                            "id": desc.get("cweId"),
                            "description": desc.get("description")
                        })

            # Affected packages
            affected_packages = []
            pkgs = []
            description_extended = description
            
            for a in cna.get("affected", []):
                vendor = a.get("vendor", "")
                product = a.get("product", "")
                version_info = a.get("versions", [])
                default_status = a.get('defaultStatus', '')
                
                for v in version_info:
                    pkg = {
                        "vendor": vendor,
                        "product": product,
                        "version": v.get("version"),
                        "lessThanOrEqual": v.get("lessThanOrEqual"),
                        "lessThan": v.get("lessThan"),
                        "version_type": v.get("versionType"),
                        "status": v.get("status", default_status)
                    }
                    
                    # Add CPE info if available
                    for cpe_entry in a.get("cpe", []):
                        cpe_data = CVEParser.parse_cpe(cpe_entry.get("cpe23Uri", ""))
                        pkg.update(cpe_data)
                    
                    affected_packages.append(pkg)
                
                # Extended description with package info
                package_name = a.get('packageName', '')
                version_constraint = ""
                if v.get('lessThanOrEqual'):
                    version_constraint = f"lessThanOrEqual {v.get('version')}"
                elif v.get('lessThan'):
                    version_constraint = f"lessThan {v.get('version')}"
                
                description_extended += f"\n==> {v.get('status', default_status)} {product} {package_name} {version_constraint}"
                if package_name:
                    pkgs.append(package_name)

            # Fix versions
            fix_versions = sorted(
                {f"> {pkg['lessThanOrEqual']}" for pkg in affected_packages if pkg.get("lessThanOrEqual")}
            )
            fix_version = fix_versions[0] if fix_versions else None

            # References
            references = [r.get("url") for r in cna.get("references", []) if "url" in r]

            # Timeline
            timeline = [
                {"date": t["time"], "event": t["value"]}
                for t in cna.get("timeline", []) if "time" in t and "value" in t
            ]

            # Credits
            credits = [c.get("value") for c in cna.get("credits", []) if c.get("lang") == "en"]

            # SSVC (CISA enrichment)
            ssvc_data = {}
            for adp in containers.get("adp", []):
                for metric in adp.get("metrics", []):
                    if "other" in metric and metric["other"].get("type") == "ssvc":
                        content = metric["other"].get("content", {})
                        ssvc_data = {
                            "role": content.get("role"),
                            "version": content.get("version"),
                            "exploitStatus": content.get("exploitStatus")
                        }
                        for opt in content.get("options", []):
                            ssvc_data.update(opt)
                        break

            # Generate embeddings
            text_vector = embed_model.encode(description_extended)
            package_vector = embed_model.encode(str(pkgs)) if pkgs else []

            return {
                "id": cve_id,
                "text": description_extended,
                "vector": text_vector,
                "package_vector": package_vector,
                "fulltext": json_data,
                "state": state,
                "metadata": {
                    "title": cna.get("title", ""),
                    "published_date": json_data.get("cveMetadata", {}).get("datePublished", ""),
                    "last_updated": json_data.get("cveMetadata", {}).get("dateUpdated", ""),
                    "cvss_score": cvss.get("baseScore"),
                    "cvss_vector": cvss.get("vectorString"),
                    "severity": cvss.get("baseSeverity"),
                    "cwe": cwes,
                    "affected_packages": affected_packages,
                    "fix_version": fix_version,
                    "references": references,
                    "timeline": timeline,
                    "credits": credits,
                    "assigner": json_data.get("cveMetadata", {}).get("assignerShortName"),
                    "ssvc": ssvc_data
                },
                "sources": references
            }

        except Exception as e:
            logger.error(f"Failed to parse CVE JSON: {e}")
            return {}

class GitHubCVEClient:
    """Client for downloading CVE data from GitHub"""
    
    def __init__(self, config: CVEConfig):
        self.config = config
        self.session = requests.Session()
    
    def download_year_archive(self, year: int, temp_dir: Path) -> Path:
        """Download and extract CVE data for a specific year"""
        archive_url = f"https://github.com/CVEProject/cvelistV5/archive/refs/heads/main.zip"
        
        logger.info(f"Downloading CVE archive from GitHub...")
        response = self.session.get(archive_url, stream=True)
        response.raise_for_status()
        
        # Save and extract archive
        archive_path = temp_dir / "cvelistV5.zip"
        with open(archive_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Return path to the extracted year directory
        extracted_path = temp_dir / "cvelistV5-main" / "cves" / str(year)
        if extracted_path.exists():
            return extracted_path
        else:
            raise FileNotFoundError(f"Year {year} directory not found in archive")
    
    def get_delta_log(self) -> Dict[str, Any]:
        """Fetch the delta log from GitHub"""
        try:
            response = self.session.get(self.config.delta_log_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch delta log: {e}")
            return {}
    
    def download_single_cve(self, cve_path: str) -> Optional[Dict[str, Any]]:
        """Download a single CVE file from GitHub"""
        try:
            url = f"{self.config.github_raw_base}/cves/{cve_path}"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to download CVE {cve_path}: {e}")
            return None

class CVEStorageInterface:
    """Abstract interface for CVE storage backends"""
    
    def upsert_cve(self, cve_data: Dict[str, Any]) -> bool:
        """Insert or update CVE data. Returns success/failure"""
        raise NotImplementedError
    
    def bulk_upsert_cves(self, cve_batch: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Bulk insert/update CVE data. Returns (success_count, failed_count)"""
        raise NotImplementedError
    
    def get_max_updated_timestamp(self) -> Optional[str]:
        """Get the maximum last_updated timestamp"""
        raise NotImplementedError
    
    def initialize_storage(self):
        """Initialize storage backend"""
        raise NotImplementedError
    
    def close(self):
        """Close storage connections"""
        pass