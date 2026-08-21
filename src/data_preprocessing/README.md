# CLAF Data Preprocessing

## Purpose

The CLAF data preprocessing layer transforms validated raw OULAD data into standardized, quality-controlled datasets suitable for downstream integration and analytics.

The layer operates on source data that has already passed ingestion-level file and schema validation. Preprocessing rules are defined centrally in `configs/preprocessing_rules.yaml` so that validation and transformation decisions remain explicit and reproducible.

## Supported Datasets

The preprocessing pipeline currently processes all seven OULAD source datasets:

- `courses.csv`
- `studentInfo.csv`
- `studentRegistration.csv`
- `assessments.csv`
- `studentAssessment.csv`
- `vle.csv`
- `studentVle.csv`

Each source dataset has a dedicated preprocessing module under `src/data_preprocessing/`.

## Responsibilities

The preprocessing layer is responsible for:

- enforcing configured data types;
- handling missing values according to explicit dataset rules;
- validating required and nullable columns;
- validating categorical and numeric values where configured;
- enforcing configured unique or composite keys;
- preserving repeated source observations when required by source semantics;
- validating cross-column constraints;
- producing standardized clean datasets in Parquet format;
- validating relationships between clean datasets;
- producing a machine-readable clean-layer validation summary.

## Duplicate Handling

Duplicate treatment is determined by the semantic grain of each dataset rather than by applying a global deduplication rule.

Datasets with configured unique or composite keys are checked for duplicate-key violations. For `studentVle`, repeated source observations are intentionally preserved because aggregating or removing them during preprocessing would alter the source-level interaction data. Aggregation is deferred to later analytical transformations where the required grain is explicitly defined.

## Clean-Layer Validation

After all seven datasets are written to the clean layer, the pipeline performs automated validation.

Table-level validation includes:

- expected-column checks;
- required-column null checks;
- configured data-type checks;
- configured key-uniqueness checks.

The validation layer also checks core referential relationships, including:

- `student_info` to `courses`;
- `student_registration` to `student_info`;
- `student_assessment` to `assessments`;
- `student_vle` to `vle`;
- `student_vle` to `student_info`.

The results are combined into an overall validation status and an `integration_ready` flag.

The machine-readable validation result is written to:

```text
data/metadata/clean_layer_validation_summary.json
```

## Data Flow

```text
data/raw/oulad/
        |
        v
Configuration-Driven Preprocessing
        |
        +--> Schema and type enforcement
        +--> Missing-value handling
        +--> Categorical and numeric validation
        +--> Key and duplicate-rule validation
        +--> Cross-column validation
        +--> Source-semantics preservation
        |
        v
data/clean/
        |
        +--> courses.parquet
        +--> student_info.parquet
        +--> student_registration.parquet
        +--> assessments.parquet
        +--> student_assessment.parquet
        +--> vle.parquet
        +--> student_vle.parquet
        |
        v
Clean-Layer Validation
        |
        +--> Table-level validation
        +--> Referential-integrity validation
        |
        v
clean_layer_validation_summary.json
        |
        v
integration_ready = True / False
```

## Running the Pipeline

The complete preprocessing and validation workflow can be executed from the project root with:

```bash
python -m src.data_preprocessing.run_preprocessing
```

The runner:

1. loads the project and preprocessing configuration;
2. preprocesses all seven OULAD datasets;
3. writes the clean Parquet datasets;
4. runs clean-layer validation;
5. writes the validation summary;
6. reports whether the clean layer is ready for integration.

## Non-Responsibilities

The preprocessing layer does not:

- join source entities into dimensional or analytical models;
- calculate final learning analytics KPIs;
- calculate competency scores;
- generate student risk scores;
- train machine-learning models;
- create Power BI semantic models or dashboards.

These responsibilities belong to later CLAF layers.