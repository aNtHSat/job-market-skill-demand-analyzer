"""
03_export_powerbi_data.py
--------------------------
STAGE 3 of the Pipeline: Export Data Model for Power BI.

Outputs:
  - powerbi/data/dim_jobs.csv
  - powerbi/data/dim_skills.csv
  - powerbi/data/dim_locations.csv
  - powerbi/data/fact_job_skills.csv
  - powerbi/data/powerbi_flat_reporting_view.csv
  - powerbi/data/skill_co_occurrence_matrix.csv

Provides both:
  1. Star Schema Tables for robust relational modeling in Power BI.
  2. A flat reporting view for rapid drag-and-drop report prototyping.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "job_market.db")
PBI_DATA_DIR = os.path.join(BASE_DIR, "powerbi", "data")


def export_powerbi_files():
    print("STAGE 3: Exporting Data Model for Power BI Desktop...")
    os.makedirs(PBI_DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)

    # 1. Export Star Schema Dimensions & Fact
    tables = ["dim_jobs", "dim_skills", "dim_locations", "fact_job_skills"]
    for tbl in tables:
        df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
        out_csv = os.path.join(PBI_DATA_DIR, f"{tbl}.csv")
        df.to_csv(out_csv, index=False)
        print(f"  [OK] Exported {tbl}: {len(df):,} rows -> {out_csv}")

    # 2. Export Flat Reporting View (Denormalized fact + dims for simple dashboards)
    flat_query = """
    SELECT 
        j.job_id,
        j.job_title,
        j.role_family,
        j.company,
        j.industry,
        j.city,
        j.state,
        j.city_tier,
        l.is_tech_hub,
        j.remote_status,
        j.min_exp_years,
        j.max_exp_years,
        j.exp_level_bracket,
        j.salary_min_lpa,
        j.salary_max_lpa,
        j.salary_avg_lpa,
        j.posted_date,
        j.skills_count,
        j.source_portal,
        f.skill_id,
        f.skill_name,
        f.skill_category
    FROM dim_jobs j
    LEFT JOIN dim_locations l ON j.city = l.city
    INNER JOIN fact_job_skills f ON j.job_id = f.job_id;
    """
    df_flat = pd.read_sql_query(flat_query, conn)
    flat_out = os.path.join(PBI_DATA_DIR, "powerbi_flat_reporting_view.csv")
    df_flat.to_csv(flat_out, index=False)
    print(f"  [OK] Exported flat reporting view: {len(df_flat):,} rows -> {flat_out}")

    # 3. Export Co-occurrence Matrix
    co_occur_query = """
    SELECT 
        f1.skill_name AS primary_skill,
        f2.skill_name AS paired_skill,
        COUNT(DISTINCT f1.job_id) AS pair_frequency
    FROM fact_job_skills f1
    JOIN fact_job_skills f2 ON f1.job_id = f2.job_id
    WHERE f1.skill_name < f2.skill_name
      AND f1.skill_name IN ('SQL', 'Python', 'Power BI', 'Tableau', 'Excel', 'AWS', 'Azure', 'Apache Spark', 'Machine Learning', 'dbt', 'Snowflake')
      AND f2.skill_name IN ('SQL', 'Python', 'Power BI', 'Tableau', 'Excel', 'AWS', 'Azure', 'Apache Spark', 'Machine Learning', 'dbt', 'Snowflake')
    GROUP BY f1.skill_name, f2.skill_name
    ORDER BY pair_frequency DESC;
    """
    df_co = pd.read_sql_query(co_occur_query, conn)
    co_out = os.path.join(PBI_DATA_DIR, "skill_co_occurrence_matrix.csv")
    df_co.to_csv(co_out, index=False)
    print(f"  [OK] Exported co-occurrence matrix: {len(df_co)} pairs -> {co_out}")

    conn.close()
    print("\nSTAGE 3 COMPLETE: All Power BI datasets are ready for visualization.")


if __name__ == "__main__":
    export_powerbi_files()
