# Job Skill Architecture API - Vercel Deployment

A FastAPI implementation demonstrating job skill architecture with required and recommended skills, configured for deployment on Vercel.

## Overview

This POC provides an API to explore how jobs are structured with their associated skills, distinguishing between required and recommended skills. The implementation follows the structure defined in the Recruiting folder's JSON schemas and is optimized for serverless deployment on Vercel.

## Features

- 3 sample jobs with different skill requirements
- 8 distinct skills in the skills catalog
- API endpoints to query jobs and their skill architecture
- Separation of required vs recommended skills
- Modern web UI for visualizing job skills
- Serverless-ready for Vercel deployment

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

## Local Development

### Installation

```bash
pip install -r requirements.txt
```

### Running Locally

For local development, you can use uvicorn directly:

```bash
uvicorn api.index:app --reload
```

Or use the Vercel CLI:

```bash
vercel dev
```

The API will be available at `http://localhost:8000`

## Vercel Deployment

### Prerequisites

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

### Deploy

1. From the project root directory, run:
   ```bash
   vercel
   ```

2. Follow the prompts to deploy

3. For production deployment:
   ```bash
   vercel --prod
   ```

### Project Structure

```
.
├── api/
│   └── index.py          # FastAPI application with serverless handler
├── public/
│   └── index.html        # Web UI
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md
```

## API Endpoints

### Root
- `GET /` - Serve the web UI

### Jobs
- `GET /api/jobs` - Get all jobs with their skills
- `GET /api/jobs/{job_id}` - Get a specific job by position ID
- `GET /api/jobs/{job_id}/skills` - Get job with skills separated by required/recommended
- `GET /api/jobs/{job_id}/skills/required` - Get only required skills for a job
- `GET /api/jobs/{job_id}/skills/recommended` - Get only recommended skills for a job

### Skills
- `GET /api/skills` - Get all available skills
- `GET /api/skills/{skill_name}` - Get a specific skill by name

## Web UI

The web UI is automatically served at the root URL (`/`) when deployed. It features:

- Visual distinction between required (red) and recommended (teal) skills
- Job cards with detailed information
- Statistics dashboard
- Responsive design
- Auto-refresh every 30 seconds

## Example Usage

### Get all jobs
```bash
curl https://your-project.vercel.app/api/jobs
```

### Get job with skill architecture
```bash
curl https://your-project.vercel.app/api/jobs/JDX-001/skills
```

### Get only required skills
```bash
curl https://your-project.vercel.app/api/jobs/JDX-001/skills/required
```

### Get all skills
```bash
curl https://your-project.vercel.app/api/skills
```

## API Documentation

Once deployed, interactive API documentation is available at:
- Swagger UI: `https://your-project.vercel.app/docs`
- ReDoc: `https://your-project.vercel.app/redoc`

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

## Technologies

- **FastAPI**: Modern Python web framework
- **Mangum**: ASGI adapter for AWS Lambda and Vercel serverless functions
- **Pydantic**: Data validation using Python type annotations
- **Vercel**: Serverless deployment platform

## Notes

- The application uses Mangum to adapt FastAPI for Vercel's serverless runtime
- Static files are served from the `public` directory
- All routes are handled through the FastAPI application in `api/index.py`
- CORS is enabled for cross-origin requests
