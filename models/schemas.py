"""
Pydantic models for data validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class JobStatus(str, Enum):
    """Job posting status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class CandidateStatus(str, Enum):
    """Candidate pipeline status"""
    NEW = "new"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class TaskType(str, Enum):
    """Agent task types"""
    JOB_DESCRIPTION = "job_description"
    RESUME_SCREENING = "resume_screening"
    INTERVIEW_SCHEDULING = "interview_scheduling"
    EMAIL_COMMUNICATION = "email_communication"
    ANALYTICS = "analytics"
    OFFER_GENERATION = "offer_generation"


# ============ Job Models ============

class JobRequirements(BaseModel):
    """Job requirements structure"""
    position: str
    department: Optional[str] = None
    experience_years: Optional[int] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education: Optional[str] = None
    location: Optional[str] = None
    employment_type: str = "full-time"
    salary_range: Optional[Dict[str, float]] = None


class JobDescription(BaseModel):
    """Complete job description"""
    id: Optional[str] = None
    title: str
    company_name: str
    department: Optional[str] = None
    location: str
    employment_type: str
    description: str
    responsibilities: List[str]
    requirements: List[str]
    preferred_qualifications: List[str]
    benefits: List[str] = []
    salary_range: Optional[str] = None
    status: JobStatus = JobStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Candidate Models ============

class Resume(BaseModel):
    """Parsed resume data"""
    candidate_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    certifications: List[str] = []
    raw_text: str


class CandidateProfile(BaseModel):
    """Candidate profile"""
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_path: Optional[str] = None
    parsed_resume: Optional[Resume] = None
    job_id: Optional[str] = None
    status: CandidateStatus = CandidateStatus.NEW
    match_score: Optional[float] = None
    screening_notes: Optional[str] = None
    interview_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ScreeningResult(BaseModel):
    """Resume screening result"""
    candidate_id: str
    job_id: str
    match_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    education_match: bool
    summary: str
    recommendation: str
    strengths: List[str]
    concerns: List[str]


# ============ Interview Models ============

class InterviewSlot(BaseModel):
    """Interview time slot"""
    start_time: datetime
    end_time: datetime
    interviewer: str
    location: Optional[str] = None
    meeting_link: Optional[str] = None


class InterviewSchedule(BaseModel):
    """Interview scheduling details"""
    candidate_id: str
    job_id: str
    interview_type: str  # phone, technical, behavioral, etc.
    slots: List[InterviewSlot]
    status: str = "scheduled"
    notes: Optional[str] = None


# ============ Communication Models ============

class EmailTemplate(BaseModel):
    """Email template"""
    template_type: str
    subject: str
    body: str
    variables: List[str] = []


class EmailMessage(BaseModel):
    """Email message"""
    to_email: EmailStr
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None


# ============ Agent Models ============

class AgentTask(BaseModel):
    """Task for agent execution"""
    task_id: str
    task_type: TaskType
    description: str
    input_data: Dict[str, Any]
    priority: int = 1
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationMessage(BaseModel):
    """Conversation message"""
    role: str  # user or assistant
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ConversationState(BaseModel):
    """Conversation state management"""
    session_id: str
    messages: List[ConversationMessage] = []
    context: Dict[str, Any] = {}
    active_tasks: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ============ Analytics Models ============

class HiringMetrics(BaseModel):
    """Hiring analytics"""
    total_jobs: int
    active_jobs: int
    total_candidates: int
    candidates_by_status: Dict[str, int]
    average_time_to_hire: Optional[float] = None
    average_match_score: Optional[float] = None
    top_skills_demanded: List[Dict[str, int]] = []
    interviews_scheduled: int
    offers_made: int


# ============ Response Models ============

class AgentResponse(BaseModel):
    """Standard agent response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    next_actions: Optional[List[str]] = None