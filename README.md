# Configurable Learning Analytics Framework
### Functional Implementation & Technical Proof for IT:U Learning Data Analyst Assessment
The second-round task requested a conceptual data pipeline and analytics framework to measure computational thinking and digital competencies across diverse academic backgrounds at IT:U. While coding was not required for the presentation, I engineered a functional, parameter-driven prototype on GitHub (configurable-learning-analytics-framework) to validate the conceptual design.   I built this implementation to demonstrate how object-oriented design and dynamic configuration engines can translate high-level learning analytics models into scalable, production-ready software tools. It illustrates my ability to bridge data strategy with software engineering, ensuring that IT:U’s project-based LearnLab environment is backed by adaptive, extensible data infrastructure.

## 📄 Assessment Task & Presentation Concept

To demonstrate both analytical strategy and technical execution, this repository includes the original interview task alongside the corresponding design concept presentation:

* ### [📋 IT:U Second-Round Interview Task Guide (PDF)](./Second-Round Interviews Tasks LA.pdf)
  *The official scenario and requirements provided by IT:U regarding the measurement of Computational Thinking and Digital Competencies.*

* ### [📊 Learning Analytics Framework & Design Concept (Presentation)](./ITU_Final_Presentation.pdf)
  *The 5-slide presentation covering the proposed data collection strategy, data architecture, key metrics, and continuous feedback loops.*

---



# Configurable Learning Analytics Framework (CLAF)

CLAF is a configurable learning analytics framework designed to transform raw educational data into validated analytical models, learning metrics, early-warning indicators, and decision-support dashboards.

The framework separates reusable data-processing and analytics logic from configurable data sources, KPI definitions, competency definitions, measurement rules, thresholds, and analytical parameters. This allows the same architecture to be adapted to different learning environments without redesigning the complete analytics pipeline.

The current reference implementation uses the **Open University Learning Analytics Dataset (OULAD)** to demonstrate the framework using real student learning data.

> **Project Status:** Active Development  
> **Current Stage:** Metrics and Learning Analytics Engine  
> **Next Milestone:** Early-Warning Analytics and Power BI Dashboard

---

## Project Motivation

Educational institutions collect data from learning management systems, assessments, student information systems, Student Surveys, and digital learning environments. However, transforming these data into meaningful and actionable learning insights requires more than simply building dashboards.

The data must first be:

- collected consistently;
- cleaned and validated;
- integrated at clearly defined analytical grains;
- transformed into interpretable learning metrics;
- compared across meaningful time periods and cohorts;
- translated into indicators that can support educational decisions.

CLAF provides an end-to-end architecture for this process.

The framework is intended to support stakeholders such as:

- students;
- instructors and teachers;
- academic advisors;
- program coordinators;
- learning designers;
- institutional leadership.

---

## Framework Objective

The objective of CLAF is to provide a reusable analytical foundation for:

- student engagement analysis;
- assessment-performance analysis;
- submission-behavior analysis;
- temporal learning trends;
- cohort comparison;
- competency-oriented analytics;
- configurable early-warning indicators;
- risk and improvement signals;
- stakeholder-oriented dashboards;
- continuous improvement of learning and course design.

Rather than coupling analytical rules directly to one dataset, CLAF keeps the underlying pipeline stable while allowing learning analytics definitions and parameters to be configured.

---

## Architecture

The current CLAF architecture follows the analytical flow below:

```text
Raw Educational Data
        │
        ▼
Configurable Data Ingestion
        │
        ▼
Preprocessing / Clean Layer
        │
        ▼
Clean-Layer Validation
        │
        ▼
Analytical Integration
        │
        ▼
Analytics-Layer Validation
        │
        ▼
Configurable Metrics Engine
        │
        ▼
Learning Indicators
        │
        ▼
Early-Warning Analytics
        │
        ▼
Dashboards & Decision Support
        │
        ▼
Continuous Improvement
```

Each layer has a distinct responsibility.

The ingestion and preprocessing layers establish reliable data. The integration layer creates analysis-ready entities with explicitly defined grains and validated relationships. The metrics layer transforms these entities into interpretable learning measures that can later support early-warning indicators and dashboards.

---

## Configurable Design

A central design principle of CLAF is the separation between **stable implementation logic** and **configurable analytical rules**.

```text
Reusable Framework
        │
        ├── Data Ingestion
        ├── Preprocessing
        ├── Data Integration
        ├── Validation
        └── Metrics Calculation
                 │
                 ▼
        Configurable Layer
        │
        ├── Data Sources
        ├── KPI Definitions
        ├── Competency Definitions
        ├── Measurement Rules
        ├── Thresholds
        ├── Time Windows
        └── Analytical Parameters
```

This design allows analytical rules to evolve without requiring the entire data pipeline to be rewritten.

For example, future deployments can modify engagement windows, performance thresholds, competency mappings, risk thresholds, or metric weights through configuration while retaining the underlying processing architecture.

---

## Reference Implementation: OULAD

The current implementation uses the **Open University Learning Analytics Dataset (OULAD)** as the reference dataset.

OULAD provides student-level information covering areas such as:

- student demographics;
- module registrations;
- course presentations;
- assessments;
- assessment submissions;
- Virtual Learning Environment (VLE) activities.

The dataset provides a realistic environment for developing and validating the CLAF architecture on real educational data.

Raw OULAD data are **not stored in this repository**.

---

## Current Analytical Model

The validated analytics layer currently contains four primary analytical entities.

| Analytical Entity | Grain | Purpose |
|---|---|---|
| **Student Enrollment** | `id_student + code_module + code_presentation` | Represents a student's enrollment and learning context within a module presentation |
| **Assessment Submission** | `id_student + id_assessment` | Represents student assessment submission and performance information |
| **VLE Activity** | `id_student + code_module + code_presentation + date` | Represents aggregated daily digital learning activity |
| **Course Presentation** | `code_module + code_presentation` | Represents the contextual information for each module presentation |

These entities provide the analytical foundation for student-level, temporal, cohort-level, and early-warning metrics.

---

## Data Validation

Validation is treated as a first-class component of the framework rather than as a final reporting check.

CLAF currently performs validation across multiple pipeline stages, including:

- source and schema validation;
- preprocessing validation;
- analytical grain validation;
- duplicate-key checks;
- relationship validation;
- referential-integrity checks;
- analytics-readiness validation.

The current analytics layer validates relationships between:

```text
Student Enrollment
        │
        └──────────────► Course Presentation

Assessment Submission
        │
        ├──────────────► Student Enrollment
        │
        └──────────────► Course Presentation

VLE Activity
        │
        ├──────────────► Student Enrollment
        │
        └──────────────► Course Presentation
```

The current implementation successfully passes the analytics-layer relationship validation and produces:

```text
overall_status = passed
analytics_ready = true
```

Only validated analytical data are intended to proceed to downstream metric calculation.

---

## Metrics and Learning Analytics Engine

The metrics layer is currently under development.

Its purpose is to transform validated analytical entities into interpretable measures of student learning behavior and performance.

The initial metric domains include:

### Engagement

Examples include:

- total VLE activity;
- number of active learning days;
- average activity per active day;
- weekly activity;
- weekly active days;
- week-to-week engagement change.

### Assessment Performance

Examples include:

- average assessment score;
- weighted assessment performance;
- completed assessments;
- scored assessments.

### Submission Behavior

Examples include:

- on-time submissions;
- late submissions;
- on-time submission rate;
- average submission timing relative to the assessment due date.

### Cohort Comparison

Individual student measures will also be interpreted relative to their module presentation.

Planned comparisons include:

- student engagement relative to cohort engagement;
- student assessment performance relative to cohort performance;
- temporal change relative to relevant cohort patterns.

This provides context beyond simple absolute thresholds.

---

## Early-Warning Analytics

The planned early-warning layer will initially use **interpretable analytical indicators** rather than relying immediately on black-box predictive models.

Potential signals include:

```text
Low Engagement
        +
Sustained Engagement Decline
        +
Low Assessment Performance
        +
Late Submission Behaviour
        +
Incomplete Assessment Activity
        │
        ▼
Interpretable Early-Warning Indicators
```

Thresholds, weighting rules, and risk classifications will be configurable.

The objective is not simply to classify a student as "at risk", but to retain enough metric-level information to explain **why** the indicator was generated and support appropriate intervention.

---

## Dashboard and Decision Support

The planned dashboard layer will translate CLAF metrics into stakeholder-oriented learning analytics.

Initial dashboard areas will include:

```text
Student Overview
        │
        ├── Engagement
        ├── Assessment Performance
        ├── Submission Behaviour
        ├── Weekly Trends
        ├── Cohort Comparison
        └── Early-Warning Indicators
```

The first dashboard implementation is planned in **Power BI**.

The dashboard layer is currently under development and will be added after the core metrics and early-warning calculations have been validated.

---

## Current Implementation Status

CLAF is being implemented incrementally.

### Completed

- [x] Project architecture and repository structure
- [x] Dataset requirements and domain modeling
- [x] OULAD dataset evaluation
- [x] Configurable data ingestion
- [x] Source-data validation
- [x] Configurable preprocessing
- [x] Clean-layer validation
- [x] Analytical data integration
- [x] Student Enrollment analytical entity
- [x] Assessment Submission analytical entity
- [x] Daily VLE Activity analytical entity
- [x] Course Presentation analytical entity
- [x] Analytics-layer relationship validation
- [x] Analytics-readiness validation
- [x] Metrics architecture and metric-definition contract

### In Progress

- [ ] Configurable learning analytics metrics engine
- [ ] Student engagement metrics
- [ ] Weekly engagement metrics
- [ ] Assessment-performance metrics
- [ ] Submission-behavior metrics
- [ ] Student learning profile
- [ ] Cohort comparison metrics

### Planned

- [ ] Interpretable early-warning indicators
- [ ] Risk and improvement signals
- [ ] Power BI analytical model
- [ ] Learning analytics dashboard
- [ ] Continuous-improvement feedback layer

---

## Project Structure

```text
configurable-learning-analytics-framework/
│
├── configs/
│   ├── competencies.yaml
│   ├── config.yaml
│   ├── kpis.yaml
│   ├── logging.yaml
│   ├── measurement_rules.yaml
│   └── preprocessing_rules.yaml
│
├── data/
│   ├── raw/
│   ├── clean/
│   ├── analytics/
│   └── metadata/
│
├── docs/
│   └── Architecture, dataset, preprocessing,
│       integration and metrics documentation
│
├── notebooks/
│   └── Dataset exploration and evaluation
│
├── src/
│   ├── data_ingestion/
│   ├── data_preprocessing/
│   ├── data_integration/
│   ├── metrics/
│   └── utils/
│
├── README.md
├── requirements.txt
└── LICENSE
```

Generated datasets and raw educational data are excluded from version control.

---

## Metric Design Principles

Every CLAF metric follows an explicit definition contract.

A metric should identify:

```text
Metric
  │
  ├── Metric ID
  ├── Analytical Domain
  ├── Source
  ├── Measure
  ├── Grain
  ├── Aggregation
  ├── Time Window
  ├── Missing-Value Rule
  ├── Parameters
  └── Output Field
```

Important analytical distinctions are preserved.

For example:

- a missing assessment score is not automatically interpreted as zero;
- an unavailable assessment due date is not automatically interpreted as a late submission;
- missing activity information must be distinguished from genuine zero activity.

These rules help prevent apparently simple dashboard metrics from introducing misleading analytical assumptions.

---

## Reproducibility and Traceability

The framework is designed so that downstream metrics can be traced back through the analytical pipeline.

```text
Dashboard Indicator
        ↓
Learning Metric
        ↓
Metric Definition / Configuration
        ↓
Validated Analytical Entity
        ↓
Clean Dataset
        ↓
Raw Educational Data
```

This traceability is particularly important for early-warning analytics because stakeholders should be able to understand the evidence contributing to an analytical signal.

---

## Documentation

Detailed design and implementation documentation is available in the [`docs/`](docs/) directory.

The documentation covers areas such as:

- CLAF architecture and analytics design;
- dataset selection and evaluation;
- analytical data requirements;
- preprocessing and clean-layer design;
- integration and analytical modeling;
- metrics and analytics-engine design.

---

## Technology Stack

The current implementation uses:

- **Python 3.11**
- **Pandas**
- **PyArrow / Parquet**
- **YAML-based configuration**
- **Python logging**
- **Jupyter**
- **Git / GitHub**

Planned visualization and decision-support layer:

- **Power BI**

---

## Current Focus

The current development focus is the **Configurable Metrics and Learning Analytics Engine**.

The immediate milestone is to produce validated student engagement, assessment, submission-behavior, temporal, and cohort-comparison metrics.

These metrics will then provide the analytical foundation for the first interpretable **early-warning dashboard**.

---

## License

This project is released under the license included in the repository.

The OULAD dataset is an external dataset and remains subject to its own licensing and attribution requirements.
