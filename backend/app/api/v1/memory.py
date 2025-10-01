from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import MemoryTestInput, MemoryTestResult
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

@router.post("/memory", response_model=MemoryTestResult)
async def memory_test(
    user_id: str = Form(...),
    response_text: Optional[str] = Form(None),
    response_time_ms: Optional[int] = Form(None),
    audio_file: Optional[UploadFile] = File(None)
):
    """Process memory test - accepts text or audio input"""
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
        prompt = PromptTemplates.memory_test(locale, text, response_time_ms)
        result = groq_client.call_llm(prompt)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Create result object
        memory_result = MemoryTestResult(
            user_id=user_id,
            correct_words=result.get("correct_words", []),
            missed_words=result.get("missed_words", []),
            score=result.get("score", 0),
            response_time_ms=response_time_ms,
            cognitive_indicators=result.get("cognitive_indicators", []),
            risk_level=result.get("risk_level", "low"),
            confidence=result.get("confidence", "medium"),
            notes=result.get("notes", "")
        )
        
        # Store in database
        await db.memory_tests.insert_one(memory_result.dict())
        
        return memory_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))