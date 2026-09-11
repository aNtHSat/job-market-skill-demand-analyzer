# Power BI Implementation & Modeling Guide

This guide walks you through importing the pipeline output into **Power BI Desktop**, configuring the **Star Schema data model**, applying DAX measures, and creating an executive-grade dashboard.

---

## 1. Importing the Data into Power BI

### Option A: Direct CSV Import (Recommended)
1. Open **Power BI Desktop**.
2. Click **Get Data** -> **Text/CSV**.
3. Navigate to `powerbi/data/` and import these 4 tables:
   - `dim_jobs.csv`
   - `dim_skills.csv`
   - `dim_locations.csv`
   - `fact_job_skills.csv`
4. Click **Load** (or *Transform Data* if you want to inspect types).

### Option B: Using the Pre-joined Flat View (Quick Prototype)
If you want to create a single-page prototype in under 5 minutes without configuring relationships:
- Import `powerbi/data/powerbi_flat_reporting_view.csv`.

---

## 2. Setting Up the Star Schema Data Model

Navigate to the **Model View** (icon on the left sidebar) to verify relationships.

```
       +-------------------+       +-------------------+
       |   dim_locations   |       |    dim_skills     |
       +-------------------+       +-------------------+
       | *location_id      |       | *skill_id         |
       |  city             |       |  skill_name       |
       |  state            |       |  skill_category   |
       +---------+---------+       +---------+---------+
                 | 1                         | 1
                 |                           |
                 | *                         | *
       +---------v---------+       +---------v---------+
       |     dim_jobs      |       |  fact_job_skills  |
       +-------------------+       +-------------------+
       | *job_id           | 1   * | *job_id           |
       |  job_title        +------>| *skill_id         |
       |  role_family      |       |  skill_name       |
       |  company          |       |  skill_category   |
       |  city             |       +-------------------+
       |  salary_avg_lpa   |
       |  exp_level_bracket|
       +-------------------+
```

### Relationship Configuration Rules:
1. **`dim_jobs[job_id]` $\rightarrow$ `fact_job_skills[job_id]`**
   - **Cardinality**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single` (or `Both` if you want selecting a skill in a slicer to directly filter the jobs table KPI cards).
2. **`dim_skills[skill_id]` $\rightarrow$ `fact_job_skills[skill_id]`**
   - **Cardinality**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single`
3. **`dim_locations[city]` $\rightarrow$ `dim_jobs[city]`**
   - **Cardinality**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single`

---

## 3. Creating the DAX Measures Table

1. In the **Home** tab, click **Enter Data**.
2. Name the table `_Measures` and click **Load**.
3. Right-click `_Measures` -> **New Measure**.
4. Open `powerbi/dax_measures.dax` and paste the measures:
   - `[Total Postings]`
   - `[Skill Market Penetration %]` (Format as `0.0%`)
   - `[Average Salary LPA]` (Format as Currency `₹ 0.0 LPA`)
   - `[SQL Penetration %]`, `[Python Penetration %]`, `[Power BI Penetration %]`
   - `[Skill Salary Premium LPA]`

---

## 4. Recommended 3-Page Dashboard Layout

### Page 1: Executive Market Overview
- **Top Header**: Project Title + Slicers (`Role Family`, `City`, `Experience Level`).
- **KPI Cards (Top Row)**:
  1. Total Postings (`5,200`)
  2. Average Market Salary (`₹12.4 LPA`)
  3. #1 In-Demand Skill (`SQL - 78.4%`)
  4. Remote Flexibility (`10.2% Postings`)
- **Main Visuals**:
  - **Bar Chart**: Top 15 In-Demand Skills by Market Penetration %.
  - **Donut Chart**: Postings by Role Family (Data Analyst vs BI vs DE vs Python).
  - **Treemap / Map**: Postings by City (Bengaluru, Hyderabad, Pune, Mumbai, etc.).

### Page 2: Role Deep-Dive & Tech Stack Matrix
- **Matrix Visual**:
  - Rows: `dim_skills[skill_name]`
  - Columns: `dim_jobs[role_family]`
  - Values: `[Skill Market Penetration %]`
- **Clustered Column Chart**: "The Big 3 Analytics Tools" (SQL vs Python vs Power BI) segmented across Junior, Mid, and Senior experience levels.
- **Card / Gauge**: Power BI vs Tableau market demand ratio.

### Page 3: Salary & Skill Premium Analyzer
- **Scatter Plot**:
  - X-Axis: `[Skill Market Penetration %]` (Popularity)
  - Y-Axis: `[Average Salary LPA]` (Earning Power)
  - Bubble Size: `[Total Postings]`
  - Legend: `dim_skills[skill_category]`
  - *Insight Highlight*: "High Demand + High Salary" quadrant (e.g., Snowflake, dbt, Spark).
- **Bar Chart**: Skill Salary Premium (Which skills boost your salary above market baseline?).
