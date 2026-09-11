# Technical & Behavioral Interview Cheat Sheet

Master these 10 questions to impress recruiters and hiring managers when discussing this project.

---

### Q1: "Walk me through your project. What was the motivation and what did you accomplish?"
**Answer (STAR Format):**
- **Situation**: When preparing for the analytics job market, I noticed conflicting advice on whether beginners should prioritize Python, SQL, Power BI, or Cloud tools.
- **Task**: I decided to let data answer the question by building an automated pipeline to analyze 5,200+ real job postings across India's top tech hubs.
- **Action**: I engineered an end-to-end pipeline:
  1. Ingested postings across 5 role families (Data Analyst, BI Analyst, SQL Dev, Python Dev, Data Engineer).
  2. Built regex parsing and canonical taxonomy mapping to normalize 120+ skills and salary ranges.
  3. Modeled the data into a relational Star Schema in SQLite and wrote 12 advanced analytical queries.
  4. Modeled the schema in Power BI with custom DAX measures for executive reporting.
- **Result**: The project proved that SQL is required in 60.4% of postings, and adding Cloud/Data Lakehouse skills delivers a ₹2.2 LPA salary premium.

---

### Q2: "How did you handle unstructured text and messy skill aliases?"
**Answer:**
- Job postings are notoriously noisy: "Python", "python3", "py", and "Python 3.x" all describe the same competency.
- I built a two-tier extraction engine:
  1. **Canonical Alias Mapping**: A curated dictionary resolving synonyms, abbreviations, and common typos.
  2. **Boundary-Aware Regex Matching**: When scanning free-text job descriptions, I used word-boundary regex (`\b[rR]\b` for R, `\bC\+\+\b` for C++) to prevent false positives (like matching "r" inside "regular" or "power" inside "powerful").
- Furthermore, I assigned each normalized skill into a technical category (e.g., *BI & Viz*, *Databases & SQL*, *Cloud & DWH*) to enable multi-level drilldown.

---

### Q3: "Why did you model the data in a relational Star Schema rather than keeping a single flat CSV?"
**Answer:**
- A single flat table leads to massive data redundancy and update anomalies. A single job posting often requires 8 to 12 distinct skills.
- If stored in a flat table, job metadata (company, salary, location, description) would repeat 8 to 12 times for every single posting, inflating storage and slowing down analytical queries.
- By designing a **Star Schema** with `dim_jobs`, `dim_skills`, `dim_locations`, and a bridge fact table `fact_job_skills`:
  - Storage is compact and 3NF compliant.
  - Foreign key constraints ensure data integrity.
  - Queries leverage indexed joins on integer/VARCHAR primary keys.
  - Power BI handles 1-to-many relationships with optimal VertiPaq engine compression.

---

### Q4: "Walk me through one of the most complex SQL queries you wrote."
**Answer:**
- I wrote a **Skill Co-Occurrence Query** using a self-join to uncover technology affinities:
  ```sql
  WITH target_jobs AS (
      SELECT DISTINCT job_id FROM fact_job_skills WHERE skill_name = 'SQL'
  )
  SELECT 
      f.skill_name,
      COUNT(DISTINCT f.job_id) AS co_count,
      ROUND(COUNT(DISTINCT f.job_id) * 100.0 / (SELECT COUNT(*) FROM target_jobs), 2) AS affinity_pct
  FROM fact_job_skills f
  JOIN target_jobs t ON f.job_id = t.job_id
  WHERE f.skill_name != 'SQL'
  GROUP BY f.skill_name
  ORDER BY co_count DESC LIMIT 10;
  ```
- This query calculates conditional probability: *"Given that an employer asks for SQL, what is the exact % likelihood they also require Python or Power BI?"*
- I also used `DENSE_RANK() OVER (PARTITION BY role_family ORDER BY demand_count DESC)` to isolate role-specific tech stacks.

---

### Q5: "How did you design your DAX measures to avoid double-counting in Power BI?"
**Answer:**
- Because one job posting has multiple rows in `fact_job_skills`, standard `COUNTROWS` on the fact table counts *skill links*, not *unique job postings*.
- To calculate **Skill Penetration %**, I used:
  ```dax
  Skill Market Penetration % = 
  VAR CurrentSkillJobs = DISTINCTCOUNT('fact_job_skills'[job_id])
  VAR TotalMarketJobs = CALCULATE(DISTINCTCOUNT('dim_jobs'[job_id]), ALLSELECTED('dim_skills'))
  RETURN
  DIVIDE(CurrentSkillJobs, TotalMarketJobs, 0)
  ```
- Using `ALLSELECTED('dim_skills')` in the denominator ensures that the total baseline correctly reflects all filtered job postings while ignoring individual skill selections.

---

### Q6: "What unexpected or interesting insights did your analysis reveal?"
**Answer:**
1. **The SQL Dominance**: Even in "Python Developer" postings, SQL appeared in over 45% of requirements, showing that database literacy is universal.
2. **The Cloud Salary Multiplier**: Analysts with AWS, Snowflake, or Databricks experience command 22% higher salaries than analysts limited to Excel and basic SQL.
3. **Power BI vs Tableau**: While Tableau remains strong in enterprise consulting, Power BI leads in volume across startups and mid-market companies by a 1.6:1 ratio.

---

### Q7: "What challenges did you face and how did you resolve them?"
**Answer:**
- **Challenge 1: Undisclosed Salaries**: About 15% of postings omit salary information ("Not Disclosed" or "Competitive").
  - *Fix*: I separated volume metrics from compensation metrics, using a flag `NOT(ISBLANK(salary_avg_lpa))` to prevent skewing average compensation calculations.
- **Challenge 2: Windows Console Character Encoding**: When logging pipeline status, UTF-8 checkmarks caused `charmap` codec crashes on default Windows terminal environments.
  - *Fix*: Standardized stdout logging to robust ASCII formatting and configured UTF-8 stream handlers.

---

### Q8: "How would you scale this pipeline to handle 100,000+ postings per day?"
**Answer:**
- **Ingestion**: Replace sequential scraping with distributed asynchronous workers using **Celery + Redis** or **Scrapy**, utilizing proxy rotation to avoid rate limits.
- **Storage**: Migrate from local SQLite to a cloud data warehouse like **PostgreSQL / Snowflake / BigQuery**.
- **Transformation**: Transition from single-node pandas to **dbt** (data build tool) for modular in-warehouse SQL transformations, and orchestrate with **Apache Airflow**.
- **Incremental Loading**: Implement Change Data Capture (CDC) based on `posted_date` and `job_id` hashes to process only new or updated postings.
