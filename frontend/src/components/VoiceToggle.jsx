import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Volume2, VolumeX } from 'lucide-react'

function VoiceToggle({ className = '' }) {
  const { t } = useTranslation()
  const [voiceEnabled, setVoiceEnabled] = useState(false)

  useEffect(() => {
    // Load voice preference from localStorage
    const savedPreference = localStorage.getItem('voiceEnabled')
    if (savedPreference !== null) {
      setVoiceEnabled(JSON.parse(savedPreference))
    }
  }, [])

  const toggleVoice = () => {
    const newState = !voiceEnabled
    setVoiceEnabled(newState)
    localStorage.setItem('voiceEnabled', JSON.stringify(newState))
    
    // Dispatch custom event to notify other components
    window.dispatchEvent(new CustomEvent('voiceToggleChanged', {
      detail: { voiceEnabled: newState }
    }))
    
    // Provide feedback to user
    if (newState) {
      // Play a welcome sound or announcement
      const utterance = new SpeechSynthesisUtterance(t('common.voice_enabled') || 'Voice assistance enabled')
      utterance.volume = 0.7
      utterance.rate = 0.9
      window.speechSynthesis.speak(utterance)
    }
  }

  return (
    <button
      onClick={toggleVoice}
      className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-colors ${
        voiceEnabled
          ? 'bg-green-100 text-green-700 hover:bg-green-200'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      } ${className}`}
      title={voiceEnabled ? t('common.voice_disable') || 'Disable voice' : t('common.voice_enable') || 'Enable voice'}
      data-testid="voice-toggle"
      aria-label={voiceEnabled ? 'Disable voice assistance' : 'Enable voice assistance'}
      aria-pressed={voiceEnabled}
    >
      {voiceEnabled ? (
        <Volume2 className="w-4 h-4" />
      ) : (
        <VolumeX className="w-4 h-4" />
      )}
      <span className="text-sm font-medium hidden sm:inline">
        {voiceEnabled ? (t('common.voice_on') || 'Voice On') : (t('common.voice_off') || 'Voice Off')}
      </span>
    </button>
  )
}

// Hook to get voice preference in other components
export function useVoicePreference() {
  const [voiceEnabled, setVoiceEnabled] = useState(false)

  useEffect(() => {
    // Load initial state
    const savedPreference = localStorage.getItem('voiceEnabled')
    if (savedPreference !== null) {
      setVoiceEnabled(JSON.parse(savedPreference))
    }

    // Listen for changes
    const handleVoiceToggle = (event) => {
      setVoiceEnabled(event.detail.voiceEnabled)
    }

    window.addEventListener('voiceToggleChanged', handleVoiceToggle)
    return () => window.removeEventListener('voiceToggleChanged', handleVoiceToggle)
  }, [])

  return voiceEnabled
}

export default VoiceToggle