from fastapi import APIRouter, HTTPException
from app.models.schemas import UserRegistration, UserProfile
from motor.motor_asyncio import AsyncIOMotorDatabase
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

router = APIRouter()

@router.post("/registration", response_model=UserProfile)
async def register_user(user: UserRegistration):
    """Register a new user and create their profile"""
    try:
        user_profile = UserProfile(
            name=user.name,
            age=user.age,
            locale=user.locale
        )
        
        await db.users.insert_one(user_profile.dict())
        return user_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Get user profile by ID"""
    try:
        user = await db.users.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfile(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))