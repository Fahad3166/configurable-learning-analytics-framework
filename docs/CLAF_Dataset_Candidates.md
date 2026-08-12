# Configurable Learning Analytics Framework (CLAF)

# Candidate Dataset Discovery

## Purpose

This document records the public datasets identified during the initial dataset discovery phase of the Configurable Learning Analytics Framework (CLAF).

The purpose of this phase is to identify realistic candidate datasets that may support implementation of the CLAF analytical architecture.

No dataset is selected at this stage.

Candidate datasets will be inspected and evaluated in subsequent phases using the criteria defined in:

`docs/CLAF_Dataset_Evaluation_Framework.md`

The final dataset selection will therefore be based on evidence and alignment with the CLAF data contract rather than dataset popularity or convenience.

---

# 1. Discovery Approach

Candidate datasets were identified based on the following requirements:

* Educational relevance
* Learner-level data
* Course, module, or program context
* Learning activity or engagement information
* Assessment or performance information
* Temporal information
* Potential for longitudinal analysis
* Potential for cohort or group comparison
* Sufficient scale for data engineering and analytics
* Public availability
* Clear provenance and licensing information where available

The initial search prioritized learning analytics datasets because CLAF is intended to demonstrate an end-to-end educational analytics architecture rather than a generic student-performance prediction model.

---

# 2. Candidate Summary

| Rank | Dataset                                              | Initial CLAF Potential | Status              |
| ---- | ---------------------------------------------------- | ---------------------- | ------------------- |
| 1    | Open University Learning Analytics Dataset (OULAD)   | Very High              | Primary candidate   |
| 2    | Educational Technology Learning Analytics Dataset    | High                   | Candidate           |
| 3    | Student Learning Interaction Logs Dataset            | High                   | Backup / synthetic  |
| 4    | UCI Student Performance                              | Moderate               | Secondary candidate |
| 5    | UCI Higher Education Students Performance Evaluation | Low–Moderate           | Backup candidate    |

The ranking above is preliminary and does not represent the final dataset evaluation score.

---

# 3. Candidate 1 — Open University Learning Analytics Dataset (OULAD)

## Source

Open University Learning Analytics Dataset (OULAD)

Primary research/data source:

https://analyse.kmi.open.ac.uk/open_dataset

A Kaggle mirror is also available:

https://www.kaggle.com/datasets/thedevastator/open-university-learning-analytics-dataset

## Description

OULAD is an educational dataset from The Open University designed for learning analytics research.

The dataset contains data from 32,593 students across 22 module presentations. It includes information covering students, assessments and interactions with the Virtual Learning Environment (VLE).

The dataset has also been used in research on student behavior, performance and early identification of students at risk.

## Initial CLAF Mapping

Potentially available CLAF concepts include:

* Student
* Module
* Assessment
* Learning Activity
* Time
* Performance
* Cohort/group context

Potentially derivable analytical concepts include:

* Engagement
* Assessment performance
* Activity frequency
* Activity trends
* Progression
* Risk indicators
* Growth measures

## Strengths

* Strong alignment with learning analytics
* Learner-level records
* Module/course context
* Assessment information
* VLE interaction data
* Temporal activity data
* Suitable for longitudinal analysis
* Large enough to demonstrate data engineering
* Strong research relevance
* Well suited to student-risk and engagement analysis

## Limitations

OULAD does not provide a ready-made CLAF competency framework.

Competency entities and competency attainment therefore cannot simply be claimed to originate from the dataset.

If competency analytics are demonstrated, the mapping must be explicitly defined through CLAF configuration and measurement rules.

Intervention data is also not directly available as a complete intervention-history entity.

## Initial Assessment

**Very High potential.**

OULAD is currently the strongest candidate because its structure is closely aligned with the core CLAF use case:

```text
Student
    ↓
Module
    ↓
VLE Activity
    ↓
Assessment
    ↓
Time
    ↓
Performance / Progression
```

## Status

**Primary candidate — requires detailed inspection before final selection.**

---

# 4. Candidate 2 — Educational Technology Learning Analytics Dataset

## Source

Kaggle:

https://www.kaggle.com/datasets/birendeepsingh/educational-technology-learning-analytics-dataset

## Description

The dataset describes an online learning environment containing:

* 8,000 students
* 150 courses
* 200,000+ learning interactions

The dataset description states that it includes student demographics, educational background, learning preferences, course metadata, interaction tracking, performance metrics, engagement patterns, help-seeking behavior and peer interaction.

The dataset is published on Kaggle under an Apache 2.0 license according to its dataset page.

## Initial CLAF Mapping

Potentially available concepts include:

* Student
* Course
* Learning Activity
* Assessment/performance
* Engagement
* Time/context
* Learning preferences

Potential analytical measures may include:

* Engagement
* Course performance
* Completion
* Interaction patterns
* Help-seeking behavior
* Peer interaction

## Strengths

* Large number of students
* Large number of interactions
* Course context
* Performance information
* Engagement information
* Multiple activity types
* Suitable for demonstrating data engineering and analytics
* Potentially useful for machine-learning experiments

## Limitations

The dataset requires detailed inspection before we can determine:

* Exact file structure
* Exact field definitions
* Temporal granularity
* Identifier relationships
* Data provenance
* Whether all described relationships are represented directly in the downloadable files

The dataset description alone is not sufficient to establish complete CLAF compatibility.

## Initial Assessment

**High potential, subject to validation.**

## Status

**Candidate — inspect before selection.**

---

# 5. Candidate 3 — Student Learning Interaction Logs Dataset

## Source

Kaggle:

https://www.kaggle.com/datasets/ziya07/student-learning-interaction-logs-dataset

## Description

The dataset describes simulated student interactions in a digital learning environment.

The Kaggle description reports:

* 9,000+ learning sessions
* 300 students
* 22 features
* Sequential session data
* Student behavior
* Engagement
* Performance
* Progression

Example fields include:

* `student_id`
* `session_id`
* `timestamp`
* `module_id`
* `time_spent_minutes`
* `pages_visited`
* `video_watched_percent`
* `click_events`
* `forum_posts`
* `quiz_score`
* `assignment_score`
* `feedback_rating`
* `cumulative_quiz_score`
* `learning_trend`
* `attention_score`
* `success_label`

The dataset is described as simulated and is published under CC0 according to its Kaggle page.

## Initial CLAF Mapping

Potentially available concepts include:

* Student
* Module
* Learning Activity
* Assessment/performance
* Time
* Engagement
* Feedback
* Progression

## Strengths

* Explicit learner-level session data
* Strong temporal structure
* Module information
* Engagement measures
* Assessment information
* Performance trends
* Easy to use for longitudinal analytics
* Useful for demonstrating the analytical engine

## Limitations

The dataset is explicitly described as **simulated**.

Therefore, it should not be presented as real institutional or LMS data.

It may be useful for demonstrating architecture or testing analytical components, but it is weaker than a real educational dataset for the primary CLAF implementation.

## Initial Assessment

**High technical potential but lower empirical credibility because the data is simulated.**

## Status

**Backup / synthetic-data demonstration candidate.**

---

# 6. Candidate 4 — UCI Student Performance

## Source

UCI Machine Learning Repository:

https://archive.ics.uci.edu/dataset/320/student%2Bperformance

## Description

The UCI Student Performance dataset contains student achievement data from two Portuguese schools.

The dataset contains 649 instances and covers student grades together with demographic, social and school-related attributes.

Two subjects are represented:

* Mathematics
* Portuguese language

The dataset includes grades from different periods.

In particular:

* `G1` represents the first-period grade
* `G2` represents the second-period grade
* `G3` represents the final grade

The UCI documentation specifically notes the strong correlation between G1/G2 and the final grade G3.

## Initial CLAF Mapping

Potentially available concepts include:

* Student
* Performance
* Time/period
* Educational context
* Demographic information
* Academic progression

## Strengths

* Well documented
* Established research dataset
* Clear provenance
* Small and easy to process
* Contains sequential academic performance measures
* Suitable for regression/classification
* Useful for demonstrating progression and risk modelling

## Limitations

The dataset is from secondary education rather than higher education.

It does not provide detailed LMS/VLE activity data.

It does not contain:

* Detailed learning activities
* Module-level LMS interactions
* Competency framework
* Intervention history

Therefore, it does not fully represent the CLAF learning-analytics architecture.

## Initial Assessment

**Moderate potential.**

It could be useful as a secondary analytical example, but it is not currently preferred for the main CLAF implementation.

## Status

**Secondary candidate.**

---

# 7. Candidate 5 — UCI Higher Education Students Performance Evaluation

## Source

UCI Machine Learning Repository:

https://archive.ics.uci.edu/dataset/856/higher%2Beducation%2Bstudents%2B%20performance%2Bevaluation

## Description

The dataset was collected from students in the Faculty of Engineering and Faculty of Educational Sciences in 2019.

The purpose of the dataset is to predict students' end-of-term performance using machine-learning techniques.

The UCI repository reports:

* 145 instances
* 31 features
* Multivariate data
* Classification task
* No missing values

The variables include personal characteristics, family information and educational habits.

## Initial CLAF Mapping

Potentially available concepts include:

* Student
* Higher-education context
* Educational habits
* Performance outcome
* Demographic information

## Strengths

* Genuine higher-education context
* Clear provenance
* No missing values according to UCI
* Easy to process
* Suitable for classification experiments

## Limitations

The dataset is very small.

It does not provide detailed:

* LMS activity
* Module structure
* Assessment history
* Longitudinal learner activity
* Competency measurements
* Intervention data

It therefore has limited value for demonstrating the complete CLAF architecture.

## Initial Assessment

**Low to moderate potential.**

## Status

**Backup candidate only.**

---

# 8. Preliminary Comparison

| Criterion              | OULAD                 | Educational Technology LA | Student Interaction Logs | UCI Student Performance | UCI Higher Education  |
| ---------------------- | --------------------- | ------------------------- | ------------------------ | ----------------------- | --------------------- |
| Learner data           | Strong                | Strong*                   | Strong                   | Strong                  | Strong                |
| Course/module data     | Strong                | Strong*                   | Strong                   | Weak                    | Weak                  |
| Learning activity      | Strong                | Strong*                   | Strong                   | None                    | None                  |
| Assessment             | Strong                | Strong*                   | Strong                   | Strong                  | Limited               |
| Temporal data          | Strong                | To verify                 | Strong                   | Limited                 | Weak                  |
| Longitudinal analysis  | Strong                | To verify                 | Strong                   | Limited                 | Weak                  |
| Engagement analysis    | Strong                | Strong*                   | Strong                   | Weak                    | Weak                  |
| Cohort/group analysis  | Potential             | To verify                 | Potential                | Limited                 | Limited               |
| Competency data        | Not native            | To verify                 | Not native               | None                    | None                  |
| Intervention data      | Not native            | To verify                 | Limited                  | None                    | None                  |
| Educational relevance  | Very strong           | Strong                    | Strong                   | Moderate                | Strong                |
| Data scale             | Large                 | Large                     | Medium                   | Small                   | Very small            |
| Data type              | Real educational data | To verify                 | Simulated                | Real educational data   | Real educational data |
| Initial CLAF potential | **Very High**         | **High**                  | **High**                 | **Moderate**            | **Low–Moderate**      |

`*` Based on the published dataset description and requires validation against the actual downloadable files.

---

# 9. Preliminary Ranking

The current ranking is:

### 1. OULAD

**Primary candidate**

Strongest match to the CLAF architecture because it combines learner, module, assessment, VLE interaction and temporal data.

### 2. Educational Technology Learning Analytics Dataset

**Strong alternative**

Potentially very useful due to its scale and breadth, but the actual downloadable structure and provenance need to be inspected.

### 3. Student Learning Interaction Logs Dataset

**Technical backup**

Excellent structure for demonstrating longitudinal analytics, but explicitly simulated.

### 4. UCI Student Performance

**Secondary analytical dataset**

Useful for academic progression and predictive modelling but lacks LMS activity data.

### 5. UCI Higher Education Students Performance Evaluation

**Backup**

Relevant higher-education context but too small and limited for the main CLAF architecture.

---

# 10. Important Data Provenance Principle

CLAF distinguishes between:

### Source Data

Information directly obtained from the original dataset.

### Clean Data

Source data after validated preprocessing and quality transformations.

### Derived Data

Metrics calculated from source data.

Examples:

* Weekly engagement
* Assessment percentage
* Four-week growth
* Risk score
* Competency score derived through documented measurement rules

### Configured Data

Information introduced through CLAF configuration.

Examples:

* Competency definitions
* KPI thresholds
* Measurement weights
* Risk thresholds
* Growth windows

### Synthetic Data

Artificially generated data used only when a required CLAF capability cannot be demonstrated using the selected public dataset.

Synthetic data must always be explicitly labelled.

CLAF will not present derived, configured, or synthetic information as if it were directly collected by the original dataset.

---

# 11. Current Discovery Decision

No final dataset has been selected during Candidate Discovery.

The current recommendation is to inspect **OULAD first**, followed by the Educational Technology Learning Analytics Dataset.

The inspection phase will examine the actual downloadable files rather than relying only on high-level dataset descriptions.

The inspection will focus on:

* File structure
* Table structure
* Column names
* Data types
* Primary identifiers
* Foreign-key relationships
* Timestamp fields
* Assessment records
* Learning activity records
* Student records
* Module/course records
* Missing values
* Duplicate records
* Dataset size
* Licensing
* Provenance
* Compatibility with the CLAF entity model

The final decision will be made only after completing the CLAF Dataset Evaluation Framework.

---

# 12. Next Step

The next phase is:

**Sprint 2.4B — Candidate Dataset Inspection**

The first candidate to inspect is:

**Open University Learning Analytics Dataset (OULAD)**

The objective is to inspect the actual data structure and map it to the CLAF data contract before assigning the final evaluation score.
