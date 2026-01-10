# Job Skill Architecture API - POC

A FastAPI implementation demonstrating job skill architecture with required and recommended skills, based on the HR Open Standards Recruiting specification.

## Overview

This POC provides an API to explore how jobs are structured with their associated skills, distinguishing between required and recommended skills. The implementation follows the structure defined in the Recruiting folder's JSON schemas.

## Features

- 3 sample jobs with different skill requirements
- 8 distinct skills in the skills catalog
- API endpoints to query jobs and their skill architecture
- Separation of required vs recommended skills

## Sample Data

### Jobs
1. **Senior Backend Developer** (JDX-001) - TechCorp Solutions
2. **Full Stack Developer** (JDX-002) - DataSystems Inc
3. **DevOps Engineer** (JDX-003) - CloudTech Innovations

### Skills
1. Python Programming
2. FastAPI Development
3. SQL Database Design
4. Docker Containerization
5. AWS Cloud Services
6. Git Version Control
7. RESTful API Design
8. PostgreSQL

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Web UI

A simple web interface is available at the root URL:
- **Web UI**: `http://localhost:8000/`

The UI displays all jobs with their skills, clearly showing required vs recommended skills with color coding and statistics.

## API Endpoints

### Root
- `GET /` - API information and available endpoints

### Jobs
- `GET /api/jobs` - Get all jobs with their skills
- `GET /api/jobs/{job_id}` - Get a specific job by position ID
- `GET /api/jobs/{job_id}/skills` - Get job with skills separated by required/recommended
- `GET /api/jobs/{job_id}/skills/required` - Get only required skills for a job
- `GET /api/jobs/{job_id}/skills/recommended` - Get only recommended skills for a job

### Skills
- `GET /api/skills` - Get all available skills
- `GET /api/skills/{skill_name}` - Get a specific skill by name

## Example Usage

### Get all jobs
```bash
curl http://localhost:8000/api/jobs
```

### Get job with skill architecture
```bash
curl http://localhost:8000/api/jobs/JDX-001/skills
```

### Get only required skills
```bash
curl http://localhost:8000/api/jobs/JDX-001/skills/required
```

### Get all skills
```bash
curl http://localhost:8000/api/skills
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Data Model

The implementation follows the HR Open Standards structure:

- **Job**: Contains identifiers, hiring organization, name, position ID, date created, and skills
- **JobSkill**: Skill associated with a job, including annotation (required/preferred flags)
- **Skill**: Standalone skill definition with name, description, and years of experience

## Skill Annotations

Skills can be annotated with:
- `required`: Boolean indicating if the skill is required
- `preferred`: Boolean indicating if the skill is preferred/recommended
- `requiredAtHiring`: Boolean indicating if the skill must be present at hiring time
- `acquisitionDifficulty`: Numeric rating of difficulty to acquire the skill
