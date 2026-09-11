-- ==============================================================================
-- 01_schema_ddl.sql
-- Relational Star-Schema DDL for Job Market Skill-Demand Analyzer
-- Target Engine: SQLite 3 / ANSI SQL Compatible (PostgreSQL/MySQL friendly)
-- ==============================================================================

-- Drop existing tables if re-initializing
DROP TABLE IF EXISTS fact_job_skills;
DROP TABLE IF EXISTS dim_jobs;
DROP TABLE IF EXISTS dim_skills;
DROP TABLE IF EXISTS dim_locations;

-- ------------------------------------------------------------------------------
-- 1. DIMENSION: dim_locations
-- ------------------------------------------------------------------------------
CREATE TABLE dim_locations (
    location_id     VARCHAR(20) PRIMARY KEY,
    city            VARCHAR(100) NOT NULL UNIQUE,
    state           VARCHAR(100) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    city_tier       VARCHAR(50),
    is_tech_hub     INTEGER DEFAULT 0 CHECK (is_tech_hub IN (0, 1))
);

-- ------------------------------------------------------------------------------
-- 2. DIMENSION: dim_skills
-- ------------------------------------------------------------------------------
CREATE TABLE dim_skills (
    skill_id        VARCHAR(20) PRIMARY KEY,
    skill_name      VARCHAR(100) NOT NULL UNIQUE,
    skill_category  VARCHAR(100) NOT NULL
);

-- ------------------------------------------------------------------------------
-- 3. DIMENSION: dim_jobs
-- ------------------------------------------------------------------------------
CREATE TABLE dim_jobs (
    job_id              VARCHAR(50) PRIMARY KEY,
    job_title           VARCHAR(200) NOT NULL,
    role_family         VARCHAR(100) NOT NULL,
    company             VARCHAR(150) NOT NULL,
    industry            VARCHAR(100),
    city                VARCHAR(100),
    state               VARCHAR(100),
    city_tier           VARCHAR(50),
    remote_status       VARCHAR(50),
    min_exp_years       INTEGER DEFAULT 0,
    max_exp_years       INTEGER DEFAULT 2,
    exp_level_bracket   VARCHAR(100),
    salary_min_lpa      REAL,
    salary_max_lpa      REAL,
    salary_avg_lpa      REAL,
    posted_date         DATE,
    skills_count        INTEGER DEFAULT 0,
    source_portal       VARCHAR(100),
    FOREIGN KEY (city) REFERENCES dim_locations(city)
);

-- ------------------------------------------------------------------------------
-- 4. FACT TABLE: fact_job_skills (Many-to-Many Bridge)
-- ------------------------------------------------------------------------------
CREATE TABLE fact_job_skills (
    job_id          VARCHAR(50) NOT NULL,
    skill_id        VARCHAR(20) NOT NULL,
    skill_name      VARCHAR(100) NOT NULL,
    skill_category  VARCHAR(100) NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES dim_jobs(job_id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES dim_skills(skill_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------------------------
-- 5. PERFORMANCE INDEXES
-- Optimized for high-speed analytical aggregations, joins, and filters
-- ------------------------------------------------------------------------------
CREATE INDEX idx_jobs_role ON dim_jobs(role_family);
CREATE INDEX idx_jobs_city ON dim_jobs(city);
CREATE INDEX idx_jobs_exp ON dim_jobs(exp_level_bracket);
CREATE INDEX idx_jobs_salary ON dim_jobs(salary_avg_lpa);
CREATE INDEX idx_jobs_date ON dim_jobs(posted_date);

CREATE INDEX idx_skills_cat ON dim_skills(skill_category);
CREATE INDEX idx_skills_name ON dim_skills(skill_name);

CREATE INDEX idx_fact_job ON fact_job_skills(job_id);
CREATE INDEX idx_fact_skill ON fact_job_skills(skill_id);
CREATE INDEX idx_fact_skill_name ON fact_job_skills(skill_name);
CREATE INDEX idx_fact_role_join ON fact_job_skills(job_id, skill_name);
