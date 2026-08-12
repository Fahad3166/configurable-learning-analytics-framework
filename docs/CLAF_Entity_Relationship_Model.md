## Configurable Learning Analytics Framework (CLAF)
### Entity Relationship Model

## Purpose
The CLAF Entity Relationship Model defines the core educational entities, their attributes, relationships, and data requirements.

The model follows a learner-centric design that supports:

Student success analytics
Competency assessment
Engagement analysis
Cohort comparison
Curriculum evaluation
Growth measurement
Risk identification
Continuous improvement

The data model is intentionally stable, while competencies, KPIs, and measurement rules remain configurable.

### 1. Entity Overview

## Entity	                Description
Student	                   Individual learner
Program	                   Academic program
Cohort	                   Group of students
Module	                   Course or subject
Learning Activity	       LMS interactions
Assessment	Learning       evidence
Competency	               Skills and capabilities
Outcome	Achievement        results
Intervention	           Support actions
Time	                   Temporal dimension


### 2. Entity Definitions

## 2.1 Student
Purpose
Represents the learner.

Attributes
## Field	     Type   	Required	Example
student_id	      String	Yes     	S001
cohort_id	      String	Yes	        C2025
program_id	      String	Yes	        P001
enrollment_date	  Date	    Yes         2025-09-01
status	          String	Yes	        Active
gender	          String	Optional	Female
age_group	      String	Optional	20-25

## Primary Key
student_id
Relationships
Student → Cohort
Student → Program
Student → Learning Activity
Student → Assessment
Student → Competency
Student → Outcome
Student → Intervention

## 2.2 Program
Purpose
Represents an educational program.

Attributes
## Field	      Type	Required	   Example
program_id	      String	Yes	        P001
program_name	  String	Yes	        MSc Data Science
level	          String	Optional	Master
department	      String	Optional	Computer Science

## Primary Key
program_id
Relationships
Program → Cohort
Program → Module
Program → Student


## 2.3 Cohort
Purpose
Represents a group of students.

Attributes
## Field	    Type	Required	Example
cohort_id	String	Yes	C2025
program_id	String	Yes	P001
start_date	Date	Yes	2025-09-01
end_date	Date	Yes	2027-06-30

Primary Key
cohort_id
Foreign Key
program_id

## 2.4 Module
Purpose
Represents a course or learning unit.

Attributes
## Field	Type	Required	Example
module_id	String	Yes	M001
module_name	String	Yes	Machine Learning
program_id	String	Yes	P001
credits	Integer	Optional	6
semester	Integer	Optional	2


Primary Key
module_id
Foreign Key
program_id

## 2.5 Learning Activity
Purpose
Represents learner engagement.

Attributes
Field	Type	Required	Example
activity_id	String	Yes	A001
student_id	String	Yes	S001
module_id	String	Yes	M001
activity_type	String	Yes	Video
duration_minutes	Float	Optional	35
timestamp	Datetime	Yes	2025-09-10 14:00

Primary Key
activity_id
Foreign Keys
student_id
module_id

## 2.6 Assessment
Purpose
Represents evidence of learning.

Attributes
## Field	Type	Required	Example
assessment_id	String	Yes	AS001
student_id	String	Yes	S001
module_id	String	Yes	M001
assessment_type	String	Yes	Quiz
score	Float	Yes	82
max_score	Float	Yes	100
date	Date	Yes	2025-10-01

Derived Fields
percentage
pass_fail
normalized_score

## 2.7 Competency
Purpose
Represents configurable competencies.

Attributes
## Field	Type	Required	Example
competency_id	String	Yes	COMP01
competency_name	String	Yes	Computational Thinking
level	Integer	Optional	3
framework	String	Optional	DigComp

## 2.8 Outcome
Purpose
Represents achievement.

Attributes
## Field	Type	Required	Example
outcome_id	String	Yes	O001
student_id	String	Yes	S001
competency_id	String	Yes	COMP01
attainment_level	Float	Yes	0.78
status	String	Yes	Achieved


## 2.9 Intervention
Purpose
Represents support actions.

Attributes
## Field	Type	Required	Example
intervention_id	String	Yes	I001
student_id	String	Yes	S001
intervention_type	String	Yes	Tutoring
date	Date	Yes	2025-10-15
reason	String	Optional	Low engagement


## 3. Relationship Model

PROGRAM
    │
    ├── COHORT
    │       │
    │       └── STUDENT
    │                │
    │                ├── LEARNING ACTIVITY
    │                │
    │                ├── ASSESSMENT
    │                │
    │                ├── OUTCOME
    │                │
    │                └── INTERVENTION
    │
    └── MODULE
             │
             ├── LEARNING ACTIVITY
             ├── ASSESSMENT
             └── COMPETENCY

## 4. Simplified ER Diagram

PROGRAM
   │
   ├── COHORT
   │      │
   │      ▼
   │   STUDENT
   │      │
   │      ├── ACTIVITY
   │      ├── ASSESSMENT
   │      ├── OUTCOME
   │      └── INTERVENTION
   │
   └── MODULE
           │
           ▼
      COMPETENCY

## 5. Analytical Principles

CLAF follows five principles:

1-Learner-Centric

All analytics originate from the learner.

2-Time-Aware

Growth and trends are measured over time.

3-Competency-Based

Competencies are configurable.

4-Multi-Level

5-Analytics support:

Student
Cohort
Module
Program
Institution
Continuous Improvement

Analytics should support interventions and curriculum enhancement.

## 6. Design Philosophy

The educational data model remains stable.

Configurable elements include:

Competencies
KPIs
Thresholds
Weights
Risk rules
Growth calculations

This enables CLAF to support different educational use cases without redesigning the architecture.

Why this matters

Now we have:

Educational Question
        ↓
Data Requirements
        ↓
Entity Model
        ↓
Target Schema
        ↓
Dataset Selection
        ↓
Data Mapping

This means when we search datasets next, we won't ask:

"Which dataset is available?"

We will ask:

"Which dataset best fits our CLAF schema?"