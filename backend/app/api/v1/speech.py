from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import SpeechTestInput, SpeechTestResult
from app.services.groq_client import GroqClient, PromptTemplates
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import tempfile
from typing import Optional

ROOT_DIR = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter()
groq_client = GroqClient()

@router.post("/speech", response_model=SpeechTestResult)
async def speech_test(
    user_id: str = Form(...),
    task_type: str = Form(...),  # reading, picture_description, spontaneous
    response_text: Optional[str] = Form(None),
    audio_quality: str = Form("good"),
    audio_file: Optional[UploadFile] = File(None)
):
    """Process speech/text analysis test"""
    try:
        # Get user locale
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        locale = user.get("locale", "en")
        
        # Process audio if provided
        text = response_text
        if audio_file and not text:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                content = await audio_file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            text = groq_client.transcribe_audio(tmp_path)
            os.unlink(tmp_path)
        
        if not text:
            raise HTTPException(status_code=400, detail="No text or audio provided")
        
        # Analyze with Groq
        prompt = PromptTemplates.speech_test(locale, task_type, text, audio_quality)
        result = groq_client.call_llm(prompt)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Create result object
        speech_result = SpeechTestResult(
            user_id=user_id,
            task_type=task_type,
            fluency_score=result.get("fluency_score", 0.0),
            hesitation=result.get("hesitation", "low"),
            word_finding=result.get("word_finding", "none"),
            grammar_errors=result.get("grammar_errors", "none"),
            vocabulary=result.get("vocabulary", "normal"),
            coherence=result.get("coherence", "high"),
            dementia_indicators=result.get("dementia_indicators", []),
            risk_level=result.get("risk_level", "low"),
            confidence=result.get("confidence", "medium"),
            notes=result.get("notes", "")
        )
        
        # Store in database
        await db.speech_tests.insert_one(speech_result.dict())
        
        return speech_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))