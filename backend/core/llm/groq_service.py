from groq import Groq
from config.settings import settings
import json
import time
from typing import Dict, Any, Optional

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.default_model = "llama-3.3-70b-versatile"  # Updated to current model
    
    async def analyze_test_result(self, prompt: str, test_data: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze test results using Groq LLM
        """
        try:
            start_time = time.time()
            
            # Format the complete prompt
            full_prompt = f"{prompt}\n\nTest Data: {json.dumps(test_data, indent=2)}"
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=[
                    {"role": "system", "content": "You are a neurologist specializing in cognitive assessment. Provide detailed analysis in JSON format."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return {
                "analysis": result,
                "model": response.model,
                "processing_time": processing_time,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            print(f"Groq analysis error: {str(e)}")
            raise
    
    async def transcribe_audio(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio using Groq Whisper with enhanced multilingual support
        """
        try:
            start_time = time.time()
            
            # Map language codes to Whisper supported languages
            language_map = {
                'hi-en': 'hi',  # Hinglish -> Hindi
                'ta': 'ta',     # Tamil
                'te': 'hi',     # Telugu -> Hindi (closest supported)
                'bn': 'hi',     # Bengali -> Hindi (closest supported)  
                'mr': 'hi',     # Marathi -> Hindi (closest supported)
                'gu': 'hi',     # Gujarati -> Hindi (closest supported)
                'zh': 'zh',     # Chinese
                'ar': 'ar',     # Arabic
                'es': 'es',     # Spanish
                'fr': 'fr',     # French
                'de': 'de',     # German
                'en': 'en',     # English
                'hi': 'hi'      # Hindi
            }
            
            # Get the appropriate language code for Whisper
            whisper_language = language_map.get(language, 'en')
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    response_format="verbose_json",  # Get more detailed response
                    language=whisper_language,
                    temperature=0.0  # More deterministic results
                )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "transcription": response.text,
                "language": language,
                "detected_language": getattr(response, 'language', whisper_language),
                "processing_time": processing_time,
                "segments": getattr(response, 'segments', []) if hasattr(response, 'segments') else []
            }
        except Exception as e:
            print(f"Groq transcription error: {str(e)}")
            raise
    
    # TTS functionality removed - using local audio assets instead
    
    async def analyze_speech_pattern(self, transcription: str, audio_duration: int, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze speech patterns for cognitive assessment with enhanced multilingual support
        """
        language = user_context.get('language', 'en')
        
        # Language-specific analysis considerations
        language_notes = {
            'en': 'Standard English fluency and grammatical patterns',
            'hi': 'Hindi grammatical structures, Sanskrit-derived vocabulary',
            'hi-en': 'Hinglish code-switching patterns, bilingual fluency indicators',
            'ta': 'Tamil agglutinative grammar, classical and modern usage',
            'te': 'Telugu phonology and grammatical complexity',
            'bn': 'Bengali grammatical patterns and cultural expressions',
            'mr': 'Marathi linguistic features and regional variations',
            'gu': 'Gujarati phonological patterns and vocabulary',
            'es': 'Spanish grammatical structures and regional variations',
            'fr': 'French phonology, liaison, and grammatical complexity',
            'de': 'German grammatical complexity, compound words, case system',
            'zh': 'Mandarin tonal patterns, grammatical structures',
            'ar': 'Arabic root patterns, grammatical complexity, dialectal variations'
        }
        
        prompt = f"""
You are a multilingual speech-language pathologist specializing in cognitive assessment.
Analyze this {language} speech sample for cognitive impairment indicators.

Transcription: {transcription}
Duration: {audio_duration} seconds  
Language: {language}
User Context: {json.dumps(user_context)}

Language-specific considerations: {language_notes.get(language, 'General linguistic patterns')}

Provide analysis in JSON format with:
- fluency_score (0-100): Rate speech flow and hesitations
- coherence_score (0-100): Logical flow and topic maintenance  
- lexical_diversity (0-100): Vocabulary richness and repetition
- grammatical_complexity (0-100): Sentence structure complexity
- cognitive_indicators (list): Specific markers of cognitive issues
- risk_level (low/mild/moderate/high/severe): Overall cognitive risk assessment
- clinical_notes (string): Professional observations in user's language
- cultural_considerations (string): Language/culture-specific factors
- language_proficiency (0-100): Estimated language proficiency level
- code_switching_analysis (string): For multilingual contexts like Hinglish

Assessment criteria by language:
- For Indian languages: Consider cultural narrative styles, respect markers, family references
- For Hinglish: Assess natural code-switching vs. confusion-based mixing
- For tonal languages: Consider tone accuracy and meaning preservation
- For Arabic: Assess classical vs. dialectal usage appropriately
- For European languages: Consider grammatical case/gender accuracy

Focus on genuine cognitive markers vs. normal language variation.
"""
        
        return await self.analyze_test_result(
            prompt, 
            {
                "transcription": transcription, 
                "duration": audio_duration, 
                "language": language,
                "word_count": len(transcription.split()) if transcription else 0,
                "speaking_rate": len(transcription.split()) / (audio_duration / 60) if audio_duration > 0 and transcription else 0
            }, 
            self.default_model
        )

groq_service = GroqService()
