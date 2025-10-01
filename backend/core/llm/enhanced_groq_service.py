from groq import Groq
from config.settings import settings
import json
import time
import librosa
import numpy as np
from pydub import AudioSegment
from typing import Dict, Any, Optional, List
import os
import tempfile

class EnhancedGroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.text_model = "llama-3.3-70b-versatile"
        self.fast_model = "llama-3.1-8b-instant"
        self.whisper_model = "whisper-large-v3-turbo"
        
        # Supported languages with their codes
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'or': 'Odia',
            'as': 'Assamese',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'ja': 'Japanese',
            'ko': 'Korean',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'it': 'Italian'
        }
    
    async def analyze_cognitive_test(self, test_name: str, test_data: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced cognitive test analysis with detailed scoring and recommendations
        """
        language = user_context.get('language', 'en')
        
        prompt = f"""
You are a neuropsychologist specializing in dementia and cognitive assessment. Analyze this {test_name} test result with cultural and linguistic considerations for a {language} speaker.

User Context:
- Age: {user_context.get('age', 'Unknown')}
- Education: {user_context.get('education_level', 'Unknown')}
- Language: {self.supported_languages.get(language, 'Unknown')}
- Vision Status: {user_context.get('vision_type', 'Unknown')}

Test Data: {json.dumps(test_data, indent=2)}

Provide comprehensive analysis in JSON format with:
{{
    "overall_score": float (0-100),
    "risk_level": "low|mild|moderate|high|severe",
    "confidence_score": float (0-100),
    "domain_scores": {{
        "memory": float,
        "attention": float,
        "language": float,
        "visuospatial": float,
        "executive_function": float
    }},
    "detailed_analysis": {{
        "strengths": ["list of cognitive strengths"],
        "weaknesses": ["list of areas of concern"],
        "red_flags": ["list of concerning findings"],
        "cultural_considerations": "string explaining cultural/linguistic factors"
    }},
    "recommendations": {{
        "immediate_actions": ["list of immediate steps"],
        "follow_up_tests": ["list of recommended tests"],
        "lifestyle_suggestions": ["list of lifestyle recommendations"],
        "medical_referral": "boolean indicating if medical consultation needed"
    }},
    "interpretation": "detailed clinical interpretation in {self.supported_languages.get(language, 'English')}",
    "next_assessment_timeframe": "recommended timeframe for next assessment"
}}

Consider:
- Age-appropriate norms
- Education level impact on performance
- Cultural and linguistic factors
- Vision status adaptations
- Test reliability and validity
"""
        
        return await self._make_llm_request(prompt, self.text_model)
    
    async def analyze_speech_detailed(self, audio_file_path: str, test_context: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive speech analysis with acoustic features and linguistic analysis
        """
        try:
            # Extract detailed audio features
            audio_features = await self._extract_audio_features(audio_file_path)
            
            # Transcribe with detailed timing
            transcription_result = await self.transcribe_with_timestamps(audio_file_path, user_context.get('language', 'en'))
            
            # Analyze speech patterns
            language = user_context.get('language', 'en')
            
            prompt = f"""
You are a speech-language pathologist specializing in cognitive assessment through speech analysis. 

Audio Features:
{json.dumps(audio_features, indent=2)}

Transcription with Timestamps:
{json.dumps(transcription_result, indent=2)}

User Context:
- Age: {user_context.get('age', 'Unknown')}
- Education: {user_context.get('education_level', 'Unknown')}
- Native Language: {self.supported_languages.get(language, 'Unknown')}

Test Context: {json.dumps(test_context, indent=2)}

Provide comprehensive speech analysis in JSON format:
{{
    "acoustic_analysis": {{
        "speech_rate": float,
        "pause_frequency": float,
        "voice_stability": float,
        "articulation_clarity": float,
        "prosody_score": float
    }},
    "linguistic_analysis": {{
        "fluency_score": float (0-100),
        "coherence_score": float (0-100),
        "lexical_diversity": float (0-100),
        "grammatical_complexity": float (0-100),
        "semantic_content": float (0-100),
        "word_finding_difficulty": float (0-100)
    }},
    "temporal_analysis": {{
        "total_speaking_time": float,
        "pause_patterns": ["description of pause patterns"],
        "hesitation_frequency": float,
        "speech_timing_variability": float
    }},
    "cognitive_indicators": {{
        "word_retrieval_issues": ["specific examples"],
        "semantic_errors": ["list of semantic issues"],
        "phonemic_issues": ["phonemic problems identified"],
        "discourse_coherence": "assessment of topic maintenance"
    }},
    "risk_assessment": {{
        "overall_risk": "low|mild|moderate|high|severe",
        "confidence": float (0-100),
        "key_concerns": ["list of primary concerns"],
        "positive_indicators": ["list of preserved abilities"]
    }},
    "recommendations": {{
        "follow_up_needed": boolean,
        "specific_assessments": ["recommended detailed assessments"],
        "therapy_suggestions": ["therapeutic recommendations"]
    }},
    "interpretation": "detailed interpretation in {self.supported_languages.get(language, 'English')}"
}}

Consider cultural and linguistic norms for {self.supported_languages.get(language, 'English')} speakers.
"""
            
            analysis = await self._make_llm_request(prompt, self.text_model)
            
            # Combine all results
            return {
                "audio_features": audio_features,
                "transcription": transcription_result,
                "analysis": analysis["analysis"],
                "processing_time": analysis["processing_time"],
                "model_info": analysis["model_info"]
            }
            
        except Exception as e:
            print(f"Enhanced speech analysis error: {str(e)}")
            raise
    
    async def transcribe_with_timestamps(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio with word-level timestamps using Groq Whisper
        """
        try:
            start_time = time.time()
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.whisper_model,
                    file=audio_file,
                    response_format="verbose_json",
                    language=language if language in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi'] else None,
                    timestamp_granularities=["word", "segment"]
                )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "text": response.text,
                "language": response.language,
                "duration": response.duration,
                "words": getattr(response, 'words', []),
                "segments": getattr(response, 'segments', []),
                "processing_time": processing_time
            }
            
        except Exception as e:
            print(f"Transcription with timestamps error: {str(e)}")
            raise
    
    async def _extract_audio_features(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Extract detailed acoustic features from audio file
        """
        try:
            # Load audio with librosa
            y, sr = librosa.load(audio_file_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Extract features
            features = {
                "duration": float(duration),
                "sample_rate": int(sr),
                "energy": {
                    "rms_mean": float(np.mean(librosa.feature.rms(y=y))),
                    "rms_std": float(np.std(librosa.feature.rms(y=y)))
                },
                "spectral": {
                    "centroid_mean": float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                    "rolloff_mean": float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                    "bandwidth_mean": float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
                },
                "temporal": {
                    "zero_crossing_rate": float(np.mean(librosa.feature.zero_crossing_rate(y))),
                    "tempo": float(librosa.feature.tempo(y=y, sr=sr)[0])
                }
            }
            
            # Detect pauses (silence detection)
            frame_length = 2048
            hop_length = 512
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            silence_threshold = np.mean(rms) * 0.1
            
            # Convert to time-based silence detection
            silence_frames = rms < silence_threshold
            frame_times = librosa.frames_to_time(np.arange(len(silence_frames)), sr=sr, hop_length=hop_length)
            
            # Calculate pause statistics
            pause_durations = []
            in_pause = False
            pause_start = 0
            
            for i, is_silent in enumerate(silence_frames):
                if is_silent and not in_pause:
                    pause_start = frame_times[i]
                    in_pause = True
                elif not is_silent and in_pause:
                    pause_duration = frame_times[i] - pause_start
                    if pause_duration > 0.1:  # Only count pauses > 100ms
                        pause_durations.append(pause_duration)
                    in_pause = False
            
            features["pauses"] = {
                "count": len(pause_durations),
                "total_duration": float(sum(pause_durations)),
                "mean_duration": float(np.mean(pause_durations)) if pause_durations else 0,
                "max_duration": float(max(pause_durations)) if pause_durations else 0
            }
            
            return features
            
        except Exception as e:
            print(f"Audio feature extraction error: {str(e)}")
            return {"error": str(e)}
    
    async def generate_personalized_recommendations(self, user_data: Dict[str, Any], test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate personalized recommendations based on comprehensive assessment
        """
        language = user_data.get('language', 'en')
        
        prompt = f"""
You are a geriatrician and neuropsychologist creating personalized care recommendations.

User Profile:
{json.dumps(user_data, indent=2)}

Test Results Summary:
{json.dumps(test_results, indent=2)}

Generate comprehensive recommendations in JSON format in {self.supported_languages.get(language, 'English')}:
{{
    "overall_assessment": {{
        "summary": "brief overall assessment",
        "primary_concerns": ["list of main concerns"],
        "preserved_abilities": ["list of strengths to build upon"]
    }},
    "immediate_recommendations": {{
        "medical_consultation": {{
            "needed": boolean,
            "urgency": "low|medium|high|urgent",
            "specific_referrals": ["list of specialist referrals"],
            "reason": "explanation for referral"
        }},
        "safety_measures": ["immediate safety recommendations"],
        "medication_review": "recommendation for medication assessment"
    }},
    "cognitive_interventions": {{
        "cognitive_training": ["specific cognitive exercises"],
        "memory_strategies": ["practical memory aids"],
        "attention_exercises": ["attention improvement activities"],
        "problem_solving_activities": ["executive function exercises"]
    }},
    "lifestyle_modifications": {{
        "physical_activity": ["specific exercise recommendations"],
        "social_engagement": ["social activity suggestions"],
        "nutrition": ["dietary recommendations"],
        "sleep_hygiene": ["sleep improvement suggestions"],
        "stress_management": ["stress reduction techniques"]
    }},
    "technology_aids": {{
        "memory_apps": ["recommended mobile apps"],
        "reminder_systems": ["technology-based reminder suggestions"],
        "communication_aids": ["assistive communication tools"]
    }},
    "family_support": {{
        "education_resources": ["family education materials"],
        "communication_strategies": ["ways to improve communication"],
        "caregiver_support": ["resources for caregivers"]
    }},
    "monitoring_plan": {{
        "follow_up_schedule": "recommended follow-up timeline",
        "progress_indicators": ["what to monitor"],
        "warning_signs": ["signs that require immediate attention"]
    }},
    "cultural_adaptations": "specific considerations for cultural context"
}}

Ensure recommendations are:
- Culturally appropriate for {self.supported_languages.get(language, 'English')} speakers
- Practical and actionable
- Tailored to education level and age
- Sensitive to vision status
"""
        
        return await self._make_llm_request(prompt, self.text_model)
    
    async def _make_llm_request(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        Make a request to Groq LLM with error handling
        """
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant specializing in cognitive assessment. Always respond in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "analysis": result,
                "processing_time": processing_time,
                "model_info": {
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
            
        except Exception as e:
            print(f"LLM request error: {str(e)}")
            raise

# Global service instance
enhanced_groq_service = EnhancedGroqService()