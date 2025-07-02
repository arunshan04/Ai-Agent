import tempfile
from pathlib import Path
from tqdm import tqdm
import json
# cveSyncSqlite.py

# Import your classes
from cveSqlite import SQLiteManager  # Adjust path accordingly
from cveBase import CVEConfig, CVEEmbeddingModel, GitHubCVEClient, CVEParser,logger

def run_full_sync():
    config = CVEConfig()
    model = CVEEmbeddingModel(config.model_path)
    github_client = GitHubCVEClient(config)
    sqlite_db = SQLiteManager(config.sqlite_db_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        year_dir = github_client.download_year_archive(config.start_year, Path(tmpdir))
        cve_files = list(year_dir.glob("**/*.json"))

        logger.info(f"Found {len(cve_files)} CVE JSON files for {config.start_year}")
        batch = []

        for cve_file in tqdm(cve_files, desc="Processing CVEs"):
            try:
                with open(cve_file, "r", encoding="utf-8") as f:
                    cve_json = json.load(f)
                    parsed = CVEParser.extract_cve_data(cve_json, model)
                    if parsed:
                        batch.append(parsed)
            except Exception as e:
                logger.error(f"Failed to process {cve_file}: {e}")
        
        success, failed = sqlite_db.bulk_upsert_cves(batch)
        sqlite_db.log_sync("FULL", "SQLite", success, failed)
        logger.info(f"Sync completed: {success} success, {failed} failed")

if __name__ == "__main__":
    run_full_sync()