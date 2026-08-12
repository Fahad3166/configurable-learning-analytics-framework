# CLAF Dataset Decision

## 1. Selected Dataset

**Dataset:** Open University Learning Analytics Dataset (OULAD)

OULAD has been selected as the primary dataset for the first CLAF implementation.

The dataset provides a sufficiently rich combination of student, course, assessment, registration, and virtual learning environment activity data to demonstrate the core CLAF analytical architecture.

---

## 2. Decision Rationale

OULAD was selected because it provides:

- Student-level learning data
- Module and presentation structure
- Cohort-like presentation periods
- Assessment definitions and outcomes
- Assessment submission behaviour
- LMS/VLE interaction data
- Longitudinal activity records
- Sufficient scale for demonstrating an analytical data pipeline
- Public and reproducible data suitable for a GitHub-based project

The dataset also contains multiple module presentations across different periods, enabling comparison across cohorts and module presentations.

---

## 3. Validated Data Relationships

The dataset profiling phase confirmed the following relationships:

| Relationship | Result |
|---|---|
| Assessment ID uniqueness | Validated |
| VLE site ID uniqueness | Validated |
| Registration students → StudentInfo | 0 missing |
| StudentAssessment students → StudentInfo | 0 missing |
| StudentAssessment assessment IDs → Assessments | 0 missing |
| StudentVLE VLE sites → VLE | 0 missing |
| StudentInfo module/presentation → Courses | 0 missing |

The `studentInfo` table was identified as being at a student × module × presentation grain rather than a student-only grain. Therefore, `id_student` is not treated as a standalone primary key for this table.

---

## 4. Temporal Suitability

OULAD provides sufficient temporal structure for longitudinal learning analytics.

The 22 module presentations have nominal durations between 234 and 269 days.

Observed VLE activity spans the full nominal duration for every presentation. Additional activity is also observed before the nominal presentation start.

The dataset therefore supports construction of a configurable analytical grain:

`student × module × presentation × week`

This supports longitudinal metrics such as:

- Weekly engagement
- Assessment progression
- Recent activity
- Previous-period activity
- Four-week comparison windows
- Growth and decline indicators

---

## 5. Limitations

OULAD does not directly provide all concepts required by the conceptual CLAF model.

The following are not directly available:

- Explicit competency definitions
- Explicit learning outcomes
- Instructor observations
- Survey responses
- Direct teaching-quality measures
- A complete institutional program hierarchy

These limitations will not be hidden or artificially filled.

Instead, CLAF will demonstrate how these concepts can be represented through configurable dimensions and measurement rules.

For example, competencies can be defined through configuration rather than hard-coded into the data pipeline.

---

## 6. CLAF Design Implication

The OULAD implementation will demonstrate the principle that the analytical framework should remain reusable while measurement definitions remain configurable.

The implementation will therefore separate:

1. Source data
2. Data quality and cleaning
3. Analytical entities
4. Measurement rules
5. KPI definitions
6. Competency configuration
7. Analytical calculations
8. Dashboard outputs

This allows the same analytical architecture to be reused with a different educational dataset without rebuilding the entire system from scratch.

---

## 7. Temporal Measurement Configuration

The prototype will use a configurable weekly temporal model.

Example:

```yaml
temporal_granularity:
  unit: week
  anchor: presentation_start
  days_per_week: 7

growth_measurement:
  window_size: 4
  comparison: previous_equal_window