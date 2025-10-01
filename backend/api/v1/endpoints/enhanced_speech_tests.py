from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import aiofiles
from datetime import datetime
import tempfile

from core.database.connection import get_db
from core.database.models import TestResult, SpeechTestResult, TestSession, User, AudioFile
from core.llm.enhanced_groq_service import enhanced_groq_service

router = APIRouter()

class SpeechTestContext(BaseModel):
    test_type: str  # 'fluency', 'description', 'reading', 'conversation', 'word_list'
    prompt_text: Optional[str] = None
    expected_duration: Optional[int] = None
    language: Optional[str] = "en"

class EnhancedSpeechTestResponse(BaseModel):
    id: str
    session_id: str
    test_name: str
    test_type: str
    transcription: Optional[str]
    audio_features: Optional[Dict[str, Any]]
    linguistic_analysis: Optional[Dict[str, Any]]
    acoustic_analysis: Optional[Dict[str, Any]]
    temporal_analysis: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: Optional[Dict[str, Any]]
    processing_time: Optional[int]
    
    class Config:
        from_attributes = True

@router.post("/enhanced/submit", response_model=EnhancedSpeechTestResponse)
async def submit_enhanced_speech_test(
    session_id: str = Form(...),
    test_name: str = Form(...),
    test_context: str = Form(...),  # JSON string of SpeechTestContext
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit speech test with comprehensive analysis including acoustic features
    """
    # Parse test context
    import json
    try:
        context_data = json.loads(test_context)
        test_context_obj = SpeechTestContext(**context_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid test context: {str(e)}")
    
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
        "vision_type": user.vision_type,
        "name": user.name
    }
    
    # Validate audio file
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Create temp directory and save file
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, f"{str(uuid.uuid4())}_{audio_file.filename}")
    
    try:
        # Save uploaded file
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await audio_file.read()
            await out_file.write(content)
        
        # Perform enhanced speech analysis
        analysis_result = await enhanced_groq_service.analyze_speech_detailed(
            temp_file_path,
            context_data,
            user_context
        )
        
        # Extract components
        audio_features = analysis_result.get("audio_features", {})
        transcription_data = analysis_result.get("transcription", {})
        analysis = analysis_result.get("analysis", {})
        
        # Calculate overall scores
        linguistic_analysis = analysis.get("linguistic_analysis", {})
        overall_score = (
            linguistic_analysis.get("fluency_score", 0) +
            linguistic_analysis.get("coherence_score", 0) +
            linguistic_analysis.get("lexical_diversity", 0)
        ) / 3
        
        risk_level = analysis.get("risk_assessment", {}).get("overall_risk", "medium")
        
        # Create test result record
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=str(session_id),
            test_name=test_name,
            test_type="speech",
            score=float(overall_score),
            max_score=100.0,
            risk_level=risk_level,
            raw_data={
                "test_context": context_data,
                "audio_features": audio_features,
                "transcription_data": transcription_data
            },
            analysis_result=analysis,
            created_at=datetime.utcnow()
        )
        
        db.add(test_result)
        
        # Create detailed speech test result
        speech_result = SpeechTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name=test_name,
            audio_file_url=f"temp://{temp_file_path}",  # In production, upload to Supabase Storage
            transcription=transcription_data.get("text", ""),
            duration=int(audio_features.get("duration", 0)),
            fluency_score=linguistic_analysis.get("fluency_score", 0),
            coherence_score=linguistic_analysis.get("coherence_score", 0),
            lexical_diversity=linguistic_analysis.get("lexical_diversity", 0),
            grammatical_complexity=linguistic_analysis.get("grammatical_complexity", 0),
            details={
                "acoustic_analysis": analysis.get("acoustic_analysis", {}),
                "temporal_analysis": analysis.get("temporal_analysis", {}),
                "cognitive_indicators": analysis.get("cognitive_indicators", {})
            }
        )
        
        db.add(speech_result)
        
        # Create audio file record
        file_size = os.path.getsize(temp_file_path)
        audio_record = AudioFile(
            id=str(uuid.uuid4()),
            user_id=session.user_id,
            test_result_id=test_result.id,
            file_url=temp_file_path,
            duration=int(audio_features.get("duration", 0)),
            file_size=file_size,
            format=audio_file.filename.split('.')[-1].lower()
        )
        
        db.add(audio_record)
        db.commit()
        db.refresh(test_result)
        
        return EnhancedSpeechTestResponse(
            id=test_result.id,
            session_id=test_result.session_id,
            test_name=test_result.test_name,
            test_type=test_context_obj.test_type,
            transcription=transcription_data.get("text", ""),
            audio_features=audio_features,
            linguistic_analysis=analysis.get("linguistic_analysis"),
            acoustic_analysis=analysis.get("acoustic_analysis"),
            temporal_analysis=analysis.get("temporal_analysis"),
            risk_assessment=analysis.get("risk_assessment"),
            recommendations=analysis.get("recommendations"),
            processing_time=analysis_result.get("processing_time")
        )
        
    except Exception as e:
        db.rollback()
        print(f"Enhanced speech analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Speech processing error: {str(e)}")
    
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass

@router.get("/tests/prompts")
async def get_speech_test_prompts():
    """
    Get available speech test prompts for different test types
    """
    return {
        "test_types": {
            "fluency": {
                "name": "Verbal Fluency",
                "prompts": [
                    {
                        "id": "semantic_animals",
                        "text": "Name as many animals as you can in 60 seconds",
                        "category": "semantic",
                        "duration": 60,
                        "languages": ["en", "hi", "es", "fr"]
                    },
                    {
                        "id": "phonemic_f", 
                        "text": "Say as many words starting with 'F' as you can in 60 seconds",
                        "category": "phonemic",
                        "duration": 60,
                        "languages": ["en"]
                    },
                    {
                        "id": "semantic_food",
                        "text": "Name as many food items as you can in 60 seconds",
                        "category": "semantic", 
                        "duration": 60,
                        "languages": ["en", "hi", "es", "fr", "ta", "te"]
                    }
                ]
            },
            "description": {
                "name": "Picture Description",
                "prompts": [
                    {
                        "id": "cookie_theft",
                        "text": "Describe everything you see happening in this picture",
                        "image_url": "https://example.com/cookie_theft.jpg",
                        "duration": 120,
                        "languages": ["en", "hi", "es", "fr", "ta", "te"]
                    }
                ]
            },
            "reading": {
                "name": "Reading Task",
                "prompts": [
                    {
                        "id": "passage_1",
                        "text": "Read this passage aloud: 'The rainbow is a beautiful natural phenomenon...'",
                        "duration": 60,
                        "languages": ["en"]
                    }
                ]
            },
            "conversation": {
                "name": "Conversation",
                "prompts": [
                    {
                        "id": "daily_routine",
                        "text": "Tell me about your typical day from morning to evening",
                        "duration": 180,
                        "languages": ["en", "hi", "es", "fr", "ta", "te", "bn", "mr", "gu"]
                    },
                    {
                        "id": "childhood_memory",
                        "text": "Share a happy memory from your childhood",
                        "duration": 180,
                        "languages": ["en", "hi", "es", "fr", "ta", "te", "bn", "mr", "gu"]
                    }
                ]
            }
        }
    }

@router.get("/session/{session_id}/detailed", response_model=List[EnhancedSpeechTestResponse])
async def get_session_detailed_speech_results(session_id: str, db: Session = Depends(get_db)):
    """
    Get detailed speech test results for a session
    """
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_type == "speech"
    ).all()
    
    detailed_results = []
    for result in results:
        speech_details = db.query(SpeechTestResult).filter(
            SpeechTestResult.test_result_id == result.id
        ).first()
        
        detailed_results.append(EnhancedSpeechTestResponse(
            id=result.id,
            session_id=result.session_id,
            test_name=result.test_name,
            test_type=result.raw_data.get("test_context", {}).get("test_type", "unknown"),
            transcription=speech_details.transcription if speech_details else "",
            audio_features=result.raw_data.get("audio_features"),
            linguistic_analysis=result.analysis_result.get("linguistic_analysis"),
            acoustic_analysis=result.analysis_result.get("acoustic_analysis"),
            temporal_analysis=result.analysis_result.get("temporal_analysis"),
            risk_assessment=result.analysis_result.get("risk_assessment"),
            recommendations=result.analysis_result.get("recommendations"),
            processing_time=None
        ))
    
    return detailed_results

@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en")
):
    """
    Simple transcription endpoint for real-time transcription
    """
    if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, f"{str(uuid.uuid4())}_{audio_file.filename}")
    
    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await audio_file.read()
            await out_file.write(content)
        
        # Transcribe with timestamps
        result = await enhanced_groq_service.transcribe_with_timestamps(temp_file_path, language)
        
        return {
            "transcription": result["text"],
            "language": result["language"],
            "duration": result["duration"],
            "words": result.get("words", []),
            "segments": result.get("segments", []),
            "processing_time": result["processing_time"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    
    finally:
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            os.rmdir(temp_dir)
        except:
            pass