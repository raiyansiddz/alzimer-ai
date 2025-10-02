from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import uuid
import io
from pathlib import Path

from core.database.connection import get_db
from core.database.models import User, TestSession, TestResult, SpeechTestResult, AudioFile
from core.tests.speech_test_engine import speech_test_engine, UserType
from core.analysis.llm_analysis_engine import llm_analysis_engine
from core.services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class SpeechTestRequest(BaseModel):
    user_id: str
    session_id: str
    test_type: str

class CookieTheftResponse(BaseModel):
    user_id: str
    session_id: str
    transcription: str
    duration_seconds: float
    audio_file_url: Optional[str] = None

class NarrativeResponse(BaseModel):
    user_id: str
    session_id: str
    prompt_used: str
    transcription: str
    duration_seconds: float
    audio_file_url: Optional[str] = None

class NamingTestResponse(BaseModel):
    user_id: str
    session_id: str
    objects_presented: List[str]
    responses_given: List[str]
    response_times: List[float]
    accuracy_percentage: float

class VerbalFluencyResponse(BaseModel):
    user_id: str
    session_id: str
    category_or_letter: str
    words_generated: List[str]
    total_count: int
    time_taken: float

# BLIND USER SPEECH TESTS
@router.post("/blind/boston-naming-audio/start", summary="Start Boston Naming Test (Audio) for blind users")
async def start_boston_naming_audio_blind(request: SpeechTestRequest, db: Session = Depends(get_db)):
    """Start Boston Naming Test adapted for blind users with audio descriptions"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await speech_test_engine.run_boston_naming_audio(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Boston Naming Test (Audio)",
            test_type="speech",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Boston Naming Audio start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/boston-naming-audio/submit", summary="Submit Boston Naming Test responses for blind users")
async def submit_boston_naming_audio_blind(response: NamingTestResponse, db: Session = Depends(get_db)):
    """Submit Boston Naming Test responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Boston Naming Test (Audio)"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Calculate accuracy and prepare data
        correct_responses = sum(1 for presented, given in zip(response.objects_presented, response.responses_given)
                              if presented.lower() == given.lower())
        accuracy = (correct_responses / len(response.objects_presented)) * 100 if response.objects_presented else 0
        
        # Create speech test result
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Boston Naming Test (Audio)",
            transcription=" | ".join(response.responses_given),
            fluency_score=accuracy,
            coherence_score=85.0,  # Default for naming tasks
            details={
                "objects_presented": response.objects_presented,
                "responses_given": response.responses_given,
                "response_times": response.response_times,
                "accuracy_percentage": accuracy
            }
        )
        db.add(speech_result)
        
        # Update main test result
        test_result.score = correct_responses
        test_result.max_score = len(response.objects_presented)
        
        # Prepare analysis data
        speech_data = {
            "transcription": " | ".join(response.responses_given),
            "objects_presented": response.objects_presented,
            "responses_given": response.responses_given,
            "accuracy_percentage": accuracy,
            "response_times": response.response_times
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "blind"
        }
        
        # This would need a specific analysis method for naming tests
        # For now, using general speech analysis
        analysis_result = {
            "test_name": "Boston Naming Test (Audio)",
            "analysis_type": "naming_assessment",
            "accuracy": accuracy,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "clinical_notes": f"Naming accuracy: {accuracy:.1f}%, Average response time: {sum(response.response_times)/len(response.response_times):.2f}s"
        }
        
        test_result.analysis_result = analysis_result
        test_result.risk_level = "low" if accuracy >= 80 else "medium" if accuracy >= 60 else "high"
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "accuracy": accuracy,
            "correct_responses": correct_responses,
            "total_objects": len(response.objects_presented),
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Boston Naming Audio submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/narrative-speech/start", summary="Start Narrative Speech Sample for blind users")
async def start_narrative_speech_blind(request: SpeechTestRequest, db: Session = Depends(get_db)):
    """Start Narrative Speech Sample for blind users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await speech_test_engine.run_narrative_speech_sample(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Narrative Speech Sample",
            test_type="speech",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Narrative Speech start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/blind/narrative-speech/submit", summary="Submit Narrative Speech responses for blind users")
async def submit_narrative_speech_blind(response: NarrativeResponse, db: Session = Depends(get_db)):
    """Submit Narrative Speech responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Narrative Speech Sample"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create speech test result
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Narrative Speech Sample",
            audio_file_url=response.audio_file_url,
            transcription=response.transcription,
            duration=int(response.duration_seconds),
            details={
                "prompt_used": response.prompt_used,
                "word_count": len(response.transcription.split()),
                "duration_seconds": response.duration_seconds
            }
        )
        db.add(speech_result)
        
        # Prepare analysis data
        speech_data = {
            "transcription": response.transcription,
            "duration_seconds": response.duration_seconds,
            "word_count": len(response.transcription.split()),
            "narrative_topic": response.prompt_used
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "blind"
        }
        
        # Analyze narrative speech
        analysis_result = await llm_analysis_engine.analyze_cookie_theft_speech(speech_data, user_context)
        
        # Update main test result
        word_count = len(response.transcription.split())
        words_per_minute = (word_count / response.duration_seconds) * 60 if response.duration_seconds > 0 else 0
        
        test_result.score = word_count  # Using word count as a basic score
        test_result.max_score = 150  # Expected word count for good narrative
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "word_count": word_count,
            "words_per_minute": words_per_minute,
            "duration_seconds": response.duration_seconds,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Narrative Speech submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WEAK VISION USER SPEECH TESTS
@router.post("/weak-vision/cookie-theft/start", summary="Start Cookie Theft description for weak vision users")
async def start_cookie_theft_weak_vision(request: SpeechTestRequest, db: Session = Depends(get_db)):
    """Start Cookie Theft description test for weak vision users with large, high-contrast image"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await speech_test_engine.run_cookie_theft_large_image(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="Cookie Theft Description (Large Image)",
            test_type="speech",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"Cookie Theft Large Image start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weak-vision/cookie-theft/submit", summary="Submit Cookie Theft responses for weak vision users")
async def submit_cookie_theft_weak_vision(response: CookieTheftResponse, db: Session = Depends(get_db)):
    """Submit Cookie Theft responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "Cookie Theft Description (Large Image)"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create speech test result
        word_count = len(response.transcription.split())
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="Cookie Theft Description (Large Image)",
            audio_file_url=response.audio_file_url,
            transcription=response.transcription,
            duration=int(response.duration_seconds),
            details={
                "word_count": word_count,
                "duration_seconds": response.duration_seconds,
                "adaptations_used": ["large_image", "high_contrast"]
            }
        )
        db.add(speech_result)
        
        # Prepare analysis data
        key_elements = test_result.raw_data.get("key_elements", [])
        speech_data = {
            "transcription": response.transcription,
            "duration_seconds": response.duration_seconds,
            "word_count": word_count,
            "key_elements": key_elements,
            "information_units": []  # Would be calculated by analysis
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "vision_type": "weak_vision",
            "user_type": "weak_vision"
        }
        
        # Analyze Cookie Theft description
        analysis_result = await llm_analysis_engine.analyze_cookie_theft_speech(speech_data, user_context)
        
        # Update main test result
        test_result.score = word_count
        test_result.max_score = 100  # Expected word count
        test_result.analysis_result = analysis_result
        test_result.risk_level = analysis_result.get("analysis_result", {}).get("risk_level", "medium")
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "word_count": word_count,
            "duration_seconds": response.duration_seconds,
            "transcription": response.transcription,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"Cookie Theft Large Image submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weak-vision/cowat/start", summary="Start COWAT test for weak vision users")
async def start_cowat_weak_vision(request: SpeechTestRequest, db: Session = Depends(get_db)):
    """Start Controlled Oral Word Association Test for weak vision users"""
    try:
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_config = await speech_test_engine.run_cowat_test(request.user_id)
        
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            test_name="COWAT (F-A-S Test)",
            test_type="speech",
            raw_data=test_config,
            created_at=datetime.utcnow()
        )
        db.add(test_result)
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "test_config": test_config,
            "status": "started"
        }
    
    except Exception as e:
        logger.error(f"COWAT start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/weak-vision/cowat/submit", summary="Submit COWAT responses for weak vision users")
async def submit_cowat_weak_vision(response: VerbalFluencyResponse, db: Session = Depends(get_db)):
    """Submit COWAT responses and get analysis"""
    try:
        user = db.query(User).filter(User.id == response.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        test_result = db.query(TestResult).filter(
            TestResult.session_id == response.session_id,
            TestResult.test_name == "COWAT (F-A-S Test)"
        ).first()
        
        if not test_result:
            raise HTTPException(status_code=404, detail="Test result not found")
        
        # Create speech test result
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name="COWAT (F-A-S Test)",
            transcription=" | ".join(response.words_generated),
            duration=int(response.time_taken),
            fluency_score=response.total_count,
            details={
                "letter": response.category_or_letter,
                "words_generated": response.words_generated,
                "total_count": response.total_count,
                "time_taken": response.time_taken
            }
        )
        db.add(speech_result)
        
        # Prepare analysis data for verbal fluency
        fluency_data = {
            "fluency_type": "phonemic",
            "category_or_letter": response.category_or_letter,
            "words_list": response.words_generated,
            "total_count": response.total_count,
            "time_taken": response.time_taken
        }
        
        user_context = {
            "age": user.age,
            "education_level": user.education_level,
            "language": user.language,
            "user_type": "weak_vision"
        }
        
        # This would use a specific verbal fluency analysis method
        analysis_result = {
            "test_name": "COWAT (F-A-S Test)",
            "analysis_type": "verbal_fluency",
            "total_words": response.total_count,
            "words_per_minute": (response.total_count / response.time_taken) * 60 if response.time_taken > 0 else 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "clinical_notes": f"Generated {response.total_count} words for letter '{response.category_or_letter}' in {response.time_taken:.1f} seconds"
        }
        
        # Update main test result
        test_result.score = response.total_count
        test_result.max_score = 20  # Average expected for letter fluency
        test_result.analysis_result = analysis_result
        test_result.risk_level = "low" if response.total_count >= 15 else "medium" if response.total_count >= 10 else "high"
        
        db.commit()
        
        return {
            "test_result_id": test_result.id,
            "total_words": response.total_count,
            "letter": response.category_or_letter,
            "time_taken": response.time_taken,
            "words_per_minute": (response.total_count / response.time_taken) * 60 if response.time_taken > 0 else 0,
            "analysis": analysis_result,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"COWAT submit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AUDIO UPLOAD ENDPOINT
@router.post("/upload-audio", summary="Upload audio recording")
async def upload_audio_recording(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...),
    test_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload audio recording to Supabase Storage"""
    try:
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read file content
        file_content = await audio.read()
        
        # Upload to Supabase Storage
        file_url = await supabase_service.upload_audio_file(
            file_content=file_content,
            file_name=audio.filename,
            user_id=user_id
        )
        
        if not file_url:
            raise HTTPException(status_code=500, detail="File upload failed")
        
        # Create audio file record
        audio_file = AudioFile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_url=file_url,
            duration=0,  # Would need to be calculated
            file_size=len(file_content),
            format=audio.content_type,
            created_at=datetime.utcnow()
        )
        db.add(audio_file)
        db.commit()
        
        return {
            "audio_file_id": audio_file.id,
            "file_url": file_url,
            "status": "uploaded"
        }
    
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))