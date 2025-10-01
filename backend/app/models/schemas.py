from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


# User Registration
class UserRegistration(BaseModel):
    name: str
    age: int
    locale: str = "en"  # en, hi, es, etc.


class UserProfile(BaseModel):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    locale: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Memory Test
class MemoryTestInput(BaseModel):
    user_id: str
    response_text: Optional[str] = None
    response_time_ms: Optional[int] = None
    audio_file: Optional[str] = None  # Base64 or file path


class MemoryTestResult(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    correct_words: List[str]
    missed_words: List[str]
    score: int
    total_words: int = 5
    response_time_ms: Optional[int]
    cognitive_indicators: List[str]
    risk_level: str
    confidence: str
    notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Pattern Test
class PatternTestInput(BaseModel):
    user_id: str
    user_answer: str
    response_time_ms: Optional[int] = None


class PatternTestResult(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    is_correct: bool
    correct_answer: str
    user_answer: str
    response_category: str
    cognitive_indicators: List[str]
    risk_level: str
    confidence: str
    notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Clock Drawing Test
class ClockTestInput(BaseModel):
    user_id: str
    image_base64: str
    response_time_ms: Optional[int] = None
    image_metadata: Optional[Dict] = None


class ClockTestResult(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    overall_accuracy: float
    numbers_present: bool
    numbers_position: str
    hands_position: str
    hand_size_ratio: str
    spatial_organization: str
    cognitive_indicators: List[str]
    dementia_indicators: List[str]
    confidence: str
    risk_level: str
    clinical_notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Speech Test
class SpeechTestInput(BaseModel):
    user_id: str
    task_type: str  # reading, picture_description, spontaneous
    response_text: Optional[str] = None
    audio_file: Optional[str] = None  # Base64 or file path
    audio_quality: str = "good"


class SpeechTestResult(BaseModel):
    test_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    task_type: str
    fluency_score: float
    hesitation: str
    word_finding: str
    grammar_errors: str
    vocabulary: str
    coherence: str
    dementia_indicators: List[str]
    risk_level: str
    confidence: str
    notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Behavioral Monitoring
class BehavioralDataInput(BaseModel):
    user_id: str
    interaction_summary: Dict[str, Any]


class BehavioralAnalysisResult(BaseModel):
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    response_time_trend: str
    error_frequency: str
    navigation_efficiency: str
    learning_adaptation: str
    completion_consistency: str
    behavioral_indicators: List[str]
    risk_level: str
    confidence: str
    clinical_notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Comprehensive Report
class ReportRequest(BaseModel):
    user_id: str
    locale: str = "en"
    baseline: Optional[Dict] = None


class ClinicalReport(BaseModel):
    overall_risk_score: float
    risk_level: str
    confidence: str
    key_findings: List[str]
    significant_indicators: List[str]
    baseline_comparison: str
    clinical_interpretation: str
    recommendations: List[str]
    follow_up: str
    red_flags: List[str]


class PatientFriendlyReport(BaseModel):
    summary: str
    what_this_means: str
    key_findings: List[str]
    next_steps: List[str]
    reassurance: str


class ComprehensiveReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    clinical_report: ClinicalReport
    patient_friendly: PatientFriendlyReport
    timestamp: datetime = Field(default_factory=datetime.utcnow)
