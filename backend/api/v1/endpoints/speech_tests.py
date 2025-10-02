from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import aiofiles
from datetime import datetime

from core.database.connection import get_db
from core.database.models import TestResult, SpeechTestResult, TestSession, User, AudioFile
from core.llm.groq_service import groq_service

router = APIRouter()

class SpeechTestResponse(BaseModel):
    id: str
    session_id: str
    test_name: str
    transcription: Optional[str]
    analysis_result: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

@router.post("/submit", response_model=SpeechTestResponse)
async def submit_speech_test(
    session_id: str = Form(...),
    test_name: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit speech test with audio file for transcription and analysis
    """
    # Verify session exists
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user for context
    user = db.query(User).filter(User.id == session.user_id).first()
    user_context = {
        "age": user.age,
        "education_level": user.education_level,
        "language": user.language,
        "vision_type": user.vision_type
    }
    
    # Save audio file temporarily
    temp_dir = "/tmp/audio_files"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{str(uuid.uuid4())}_{audio_file.filename}")
    
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await audio_file.read()
        await out_file.write(content)
    
    try:
        # Transcribe audio using Groq Whisper
        transcription_result = await groq_service.transcribe_audio(temp_file_path)
        transcription = transcription_result["transcription"]
        
        # Get file info
        file_size = os.path.getsize(temp_file_path)
        
        # Analyze speech patterns
        analysis = await groq_service.analyze_speech_pattern(
            transcription,
            audio_duration=0,  # Would need to extract from audio file
            user_context=user_context
        )
        
        analysis_result = analysis["analysis"]
        
        # Create test result
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=str(session_id),
            test_name=test_name,
            test_type="speech",
            score=analysis_result.get("fluency_score", 0),
            max_score=100.0,
            risk_level=analysis_result.get("risk_level", "medium"),
            raw_data={"transcription": transcription},
            analysis_result=analysis_result,
            created_at=datetime.utcnow()
        )
        
        db.add(test_result)
        
        # Create speech test result
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name=test_name,
            audio_file_url=temp_file_path,  # In production, upload to Supabase Storage
            transcription=transcription,
            duration=0,  # Would extract from audio
            fluency_score=analysis_result.get("fluency_score", 0),
            coherence_score=analysis_result.get("coherence_score", 0),
            lexical_diversity=analysis_result.get("lexical_diversity", 0),
            grammatical_complexity=analysis_result.get("grammatical_complexity", 0),
            details=analysis_result
        )
        
        db.add(speech_result)
        
        # Create audio file record
        audio_record = AudioFile(
            id=str(uuid.uuid4()),
            user_id=session.user_id,
            test_result_id=test_result.id,
            file_url=temp_file_path,
            file_size=file_size,
            format=audio_file.filename.split('.')[-1]
        )
        
        db.add(audio_record)
        db.commit()
        db.refresh(test_result)
        
        # Convert UUIDs to strings for response
        return {
            "id": str(test_result.id),
            "session_id": str(test_result.session_id),
            "test_name": test_result.test_name,
            "score": test_result.score,
            "max_score": test_result.max_score,
            "risk_level": test_result.risk_level,
            "analysis_result": test_result.analysis_result,
            "audio_file_url": audio_file_url
        }
        
    except Exception as e:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Speech processing error: {str(e)}")

@router.get("/session/{session_id}", response_model=List[SpeechTestResponse])
async def get_session_speech_tests(session_id: str, db: Session = Depends(get_db)):
    """
    Get all speech test results for a session
    """
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "speech"
    ).all()
    
    # Convert UUIDs to strings for response
    return [{
        "id": str(result.id),
        "session_id": str(result.session_id),
        "test_name": result.test_name,
        "score": result.score,
        "max_score": result.max_score,
        "risk_level": result.risk_level,
        "analysis_result": result.analysis_result,
        "audio_file_url": result.raw_data.get("audio_file_url") if result.raw_data else None
    } for result in results]
