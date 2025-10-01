from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

from core.database.connection import get_db
from core.database.models import User, UserPreference

router = APIRouter()
security = HTTPBearer()

class UserRegister(BaseModel):
    email: EmailStr
    name: str
    age: Optional[int] = None
    education_level: Optional[str] = None
    vision_type: Optional[str] = None
    language: str = "en"

class UserLogin(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    age: Optional[int]
    education_level: Optional[str]
    vision_type: Optional[str]
    language: str
    
    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    new_user = User(
        id=str(str(uuid.uuid4())),
        email=user_data.email,
        name=user_data.name,
        age=user_data.age,
        education_level=user_data.education_level,
        vision_type=user_data.vision_type,
        language=user_data.language
    )
    
    db.add(new_user)
    
    # Create default preferences
    preferences = UserPreference(
        id=str(str(uuid.uuid4())),
        user_id=new_user.id
    )
    db.add(preferences)
    
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user (simplified - in production use proper authentication)
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get current user details
    """
    user = db.query(User).filter(User.id == str(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
