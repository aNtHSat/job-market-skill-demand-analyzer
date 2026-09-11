-- ==============================================================================
-- 02_analytics_queries.sql
-- Advanced Analytical SQL Queries for Job Market Skill-Demand Analyzer
-- Target Engine: SQLite / ANSI SQL (PostgreSQL, MySQL, Snowflake compatible)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Top 10 Most In-Demand Skills Across All Data Roles
-- Calculates absolute frequency and market penetration percentage.
-- ------------------------------------------------------------------------------
SELECT 
    f.skill_name,
    f.skill_category,
    COUNT(DISTINCT f.job_id) AS total_postings,
    ROUND(COUNT(DISTINCT f.job_id) * 100.0 / (SELECT COUNT(*) FROM dim_jobs), 2) AS market_penetration_pct
FROM fact_job_skills f
GROUP BY f.skill_name, f.skill_category
ORDER BY total_postings DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 2: Top 5 In-Demand Skills Ranked by Role Family (Window Function: DENSE_RANK)
-- Demonstrates partitioning by role to see what separates Data Analyst from BI & DE.
-- ------------------------------------------------------------------------------
WITH role_skill_counts AS (
    SELECT 
        j.role_family,
        f.skill_name,
        f.skill_category,
        COUNT(DISTINCT j.job_id) AS demand_count,
        ROUND(COUNT(DISTINCT j.job_id) * 100.0 / COUNT(DISTINCT j.job_id), 2) AS role_pct
    FROM dim_jobs j
    JOIN fact_job_skills f ON j.job_id = f.job_id
    GROUP BY j.role_family, f.skill_name, f.skill_category
),
ranked_skills AS (
    SELECT 
        role_family,
        skill_name,
        skill_category,
        demand_count,
        DENSE_RANK() OVER (
            PARTITION BY role_family 
            ORDER BY demand_count DESC
        ) AS rank_in_role
    FROM role_skill_counts
)
SELECT 
    role_family,
    rank_in_role,
    skill_name,
    skill_category,
    demand_count
FROM ranked_skills
WHERE rank_in_role <= 5
ORDER BY role_family, rank_in_role;


-- ------------------------------------------------------------------------------
-- QUERY 3: The Data Analyst Core Trifecta (SQL vs Python vs Power BI/Tableau)
-- Evaluates the exact % of Data Analyst postings demanding each core pillar.
-- ------------------------------------------------------------------------------
WITH da_jobs AS (
    SELECT job_id 
    FROM dim_jobs 
    WHERE role_family = 'Data Analyst'
),
skill_flags AS (
    SELECT 
        d.job_id,
        MAX(CASE WHEN f.skill_name = 'SQL' THEN 1 ELSE 0 END) AS has_sql,
        MAX(CASE WHEN f.skill_name = 'Python' THEN 1 ELSE 0 END) AS has_python,
        MAX(CASE WHEN f.skill_name IN ('Power BI', 'Tableau') THEN 1 ELSE 0 END) AS has_viz_tool,
        MAX(CASE WHEN f.skill_name = 'Excel' THEN 1 ELSE 0 END) AS has_excel
    FROM da_jobs d
    LEFT JOIN fact_job_skills f ON d.job_id = f.job_id
    GROUP BY d.job_id
)
SELECT 
    COUNT(*) AS total_da_postings,
    ROUND(SUM(has_sql) * 100.0 / COUNT(*), 2) AS sql_demand_pct,
    ROUND(SUM(has_python) * 100.0 / COUNT(*), 2) AS python_demand_pct,
    ROUND(SUM(has_viz_tool) * 100.0 / COUNT(*), 2) AS bi_tool_demand_pct,
    ROUND(SUM(has_excel) * 100.0 / COUNT(*), 2) AS excel_demand_pct,
    ROUND(SUM(CASE WHEN has_sql = 1 AND has_python = 1 AND has_viz_tool = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS full_stack_analyst_pct
FROM skill_flags;


-- ------------------------------------------------------------------------------
-- QUERY 4: Skill Co-Occurrence Matrix (Self-Join Association Analysis)
-- "When an employer requires SQL, which other skills are paired with it most often?"
-- ------------------------------------------------------------------------------
WITH sql_jobs AS (
    SELECT DISTINCT job_id
    FROM fact_job_skills
    WHERE skill_name = 'SQL'
)
SELECT 
    f.skill_name AS co_occurring_skill,
    f.skill_category,
    COUNT(DISTINCT f.job_id) AS co_occurrence_count,
    ROUND(COUNT(DISTINCT f.job_id) * 100.0 / (SELECT COUNT(*) FROM sql_jobs), 2) AS conditional_probability_pct
FROM fact_job_skills f
JOIN sql_jobs s ON f.job_id = s.job_id
WHERE f.skill_name != 'SQL'
GROUP BY f.skill_name, f.skill_category
ORDER BY co_occurrence_count DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 5: The "BI Tool Showdown" - Power BI vs. Tableau by City
-- Analyzes visualization market share across top Indian tech hubs.
-- ------------------------------------------------------------------------------
SELECT 
    j.city,
    COUNT(DISTINCT j.job_id) AS total_city_jobs,
    SUM(CASE WHEN f.skill_name = 'Power BI' THEN 1 ELSE 0 END) AS powerbi_jobs,
    SUM(CASE WHEN f.skill_name = 'Tableau' THEN 1 ELSE 0 END) AS tableau_jobs,
    ROUND(SUM(CASE WHEN f.skill_name = 'Power BI' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 2) AS powerbi_share_pct,
    ROUND(SUM(CASE WHEN f.skill_name = 'Tableau' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 2) AS tableau_share_pct
FROM dim_jobs j
JOIN fact_job_skills f ON j.job_id = f.job_id
WHERE f.skill_name IN ('Power BI', 'Tableau')
GROUP BY j.city
ORDER BY total_city_jobs DESC;


-- ------------------------------------------------------------------------------
-- QUERY 6: Salary Premium Analysis - What is the ROI of Learning Cloud & Big Data?
-- Compares average salary of Data Analyst roles that require Cloud/Modern tools vs traditional.
-- ------------------------------------------------------------------------------
WITH da_salaries AS (
    SELECT 
        j.job_id,
        j.salary_avg_lpa,
        MAX(CASE WHEN f.skill_name IN ('AWS', 'Azure', 'Snowflake', 'Databricks', 'BigQuery') THEN 1 ELSE 0 END) AS has_cloud_or_lakehouse
    FROM dim_jobs j
    JOIN fact_job_skills f ON j.job_id = f.job_id
    WHERE j.role_family = 'Data Analyst' 
      AND j.salary_avg_lpa IS NOT NULL
    GROUP BY j.job_id, j.salary_avg_lpa
)
SELECT 
    CASE 
        WHEN has_cloud_or_lakehouse = 1 THEN 'Requires Cloud/Modern Data Stack'
        ELSE 'Traditional Stack (SQL/Excel/BI only)'
    END AS skill_tier,
    COUNT(*) AS job_sample_count,
    ROUND(AVG(salary_avg_lpa), 2) AS avg_salary_lpa,
    ROUND(MIN(salary_avg_lpa), 2) AS min_salary_lpa,
    ROUND(MAX(salary_avg_lpa), 2) AS max_salary_lpa
FROM da_salaries
GROUP BY has_cloud_or_lakehouse;


-- ------------------------------------------------------------------------------
-- QUERY 7: Skill Demand Evolution by Experience Level (Junior vs Mid vs Senior)
-- Uncovers how tech stack expectations shift as candidates advance.
-- ------------------------------------------------------------------------------
SELECT 
    j.exp_level_bracket,
    f.skill_name,
    COUNT(DISTINCT j.job_id) AS demand_count,
    ROUND(COUNT(DISTINCT j.job_id) * 100.0 / total_exp.total_bracket_jobs, 2) AS demand_pct
FROM dim_jobs j
JOIN fact_job_skills f ON j.job_id = f.job_id
JOIN (
    SELECT exp_level_bracket, COUNT(*) AS total_bracket_jobs
    FROM dim_jobs
    GROUP BY exp_level_bracket
) total_exp ON j.exp_level_bracket = total_exp.exp_level_bracket
WHERE f.skill_name IN ('SQL', 'Python', 'Power BI', 'Excel', 'AWS', 'Apache Spark', 'Machine Learning')
GROUP BY j.exp_level_bracket, f.skill_name, total_exp.total_bracket_jobs
ORDER BY j.exp_level_bracket, demand_count DESC;


-- ------------------------------------------------------------------------------
-- QUERY 8: Industry Sector Tech Stack Benchmark
-- Which industries pay the highest average salary and what is their preferred stack?
-- ------------------------------------------------------------------------------
SELECT 
    j.industry,
    COUNT(DISTINCT j.job_id) AS total_openings,
    ROUND(AVG(j.salary_avg_lpa), 2) AS avg_industry_salary_lpa,
    ROUND(SUM(CASE WHEN f.skill_name = 'SQL' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 1) AS sql_pct,
    ROUND(SUM(CASE WHEN f.skill_name = 'Python' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 1) AS python_pct,
    ROUND(SUM(CASE WHEN f.skill_name = 'Power BI' THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 1) AS powerbi_pct
FROM dim_jobs j
LEFT JOIN fact_job_skills f ON j.job_id = f.job_id
GROUP BY j.industry
ORDER BY avg_industry_salary_lpa DESC;


-- ------------------------------------------------------------------------------
-- QUERY 9: Remote vs. On-Site vs. Hybrid Skill Demand
-- Does working remotely require higher cloud and collaboration skills?
-- ------------------------------------------------------------------------------
SELECT 
    j.remote_status,
    COUNT(DISTINCT j.job_id) AS total_postings,
    ROUND(AVG(j.salary_avg_lpa), 2) AS avg_salary_lpa,
    ROUND(SUM(CASE WHEN f.skill_name IN ('AWS', 'Azure', 'Google Cloud') THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 2) AS cloud_demand_pct,
    ROUND(SUM(CASE WHEN f.skill_name IN ('Git', 'Docker') THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT j.job_id), 2) AS devops_tools_pct
FROM dim_jobs j
JOIN fact_job_skills f ON j.job_id = f.job_id
GROUP BY j.remote_status
ORDER BY total_postings DESC;


-- ------------------------------------------------------------------------------
-- QUERY 10: Top 10 Highest-Paying Individual Skills Across Analytics & Engineering
-- Filters for skills with at least 150 job postings to avoid single-job outliers.
-- ------------------------------------------------------------------------------
SELECT 
    f.skill_name,
    f.skill_category,
    COUNT(DISTINCT j.job_id) AS sample_postings,
    ROUND(AVG(j.salary_avg_lpa), 2) AS avg_salary_lpa,
    ROUND(MIN(j.salary_avg_lpa), 2) AS min_salary_lpa,
    ROUND(MAX(j.salary_avg_lpa), 2) AS max_salary_lpa
FROM fact_job_skills f
JOIN dim_jobs j ON f.job_id = j.job_id
WHERE j.salary_avg_lpa IS NOT NULL
GROUP BY f.skill_name, f.skill_category
HAVING sample_postings >= 150
ORDER BY avg_salary_lpa DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- QUERY 11: Skill Breadth (Skill Count per Posting) vs. Salary
-- "Does knowing more skills translate to a higher paycheck?"
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN skills_count <= 4 THEN '1 - 4 Skills (Specialist / Entry)'
        WHEN skills_count BETWEEN 5 AND 8 THEN '5 - 8 Skills (Balanced Core)'
        WHEN skills_count BETWEEN 9 AND 12 THEN '9 - 12 Skills (Multi-Disciplinary)'
        ELSE '13+ Skills (Full-Stack / Lead)'
    END AS skill_breadth_tier,
    COUNT(*) AS total_postings,
    ROUND(AVG(salary_avg_lpa), 2) AS avg_salary_lpa,
    ROUND(AVG(min_exp_years), 1) AS avg_required_min_exp
FROM dim_jobs
WHERE salary_avg_lpa IS NOT NULL
GROUP BY skill_breadth_tier
ORDER BY avg_salary_lpa ASC;


-- ------------------------------------------------------------------------------
-- QUERY 12: Monthly Skill Trend & Hiring Velocity
-- Tracks monthly posting volume for key skills over time.
-- ------------------------------------------------------------------------------
SELECT 
    SUBSTR(j.posted_date, 1, 7) AS posting_month,
    f.skill_name,
    COUNT(DISTINCT j.job_id) AS monthly_postings
FROM dim_jobs j
JOIN fact_job_skills f ON j.job_id = f.job_id
WHERE f.skill_name IN ('SQL', 'Python', 'Power BI', 'AWS', 'Snowflake')
GROUP BY posting_month, f.skill_name
ORDER BY posting_month ASC, monthly_postings DESC;
