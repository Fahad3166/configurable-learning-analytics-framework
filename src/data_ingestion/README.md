# CLAF Data Ingestion

## Purpose

The data ingestion layer is responsible for registering and validating source datasets before downstream processing.

It preserves source fidelity and does not perform analytical transformations.

## Responsibilities

- Discover configured source files
- Validate file availability
- Capture file metadata
- Perform basic structural checks
- Record ingestion execution information
- Preserve raw source data

## Non-Responsibilities

The ingestion layer does not:

- clean data
- join datasets
- engineer analytical features
- calculate KPIs
- train machine-learning models
- prepare Power BI datasets

## Current Source

Open University Learning Analytics Dataset (OULAD)

Local source location:

`data/raw/oulad/`

Expected files:

- assessments.csv
- courses.csv
- studentAssessment.csv
- studentInfo.csv
- studentRegistration.csv
- studentVle.csv
- vle.csv

## Design Principle

Dataset-specific source definitions should be configurable rather than hard-coded throughout the Python implementation.