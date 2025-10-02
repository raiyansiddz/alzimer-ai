import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  Mic, 
  Square, 
  Play, 
  Clock, 
  CheckCircle, 
  Brain,
  Volume2,
  AlertCircle,
  ArrowRight
} from 'lucide-react'
import TTSButton from './TTSButton'

function SpeechTestInterface({ session, testConfig, onComplete, onExit }) {
  const { t, i18n } = useTranslation()
  const [currentTestIndex, setCurrentTestIndex] = useState(0)
  const [testState, setTestState] = useState('instruction') // instruction, recording, analyzing, completed
  const [isRecording, setIsRecording] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [recordings, setRecordings] = useState({})
  const [analysisResults, setAnalysisResults] = useState({})
  const [totalScore, setTotalScore] = useState(0)
  
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  // Define speech test configurations
  const testDefinitions = {
    'speech-analysis': {
      name: t('tests.speech_language_assessment'),
      tests: [
        {
          id: 'animal_fluency',
          name: t('speech_tests.fluency_animals.name'),
          instruction: t('speech_tests.fluency_animals.instruction'),
          duration: 60,
          type: 'fluency',
          prompt: 'Name as many animals as you can think of. Start now!'
        },
        {
          id: 'picture_description',
          name: t('speech_tests.description_picture.name'),
          instruction: t('speech_tests.description_picture.instruction'), 
          duration: 120,
          type: 'description',
          prompt: 'Describe what you see in the picture. Include details about what is happening.',
          image: '/api/test-images/cookie-theft.jpg' // Standard neuropsych image
        },
        {
          id: 'conversation',
          name: t('speech_tests.conversation_daily.name'),
          instruction: t('speech_tests.conversation_daily.instruction'),
          duration: 180,
          type: 'conversation',
          prompt: 'Tell me about your typical day from morning to evening.'
        }
      ]
    }
  }

  const currentTestDefinition = testDefinitions[testConfig.id]
  const currentTest = currentTestDefinition?.tests[currentTestIndex]
  const totalTests = currentTestDefinition?.tests.length || 1

  useEffect(() => {
    let interval
    if (testState === 'recording' && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => {
          if (time <= 1) {
            stopRecording()
            return 0
          }
          return time - 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [testState, timeRemaining])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      })

      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        handleRecordingComplete(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
      setTestState('recording')
      setTimeRemaining(currentTest.duration)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Microphone access is required for speech tests. Please allow microphone access and try again.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    setIsRecording(false)
  }

  const handleRecordingComplete = async (audioBlob) => {
    setTestState('analyzing')
    
    // Store the recording
    setRecordings(prev => ({
      ...prev,
      [currentTest.id]: {
        blob: audioBlob,
        duration: currentTest.duration - timeRemaining,
        timestamp: new Date().toISOString()
      }
    }))
    
    // Simulate analysis (in real implementation, this would call the backend)
    setTimeout(() => {
      const mockAnalysis = generateMockAnalysis(currentTest.type, audioBlob.size)
      
      setAnalysisResults(prev => ({
        ...prev,
        [currentTest.id]: mockAnalysis
      }))
      
      setTotalScore(prevScore => prevScore + mockAnalysis.total_score)
      setTestState('completed')
    }, 3000)
  }

  const generateMockAnalysis = (testType, audioSize) => {
    // Generate realistic mock analysis based on test type
    const baseScore = Math.random() * 20 + 70 // 70-90 range
    
    switch (testType) {
      case 'fluency':
        return {
          transcription: 'Animals mentioned: cat, dog, elephant, lion, tiger, bear, rabbit, horse, cow, sheep...',
          total_words: Math.floor(Math.random() * 20 + 15),
          unique_animals: Math.floor(Math.random() * 15 + 12),
          fluency_score: Math.round(baseScore),
          coherence_score: Math.round(baseScore + Math.random() * 10 - 5),
          total_score: Math.round(baseScore),
          analysis: {
            strengths: ['Good vocabulary access', 'Clear pronunciation'],
            concerns: [],
            recommendations: ['Continue regular cognitive activities']
          }
        }
      case 'description':
        return {
          transcription: 'I can see a kitchen scene with a woman and children. The woman appears to be washing dishes...',
          word_count: Math.floor(Math.random() * 50 + 80),
          fluency_score: Math.round(baseScore - 5),
          coherence_score: Math.round(baseScore),
          lexical_diversity: Math.round(baseScore + 5),
          total_score: Math.round(baseScore),
          analysis: {
            strengths: ['Good descriptive language', 'Logical sequence'],
            concerns: [],
            recommendations: ['Excellent narrative skills']
          }
        }
      case 'conversation':
        return {
          transcription: 'I usually wake up around 7 AM. Then I have breakfast and read the newspaper...',
          word_count: Math.floor(Math.random() * 80 + 120),
          fluency_score: Math.round(baseScore),
          coherence_score: Math.round(baseScore + 5),
          grammatical_complexity: Math.round(baseScore - 3),
          total_score: Math.round(baseScore),
          analysis: {
            strengths: ['Natural conversation flow', 'Good temporal organization'],
            concerns: [],
            recommendations: ['Strong communication abilities']
          }
        }
      default:
        return {
          total_score: Math.round(baseScore),
          analysis: { strengths: [], concerns: [], recommendations: [] }
        }
    }
  }

  const nextTest = () => {
    if (currentTestIndex < totalTests - 1) {
      setCurrentTestIndex(prev => prev + 1)
      setTestState('instruction')
    } else {
      completeAllTests()
    }
  }

  const completeAllTests = async () => {
    try {
      const finalResults = {
        session_id: session.id,
        test_type: testConfig.id,
        total_score: totalScore,
        max_score: totalTests * 100,
        completion_rate: (totalScore / (totalTests * 100)) * 100,
        recordings: Object.keys(recordings).length,
        analysis_results: analysisResults,
        risk_level: totalScore / totalTests > 75 ? 'low' : totalScore / totalTests > 60 ? 'moderate' : 'high'
      }
      
      console.log('Speech tests completed:', finalResults)
      onComplete(finalResults)
    } catch (error) {
      console.error('Error completing speech tests:', error)
      onComplete({ error: 'Failed to save speech test results' })
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!currentTest) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Test Configuration Error</h2>
          <p className="text-gray-600 mb-8">The selected speech test is not properly configured.</p>
          <button
            onClick={onExit}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          >
            Return to Tests
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="glass rounded-xl p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {currentTestDefinition.name}
            </h1>
            <p className="text-gray-600">
              Test {currentTestIndex + 1} of {totalTests} • {currentTest.name}
            </p>
            <p className="text-sm text-green-600 mt-1">
              Total Score: {Math.round(totalScore)}/{totalTests * 100}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {timeRemaining > 0 && testState === 'recording' && (
              <div className="flex items-center gap-2 px-3 py-2 bg-red-100 rounded-lg">
                <Clock className="w-4 h-4 text-red-600" />
                <span className="font-medium text-red-800">
                  {formatTime(timeRemaining)}
                </span>
              </div>
            )}
            
            <button
              onClick={onExit}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
            >
              Exit Test
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-gray-600">Progress</span>
            <span className="text-sm font-medium text-gray-900">
              {Math.round(((currentTestIndex + (testState === 'completed' ? 1 : 0)) / totalTests) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${((currentTestIndex + (testState === 'completed' ? 1 : 0)) / totalTests) * 100}%` 
              }}
            />
          </div>
        </div>
      </div>

      {/* Test Content */}
      <div className="glass rounded-xl p-8">
        {/* Instructions State */}
        {testState === 'instruction' && (
          <div className="text-center">
            <Mic className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {currentTest.name}
            </h2>
            
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6 text-left">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-green-900">Instructions</h3>
                <TTSButton 
                  text={currentTest.instruction}
                  language={i18n.language}
                  testType="speech-tests"
                  step={`${currentTest.id}-instruction`}
                />
              </div>
              <p className="text-green-800 leading-relaxed mb-4">
                {currentTest.instruction}
              </p>
              
              {currentTest.image && (
                <div className="mt-4 p-4 bg-white rounded border">
                  <p className="font-medium mb-2">You will describe this image:</p>
                  <div className="flex justify-center">
                    <div className="w-64 h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                      <span className="text-gray-500">Cookie Theft Picture</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="flex items-center gap-4 text-sm text-green-700 mt-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Duration: {formatTime(currentTest.duration)}
                </div>
                <div className="flex items-center gap-1">
                  <Mic className="w-4 h-4" />
                  Voice Recording Required
                </div>
              </div>
            </div>

            <button
              onClick={startRecording}
              className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center gap-2 mx-auto"
            >
              <Mic className="w-5 h-5" />
              Start Recording
            </button>
          </div>
        )}

        {/* Recording State */}
        {testState === 'recording' && (
          <div className="text-center">
            <div className="mb-8">
              <div className="relative inline-block">
                <Mic className="w-24 h-24 mx-auto mb-4 text-red-600" />
                <div className="absolute -inset-2 bg-red-200 rounded-full animate-ping opacity-75" />
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Recording in Progress
              </h2>
              
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                <div className="flex items-center justify-center mb-4">
                  <Volume2 className="w-6 h-6 text-red-600 mr-2" />
                  <p className="text-red-800 text-lg font-medium">
                    {currentTest.prompt}
                  </p>
                </div>
                
                {currentTest.image && (
                  <div className="mb-4">
                    <div className="w-64 h-48 bg-gray-200 rounded-lg flex items-center justify-center mx-auto">
                      <span className="text-gray-500">Cookie Theft Picture</span>
                    </div>
                  </div>
                )}
                
                <div className="text-sm text-red-600">
                  Speak clearly and naturally. The recording will stop automatically when time is up.
                </div>
              </div>

              <button
                onClick={stopRecording}
                className="bg-red-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center gap-2 mx-auto"
              >
                <Square className="w-5 h-5" />
                Stop Recording
              </button>
            </div>
          </div>
        )}

        {/* Analyzing State */}
        {testState === 'analyzing' && (
          <div className="text-center">
            <Brain className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-pulse" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Analyzing Speech
            </h2>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <p className="text-blue-800">
                AI is analyzing your speech patterns, fluency, and language complexity...
              </p>
              
              <div className="mt-4 w-full bg-blue-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '60%'}}></div>
              </div>
            </div>
          </div>
        )}

        {/* Completed State */}
        {testState === 'completed' && (
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Analysis Complete
            </h2>
            
            {analysisResults[currentTest.id] && (
              <div className="bg-gray-50 rounded-lg p-6 mb-8 text-left">
                <h3 className="font-semibold text-gray-900 mb-4">Speech Analysis Results</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {analysisResults[currentTest.id].fluency_score || analysisResults[currentTest.id].total_score}
                    </p>
                    <p className="text-sm text-gray-600">Fluency Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {analysisResults[currentTest.id].coherence_score || analysisResults[currentTest.id].total_score}
                    </p>
                    <p className="text-sm text-gray-600">Coherence Score</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">
                      {analysisResults[currentTest.id].total_score}
                    </p>
                    <p className="text-sm text-gray-600">Overall Score</p>
                  </div>
                </div>
                
                {analysisResults[currentTest.id].transcription && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-800 mb-2">Transcription Sample:</h4>
                    <p className="text-sm text-gray-600 bg-white p-3 rounded border italic">
                      "{analysisResults[currentTest.id].transcription.substring(0, 150)}..."
                    </p>
                  </div>
                )}
                
                {analysisResults[currentTest.id].analysis?.strengths?.length > 0 && (
                  <div className="mb-3">
                    <h4 className="font-medium text-green-800 mb-1">Strengths:</h4>
                    <ul className="text-sm text-green-700 list-disc list-inside">
                      {analysisResults[currentTest.id].analysis.strengths.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-center gap-4">
              {currentTestIndex < totalTests - 1 ? (
                <button
                  onClick={nextTest}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center gap-2"
                >
                  Next Test
                  <ArrowRight className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={completeAllTests}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Complete Speech Assessment
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SpeechTestInterface