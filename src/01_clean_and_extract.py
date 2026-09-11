"""
01_clean_and_extract.py
-------------------------
STAGE 1 of the Pipeline: Clean & Extract Job Data & Skills.

Input : data/raw/raw_job_postings.csv (and optional data/skill2vec_1K.csv)
Outputs:
  - data/processed/jobs_cleaned.csv
  - data/processed/job_skills_bridge.csv
  - data/processed/dim_skills.csv
  - data/processed/dim_locations.csv

Performs:
  1. Skill name normalization & canonical alias resolution (e.g., "py", "python3" -> "Python").
  2. Skill categorization (BI & Viz, Databases, Programming, Cloud, Big Data, ML/Stats).
  3. Text extraction: Regex pattern matching across raw skills and job descriptions.
  4. Salary parsing: Extracts min, max, and avg salary in LPA (Lakhs Per Annum).
  5. Experience parsing: Extracts min and max years, assigns standard career bracket.
"""

import os
import re
import csv
import pandas as pd
from typing import Tuple, Optional, Set, List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_PROC_DIR = os.path.join(BASE_DIR, "data", "processed")

RAW_INPUT_CSV = os.path.join(DATA_RAW_DIR, "raw_job_postings.csv")
SKILL2VEC_INPUT = os.path.join(BASE_DIR, "data", "skill2vec_1K.csv")

OUTPUT_JOBS_CSV = os.path.join(DATA_PROC_DIR, "jobs_cleaned.csv")
OUTPUT_BRIDGE_CSV = os.path.join(DATA_PROC_DIR, "job_skills_bridge.csv")
OUTPUT_SKILLS_CSV = os.path.join(DATA_PROC_DIR, "dim_skills.csv")
OUTPUT_LOCATIONS_CSV = os.path.join(DATA_PROC_DIR, "dim_locations.csv")

# Standard Skill Alias Map (Extending user's dictionary with comprehensive tech stack)
SKILL_ALIASES = {
    # Programming & Languages
    "py": "Python", "python3": "Python", "python 3": "Python", "python 3.x": "Python",
    "pypy": "Python", "js": "JavaScript", "javascript": "JavaScript", "es6": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "c++": "C++", "cpp": "C++", "golang": "Go", "go lang": "Go",
    "r": "R", "r-lang": "R", "r programming": "R",
    "scala": "Scala", "bash": "Bash/Shell", "shell scripting": "Bash/Shell", "linux": "Linux",

    # Databases & SQL
    "sql": "SQL", "ansi sql": "SQL", "structured query language": "SQL",
    "sql server": "SQL Server", "ms sql": "SQL Server", "mssql": "SQL Server", "ms sql server": "SQL Server",
    "t-sql": "T-SQL", "tsql": "T-SQL",
    "pl/sql": "PL/SQL", "plsql": "PL/SQL", "oracle plsql": "PL/SQL",
    "mysql": "MySQL", "my-sql": "MySQL",
    "postgresql": "PostgreSQL", "postgres": "PostgreSQL", "pgsql": "PostgreSQL",
    "oracle": "Oracle", "oracle db": "Oracle",
    "nosql": "NoSQL", "no-sql": "NoSQL",
    "mongodb": "MongoDB", "mongo": "MongoDB",
    "redis": "Redis", "cassandra": "Cassandra",

    # Business Intelligence & Visualization
    "powerbi": "Power BI", "power-bi": "Power BI", "ms power bi": "Power BI", "microsoft power bi": "Power BI",
    "tableau": "Tableau", "tableau desktop": "Tableau", "tableau server": "Tableau",
    "excel": "Excel", "ms excel": "Excel", "ms-excel": "Excel", "microsoft excel": "Excel",
    "excel vba": "Excel VBA", "vba": "Excel VBA", "advance excel": "Excel", "advanced excel": "Excel",
    "looker": "Looker", "looker studio": "Looker", "google data studio": "Looker",
    "dax": "DAX", "power query": "Power Query", "data modeling": "Data Modeling", "star schema": "Data Modeling",
    "ssis": "SSIS", "ssrs": "SSRS", "ssas": "SSAS",
    "data visualization": "Data Visualization", "dashboard design": "Dashboard Design",

    # Cloud & Modern Data Stack
    "aws": "AWS", "amazon web services": "AWS",
    "azure": "Azure", "az": "Azure", "microsoft azure": "Azure", "ms azure": "Azure",
    "gcp": "Google Cloud", "google cloud platform": "Google Cloud", "google cloud": "Google Cloud",
    "snowflake": "Snowflake", "snow flake": "Snowflake",
    "databricks": "Databricks", "azure databricks": "Databricks",
    "bigquery": "BigQuery", "google bigquery": "BigQuery",
    "synapse": "Azure Synapse", "azure synapse": "Azure Synapse",
    "fabric": "Microsoft Fabric",

    # Big Data & Data Engineering
    "spark": "Apache Spark", "apache spark": "Apache Spark", "pyspark": "PySpark",
    "airflow": "Apache Airflow", "apache airflow": "Apache Airflow",
    "kafka": "Apache Kafka", "apache kafka": "Apache Kafka",
    "dbt": "dbt", "data build tool": "dbt",
    "etl": "ETL", "data pipeline": "Data Pipelines", "data pipelines": "Data Pipelines",
    "data warehousing": "Data Warehousing", "dwh": "Data Warehousing",
    "hadoop": "Hadoop", "hive": "Apache Hive",

    # Data Science & Analytics
    "pandas": "Pandas", "numpy": "NumPy", "scipy": "SciPy",
    "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "machine learning": "Machine Learning", "ml": "Machine Learning",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "nlp": "NLP", "natural language processing": "NLP",
    "statistics": "Statistics", "statistical analysis": "Statistics",
    "eda": "Exploratory Data Analysis", "exploratory data analysis": "Exploratory Data Analysis",
    "a/b testing": "A/B Testing", "hypothesis testing": "A/B Testing",

    # DevOps & Soft Skills
    "git": "Git", "github": "Git", "gitlab": "Git",
    "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "problem solving": "Problem Solving",
    "communication skills": "Communication", "communication": "Communication",
    "stakeholder management": "Stakeholder Management",
    "agile": "Agile/Scrum", "scrum": "Agile/Scrum",
    "storytelling": "Data Storytelling", "data storytelling": "Data Storytelling"
}

# Skill Categorization Dictionary
SKILL_CATEGORY_MAP = {
    # BI & Visualization
    "Power BI": "BI & Visualization",
    "Tableau": "BI & Visualization",
    "Excel": "BI & Visualization",
    "Excel VBA": "BI & Visualization",
    "Looker": "BI & Visualization",
    "DAX": "BI & Visualization",
    "Power Query": "BI & Visualization",
    "Data Modeling": "BI & Visualization",
    "SSIS": "BI & Visualization",
    "SSRS": "BI & Visualization",
    "SSAS": "BI & Visualization",
    "Data Visualization": "BI & Visualization",
    "Dashboard Design": "BI & Visualization",

    # Databases & SQL
    "SQL": "Databases & SQL",
    "SQL Server": "Databases & SQL",
    "T-SQL": "Databases & SQL",
    "PL/SQL": "Databases & SQL",
    "MySQL": "Databases & SQL",
    "PostgreSQL": "Databases & SQL",
    "Oracle": "Databases & SQL",
    "NoSQL": "Databases & SQL",
    "MongoDB": "Databases & SQL",
    "Redis": "Databases & SQL",
    "Cassandra": "Databases & SQL",

    # Programming & Languages
    "Python": "Programming & Languages",
    "R": "Programming & Languages",
    "JavaScript": "Programming & Languages",
    "TypeScript": "Programming & Languages",
    "C++": "Programming & Languages",
    "Go": "Programming & Languages",
    "Scala": "Programming & Languages",
    "Bash/Shell": "Programming & Languages",
    "Linux": "Programming & Languages",

    # Cloud & Modern Data Stack
    "AWS": "Cloud & Data Warehousing",
    "Azure": "Cloud & Data Warehousing",
    "Google Cloud": "Cloud & Data Warehousing",
    "Snowflake": "Cloud & Data Warehousing",
    "Databricks": "Cloud & Data Warehousing",
    "BigQuery": "Cloud & Data Warehousing",
    "Azure Synapse": "Cloud & Data Warehousing",
    "Microsoft Fabric": "Cloud & Data Warehousing",

    # Big Data & Data Engineering
    "Apache Spark": "Big Data & Engineering",
    "PySpark": "Big Data & Engineering",
    "Apache Airflow": "Big Data & Engineering",
    "Apache Kafka": "Big Data & Engineering",
    "dbt": "Big Data & Engineering",
    "ETL": "Big Data & Engineering",
    "Data Pipelines": "Big Data & Engineering",
    "Data Warehousing": "Big Data & Engineering",
    "Hadoop": "Big Data & Engineering",
    "Apache Hive": "Big Data & Engineering",

    # Data Science & Analytics
    "Pandas": "Data Science & Analytics",
    "NumPy": "Data Science & Analytics",
    "SciPy": "Data Science & Analytics",
    "Scikit-Learn": "Data Science & Analytics",
    "Machine Learning": "Data Science & Analytics",
    "Deep Learning": "Data Science & Analytics",
    "NLP": "Data Science & Analytics",
    "Statistics": "Data Science & Analytics",
    "Exploratory Data Analysis": "Data Science & Analytics",
    "A/B Testing": "Data Science & Analytics",

    # DevOps, Tools & Soft Skills
    "Git": "DevOps & Collaboration",
    "Docker": "DevOps & Collaboration",
    "Kubernetes": "DevOps & Collaboration",
    "CI/CD": "DevOps & Collaboration",
    "Problem Solving": "Professional & Soft Skills",
    "Communication": "Professional & Soft Skills",
    "Stakeholder Management": "Professional & Soft Skills",
    "Agile/Scrum": "Professional & Soft Skills",
    "Data Storytelling": "Professional & Soft Skills"
}


def clean_skill_string(raw_skill: str) -> Optional[str]:
    """Cleans a single skill string and resolves it through the alias catalog."""
    if not raw_skill or not isinstance(raw_skill, str):
        return None
    s = raw_skill.strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("_", " ")

    # Check exact alias match
    if s in SKILL_ALIASES:
        return SKILL_ALIASES[s]

    # Special handling for single letters like 'r'
    if s == "r":
        return "R"

    # Title case standard fallback
    standardized = s.title()
    return standardized if len(standardized) >= 2 else None


def parse_salary(salary_raw: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Parses salary strings like '₹5.0 - ₹9.5 LPA' into (min_lpa, max_lpa, avg_lpa).
    Returns (None, None, None) if not disclosed.
    """
    if not salary_raw or not isinstance(salary_raw, str):
        return None, None, None
    if "not disclosed" in salary_raw.lower() or "competitive" in salary_raw.lower():
        return None, None, None

    # Find float or int numbers
    numbers = re.findall(r"(\d+(?:\.\d+)?)", salary_raw)
    if len(numbers) >= 2:
        try:
            val1 = float(numbers[0])
            val2 = float(numbers[1])
            min_sal = min(val1, val2)
            max_sal = max(val1, val2)
            avg_sal = round((min_sal + max_sal) / 2.0, 2)
            return min_sal, max_sal, avg_sal
        except ValueError:
            return None, None, None
    elif len(numbers) == 1:
        try:
            val = float(numbers[0])
            return val, val, val
        except ValueError:
            return None, None, None
    return None, None, None


def parse_experience(exp_raw: str) -> Tuple[int, int, str]:
    """
    Parses experience strings like '1 - 3 yrs' into min_exp, max_exp, and bracket.
    """
    if not exp_raw or not isinstance(exp_raw, str):
        return 0, 2, "Entry / Junior (0-2 yrs)"
    
    numbers = re.findall(r"\b(\d+)\b", exp_raw)
    if len(numbers) >= 2:
        min_e = int(numbers[0])
        max_e = int(numbers[1])
    elif len(numbers) == 1:
        min_e = int(numbers[0])
        max_e = min_e + 2
    else:
        min_e, max_e = 0, 2

    # Categorize into standard career brackets
    if max_e <= 2:
        bracket = "Entry / Junior (0-2 yrs)"
    elif max_e <= 5:
        bracket = "Mid-Level (3-5 yrs)"
    elif max_e <= 9:
        bracket = "Senior (6-9 yrs)"
    else:
        bracket = "Lead / Principal (10+ yrs)"

    return min_e, max_e, bracket


def extract_skills_from_text(raw_skills_str: str, description_str: str) -> Set[str]:
    """
    Extracts and normalizes skills from both explicit raw_skills field and job description.
    """
    skills_found = set()

    # 1. Parse raw_skills field
    if raw_skills_str and isinstance(raw_skills_str, str):
        tokens = re.split(r"[,|;]", raw_skills_str)
        for token in tokens:
            cleaned = clean_skill_string(token)
            if cleaned and len(cleaned) >= 2:
                skills_found.add(cleaned)

    # 2. Text matching in description for key skills
    text = (description_str or "").lower()
    for alias_key, canonical_skill in SKILL_ALIASES.items():
        # Use boundary check to avoid substring confusion (e.g. 'r' inside 'regular')
        pattern = r"\b" + re.escape(alias_key) + r"\b"
        if re.search(pattern, text):
            skills_found.add(canonical_skill)

    return skills_found


def main():
    os.makedirs(DATA_PROC_DIR, exist_ok=True)
    print("STAGE 1: Cleaning & Extracting data...")

    if not os.path.exists(RAW_INPUT_CSV):
        raise FileNotFoundError(f"Missing {RAW_INPUT_CSV}. Run 00_ingest_data.py first.")

    df_raw = pd.read_csv(RAW_INPUT_CSV)
    print(f"Loaded {len(df_raw)} raw job postings from {RAW_INPUT_CSV}")

    cleaned_jobs = []
    job_skills_bridge = []
    all_locations = {}

    for _, row in df_raw.iterrows():
        job_id = str(row["job_id"]).strip()
        title = str(row["job_title"]).strip()
        role_family = str(row["role_family"]).strip()
        company = str(row["company"]).strip()
        industry = str(row["industry"]).strip()
        city = str(row["location_city"]).strip()
        state = str(row["location_state"]).strip()
        country = str(row["location_country"]).strip()
        city_tier = str(row["city_tier"]).strip()
        remote_status = str(row["remote_status"]).strip()
        posted_date = str(row["posted_date"]).strip()
        source_portal = str(row["source_portal"]).strip()

        # Parse salary & experience
        min_sal, max_sal, avg_sal = parse_salary(str(row["salary_raw"]))
        min_exp, max_exp, exp_bracket = parse_experience(str(row["experience_raw"]))

        # Track location
        loc_key = (city, state, country)
        if loc_key not in all_locations:
            all_locations[loc_key] = {
                "city": city,
                "state": state,
                "country": country,
                "city_tier": city_tier,
                "is_tech_hub": 1 if city in ["Bengaluru", "Hyderabad", "Pune", "Mumbai", "Gurgaon"] else 0
            }

        # Extract skills
        skills = extract_skills_from_text(str(row["raw_skills"]), str(row["job_description"]))

        # If a job posting is for Data Analyst or BI and mentions SQL, ensure SQL is included
        if "sql" in title.lower() and "SQL" not in skills:
            skills.add("SQL")
        if "python" in title.lower() and "Python" not in skills:
            skills.add("Python")
        if "power bi" in title.lower() and "Power BI" not in skills:
            skills.add("Power BI")

        # Save to jobs table
        cleaned_jobs.append({
            "job_id": job_id,
            "job_title": title,
            "role_family": role_family,
            "company": company,
            "industry": industry,
            "city": city,
            "state": state,
            "city_tier": city_tier,
            "remote_status": remote_status,
            "min_exp_years": min_exp,
            "max_exp_years": max_exp,
            "exp_level_bracket": exp_bracket,
            "salary_min_lpa": min_sal,
            "salary_max_lpa": max_sal,
            "salary_avg_lpa": avg_sal,
            "posted_date": posted_date,
            "skills_count": len(skills),
            "source_portal": source_portal
        })

        for skill in skills:
            category = SKILL_CATEGORY_MAP.get(skill, "Other Technical Skills")
            job_skills_bridge.append({
                "job_id": job_id,
                "skill_name": skill,
                "skill_category": category
            })

    # Optional: If skill2vec_1K.csv exists, also merge those skill mappings
    if os.path.exists(SKILL2VEC_INPUT):
        print(f"Detected {SKILL2VEC_INPUT}. Merging additional skill2vec data...")
        with open(SKILL2VEC_INPUT, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                s2v_job_id = f"S2V-{row[0].strip()}"
                for raw_s in row[1:]:
                    cleaned_s = clean_skill_string(raw_s)
                    if cleaned_s:
                        cat = SKILL_CATEGORY_MAP.get(cleaned_s, "Other Technical Skills")
                        job_skills_bridge.append({
                            "job_id": s2v_job_id,
                            "skill_name": cleaned_s,
                            "skill_category": cat
                        })

    df_jobs_clean = pd.DataFrame(cleaned_jobs)
    df_bridge = pd.DataFrame(job_skills_bridge).drop_duplicates()

    # Dim Skills
    dim_skills = df_bridge[["skill_name", "skill_category"]].drop_duplicates().reset_index(drop=True)
    dim_skills["skill_id"] = [f"SKILL-{i+1:04d}" for i in range(len(dim_skills))]
    dim_skills = dim_skills[["skill_id", "skill_name", "skill_category"]]

    # Merge skill_id back into bridge
    df_bridge = df_bridge.merge(dim_skills[["skill_id", "skill_name"]], on="skill_name", how="left")

    # Dim Locations
    df_locations = pd.DataFrame(list(all_locations.values())).drop_duplicates().reset_index(drop=True)
    df_locations["location_id"] = [f"LOC-{i+1:03d}" for i in range(len(df_locations))]

    # Save to CSV
    df_jobs_clean.to_csv(OUTPUT_JOBS_CSV, index=False)
    df_bridge.to_csv(OUTPUT_BRIDGE_CSV, index=False)
    dim_skills.to_csv(OUTPUT_SKILLS_CSV, index=False)
    df_locations.to_csv(OUTPUT_LOCATIONS_CSV, index=False)

    print("\nSTAGE 1 COMPLETE:")
    print(f"  - Cleaned Job Postings    : {len(df_jobs_clean):,} rows -> {OUTPUT_JOBS_CSV}")
    print(f"  - Unique Jobs with Skills : {df_bridge['job_id'].nunique():,}")
    print(f"  - Unique Standard Skills  : {dim_skills['skill_name'].nunique():,} -> {OUTPUT_SKILLS_CSV}")
    print(f"  - Total Job-Skill Links   : {len(df_bridge):,} rows -> {OUTPUT_BRIDGE_CSV}")
    print(f"  - Unique Locations        : {len(df_locations)} -> {OUTPUT_LOCATIONS_CSV}")


if __name__ == "__main__":
    main()
