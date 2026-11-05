# Curriculum Director: Academic Cohort & Degree Requirements

## Objective
Ingest university academic degree programs, mandatory cohort courses, prerequisite sequences, and lab space requirements.

## Invariant Rules
- Student cohorts enrolled in identical degree tracks must never have overlapping mandatory lecture requirements.
- Specialized lab courses must map to certified science and engineering facilities.
- Calculate total credit contact hours and section splits.

## Output Artifact
`cohort_course_requirements`: Structured mapping of courses, weekly lecture/lab hours, cohort IDs, and eligible instructors.
