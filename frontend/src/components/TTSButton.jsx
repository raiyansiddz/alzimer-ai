import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { Volume2, VolumeX, Loader2 } from 'lucide-react'
import { useVoicePreference } from './VoiceToggle'

function TTSButton({ 
  text, 
  language = 'en', 
  className = '', 
  disabled = false, 
  testType = 'general',
  step = 'instruction',
  autoPlay = false
}) {
  const { t } = useTranslation()
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [audioError, setAudioError] = useState(false)
  const audioRef = useRef(null)
  const voiceEnabled = useVoicePreference()

  // Generate audio file path based on structure: /assets/[language]/[test-type]/[step].mp3
  const getAudioPath = () => {
    return `/src/assets/${language}/${testType}/${step}.mp3`
  }

  useEffect(() => {
    if (autoPlay && !disabled && voiceEnabled && text) {
      // Add a small delay to ensure smooth transitions
      const timeout = setTimeout(() => {
        playTTS()
      }, 500)
      return () => clearTimeout(timeout)
    }
  }, [autoPlay, disabled, voiceEnabled, text])

  const playTTS = async () => {
    if (disabled) return

    if (isPlaying) {
      // Stop current audio
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.currentTime = 0
      }
      setIsPlaying(false)
      return
    }

    try {
      setIsLoading(true)
      setAudioError(false)

      // Try to load and play local audio file
      const audioPath = getAudioPath()
      
      if (audioRef.current) {
        audioRef.current.src = audioPath
        
        await new Promise((resolve, reject) => {
          audioRef.current.onloadeddata = resolve
          audioRef.current.onerror = reject
          audioRef.current.load()
        })
        
        setIsPlaying(true)
        setIsLoading(false)
        
        await audioRef.current.play()
        
      }
    } catch (error) {
      console.warn(`Audio file not found: ${getAudioPath()}, falling back to browser TTS`)
      setAudioError(true)
      setIsLoading(false)
      
      // Fallback to browser's built-in Speech Synthesis
      fallbackToSpeechSynthesis()
    }
  }

  const fallbackToSpeechSynthesis = () => {
    if (!('speechSynthesis' in window) || !text.trim()) {
      setIsPlaying(false)
      return
    }

    try {
      setIsPlaying(true)
      
      // Create speech synthesis utterance
      const utterance = new SpeechSynthesisUtterance(text)
      
      // Configure language and voice
      utterance.lang = language === 'hi-en' ? 'hi' : language
      utterance.rate = 0.8
      utterance.pitch = 1.0
      utterance.volume = 1.0

      // Try to find a voice for the specific language
      const voices = window.speechSynthesis.getVoices()
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith(language.split('-')[0]) || 
        voice.lang.startsWith('hi') || 
        voice.lang.startsWith('en')
      )
      
      if (preferredVoice) {
        utterance.voice = preferredVoice
      }

      // Set up event listeners
      utterance.onend = () => {
        setIsPlaying(false)
      }

      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error)
        setIsPlaying(false)
      }

      // Speak the text
      window.speechSynthesis.speak(utterance)

    } catch (error) {
      console.error('Fallback TTS Error:', error)
      setIsPlaying(false)
    }
  }

  const handleAudioEnd = () => {
    setIsPlaying(false)
  }

  const handleAudioError = () => {
    console.warn('Audio playback error, falling back to speech synthesis')
    setAudioError(true)
    setIsPlaying(false)
    setIsLoading(false)
    fallbackToSpeechSynthesis()
  }

  return (
    <>
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        onError={handleAudioError}
        style={{ display: 'none' }}
      />
      
      <button
        onClick={playTTS}
        disabled={disabled || isLoading}
        className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
          isPlaying 
            ? 'bg-red-100 text-red-700 hover:bg-red-200' 
            : audioError 
              ? 'bg-orange-100 text-orange-700 hover:bg-orange-200' 
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
        } disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
        title={
          isLoading 
            ? 'Loading...' 
            : isPlaying 
              ? t('common.stop') 
              : audioError 
                ? 'Using fallback voice' 
                : t('common.play')
        }
        data-testid="tts-button"
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : isPlaying ? (
          <VolumeX className="w-4 h-4" />
        ) : (
          <Volume2 className="w-4 h-4" />
        )}
        <span className="text-sm font-medium">
          {isLoading 
            ? 'Loading...' 
            : isPlaying 
              ? t('common.stop') 
              : audioError 
                ? 'Fallback' 
                : t('common.play')
          }
        </span>
      </button>
    </>
  )
}

export default TTSButton