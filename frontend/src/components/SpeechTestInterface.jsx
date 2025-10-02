import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  Mic, 
  Square, 
  Play, 
  Upload,
  Volume2,
  CheckCircle,
  AlertCircle,
  Clock,
  FileAudio
} from 'lucide-react'
import TTSButton from './TTSButton'

function SpeechTestInterface({ session, testConfig, onComplete, onExit }) {
  const { t, i18n } = useTranslation()
  const [currentTestIndex, setCurrentTestIndex] = useState(0)
  const [testState, setTestState] = useState('instruction')
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [transcription, setTranscription] = useState('')
  const [recordingTime, setRecordingTime] = useState(0)
  const [analysisResult, setAnalysisResult] = useState(null)

  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const intervalRef = useRef(null)

  const speechTests = [
    {
      id: 'fluency_animals',
      type: 'fluency',
      name: t('speech_tests.fluency_animals.name'),
      instruction: t('speech_tests.fluency_animals.instruction'),
      duration: 60,
      prompt: t('speech_tests.fluency_animals.prompt')
    },
    {
      id: 'description_picture',
      type: 'description', 
      name: t('speech_tests.description_picture.name'),
      instruction: t('speech_tests.description_picture.instruction'),
      duration: 120,
      prompt: t('speech_tests.description_picture.prompt'),
      image: 'https://images.unsplash.com/photo-1515378960530-7c0da6231fb1?w=500&h=400&fit=crop' // Picnic scene
    },
    {
      id: 'conversation_daily',
      type: 'conversation',
      name: t('speech_tests.conversation_daily.name'),
      instruction: t('speech_tests.conversation_daily.instruction'),
      duration: 180,
      prompt: t('speech_tests.conversation_daily.prompt')
    }
  ]

  const currentTest = speechTests[currentTestIndex]

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop()
      }
    }
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        } 
      })

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start(1000) // Collect data every second
      setIsRecording(true)
      setRecordingTime(0)
      setTestState('recording')

      // Start timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => {
          if (prev >= currentTest.duration) {
            stopRecording()
            return prev
          }
          return prev + 1
        })
      }, 1000)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Could not access microphone. Please check your permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    
    setIsRecording(false)
    clearInterval(intervalRef.current)
    setTestState('processing')
  }

  const submitRecording = async () => {
    if (!audioBlob) return

    try {
      setTestState('analyzing')
      
      // Create FormData for upload
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')
      formData.append('session_id', session.id)
      formData.append('test_name', currentTest.name)
      formData.append('test_context', JSON.stringify({
        test_type: currentTest.type,
        prompt_text: currentTest.prompt,
        expected_duration: currentTest.duration,
        language: i18n.language
      }))

      // Submit to enhanced speech API
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/speech-tests/enhanced/submit`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to analyze speech')
      }

      const result = await response.json()
      setAnalysisResult(result)
      setTranscription(result.transcription)
      setTestState('results')

    } catch (error) {
      console.error('Error analyzing speech:', error)
      setTestState('error')
    }
  }

  const nextTest = () => {
    if (currentTestIndex < speechTests.length - 1) {
      setCurrentTestIndex(currentTestIndex + 1)
      setTestState('instruction')
      setAudioBlob(null)
      setTranscription('')
      setRecordingTime(0)
      setAnalysisResult(null)
    } else {
      onComplete()
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="glass rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{currentTest.name}</h1>
            <p className="text-gray-600">
              Test {currentTestIndex + 1} of {speechTests.length} • Speech Assessment
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {recordingTime > 0 && (
              <div className="flex items-center gap-2 px-3 py-2 bg-red-100 rounded-lg">
                <div className="w-2 h-2 bg-red-600 rounded-full animate-pulse" />
                <span className="font-medium text-red-800">
                  {formatTime(recordingTime)} / {formatTime(currentTest.duration)}
                </span>
              </div>
            )}
            
            <button
              onClick={onExit}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              data-testid="exit-test-btn"
            >
              {t('tests.exit_test')}
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-gray-600">{t('tests.progress')}</span>
            <span className="text-sm font-medium text-gray-900">
              {Math.round(((currentTestIndex + (testState === 'results' ? 1 : 0)) / speechTests.length) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${((currentTestIndex + (testState === 'results' ? 1 : 0)) / speechTests.length) * 100}%` 
              }}
            />
          </div>
        </div>
      </div>

      {/* Test Content */}
      <div className="glass rounded-xl p-8">
        {/* Instructions */}
        {testState === 'instruction' && (
          <div className="text-center">
            <div className="mb-8">
              <Mic className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {currentTest.name}
              </h2>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6 text-left">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-green-900">{t('tests.instructions_title')}</h3>
                  <TTSButton 
                    text={currentTest.instruction}
                    language={i18n.language}
                    className="text-xs"
                    testType="speech-tests"
                    step={`${currentTest.id}-instruction`}
                    autoPlay={testState === 'instruction'}
                  />
                </div>
                <p className="text-green-800 leading-relaxed mb-4">
                  {currentTest.instruction}
                </p>
                
                <div className="flex items-center gap-4 text-sm text-green-700">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {t('tests.duration')}: {formatTime(currentTest.duration)}
                  </div>
                  <div className="flex items-center gap-1">
                    <Mic className="w-4 h-4" />
                    {t('speech_tests.record_instruction')}
                  </div>
                </div>
              </div>

              {/* Picture for description task */}
              {currentTest.image && (
                <div className="mb-6">
                  <img 
                    src={currentTest.image}
                    alt="Picture to describe"
                    className="max-w-md mx-auto rounded-lg shadow-lg"
                  />
                </div>
              )}
            </div>

            <button
              onClick={startRecording}
              className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center gap-2 mx-auto"
              data-testid="start-recording-btn"
            >
              <Mic className="w-5 h-5" />
              {t('speech_tests.record_instruction')}
            </button>
          </div>
        )}

        {/* Recording */}
        {testState === 'recording' && (
          <div className="text-center">
            <div className="mb-8">
              <div className="relative inline-block">
                <Mic className="w-24 h-24 text-red-600 mx-auto mb-4" />
                <div className="absolute -inset-2 bg-red-200 rounded-full animate-ping opacity-75" />
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('speech_tests.recording_in_progress')}</h2>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-red-800 font-medium">{currentTest.prompt}</p>
                  <TTSButton 
                    text={currentTest.prompt}
                    language={i18n.language}
                    className="text-xs"
                    testType="speech-tests"
                    step={`${currentTest.id}-prompt`}
                    autoPlay={testState === 'recording'}
                  />
                </div>
                <div className="text-2xl font-bold text-red-900">
                  {formatTime(recordingTime)} / {formatTime(currentTest.duration)}
                </div>
              </div>
            </div>

            <button
              onClick={stopRecording}
              className="bg-red-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center gap-2 mx-auto"
              data-testid="stop-recording-btn"
            >
              <Square className="w-5 h-5" />
              {t('speech_tests.stop_recording')}
            </button>
          </div>
        )}

        {/* Processing */}
        {testState === 'processing' && (
          <div className="text-center">
            <FileAudio className="w-16 h-16 text-blue-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">{t('speech_tests.recording_complete')}</h2>
            
            <p className="text-gray-600 mb-8">
              {t('speech_tests.submit_recording')}
            </p>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => setTestState('recording')}
                className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              >
                {t('speech_tests.record_again')}
              </button>
              
              <button
                onClick={submitRecording}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                data-testid="submit-recording-btn"
              >
                {t('speech_tests.submit_recording')}
              </button>
            </div>
          </div>
        )}

        {/* Analyzing */}
        {testState === 'analyzing' && (
          <div className="text-center">
            <div className="mb-8">
              <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('speech_tests.analyzing_speech')}</h2>
              <p className="text-gray-600">
                {t('speech_tests.analysis')}
              </p>
            </div>
          </div>
        )}

        {/* Results */}
        {testState === 'results' && analysisResult && (
          <div>
            <div className="mb-8 text-center">
              <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('speech_tests.analysis_complete')}</h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              {/* Transcription */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <FileAudio className="w-4 h-4" />
                  {t('speech_tests.transcription')}
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {transcription || 'Transcription not available'}
                </p>
              </div>

              {/* Scores */}
              <div className="space-y-4">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{t('speech_tests.fluency_score')}</span>
                    <span className="text-xl font-bold text-blue-600">
                      {Math.round(analysisResult.linguistic_analysis?.fluency_score || 0)}%
                    </span>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">{t('speech_tests.coherence_score')}</span>
                    <span className="text-xl font-bold text-purple-600">
                      {Math.round(analysisResult.linguistic_analysis?.coherence_score || 0)}%
                    </span>
                  </div>
                </div>

                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-900">Lexical Diversity</span>
                    <span className="text-xl font-bold text-green-600">
                      {Math.round(analysisResult.linguistic_analysis?.lexical_diversity || 0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {analysisResult.recommendations && (
              <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-indigo-900 mb-3">{t('speech_tests.recommendations')}</h3>
                <div className="text-indigo-800">
                  {typeof analysisResult.recommendations === 'string' 
                    ? analysisResult.recommendations
                    : JSON.stringify(analysisResult.recommendations, null, 2)
                  }
                </div>
              </div>
            )}

            <div className="flex justify-center">
              {currentTestIndex < speechTests.length - 1 ? (
                <button
                  onClick={nextTest}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                  data-testid="next-speech-test-btn"
                >
                  {t('common.next')} {t('tests.speech_tests')}
                </button>
              ) : (
                <button
                  onClick={onComplete}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                  data-testid="complete-speech-tests-btn"
                >
                  {t('common.complete')} {t('tests.speech_tests')}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Error */}
        {testState === 'error' && (
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Analysis Failed</h2>
            
            <p className="text-gray-600 mb-8">
              We encountered an error while analyzing your speech. Please try again.
            </p>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => setTestState('processing')}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
              
              <button
                onClick={nextTest}
                className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
              >
                Skip Test
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SpeechTestInterface