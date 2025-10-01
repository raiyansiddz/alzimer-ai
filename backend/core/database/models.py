from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from core.database.connection import Base
import json as jsonlib

# SQLite compatible UUID type
def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    education_level = Column(String)
    vision_type = Column(String)
    language = Column(String, nullable=False, default='en')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    test_sessions = relationship("TestSession", back_populates="user")
    reports = relationship("Report", back_populates="user")
    progress_tracking = relationship("ProgressTracking", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    voice_speed = Column(Float, default=1.0)
    voice_gender = Column(String, default='female')
    text_size = Column(String, default='medium')
    high_contrast = Column(Boolean, default=False)
    voice_guidance = Column(Boolean, default=True)
    interface_type = Column(String, default='mixed')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="preferences")

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    session_type = Column(String)
    status = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    overall_score = Column(Float)
    overall_risk_level = Column(String)
    next_recommended_date = Column(Date)
    
    user = relationship("User", back_populates="test_sessions")
    test_results = relationship("TestResult", back_populates="session")
    reports = relationship("Report", back_populates="session")

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey('test_sessions.id', ondelete='CASCADE'), index=True)
    test_name = Column(String, nullable=False)
    test_type = Column(String)
    score = Column(Float)
    max_score = Column(Float)
    risk_level = Column(String)
    raw_data = Column(JSON)
    analysis_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("TestSession", back_populates="test_results")
    cognitive_results = relationship("CognitiveTestResult", back_populates="test_result")
    speech_results = relationship("SpeechTestResult", back_populates="test_result")
    behavioral_results = relationship("BehavioralTestResult", back_populates="test_result")
    llm_logs = relationship("LLMAnalysisLog", back_populates="test_result")

class CognitiveTestResult(Base):
    __tablename__ = "cognitive_test_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'))
    test_name = Column(String, nullable=False)
    subtest_name = Column(String)
    score = Column(Float)
    max_score = Column(Float)
    response_time = Column(Integer)
    errors = Column(Integer)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="cognitive_results")

class SpeechTestResult(Base):
    __tablename__ = "speech_test_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'))
    test_name = Column(String, nullable=False)
    audio_file_url = Column(String)
    transcription = Column(Text)
    duration = Column(Integer)
    fluency_score = Column(Float)
    coherence_score = Column(Float)
    lexical_diversity = Column(Float)
    grammatical_complexity = Column(Float)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="speech_results")

class BehavioralTestResult(Base):
    __tablename__ = "behavioral_test_results"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'))
    test_name = Column(String, nullable=False)
    response_times = Column(Text)
    accuracy = Column(Float)
    efficiency = Column(Float)
    learning_curve = Column(JSON)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="behavioral_results")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    session_id = Column(String, ForeignKey('test_sessions.id', ondelete='CASCADE'))
    report_type = Column(String)
    file_url = Column(String, nullable=False)
    summary = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="reports")
    session = relationship("TestSession", back_populates="reports")

class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    test_name = Column(String)
    date = Column(Date)
    score = Column(Float)
    risk_level = Column(String)
    change_from_previous = Column(Float)
    trend = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress_tracking")

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    reminder_type = Column(String)
    next_reminder_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="reminders")

class LLMAnalysisLog(Base):
    __tablename__ = "llm_analysis_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'), index=True)
    llm_provider = Column(String)
    model_name = Column(String)
    prompt = Column(Text)
    response = Column(Text)
    processing_time = Column(Integer)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    test_result = relationship("TestResult", back_populates="llm_logs")

class AudioFile(Base):
    __tablename__ = "audio_files"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'))
    file_url = Column(String, nullable=False)
    duration = Column(Integer)
    file_size = Column(Integer)
    format = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ImageFile(Base):
    __tablename__ = "image_files"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'))
    test_result_id = Column(String, ForeignKey('test_results.id', ondelete='CASCADE'))
    file_url = Column(String, nullable=False)
    file_size = Column(Integer)
    format = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
