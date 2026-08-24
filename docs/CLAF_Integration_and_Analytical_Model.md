# CLAF Integration and Analytical Model

## Purpose

The CLAF integration layer transforms validated clean datasets into analytics-ready entities while preserving the semantic grain of each analytical domain.

The integration layer operates only on datasets that have passed clean-layer validation and have been marked as integration-ready.

The current implementation produces four analytical entities and validates their relationships before marking the analytics layer as ready for downstream metric calculation and BI modeling.

## Analytical Entities

The Sprint 5 analytical model contains four implemented entities:

1. Student Enrollment
   - one record per student, module, and presentation

2. Assessment Submission
   - one record per student and assessment

3. VLE Activity
   - one record per student, module, presentation, and activity day

4. Course Presentation
   - one record per module and presentation

## Grain and Source Mapping

| Analytical Entity | Grain | Primary Clean Sources |
|---|---|---|
| Student Enrollment | one row per `id_student + code_module + code_presentation` | `student_info.parquet`, `student_registration.parquet` |
| Assessment Submission | one row per `id_student + id_assessment` | `student_assessment.parquet`, `assessments.parquet` |
| VLE Activity | one row per `id_student + code_module + code_presentation + date` | `student_vle.parquet` |
| Course Presentation | one row per `code_module + code_presentation` | `courses.parquet` |

The integration layer must preserve the declared grain of each entity and avoid joins that multiply records unexpectedly. Any aggregation that changes grain must be explicit and validated.

---

## Student Enrollment Integration

### Grain

One row per:

`id_student + code_module + code_presentation`

### Clean Sources

- `student_info.parquet`
- `student_registration.parquet`

### Join Type

One-to-one join on:

- `id_student`
- `code_module`
- `code_presentation`

### Integration Rule

The join must preserve exactly 32,593 enrollment records.

No row multiplication or row loss is permitted.

### Analytical Attributes

The integrated Student Enrollment entity contains:

- student demographic attributes;
- educational background;
- socioeconomic information;
- previous attempts;
- studied credits;
- disability indicator;
- final result;
- registration date;
- unregistration date.

### Validation Expectations

After integration:

- row count must equal 32,593;
- the composite enrollment grain must remain unique;
- no unmatched registration records may exist;
- no unmatched student information records may exist.

### Implementation Result

The Student Enrollment integration was implemented successfully using a validated one-to-one join between `student_info.parquet` and `student_registration.parquet`.

The persisted analytical entity contains:

- 32,593 enrollment records;
- 14 columns;
- zero duplicate enrollment keys;
- 45 missing registration dates preserved;
- 22,521 missing unregistration dates preserved.

Output:

`data/analytics/student_enrollment.parquet`

---

## Assessment Submission Integration

### Grain

One row per:

`id_student + id_assessment`

### Clean Sources

- `student_assessment.parquet`
- `assessments.parquet`

### Join Type

Many-to-one join on:

- `id_assessment`

### Integration Rule

Each student assessment record must map to exactly one assessment definition.

The join must preserve exactly 173,912 student-assessment records.

### Analytical Attributes

The integrated Assessment Submission entity contains:

- student identifier;
- assessment identifier;
- submission date;
- banked-assessment indicator;
- score;
- module;
- presentation;
- assessment type;
- assessment due date;
- assessment weight.

### Validation Expectations

After integration:

- row count must equal 173,912;
- grain `id_student + id_assessment` must remain unique;
- no student-assessment record may be missing assessment metadata;
- the join must not multiply records.

### Implementation Result

The Assessment Submission integration was implemented successfully using a validated many-to-one join between `student_assessment.parquet` and `assessments.parquet`.

The persisted analytical entity contains:

- 173,912 student-assessment records;
- 10 columns;
- zero duplicate `id_student + id_assessment` keys;
- zero missing assessment metadata records;
- 173 missing scores preserved;
- 2,865 records with unavailable assessment due dates preserved.

Output:

`data/analytics/assessment_submission.parquet`

---

## VLE Activity Integration

### Grain

One row per:

`id_student + code_module + code_presentation + date`

The `date` field represents the activity day relative to the start of the module presentation.

### Clean Source

- `student_vle.parquet`

### Integration Strategy

The clean `student_vle` dataset contains source interaction observations that were intentionally preserved during preprocessing.

For the analytical layer, these observations are aggregated to student-day level within each module presentation.

The activity measure is:

`daily_clicks = SUM(sum_click)`

This explicitly changes the grain from source interaction observations to student-level daily engagement.

### Integration Rules

- all source `sum_click` values must contribute to `daily_clicks`;
- total clicks before and after aggregation must remain identical;
- the analytical grain must be unique;
- each activity record must belong to a valid student enrollment;
- module and presentation context must be preserved;
- source observations must not be removed before aggregation.

### Analytical Attributes

The VLE Activity entity contains:

- `id_student`;
- `code_module`;
- `code_presentation`;
- `date`;
- `daily_clicks`.

Site-level VLE metadata remains available in the clean layer for future activity-type analysis.

### Implementation Result

The VLE Activity analytical entity was implemented successfully by aggregating validated `student_vle.parquet` observations to the defined student-day grain.

The persisted analytical entity contains:

- 1,808,119 student-day activity records;
- 5 columns;
- zero duplicate analytical keys;
- zero missing values;
- 39,605,099 total clicks preserved from the clean source;
- daily click values ranging from 1 to 6,988.

The aggregation reduced the source interaction table from 10,655,280 rows to 1,808,119 analytical rows without changing total engagement volume.

Output:

`data/analytics/vle_activity.parquet`

---

## Course Presentation Entity

### Grain

One row per:

`code_module + code_presentation`

### Clean Source

- `courses.parquet`

### Purpose

The Course Presentation entity provides shared module and presentation context for the analytical layer.

It acts as a common reference entity for Student Enrollment, Assessment Submission, and VLE Activity.

### Analytical Attributes

- `code_module`;
- `code_presentation`;
- `module_presentation_length`.

### Integration Rules

- the composite key `code_module + code_presentation` must be unique;
- all 22 clean course-presentation records must be preserved;
- `module_presentation_length` must remain available for later time-based analytics;
- no analytical entity may reference a module-presentation combination that is absent from this entity.

### Implementation Result

The Course Presentation analytical entity was created successfully from the validated `courses.parquet` clean dataset.

The source already existed at the required analytical grain, so no join or aggregation was required. A composite-key validation was applied to protect the `code_module + code_presentation` grain.

The persisted analytical entity contains:

- 22 course-presentation records;
- 3 columns;
- zero duplicate course-presentation keys;
- zero missing values;
- module presentation lengths ranging from 234 to 269 days.

Output:

`data/analytics/course_presentation.parquet`

---

## Analytics-Layer Relationships

The analytical model uses Course Presentation and Student Enrollment as shared reference entities.

```text
                    Course Presentation
                           |
                           v
                   Student Enrollment
                    /             \
                   v               v
        Assessment Submission   VLE Activity
```

The following relationships are validated automatically:

1. `student_enrollment` → `course_presentation`
2. `assessment_submission` → `course_presentation`
3. `vle_activity` → `course_presentation`
4. `assessment_submission` → `student_enrollment`
5. `vle_activity` → `student_enrollment`

All five relationships currently pass with zero invalid references.

---

## Analytics-Layer Validation

Analytics-layer referential integrity is validated through:

`src/data_integration/analytics_validation.py`

The validation workflow:

- checks the five core analytical relationships;
- records child row counts;
- counts invalid references;
- determines an overall validation status;
- derives the `analytics_ready` flag;
- writes a machine-readable JSON summary.

Validation output:

`data/metadata/analytics_layer_validation_summary.json`

Current result:

```text
overall_status = passed
analytics_ready = True
relationships_validated = 5
```

---

## Integration Pipeline

The complete clean-to-analytics workflow is orchestrated through:

`src/data_integration/run_integration.py`

Run the integration pipeline from the project root with:

```bash
python -m src.data_integration.run_integration
```

The pipeline performs:

```text
data/clean/
    |
    +--> Student Enrollment
    |
    +--> Assessment Submission
    |
    +--> VLE Activity
    |
    +--> Course Presentation
    |
    v
data/analytics/
    |
    v
Analytics-Layer Validation
    |
    v
analytics_layer_validation_summary.json
    |
    v
analytics_ready = True / False
```

The current end-to-end integration pipeline completes successfully with:

```text
Analytics-layer validation completed with status 'passed'
Analytics ready: True
CLAF data integration pipeline completed
```

---

## Scope Boundary

The integration layer prepares relationally consistent analytical entities.

It does not yet:

- calculate final learning analytics KPIs;
- calculate weekly engagement change;
- generate risk scores;
- calculate competency attainment;
- perform predictive modeling;
- create the final Power BI semantic model;
- create dashboards.

These responsibilities belong to later CLAF layers.