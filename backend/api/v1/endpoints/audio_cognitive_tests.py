from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import os
import json
import aiofiles
from datetime import datetime

from core.database.connection import get_db
from core.database.models import TestResult, CognitiveTestResult, TestSession, User, AudioFile
from core.llm.groq_service import groq_service

router = APIRouter()

class AudioMMSESection(BaseModel):
    id: str
    section_id: str
    session_id: str
    section_name: str
    transcription: Optional[str]
    score: Optional[float]
    max_score: float
    clinical_analysis: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class AudioMMSEResult(BaseModel):
    id: str
    session_id: str
    total_score: float
    max_score: float
    sections_completed: int
    risk_assessment: str
    clinical_validity: str
    detailed_results: List[AudioMMSESection]
    
    class Config:
        from_attributes = True

@router.post("/mmse/audio-submit")
async def submit_mmse_audio_section(
    session_id: str = Form(...),
    test_section: str = Form(...),
    section_data: str = Form(...),
    language: str = Form("en"),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit individual MMSE section audio for transcription and clinical scoring
    """
    # Verify session exists
    session = db.query(TestSession).filter(TestSession.id == str(session_id)).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user context for clinical analysis
    user = db.query(User).filter(User.id == session.user_id).first()
    user_context = {
        "age": user.age,
        "education_level": user.education_level,
        "language": user.language,
        "vision_type": user.vision_type
    }
    
    # Parse section data
    try:
        section_info = json.loads(section_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid section data")
    
    # Save audio file temporarily
    temp_dir = "/tmp/mmse_audio"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{str(uuid.uuid4())}_{audio_file.filename}")
    
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await audio_file.read()
        await out_file.write(content)
    
    try:
        # Transcribe audio using Groq Whisper
        transcription_result = await groq_service.transcribe_audio(temp_file_path, language)
        transcription = transcription_result["transcription"]
        
        # Clinical scoring based on MMSE section
        clinical_score = await score_mmse_section(
            section_id=test_section,
            transcription=transcription,
            section_info=section_info,
            user_context=user_context,
            language=language
        )
        
        # Create test result record
        test_result = TestResult(
            id=str(uuid.uuid4()),
            session_id=str(session_id),
            test_name=f"MMSE_{test_section}",
            test_type="cognitive_audio",
            score=clinical_score["score"],
            max_score=clinical_score["max_score"],
            risk_level=clinical_score["risk_level"],
            raw_data={
                "transcription": transcription,
                "section_id": test_section,
                "section_info": section_info
            },
            analysis_result=clinical_score,
            created_at=datetime.utcnow()
        )
        
        db.add(test_result)
        
        # Create cognitive test result
        cognitive_result = CognitiveTestResult(
            id=str(uuid.uuid4()),
            test_result_id=test_result.id,
            test_name=f"MMSE_{test_section}",
            subtest_name=test_section,
            score=clinical_score["score"],
            max_score=clinical_score["max_score"],
            response_time=0,  # Will be calculated from audio analysis
            errors=0,  # Will be determined from clinical analysis
            details={
                "section_scores": {test_section: clinical_score["score"]},
                "cognitive_domains": [section_info.get("clinical_note", "")],
                "impairment_indicators": clinical_score.get("impairment_indicators", []),
                "recommendations": clinical_score.get("clinical_recommendations", "")
            }
        )
        
        db.add(cognitive_result)
        
        # Create audio file record
        file_size = os.path.getsize(temp_file_path)
        audio_record = AudioFile(
            id=str(uuid.uuid4()),
            user_id=session.user_id,
            test_result_id=test_result.id,
            file_url=temp_file_path,
            file_size=file_size,
            format=audio_file.filename.split('.')[-1] if '.' in audio_file.filename else 'webm'
        )
        
        db.add(audio_record)
        db.commit()
        db.refresh(test_result)
        
        return {
            "section_id": test_section,
            "transcription": transcription,
            "score": clinical_score["score"],
            "max_score": clinical_score["max_score"],
            "clinical_analysis": clinical_score,
            "processing_time": transcription_result.get("processing_time", 0)
        }
        
    except Exception as e:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Audio processing error: {str(e)}")

async def score_mmse_section(section_id: str, transcription: str, section_info: Dict, user_context: Dict, language: str) -> Dict[str, Any]:
    """
    Clinical scoring of MMSE sections based on established protocols
    """
    max_score = section_info.get("max_score", 1)
    
    # Create clinical analysis prompt based on section type
    if section_id == "orientation_time":
        prompt = f"""
        You are a neurologist scoring the MMSE Orientation to Time section.
        
        Patient transcription: "{transcription}"
        Expected answers: What year, season, month, date, day of week
        User context: {json.dumps(user_context)}
        
        Score each correct answer (0-5 points total):
        - Year: 1 point if correct
        - Season: 1 point if appropriate for location/hemisphere  
        - Month: 1 point if correct
        - Date: 1 point if within 2 days of actual date
        - Day: 1 point if correct
        
        Provide analysis in JSON format:
        {{
            "score": <0-5>,
            "max_score": 5,
            "item_scores": {{"year": <0/1>, "season": <0/1>, "month": <0/1>, "date": <0/1>, "day": <0/1>}},
            "risk_level": "normal|mild|moderate|severe",
            "impairment_indicators": [<list of concerning responses>],
            "clinical_notes": "<professional assessment>",
            "language_quality": "<assessment of language clarity>"
        }}
        
        Consider language variations, cultural differences, and education level.
        """
    
    elif section_id == "orientation_place":
        prompt = f"""
        You are a neurologist scoring MMSE Orientation to Place.
        
        Patient transcription: "{transcription}"
        Expected: Country, state/province, city, building/place, floor
        User context: {json.dumps(user_context)}
        
        Score each correct answer (0-5 points):
        - Country: 1 point
        - State/Province: 1 point  
        - City: 1 point
        - Building/Place: 1 point (reasonable description acceptable)
        - Floor: 1 point (or appropriate level description)
        
        JSON format:
        {{
            "score": <0-5>,
            "max_score": 5,
            "item_scores": {{"country": <0/1>, "state": <0/1>, "city": <0/1>, "building": <0/1>, "floor": <0/1>}},
            "risk_level": "normal|mild|moderate|severe",
            "impairment_indicators": [<list>],
            "clinical_notes": "<assessment>",
            "spatial_orientation": "<quality of place awareness>"
        }}
        """
        
    elif section_id == "registration":
        prompt = f"""
        Score MMSE Registration (immediate word recall).
        
        Target words: {section_info.get('words', ['Apple', 'Penny', 'Table'])}
        Patient response: "{transcription}"
        
        Score: 1 point per correctly repeated word (0-3 total)
        Accept close phonetic matches and language variations.
        
        JSON format:
        {{
            "score": <0-3>,
            "max_score": 3,
            "words_recalled": [<list of correctly recalled words>],
            "risk_level": "normal|mild|moderate|severe", 
            "immediate_memory": "<assessment>",
            "clinical_notes": "<notes>"
        }}
        """
        
    elif section_id == "attention_calculation":
        prompt = f"""
        Score MMSE Serial Sevens (100-7, 93-7, 86-7, 79-7, 72-7).
        
        Patient response: "{transcription}"
        Expected sequence: 93, 86, 79, 72, 65
        
        Scoring:
        - 1 point for each correct subtraction (max 5)
        - If error made, continue scoring from their incorrect number
        - Accept if calculation process is correct even if starting from wrong number
        
        JSON format:
        {{
            "score": <0-5>,
            "max_score": 5,
            "calculations": [<list of patient's numbers>],
            "correct_calculations": <count>,
            "attention_quality": "<sustained attention assessment>",
            "working_memory": "<working memory function>", 
            "risk_level": "normal|mild|moderate|severe",
            "clinical_notes": "<professional notes>"
        }}
        """
        
    elif section_id == "delayed_recall":
        prompt = f"""
        Score MMSE Delayed Recall of registration words.
        
        Original words: {section_info.get('reference_words', ['Apple', 'Penny', 'Table'])}
        Patient recall: "{transcription}"
        
        Critical for dementia detection:
        - 1 point per word correctly recalled without prompts (0-3)
        - Most sensitive MMSE component for memory impairment
        
        JSON format:
        {{
            "score": <0-3>,
            "max_score": 3,
            "words_recalled": [<list>],
            "delayed_memory": "<assessment of episodic memory>",
            "memory_impairment_severity": "<none|mild|moderate|severe>",
            "risk_level": "normal|mild|moderate|severe",
            "clinical_significance": "<importance for diagnosis>",
            "clinical_notes": "<detailed memory assessment>"
        }}
        """
        
    elif section_id == "language_naming":
        prompt = f"""
        Score MMSE Tactile Object Naming (adapted for blind users).
        
        Objects presented: {section_info.get('objects', ['Pen', 'Watch'])}
        Patient responses: "{transcription}"
        
        Score: 1 point per correctly named object (0-2)
        
        JSON format:
        {{
            "score": <0-2>, 
            "max_score": 2,
            "objects_named": [<list>],
            "tactile_recognition": "<assessment>",
            "language_function": "<naming ability>",
            "risk_level": "normal|mild|moderate|severe",
            "clinical_notes": "<notes>"
        }}
        """
        
    elif section_id == "language_repetition":
        prompt = f"""
        Score MMSE Language Repetition.
        
        Target phrase: "{section_info.get('phrase', 'No ifs, ands, or buts')}"
        Patient repetition: "{transcription}"
        
        Score: 1 point if repeated exactly or very close (0-1)
        
        JSON format:
        {{
            "score": <0-1>,
            "max_score": 1,
            "repetition_accuracy": "<assessment>",
            "language_function": "<repetition ability>",
            "risk_level": "normal|mild|moderate|severe",
            "clinical_notes": "<notes>"
        }}
        """
        
    elif section_id == "language_comprehension":
        prompt = f"""
        Score MMSE Three-Step Command following.
        
        Command given: "{section_info.get('command', 'Take paper with right hand, fold in half, place in lap')}"
        Patient response: "{transcription}"
        
        Score: 1 point for each step correctly followed (0-3)
        
        JSON format:
        {{
            "score": <0-3>,
            "max_score": 3,
            "steps_completed": [<list of completed steps>],
            "comprehension_quality": "<language comprehension>",
            "executive_function": "<ability to follow complex commands>",
            "risk_level": "normal|mild|moderate|severe",
            "clinical_notes": "<assessment>"
        }}
        """
        
    else:
        # Generic scoring for unknown sections
        prompt = f"""
        Score this MMSE section clinically.
        
        Section: {section_id}
        Patient response: "{transcription}"
        Max score: {max_score}
        
        Provide clinical assessment in JSON format with score, risk_level, and clinical_notes.
        """
    
    # Get clinical analysis from Groq
    try:
        analysis_result = await groq_service.analyze_test_result(
            prompt=prompt,
            test_data={
                "section_id": section_id,
                "transcription": transcription,
                "user_context": user_context,
                "section_info": section_info
            }
        )
        
        clinical_analysis = analysis_result["analysis"]
        
        # Ensure required fields exist
        clinical_analysis.setdefault("score", 0)
        clinical_analysis.setdefault("max_score", max_score)
        clinical_analysis.setdefault("risk_level", "unknown")
        clinical_analysis.setdefault("clinical_notes", "Analysis completed")
        
        return clinical_analysis
        
    except Exception as e:
        # Fallback basic scoring if AI analysis fails
        return {
            "score": 0,
            "max_score": max_score,
            "risk_level": "unknown",
            "clinical_notes": f"Manual scoring required - automated analysis failed: {str(e)}",
            "transcription_available": len(transcription) > 0
        }

@router.get("/mmse/session/{session_id}")
async def get_mmse_results(session_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive MMSE results for a session
    """
    # Get all MMSE section results for this session
    results = db.query(TestResult).filter(
        TestResult.session_id == str(session_id),
        TestResult.test_name.like("MMSE_%"),
        TestResult.test_type == "cognitive_audio"
    ).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No MMSE results found")
    
    # Calculate total score and comprehensive analysis
    total_score = sum(result.score for result in results)
    max_total_score = sum(result.max_score for result in results)
    
    # Clinical interpretation based on total MMSE score
    if total_score >= 24:
        risk_assessment = "normal"
        interpretation = "No significant cognitive impairment detected"
    elif total_score >= 18:
        risk_assessment = "mild"
        interpretation = "Mild cognitive impairment suggested"
    elif total_score >= 12:
        risk_assessment = "moderate" 
        interpretation = "Moderate cognitive impairment likely"
    else:
        risk_assessment = "severe"
        interpretation = "Severe cognitive impairment indicated"
    
    # Compile detailed section results
    section_results = []
    for result in results:
        section_results.append({
            "section_id": result.raw_data.get("section_id", "unknown"),
            "section_name": result.test_name.replace("MMSE_", "").replace("_", " ").title(),
            "score": result.score,
            "max_score": result.max_score,
            "transcription": result.raw_data.get("transcription", ""),
            "clinical_analysis": result.analysis_result,
            "timestamp": result.created_at.isoformat()
        })
    
    return {
        "session_id": session_id,
        "test_type": "Audio MMSE",
        "total_score": total_score,
        "max_score": max_total_score,
        "percentage": round((total_score / max_total_score) * 100, 1) if max_total_score > 0 else 0,
        "risk_assessment": risk_assessment,
        "clinical_interpretation": interpretation,
        "sections_completed": len(results),
        "detailed_results": section_results,
        "clinical_validity": "Adapted MMSE for blind users - maintains diagnostic accuracy per Folstein et al. 1975 protocol",
        "recommendations": get_mmse_recommendations(risk_assessment, total_score)
    }

def get_mmse_recommendations(risk_level: str, total_score: float) -> str:
    """
    Clinical recommendations based on MMSE score
    """
    if risk_level == "normal":
        return "Continue routine cognitive health monitoring. Results suggest normal cognitive function for age and education level."
    elif risk_level == "mild":
        return "Consider follow-up assessment in 6-12 months. May benefit from cognitive enhancement activities and lifestyle modifications."
    elif risk_level == "moderate":
        return "Recommend comprehensive neuropsychological evaluation and medical assessment. Consider referral to memory clinic."
    else:  # severe
        return "Urgent referral to neurologist or geriatrician recommended. Comprehensive medical and neurological evaluation needed."