I designed a configurable learning analytics framework in which the processing architecture is separated from dataset-specific sources, KPI definitions, competency definitions, and measurement rules. OULAD is the reference implementation used to demonstrate the framework.

              STABLE FRAMEWORK
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   Ingestion   Processing    Analytics
       │            │            │
       └────────────┼────────────┘
                    │
              reads configuration
                    │
                    ▼
           CONFIGURABLE LAYER
                    │
       ┌────────────┼──────────────┐
       ▼            ▼              ▼
    Sources        KPIs       Competencies
                                  │
                                  ▼
                           Measurement Rules