# CLAF Metrics and Analytics Engine

## 1. Purpose

The CLAF Metrics and Analytics Engine transforms validated analytical entities into interpretable learning analytics measures for students, instructors, advisors, program coordinators, and institutional decision-makers.

The metrics layer operates only on analytical datasets that have passed analytics-layer validation and have been marked as analytics-ready.

Metric definitions remain configurable where possible so that thresholds, time windows, weighting rules, and analytical interpretations can be adapted without rewriting the underlying data pipeline.

The metrics engine is designed around three principles:

1. calculate transparent and reproducible learning metrics;
2. preserve the distinction between zero, missing, and unavailable evidence;
3. provide validated metric entities for downstream dashboards, cohort analysis, student profiles, and interpretable risk indicators.


## 2. Metrics Layer Inputs

The metrics engine currently consumes the following validated analytical entities:

- `student_enrollment.parquet`
- `assessment_submission.parquet`
- `vle_activity.parquet`
- `course_presentation.parquet`

Assessment metric construction additionally uses:

- `data/clean/assessments.parquet`

The analytical entities provide the stable grains required by the metrics engine, while the clean assessment catalog preserves authoritative assessment definitions required for eligibility and observability analysis.


## 3. Design Principles

The CLAF metrics engine follows these principles:

1. Every metric must have an explicitly defined grain.
2. Metric calculations must preserve the declared analytical grain.
3. Configurable thresholds and windows should not be hard-coded into calculation logic.
4. Missing data must be distinguished from genuine zero activity or zero performance.
5. Aggregations must be reproducible and validated.
6. Student-level metrics must retain module and presentation context.
7. Participation boundaries must be respected when constructing expected learning activity.
8. Dataset observability limitations must not automatically be interpreted as learner failure.
9. Risk indicators must remain interpretable from their contributing metrics.
10. Metric outputs must be suitable for downstream BI and dashboard modeling.
11. Validation must succeed before metric artifacts are persisted.


## 4. Metric Domains

The CLAF metrics engine supports or plans to support the following analytical domains:

- engagement metrics;
- assessment-performance metrics;
- submission-behavior metrics;
- temporal change metrics;
- student learning profile metrics;
- cohort comparison metrics;
- configurable risk and improvement signals.

The implementation prioritizes transparent descriptive and comparative measures before composite risk scoring.


## 5. Metric Grains

### 5.1 Student Enrollment

Key:

`id_student + code_module + code_presentation`

Purpose:

Represents one student's learning profile within one module presentation.

This is the primary grain for combining engagement, assessment, submission, cohort, and later risk metrics.


### 5.2 Student Week

Key:

`id_student + code_module + code_presentation + week`

Purpose:

Supports temporal engagement, inactivity, change, and improvement analysis.


### 5.3 Course Presentation

Key:

`code_module + code_presentation`

Purpose:

Supports cohort and module-presentation comparison.


### 5.4 Assessment Submission

Key:

`id_student + id_assessment`

Purpose:

Represents individual student assessment behavior before aggregation to student-enrollment grain.

A metric must not silently change between these grains. Any transformation from one grain to another must be explicit in the calculation logic.


## 6. Metric Definition Contract

Each CLAF metric should have a clear specification before implementation.

A metric definition should describe:

- `metric_id`: stable machine-readable identifier;
- `name`: human-readable metric name;
- `domain`: analytical domain;
- `grain`: entity level at which the metric is calculated;
- `source`: analytical dataset or datasets required;
- `measure`: source field used in the calculation;
- `aggregation`: calculation or aggregation method;
- `time_window`: temporal window when applicable;
- `missing_value_rule`: treatment of unavailable observations;
- `zero_value_rule`: interpretation of genuine zero activity or performance;
- `parameters`: configurable thresholds, weights, or calculation settings;
- `output_field`: column produced by the metrics engine;
- `description`: analytical meaning of the metric.


## 7. Configuration Boundary

Configuration should control analytical values that may reasonably change between CLAF deployments, including:

- activity windows;
- comparison periods;
- performance thresholds;
- submission-timeliness thresholds;
- risk thresholds;
- metric weights.

Python code is responsible for:

- calculation methods;
- aggregation logic;
- grain enforcement;
- input validation;
- output validation;
- reproducible transformations.

This separates configurable analytical rules from implementation logic.


# 8. Engagement Metrics

## 8.1 Student-Level Engagement Metrics

The first student-level engagement metric set is calculated from:

`data/analytics/vle_activity.parquet`

Metric grain:

`id_student + code_module + code_presentation`

Implemented metrics:

| Metric | Output Field | Definition |
|---|---|---|
| Total VLE activity | `total_clicks` | Total recorded VLE clicks for the enrollment |
| Active days | `active_days` | Number of distinct days with recorded VLE activity |
| Last activity day | `last_activity_day` | Latest relative presentation day containing activity |
| Average clicks per active day | `avg_clicks_per_active_day` | Mean clicks across days on which the student was active |

The persisted artifact is:

`data/metrics/engagement_metrics.parquet`

Implementation result:

- 29,228 student-enrollment records with observed VLE activity;
- 7 columns;
- 0 duplicate student-enrollment keys;
- 0 missing metric values;
- 39,605,099 total clicks preserved from the analytical VLE Activity source.

The Student Enrollment analytical entity contains 32,593 enrollments overall.

Therefore, 3,365 valid enrollments have no observed VLE activity and are intentionally absent from this engagement-only metric table.

These enrollments are handled explicitly when the complete student learning profile is constructed rather than being silently converted to zero during the initial engagement aggregation.


# 9. Weekly Engagement and Temporal Metrics

## 9.1 Weekly Time Model

Weekly engagement metrics use the presentation-relative `date` field from the VLE Activity analytical entity.

Observed VLE activity includes interaction before presentation day 0. CLAF therefore uses the following convention:

- `week = 0`: observed pre-course activity where `date < 0`;
- `week = 1`: presentation days 0 through 6;
- `week = 2`: presentation days 7 through 13;
- subsequent weeks continue in seven-day intervals.

For activity on or after presentation day 0:

`week = floor(date / 7) + 1`

Pre-course activity is preserved because it represents genuine learner interaction, but it is separated from Week 1 so that it does not distort course-period engagement.


## 9.2 Student-Week Timeline Contract

Observed VLE activity alone cannot define the student-week timeline because students may legitimately have weeks with no activity.

CLAF therefore constructs a continuous eligible student-week spine from:

- Student Enrollment;
- Course Presentation;
- observed weekly VLE activity.

Student-week grain:

`id_student + code_module + code_presentation + week`


## 9.3 Course-Period Boundaries

For each enrollment, course-period weeks begin at presentation day 0.

When an unregistration date is available, the final eligible course day is:

`min(date_unregistration, module_presentation_length)`

When `date_unregistration` is unavailable:

`final_eligible_day = module_presentation_length`

The module presentation length is treated as an inclusive analytical boundary because validation of the OULAD VLE data identified legitimate activity recorded on that presentation-relative day.

Students whose recorded unregistration date occurs before presentation day 0 receive no course-period weeks.

Activity recorded after the student's defined participation boundary remains preserved in the analytical VLE Activity source but is excluded from participation-based student-week metrics.


## 9.4 Pre-Course Activity

Week 0 represents observed pre-course activity.

Week 0 is not generated automatically for every enrollment. It exists only when genuine pre-course VLE activity is present.

The generated eligible course-period student-week spine begins with Week 1.


## 9.5 Zero-Activity Weeks

For an otherwise eligible student-week with no recorded VLE activity:

`weekly_clicks = 0`

`weekly_active_days = 0`

This represents genuine absence of recorded activity during a period in which the student was eligible to participate.

It is analytically different from:

- missing data;
- pre-course activity;
- activity outside the participation period.


## 9.6 Weekly Engagement Implementation

The implemented student-week engagement artifact contains:

- 928,416 eligible student-week rows;
- 29,915 represented enrollments;
- 577,015 weeks with recorded VLE activity;
- 351,401 eligible weeks with zero recorded VLE activity;
- 0 duplicate student-week keys.

The artifact preserves:

`37,369,163`

clicks occurring within the defined eligible participation timeline.


## 9.7 Weekly Engagement Change

Week-over-week engagement change is calculated as:

`((current_week_clicks - previous_week_clicks) / previous_week_clicks) * 100`

The following rules apply:

- first eligible course week → change is undefined;
- positive previous week → positive current week → percentage change is calculated;
- positive previous week → zero current week → `-100%`;
- zero previous week → positive current week → change is undefined;
- zero previous week → zero current week → change is undefined.

Undefined changes remain missing rather than being converted to artificial zero or infinity.

The validated implementation produced:

- 570,208 mathematically valid percentage-change observations;
- 109,134 transitions to `-100%`;
- 0 infinite percentage-change values.

The persisted artifact is:

`data/metrics/student_week_engagement.parquet`

The artifact contains:

- 928,416 rows;
- 8 columns;
- 0 duplicate student-week keys;
- 0 invalid week values;
- 0 negative click values;
- 0 invalid weekly active-day values;
- 0 missing weekly click values;
- 0 missing weekly active-day values;
- 0 infinite percentage-change values.


# 10. Assessment Metrics

## 10.1 Overview

The assessment metrics layer transforms assessment definitions, student submissions, enrollment participation boundaries, and course presentation metadata into validated student-level learning measures.

Assessment metrics use the student-enrollment grain:

`id_student + code_module + code_presentation`

The implementation separates:

- assessment eligibility;
- assessment completion;
- scoring;
- coursework weighting;
- examination performance;
- submission timeliness.

This prevents analytically different forms of learning evidence from being combined without an explicit rule.

Implementation:

`src/metrics/assessment.py`

Persisted artifact:

`data/metrics/assessment_metrics.parquet`


## 10.2 Assessment Data Sources

The assessment pipeline uses:

- `data/clean/assessments.parquet`
- `data/analytics/assessment_submission.parquet`
- `data/analytics/student_enrollment.parquet`
- `data/analytics/course_presentation.parquet`

The authoritative assessment catalog comes from the clean assessment table rather than only from assessments appearing in student submissions.

The complete assessment catalog contains:

- 206 assessment definitions;
- 106 TMA assessments;
- 76 CMA assessments;
- 24 Exam assessments.

This preserves assessment definitions even when no student outcome records are observable for a particular assessment.


## 10.3 Assessment Eligibility

Assessment completion is evaluated only against assessment opportunities that fall within a student's participation period.

Each enrollment is matched with assessment definitions belonging to its module presentation.

Eligibility follows these rules:

1. When an assessment has an actual due date, the due date is used as its eligibility boundary.
2. When the actual due date is missing, `module_presentation_length` is used as the eligibility boundary.
3. If `date_unregistration` is missing, the student remains eligible for assessment opportunities within the presentation.
4. If `date_unregistration` exists, the assessment is eligible only when:

`eligibility_boundary <= date_unregistration`

The presentation-length fallback is used only for participation eligibility.

It is not interpreted as an artificial assessment due date.

The full-catalog eligibility model produced:

- 242,670 eligible student-assessment opportunities;
- 27,904 enrollments with at least one eligible assessment;
- 4,689 enrollments with zero eligible assessments;
- 0 duplicate student-assessment keys;
- 0 missing eligibility boundaries.

All 4,689 enrollments with zero eligible assessments had a known unregistration date and had unregistered before their first assessment opportunity.

Therefore, these enrollments should not be interpreted as having 0% assessment completion.

When the full student learning profile is constructed, assessment completion for these enrollments remains unavailable (`NA`) because no assessment became eligible during their participation period.


## 10.4 Assessment Observability

An assessment definition existing in the source catalog does not necessarily mean that student outcome data for that assessment are observable.

The full catalog contains:

`206 assessment definitions`

Only:

`188 assessment IDs`

appear at least once in the student assessment submission data.

The remaining 18 assessment definitions:

- are all Exam assessments;
- occur across 18 course presentations;
- have no recorded student submissions anywhere in the dataset;
- generate 18,485 otherwise eligible student-assessment opportunities.

Treating these structurally unobserved exams as ordinary unsubmitted assessments would convert a dataset observability limitation into apparent student non-completion.

CLAF therefore distinguishes between two concepts.

### Assessment Catalog Coverage

All 206 assessment definitions are preserved for metadata, traceability, and analytical transparency.

### Assessment Outcome Observability

For completion measurement, an assessment definition is considered observable when its `id_assessment` appears at least once in the student assessment submission source.

The final completion denominator therefore contains only assessment opportunities that are both:

1. eligible for the student; and
2. observable in the available outcome data.

This prevents unavailable dataset-level outcomes from being interpreted as individual student failures.


## 10.5 Assessment Completion

Assessment completion is calculated as:

`assessment_completion_rate = assessment_submission_count / eligible_assessment_count`

where:

- `eligible_assessment_count` represents eligible observable assessment opportunities;
- `assessment_submission_count` represents eligible assessments with an observed submission;
- `scored_assessment_count` represents eligible submitted assessments with an available score.

A submitted eligible assessment counts as completed even when its score is missing.

Missing scores are therefore treated separately from submission completion.

The final implementation produced:

- 224,185 observable eligible assessment opportunities;
- 172,244 eligible submitted assessments;
- 172,087 eligible scored assessments;
- 27,904 student-enrollment metric rows;
- 0 duplicate enrollment keys.

Completion distribution:

- 14,942 enrollments with 100% completion;
- 10,547 enrollments with partial completion;
- 2,415 enrollments with 0% completion;
- mean completion rate approximately 75.17%.

The distinction between zero and unavailable completion is preserved:

- `0` means eligible observable assessments existed but none were submitted;
- `NA` means a meaningful completion rate cannot be calculated because no assessment became eligible during the participation period.


## 10.6 Mean Assessment Score

`mean_score` is the arithmetic mean of available scores from eligible submitted assessments.

Only assessments with an available score contribute.

Missing scores are not converted to zero.

The implementation produced:

- 25,472 enrollments with a calculable mean score;
- mean enrollment-level score approximately 72.83;
- minimum 0;
- maximum 100.

There are 2,432 assessment-eligible enrollments without a calculable mean score because no eligible scored assessment evidence is available.

Their `mean_score` remains `NA`.


## 10.7 Coursework Weighted Performance

Coursework performance is calculated separately from examination performance.

Only TMA and CMA assessments participate in coursework weighting.

Rules:

- Exam assessments are excluded.
- Zero-weight coursework assessments are excluded from weighted-score calculation.
- Only eligible coursework assessments are considered.
- Missing scores are not interpreted as zero.
- Weighted performance uses scored positive coursework weight.
- Evidence coverage is reported separately.

Weighted coursework performance:

`coursework_weighted_score = Σ(score × weight) / Σ(scored positive coursework weight)`

Coverage:

`coursework_score_coverage = scored_coursework_weight / eligible_coursework_weight`

where:

- `eligible_coursework_weight` is total positive TMA/CMA weight for which the student was eligible;
- `scored_coursework_weight` is eligible positive coursework weight with an available score.

This separates observed performance from completeness of performance evidence.

Implementation results:

- 25,451 enrollments with positive eligible coursework weight;
- 23,217 with scored positive coursework weight;
- 13,917 with 100% score coverage;
- 9,300 with partial score coverage;
- 2,234 with 0% score coverage.

Total eligible positive coursework weight:

`2,256,135.5`

Total scored positive coursework weight:

`1,713,067.5`

Enrollment-level weighted score:

- mean approximately 70.74;
- minimum 0;
- maximum 100.

When coursework score coverage is zero:

`coursework_weighted_score = NA`

rather than zero.


## 10.8 Examination Performance

Exam performance remains separate from coursework performance.

`exam_score` is calculated from eligible Exam assessments with an available score.

The implemented data contain:

- 4,958 eligible scored exam records;
- 4,958 student enrollments with an exam score;
- one scored eligible exam per represented enrollment.

Enrollment-level exam score:

- mean approximately 65.58;
- minimum 0;
- maximum 100.

The implementation aggregates exam evidence at student-enrollment grain so that the metric remains reusable for datasets containing multiple exam components.

CLAF does not automatically combine `exam_score` and `coursework_weighted_score`.

Any future combined performance indicator must have an explicitly defined configurable rule.


## 10.9 Banked Assessments

The eligible assessment population contains 1,773 banked submissions.

Among them:

- 1,772 have an available score;
- 1 has a missing score;
- all have `date_submitted = -1`.

The `-1` submission value should not be interpreted as ordinary submission timing.

CLAF therefore applies the rule:

**Banked assessments remain valid evidence for completion and score-based metrics but are excluded from submission-timeliness metrics.**

This preserves transferred assessment evidence without artificially improving timeliness indicators.


## 10.10 Submission Timeliness

Submission timeliness is calculated only when meaningful timing evidence exists.

A submission enters the timeliness population when:

1. the assessment is eligible;
2. the assessment was submitted;
3. the actual assessment due date is available;
4. the assessment is not banked.

The presentation-length fallback used for eligibility is never substituted for a missing due date in timeliness calculations.

For each valid submission:

`days_from_due = date_submitted - assessment_due_date`

Interpretation:

- `< 0`: early;
- `= 0`: on the due date;
- `> 0`: late.

Student-level timeliness metrics:

- `timeliness_assessment_count`
- `mean_days_from_due`
- `late_submission_count`
- `on_time_submission_count`
- `on_time_submission_rate`

On-time rate:

`on_time_submission_rate = on_time_submission_count / timeliness_assessment_count`

A submission is on time when:

`days_from_due <= 0`

The valid timeliness population contains:

- 167,606 assessment submissions;
- 25,236 student enrollments;
- 89,180 early submissions;
- 29,357 submissions on the due date;
- 49,069 late submissions;
- 118,537 early or on-time submissions.

Missing timeliness metrics indicate unavailable valid timing evidence rather than poor submission behavior.


## 10.11 Final Assessment Metric Model

Persisted artifact:

`data/metrics/assessment_metrics.parquet`

Grain:

`id_student + code_module + code_presentation`

The artifact contains:

- 27,904 rows;
- 19 columns;
- 0 duplicate enrollment keys.

Fields:

- `id_student`
- `code_module`
- `code_presentation`
- `eligible_assessment_count`
- `assessment_submission_count`
- `scored_assessment_count`
- `assessment_completion_rate`
- `mean_score`
- `eligible_coursework_weight`
- `scored_coursework_weight`
- `coursework_score_coverage`
- `coursework_weighted_score`
- `exam_score`
- `scored_exam_count`
- `timeliness_assessment_count`
- `mean_days_from_due`
- `late_submission_count`
- `on_time_submission_count`
- `on_time_submission_rate`


## 10.12 Missing-Value Semantics

The assessment metric table intentionally preserves missing values when the required analytical evidence does not exist.

Examples:

- no scored assessment evidence → `mean_score = NA`;
- no positive-weight eligible coursework → coursework weighting unavailable;
- eligible positive-weight coursework but no scored coursework → `coursework_score_coverage = 0` and `coursework_weighted_score = NA`;
- no observed eligible exam score → `exam_score = NA`;
- no valid non-banked submission with an actual due date → timeliness metrics unavailable.

This preserves the distinction between:

- genuine zero;
- non-participation;
- missing evidence;
- structurally unavailable evidence.


## 10.13 Assessment Validation

The assessment artifact is validated before persistence.

Checks include:

- unique student-enrollment grain;
- positive eligible assessment counts;
- submitted count not exceeding eligible count;
- scored count not exceeding submitted count;
- completion rate within `[0, 1]`;
- mean score within `[0, 100]`;
- coursework weighted score within `[0, 100]`;
- coursework coverage within `[0, 1]`;
- exam score within `[0, 100]`;
- on-time rate within `[0, 1]`;
- late plus on-time counts equal the timeliness denominator.

Final result:

`status = passed`

Validation produced:

- 27,904 rows;
- 0 duplicate keys;
- 0 invalid eligible counts;
- 0 invalid submission counts;
- 0 invalid scored counts;
- 0 invalid completion rates;
- 0 invalid mean scores;
- 0 invalid coursework weighted scores;
- 0 invalid coursework coverage values;
- 0 invalid exam scores;
- 0 invalid on-time rates;
- 0 inconsistent timeliness counts.

The persisted Parquet artifact was read back and successfully revalidated.


# 11. Implemented Metric Catalog

## 11.1 Engagement

| Metric ID | Output Field | Grain |
|---|---|---|
| `engagement_total_clicks` | `total_clicks` | Student Enrollment |
| `engagement_active_days` | `active_days` | Student Enrollment |
| `engagement_last_activity_day` | `last_activity_day` | Student Enrollment |
| `engagement_avg_clicks_active_day` | `avg_clicks_per_active_day` | Student Enrollment |
| `engagement_weekly_clicks` | `weekly_clicks` | Student Week |
| `engagement_weekly_active_days` | `weekly_active_days` | Student Week |
| `engagement_weekly_change` | `weekly_click_change_pct` | Student Week |


## 11.2 Assessment Performance

| Metric ID | Output Field | Grain |
|---|---|---|
| `assessment_eligible_count` | `eligible_assessment_count` | Student Enrollment |
| `assessment_submission_count` | `assessment_submission_count` | Student Enrollment |
| `assessment_scored_count` | `scored_assessment_count` | Student Enrollment |
| `assessment_completion_rate` | `assessment_completion_rate` | Student Enrollment |
| `assessment_mean_score` | `mean_score` | Student Enrollment |
| `assessment_coursework_weight` | `eligible_coursework_weight` | Student Enrollment |
| `assessment_scored_coursework_weight` | `scored_coursework_weight` | Student Enrollment |
| `assessment_coursework_coverage` | `coursework_score_coverage` | Student Enrollment |
| `assessment_coursework_weighted_score` | `coursework_weighted_score` | Student Enrollment |
| `assessment_exam_score` | `exam_score` | Student Enrollment |
| `assessment_scored_exam_count` | `scored_exam_count` | Student Enrollment |


## 11.3 Submission Behavior

| Metric ID | Output Field | Grain |
|---|---|---|
| `submission_timeliness_count` | `timeliness_assessment_count` | Student Enrollment |
| `submission_mean_days_from_due` | `mean_days_from_due` | Student Enrollment |
| `submission_late_count` | `late_submission_count` | Student Enrollment |
| `submission_on_time_count` | `on_time_submission_count` | Student Enrollment |
| `submission_on_time_rate` | `on_time_submission_rate` | Student Enrollment |


# 12. Planned Metrics

The following metric domains have not yet been finalized and will be implemented after the validated engagement and assessment layers.


## 12.1 Student Learning Profile

The student learning profile will combine validated student-enrollment metrics with the complete Student Enrollment population.

Its purpose is to provide one consistent analytical entity for downstream dashboard and risk analysis while preserving the difference between:

- zero activity;
- zero performance;
- missing evidence;
- unavailable metrics.


## 12.2 Cohort Comparison

Planned cohort measures include:

- cohort mean engagement;
- cohort mean active days;
- cohort mean assessment performance;
- student engagement relative to the cohort;
- student assessment performance relative to the cohort.

Primary cohort grain:

`code_module + code_presentation`

Cohort metrics provide contextual interpretation rather than relying only on absolute thresholds.


## 12.3 Risk and Improvement Signals

Risk indicators will be introduced only after their underlying metrics have been independently implemented and validated.

Potential inputs include:

- low engagement;
- sustained decline in weekly activity;
- low assessment performance;
- incomplete assessments;
- late-submission behavior;
- performance relative to the relevant cohort.

Risk thresholds, weights, and classification rules will be configurable rather than embedded directly into metric calculation code.

The first implementation will prioritize interpretable rules before predictive machine-learning approaches.


# 13. Current Metrics-Layer Outputs

The currently validated metric artifacts are:

### Student Engagement

`data/metrics/engagement_metrics.parquet`

Grain:

`id_student + code_module + code_presentation`

Rows:

`29,228`


### Student-Week Engagement

`data/metrics/student_week_engagement.parquet`

Grain:

`id_student + code_module + code_presentation + week`

Rows:

`928,416`


### Assessment Metrics

`data/metrics/assessment_metrics.parquet`

Grain:

`id_student + code_module + code_presentation`

Rows:

`27,904`

All three metric artifacts have passed their implemented validation checks.


# 14. Metrics Engine Design Summary

The current CLAF metrics layer follows the analytical flow:

```text
Validated Analytical Entities
            |
            v
Participation and Eligibility Rules
            |
            v
Metric-Specific Transformations
            |
            v
Missing / Zero / Observability Semantics
            |
            v
Metric Validation
            |
            v
Validated Metric Artifacts
            |
            v
Student Learning Profile
            |
            v
Cohort Comparison
            |
            v
Risk and Improvement Signals
            |
            v
Power BI Dashboards
```

The implementation deliberately separates metric construction from interpretation.

Raw observations are first transformed into validated descriptive measures. Student profiles, cohort comparisons, and risk indicators are then built on top of those measures rather than directly from raw learning-event data.

This architecture supports CLAF's goal of providing a configurable learning analytics framework in which analytical rules can evolve while the underlying ingestion, preprocessing, integration, and metric layers remain reproducible and traceable.


### Assessment Performance Improvement

CLAF includes an optional longitudinal assessment improvement indicator for measuring how student performance changes during a course presentation. The indicator is designed as an improvement measure rather than as a required component of the primary risk classification.

#### Metric

`assessment_score_change`

#### Grain

Student Enrollment:

`id_student + code_module + code_presentation`

#### Assessment Evidence

The initial OULAD implementation uses scored coursework assessments of the following types:

- TMA
- CMA

Exam assessments are excluded because they do not provide suitable repeated coursework observations for an in-course progression measure.

Only assessments that:

- have a valid score,
- have a known assessment date,
- occur within the student's eligible participation period, and
- are available by the configured observation point

are considered.

#### Observation Point

Assessment improvement is evaluated at a configurable course-progress observation point.

For the initial OULAD configuration:

`observation_progress = 0.50`

This means that only assessment evidence available by approximately 50% of the module presentation is used.

Using an intermediate observation point supports the continuous-improvement purpose of CLAF and avoids defining improvement using information that becomes available only at the end of the course.

#### Assessment Windows

The metric compares two consecutive assessment windows.

For the initial configuration:

`window_assessments = 2`

The four most recent eligible scored coursework assessments available at the observation point are selected.

They are divided into:

- Previous window: the earlier two assessments
- Recent window: the most recent two assessments

The window means are calculated as:

`previous_assessment_mean = mean(previous 2 assessment scores)`

`recent_assessment_mean = mean(recent 2 assessment scores)`

The progression metric is:

`assessment_score_change = recent_assessment_mean - previous_assessment_mean`

A positive value represents increasing assessment performance, while a negative value represents declining assessment performance.

#### Minimum Evidence Requirement

At least four eligible scored coursework assessments are required:

`minimum_scored_assessments = 4`

When fewer than four assessments are available, assessment progression is unavailable rather than interpreted as zero improvement or decline.

This missingness is intentional and represents insufficient longitudinal evidence.

#### Improvement Classification

The initial OULAD configuration uses the following thresholds:

| Status | Rule |
| --- | --- |
| Improved | `assessment_score_change >= +10` |
| Stable | `-10 < assessment_score_change < +10` |
| Declined | `assessment_score_change <= -10` |

The thresholds are stored in `configs/kpis.yaml` and are therefore configurable rather than hard-coded into the metrics engine.

#### OULAD Validation Result

At the 50% observation point, 10,073 student enrollments had sufficient evidence for the four-assessment comparison.

The resulting classifications were:

| Classification | Enrollments | Percentage |
| --- | ---: | ---: |
| Stable | 6,316 | 62.70% |
| Declined | 2,399 | 23.82% |
| Improved | 1,358 | 13.48% |
| **Total** | **10,073** | **100.00%** |

The median assessment score change was `-1.5` points.

The observed score-change distribution ranged from `-68.5` to `+59.5` points.

#### Relationship to Risk Classification

Assessment improvement is not required for the primary CLAF risk classification.

The primary risk model continues to use the validated five-signal evidence framework:

1. engagement relative to cohort,
2. performance relative to cohort,
3. assessment completion,
4. submission timeliness, and
5. engagement trajectory.

Assessment progression is maintained as a separate longitudinal improvement indicator.

This separation prevents students with insufficient repeated assessment evidence from receiving additional risk merely because the improvement metric cannot be calculated.

#### Output Artifact

The validated assessment improvement artifact is:

`data/metrics/assessment_improvement.parquet`

The artifact uses Student Enrollment grain and contains 10,073 rows in the initial OULAD implementation.

The output includes:

- `id_student`
- `code_module`
- `code_presentation`
- `previous_assessment_mean`
- `recent_assessment_mean`
- `assessment_score_change`
- `assessment_observation_progress`
- `assessment_window_size`
- `assessment_improvement_status`

Validation confirms:

- duplicate Student Enrollment keys: 0
- missing assessment score changes: 0
- invalid improvement categories: 0
- previous assessment means outside 0–100: 0
- recent assessment means outside 0–100: 0

The assessment improvement artifact therefore passed CLAF metric-layer validation.