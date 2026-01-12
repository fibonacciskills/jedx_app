# JEDx and Skills API Recreation Guide

This document describes how to recreate the JEDx Job Posting API and HROpen Skills API implementation.

## Project Overview

This FastAPI application implements two main API standards:
1. **JEDx (Job Education Data Exchange)** - Job posting format based on `JobPostingType.json` schema
2. **HROpen Skills API** - Skills assertion format based on OpenAPI specification

## Prerequisites

- Python 3.11+ (tested with Python 3.13)
- Virtual environment (venv)

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

Create `requirements.txt`:
```
fastapi==0.104.1
pydantic>=2.9.0
uvicorn[standard]>=0.24.0
```

Install:
```bash
pip install -r requirements.txt
```

### 3. Project Structure

```
jedx_app/
├── api/
│   └── index.py          # Main FastAPI application
├── public/
│   └── index.html        # Web UI (optional)
├── requirements.txt
├── render.yaml           # Render deployment config (optional)
└── cursor.md             # This file
```

## JEDx API Implementation

### Overview

The JEDx API transforms internal job data into the standardized `JobPostingType` format, which includes:
- Skills with annotations (required/preferred)
- Responsibilities
- Required experiences
- Required credentials
- Hiring organization details

### Key Models

#### 1. Internal Job Model (Source Data)

```python
class Job(BaseModel):
    identifiers: List[Identifier]
    hiringOrganization: HiringOrganization
    name: str
    positionID: str
    dateCreated: str
    skills: List[JobSkill] = []

class JobSkill(BaseModel):
    name: str
    description: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    annotation: Optional[SkillAnnotation] = None
```

#### 2. JEDx JobPosting Model (Target Format)

```python
class JobPosting(BaseModel):
    """JobPosting model based on JobPostingType.json schema"""
    identifiers: Optional[List[Identifier]] = []
    name: Optional[str] = None
    title: Optional[str] = None
    positionID: Optional[str] = None
    postingID: Optional[str] = None
    hiringOrganization: Optional[JDXOrganization] = None
    dateCreated: Optional[str] = None
    
    # Skills and competencies
    skills: Optional[List[AnnotatedDefinedTerm]] = []
    responsibilities: Optional[List[AnnotatedDefinedTerm]] = []
    
    # Experience and credentials
    requiredExperiences: Optional[List[dict]] = []
    requiredCredentials: Optional[List[dict]] = []
    # ... many more optional fields
```

#### 3. AnnotatedDefinedTerm (Skills Format)

```python
class AnnotatedDefinedTerm(BaseModel):
    name: str
    termCode: Optional[str] = None
    descriptions: Optional[List[str]] = None
    annotation: Optional[ScaleAnnotation] = None

class ScaleAnnotation(BaseModel):
    required: Optional[bool] = None
    preferred: Optional[bool] = None
    requiredAtHiring: Optional[bool] = None
    acquisitionDifficulty: Optional[float] = None
    # ... other fields
```

### Transformation Function

The key transformation happens in `transform_job_to_posting()`:

```python
def transform_job_to_posting(job: Job) -> JobPosting:
    """Transform a Job to JobPosting format based on JobPostingType schema"""
    
    # 1. Transform skills
    skills = []
    for skill in job.skills:
        annotation = None
        if skill.annotation:
            annotation = ScaleAnnotation(
                required=skill.annotation.required,
                preferred=skill.annotation.preferred,
                requiredAtHiring=skill.annotation.requiredAtHiring
            )
        skills.append(AnnotatedDefinedTerm(
            name=skill.name,
            descriptions=[skill.description] if skill.description else None,
            annotation=annotation
        ))
    
    # 2. Transform organization
    hiring_org = JDXOrganization(legalName=job.hiringOrganization.legalName)
    
    # 3. Add job-specific data (responsibilities, experiences, credentials)
    # This can be job-specific or pulled from a database
    responsibilities_data = [...]  # Job-specific
    required_experiences_data = [...]  # Job-specific
    required_credentials_data = [...]  # Job-specific
    
    # 4. Return JobPosting
    return JobPosting(
        identifiers=job.identifiers,
        name=job.name,
        title=job.name,
        positionID=job.positionID,
        postingID=job.positionID,
        hiringOrganization=hiring_org,
        dateCreated=job.dateCreated,
        skills=skills,
        responsibilities=responsibilities_data,
        requiredExperiences=required_experiences_data,
        requiredCredentials=required_credentials_data,
        # ... other fields
    )
```

### Endpoint

```python
@app.get("/api/jobs/{job_id}", response_model=JobPosting)
async def get_job_by_id(job_id: str):
    """Get a specific job by position ID in JobPostingType format"""
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    job_posting = transform_job_to_posting(job)
    return job_posting
```

### Key Points

1. **Skills Transformation**: Convert `JobSkill` with simple annotations to `AnnotatedDefinedTerm` with `ScaleAnnotation`
2. **Descriptions**: Convert single description string to list format (`descriptions: List[str]`)
3. **Job-Specific Data**: Responsibilities, experiences, and credentials are populated based on `positionID` (could come from a database)
4. **Optional Fields**: The `JobPosting` model has many optional fields - only populate what you have data for

## Skills API Implementation

### Overview

The HROpen Skills API provides skill assertions for JEDx objects, mapping job skills to a standardized format with:
- Skill details (name, description, coded notation)
- Proficiency levels (Advanced, Proficient, Developing)
- Validation status (Validated, Provisional)
- Reference to the JEDx object

### Key Models

#### 1. Skills API Models

```python
class SkillModel(BaseModel):
    id: str  # URI format
    name: Optional[str] = None
    description: Optional[str] = None
    codedNotation: Optional[str] = None
    ctid: Optional[str] = None
    keywords: Optional[List[SkillKeyword]] = None
    verifications: Optional[List[dict]] = None

class ProficiencyLevel(BaseModel):
    type: str = Field(default="DefinedTerm", alias="@type")
    name: str
    
    class Config:
        populate_by_name = True

class SkillAssertion(BaseModel):
    type: str = Field(default="SkillAssertion", alias="@type")
    skill: SkillModel
    proficiencyLevel: ProficiencyLevel
    validationStatus: str  # Validated, Provisional, Proposed, Expired
    validFrom: str
    validUntil: Optional[str] = None
    
    class Config:
        populate_by_name = True

class ReferencedObject(BaseModel):
    id: str  # URI
    type: Optional[str] = None

class SkillsResponse(BaseModel):
    context: str = Field(default="https://schema.hropenstandards.org/4.5/recruiting/rdf/SkillsApi.json", alias="@context")
    object: Optional[ReferencedObject] = None
    proficiencyScales: Optional[List[dict]] = []
    skills: List[SkillAssertion]
    
    class Config:
        populate_by_name = True
```

### Important: Field Aliases

The Skills API uses JSON-LD format with `@type` and `@context` fields. Pydantic requires using `Field` with `alias`:

```python
# Use alias for special characters
type: str = Field(default="SkillAssertion", alias="@type")

# Enable both field name and alias
class Config:
    populate_by_name = True
```

This allows serialization to use `@type` in JSON while using `type` in Python code.

### Transformation Logic

The Skills API maps JEDx job skills to skill assertions:

```python
@app.get("/skills", response_model=SkillsResponse)
async def get_skills_api(identifier: str):
    """
    HROpen Skills API endpoint - Get skill assertions for a JEDx object
    """
    # 1. Extract job ID from identifier (supports URI or just ID)
    job_id = identifier.split("/")[-1] if "/" in identifier else identifier
    
    # 2. Find the job
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with identifier {identifier} not found")
    
    # 3. Build skill assertions
    skill_assertions = []
    for job_skill in job.skills:
        # Determine validation status and proficiency level
        validation_status = "Validated"
        proficiency_name = "Proficient"
        
        if job_skill.annotation:
            if job_skill.annotation.preferred and not job_skill.annotation.required:
                # Preferred only -> Provisional, Developing
                validation_status = "Provisional"
                proficiency_name = "Developing"
            elif job_skill.annotation.required:
                if job_skill.annotation.requiredAtHiring:
                    # Required at hiring -> Validated, Advanced
                    validation_status = "Validated"
                    proficiency_name = "Advanced"
                else:
                    # Required but not at hiring -> Validated, Proficient
                    validation_status = "Validated"
                    proficiency_name = "Proficient"
        
        # Create skill URI and coded notation
        skill_slug = job_skill.name.lower().replace(' ', '-')
        skill_id = f"https://example.com/skills/{skill_slug}"
        coded_notation = ''.join([word[:2].upper() for word in job_skill.name.split()[:2]]) + f"-{len(skill_assertions) + 1:03d}"
        
        # Build skill assertion
        skill_assertion = SkillAssertion(
            skill=SkillModel(
                id=skill_id,
                name=job_skill.name,
                description=job_skill.description,
                codedNotation=coded_notation
            ),
            proficiencyLevel=ProficiencyLevel(name=proficiency_name),
            validationStatus=validation_status,
            validFrom=job.dateCreated
        )
        skill_assertions.append(skill_assertion)
    
    # 4. Build referenced object
    job_uri = f"https://api.hropenstandards.org/jedx/jobs/{job.positionID}"
    referenced_object = ReferencedObject(
        id=job_uri,
        type="JobPosting"
    )
    
    # 5. Return SkillsResponse
    return SkillsResponse(
        object=referenced_object,
        skills=skill_assertions
    )
```

### Mapping Rules

**Validation Status:**
- `required=True` → `validationStatus: "Validated"`
- `preferred=True` (only) → `validationStatus: "Provisional"`

**Proficiency Levels:**
- `requiredAtHiring=True` → `"Advanced"`
- `required=True` (not at hiring) → `"Proficient"`
- `preferred=True` (only) → `"Developing"`

### Endpoint Usage

```
GET /skills?identifier=JDX-001
GET /skills?identifier=https://api.hropenstandards.org/jedx/jobs/JDX-001
```

Both formats work - the endpoint extracts the job ID from the identifier.

## Running Locally

### Development Server

```bash
source venv/bin/activate
python -m uvicorn api.index:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Test Endpoints

**JEDx API:**
```bash
curl http://localhost:8000/api/jobs/JDX-001
```

**Skills API:**
```bash
curl "http://localhost:8000/skills?identifier=JDX-001"
```

## Deployment

### Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: jedx-app
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api.index:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

2. Deploy via Render dashboard or CLI

### Vercel (Alternative)

For Vercel, you would need:
- `vercel.json` configuration
- `mangum` adapter (not currently used)
- Handler export: `handler = Mangum(app)`

Currently configured for Render deployment.

## Key Differences: JEDx vs Skills API

| Aspect | JEDx API | Skills API |
|--------|----------|------------|
| **Endpoint** | `/api/jobs/{job_id}` | `/skills?identifier={job_id}` |
| **Format** | JobPostingType schema | HROpen Skills API schema |
| **Skills Format** | `AnnotatedDefinedTerm` with `ScaleAnnotation` | `SkillAssertion` with `ProficiencyLevel` |
| **Field Names** | Standard Python names | JSON-LD with `@type`, `@context` (aliases) |
| **Focus** | Complete job posting | Skills with proficiency levels |
| **Links** | Self-contained | References JEDx object via URI |

## Additional Notes

1. **Data Storage**: Currently uses in-memory `sample_jobs` list. In production, connect to a database.
2. **Skill URIs**: Skill IDs are simplified (`https://example.com/skills/...`). In production, use proper skill taxonomy URIs.
3. **Coded Notation**: Currently auto-generated. In production, use standardized skill codes from taxonomies.
4. **Error Handling**: Basic error handling with HTTPException. Add more comprehensive error handling for production.
5. **CORS**: Currently allows all origins (`*`). Restrict in production.

## References

- JEDx Schema: `Recruiting/json/JobPostingType.json`
- Skills API Schema: `SkillsData/schema/openapi.yaml`
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://docs.pydantic.dev/
