import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  Brain, 
  Clock, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Play,
  Pause,
  Mic,
  Square,
  RotateCcw,
  AlertCircle
} from 'lucide-react'
import TTSButton from './TTSButton'
import { testSessionAPI } from '../lib/api'

function CognitiveTestInterface({ session, testConfig, onComplete, onExit }) {
  const { t, i18n } = useTranslation()
  const [currentTestIndex, setCurrentTestIndex] = useState(0)
  const [testState, setTestState] = useState('instruction') // instruction, active, completed
  const [responses, setResponses] = useState({})
  const [currentResponse, setCurrentResponse] = useState('')
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [score, setScore] = useState(0)
  const [maxScore, setMaxScore] = useState(0)
  
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])

  // Define comprehensive test configurations
  const testDefinitions = {
    'cognitive-battery': {
      name: t('tests.comprehensive_cognitive_battery'),
      tests: [
        {
          id: 'mmse_orientation',
          name: 'MMSE - Orientation',
          type: 'questions',
          instruction: 'Please answer the following questions about time and place.',
          questions: [
            'What year is it?',
            'What season is it?', 
            'What month is it?',
            'What is today\'s date?',
            'What day of the week is it?',
            'What country are we in?',
            'What state/province are we in?',
            'What city are we in?',
            'What building are we in?',
            'What floor are we on?'
          ],
          maxScore: 10,
          timeLimit: 300
        },
        {
          id: 'mmse_memory',
          name: 'MMSE - Memory',
          type: 'memory',
          instruction: 'I will say three words. Listen carefully and repeat them back to me.',
          words: ['Apple', 'Penny', 'Table'],
          maxScore: 3,
          timeLimit: 60
        },
        {
          id: 'digit_span',
          name: 'Digit Span Test',
          type: 'digit_sequence',
          instruction: 'I will say some numbers. Repeat them back in the same order.',
          sequences: [
            '2-1-9',
            '4-2-7-3', 
            '1-5-2-8-6',
            '6-1-9-4-7-3'
          ],
          maxScore: 4,
          timeLimit: 180
        }
      ]
    },
    'memory-focus': {
      name: t('tests.memory_assessment'),
      tests: [
        {
          id: 'word_recall',
          name: 'Word List Recall',
          type: 'memory_list',
          instruction: 'I will read 15 words. Listen carefully and remember as many as you can.',
          wordList: ['Drum', 'Curtain', 'Bell', 'Coffee', 'School', 'Parent', 'Moon', 'Garden', 'Hat', 'Farmer', 'Nose', 'Turkey', 'Color', 'House', 'River'],
          maxScore: 15,
          timeLimit: 120
        },
        {
          id: 'delayed_recall',
          name: 'Delayed Word Recall',
          type: 'delayed_memory',
          instruction: 'Now tell me all the words from the list you can remember.',
          maxScore: 15,
          timeLimit: 120
        }
      ]
    },
    'quick-screen': {
      name: t('tests.quick_cognitive_screening'),
      tests: [
        {
          id: 'quick_mmse',
          name: 'Quick MMSE Screening',
          type: 'questions',
          instruction: 'Quick cognitive screening questions.',
          questions: [
            'What year is it?',
            'What month is it?',
            'What day of the week is it?',
            'What country are we in?',
            'What city are we in?'
          ],
          maxScore: 5,
          timeLimit: 120
        }
      ]
    }
  }

  const currentTestDefinition = testDefinitions[testConfig.id]
  const currentTest = currentTestDefinition?.tests[currentTestIndex]
  const totalTests = currentTestDefinition?.tests.length || 1

  useEffect(() => {
    let interval
    if (testState === 'active' && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => {
          if (time <= 1) {
            handleTimeUp()
            return 0
          }
          return time - 1
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [testState, timeRemaining])

  const handleTimeUp = () => {
    if (isRecording) {
      stopRecording()
    } else {
      submitResponse()
    }
  }

  const startTest = () => {
    if (!currentTest) return
    
    setTestState('active')
    setTimeRemaining(currentTest.timeLimit)
    setCurrentResponse('')
    
    // Start recording for speech-based tests
    if (['memory', 'memory_list', 'delayed_memory', 'digit_sequence'].includes(currentTest.type)) {
      setTimeout(() => startRecording(), 2000)
    }
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true
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
        handleAudioResponse(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)

    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Microphone access required for this test. Please allow microphone access and try again.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
    }
    setIsRecording(false)
  }

  const handleAudioResponse = async (audioBlob) => {
    // Simulate analysis - in real implementation, this would call the backend
    const mockAnalysis = {
      transcription: 'User response recorded',
      score: Math.floor(Math.random() * currentTest.maxScore + 1),
      maxScore: currentTest.maxScore
    }
    
    setResponses(prev => ({
      ...prev,
      [currentTest.id]: mockAnalysis
    }))
    
    setScore(prevScore => prevScore + mockAnalysis.score)
    setMaxScore(prevMax => prevMax + mockAnalysis.maxScore)
    
    setTestState('completed')
  }

  const submitResponse = () => {
    if (!currentTest) return
    
    // Simple scoring for text responses
    const responseScore = currentResponse.trim() ? Math.ceil(currentTest.maxScore * 0.8) : 0
    
    setResponses(prev => ({
      ...prev,
      [currentTest.id]: {
        response: currentResponse,
        score: responseScore,
        maxScore: currentTest.maxScore
      }
    }))
    
    setScore(prevScore => prevScore + responseScore)
    setMaxScore(prevMax => prevMax + currentTest.maxScore)
    
    setTestState('completed')
  }

  const nextTest = () => {
    if (currentTestIndex < totalTests - 1) {
      setCurrentTestIndex(prev => prev + 1)
      setTestState('instruction')
      setCurrentResponse('')
    } else {
      completeAllTests()
    }
  }

  const completeAllTests = async () => {
    try {
      // Submit results to backend
      const finalResults = {
        session_id: session.id,
        test_type: testConfig.id,
        total_score: score,
        max_score: maxScore,
        completion_rate: (score / maxScore) * 100,
        responses: responses,
        risk_level: score / maxScore > 0.7 ? 'low' : score / maxScore > 0.5 ? 'moderate' : 'high'
      }
      
      // In real implementation, call API to save results
      console.log('Test completed:', finalResults)
      
      onComplete(finalResults)
    } catch (error) {
      console.error('Error completing test:', error)
      onComplete({ error: 'Failed to save test results' })
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
          <p className="text-gray-600 mb-8">The selected test is not properly configured.</p>
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
            <p className="text-sm text-indigo-600 mt-1">
              Score: {score}/{maxScore}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {timeRemaining > 0 && testState === 'active' && (
              <div className="flex items-center gap-2 px-3 py-2 bg-blue-100 rounded-lg">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-blue-800">
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
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
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
            <Brain className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {currentTest.name}
            </h2>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 text-left">
              <h3 className="font-semibold text-blue-900 mb-3">Instructions</h3>
              <p className="text-blue-800 leading-relaxed mb-4">
                {currentTest.instruction}
              </p>
              
              {/* Show test-specific content */}
              {currentTest.type === 'questions' && (
                <div className="mt-4">
                  <p className="font-medium mb-2">Questions ({currentTest.questions.length}):</p>
                  <ol className="list-decimal list-inside space-y-1 text-sm">
                    {currentTest.questions.map((question, idx) => (
                      <li key={idx}>{question}</li>
                    ))}
                  </ol>
                </div>
              )}
              
              {currentTest.type === 'memory' && currentTest.words && (
                <div className="mt-4 p-4 bg-white rounded border">
                  <p className="font-medium mb-2">Remember these words:</p>
                  <div className="flex gap-3 justify-center">
                    {currentTest.words.map((word, idx) => (
                      <span key={idx} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded font-semibold">
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {currentTest.type === 'memory_list' && currentTest.wordList && (
                <div className="mt-4 p-4 bg-white rounded border">
                  <p className="font-medium mb-2">Word List ({currentTest.wordList.length} words):</p>
                  <div className="grid grid-cols-3 gap-2 text-sm">
                    {currentTest.wordList.map((word, idx) => (
                      <span key={idx} className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-center">
                        {word}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center gap-4 text-sm text-blue-700 mt-4">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Time Limit: {formatTime(currentTest.timeLimit)}
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4" />
                  Max Score: {currentTest.maxScore} points
                </div>
              </div>
            </div>

            <button
              onClick={startTest}
              className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
            >
              Begin Test
            </button>
          </div>
        )}

        {/* Active Test State */}
        {testState === 'active' && (
          <div className="text-center">
            <div className="mb-8">
              {isRecording ? (
                <div className="relative inline-block">
                  <Mic className="w-24 h-24 mx-auto mb-4 text-red-600" />
                  <div className="absolute -inset-2 bg-red-200 rounded-full animate-ping opacity-75" />
                </div>
              ) : (
                <Brain className="w-24 h-24 mx-auto mb-4 text-blue-600" />
              )}
              
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {isRecording ? 'Recording Your Response' : currentTest.name}
              </h2>
              
              <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                <p className="text-green-800 text-lg mb-4">
                  {currentTest.instruction}
                </p>
                
                {!isRecording && ['questions', 'delayed_memory'].includes(currentTest.type) && (
                  <div>
                    <textarea
                      value={currentResponse}
                      onChange={(e) => setCurrentResponse(e.target.value)}
                      placeholder="Type your answer here..."
                      className="w-full p-4 border border-gray-300 rounded-lg resize-none h-32 mb-4"
                    />
                    <button
                      onClick={submitResponse}
                      className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                    >
                      Submit Response
                    </button>
                  </div>
                )}
                
                {isRecording && (
                  <button
                    onClick={stopRecording}
                    className="bg-red-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-red-700 transition-colors flex items-center gap-2 mx-auto"
                  >
                    <Square className="w-5 h-5" />
                    Stop Recording
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Completed State */}
        {testState === 'completed' && (
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Test Complete
            </h2>
            
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-indigo-600">
                    {responses[currentTest.id]?.score || 0}/{currentTest.maxScore}
                  </p>
                  <p className="text-sm text-gray-600">Score</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-purple-600">
                    {Math.round(((responses[currentTest.id]?.score || 0) / currentTest.maxScore) * 100)}%
                  </p>
                  <p className="text-sm text-gray-600">Accuracy</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-green-600">
                    {currentTestIndex + 1}/{totalTests}
                  </p>
                  <p className="text-sm text-gray-600">Progress</p>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              {currentTestIndex < totalTests - 1 ? (
                <button
                  onClick={nextTest}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2"
                >
                  Next Test
                  <ArrowRight className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={completeAllTests}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Complete Assessment
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CognitiveTestInterface