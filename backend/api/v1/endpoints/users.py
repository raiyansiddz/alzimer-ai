from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid

from core.database.connection import get_db
from core.database.models import User, UserPreference

router = APIRouter()

class UserPreferenceUpdate(BaseModel):
    voice_speed: Optional[float] = None
    voice_gender: Optional[str] = None
    text_size: Optional[str] = None
    high_contrast: Optional[bool] = None
    voice_guidance: Optional[bool] = None
    interface_type: Optional[str] = None

class UserPreferenceResponse(BaseModel):
    id: str
    user_id: str
    voice_speed: float
    voice_gender: str
    text_size: str
    high_contrast: bool
    voice_guidance: bool
    interface_type: str
    
    class Config:
        from_attributes = True

@router.get("/preferences/{user_id}", response_model=UserPreferenceResponse)
async def get_user_preferences(user_id: str, db: Session = Depends(get_db)):
    """
    Get user preferences
    """
    preferences = db.query(UserPreference).filter(UserPreference.user_id == str(user_id)).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    return preferences

@router.put("/preferences/{user_id}", response_model=UserPreferenceResponse)
async def update_user_preferences(user_id: str, pref_data: UserPreferenceUpdate, db: Session = Depends(get_db)):
    """
    Update user preferences
    """
    preferences = db.query(UserPreference).filter(UserPreference.user_id == str(user_id)).first()
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found")
    
    # Update fields
    for field, value in pref_data.dict(exclude_unset=True).items():
        setattr(preferences, field, value)
    
    db.commit()
    db.refresh(preferences)
    
    return preferences
