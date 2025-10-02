import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { testSessionAPI, progressAPI, reportAPI } from '../lib/api'
import { 
  Brain, 
  Calendar, 
  TrendingUp, 
  FileText, 
  Play, 
  Clock,
  Activity,
  BarChart3,
  Users,
  AlertCircle
} from 'lucide-react'
import Layout from '../components/Layout'

function DashboardPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState({
    recentTests: [],
    progressSummary: null,
    nextAssessment: null,
    reports: []
  })

  const user = JSON.parse(localStorage.getItem('user') || '{}')

  useEffect(() => {
    if (!user.id) {
      navigate('/login')
      return
    }
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load all data concurrently for better performance
      const [sessionsResult, progressResult, reportsResult] = await Promise.allSettled([
        testSessionAPI.getUserSessions(user.id),
        progressAPI.getUserProgress(user.id).catch(() => null),
        reportAPI.getUserReports(user.id).catch(() => null)
      ])
      
      const recentTests = sessionsResult.status === 'fulfilled' ? 
        (sessionsResult.value?.data?.slice(0, 5) || []) : []
      
      const progressSummary = progressResult.status === 'fulfilled' ? 
        progressResult.value?.data : null
      
      const reports = reportsResult.status === 'fulfilled' ? 
        (reportsResult.value?.data?.slice(0, 3) || []) : []

      setDashboardData({
        recentTests,
        progressSummary,
        nextAssessment: null, // Will be calculated from last test
        reports
      })
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
      // Set empty data on error to prevent loading forever
      setDashboardData({
        recentTests: [],
        progressSummary: null,
        nextAssessment: null,
        reports: []
      })
    } finally {
      setLoading(false)
    }
  }

  const startNewTest = async () => {
    try {
      const sessionData = {
        user_id: user.id,
        session_type: 'comprehensive',
        status: 'active'
      }
      
      const response = await testSessionAPI.create(sessionData)
      navigate(`/tests?session_id=${response.data.id}`)
    } catch (error) {
      console.error('Failed to start new test:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const getRiskLevelColor = (riskLevel) => {
    const colors = {
      low: 'text-green-600 bg-green-100',
      mild: 'text-yellow-600 bg-yellow-100',
      moderate: 'text-orange-600 bg-orange-100',
      high: 'text-red-600 bg-red-100',
      severe: 'text-red-800 bg-red-200'
    }
    return colors[riskLevel] || 'text-gray-600 bg-gray-100'
  }

  if (loading) {
    return (
      <Layout>
        <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center">
          <div className="text-center">
            <Brain className="w-12 h-12 text-indigo-600 mx-auto mb-4 animate-pulse" />
            <p className="text-gray-600">{t('common.loading')}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('dashboard.welcome')}, {user.name}!
          </h1>
          <p className="text-gray-600">
            Track your cognitive health journey and stay informed about your progress.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="glass rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Tests</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.recentTests.length}
                </p>
              </div>
              <Brain className="w-8 h-8 text-indigo-600" />
            </div>
          </div>

          <div className="glass rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.recentTests.filter(t => t.status === 'completed').length}
                </p>
              </div>
              <Activity className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="glass rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Reports</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.reports.length}
                </p>
              </div>
              <FileText className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="glass rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {dashboardData.recentTests.length > 0 
                    ? Math.round(dashboardData.recentTests.reduce((acc, test) => acc + (test.overall_score || 0), 0) / dashboardData.recentTests.length)
                    : '-'
                  }
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Quick Actions */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">{t('dashboard.quick_actions')}</h2>
            
            <div className="space-y-4">
              <button
                onClick={startNewTest}
                className="w-full bg-indigo-600 text-white p-4 rounded-xl font-semibold hover:bg-indigo-700 transition-all flex items-center gap-3"
                data-testid="start-new-test-btn"
              >
                <Play className="w-5 h-5" />
                {t('dashboard.start_new_test')}
              </button>

              <button
                onClick={() => navigate('/reports')}
                className="w-full bg-purple-600 text-white p-4 rounded-xl font-semibold hover:bg-purple-700 transition-all flex items-center gap-3"
                data-testid="view-reports-btn"
              >
                <FileText className="w-5 h-5" />
                {t('dashboard.view_reports')}
              </button>

              <button
                onClick={() => navigate('/profile')}
                className="w-full bg-gray-600 text-white p-4 rounded-xl font-semibold hover:bg-gray-700 transition-all flex items-center gap-3"
                data-testid="update-profile-btn"
              >
                <Users className="w-5 h-5" />
                {t('dashboard.update_profile')}
              </button>
            </div>
          </div>

          {/* Recent Tests */}
          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">{t('dashboard.recent_tests')}</h2>
            
            {dashboardData.recentTests.length === 0 ? (
              <div className="text-center py-8">
                <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">{t('dashboard.no_tests')}</p>
                <button
                  onClick={startNewTest}
                  className="text-indigo-600 font-semibold hover:underline"
                >
                  {t('dashboard.schedule_first_test')}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {dashboardData.recentTests.map((test) => (
                  <div key={test.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">
                        {test.session_type} Assessment
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(test.overall_risk_level)}`}>
                        {test.overall_risk_level || 'Pending'}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {formatDate(test.started_at)}
                      </div>
                      
                      {test.overall_score && (
                        <div className="flex items-center gap-1">
                          <BarChart3 className="w-4 h-4" />
                          Score: {Math.round(test.overall_score)}
                        </div>
                      )}
                      
                      <span className={`px-2 py-1 rounded text-xs ${
                        test.status === 'completed' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'
                      }`}>
                        {test.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Progress Summary */}
        {dashboardData.progressSummary && (
          <div className="mt-8 glass rounded-2xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">{t('dashboard.progress_summary')}</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600 mb-2">
                  {dashboardData.progressSummary.trend || 'Stable'}
                </div>
                <p className="text-sm text-gray-600">Overall Trend</p>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-2">
                  {dashboardData.progressSummary.improvement || '+2%'}
                </div>
                <p className="text-sm text-gray-600">Improvement</p>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-2">
                  {dashboardData.recentTests.filter(t => t.status === 'completed').length}
                </div>
                <p className="text-sm text-gray-600">Tests Completed</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default DashboardPage