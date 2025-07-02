import sqlite3
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from cveBase import CVEConfig, CVEEmbeddingModel, GitHubCVEClient, CVEParser,logger,CVEStorageInterface


logger = logging.getLogger(__name__)

class SQLiteManager(CVEStorageInterface):
    """Manage SQLite database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.initialize_storage()
    
    def initialize_storage(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # CVE summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cve_summary (
                cve_id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                published_date TEXT,
                last_updated TEXT,
                cvss_score REAL,
                severity TEXT,
                state TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Affected packages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS affected_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT,
                vendor TEXT,
                product TEXT,
                version TEXT,
                status TEXT,
                version_constraint TEXT,
                FOREIGN KEY (cve_id) REFERENCES cve_summary (cve_id)
            )
        ''')
        
        # Sync tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sync_type TEXT,
                target_system TEXT,
                last_sync_date TEXT,
                processed_count INTEGER,
                failed_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"SQLite database initialized at {self.db_path}")
    
    def upsert_cve(self, cve_data: Dict[str, Any]) -> bool:
        """Insert or update CVE data in SQLite"""
        if not cve_data or cve_data.get("state") == "REJECTED":
            return True
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            metadata = cve_data.get("metadata", {})
            
            # Upsert CVE summary
            cursor.execute('''
                INSERT OR REPLACE INTO cve_summary 
                (cve_id, title, description, published_date, last_updated, 
                 cvss_score, severity, state, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                cve_data.get("id"),
                metadata.get("title"),
                cve_data.get("text"),
                metadata.get("published_date"),
                metadata.get("last_updated"),
                metadata.get("cvss_score"),
                metadata.get("severity"),
                cve_data.get("state", "PUBLISHED")
            ))
            
            # Delete existing packages for this CVE and insert new ones
            cursor.execute('DELETE FROM affected_packages WHERE cve_id = ?', (cve_data.get("id"),))
            
            for pkg in metadata.get("affected_packages", []):
                version_constraint = ""
                if pkg.get("lessThanOrEqual"):
                    version_constraint = f"<= {pkg.get('lessThanOrEqual')}"
                elif pkg.get("lessThan"):
                    version_constraint = f"< {pkg.get('lessThan')}"
                
                cursor.execute('''
                    INSERT INTO affected_packages 
                    (cve_id, vendor, product, version, status, version_constraint)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    cve_data.get("id"),
                    pkg.get("vendor"),
                    pkg.get("product"),
                    pkg.get("version"),
                    pkg.get("status"),
                    version_constraint
                ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert CVE {cve_data.get('id')}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def bulk_upsert_cves(self, cve_batch: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Bulk insert/update CVE data. Returns (success_count, failed_count)"""
        success_count = 0
        failed_count = 0
        
        for cve_data in cve_batch:
            if self.upsert_cve(cve_data):
                success_count += 1
            else:
                failed_count += 1
        
        return success_count, failed_count
    
    def get_max_updated_timestamp(self) -> Optional[str]:
        """Get the maximum last_updated timestamp from SQLite CVE data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT MAX(last_updated) FROM cve_summary WHERE last_updated IS NOT NULL')
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result and result[0] else None
    
    def log_sync(self, sync_type: str, target_system: str, processed_count: int, failed_count: int):
        """Log sync operation for specific target system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_tracking (sync_type, target_system, last_sync_date, processed_count, failed_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (sync_type, target_system, datetime.now(timezone.utc).isoformat(), processed_count, failed_count))
        
        conn.commit()
        conn.close()
    
    def get_last_sync_date(self, sync_type: str, target_system: str) -> Optional[str]:
        """Get the last successful sync date for a specific target system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT last_sync_date FROM sync_tracking 
            WHERE sync_type = ? AND target_system = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (sync_type, target_system))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_cve_count(self) -> int:
        """Get total count of CVEs in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM cve_summary')
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0
    
    def search_cves(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search CVEs by text query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cve_id, title, description, cvss_score, severity, published_date
            FROM cve_summary 
            WHERE description LIKE ? OR title LIKE ?
            ORDER BY cvss_score DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "cve_id": row[0],
                "title": row[1],
                "description": row[2],
                "cvss_score": row[3],
                "severity": row[4],
                "published_date": row[5]
            })
        
        conn.close()
        return results
    
    def get_cve_by_id(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed CVE information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get CVE summary
        cursor.execute('''
            SELECT * FROM cve_summary WHERE cve_id = ?
        ''', (cve_id,))
        
        cve_row = cursor.fetchone()
        if not cve_row:
            conn.close()
            return None
        
        # Get affected packages
        cursor.execute('''
            SELECT vendor, product, version, status, version_constraint
            FROM affected_packages WHERE cve_id = ?
        ''', (cve_id,))
        
        packages = []
        for pkg_row in cursor.fetchall():
            packages.append({
                "vendor": pkg_row[0],
                "product": pkg_row[1],
                "version": pkg_row[2],
                "status": pkg_row[3],
                "version_constraint": pkg_row[4]
            })
        
        conn.close()
        
        return {
            "cve_id": cve_row[0],
            "title": cve_row[1],
            "description": cve_row[2],
            "published_date": cve_row[3],
            "last_updated": cve_row[4],
            "cvss_score": cve_row[5],
            "severity": cve_row[6],
            "state": cve_row[7],
            "affected_packages": packages
        }
    
    def get_cves_by_product(self, product: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get CVEs affecting a specific product"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT c.cve_id, c.title, c.cvss_score, c.severity, c.published_date
            FROM cve_summary c
            JOIN affected_packages p ON c.cve_id = p.cve_id
            WHERE p.product LIKE ?
            ORDER BY c.cvss_score DESC
            LIMIT ?
        ''', (f'%{product}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "cve_id": row[0],
                "title": row[1],
                "cvss_score": row[2],
                "severity": row[3],
                "published_date": row[4]
            })
        
        conn.close()
        return results
    
    def get_high_severity_cves(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get high severity CVEs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cve_id, title, cvss_score, severity, published_date
            FROM cve_summary 
            WHERE severity IN ('HIGH', 'CRITICAL') AND cvss_score IS NOT NULL
            ORDER BY cvss_score DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "cve_id": row[0],
                "title": row[1],
                "cvss_score": row[2],
                "severity": row[3],
                "published_date": row[4]
            })
        
        conn.close()
        return results
    
    def close(self):
        """Close SQLite connections (no persistent connections to close)"""
        pass