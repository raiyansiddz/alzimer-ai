import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { testSessionAPI } from '../lib/api'
import { 
  Brain, 
  Mic, 
  Activity, 
  Clock, 
  Play, 
  CheckCircle,
  AlertCircle,
  ChevronRight
} from 'lucide-react'
import Layout from '../components/Layout'
import CognitiveTestInterface from '../components/CognitiveTestInterface'
import SpeechTestInterface from '../components/SpeechTestInterface'
import AccessibleTestSelector from '../components/AccessibleTestSelector'
import AudioMMSE from '../components/AudioMMSE'

function TestsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  
  const [activeTab, setActiveTab] = useState('available')
  const [selectedTest, setSelectedTest] = useState(null)
  const [currentSession, setCurrentSession] = useState(null)
  const [userSessions, setUserSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [showPersonalizedTests, setShowPersonalizedTests] = useState(false)
  const [selectedTestSuite, setSelectedTestSuite] = useState(null)

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  // Fallback user for demo purposes if not logged in
  const demoUser = {
    id: '09c1eaca-93d7-4498-a10b-4adcb8e62dc0',
    email: 'test@demo.com',
    name: 'Test User',
    age: 45,
    education_level: 'graduate',
    vision_type: 'normal',
    language: 'en'
  }
  
  const activeUser = user.id ? user : demoUser
  
  // Create user profile for AccessibleTestSelector
  const userProfile = {
    vision_status: activeUser.vision_type || 'normal',
    education_level: activeUser.education_level || 'graduate',
    language: activeUser.language || 'en',
    age: activeUser.age
  }

  // Get session_id from URL params if continuing a test
  const urlParams = new URLSearchParams(location.search)
  const sessionId = urlParams.get('session_id')

  useEffect(() => {
    if (!user.id) {
      navigate('/login')
      return
    }
    
    loadUserSessions()
    
    if (sessionId) {
      loadCurrentSession(sessionId)
    }
  }, [sessionId])

  const loadUserSessions = async () => {
    try {
      const response = await testSessionAPI.getUserSessions(activeUser.id)
      setUserSessions(response.data || [])
    } catch (error) {
      console.error('Failed to load user sessions:', error)
    }
  }

  const loadCurrentSession = async (id) => {
    try {
      const response = await testSessionAPI.get(id)
      setCurrentSession(response.data)
    } catch (error) {
      console.error('Failed to load current session:', error)
    }
  }

  const availableTests = [
    {
      id: 'cognitive-battery',
      name: t('tests.comprehensive_cognitive_battery') || 'Comprehensive Cognitive Battery',
      type: 'cognitive',
      description: 'Complete cognitive assessment including memory, attention, and executive function tests',
      duration: 45,
      tests: ['mmse', 'moca', 'avlt', 'digit_span', 'verbal_fluency'],
      icon: Brain,
      color: 'indigo'
    },
    {
      id: 'memory-focus', 
      name: t('tests.memory_assessment') || 'Memory Assessment',
      type: 'cognitive',
      description: 'Focused evaluation of memory functions including learning and recall',
      duration: 20,
      tests: ['avlt', 'digit_span'],
      icon: Brain,
      color: 'purple'
    },
    {
      id: 'speech-analysis',
      name: t('tests.speech_language_assessment') || 'Speech & Language Assessment',
      type: 'speech',
      description: 'Comprehensive analysis of speech patterns, fluency, and language abilities',
      duration: 15,
      tests: ['fluency', 'description', 'conversation'],
      icon: Mic,
      color: 'green'
    },
    {
      id: 'quick-screen',
      name: t('tests.quick_cognitive_screening') || 'Quick Cognitive Screening',
      type: 'cognitive',
      description: 'Brief screening test for initial cognitive assessment',
      duration: 10,
      tests: ['mmse'],
      icon: Clock,
      color: 'blue'
    }
  ]

  const startTest = async (testConfig) => {
    try {
      setLoading(true)
      
      const sessionData = {
        user_id: activeUser.id,
        session_type: 'baseline', // Use valid session type
        notes: `Starting ${testConfig.name}`
      }
      
      const response = await testSessionAPI.create(sessionData)
      setCurrentSession(response.data)
      setSelectedTest(testConfig)
      
      // Update URL
      navigate(`/tests?session_id=${response.data.id}`)
      
    } catch (error) {
      console.error('Failed to start test:', error)
      alert(`Failed to start test: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const continueTest = async (session) => {
    try {
      setCurrentSession(session)
      const testConfig = availableTests.find(t => t.id === session.session_type)
      setSelectedTest(testConfig)
      navigate(`/tests?session_id=${session.id}`)
    } catch (error) {
      console.error('Failed to continue test:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status) => {
    const colors = {
      active: 'text-blue-600 bg-blue-100',
      completed: 'text-green-600 bg-green-100',
      paused: 'text-yellow-600 bg-yellow-100',
      cancelled: 'text-red-600 bg-red-100'
    }
    return colors[status] || 'text-gray-600 bg-gray-100'
  }

  const getButtonColors = (color) => {
    const colorMap = {
      indigo: 'bg-indigo-600 hover:bg-indigo-700',
      purple: 'bg-purple-600 hover:bg-purple-700',
      green: 'bg-green-600 hover:bg-green-700',
      blue: 'bg-blue-600 hover:bg-blue-700'
    }
    return colorMap[color] || 'bg-indigo-600 hover:bg-indigo-700'
  }

  const getIconColors = (color) => {
    const colorMap = {
      indigo: { bg: 'bg-indigo-100', text: 'text-indigo-600' },
      purple: { bg: 'bg-purple-100', text: 'text-purple-600' },
      green: { bg: 'bg-green-100', text: 'text-green-600' },
      blue: { bg: 'bg-blue-100', text: 'text-blue-600' }
    }
    return colorMap[color] || { bg: 'bg-indigo-100', text: 'text-indigo-600' }
  }

  // If in active test session, show the appropriate test interface
  if (currentSession && selectedTest) {
    // Handle personalized test suites
    if (selectedTestSuite && selectedTestSuite.id === 'blind_audio_suite') {
      // Check which test from the suite to show
      const currentTestId = selectedTest.id || selectedTestSuite.tests[0].id
      
      if (currentTestId === 'audio_mmse') {
        return (
          <Layout>
            <AudioMMSE 
              session={currentSession}
              onComplete={() => {
                setCurrentSession(null)
                setSelectedTest(null)
                setSelectedTestSuite(null)
                navigate('/tests')
                loadUserSessions()
              }}
              onExit={() => {
                setCurrentSession(null)
                setSelectedTest(null)
                setSelectedTestSuite(null)
                navigate('/tests')
              }}
            />
          </Layout>
        )
      }
    }
    
    // Standard test interfaces
    if (selectedTest.type === 'cognitive') {
      return (
        <Layout>
          <CognitiveTestInterface 
            session={currentSession}
            testConfig={selectedTest}
            onComplete={() => {
              setCurrentSession(null)
              setSelectedTest(null)
              setSelectedTestSuite(null)
              navigate('/tests')
              loadUserSessions()
            }}
            onExit={() => {
              setCurrentSession(null)
              setSelectedTest(null)
              setSelectedTestSuite(null)
              navigate('/tests')
            }}
          />
        </Layout>
      )
    } else if (selectedTest.type === 'speech') {
      return (
        <Layout>
          <SpeechTestInterface 
            session={currentSession}
            testConfig={selectedTest}
            onComplete={() => {
              setCurrentSession(null)
              setSelectedTest(null)
              setSelectedTestSuite(null)
              navigate('/tests')
              loadUserSessions()
            }}
            onExit={() => {
              setCurrentSession(null)
              setSelectedTest(null)
              setSelectedTestSuite(null)
              navigate('/tests')
            }}
          />
        </Layout>
      )
    }
  }

  // Show personalized test selector
  if (showPersonalizedTests) {
    return (
      <Layout>
        <AccessibleTestSelector 
          userProfile={userProfile}
          onTestSuiteSelected={(suite) => {
            setSelectedTestSuite(suite)
            // Start the first test in the suite
            const firstTest = {
              id: suite.tests[0].id,
              name: suite.tests[0].name,
              type: 'cognitive', // Most personalized tests are cognitive
              suite: suite
            }
            startTest(firstTest)
          }}
        />
        <div className="mt-6 text-center">
          <button
            onClick={() => setShowPersonalizedTests(false)}
            className="bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-700 transition-colors"
          >
            Back to Standard Tests
          </button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('tests.available_tests')}
          </h1>
          <p className="text-gray-600">
            Choose from our comprehensive cognitive assessment tests to monitor your brain health.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 mb-8">
          <button
            onClick={() => setActiveTab('available')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'available'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            data-testid="available-tests-tab"
          >
            {t('tests.available_tests')}
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'history'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            data-testid="test-history-tab"
          >
            {t('tests.test_history')}
          </button>
        </div>

        {/* Available Tests */}
        {activeTab === 'available' && (
          <>
            {/* Personalized Assessment Section */}
            <div className="mb-8 p-6 bg-gradient-to-r from-purple-100 to-indigo-100 rounded-xl border border-purple-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-3">🎯 Personalized Assessment</h2>
              <p className="text-gray-700 mb-4">
                Get a customized test battery based on your vision status ({userProfile.vision_status}), 
                education level ({userProfile.education_level}), and language preference.
              </p>
              <div className="flex items-center justify-between">
                <div className="text-sm text-purple-700">
                  ✓ Clinically validated tests adapted for your needs<br/>
                  ✓ Evidence-based cognitive assessment<br/>
                  ✓ Accessibility-first design
                </div>
                <button
                  onClick={() => setShowPersonalizedTests(true)}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
                  data-testid="start-personalized-assessment"
                >
                  Start Personalized Assessment
                </button>
              </div>
            </div>

            {/* Standard Tests */}
            <h3 className="text-xl font-bold text-gray-900 mb-4">Standard Test Library</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {availableTests.map((test) => {
              const IconComponent = test.icon
              return (
                <div key={test.id} className="glass rounded-2xl p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`p-3 rounded-lg ${getIconColors(test.color).bg}`}>
                      <IconComponent className={`w-6 h-6 ${getIconColors(test.color).text}`} />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      {test.duration} {t('tests.minutes')}
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">{test.name}</h3>
                  <p className="text-gray-600 mb-4">{test.description}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">
                        {test.tests.length} {test.tests.length === 1 ? 'test' : 'tests'}
                      </span>
                    </div>
                    
                    <button
                      onClick={() => startTest(test)}
                      disabled={loading}
                      className={`${getButtonColors(test.color)} text-white px-6 py-2 rounded-lg font-semibold transition-all disabled:opacity-50 flex items-center gap-2`}
                      data-testid={`start-test-${test.id}`}
                    >
                      <Play className="w-4 h-4" />
                      {loading ? t('common.loading') : t('tests.start_test')}
                    </button>
                  </div>
                </div>
              )
            })}
            </div>
          </>
        )}

        {/* Test History */}
        {activeTab === 'history' && (
          <div className="space-y-4">
            {userSessions.length === 0 ? (
              <div className="text-center py-12">
                <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No tests yet</h3>
                <p className="text-gray-600 mb-6">You haven't completed any cognitive tests yet.</p>
                <button
                  onClick={() => setActiveTab('available')}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Browse Available Tests
                </button>
              </div>
            ) : (
              userSessions.map((session) => (
                <div key={session.id} className="glass rounded-xl p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {availableTests.find(t => t.id === session.session_type)?.name || session.session_type}
                        </h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(session.status)}`}>
                          {session.status}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm text-gray-600">
                        <span>Started: {formatDate(session.started_at)}</span>
                        {session.completed_at && (
                          <span>Completed: {formatDate(session.completed_at)}</span>
                        )}
                        {session.overall_score && (
                          <span className="font-medium">Score: {Math.round(session.overall_score)}</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {session.status === 'active' && (
                        <button
                          onClick={() => continueTest(session)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                          data-testid={`continue-test-${session.id}`}
                        >
                          <Play className="w-4 h-4" />
                          {t('tests.continue_test')}
                        </button>
                      )}
                      
                      {session.status === 'completed' && (
                        <button
                          onClick={() => navigate(`/reports?session_id=${session.id}`)}
                          className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center gap-2"
                          data-testid={`view-report-${session.id}`}
                        >
                          View Report
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default TestsPage