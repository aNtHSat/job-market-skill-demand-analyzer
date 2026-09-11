"""
02_load_to_sql.py
-------------------
STAGE 2 of the Pipeline: Relational Database Loader & Star Schema Indexer.

Inputs:
  - sql/01_schema_ddl.sql
  - data/processed/dim_locations.csv
  - data/processed/dim_skills.csv
  - data/processed/jobs_cleaned.csv
  - data/processed/job_skills_bridge.csv

Output:
  - data/job_market.db (SQLite database)
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PROC_DIR = os.path.join(DATA_DIR, "processed")
SQL_DIR = os.path.join(BASE_DIR, "sql")

DDL_FILE = os.path.join(SQL_DIR, "01_schema_ddl.sql")
DB_FILE = os.path.join(DATA_DIR, "job_market.db")

JOBS_CSV = os.path.join(DATA_PROC_DIR, "jobs_cleaned.csv")
SKILLS_CSV = os.path.join(DATA_PROC_DIR, "dim_skills.csv")
BRIDGE_CSV = os.path.join(DATA_PROC_DIR, "job_skills_bridge.csv")
LOCATIONS_CSV = os.path.join(DATA_PROC_DIR, "dim_locations.csv")


def load_database():
    print("STAGE 2: Loading cleaned data into Relational SQL Database...")

    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Execute DDL script
    print(f"Applying schema DDL from {DDL_FILE}...")
    with open(DDL_FILE, "r", encoding="utf-8") as f:
        ddl_script = f.read()
    cursor.executescript(ddl_script)

    # 2. Load dim_locations
    df_loc = pd.read_csv(LOCATIONS_CSV)
    df_loc.to_sql("dim_locations", conn, if_exists="append", index=False)
    print(f"  [OK] Loaded dim_locations: {len(df_loc)} records")

    # 3. Load dim_skills
    df_skills = pd.read_csv(SKILLS_CSV)
    df_skills.to_sql("dim_skills", conn, if_exists="append", index=False)
    print(f"  [OK] Loaded dim_skills   : {len(df_skills)} records")

    # 4. Load dim_jobs
    df_jobs = pd.read_csv(JOBS_CSV)
    # Select columns matching dim_jobs DDL
    job_columns = [
        "job_id", "job_title", "role_family", "company", "industry",
        "city", "state", "city_tier", "remote_status",
        "min_exp_years", "max_exp_years", "exp_level_bracket",
        "salary_min_lpa", "salary_max_lpa", "salary_avg_lpa",
        "posted_date", "skills_count", "source_portal"
    ]
    df_jobs[job_columns].to_sql("dim_jobs", conn, if_exists="append", index=False)
    print(f"  [OK] Loaded dim_jobs     : {len(df_jobs)} records")

    # 5. Load fact_job_skills
    df_bridge = pd.read_csv(BRIDGE_CSV)
    bridge_columns = ["job_id", "skill_id", "skill_name", "skill_category"]
    df_bridge[bridge_columns].to_sql("fact_job_skills", conn, if_exists="append", index=False)
    print(f"  [OK] Loaded fact_job_skills: {len(df_bridge)} records")

    conn.commit()

    # Integrity verification
    cursor.execute("SELECT COUNT(*) FROM dim_jobs;")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT skill_name) FROM fact_job_skills;")
    unique_skills_used = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM fact_job_skills;")
    total_links = cursor.fetchone()[0]

    print("\nDATABASE INTEGRITY CHECK:")
    print(f"  - Database path        : {DB_FILE}")
    print(f"  - Total Jobs Stored    : {total_jobs:,}")
    print(f"  - Total Skills Mapped  : {unique_skills_used:,}")
    print(f"  - Total Skill Links    : {total_links:,}")
    
    db_size_mb = os.path.getsize(DB_FILE) / (1024 * 1024)
    print(f"  - Database File Size   : {db_size_mb:.2f} MB")

    conn.close()


if __name__ == "__main__":
    load_database()
