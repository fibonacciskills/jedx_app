from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
import os

# Mangum only needed for Vercel/Lambda - not for Render
# from mangum import Mangum

app = FastAPI(
    title="Job Skill Architecture API",
    description="POC API for demonstrating job skill architecture with required and recommended skills",
    version="1.0.0"
)

# Add CORS middleware for Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class Identifier(BaseModel):
    value: str
    schemeId: str = "UUID"
    description: Optional[str] = None
    schemeLink: Optional[str] = None


class HiringOrganization(BaseModel):
    legalName: str


class SkillAnnotation(BaseModel):
    required: Optional[bool] = False
    preferred: Optional[bool] = False
    requiredAtHiring: Optional[bool] = None
    acquisitionDifficulty: Optional[float] = None


class JobSkill(BaseModel):
    name: str
    description: Optional[str] = None
    yearsOfExperience: Optional[int] = None
    annotation: Optional[SkillAnnotation] = None


class Job(BaseModel):
    identifiers: List[Identifier]
    hiringOrganization: HiringOrganization
    name: str
    positionID: str
    dateCreated: str
    skills: List[JobSkill] = []


class Skill(BaseModel):
    name: str
    description: Optional[str] = None
    yearsOfExperience: Optional[int] = None


class JobWithSkillsResponse(BaseModel):
    job: Job
    required_skills: List[JobSkill]
    recommended_skills: List[JobSkill]


# JobPostingType Models (based on JobPostingType.json schema)
class ScaleAnnotation(BaseModel):
    required: Optional[bool] = None
    preferred: Optional[bool] = None
    requiredAtHiring: Optional[bool] = None
    acquisitionDifficulty: Optional[float] = None
    acquiredInternally: Optional[bool] = None
    descriptions: Optional[List[str]] = None


class AnnotatedDefinedTerm(BaseModel):
    name: str
    termCode: Optional[str] = None
    descriptions: Optional[List[str]] = None
    annotation: Optional[ScaleAnnotation] = None


class JDXOrganization(BaseModel):
    name: Optional[str] = None
    legalName: Optional[str] = None
    descriptions: Optional[List[str]] = None


class Place(BaseModel):
    name: Optional[str] = None
    address: Optional[dict] = None
    descriptions: Optional[List[str]] = None


class JobPosting(BaseModel):
    """JobPosting model based on JobPostingType.json schema"""
    identifiers: Optional[List[Identifier]] = []
    name: Optional[str] = None
    title: Optional[str] = None
    positionID: Optional[str] = None
    postingID: Optional[str] = None
    hiringOrganization: Optional[JDXOrganization] = None
    dateCreated: Optional[str] = None
    datePosted: Optional[str] = None
    dateModified: Optional[str] = None
    validFrom: Optional[str] = None
    validThrough: Optional[str] = None
    
    # Skills and competencies
    skills: Optional[List[AnnotatedDefinedTerm]] = []
    abilities: Optional[List[AnnotatedDefinedTerm]] = []
    knowledge: Optional[List[AnnotatedDefinedTerm]] = []
    competencies: Optional[List[AnnotatedDefinedTerm]] = []
    responsibilities: Optional[List[AnnotatedDefinedTerm]] = []
    tasks: Optional[List[AnnotatedDefinedTerm]] = []
    workActivities: Optional[List[AnnotatedDefinedTerm]] = []
    technologies: Optional[List[AnnotatedDefinedTerm]] = []
    
    # Experience and credentials
    requiredExperiences: Optional[List[dict]] = []
    preferredExperiences: Optional[List[dict]] = []
    requiredCredentials: Optional[List[dict]] = []
    preferredCredentials: Optional[List[dict]] = []
    requiredEducation: Optional[List[dict]] = []
    preferredEducation: Optional[List[dict]] = []
    
    # Job details
    jobLocation: Optional[Place] = None
    jobLocationTypes: Optional[List[str]] = []
    jobSchedules: Optional[List[AnnotatedDefinedTerm]] = []
    jobTerms: Optional[List[AnnotatedDefinedTerm]] = []
    jobBenefits: Optional[List[str]] = []
    baseSalaries: Optional[List[dict]] = []
    estimatedSalaries: Optional[List[dict]] = []
    
    # Additional fields
    employerOverview: Optional[List[str]] = []
    qualificationSummary: Optional[List[str]] = []
    formattedDescriptions: Optional[List[str]] = []
    shiftSchedules: Optional[List[str]] = []
    workHours: Optional[List[str]] = []
    
    # Categories
    industries: Optional[List[str]] = []
    industryCodes: Optional[List[AnnotatedDefinedTerm]] = []
    occupationCategories: Optional[List[AnnotatedDefinedTerm]] = []
    careerLevels: Optional[List[AnnotatedDefinedTerm]] = []
    experienceCategories: Optional[List[AnnotatedDefinedTerm]] = []
    educationLevels: Optional[List[AnnotatedDefinedTerm]] = []
    
    # Additional optional fields (many more available in schema)
    totalJobOpenings: Optional[int] = None
    jobImmediateStart: Optional[bool] = None
    disclaimers: Optional[List[str]] = []
    specialCommitments: Optional[List[str]] = []
    travelRequirements: Optional[List[str]] = []


# Sample Data
sample_skills = [
    Skill(name="Python Programming", description="Proficiency in Python programming language", yearsOfExperience=3),
    Skill(name="FastAPI Development", description="Experience building REST APIs with FastAPI framework", yearsOfExperience=2),
    Skill(name="SQL Database Design", description="Ability to design and optimize SQL databases", yearsOfExperience=4),
    Skill(name="Docker Containerization", description="Experience with containerization using Docker", yearsOfExperience=2),
    Skill(name="AWS Cloud Services", description="Knowledge of Amazon Web Services cloud platform", yearsOfExperience=3),
    Skill(name="Git Version Control", description="Proficiency with Git for version control", yearsOfExperience=5),
    Skill(name="RESTful API Design", description="Understanding of REST principles and API design", yearsOfExperience=3),
    Skill(name="PostgreSQL", description="Experience with PostgreSQL database management", yearsOfExperience=2),
]

sample_jobs = [
    Job(
        identifiers=[Identifier(value=str(uuid4()), schemeId="UUID")],
        hiringOrganization=HiringOrganization(legalName="TechCorp Solutions"),
        name="Senior Backend Developer",
        positionID="JDX-001",
        dateCreated="2024-01-15T10:00:00Z",
        skills=[
            JobSkill(
                name="Python Programming",
                description="Proficiency in Python programming language",
                yearsOfExperience=3,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="FastAPI Development",
                description="Experience building REST APIs with FastAPI framework",
                yearsOfExperience=2,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="SQL Database Design",
                description="Ability to design and optimize SQL databases",
                yearsOfExperience=4,
                annotation=SkillAnnotation(required=True, requiredAtHiring=False)
            ),
            JobSkill(
                name="Docker Containerization",
                description="Experience with containerization using Docker",
                yearsOfExperience=2,
                annotation=SkillAnnotation(preferred=True)
            ),
            JobSkill(
                name="AWS Cloud Services",
                description="Knowledge of Amazon Web Services cloud platform",
                yearsOfExperience=3,
                annotation=SkillAnnotation(preferred=True)
            ),
        ]
    ),
    Job(
        identifiers=[Identifier(value=str(uuid4()), schemeId="UUID")],
        hiringOrganization=HiringOrganization(legalName="DataSystems Inc"),
        name="Full Stack Developer",
        positionID="JDX-002",
        dateCreated="2024-02-01T09:30:00Z",
        skills=[
            JobSkill(
                name="Python Programming",
                description="Proficiency in Python programming language",
                yearsOfExperience=2,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="RESTful API Design",
                description="Understanding of REST principles and API design",
                yearsOfExperience=3,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="PostgreSQL",
                description="Experience with PostgreSQL database management",
                yearsOfExperience=2,
                annotation=SkillAnnotation(required=True, requiredAtHiring=False)
            ),
            JobSkill(
                name="Git Version Control",
                description="Proficiency with Git for version control",
                yearsOfExperience=3,
                annotation=SkillAnnotation(preferred=True)
            ),
            JobSkill(
                name="FastAPI Development",
                description="Experience building REST APIs with FastAPI framework",
                yearsOfExperience=1,
                annotation=SkillAnnotation(preferred=True)
            ),
        ]
    ),
    Job(
        identifiers=[Identifier(value=str(uuid4()), schemeId="UUID")],
        hiringOrganization=HiringOrganization(legalName="CloudTech Innovations"),
        name="DevOps Engineer",
        positionID="JDX-003",
        dateCreated="2024-02-10T14:20:00Z",
        skills=[
            JobSkill(
                name="Docker Containerization",
                description="Experience with containerization using Docker",
                yearsOfExperience=3,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="AWS Cloud Services",
                description="Knowledge of Amazon Web Services cloud platform",
                yearsOfExperience=4,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="Git Version Control",
                description="Proficiency with Git for version control",
                yearsOfExperience=4,
                annotation=SkillAnnotation(required=True, requiredAtHiring=True)
            ),
            JobSkill(
                name="Python Programming",
                description="Proficiency in Python programming language",
                yearsOfExperience=2,
                annotation=SkillAnnotation(preferred=True)
            ),
            JobSkill(
                name="SQL Database Design",
                description="Ability to design and optimize SQL databases",
                yearsOfExperience=2,
                annotation=SkillAnnotation(preferred=True)
            ),
        ]
    ),
]


# API Endpoints
@app.get("/")
async def root():
    """Serve the UI homepage"""
    # Try multiple paths for Vercel deployment
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "public", "index.html"),
        os.path.join(os.path.dirname(__file__), "..", "..", "public", "index.html"),
        "public/index.html",
    ]
    
    for html_path in possible_paths:
        try:
            if os.path.exists(html_path):
                return FileResponse(html_path)
        except Exception:
            continue
    
    return JSONResponse(content={
        "message": "Job Skill Architecture API",
        "version": "1.0.0",
        "endpoints": {
            "ui": "/",
            "jobs": "/api/jobs",
            "job_by_id": "/api/jobs/{job_id}",
            "job_with_skills": "/api/jobs/{job_id}/skills",
            "skills": "/api/skills",
            "skill_by_name": "/api/skills/{skill_name}"
        }
    })


@app.get("/api/jobs", response_model=List[Job])
async def get_all_jobs():
    """Get all jobs with their skills"""
    return sample_jobs


def transform_job_to_posting(job: Job) -> JobPosting:
    """Transform a Job to JobPosting format based on JobPostingType schema"""
    # Transform skills to AnnotatedDefinedTerm format
    skills = []
    for skill in job.skills:
        annotation = None
        if skill.annotation:
            annotation = ScaleAnnotation(
                required=skill.annotation.required,
                preferred=skill.annotation.preferred,
                requiredAtHiring=skill.annotation.requiredAtHiring,
                acquisitionDifficulty=skill.annotation.acquisitionDifficulty
            )
        skills.append(AnnotatedDefinedTerm(
            name=skill.name,
            descriptions=[skill.description] if skill.description else None,
            annotation=annotation
        ))
    
    # Transform hiring organization
    hiring_org = JDXOrganization(legalName=job.hiringOrganization.legalName)
    
    # Job-specific data based on positionID
    responsibilities = []
    required_experiences = []
    required_credentials = []
    
    if job.positionID == "JDX-001":  # Senior Backend Developer
        responsibilities = [
            AnnotatedDefinedTerm(
                name="Backend API Development",
                descriptions=["Design, develop, and maintain scalable REST APIs and microservices", "Implement business logic and data processing pipelines", "Optimize API performance and ensure high availability"]
            ),
            AnnotatedDefinedTerm(
                name="Database Architecture",
                descriptions=["Design and implement database schemas", "Optimize database queries and performance", "Manage database migrations and data integrity"]
            ),
            AnnotatedDefinedTerm(
                name="System Architecture",
                descriptions=["Architect scalable backend systems", "Design system integrations and data flows", "Lead technical design discussions and code reviews"]
            )
        ]
        required_experiences = [
            {
                "duration": "P5Y",
                "descriptions": ["Backend software development experience"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            },
            {
                "duration": "P3Y",
                "descriptions": ["API development and RESTful service design"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            }
        ]
        required_credentials = [
            {
                "programConcentration": "Computer Science",
                "descriptions": ["BS"]
            }
        ]
    elif job.positionID == "JDX-002":  # Full Stack Developer
        responsibilities = [
            AnnotatedDefinedTerm(
                name="Full Stack Development",
                descriptions=["Develop both frontend and backend components of web applications", "Create responsive user interfaces and RESTful APIs", "Integrate frontend and backend systems"]
            ),
            AnnotatedDefinedTerm(
                name="Database Management",
                descriptions=["Design and maintain database schemas", "Write efficient SQL queries and stored procedures", "Implement database optimization strategies"]
            ),
            AnnotatedDefinedTerm(
                name="Application Integration",
                descriptions=["Integrate third-party APIs and services", "Implement authentication and authorization", "Ensure seamless data flow between systems"]
            )
        ]
        required_experiences = [
            {
                "duration": "P3Y",
                "descriptions": ["Full stack web development experience"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            },
            {
                "duration": "P2Y",
                "descriptions": ["API design and database management"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            }
        ]
        required_credentials = [
            {
                "programConcentration": "Computer Science",
                "descriptions": ["BS"]
            }
        ]
    elif job.positionID == "JDX-003":  # DevOps Engineer
        responsibilities = [
            AnnotatedDefinedTerm(
                name="Infrastructure Management",
                descriptions=["Design, implement, and maintain cloud infrastructure", "Manage CI/CD pipelines and deployment automation", "Monitor and optimize system performance and reliability"]
            ),
            AnnotatedDefinedTerm(
                name="Container Orchestration",
                descriptions=["Manage containerized applications with Docker and Kubernetes", "Implement infrastructure as code (IaC)", "Ensure high availability and disaster recovery"]
            ),
            AnnotatedDefinedTerm(
                name="DevOps Practices",
                descriptions=["Implement automation for testing, building, and deployment", "Manage configuration and secrets", "Collaborate with development teams on deployment strategies"]
            )
        ]
        required_experiences = [
            {
                "duration": "P4Y",
                "descriptions": ["DevOps or infrastructure engineering experience"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            },
            {
                "duration": "P3Y",
                "descriptions": ["Cloud infrastructure management and CI/CD"],
                "experienceCategories": [{"descriptions": ["Work Experience"]}]
            }
        ]
        required_credentials = [
            {
                "programConcentration": "Computer Science",
                "descriptions": ["BS"]
            }
        ]
    
    return JobPosting(
        identifiers=job.identifiers,
        name=job.name,
        title=job.name,
        positionID=job.positionID,
        postingID=job.positionID,
        hiringOrganization=hiring_org,
        dateCreated=job.dateCreated,
        skills=skills,
        responsibilities=responsibilities,
        requiredExperiences=required_experiences,
        requiredCredentials=required_credentials,
        employerOverview=[f"Position at {job.hiringOrganization.legalName}"],
        qualificationSummary=[f"{job.name} position requiring various technical skills"]
    )


@app.get("/api/jobs/{job_id}", response_model=JobPosting)
async def get_job_by_id(job_id: str):
    """Get a specific job by position ID in JobPostingType format"""
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    # Transform to JobPosting format
    job_posting = transform_job_to_posting(job)
    return job_posting


@app.get("/api/jobs/{job_id}/skills", response_model=JobWithSkillsResponse)
async def get_job_with_skills_architecture(job_id: str):
    """Get a job with skills separated by required and recommended"""
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    required_skills = [
        skill for skill in job.skills 
        if skill.annotation and skill.annotation.required
    ]
    
    recommended_skills = [
        skill for skill in job.skills 
        if skill.annotation and skill.annotation.preferred and not skill.annotation.required
    ]
    
    return JobWithSkillsResponse(
        job=job,
        required_skills=required_skills,
        recommended_skills=recommended_skills
    )


@app.get("/api/skills", response_model=List[Skill])
async def get_all_skills():
    """Get all available skills"""
    return sample_skills


@app.get("/api/skills/{skill_name}", response_model=Skill)
async def get_skill_by_name(skill_name: str):
    """Get a specific skill by name"""
    skill = next((s for s in sample_skills if s.name.lower() == skill_name.lower()), None)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
    return skill


@app.get("/api/jobs/{job_id}/skills/required", response_model=List[JobSkill])
async def get_required_skills(job_id: str):
    """Get only required skills for a job"""
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    return [
        skill for skill in job.skills 
        if skill.annotation and skill.annotation.required
    ]


@app.get("/api/jobs/{job_id}/skills/recommended", response_model=List[JobSkill])
async def get_recommended_skills(job_id: str):
    """Get only recommended skills for a job"""
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    return [
        skill for skill in job.skills 
        if skill.annotation and skill.annotation.preferred and not skill.annotation.required
    ]


# HROpen Skills API Models (based on openapi.yaml)
class SkillKeyword(BaseModel):
    name: str
    value: Optional[str] = None


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


@app.get("/skills", response_model=SkillsResponse)
async def get_skills_api(identifier: str):
    """
    HROpen Skills API endpoint - Get skill assertions for a JEDx object
    
    Maps JEDx job skills to the Skills API format, where:
    - Required skills -> validationStatus: 'Validated'
    - Preferred skills -> validationStatus: 'Provisional'
    """
    # Extract job ID from identifier URI (e.g., "https://api.example.com/jedx/jobs/JDX-001" or "JDX-001")
    job_id = identifier.split("/")[-1] if "/" in identifier else identifier
    
    # Find the job
    job = next((j for j in sample_jobs if j.positionID == job_id), None)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with identifier {identifier} not found")
    
    # Build skill assertions from job skills
    skill_assertions = []
    for job_skill in job.skills:
        # Determine validation status based on annotation
        validation_status = "Validated"  # default for required
        proficiency_name = "Required"
        
        if job_skill.annotation:
            if job_skill.annotation.preferred and not job_skill.annotation.required:
                validation_status = "Provisional"
                proficiency_name = "Preferred"
            elif job_skill.annotation.required:
                validation_status = "Validated"
                proficiency_name = "Required"
        
        # Create skill URI (simplified - could use a proper skill taxonomy URI)
        skill_id = f"https://api.example.com/skills/{job_skill.name.lower().replace(' ', '-')}"
        
        # Build skill assertion
        skill_assertion = SkillAssertion(
            skill=SkillModel(
                id=skill_id,
                name=job_skill.name,
                description=job_skill.description
            ),
            proficiencyLevel=ProficiencyLevel(name=proficiency_name),
            validationStatus=validation_status,
            validFrom=job.dateCreated
        )
        skill_assertions.append(skill_assertion)
    
    # Build referenced object
    job_uri = f"https://api.example.com/jedx/jobs/{job.positionID}"
    referenced_object = ReferencedObject(
        id=job_uri,
        type="JobPosting"
    )
    
    return SkillsResponse(
        object=referenced_object,
        skills=skill_assertions
    )


# Serverless handler (for Vercel/Lambda - not needed for Render)
# Uncomment if deploying to Vercel:
# handler = Mangum(app)
