import os
import json
from groq import Groq
from typing import Optional, Dict, Any
import base64

# Global system prompt for all Groq calls
GLOBAL_SYSTEM_PROMPT = """You are a board-certified neurologist and clinical assessor specialized in cognitive impairment and dementia screening.

Rules:
1. Always respond in JSON only when instructed. Do not include extra natural language.
2. Provide the exact fields requested by the user prompt.
3. For each result include "confidence" (high|medium|low) and "risk_level" (low|medium|high).
4. If audio/image quality is poor, set "confidence": "low" and include "notes".
5. Never provide a definitive medical diagnosis — provide risk assessment and recommend clinical follow-up where appropriate.
6. For patient-facing outputs, produce clear, simple language in the requested locale."""


class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        
    def call_llm(self, user_prompt: str, model: str = "llama-3.3-70b-versatile", 
                 temperature: float = 0.1, max_tokens: int = 2000) -> Dict[str, Any]:
        """Call Groq LLM for text analysis"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": GLOBAL_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Groq LLM Error: {e}")
            return {"error": str(e)}
    
    def call_vision(self, user_prompt: str, image_base64: str, 
                   model: str = "llama-3.2-90b-vision-preview",
                   temperature: float = 0.1, max_tokens: int = 2000) -> Dict[str, Any]:
        """Call Groq Vision for image analysis (clock drawing)"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": GLOBAL_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(content)
            except:
                return {"raw_response": content}
        except Exception as e:
            print(f"Groq Vision Error: {e}")
            return {"error": str(e)}
    
    def transcribe_audio(self, audio_file_path: str, 
                        model: str = "whisper-large-v3") -> str:
        """Transcribe audio using Groq Whisper"""
        try:
            with open(audio_file_path, "rb") as file:
                transcription = self.client.audio.transcriptions.create(
                    file=(audio_file_path, file.read()),
                    model=model,
                    response_format="text"
                )
            return transcription
        except Exception as e:
            print(f"Groq Transcription Error: {e}")
            return ""


# Prompt Templates
class PromptTemplates:
    
    @staticmethod
    def memory_test(locale: str, user_response: str, response_time_ms: Optional[int] = None) -> str:
        return f"""Task: Memory recall (5 words)
Target words: ["Apple", "Ball", "Cat", "Dog", "Elephant"]
Locale: {locale}
Input: {user_response}
Response time: {response_time_ms or 'null'} ms

Return JSON:
{{
  "correct_words": [],
  "missed_words": [],
  "score": 0,
  "total_words": 5,
  "response_time_ms": {response_time_ms or 'null'},
  "cognitive_indicators": [],
  "risk_level": "low|medium|high",
  "confidence": "high|medium|low",
  "notes": ""
}}"""

    @staticmethod
    def pattern_test(locale: str, user_answer: str, correct_answer: str, 
                    response_time_ms: Optional[int] = None) -> str:
        return f"""Task: Pattern recognition
Pattern shown: [Circle, Square, Circle, Square, ___?]
Correct answer: {correct_answer}
Locale: {locale}
User answer: {user_answer}
Response time: {response_time_ms or 'null'} ms

Return JSON:
{{
  "is_correct": true|false,
  "correct_answer": "{correct_answer}",
  "user_answer": "{user_answer}",
  "response_category": "fast|medium|slow",
  "cognitive_indicators": [],
  "risk_level": "low|medium|high",
  "confidence": "high|medium|low",
  "notes": ""
}}"""

    @staticmethod
    def clock_test(locale: str, response_time_ms: Optional[int] = None, 
                  image_metadata: Optional[Dict] = None) -> str:
        metadata = image_metadata or {}
        return f"""Task: Draw a clock that displays 10:30.
Locale: {locale}
Response time: {response_time_ms or 'null'} ms
Image metadata: {json.dumps(metadata)}

Analyze this clock drawing for signs of cognitive impairment.

Return JSON:
{{
  "overall_accuracy": 0.0,
  "numbers_present": true|false,
  "numbers_position": "correct|mostly_correct|incorrect",
  "hands_position": "correct|mostly_correct|incorrect",
  "hand_size_ratio": "correct|incorrect",
  "spatial_organization": "normal|mild_issues|severe_issues",
  "cognitive_indicators": [],
  "dementia_indicators": [],
  "confidence": "high|medium|low",
  "risk_level": "low|medium|high",
  "clinical_notes": ""
}}"""

    @staticmethod
    def speech_test(locale: str, task_type: str, transcription: str, 
                   audio_quality: str = "good") -> str:
        return f"""Task type: {task_type}
Locale: {locale}
Input text: {transcription}
Audio quality: {audio_quality}

Analyze this speech/text for signs of cognitive impairment.

Return JSON:
{{
  "fluency_score": 0.0,
  "hesitation": "low|medium|high",
  "word_finding": "none|minor|moderate|severe",
  "grammar_errors": "none|few|many",
  "vocabulary": "normal|simplified",
  "coherence": "high|medium|low",
  "dementia_indicators": [],
  "risk_level": "low|medium|high",
  "confidence": "high|medium|low",
  "notes": ""
}}"""

    @staticmethod
    def behavioral_analysis(locale: str, interaction_summary: Dict) -> str:
        return f"""Task: Behavioral monitoring analysis
Locale: {locale}
Interaction summary (JSON): {json.dumps(interaction_summary, indent=2)}

Analyze for:
1. Response time trends (improving/stable/worsening)
2. Error frequency (low/medium/high)
3. Navigation efficiency (poor/fair/good/excellent)
4. Learning curve adaptation (poor/fair/good/excellent)
5. Task completion consistency (low/medium/high)

Return JSON:
{{
  "response_time_trend": "improving|stable|worsening",
  "error_frequency": "low|medium|high",
  "navigation_efficiency": "poor|fair|good|excellent",
  "learning_adaptation": "poor|fair|good|excellent",
  "completion_consistency": "low|medium|high",
  "behavioral_indicators": [],
  "risk_level": "low|medium|high",
  "confidence": "high|medium|low",
  "clinical_notes": ""
}}"""

    @staticmethod
    def comprehensive_report(locale: str, all_results: Dict, baseline: Optional[Dict] = None) -> str:
        baseline_str = json.dumps(baseline, indent=2) if baseline else "null"
        return f"""Locale: {locale}
All test results (JSON): {json.dumps(all_results, indent=2)}
Baseline (optional): {baseline_str}

Produce a clinical-structured JSON and a patient-friendly JSON (language = {locale}).

Return JSON:
{{
  "clinical_report": {{
    "overall_risk_score": 0.0,
    "risk_level": "low|medium|high",
    "confidence": "high|medium|low",
    "key_findings": [],
    "significant_indicators": [],
    "baseline_comparison": "",
    "clinical_interpretation": "",
    "recommendations": [],
    "follow_up": "",
    "red_flags": []
  }},
  "patient_friendly": {{
    "summary": "",
    "what_this_means": "",
    "key_findings": [],
    "next_steps": [],
    "reassurance": ""
  }}
}}"""
