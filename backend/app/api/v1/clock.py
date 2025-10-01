from fastapi import APIRouter, HTTPException
from app.models.schemas import ClockTestInput, ClockTestResult
from app.services.groq_client import GroqClient, PromptTemplates
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import json

ROOT_DIR = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter()
groq_client = GroqClient()

@router.post("/clock", response_model=ClockTestResult)
async def clock_test(test_input: ClockTestInput):
    """Process clock drawing test with image analysis"""
    try:
        # Get user locale
        user = await db.users.find_one({"user_id": test_input.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        locale = user.get("locale", "en")
        
        # Remove data URL prefix if present
        image_data = test_input.image_base64
        if ";base64," in image_data:
            image_data = image_data.split(";base64,")[1]
        
        # Analyze with Groq Vision
        prompt = PromptTemplates.clock_test(
            locale,
            test_input.response_time_ms,
            test_input.image_metadata
        )
        result = groq_client.call_vision(prompt, image_data)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Handle raw response from vision model
        if "raw_response" in result:
            # Try to extract JSON from the response
            try:
                result = json.loads(result["raw_response"])
            except:
                # Fallback to default values
                result = {
                    "overall_accuracy": 0.5,
                    "numbers_present": True,
                    "numbers_position": "unknown",
                    "hands_position": "unknown",
                    "hand_size_ratio": "unknown",
                    "spatial_organization": "unknown",
                    "cognitive_indicators": ["Unable to parse vision analysis"],
                    "dementia_indicators": [],
                    "confidence": "low",
                    "risk_level": "medium",
                    "clinical_notes": "Analysis incomplete"
                }
        
        # Create result object
        clock_result = ClockTestResult(
            user_id=test_input.user_id,
            overall_accuracy=result.get("overall_accuracy", 0.0),
            numbers_present=result.get("numbers_present", False),
            numbers_position=result.get("numbers_position", "unknown"),
            hands_position=result.get("hands_position", "unknown"),
            hand_size_ratio=result.get("hand_size_ratio", "unknown"),
            spatial_organization=result.get("spatial_organization", "unknown"),
            cognitive_indicators=result.get("cognitive_indicators", []),
            dementia_indicators=result.get("dementia_indicators", []),
            confidence=result.get("confidence", "medium"),
            risk_level=result.get("risk_level", "low"),
            clinical_notes=result.get("clinical_notes", "")
        )
        
        # Store in database
        await db.clock_tests.insert_one(clock_result.dict())
        
        return clock_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))