# Voice Assets Guide for Dementia Detection System

This guide provides detailed instructions for generating and organizing voice files for the multilingual dementia detection system.

## Overview

The system supports **13 languages** with voice assets for all interactive elements. Voice files are organized in a structured hierarchy and play automatically at specific test step transitions when the voice toggle is enabled.

## Supported Languages

| Language Code | Language Name | Native Name |
|---------------|---------------|-------------|
| `en` | English | English |
| `hi` | Hindi | हिन्दी |
| `hi-en` | Hinglish | Hinglish |
| `ta` | Tamil | தமிழ் |
| `te` | Telugu | తెలుగు |
| `bn` | Bengali | বাংলা |
| `mr` | Marathi | मराठी |
| `gu` | Gujarati | ગુજરાતી |
| `es` | Spanish | Español |
| `fr` | French | Français |
| `de` | German | Deutsch |
| `zh` | Chinese | 中文 |
| `ar` | Arabic | العربية |

## File Structure

```
/app/frontend/src/assets/
├── en/
│   ├── cognitive-tests/
│   ├── speech-tests/
│   ├── behavioral-tests/
│   ├── navigation/
│   ├── common/
│   └── instructions/
├── hi/
│   └── [same structure as above]
├── hi-en/
│   └── [same structure as above]
└── [all other languages with same structure]
```

## Voice File Requirements

- **Format**: MP3
- **Quality**: 44.1 kHz, 128 kbps minimum
- **Duration**: Natural speaking pace, clear pronunciation
- **Naming**: Descriptive step names (e.g., `welcome.mp3`, `instruction.mp3`)

## Test Categories and Required Voice Files

### 1. Cognitive Tests (`cognitive-tests/`)

#### MMSE (Mini-Mental State Examination)
- `mmse-welcome.mp3` - Test introduction
- `mmse-instruction.mp3` - General test instructions
- `orientation-time-instruction.mp3` - Time orientation questions introduction
- `orientation-place-instruction.mp3` - Place orientation questions introduction
- `registration-instruction.mp3` - Word registration instructions
- `registration-words.mp3` - The three words to remember
- `attention-instruction.mp3` - Calculation task instructions
- `section-complete.mp3` - Section completion message
- `test-complete.mp3` - Full test completion message

#### AVLT (Auditory Verbal Learning Test)
- `avlt-welcome.mp3` - Test introduction
- `avlt-instruction.mp3` - General instructions
- `word-list-instruction.mp3` - Word list presentation instructions
- `word-list-reading.mp3` - The 15-word list reading
- `recall-instruction.mp3` - Word recall instructions
- `trial-complete.mp3` - Trial completion message

#### Digit Span Test
- `digit-span-welcome.mp3` - Test introduction
- `forward-instruction.mp3` - Forward digit span instructions
- `backward-instruction.mp3` - Backward digit span instructions
- `sequence-prompt.mp3` - "Listen to these numbers" prompt
- `repeat-instruction.mp3` - "Repeat the numbers" instruction

### 2. Speech Tests (`speech-tests/`)

#### Animal Fluency Test
- `fluency-welcome.mp3` - Test introduction
- `fluency-instruction.mp3` - Task instructions (name animals for 60 seconds)
- `start-prompt.mp3` - "Start naming animals now"
- `time-warning.mp3` - "30 seconds remaining"
- `recording-complete.mp3` - Recording completion message

#### Picture Description
- `description-welcome.mp3` - Test introduction
- `description-instruction.mp3` - Picture description instructions
- `describe-prompt.mp3` - "Describe what you see in the picture"
- `recording-start.mp3` - Recording start notification

#### Daily Routine Conversation
- `conversation-welcome.mp3` - Test introduction
- `conversation-instruction.mp3` - Daily routine description instructions
- `conversation-prompt.mp3` - "Tell me about your typical day"

### 3. Behavioral Tests (`behavioral-tests/`)

- `behavioral-welcome.mp3` - General behavioral test introduction
- `response-monitoring-instruction.mp3` - Response time test instructions
- `pattern-recognition-instruction.mp3` - Pattern recognition instructions
- `game-engagement-instruction.mp3` - Interactive games instructions
- `visual-response-instruction.mp3` - Visual response test instructions

### 4. Navigation (`navigation/`)

- `home-welcome.mp3` - Homepage welcome message
- `dashboard-welcome.mp3` - Dashboard welcome message
- `tests-page-intro.mp3` - Tests page introduction
- `reports-page-intro.mp3` - Reports page introduction
- `login-instruction.mp3` - Login page instructions
- `register-instruction.mp3` - Registration page instructions

### 5. Common Elements (`common/`)

- `welcome.mp3` - General welcome message
- `loading.mp3` - "Loading, please wait"
- `error.mp3` - "An error occurred"
- `success.mp3` - "Success"
- `next.mp3` - "Next"
- `previous.mp3` - "Previous"
- `submit.mp3` - "Submit"
- `cancel.mp3` - "Cancel"
- `start.mp3` - "Start"
- `stop.mp3` - "Stop"
- `complete.mp3` - "Complete"
- `continue.mp3` - "Continue"
- `retry.mp3` - "Retry"

### 6. Instructions (`instructions/`)

- `system-introduction.mp3` - System overview and capabilities
- `accessibility-features.mp3` - Accessibility features explanation
- `test-process-overview.mp3` - How tests work
- `voice-toggle-help.mp3` - How to use voice features
- `privacy-notice.mp3` - Privacy and data handling information

## Language-Specific Content Guidelines

### English (`en`)
- Use clear, professional American English
- Moderate pace, clear enunciation
- Gender-neutral voice preferred

### Hindi (`hi`)
- Use standard Hindi (Khari Boli)
- Clear pronunciation with proper matras
- Avoid regional dialects

### Hinglish (`hi-en`)
- Natural code-switching between Hindi and English
- Use common Hinglish expressions
- Maintain clarity for both language speakers

### Tamil (`ta`)
- Use standard literary Tamil
- Clear pronunciation with proper vowel lengths
- Avoid heavy regional accents

### Telugu (`te`)
- Use standard Andhra/Telangana Telugu
- Clear articulation of retroflex sounds
- Professional tone

### Bengali (`bn`)
- Use standard Kolkata Bengali
- Clear pronunciation with proper vowel sounds
- Avoid heavy regional variations

### Marathi (`mr`)
- Use standard Pune Marathi
- Clear enunciation of nasal sounds
- Professional delivery

### Gujarati (`gu`)
- Use standard Ahmedabad Gujarati
- Clear pronunciation with proper aspirated sounds
- Moderate pace

### Spanish (`es`)
- Use neutral Latin American Spanish
- Clear pronunciation, avoiding regional slang
- Professional tone

### French (`fr`)
- Use standard Parisian French
- Clear articulation with proper liaison
- Professional delivery

### German (`de`)
- Use High German (Hochdeutsch)
- Clear pronunciation with proper umlauts
- Professional tone

### Chinese (`zh`)
- Use Mandarin Chinese with standard pronunciation
- Clear tones and proper pinyin
- Professional delivery

### Arabic (`ar`)
- Use Modern Standard Arabic (MSA)
- Clear pronunciation with proper emphatic sounds
- Professional tone

## Voice Recording Guidelines

### Technical Specifications
- **Sample Rate**: 44.1 kHz
- **Bit Depth**: 16-bit minimum
- **Format**: MP3, 128 kbps minimum
- **Mono/Stereo**: Mono preferred for smaller file sizes
- **Background Noise**: Minimal, use noise reduction if necessary

### Recording Environment
- Quiet room with minimal echo/reverb
- Use professional or prosumer microphone
- Maintain consistent distance from microphone
- Record in chunks if needed for quality consistency

### Voice Guidelines
- **Pace**: Natural speaking pace, slightly slower for clarity
- **Tone**: Professional, warm, and reassuring
- **Volume**: Consistent throughout recordings
- **Pronunciation**: Clear and precise
- **Pauses**: Natural pauses between sentences/sections

### Quality Control
- Listen to each recording for clarity
- Check for background noise or audio artifacts
- Ensure consistent volume levels across all files
- Test playback on different devices/speakers

## Auto-Play Trigger Points

Voice files automatically play at these specific test transitions when voice toggle is enabled:

### Cognitive Tests
1. **Test Start**: When user clicks "Start Test"
2. **Section Transition**: When moving between test sections
3. **Instruction Phase**: Before each major test component
4. **Completion**: When test is finished

### Speech Tests
1. **Pre-Recording**: Before recording starts
2. **Recording Start**: When recording begins
3. **Recording Complete**: When recording ends
4. **Results**: When analysis is complete

### Navigation
1. **Page Load**: When entering major sections
2. **State Changes**: During important UI state changes
3. **Error States**: When errors occur
4. **Success States**: When actions complete successfully

## File Naming Convention

Use descriptive, kebab-case naming:

- `test-name-step-description.mp3`
- Examples:
  - `mmse-orientation-time-instruction.mp3`
  - `speech-fluency-animals-start-prompt.mp3`
  - `navigation-dashboard-welcome.mp3`

## Implementation Notes

1. **Fallback Behavior**: If MP3 file is missing, system falls back to browser's built-in Speech Synthesis API
2. **Loading States**: System shows loading indicator while audio loads
3. **Error Handling**: Graceful degradation if audio files fail to load
4. **Performance**: Audio files are loaded on-demand to optimize page load times
5. **Accessibility**: All audio has corresponding text for screen readers

## Testing Your Voice Files

1. Place MP3 files in correct directory structure
2. Start the development server
3. Navigate to test sections
4. Enable voice toggle in settings
5. Verify auto-play functionality at transition points
6. Test fallback behavior by temporarily renaming files

## Maintenance

- **Regular Updates**: Update voice files when UI text changes
- **Quality Checks**: Periodically review audio quality
- **Language Updates**: Add new languages by creating new language directories
- **Version Control**: Track voice file versions for consistency

---

**Note**: This system prioritizes accessibility and multilingual support. High-quality voice assets ensure users with visual impairments or reading difficulties can fully access the cognitive assessment platform.