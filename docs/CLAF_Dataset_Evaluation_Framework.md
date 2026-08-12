# Configurable Learning Analytics Framework (CLAF)

## Dataset Evaluation Framework

### Purpose

The CLAF Dataset Evaluation Framework defines a structured and repeatable method for evaluating publicly available datasets before they are selected for implementation.

The evaluation is based on the CLAF Data Requirements and Entity Relationship Model.

The objective is not to find a dataset that contains every possible CLAF entity. Instead, the objective is to identify datasets that provide sufficient evidence to demonstrate the core analytical capabilities of CLAF while clearly documenting missing, derived, or simulated elements.

---

# 1. Dataset Selection Principles

A candidate dataset should be evaluated according to the following principles:

1. Alignment with the CLAF data contract
2. Ability to support longitudinal analysis
3. Availability of learner-level records
4. Availability of learning or assessment evidence
5. Ability to support cohort, module, or program analysis
6. Data quality and completeness
7. Documentation and provenance
8. Licensing and reuse conditions
9. Analytical value
10. Implementation feasibility

Dataset availability alone is not sufficient for selection.

---

# 2. Evaluation Dimensions

Each candidate dataset is evaluated across eight dimensions.

| Dimension                                | Weight |
|---|---:|
| CLAF Schema Alignment                    | 25% |
| Analytical Coverage                      | 20% |
| Temporal / Longitudinal Capability       | 15% |
| Data Quality                             | 10% |
| Documentation & Provenance               | 10% |
| Licensing & Reusability                  | 5% |
| Dataset Size & Technical Feasibility     | 5% |
| Educational Relevance                    | 10% |
| **Total**                                | **100%** |
 
---

# 3. Scoring Scale

Each dimension is scored from 1 to 5.

| Score | Meaning |
|---:|---|
| 1 | Very poor |
| 2 | Poor |
| 3 | Acceptable |
| 4 | Good |
| 5 | Excellent |

The weighted score is calculated as:

`Weighted Score = Dimension Score / 5 × Dimension Weight`

The final dataset score therefore ranges from 0 to 100.

---

# 4. Evaluation Criteria

## 4.1 CLAF Schema Alignment — 25%

Measures how well the dataset maps to the CLAF entity model.

Important entities include:

- Student
- Program
- Cohort
- Module
- Learning Activity
- Assessment
- Competency
- Outcome
- Intervention
- Time

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Very limited mapping to CLAF entities |
| 2 | Only one or two useful entities |
| 3 | Several core entities available |
| 4 | Most core entities available |
| 5 | Strong coverage of the core CLAF model |

---

## 4.2 Analytical Coverage — 20%

Measures whether the dataset can support the intended CLAF analytical use cases.

Examples:

- Student performance
- Engagement
- Competency measurement
- Growth
- Risk identification
- Cohort comparison
- Module analysis
- Program analysis

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Very limited analytical use |
| 2 | Supports one major use case |
| 3 | Supports several use cases |
| 4 | Supports most core use cases |
| 5 | Supports broad learner, curriculum, and outcome analytics |

---

## 4.3 Temporal / Longitudinal Capability — 15%

Measures whether the dataset contains sufficient time information to analyze change.

Important fields may include:

- Event timestamp
- Assessment date
- Activity date
- Week
- Semester
- Cohort period

This dimension is particularly important for CLAF because growth should be measured continuously rather than only at the end of a program.

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | No meaningful temporal information |
| 2 | Single time point |
| 3 | Multiple periods but limited granularity |
| 4 | Good longitudinal structure |
| 5 | Detailed learner-level temporal records |

---

# 5. Data Quality — 10%

Evaluate:

- Missing values
- Duplicate records
- Invalid values
- Inconsistent identifiers
- Data types
- Outliers
- Referential integrity

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Severe quality problems |
| 2 | Significant quality problems |
| 3 | Manageable quality issues |
| 4 | Good quality |
| 5 | Very high quality and consistency |

---

# 6. Documentation & Provenance — 10%

Evaluate whether the dataset provides:

- Original source
- Data dictionary
- Variable descriptions
- Collection methodology
- Context
- Publication date
- Dataset version
- Known limitations

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Almost no documentation |
| 2 | Limited documentation |
| 3 | Basic documentation |
| 4 | Good documentation |
| 5 | Comprehensive documentation and provenance |

---

# 7. Licensing & Reusability — 5%

Evaluate whether the dataset can legally be:

- Downloaded
- Analyzed
- Modified
- Included in a portfolio project
- Referenced in GitHub documentation

The exact license and usage conditions must be documented before the dataset is incorporated into the project.

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Unclear or restrictive |
| 2 | Significant uncertainty |
| 3 | Usable with limitations |
| 4 | Clearly reusable |
| 5 | Clear and suitable for project use |

---

# 8. Dataset Size & Technical Feasibility — 5%

Evaluate:

- File size
- Number of records
- Number of variables
- Processing requirements
- Local hardware requirements
- Suitability for the planned CLAF architecture

The dataset should be large enough to demonstrate the architecture but manageable on a local development environment.

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Impractical for the project |
| 2 | Difficult to process |
| 3 | Manageable with limitations |
| 4 | Easily manageable |
| 5 | Well suited to the project environment |

---

# 9. Educational Relevance — 10%

Evaluate whether the dataset represents a meaningful educational context.

Examples include:

- Higher education
- Online learning
- LMS activity
- Student assessment
- Academic progression
- Competency development
- Learning outcomes

### Scoring guidance

| Score | Description |
|---:|---|
| 1 | Weak educational relevance |
| 2 | Limited relevance |
| 3 | Reasonable relevance |
| 4 | Strong educational relevance |
| 5 | Directly aligned with CLAF's educational objectives |

---

# 10. Dataset Evaluation Matrix

Candidate datasets will be recorded using the following structure.

| Dataset | Schema Alignment | Analytical Coverage | Temporal | Quality | Documentation | License | Feasibility | Educational Relevance | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Candidate A | | | | | | | | | |
| Candidate B | | | | | | | | | |
| Candidate C | | | | | | | | | |

Scores are entered from 1–5.

The final weighted score is calculated using the defined dimension weights.

---

# 11. Dataset Decision Thresholds

The following thresholds will guide selection:

| Weighted Score               | Decision |
|---:                          |---|
| 80–100                       | Strong candidate |
| 70–79                        | Suitable with documented limitations |
| 60–69                        | Usable for specific demonstrations |
| <60                          | Reject unless required for a specific purpose |

A high score does not automatically guarantee selection.

A dataset may be rejected because of:

- Licensing restrictions
- Missing critical fields
- Poor provenance
- Inability to support longitudinal analysis
- Severe data quality problems

---

# 12. Data Contract Mapping

For every shortlisted dataset, the following mapping must be completed.

| CLAF Entity | Dataset Field(s) | Mapping Type | Availability |
|---|---|---|---|
| Student | | Direct / Derived | |
| Program | | Direct / Derived / Missing | |
| Cohort | | Direct / Derived / Missing | |
| Module | | Direct / Derived / Missing | |
| Learning Activity | | Direct / Derived / Missing | |
| Assessment | | Direct / Derived / Missing | |
| Competency | | Direct / Derived / Missing | |
| Outcome | | Direct / Derived / Missing | |
| Intervention | | Direct / Derived / Missing | |
| Time | | Direct / Derived | |

---

# 13. Mapping Classification

Each CLAF entity must be classified as one of the following:

### Direct

The dataset explicitly contains the required information.

Example:

`student_id` → `Student.student_id`

### Derived

The information can be reliably calculated from existing dataset fields.

Example:

`week_number` derived from `timestamp`.

### Mapped

The information can be connected through a documented external lookup or configuration.

Example:

An assessment mapped to a competency through a measurement rule.

### Missing

The dataset does not contain sufficient information.

Missing data must not be presented as if it originated from the source dataset.

### Synthetic

Data is intentionally generated to demonstrate a CLAF capability where no appropriate public data exists.

Synthetic data must be explicitly documented.

---

# 14. Source Data vs Derived Data

CLAF maintains a strict distinction between:

### Source Data

Data obtained directly from the original dataset.

### Clean Data

Source data after quality and formatting transformations.

### Derived Data

Metrics or attributes calculated from source data.

Examples:

- Percentage score
- Weekly engagement
- Growth rate
- Risk score

### Synthetic Data

Artificially generated data used only when necessary to demonstrate an architectural capability.

The provenance of all synthetic data must be documented.

---

# 15. Dataset Selection Decision

The final dataset selection must document:

1. Dataset name
2. Original source
3. URL
4. License
5. Dataset version/date
6. Number of records
7. Number of variables
8. Main entities represented
9. CLAF mapping coverage
10. Missing entities
11. Derived entities
12. Known limitations
13. Reason for selection

---

# 16. Selection Principle

The selected dataset should provide the strongest realistic foundation for demonstrating CLAF rather than simply maximizing the number of available columns.

The objective is to demonstrate that:

`Real Educational Data → CLAF Data Contract → Configurable Analytics`

can be implemented in a transparent and reproducible manner.

---

# 17. Expected Output

At the end of the dataset evaluation phase, CLAF should contain:

- A shortlist of candidate datasets
- A completed evaluation matrix
- A selected primary dataset
- Documented backup dataset(s)
- A CLAF-to-source data mapping
- Documented limitations
- Documented licensing and provenance