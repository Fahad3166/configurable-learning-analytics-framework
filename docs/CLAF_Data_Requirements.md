# CLAF Data Requirements

## Purpose

CLAF requires a stable, learner-centric data model that can support multiple educational analytics use cases without redesigning the underlying analytical pipeline.

The framework separates relatively stable educational entities from configurable measurement rules. This allows the same architecture to measure different competencies, learning outcomes, engagement patterns, and improvement indicators by changing configuration rather than rebuilding the platform.

## Core Data Domains

| Domain | Purpose |
|---|---|
| Learner | Identify the learner and support learner-level analysis |
| Program & Cohort | Enable program and cohort comparison |
| Module  | Analyze curriculum and module-level performance |
| Learning Activity | Measure engagement and learning behavior |
| Assessment | Capture evidence of learning |
| Competency | Represent configurable competency frameworks |
| Learning Outcome | Measure attainment and achievement |
| Time | Enable longitudinal and growth analysis |
| Intervention | Evaluate support and improvement actions |


                         PROGRAM
                            │
                            │
                         COHORT
                            │
                            │
                         STUDENT
                            │
             ┌──────────────┼───────────────┐
             │              │               │
             ▼              ▼               ▼
          MODULE       LEARNING         ASSESSMENT
                         ACTIVITY            │
             │              │               │
             └──────────────┼───────────────┘
                            │
                            ▼
                       COMPETENCY
                            │
                            ▼
                       OUTCOME
                            │
                            ▼
                      GROWTH / RISK
                            │
                            ▼
                     INTERVENTION
                            │
                            ▼
                   CONTINUOUS IMPROVEMENT


                      TIME
                        │
                        ▼
Student ── Module ── Activity ── Assessment ── Competency
   │          │          │             │            │
   └──────────┴──────────┴─────────────┴────────────┘
                         │
                         ▼
                    Growth Trend