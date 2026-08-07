</> Markdown
# Configurable Learning Analytics Framework (CLAF)

## Section 1 - Project Description:
The Configurable Learning Analytics Framework (CLAF) is an end-to-end analytics platform designed to measure, monitor, and improve student learning outcomes. Rather than solving a single educational problem, the framework provides a reusable architecture that enables universities to define competency models, configure measurement rules, generate educational KPIs, support evidence-based interventions, and continuously improve teaching, curriculum design and student growth.

Learning analytics support improvement at multiple levels of the educational ecosystem—from individual learners to modules, programs, and institutional strategy.

## Section 2 — Business Problem:
Universities collect large amounts of educational data from Learning Management Systems (LMS), Student Information Systems (SIS), assessments, projects, and student surveys. However, these data sources are often analyzed independently, making it difficult to obtain a comprehensive understanding of student learning and development.
Traditional reporting focuses primarily on grades and completion rates, providing limited insight into competency development, learning engagement, or the effectiveness of educational interventions.
Furthermore, many analytics solutions are built for a single educational initiative, making them difficult to reuse when institutions introduce new competencies, programs, or curriculum changes.
As a result, universities require a configurable learning analytics framework that integrates multiple educational data sources, measures learning consistently, supports timely interventions, and enables continuous curriculum improvement through reusable analytical components.

## Section 3 — Objectives = What I am trying to achieve?

# Objective 1 - Build a reusable learning analytics framework.

# Objective 2 - Integrate educational data from multiple systems.

# Objective 3 - Provide reliable and transparent educational KPIs.

# Objective 4 - Support early identification of students who may benefit from additional support.

# Objective 5 - Enable evidence-based curriculum evaluation and continuous improvement.

# Objective 6 - Provide configurable competency models that can support future educational initiatives without redesigning the analytics architecture.


## Section — 4. Stakeholder Analysis

### Students

**Goals**
- Understand learning progress
- Monitor competency development
- Identify areas for improvement

**Questions**
- How am I progressing?
- Which competencies require improvement?
- Am I reaching expected outcomes?

**KPIs**
- Growth Score
- Competency Score
- Engagement Score
- Assessment Progress

**Possible Actions**
- Seek support
- Access learning resources
- Improve study strategies

---

### Instructors

**Goals**
- Improve teaching effectiveness
- Support students

**Questions**
- Which students may need support?
- Which topics are difficult?
- Are learning outcomes achieved?

**KPIs**
- Competency Attainment
- Engagement
- Assessment Success
- Risk Indicators

**Possible Actions**
- Adapt teaching methods
- Revise assessments
- Provide support

---

### Academic Advisors

**Goals**
- Support students proactively

**Questions**
- Which students may benefit from support?
- Are interventions effective?

**KPIs**
- Risk Score
- Intervention Outcomes
- Progress Trends

**Possible Actions**
- Contact students
- Recommend support services

---

### Program Leaders

**Goals**
- Improve curriculum quality

**Questions**
- Are competencies being achieved?
- Which modules need improvement?

**KPIs**
- Competency Growth
- Retention
- Program Outcomes

**Possible Actions**
- Curriculum redesign
- Resource allocation

---

### University Leadership

**Goals**
- Strategic planning

**Questions**
- Are institutional objectives achieved?

**KPIs**
- Retention
- Completion
- Student Success
- Equity Metrics

**Possible Actions**
- Policy decisions
- Strategic investments

## Section 5 – .Analytics Questions

5.1 Descriptive Analytics

# Purpose

# Understand the current state of learning.

# Questions

How many students are enrolled?
What are the baseline competency levels?
What is the current competency attainment?
How much competency growth has occurred?
What are the assessment outcomes?
What are student engagement patterns?
Which courses have the highest and lowest completion rates?
How do outcomes differ across cohorts?

## 5.2 Diagnostic Analytics
# Questions:

Which factors are associated with higher competency growth?
How does LMS engagement relate to assessment performance?
Which modules consistently show lower competency attainment?
Are there differences between student backgrounds?
Which competencies are most difficult to achieve?
Are some assessment types more challenging than others?
Which interventions appear to improve student outcomes?

## 5.3 Predictive Analytics

# Questions:

Which students may benefit from additional support?
Which students are likely to achieve expected competency levels?
Which students show declining engagement?
Which students are likely to complete the course successfully?
Which interventions are likely to have the greatest impact?

## 5.4 Decision Mapping

| Analytics Question                       | Decision                          | Stakeholder      |
| ---------------------------------------- | --------------------------------- | ---------------- |
| Which students may benefit from support? | Contact student                   | Academic Advisor |
| Which competencies are weak?             | Revise learning activities        | Instructor       |
| Which modules have low attainment?       | Review curriculum                 | Program Leader   |
| Are interventions effective?             | Continue or redesign intervention | Program Leader   |
| Are institutional goals achieved?        | Strategic planning                | Leadership       |



# 6. Learning Analytics Domain Model (LADM)

## 6.1 Purpose

The Learning Analytics Domain Model (LADM) defines the core business concepts, relationships, and educational processes that underpin the Configurable Learning Analytics Framework (CLAF). Rather than modelling databases or software components, the domain model captures how learning occurs within a university and how educational data supports evidence-based decision making.

The model provides a common conceptual foundation for data integration, analytics, KPI calculation, dashboard development, and continuous improvement. It is intentionally independent of implementation technologies, enabling the framework to be applied across different institutions, Learning Management Systems (LMS), and educational programs.

Unlike traditional learning analytics systems that focus on individual reports or specific educational problems, CLAF models the complete learning lifecycle—from academic structures and learning evidence to competency measurement, interventions, and institutional improvement.

---

## 6.2 Domain Categories

To maintain a clear separation of responsibilities, the domain is divided into four logical areas.

### Academic Structure

Represents the organizational structure of the university and defines where learning takes place.

**Entities**

- Program
- Module
- Course Offering
- Cohort
- Instructor

---

### Learning Domain

Represents the educational process and the development of student competencies.

**Entities**

- Student
- Competency
- Learning Checkpoint
- Assessment
- Competency Measurement

---

### Learning Behaviour

Represents behavioural and perception-based evidence collected throughout the learning process.

**Entities**

- LMS Activity
- Attendance
- Survey

---

### Decision & Continuous Improvement

Represents the analytical outputs used to support educational decisions and continuous quality improvement.

**Entities**

- Academic Advisor
- Intervention
- KPI
- Dashboard

---

# 6.3 Learning Analytics Domain Entities

| Entity | Purpose | Why it Exists |
|---------|----------|---------------|
| Student | Represents an individual learner. | Central entity whose learning journey is analysed throughout the framework. |
| Cohort | Represents a group of students progressing through the same program or intake. | Enables comparison between student groups, curriculum versions, and academic years. |
| Program | Represents an academic degree program. | Supports program-level analytics, curriculum evaluation, accreditation, and strategic reporting. |
| Module | Represents a logical unit within a program. | Enables analysis of learning outcomes and competency development at module level. |
| Course Offering | Represents the delivery of a module during a specific semester or academic period. | Allows comparison between different deliveries, instructors, and teaching approaches. |
| Instructor | Represents academic staff responsible for teaching. | Supports teaching analytics and evaluation of instructional practices. |
| Academic Advisor | Represents staff responsible for student support. | Enables monitoring and evaluation of academic interventions. |
| Competency | Represents a measurable learning outcome. | Defines what students are expected to know or be able to do. |
| Learning Checkpoint | Represents predefined measurement milestones throughout the learning process. | Enables continuous monitoring of learning progress rather than end-of-program evaluation only. |
| Assessment | Represents quizzes, assignments, projects, exams, or presentations. | Provides evidence used to evaluate competency development. |
| LMS Activity | Represents student interaction with the Learning Management System. | Provides behavioural evidence of engagement and participation. |
| Attendance | Represents participation in scheduled learning activities. | Complements engagement analytics and supports risk detection. |
| Survey | Represents student self-reported perceptions, confidence, and feedback. | Provides perception-based evidence that complements behavioural and assessment data. |
| Competency Measurement | Represents the evaluation of a competency using multiple evidence sources at a specific learning checkpoint. | Stores competency development history and supports longitudinal analysis. |
| Intervention | Represents support actions taken in response to analytical findings. | Enables evaluation of intervention effectiveness and continuous improvement. |
| KPI | Represents standardized business metrics. | Ensures consistent reporting and decision-making across dashboards. |
| Dashboard | Represents the presentation layer for stakeholders. | Communicates analytical insights to support educational decisions. |

---

# 6.4 High-Level Domain Relationships

The Learning Analytics Domain Model follows the educational lifecycle rather than the technical data flow.

```
Program
    │
contains
    ▼
Module
    │
delivered as
    ▼
Course Offering
    │
taught by
    ▼
Instructor
    │
contains
    ▼
Assessments
    │
produce
    ▼
Learning Evidence
    │
used in
    ▼
Learning Checkpoints
    │
evaluate
    ▼
Competency Measurements
    │
measure
    ▼
Competencies
    ▲
    │
Student
    │
belongs to
    ▼
Cohort
    │
generates
    ▼
Analytics
    │
calculate
    ▼
KPIs
    │
presented through
    ▼
Dashboards
    │
support
    ▼
Educational Decisions
    │
trigger
    ▼
Interventions
    │
drive
    ▼
Continuous Improvement
```

---

# 6.5 Core Concepts

## Learning Evidence

Competency development should not be measured using a single assessment. Instead, CLAF combines multiple evidence sources to create a more comprehensive representation of student learning.

Learning evidence may include:

- Assessment results
- Project performance
- LMS activity
- Attendance
- Student surveys

This evidence is evaluated at predefined Learning Checkpoints to determine competency attainment and learning progression.

---

## Learning Checkpoints

Learning Checkpoints represent predefined milestones during the learning process where competency development is evaluated.

Examples include:

- Beginning of semester (baseline)
- Every four weeks
- End of a module
- Completion of a major assessment
- End of semester

Rather than evaluating students only at the end of a program, Learning Checkpoints support continuous monitoring, early identification of learning difficulties, and timely educational interventions.

---

## Competency Measurement

Competency Measurement represents the evaluation of a student's competency at a specific Learning Checkpoint.

Each measurement combines multiple sources of learning evidence using configurable measurement rules.

This design enables:

- Historical competency tracking
- Growth analysis
- Learning trajectory analysis
- Cross-cohort comparisons
- Continuous improvement evaluation

---

## Configurable Measurement Rules

A key innovation of CLAF is the separation of competency definitions from measurement logic.

Instead of hardcoding competency calculations into software, measurement rules are configurable.

Each competency defines:

- Required evidence sources
- Weighting of each evidence source
- Expected competency level
- Performance thresholds
- Growth calculation methods

This approach allows institutions to introduce new competencies or modify existing measurement strategies without redesigning the analytics architecture.

---

# 6.6 Design Principles

The Learning Analytics Domain Model is guided by the following principles.

### Principle 1 — Continuous Learning

Learning should be measured as a continuous developmental process rather than a single end-of-program outcome.

---

### Principle 2 — Multi-Level Decision Support

Analytics should support educational decisions at multiple organizational levels, including students, instructors, academic advisors, modules, programs, and institutional leadership.

---

### Principle 3 — Evidence-Based Competency Measurement

Competencies should be evaluated using multiple sources of learning evidence rather than relying on a single assessment.

---

### Principle 4 — Standardized Business Metrics

Business metrics should be calculated once using standardized definitions and reused consistently across all dashboards and analytical applications.

---

### Principle 5 — Configurable Analytics

Competencies, measurement rules, KPIs, and analytical models should be configurable, enabling the framework to support different educational contexts without requiring architectural redesign.

---

### Principle 6 — Continuous Improvement

Analytics should not only describe learning outcomes but also support interventions, curriculum enhancement, teaching improvement, and evidence-based educational decision making.

### Phase 5 -Data Architecture

## 7.1 Data Architecture Overview
Vision
Objectives
High-level architecture diagram
## 7.2 Source Systems
Every source
Expected data
Ownership
Refresh frequency
## 7.3 Data Collection Layer
ETL
APIs
CSV ingestion
Versioning
Validation
## 7.4 Raw Zone
Purpose
Storage strategy
Naming convention
Version control
## 7.5 Clean Zone
Cleaning rules
Standardization
Validation framework
Data quality metrics
## 7.6 Integration Layer
Unified learner model
Joining strategy
Keys
Cross-system integration
## 7.7 Feature Store
Feature engineering philosophy
Feature catalog
Reusable features
## 7.8 Semantic Layer
KPI definitions
Business metrics
Configurable measurement rules
## 7.9 Analytics Engine
Statistics
Rule engine
ML integration
## 7.10 Data Flow
End-to-end pipeline
Lineage
Refresh cycle
## 7.11 Governance
Metadata
Security
GDPR
Auditing
## 7.12 Architectural Benefits
Why this architecture?
Scalability
Maintainability
Reusability
