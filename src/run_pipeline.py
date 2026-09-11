"""
run_pipeline.py
----------------
Master Orchestrator for the Job Market Skill-Demand Analyzer.

Executes the entire data pipeline sequentially:
  [Stage 0] Data Ingestion / Acquisition
  [Stage 1] Data Cleaning & Skill Normalization
  [Stage 2] Relational SQL Database Loader & Index Builder
  [Stage 3] Power BI Data Model Exporter
"""

import sys
import time
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")

STEPS = [
    ("Stage 0: Ingest & Acquire Job Postings", os.path.join(SRC_DIR, "00_ingest_data.py")),
    ("Stage 1: Clean & Standardize Skill Taxonomy", os.path.join(SRC_DIR, "01_clean_and_extract.py")),
    ("Stage 2: Load Relational SQL Database", os.path.join(SRC_DIR, "02_load_to_sql.py")),
    ("Stage 3: Export Power BI Data Model", os.path.join(SRC_DIR, "03_export_powerbi_data.py")),
]


def print_banner():
    banner = """
================================================================================
          JOB MARKET SKILL-DEMAND ANALYZER: END-TO-END PIPELINE
================================================================================
Pipeline Flow:
  Raw Scraped Postings -> Pandas/Regex Cleaning -> SQLite Star Schema -> Power BI
================================================================================
"""
    print(banner)


def run():
    print_banner()
    total_start = time.time()

    for idx, (step_name, script_path) in enumerate(STEPS, start=1):
        print(f"\n[{idx}/4] STARTING: {step_name}")
        step_start = time.time()

        res = subprocess.run([sys.executable, script_path], capture_output=False)
        if res.returncode != 0:
            print(f"\n[FAILED] {step_name} failed with return code {res.returncode}")
            sys.exit(res.returncode)

        elapsed = time.time() - step_start
        print(f"[{idx}/4] COMPLETED: {step_name} in {elapsed:.2f}s")

    total_time = time.time() - total_start
    print(f"\n{'=' * 80}")
    print(f"PIPELINE EXECUTED SUCCESSFULLY IN {total_time:.2f} SECONDS!")
    print(f"Database   : {os.path.join(BASE_DIR, 'data', 'job_market.db')}")
    print(f"Power BI   : {os.path.join(BASE_DIR, 'powerbi', 'data')}")
    print(f"Dashboard  : {os.path.join(BASE_DIR, 'dashboard', 'index.html')}")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    run()
