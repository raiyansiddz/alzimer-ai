import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Volume2, VolumeX, Loader2 } from 'lucide-react'

function TTSButton({ text, language = 'en', className = '', disabled = false }) {
  const { t } = useTranslation()
  const [isPlaying, setIsPlaying] = useState(false)
  const [isSupported, setIsSupported] = useState(false)

  useEffect(() => {
    // Check if browser supports Speech Synthesis
    setIsSupported('speechSynthesis' in window)
  }, [])

  const playTTS = async () => {
    if (!isSupported || !text.trim()) return

    if (isPlaying) {
      // Stop current speech
      window.speechSynthesis.cancel()
      setIsPlaying(false)
      return
    }

    try {
      setIsPlaying(true)

      // Create speech synthesis utterance
      const utterance = new SpeechSynthesisUtterance(text)
      
      // Configure language and voice
      utterance.lang = language
      utterance.rate = 0.8 // Slightly slower for better comprehension
      utterance.pitch = 1.0
      utterance.volume = 1.0

      // Try to find a voice for the specific language
      const voices = window.speechSynthesis.getVoices()
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith(language) || 
        voice.lang.startsWith(language.split('-')[0])
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
      console.error('TTS Error:', error)
      setIsPlaying(false)
    }
  }

  if (!isSupported) {
    return null // Don't render if not supported
  }

  return (
    <button
      onClick={playTTS}
      disabled={disabled}
      className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
        isPlaying 
          ? 'bg-red-100 text-red-700 hover:bg-red-200' 
          : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
      } disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
      title={isPlaying ? t('common.stop') : t('common.play')}
      data-testid="tts-button"
    >
      {isPlaying ? (
        <VolumeX className="w-4 h-4" />
      ) : (
        <Volume2 className="w-4 h-4" />
      )}
      <span className="text-sm font-medium">
        {isPlaying ? t('common.stop') : t('common.play')}
      </span>
    </button>
  )
}

export default TTSButton