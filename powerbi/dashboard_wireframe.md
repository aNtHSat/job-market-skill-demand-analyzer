# Power BI Dashboard Wireframe & Visual Specifications

This document outlines the visual layout, color palette, typography, and card placements for building an executive-ready dashboard in Power BI.

---

## Visual Design System

- **Canvas Size**: 16:9 (1920 x 1080 px)
- **Color Palette**:
  - Primary Accent: `#2563EB` (Royal Blue)
  - Secondary Accent: `#0D9488` (Teal / Modern Data)
  - Highlight / Alert: `#F59E0B` (Amber Gold)
  - Dark Neutral: `#0F172A` (Slate Navy)
  - Light Neutral: `#F8FAFC` (Card Background)
  - Border: `#E2E8F0`
- **Typography**: `Segoe UI` (Clean, corporate standard in Power BI)

---

## Wireframe 1: Executive Market Overview

```
+----------------------------------------------------------------------------------------------------+
|  [Logo] JOB MARKET SKILL-DEMAND ANALYZER                   [Slicer: Role] [Slicer: City] [Exp Level]
+----------------------------------------------------------------------------------------------------+
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+    |
|  | TOTAL POSTINGS     |  | AVG SALARY         |  | TOP SKILL          |  | REMOTE %           |    |
|  | 5,200              |  | ₹12.4 LPA          |  | SQL (78.4%)        |  | 10.2%              |    |
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+    |
|                                                                                                    |
|  +----------------------------------------------------+  +---------------------------------------+ |
|  | TOP 15 SKILLS BY MARKET DEMAND (%)                 |  | DEMAND BY ROLE FAMILY                 | |
|  | [Stacked Horizontal Bar Chart]                     |  | [Donut Chart]                         | |
|  | SQL        ████████████████████ 78%                |  | ■ Data Analyst (38%)                  | |
|  | Python     ███████████████ 61%                     |  | ■ BI Analyst   (24%)                  | |
|  | Power BI   ████████████ 48%                        |  | ■ Data Engineer(20%)                  | |
|  | Excel      ██████████ 41%                          |  | ■ SQL Developer(12%)                  | |
|  | Tableau    ███████ 29%                             |  | ■ Python Dev   (6%)                   | |
|  +----------------------------------------------------+  +---------------------------------------+ |
|                                                                                                    |
|  +----------------------------------------------------+  +---------------------------------------+ |
|  | HIRING VOLUME BY TECH HUB (CITY)                   |  | SALARY DISTRIBUTION BY EXPERIENCE     | |
|  | [Column Chart: Bengaluru, Hyd, Pune, Mumbai, Gur]   |  | [Clustered Column or Box Plot]        | |
|  +----------------------------------------------------+  +---------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

---

## Wireframe 2: Role Deep-Dive & Skill Matrix

```
+----------------------------------------------------------------------------------------------------+
|  ROLE BENCHMARKING & SKILL MATRIX                                                                  |
+----------------------------------------------------------------------------------------------------+
|  +-----------------------------------------------------------------------------------------------+ |
|  | HEATMAP MATRIX: SKILL PENETRATION RATE (%) BY ROLE FAMILY                                     | |
|  | Skill Name         | Data Analyst | BI Analyst | SQL Dev   | Python Dev | Data Engineer       | |
|  | ------------------ | ------------ | ---------- | --------- | ---------- | -------------       | |
|  | SQL                | 84% (High)   | 72% (Med)  | 98% (High)| 45% (Low)  | 89% (High)          | |
|  | Python             | 65% (Med)    | 32% (Low)  | 28% (Low) | 96% (High) | 88% (High)          | |
|  | Power BI           | 56% (Med)    | 88% (High) | 12% (Low) | 5%  (None) | 14% (Low)           | |
|  | Excel              | 62% (Med)    | 55% (Med)  | 18% (Low) | 8%  (None) | 12% (Low)           | |
|  | Apache Spark       | 12% (Low)    | 4%  (None) | 8%  (Low) | 22% (Low)  | 78% (High)          | |
|  +-----------------------------------------------------------------------------------------------+ |
|                                                                                                    |
|  +----------------------------------------------------+  +---------------------------------------+ |
|  | BI SHOWDOWN: POWER BI vs TABLEAU BY CITY           |  | SKILL REQUIREMENTS ACROSS CAREER STAGE| |
|  | [100% Stacked Bar Chart comparing tool share]      |  | [Grouped Column Chart: 0-2 vs 3-5 vs 6+] |
|  +----------------------------------------------------+  +---------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

---

## Wireframe 3: Salary vs. Demand ROI Quadrant

```
+----------------------------------------------------------------------------------------------------+
|  SALARY ROI & TECH STACK VALUE MAP                                                                 |
+----------------------------------------------------------------------------------------------------+
|  High Salary                                                                                       |
|      ^                                                                                             |
|      |    [Q1: High Pay / Niche Skills]           |    [Q2: The Sweet Spot (High Pay + High Demand)]|
|      |    • Databricks (₹21 LPA, 18% Demand)      |    • Apache Spark (₹22 LPA, 38% Demand)        |
|      |    • Snowflake  (₹19 LPA, 22% Demand)      |    • AWS Cloud    (₹18 LPA, 42% Demand)        |
|      |                                            |                                                |
|  Avg | -------------------------------------------+------------------------------------------------|
|  Pay |                                            |                                                |
|      |    [Q3: Entry / Foundational Stack]        |    [Q4: High Volume Commodities]               |
|      |    • Excel VBA  (₹8.5 LPA, 14% Demand)     |    • SQL     (₹13 LPA, 78% Demand)             |
|      |                                            |    • Excel   (₹9.5 LPA, 41% Demand)            |
|      v                                                                                             |
|      +--------------------------------------------+----------------------------------------------> |
|     0% Market Penetration                                                100% Market Penetration   |
+----------------------------------------------------------------------------------------------------+
```
