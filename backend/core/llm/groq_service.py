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
        Transcribe audio using Groq Whisper with language support
        """
        try:
            start_time = time.time()
            
            with open(audio_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=audio_file,
                    response_format="json",
                    language=language if language in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi'] else None
                )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return {
                "transcription": response.text,
                "language": language,
                "processing_time": processing_time
            }
        except Exception as e:
            print(f"Groq transcription error: {str(e)}")
            raise
    
    async def generate_speech(self, text: str, language: str = "en", voice: str = "Fritz-PlayAI") -> bytes:
        """
        Generate speech using Groq PlayAI TTS
        """
        try:
            start_time = time.time()
            
            # Select appropriate model based on language
            if language in ['ar']:
                model = "playai-tts-arabic"
                # Use Arabic voices: Sara-PlayAI, Khalid-PlayAI, Layla-PlayAI, Ahmed-PlayAI
                voice = "Sara-PlayAI" if voice == "Fritz-PlayAI" else voice
            else:
                model = "playai-tts"
                # Default English voice options: Fritz-PlayAI, Atlas-PlayAI, Calum-PlayAI, etc.
            
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="wav"
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Write the response to a bytes object
            audio_bytes = response.content if hasattr(response, 'content') else response.read()
            
            print(f"TTS generated successfully in {processing_time}ms for language: {language}")
            return audio_bytes
            
        except Exception as e:
            print(f"Groq TTS error: {str(e)}")
            # Return empty bytes if TTS fails
            return b""
    
    async def analyze_speech_pattern(self, transcription: str, audio_duration: int, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze speech patterns for cognitive assessment with language support
        """
        language = user_context.get('language', 'en')
        
        prompt = f"""
You are a speech-language pathologist specializing in cognitive assessment for {language} speakers.
Analyze the following speech sample for cognitive impairment indicators, considering cultural and linguistic norms.

Transcription: {transcription}
Duration: {audio_duration} seconds
User Context: {json.dumps(user_context)}

Provide analysis in JSON format with:
- fluency_score (0-100)
- coherence_score (0-100)
- lexical_diversity (0-100)
- grammatical_complexity (0-100)
- cognitive_indicators (list)
- risk_level (low/medium/high)
- clinical_notes (string in {language})
- cultural_considerations (string explaining language-specific factors)

Consider:
- Language-specific fluency patterns
- Cultural communication styles
- Code-switching behavior (if applicable)
- Dialect variations
"""
        
        return await self.analyze_test_result(prompt, {"transcription": transcription, "duration": audio_duration, "language": language}, self.default_model)

groq_service = GroqService()
