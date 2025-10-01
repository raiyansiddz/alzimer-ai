import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { 
  Brain, 
  Clock, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Play,
  Pause,
  RotateCcw,
  AlertCircle
} from 'lucide-react'

function CognitiveTestInterface({ session, testConfig, onComplete, onExit }) {
  const { t } = useTranslation()
  const [currentTestIndex, setCurrentTestIndex] = useState(0)
  const [currentTest, setCurrentTest] = useState(null)
  const [testState, setTestState] = useState('instruction')
  const [responses, setResponses] = useState({})
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [isActive, setIsActive] = useState(false)

  const testDefinitions = {
    mmse: {
      name: 'Mini-Mental State Examination',
      sections: [
        {
          id: 'orientation_time',
          name: 'Orientation to Time',
          questions: [
            'What year is it?',
            'What season is it?',
            'What month is it?',
            'What is today\'s date?',
            'What day of the week is it?'
          ],
          maxScore: 5,
          timeLimit: 300
        },
        {
          id: 'orientation_place',
          name: 'Orientation to Place',
          questions: [
            'What country are we in?',
            'What state/province are we in?',
            'What city are we in?',
            'What building are we in?',
            'What floor are we on?'
          ],
          maxScore: 5,
          timeLimit: 300
        },
        {
          id: 'registration',
          name: 'Registration',
          instruction: 'I am going to name three objects. Please repeat them back to me.',
          words: ['Apple', 'Penny', 'Table'],
          maxScore: 3,
          timeLimit: 60
        },
        {
          id: 'attention',
          name: 'Attention and Calculation',
          instruction: 'Please count backwards from 100 by 7s. Stop after 5 numbers.',
          expected: ['93', '86', '79', '72', '65'],
          maxScore: 5,
          timeLimit: 300
        }
      ]
    },
    avlt: {
      name: 'Auditory Verbal Learning Test',
      sections: [
        {
          id: 'trial_1',
          name: 'Trial 1 - First Presentation',
          wordList: ['Drum', 'Curtain', 'Bell', 'Coffee', 'School', 'Parent', 'Moon', 'Garden', 'Hat', 'Farmer', 'Nose', 'Turkey', 'Color', 'House', 'River'],
          instruction: 'I will read a list of 15 words. Listen carefully and then tell me all the words you remember.',
          maxScore: 15,
          timeLimit: 120
        }
      ]
    },
    digit_span: {
      name: 'Digit Span Test',
      sections: [
        {
          id: 'forward',
          name: 'Digits Forward',
          sequences: [
            { digits: '2-1-9', level: 3 },
            { digits: '4-2-7-3', level: 4 },
            { digits: '1-5-2-8-6', level: 5 },
            { digits: '6-1-9-4-7-3', level: 6 },
            { digits: '4-2-7-3-1-5-8', level: 7 }
          ],
          instruction: 'I will say some numbers. Repeat them back in the same order.',
          maxScore: 5,
          timeLimit: 60
        },
        {
          id: 'backward',
          name: 'Digits Backward',
          sequences: [
            { digits: '3-8-4', level: 3 },
            { digits: '6-2-9-7', level: 4 },
            { digits: '4-1-5-9-3', level: 5 },
            { digits: '6-1-8-4-3-7', level: 6 },
            { digits: '5-3-9-4-1-8-2', level: 7 }
          ],
          instruction: 'I will say some numbers. Repeat them back in reverse order.',
          maxScore: 5,
          timeLimit: 60
        }
      ]
    }
  }

  useEffect(() => {
    if (testConfig && testConfig.tests.length > 0) {
      const testType = testConfig.tests[currentTestIndex]
      setCurrentTest(testDefinitions[testType])
    }
  }, [currentTestIndex, testConfig])

  useEffect(() => {
    let interval = null
    if (isActive && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(time => time - 1)
      }, 1000)
    } else if (timeRemaining === 0 && isActive) {
      handleTimeUp()
    }
    return () => clearInterval(interval)
  }, [isActive, timeRemaining])

  const handleTimeUp = () => {
    setIsActive(false)
    // Auto-submit current section
    if (testState === 'testing') {
      setTestState('review')
    }
  }

  const startTest = () => {
    setTestState('testing')
    const section = currentTest.sections[0]
    setTimeRemaining(section.timeLimit)
    setIsActive(true)
  }

  const handleResponse = (sectionId, response) => {
    setResponses(prev => ({
      ...prev,
      [`${currentTest.name}_${sectionId}`]: response
    }))
  }

  const nextTest = () => {
    if (currentTestIndex < testConfig.tests.length - 1) {
      setCurrentTestIndex(currentTestIndex + 1)
      setTestState('instruction')
      setIsActive(false)
      setTimeRemaining(0)
    } else {
      // All tests completed
      onComplete()
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (!currentTest) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Brain className="w-12 h-12 text-indigo-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600">Loading test...</p>
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
            <h1 className="text-2xl font-bold text-gray-900">{currentTest.name}</h1>
            <p className="text-gray-600">
              Test {currentTestIndex + 1} of {testConfig.tests.length}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {timeRemaining > 0 && (
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
              data-testid="exit-test-btn"
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
              {Math.round(((currentTestIndex + (testState === 'completed' ? 1 : 0)) / testConfig.tests.length) * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${((currentTestIndex + (testState === 'completed' ? 1 : 0)) / testConfig.tests.length) * 100}%` 
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
            <div className="mb-8">
              <Brain className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {currentTest.name}
              </h2>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6 text-left">
                <h3 className="font-semibold text-blue-900 mb-3">Test Instructions:</h3>
                <ul className="space-y-2 text-blue-800">
                  {currentTest.sections.map((section, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
                      <span>{section.instruction || `Complete ${section.name}`}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={startTest}
                className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2"
                data-testid="start-test-btn"
              >
                <Play className="w-5 h-5" />
                Start Test
              </button>
            </div>
          </div>
        )}

        {/* Testing State */}
        {testState === 'testing' && (
          <div>
            <MMSETestComponent 
              test={currentTest}
              onResponse={handleResponse}
              onComplete={() => setTestState('review')}
              timeRemaining={timeRemaining}
            />
          </div>
        )}

        {/* Review State */}
        {testState === 'review' && (
          <div className="text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              {currentTest.name} Completed
            </h2>
            
            <p className="text-gray-600 mb-8">
              You have successfully completed this test section.
            </p>

            <div className="flex justify-center gap-4">
              {currentTestIndex < testConfig.tests.length - 1 ? (
                <button
                  onClick={nextTest}
                  className="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  data-testid="next-test-btn"
                >
                  Next Test
                  <ArrowRight className="w-5 h-5" />
                </button>
              ) : (
                <button
                  onClick={onComplete}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center gap-2"
                  data-testid="complete-all-tests-btn"
                >
                  Complete Assessment
                  <CheckCircle className="w-5 h-5" />
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// MMSE Test Component
function MMSETestComponent({ test, onResponse, onComplete, timeRemaining }) {
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0)
  const [sectionResponses, setSectionResponses] = useState({})
  
  const currentSection = test.sections[currentSectionIndex]

  const handleSectionResponse = (response) => {
    const updatedResponses = {
      ...sectionResponses,
      [currentSection.id]: response
    }
    setSectionResponses(updatedResponses)
    onResponse(currentSection.id, response)
  }

  const nextSection = () => {
    if (currentSectionIndex < test.sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1)
    } else {
      onComplete()
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          {currentSection.name}
        </h3>
        <p className="text-gray-600">
          Section {currentSectionIndex + 1} of {test.sections.length}
        </p>
      </div>

      {currentSection.instruction && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-blue-800 font-medium">{currentSection.instruction}</p>
        </div>
      )}

      {/* Orientation Questions */}
      {(currentSection.id === 'orientation_time' || currentSection.id === 'orientation_place') && (
        <div className="space-y-4">
          {currentSection.questions.map((question, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <label className="block text-gray-900 font-medium mb-2">
                {index + 1}. {question}
              </label>
              <input
                type="text"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter your answer..."
                onChange={(e) => {
                  const responses = sectionResponses[currentSection.id] || []
                  responses[index] = e.target.value
                  handleSectionResponse([...responses])
                }}
                data-testid={`question-${index}`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Registration */}
      {currentSection.id === 'registration' && (
        <div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mb-6 text-center">
            <p className="text-lg font-medium text-gray-900 mb-4">
              Remember these words:
            </p>
            <div className="flex justify-center gap-4">
              {currentSection.words.map((word, index) => (
                <span key={index} className="px-4 py-2 bg-indigo-100 text-indigo-800 rounded-lg font-semibold">
                  {word}
                </span>
              ))}
            </div>
          </div>
          
          <div className="space-y-3">
            <label className="block text-gray-900 font-medium">
              Now repeat the three words back to me:
            </label>
            {[0, 1, 2].map((index) => (
              <input
                key={index}
                type="text"
                placeholder={`Word ${index + 1}...`}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                onChange={(e) => {
                  const responses = sectionResponses[currentSection.id] || []
                  responses[index] = e.target.value
                  handleSectionResponse([...responses])
                }}
                data-testid={`recall-word-${index}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Attention/Calculation */}
      {currentSection.id === 'attention' && (
        <div className="space-y-4">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800 font-medium">
              Count backwards from 100 by 7s. Enter each number:
            </p>
          </div>
          
          {[0, 1, 2, 3, 4].map((index) => (
            <div key={index} className="flex items-center gap-4">
              <span className="text-gray-700 font-medium min-w-[100px]">
                {index === 0 ? '100 - 7 =' : `Answer ${index} - 7 =`}
              </span>
              <input
                type="number"
                className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Enter number..."
                onChange={(e) => {
                  const responses = sectionResponses[currentSection.id] || []
                  responses[index] = e.target.value
                  handleSectionResponse([...responses])
                }}
                data-testid={`calculation-${index}`}
              />
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-between mt-8">
        <button
          onClick={() => setCurrentSectionIndex(Math.max(0, currentSectionIndex - 1))}
          disabled={currentSectionIndex === 0}
          className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Previous
        </button>
        
        <button
          onClick={nextSection}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2"
          data-testid="next-section-btn"
        >
          {currentSectionIndex === test.sections.length - 1 ? 'Complete' : 'Next'}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

export default CognitiveTestInterface