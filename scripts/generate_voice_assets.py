#!/usr/bin/env python3
"""
Voice Assets Generator for Dementia Detection System
Creates placeholder voice files and validates the voice system structure
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List

class VoiceAssetsGenerator:
    def __init__(self, base_path: str = "/app/frontend/src/assets"):
        self.base_path = Path(base_path)
        self.languages = [
            "en", "hi", "hi-en", "ta", "te", "bn", "mr", "gu", 
            "es", "fr", "de", "zh", "ar"
        ]
        self.categories = {
            "cognitive-tests": [
                "mmse-welcome.mp3",
                "mmse-instruction.mp3", 
                "orientation-time-instruction.mp3",
                "orientation-place-instruction.mp3",
                "registration-instruction.mp3",
                "registration-words.mp3",
                "attention-instruction.mp3",
                "section-complete.mp3",
                "test-complete.mp3",
                "avlt-welcome.mp3",
                "avlt-instruction.mp3",
                "word-list-instruction.mp3",
                "word-list-reading.mp3",
                "recall-instruction.mp3",
                "trial-complete.mp3",
                "digit-span-welcome.mp3",
                "forward-instruction.mp3",
                "backward-instruction.mp3",
                "sequence-prompt.mp3",
                "repeat-instruction.mp3"
            ],
            "speech-tests": [
                "fluency-animals-welcome.mp3",
                "fluency-animals-instruction.mp3",
                "fluency-animals-prompt.mp3",
                "description-picture-welcome.mp3", 
                "description-picture-instruction.mp3",
                "description-picture-prompt.mp3",
                "conversation-daily-welcome.mp3",
                "conversation-daily-instruction.mp3",
                "conversation-daily-prompt.mp3",
                "start-prompt.mp3",
                "time-warning.mp3",
                "recording-complete.mp3",
                "recording-start.mp3"
            ],
            "behavioral-tests": [
                "behavioral-welcome.mp3",
                "response-monitoring-instruction.mp3",
                "pattern-recognition-instruction.mp3",
                "game-engagement-instruction.mp3",
                "visual-response-instruction.mp3"
            ],
            "navigation": [
                "home-welcome.mp3",
                "dashboard-welcome.mp3",
                "tests-page-intro.mp3",
                "reports-page-intro.mp3",
                "login-instruction.mp3",
                "register-instruction.mp3"
            ],
            "common": [
                "welcome.mp3",
                "loading.mp3",
                "error.mp3",
                "success.mp3",
                "next.mp3",
                "previous.mp3",
                "submit.mp3",
                "cancel.mp3",
                "start.mp3",
                "stop.mp3",
                "complete.mp3",
                "continue.mp3",
                "retry.mp3"
            ],
            "instructions": [
                "system-introduction.mp3",
                "accessibility-features.mp3",
                "test-process-overview.mp3",
                "voice-toggle-help.mp3",
                "privacy-notice.mp3"
            ]
        }
        
        # Sample texts for each file (for TTS generation)
        self.sample_texts = {
            "cognitive-tests": {
                "mmse-welcome.mp3": "Welcome to the Mini-Mental State Examination. This test will assess various aspects of your cognitive function.",
                "mmse-instruction.mp3": "I will ask you a series of questions and tasks. Please answer to the best of your ability.",
                "orientation-time-instruction.mp3": "I will now ask you some questions about time. Please answer each question.",
                "orientation-place-instruction.mp3": "Now I will ask you questions about where we are.",
                "registration-instruction.mp3": "I will say three words. Please listen carefully and repeat them back to me.",
                "registration-words.mp3": "The three words are: Apple, Penny, Table.",
                "attention-instruction.mp3": "I want you to count backwards from 100 by sevens. Say each number out loud.",
                "section-complete.mp3": "This section is complete. Well done.",
                "test-complete.mp3": "You have completed the test. Thank you for your participation.",
                "avlt-welcome.mp3": "Welcome to the Auditory Verbal Learning Test.",
                "avlt-instruction.mp3": "I will read you a list of words. Try to remember as many as possible.",
                "word-list-instruction.mp3": "Listen carefully to this list of words.",
                "word-list-reading.mp3": "Here are the fifteen words: Drum, Curtain, Bell, Coffee, School, Parent, Moon, Garden, Hat, Farmer, Nose, Turkey, Color, House, River.",
                "recall-instruction.mp3": "Now tell me all the words you can remember from the list.",
                "trial-complete.mp3": "This trial is complete. Let's continue with the next trial.",
                "digit-span-welcome.mp3": "Welcome to the Digit Span Test.",
                "forward-instruction.mp3": "I will say some numbers. Repeat them back in the same order.",
                "backward-instruction.mp3": "Now repeat the numbers in reverse order.",
                "sequence-prompt.mp3": "Listen to these numbers:",
                "repeat-instruction.mp3": "Now repeat the numbers back to me."
            },
            "speech-tests": {
                "fluency-animals-welcome.mp3": "Welcome to the Animal Fluency Test.",
                "fluency-animals-instruction.mp3": "Name as many different animals as you can in 60 seconds.",
                "fluency-animals-prompt.mp3": "Start naming animals now.",
                "description-picture-welcome.mp3": "Welcome to the Picture Description Test.",
                "description-picture-instruction.mp3": "Please describe what you see in the picture in detail.",
                "description-picture-prompt.mp3": "Tell me everything you see in this picture.",
                "conversation-daily-welcome.mp3": "Welcome to the Daily Routine Conversation.",
                "conversation-daily-instruction.mp3": "Tell me about your typical daily routine.",
                "conversation-daily-prompt.mp3": "Describe what you do during a typical day.",
                "start-prompt.mp3": "You may start speaking now.",
                "time-warning.mp3": "Thirty seconds remaining.",
                "recording-complete.mp3": "Recording complete. Thank you.",
                "recording-start.mp3": "Recording has started."
            },
            "behavioral-tests": {
                "behavioral-welcome.mp3": "Welcome to the behavioral assessment section.",
                "response-monitoring-instruction.mp3": "We will monitor your response times during this task.",
                "pattern-recognition-instruction.mp3": "Look for patterns in the following sequence.",
                "game-engagement-instruction.mp3": "Please engage with the interactive elements on screen.",
                "visual-response-instruction.mp3": "Respond when you see the target stimulus."
            },
            "navigation": {
                "home-welcome.mp3": "Welcome to the Dementia Detection System.",
                "dashboard-welcome.mp3": "Welcome to your dashboard.",
                "tests-page-intro.mp3": "Here you can access available cognitive tests.",
                "reports-page-intro.mp3": "Your test reports and results are displayed here.",
                "login-instruction.mp3": "Please enter your login credentials.",
                "register-instruction.mp3": "Please fill out the registration form."
            },
            "common": {
                "welcome.mp3": "Welcome",
                "loading.mp3": "Loading, please wait",
                "error.mp3": "An error occurred",
                "success.mp3": "Success",
                "next.mp3": "Next",
                "previous.mp3": "Previous",
                "submit.mp3": "Submit",
                "cancel.mp3": "Cancel",
                "start.mp3": "Start",
                "stop.mp3": "Stop",
                "complete.mp3": "Complete",
                "continue.mp3": "Continue",
                "retry.mp3": "Retry"
            },
            "instructions": {
                "system-introduction.mp3": "This system provides comprehensive cognitive assessment tools designed for accessibility.",
                "accessibility-features.mp3": "Voice guidance, high contrast modes, and audio-only tests are available.",
                "test-process-overview.mp3": "Tests are administered with clear instructions and progress indicators.",
                "voice-toggle-help.mp3": "Toggle voice guidance on or off using the voice button in the header.",
                "privacy-notice.mp3": "Your test data is securely stored and used only for assessment purposes."
            }
        }

    def create_directory_structure(self):
        """Create the complete directory structure for voice assets"""
        print("Creating voice assets directory structure...")
        
        for language in self.languages:
            lang_path = self.base_path / language
            lang_path.mkdir(exist_ok=True)
            
            for category in self.categories:
                category_path = lang_path / category
                category_path.mkdir(exist_ok=True)
                print(f"Created: {category_path}")
        
        print(f"Directory structure created for {len(self.languages)} languages and {len(self.categories)} categories")

    def generate_placeholder_files(self):
        """Generate placeholder MP3 files for development/testing"""
        print("Generating placeholder voice files...")
        
        total_files = 0
        
        for language in self.languages:
            lang_path = self.base_path / language
            
            for category, files in self.categories.items():
                category_path = lang_path / category
                
                for file_name in files:
                    file_path = category_path / file_name
                    
                    if not file_path.exists():
                        # Create a minimal placeholder MP3 file
                        self.create_placeholder_mp3(file_path, category, file_name)
                        total_files += 1
        
        print(f"Generated {total_files} placeholder voice files")

    def create_placeholder_mp3(self, file_path: Path, category: str, file_name: str):
        """Create a placeholder MP3 file using ffmpeg if available"""
        try:
            # Get text for this file
            text = self.sample_texts.get(category, {}).get(file_name, "Audio placeholder")
            
            # Try to use system TTS if available (macOS example)
            if os.system("which say > /dev/null 2>&1") == 0:
                # macOS TTS
                temp_file = f"/tmp/temp_audio_{file_name}.aiff"
                os.system(f'say "{text}" -o {temp_file}')
                
                # Convert to MP3 if ffmpeg is available
                if os.system("which ffmpeg > /dev/null 2>&1") == 0:
                    os.system(f'ffmpeg -i {temp_file} -acodec libmp3lame -ab 128k "{file_path}" > /dev/null 2>&1')
                    os.remove(temp_file)
                else:
                    # Just move the AIFF file
                    os.rename(temp_file, str(file_path).replace('.mp3', '.aiff'))
            
            elif os.system("which espeak > /dev/null 2>&1") == 0:
                # Linux espeak TTS
                os.system(f'espeak "{text}" -w /tmp/temp_audio.wav')
                if os.system("which ffmpeg > /dev/null 2>&1") == 0:
                    os.system(f'ffmpeg -i /tmp/temp_audio.wav "{file_path}" > /dev/null 2>&1')
                    os.remove('/tmp/temp_audio.wav')
            
            else:
                # Create a silent placeholder file
                if os.system("which ffmpeg > /dev/null 2>&1") == 0:
                    duration = min(len(text) * 0.1, 10)  # Rough estimate: 0.1s per character, max 10s
                    os.system(f'ffmpeg -f lavfi -i anullsrc=channel_layout=mono:sample_rate=44100 -t {duration} -acodec libmp3lame "{file_path}" > /dev/null 2>&1')
                else:
                    # Create an empty file as last resort
                    file_path.touch()
                    
        except Exception as e:
            print(f"Warning: Could not create audio for {file_path}: {e}")
            # Create empty placeholder
            file_path.touch()

    def validate_structure(self) -> Dict[str, any]:
        """Validate the voice assets structure"""
        print("Validating voice assets structure...")
        
        validation_results = {
            "languages_found": 0,
            "categories_found": 0,
            "total_files_found": 0,
            "missing_files": [],
            "structure_complete": True
        }
        
        for language in self.languages:
            lang_path = self.base_path / language
            if lang_path.exists():
                validation_results["languages_found"] += 1
                
                for category, expected_files in self.categories.items():
                    category_path = lang_path / category
                    if category_path.exists():
                        validation_results["categories_found"] += 1
                        
                        for file_name in expected_files:
                            file_path = category_path / file_name
                            if file_path.exists():
                                validation_results["total_files_found"] += 1
                            else:
                                validation_results["missing_files"].append(str(file_path))
                                validation_results["structure_complete"] = False
        
        return validation_results

    def generate_manifest_file(self):
        """Update the audio manifest file with current structure"""
        manifest = {
            "version": "1.0.0",
            "description": "Audio assets manifest for Dementia Detection System",
            "generated_timestamp": str(Path().resolve()),
            "languages": self.languages,
            "categories": {}
        }
        
        total_files = 0
        for category, files in self.categories.items():
            manifest["categories"][category] = {
                "description": f"Voice files for {category.replace('-', ' ')}",
                "files": files,
                "file_count": len(files)
            }
            total_files += len(files)
        
        manifest["total_files_per_language"] = total_files
        manifest["total_files_all_languages"] = total_files * len(self.languages)
        
        manifest_path = self.base_path / "audio-manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"Updated manifest file: {manifest_path}")

    def run_complete_setup(self):
        """Run the complete voice assets setup process"""
        print("🎵 Starting Voice Assets Generation for Dementia Detection System")
        print("=" * 70)
        
        # Create directory structure
        self.create_directory_structure()
        print()
        
        # Generate placeholder files
        self.generate_placeholder_files()
        print()
        
        # Validate structure
        validation = self.validate_structure()
        print(f"📊 Validation Results:")
        print(f"   Languages: {validation['languages_found']}/{len(self.languages)}")
        print(f"   Total Files: {validation['total_files_found']}")
        print(f"   Structure Complete: {validation['structure_complete']}")
        
        if validation['missing_files']:
            print(f"   Missing Files: {len(validation['missing_files'])}")
        print()
        
        # Generate manifest
        self.generate_manifest_file()
        print()
        
        print("✅ Voice Assets Setup Complete!")
        print("\n📝 Next Steps:")
        print("1. Replace placeholder files with professional recordings")
        print("2. Test voice system with actual audio files")
        print("3. Ensure all files meet quality standards (44.1kHz, 128kbps+)")
        print("4. Test accessibility features with real users")
        
        return validation

if __name__ == "__main__":
    generator = VoiceAssetsGenerator()
    results = generator.run_complete_setup()