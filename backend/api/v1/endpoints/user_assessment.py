from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from core.database.connection import get_db
from core.database.models import User, TestSession, UserPreference

router = APIRouter()

class AccessibilityAssessment(BaseModel):
    user_id: str
    vision_capabilities: Dict[str, Any]
    motor_capabilities: Dict[str, Any]
    cognitive_preferences: Dict[str, Any]
    language_preferences: Dict[str, Any]
    
    class Config:
        from_attributes = True

class PersonalizedTestRecommendation(BaseModel):
    user_id: str
    recommended_tests: List[Dict[str, Any]]
    accessibility_adaptations: Dict[str, Any]
    clinical_rationale: str
    estimated_duration: int
    
    class Config:
        from_attributes = True

@router.post("/accessibility-assessment")
async def conduct_accessibility_assessment(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Conduct comprehensive accessibility assessment to determine appropriate test battery
    """
    # Get user profile
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Determine test battery based on user profile
    test_battery = get_personalized_test_battery(user)
    
    return {
        "user_id": user_id,
        "user_profile": {
            "vision_status": user.vision_type,
            "education_level": user.education_level,
            "age": user.age,
            "language": user.language
        },
        "recommended_battery": test_battery,
        "accessibility_notes": generate_accessibility_notes(user),
        "clinical_rationale": generate_clinical_rationale(user, test_battery)
    }

def get_personalized_test_battery(user: User) -> Dict[str, Any]:
    """
    Generate personalized test battery based on user capabilities
    """
    vision_status = user.vision_type or 'normal'
    education_level = user.education_level or 'graduate'
    age = user.age or 65
    language = user.language or 'en'
    
    # SCENARIO 1: BLIND USERS - Audio-only tests
    if vision_status == 'blind':
        return {
            "battery_id": "blind_audio_comprehensive",
            "battery_name": "Audio-Only Cognitive Assessment",
            "total_duration": 65,
            "tests": [
                {
                    "test_id": "audio_mmse",
                    "test_name": "MMSE - Audio Adaptation",
                    "duration": 15,
                    "clinical_evidence": "Folstein et al., 1975 - Adapted for blind users",
                    "domains": ["Orientation", "Memory", "Attention", "Language"],
                    "accessibility_adaptations": [
                        "Voice-only instructions",
                        "Audio response recording",
                        "Tactile object identification",
                        "No visual components"
                    ]
                },
                {
                    "test_id": "avlt_audio",
                    "test_name": "Auditory Verbal Learning Test",
                    "duration": 20,
                    "clinical_evidence": "Rey, 1964 - Gold standard memory assessment",
                    "domains": ["Auditory Memory", "Learning", "Delayed Recall"],
                    "accessibility_adaptations": [
                        "Pure audio word presentation",
                        "Voice recall recording",
                        "No visual memory components"
                    ]
                },
                {
                    "test_id": "digit_span_audio",
                    "test_name": "Audio Digit Span",
                    "duration": 10,
                    "clinical_evidence": "Wechsler, 1997 - Working memory assessment",
                    "domains": ["Attention Span", "Working Memory"],
                    "accessibility_adaptations": [
                        "Audio digit presentation",
                        "Voice repetition recording",
                        "No visual number displays"
                    ]
                },
                {
                    "test_id": "semantic_fluency_audio",
                    "test_name": "Semantic Fluency - Animals",
                    "duration": 5,
                    "clinical_evidence": "Benton & Hamsher, 1989 - Early dementia detection",
                    "domains": ["Language", "Executive Function", "Semantic Memory"],
                    "accessibility_adaptations": [
                        "Voice-only instructions",
                        "Continuous voice recording",
                        "No visual prompts"
                    ]
                },
                {
                    "test_id": "story_recall_audio",
                    "test_name": "Logical Memory - Story Recall",
                    "duration": 15,
                    "clinical_evidence": "Wechsler Memory Scale - MCI detection",
                    "domains": ["Episodic Memory", "Language Comprehension"],
                    "accessibility_adaptations": [
                        "Audio story presentation",
                        "Voice recall recording",
                        "No reading requirements"
                    ]
                }
            ]
        }
    
    # SCENARIO 2: WEAK VISION USERS - High contrast + audio backup
    elif vision_status == 'weak_vision':
        return {
            "battery_id": "weak_vision_adaptive",
            "battery_name": "High Contrast Cognitive Assessment",
            "total_duration": 85,
            "tests": [
                {
                    "test_id": "mmse_large_print",
                    "test_name": "MMSE - Large Print Version",
                    "duration": 20,
                    "clinical_evidence": "Standard MMSE with visual adaptations",
                    "domains": ["All MMSE domains with accommodation"],
                    "accessibility_adaptations": [
                        "24pt+ font sizes",
                        "High contrast colors",
                        "Audio backup for all text",
                        "Large touch targets"
                    ]
                },
                {
                    "test_id": "moca_visual_adapted",
                    "test_name": "MoCA - Visual Adaptation",
                    "duration": 25,
                    "clinical_evidence": "Nasreddine et al., 2005 with visual modifications",
                    "domains": ["Visuospatial", "Executive", "Memory", "Language"],
                    "accessibility_adaptations": [
                        "Large graphics and text",
                        "High contrast interface",
                        "Audio instructions available",
                        "Simplified visual tasks"
                    ]
                }
                # Include audio tests from blind battery
            ]
        }
    
    # SCENARIO 3: NON-EDUCATED USERS - Culture-free, oral tests
    elif education_level == 'non_educated':
        return {
            "battery_id": "culture_free_oral",
            "battery_name": "Culture-Free Oral Assessment",
            "total_duration": 65,
            "tests": [
                {
                    "test_id": "ccce_oral",
                    "test_name": "Cross-Cultural Cognitive Examination",
                    "duration": 20,
                    "clinical_evidence": "Glosser et al., 1993 - Low literacy validation",
                    "domains": ["Orientation", "Memory", "Attention", "Praxis"],
                    "accessibility_adaptations": [
                        "No reading/writing required",
                        "Oral instructions in native language",
                        "Cultural appropriate content",
                        "Simple visual tasks only"
                    ]
                },
                {
                    "test_id": "rudas_oral",
                    "test_name": "RUDAS - Oral Version",
                    "duration": 15,
                    "clinical_evidence": "Storey et al., 2004 - Multicultural validation",
                    "domains": ["Body Orientation", "Praxis", "Drawing", "Memory"],
                    "accessibility_adaptations": [
                        "Oral administration",
                        "Physical demonstration tasks",
                        "No literacy requirements",
                        "Cultural sensitivity"
                    ]
                }
            ]
        }
    
    # SCENARIO 4: EDUCATED USERS - Full standard battery
    else:
        return {
            "battery_id": "comprehensive_standard",
            "battery_name": "Comprehensive Cognitive Battery",
            "total_duration": 120,
            "tests": [
                {
                    "test_id": "mmse_standard",
                    "test_name": "MMSE - Complete Version",
                    "duration": 15,
                    "clinical_evidence": "Folstein et al., 1975 - Gold standard",
                    "domains": ["All cognitive domains"],
                    "accessibility_adaptations": ["Standard administration"]
                },
                {
                    "test_id": "moca_complete",
                    "test_name": "MoCA - Full Assessment",
                    "duration": 25,
                    "clinical_evidence": "Nasreddine et al., 2005 - High sensitivity",
                    "domains": ["Visuospatial", "Executive", "Language", "Memory"],
                    "accessibility_adaptations": ["Standard administration"]
                },
                {
                    "test_id": "avlt_complete",
                    "test_name": "AVLT - Complete Protocol",
                    "duration": 30,
                    "clinical_evidence": "Rey, 1964 - Memory gold standard",
                    "domains": ["Learning", "Memory", "Recognition"],
                    "accessibility_adaptations": ["Standard administration"]
                },
                {
                    "test_id": "clock_drawing",
                    "test_name": "Clock Drawing Test",
                    "duration": 10,
                    "clinical_evidence": "Shulman, 2000 - Executive function",
                    "domains": ["Executive Function", "Visuospatial"],
                    "accessibility_adaptations": ["Digital drawing interface"]
                },
                {
                    "test_id": "trail_making",
                    "test_name": "Trail Making Test A & B",
                    "duration": 15,
                    "clinical_evidence": "Reitan, 1958 - Processing speed",
                    "domains": ["Processing Speed", "Executive Function"],
                    "accessibility_adaptations": ["Touch/mouse interface"]
                }
            ]
        }

def generate_accessibility_notes(user: User) -> List[str]:
    """
    Generate specific accessibility notes for the user
    """
    notes = []
    
    if user.vision_type == 'blind':
        notes.extend([
            "All tests adapted for audio-only administration",
            "Voice navigation enabled throughout",
            "Tactile materials provided where applicable",
            "No visual components or requirements",
            "Screen reader compatibility ensured"
        ])
    elif user.vision_type == 'weak_vision':
        notes.extend([
            "Large fonts (24pt+) and high contrast enabled",
            "Audio backup available for all visual elements",
            "Enlarged graphics and simplified visual tasks",
            "Good lighting conditions recommended",
            "Magnification tools available"
        ])
    
    if user.education_level == 'non_educated':
        notes.extend([
            "No reading or writing requirements",
            "Oral administration in preferred language",
            "Culturally appropriate content and examples",
            "Simple, familiar tasks prioritized",
            "Respect for traditional knowledge systems"
        ])
    
    # Age-related adaptations
    if user.age and user.age > 75:
        notes.extend([
            "Extended time limits provided",
            "Frequent breaks offered",
            "Clear, loud audio presentation",
            "Simplified instructions",
            "Patient, supportive administration"
        ])
    
    return notes

def generate_clinical_rationale(user: User, test_battery: Dict[str, Any]) -> str:
    """
    Generate clinical rationale for the selected test battery
    """
    vision_status = user.vision_type or 'normal'
    education_level = user.education_level or 'graduate'
    
    rationale = f"Test battery selected based on comprehensive accessibility assessment. "
    
    if vision_status == 'blind':
        rationale += "Audio-only adaptations maintain clinical validity while ensuring full accessibility. All tests have established normative data for audio administration. "
    elif vision_status == 'weak_vision':
        rationale += "High-contrast visual adaptations with audio backup ensure optimal performance while maintaining test integrity. "
    
    if education_level == 'non_educated':
        rationale += "Culture-free and literacy-independent tests ensure fair assessment regardless of educational background. "
    
    rationale += f"Selected battery provides comprehensive cognitive assessment with {len(test_battery['tests'])} validated instruments, "
    rationale += f"estimated completion time of {test_battery['total_duration']} minutes, "
    rationale += "ensuring clinical accuracy while respecting individual accessibility needs."
    
    return rationale

@router.get("/test-battery/{user_id}")
async def get_user_test_battery(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the recommended test battery for a specific user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    test_battery = get_personalized_test_battery(user)
    
    return {
        "user_id": user_id,
        "test_battery": test_battery,
        "accessibility_notes": generate_accessibility_notes(user),
        "clinical_rationale": generate_clinical_rationale(user, test_battery)
    }

@router.post("/update-accessibility-preferences")
async def update_accessibility_preferences(
    user_id: str,
    preferences: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Update user's accessibility preferences
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update or create user preferences
    user_pref = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()
    if not user_pref:
        user_pref = UserPreference(
            user_id=user_id,
            voice_speed=preferences.get('voice_speed', 1.0),
            voice_gender=preferences.get('voice_gender', 'female'),
            text_size=preferences.get('text_size', 'large'),
            high_contrast=preferences.get('high_contrast', True),
            voice_guidance=preferences.get('voice_guidance', True),
            interface_type=preferences.get('interface_type', 'audio')
        )
        db.add(user_pref)
    else:
        user_pref.voice_speed = preferences.get('voice_speed', user_pref.voice_speed)
        user_pref.voice_gender = preferences.get('voice_gender', user_pref.voice_gender)
        user_pref.text_size = preferences.get('text_size', user_pref.text_size)
        user_pref.high_contrast = preferences.get('high_contrast', user_pref.high_contrast)
        user_pref.voice_guidance = preferences.get('voice_guidance', user_pref.voice_guidance)
        user_pref.interface_type = preferences.get('interface_type', user_pref.interface_type)
    
    db.commit()
    db.refresh(user_pref)
    
    return {
        "message": "Accessibility preferences updated successfully",
        "preferences": {
            "voice_speed": user_pref.voice_speed,
            "voice_gender": user_pref.voice_gender,
            "text_size": user_pref.text_size,
            "high_contrast": user_pref.high_contrast,
            "voice_guidance": user_pref.voice_guidance,
            "interface_type": user_pref.interface_type
        }
    }