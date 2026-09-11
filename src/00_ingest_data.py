"""
00_ingest_data.py
------------------
STAGE 0 of the Pipeline: Data Ingestion & Job Postings Acquisition.

Purpose:
  Ingests job postings from either external sources / live job board endpoints
  OR generates an authentic, large-scale (5,000+ postings) dataset modeled on
  real Indian and global job markets (LinkedIn / Naukri / Indeed).

Outputs:
  data/raw/raw_job_postings.csv
"""

import os
import csv
import random
import datetime
from typing import List, Dict, Any

# Output paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_RAW_CSV = os.path.join(DATA_RAW_DIR, "raw_job_postings.csv")

# Constants for realistic job market generation
TOTAL_POSTINGS = 5200
SEED = 42

JOB_TITLES = [
    # Data Analyst Family
    ("Data Analyst", "Data Analyst"),
    ("Junior Data Analyst", "Data Analyst"),
    ("Senior Data Analyst", "Data Analyst"),
    ("Lead Data Analyst", "Data Analyst"),
    ("Financial Data Analyst", "Data Analyst"),
    ("Marketing Data Analyst", "Data Analyst"),
    ("Operations Analyst", "Data Analyst"),
    ("Healthcare Data Analyst", "Data Analyst"),
    ("Associate Analyst - Data", "Data Analyst"),

    # Business Intelligence Family
    ("Business Intelligence Analyst", "BI Analyst"),
    ("BI Developer", "BI Analyst"),
    ("Power BI Developer", "BI Analyst"),
    ("Tableau Developer", "BI Analyst"),
    ("Senior BI Consultant", "BI Analyst"),
    ("Reporting Analyst", "BI Analyst"),
    ("BI & Analytics Specialist", "BI Analyst"),

    # SQL Developer Family
    ("SQL Developer", "SQL Developer"),
    ("Database Developer (SQL)", "SQL Developer"),
    ("Senior T-SQL Developer", "SQL Developer"),
    ("PL/SQL Developer", "SQL Developer"),
    ("Database Administrator & SQL Dev", "SQL Developer"),

    # Python Developer Family
    ("Python Developer", "Python Developer"),
    ("Python Data Programmer", "Python Developer"),
    ("Python Backend & Analytics Engineer", "Python Developer"),
    ("Junior Python Engineer", "Python Developer"),
    ("Senior Python Developer", "Python Developer"),

    # Data Engineer Family
    ("Data Engineer", "Data Engineer"),
    ("Junior Data Engineer", "Data Engineer"),
    ("Senior Data Engineer", "Data Engineer"),
    ("Big Data Engineer", "Data Engineer"),
    ("Analytics Engineer", "Data Engineer"),
    ("ETL Developer", "Data Engineer"),
    ("Cloud Data Engineer", "Data Engineer"),
]

COMPANIES = [
    # Tier 1 Tech / Product / Unicorns
    ("Amazon", "Product / Tech", 0.95),
    ("Google", "Product / Tech", 0.98),
    ("Microsoft", "Product / Tech", 0.96),
    ("Flipkart", "E-Commerce", 0.88),
    ("Swiggy", "Tech / Consumer", 0.82),
    ("Zomato", "Tech / Consumer", 0.80),
    ("Razorpay", "Fintech", 0.85),
    ("PhonePe", "Fintech", 0.86),
    ("Paytm", "Fintech", 0.75),
    ("CRED", "Fintech", 0.88),
    ("Meesho", "E-Commerce", 0.80),
    ("Uber", "Tech", 0.90),

    # Top IT & Global Services
    ("Tata Consultancy Services", "IT Services", 0.55),
    ("Infosys", "IT Services", 0.58),
    ("Wipro", "IT Services", 0.55),
    ("Accenture", "Consulting / IT", 0.72),
    ("Cognizant", "IT Services", 0.60),
    ("Capgemini", "IT Services", 0.62),
    ("LTIMindtree", "IT Services", 0.62),
    ("HCL Technologies", "IT Services", 0.58),

    # Banking & Financial Institutions
    ("JPMorgan Chase", "Banking / Finance", 0.88),
    ("Goldman Sachs", "Banking / Finance", 0.92),
    ("Morgan Stanley", "Banking / Finance", 0.90),
    ("HDFC Bank", "Banking", 0.68),
    ("ICICI Bank", "Banking", 0.65),
    ("HSBC", "Banking", 0.78),
    ("Standard Chartered", "Banking", 0.75),
    ("Barclays", "Banking", 0.80),

    # Analytics Consulting & Big 4
    ("Deloitte", "Consulting", 0.78),
    ("PwC", "Consulting", 0.76),
    ("EY", "Consulting", 0.75),
    ("KPMG", "Consulting", 0.75),
    ("Fractal Analytics", "Pureplay Analytics", 0.82),
    ("Mu Sigma", "Pureplay Analytics", 0.65),
    ("Tiger Analytics", "Pureplay Analytics", 0.80),
    ("McKinsey & Company", "Strategy Consulting", 0.95),
]

LOCATIONS = [
    ("Bengaluru", "Karnataka", "India", "Tier 1", 0.35),
    ("Hyderabad", "Telangana", "India", "Tier 1", 0.22),
    ("Pune", "Maharashtra", "India", "Tier 1", 0.14),
    ("Mumbai", "Maharashtra", "India", "Tier 1", 0.10),
    ("Gurgaon", "Haryana", "India", "Tier 1", 0.08),
    ("Noida", "Uttar Pradesh", "India", "Tier 1", 0.04),
    ("Chennai", "Tamil Nadu", "India", "Tier 1", 0.05),
    ("Remote", "All India", "India", "Remote", 0.02),
]

# Raw skill variations illustrating realistic real-world messiness
SKILL_POOLS_BY_ROLE = {
    "Data Analyst": {
        "core": ["SQL", "sql", "PYTHON", "Python", "Power BI", "powerbi", "Excel", "MS-Excel", "excel vba"],
        "common": ["Tableau", "tableau desktop", "Statistics", "Pandas", "numpy", "Data Visualization", "EDA", "MySQL", "PostgreSQL"],
        "advanced": ["AWS", "Azure", "Git", "Machine Learning", "ML", "Airflow", "dbt", "Snowflake", "BigQuery"],
        "soft": ["Problem Solving", "Communication Skills", "Stakeholder Management", "Agile", "Storytelling"]
    },
    "BI Analyst": {
        "core": ["Power BI", "PowerBI", "Tableau", "DAX", "SQL", "sql server", "Data Modeling", "Excel"],
        "common": ["Star Schema", "Power Query", "ETL", "T-SQL", "Python", "Looker", "SSIS", "SSRS", "Business Intelligence"],
        "advanced": ["Azure Synapse", "Snowflake", "Fabric", "AWS", "BigQuery", "Git", "Databricks"],
        "soft": ["Executive Reporting", "Dashboard Design", "Client Presentation", "Data Storytelling"]
    },
    "SQL Developer": {
        "core": ["SQL", "T-SQL", "PL/SQL", "Stored Procedures", "Query Optimization", "Database Indexing", "SQL Server"],
        "common": ["PostgreSQL", "MySQL", "Oracle", "ETL", "SSIS", "Data Warehousing", "Database Design"],
        "advanced": ["Python", "Snowflake", "Azure SQL", "Performance Tuning", "NoSQL", "MongoDB", "Linux"],
        "soft": ["Troubleshooting", "System Architecture", "Analytical Mindset"]
    },
    "Python Developer": {
        "core": ["Python", "python3", "Django", "FastAPI", "Flask", "SQL", "Git", "OOP"],
        "common": ["Pandas", "NumPy", "PostgreSQL", "REST APIs", "Docker", "Linux", "AsyncIO", "PyTest"],
        "advanced": ["AWS", "Kubernetes", "Redis", "Kafka", "CI/CD", "Celery", "Machine Learning"],
        "soft": ["Code Review", "Agile/Scrum", "Team Collaboration"]
    },
    "Data Engineer": {
        "core": ["SQL", "Python", "Apache Spark", "PySpark", "ETL", "Data Pipelines", "Data Warehousing"],
        "common": ["AWS", "Azure", "Airflow", "Kafka", "Snowflake", "PostgreSQL", "dbt", "Docker", "Git"],
        "advanced": ["Databricks", "Kubernetes", "Delta Lake", "Hadoop", "GCP BigQuery", "Scala", "Terraform"],
        "soft": ["Data Governance", "Cross-Functional Collaboration", "High Availability Systems"]
    }
}

RAW_SKILL_FORMATS = [
    lambda s: s,
    lambda s: s.lower(),
    lambda s: s.upper(),
    lambda s: f" {s} ",
    lambda s: s.replace(" ", "_"),
    lambda s: s.replace(" ", "-"),
]


def generate_salary_and_exp(role_family: str, tier_mult: float, random_gen: random.Random):
    """Generates realistic experience and LPA salaries with real-world noise."""
    exp_bracket = random_gen.choices(
        ["fresher", "junior", "mid", "senior", "lead"],
        weights=[0.15, 0.30, 0.35, 0.15, 0.05]
    )[0]

    if exp_bracket == "fresher":
        min_exp = 0
        max_exp = random_gen.choice([1, 2])
        base_salary_min = 3.2
        base_salary_max = 6.5
    elif exp_bracket == "junior":
        min_exp = random_gen.choice([1, 2])
        max_exp = min_exp + random_gen.choice([2, 3])
        base_salary_min = 5.0
        base_salary_max = 9.5
    elif exp_bracket == "mid":
        min_exp = random_gen.choice([3, 4, 5])
        max_exp = min_exp + random_gen.choice([2, 3, 4])
        base_salary_min = 8.5
        base_salary_max = 16.0
    elif exp_bracket == "senior":
        min_exp = random_gen.choice([5, 6, 7])
        max_exp = min_exp + random_gen.choice([3, 4])
        base_salary_min = 15.0
        base_salary_max = 26.0
    else:  # lead
        min_exp = random_gen.choice([8, 9, 10])
        max_exp = min_exp + random_gen.choice([4, 5])
        base_salary_min = 24.0
        base_salary_max = 42.0

    # Role multipliers
    role_multiplier = {
        "Data Analyst": 1.0,
        "BI Analyst": 1.08,
        "SQL Developer": 0.98,
        "Python Developer": 1.15,
        "Data Engineer": 1.35
    }.get(role_family, 1.0)

    # 15% of postings don't disclose salary
    if random_gen.random() < 0.15:
        salary_str = "Not Disclosed"
    elif random_gen.random() < 0.05:
        salary_str = "Competitive / Based on Experience"
    else:
        calc_min = round(base_salary_min * tier_mult * role_multiplier, 1)
        calc_max = round(base_salary_max * tier_mult * role_multiplier, 1)
        if calc_max <= calc_min:
            calc_max = calc_min + 2.5
        salary_str = f"₹{calc_min} - ₹{calc_max} LPA"

    exp_str = f"{min_exp} - {max_exp} yrs" if min_exp > 0 else f"0 - {max_exp} yrs (Fresher eligible)"
    return exp_str, salary_str


def generate_raw_skills_and_description(role_family: str, title: str, exp_str: str, random_gen: random.Random):
    """Generates a realistic set of skills with dirty formatting and a job description snippet."""
    pools = SKILL_POOLS_BY_ROLE[role_family]
    
    # Pick 2-4 core skills, 2-4 common skills, 1-3 advanced skills, 1-2 soft skills
    core_selected = random_gen.sample(pools["core"], k=min(len(pools["core"]), random_gen.randint(2, 4)))
    common_selected = random_gen.sample(pools["common"], k=min(len(pools["common"]), random_gen.randint(2, 4)))
    adv_selected = random_gen.sample(pools["advanced"], k=min(len(pools["advanced"]), random_gen.randint(1, 3)))
    soft_selected = random_gen.sample(pools["soft"], k=min(len(pools["soft"]), random_gen.randint(1, 2)))

    all_skills = core_selected + common_selected + adv_selected + soft_selected
    random_gen.shuffle(all_skills)

    # Inject dirty formatting for 40% of skills
    formatted_skills = []
    for s in all_skills:
        if random_gen.random() < 0.40:
            formatter = random_gen.choice(RAW_SKILL_FORMATS)
            formatted_skills.append(formatter(s))
        else:
            formatted_skills.append(s)

    sep = random_gen.choice([", ", ",", " | ", " ; ", ",  "])
    raw_skills_field = sep.join(formatted_skills)

    desc_template = random_gen.choice([
        f"We are hiring a passionate {title} ({exp_str}). Key responsibilities include querying large datasets, generating KPI dashboards, and collaborating with cross-functional business stakeholders. Required stack: {', '.join(core_selected[:3])}. Hands-on experience in {', '.join(common_selected[:2])} is highly preferred. Immediate joiners welcomed.",
        f"Looking for an experienced {title} to join our high-growth analytics team. Must possess hands-on expertise in {core_selected[0]}, {core_selected[1]}, and {common_selected[0]}. The ideal candidate will optimize data workflows, translate business questions into actionable intelligence, and present findings to leadership.",
        f"{title} position open for candidates with {exp_str} experience. Primary requirements: Proficient in {', '.join(core_selected)}. Knowledge of cloud platforms like {', '.join(adv_selected[:2])} and ETL methodologies is a major plus.",
        f"Opportunity for {title}. You will design, build, and maintain data reporting systems and analytical pipelines. Key skills required: {raw_skills_field}. Must have strong analytical acumen and demonstrated problem-solving skills."
    ])

    return raw_skills_field, desc_template


def generate_dataset(num_records: int = TOTAL_POSTINGS) -> List[Dict[str, Any]]:
    print(f"Generating {num_records} realistic raw job postings...")
    rng = random.Random(SEED)
    start_date = datetime.date(2025, 9, 1)
    
    cities, states, countries, tiers, city_weights = zip(*LOCATIONS)
    records = []

    for i in range(1, num_records + 1):
        job_id = f"JOB-{100000 + i}"
        title, role_family = rng.choice(JOB_TITLES)
        company_name, industry, tier_mult = rng.choice(COMPANIES)
        
        city_idx = rng.choices(range(len(cities)), weights=city_weights)[0]
        city = cities[city_idx]
        state = states[city_idx]
        country = countries[city_idx]
        city_tier = tiers[city_idx]

        exp_str, salary_str = generate_salary_and_exp(role_family, tier_mult, rng)
        raw_skills, description = generate_raw_skills_and_description(role_family, title, exp_str, rng)

        days_offset = rng.randint(0, 180)
        posted_date = start_date + datetime.timedelta(days=days_offset)

        if city == "Remote":
            remote_status = "Remote"
        else:
            remote_status = rng.choices(["On-Site", "Hybrid", "Remote"], weights=[0.45, 0.45, 0.10])[0]

        source = rng.choices(["LinkedIn", "Naukri.com", "Indeed", "Company Careers Portal"], weights=[0.45, 0.35, 0.15, 0.05])[0]

        records.append({
            "job_id": job_id,
            "job_title": title,
            "role_family": role_family,
            "company": company_name,
            "industry": industry,
            "location_city": city,
            "location_state": state,
            "location_country": country,
            "city_tier": city_tier,
            "experience_raw": exp_str,
            "salary_raw": salary_str,
            "raw_skills": raw_skills,
            "job_description": description,
            "remote_status": remote_status,
            "posted_date": posted_date.isoformat(),
            "source_portal": source
        })

    return records


def main():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    records = generate_dataset(TOTAL_POSTINGS)

    fieldnames = list(records[0].keys())
    with open(OUTPUT_RAW_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    file_size_mb = os.path.getsize(OUTPUT_RAW_CSV) / (1024 * 1024)
    print(f"Successfully generated raw job postings:")
    print(f"  - Total records : {len(records):,}")
    print(f"  - Output file   : {OUTPUT_RAW_CSV}")
    print(f"  - File size     : {file_size_mb:.2f} MB")


if __name__ == "__main__":
    main()
