import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { reportAPI, testSessionAPI } from '../lib/api'
import { 
  FileText, 
  Download, 
  Calendar, 
  BarChart3, 
  TrendingUp, 
  AlertCircle,
  CheckCircle,
  Eye,
  Plus,
  Filter,
  Search
} from 'lucide-react'
import Layout from '../components/Layout'

function ReportsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()
  
  const [reports, setReports] = useState([])
  const [sessions, setSessions] = useState([])
  const [selectedReport, setSelectedReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // Get session_id from URL params if viewing specific report
  const urlParams = new URLSearchParams(location.search)
  const sessionId = urlParams.get('session_id')

  useEffect(() => {
    if (!user.id) {
      navigate('/login')
      return
    }
    
    loadData()
  }, [sessionId])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Load user reports
      const reportsResponse = await reportAPI.getUserReports(user.id)
      setReports(reportsResponse.data || [])
      
      // Load completed sessions for report generation
      const sessionsResponse = await testSessionAPI.getUserSessions(user.id)
      const completedSessions = sessionsResponse.data.filter(s => s.status === 'completed') || []
      setSessions(completedSessions)
      
      // If specific session requested, generate report if not exists
      if (sessionId) {
        const existingReport = reportsResponse.data.find(r => r.session_id === sessionId)
        if (existingReport) {
          setSelectedReport(existingReport)
        } else {
          // Generate report for this session
          await generateReport(sessionId, 'comprehensive')
        }
      }
      
    } catch (error) {
      console.error('Failed to load reports:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async (sessionId, reportType = 'comprehensive') => {
    try {
      setGenerating(true)
      
      const response = await reportAPI.generate(sessionId, reportType)
      
      // Reload reports to include the new one
      const reportsResponse = await reportAPI.getUserReports(user.id)
      setReports(reportsResponse.data || [])
      
      // Set as selected report
      const newReport = reportsResponse.data.find(r => r.session_id === sessionId)
      if (newReport) {
        setSelectedReport(newReport)
      }
      
    } catch (error) {
      console.error('Failed to generate report:', error)
    } finally {
      setGenerating(false)
    }
  }

  const downloadReport = async (reportId) => {
    try {
      const response = await reportAPI.download(reportId)
      
      // Create blob and download
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `cognitive-report-${reportId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
    } catch (error) {
      console.error('Failed to download report:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getRiskLevelColor = (riskLevel) => {
    const colors = {
      low: 'text-green-600 bg-green-100 border-green-200',
      mild: 'text-yellow-600 bg-yellow-100 border-yellow-200',
      moderate: 'text-orange-600 bg-orange-100 border-orange-200',
      high: 'text-red-600 bg-red-100 border-red-200',
      severe: 'text-red-800 bg-red-200 border-red-300'
    }
    return colors[riskLevel] || 'text-gray-600 bg-gray-100 border-gray-200'
  }

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.report_type?.toLowerCase().includes(searchTerm.toLowerCase())
    
    if (filter === 'all') return matchesSearch
    return matchesSearch && report.report_type === filter
  })

  if (loading) {
    return (
      <Layout>
        <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center">
          <div className="text-center">
            <FileText className="w-12 h-12 text-indigo-600 mx-auto mb-4 animate-pulse" />
            <p className="text-gray-600">{t('common.loading')}</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {t('reports.my_reports')}
          </h1>
          <p className="text-gray-600">
            View and download detailed reports of your cognitive assessments.
          </p>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search reports..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent w-full"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                data-testid="search-reports"
              />
            </div>
          </div>
          
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            data-testid="filter-reports"
          >
            <option value="all">All Report Types</option>
            <option value="comprehensive">Comprehensive</option>
            <option value="summary">Summary</option>
            <option value="progress">Progress</option>
          </select>
        </div>

        {/* Generate New Report */}
        {sessions.length > 0 && (
          <div className="glass rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Generate New Report</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sessions.slice(0, 6).map((session) => {
                const hasReport = reports.some(r => r.session_id === session.id)
                return (
                  <div key={session.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 truncate">
                        {session.session_type} Assessment
                      </h3>
                      {hasReport && (
                        <CheckCircle className="w-4 h-4 text-green-600" />
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">
                      {formatDate(session.completed_at)}
                    </p>
                    
                    <button
                      onClick={() => generateReport(session.id)}
                      disabled={generating || hasReport}
                      className={`w-full px-3 py-2 rounded font-medium text-sm transition-colors ${
                        hasReport 
                          ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      }`}
                      data-testid={`generate-report-${session.id}`}
                    >
                      {generating ? 'Generating...' : hasReport ? 'Report Exists' : 'Generate Report'}
                    </button>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Reports List */}
        {filteredReports.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-600 mb-6">
              {reports.length === 0 
                ? "You haven't generated any reports yet. Complete a test to generate your first report."
                : "No reports match your current search criteria."
              }
            </p>
            {reports.length === 0 && (
              <button
                onClick={() => navigate('/tests')}
                className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
              >
                Take Your First Test
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {filteredReports.map((report) => (
              <div key={report.id} className="glass rounded-xl p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <FileText className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {report.report_type} Report
                      </h3>
                      <p className="text-sm text-gray-600">
                        {formatDate(report.created_at)}
                      </p>
                    </div>
                  </div>
                  
                  <span className="px-2 py-1 bg-green-100 text-green-600 text-xs font-medium rounded">
                    Ready
                  </span>
                </div>

                {report.summary && (
                  <p className="text-sm text-gray-700 mb-4 line-clamp-3">
                    {report.summary}
                  </p>
                )}

                <div className="flex items-center gap-2 mb-4">
                  <button
                    onClick={() => setSelectedReport(report)}
                    className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
                    data-testid={`view-report-${report.id}`}
                  >
                    <Eye className="w-4 h-4" />
                    View
                  </button>
                  
                  <button
                    onClick={() => downloadReport(report.id)}
                    className="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                    data-testid={`download-report-${report.id}`}
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Report Viewer Modal */}
        {selectedReport && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
            <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 capitalize">
                    {selectedReport.report_type} Report
                  </h2>
                  <p className="text-gray-600">
                    Generated on {formatDate(selectedReport.created_at)}
                  </p>
                </div>
                
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => downloadReport(selectedReport.id)}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Download
                  </button>
                  
                  <button
                    onClick={() => setSelectedReport(null)}
                    className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-400 transition-colors"
                    data-testid="close-report-modal"
                  >
                    Close
                  </button>
                </div>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-100px)]">
                {selectedReport.summary && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Executive Summary</h3>
                    <p className="text-gray-700 leading-relaxed">{selectedReport.summary}</p>
                  </div>
                )}
                
                {selectedReport.recommendations && (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">Recommendations</h3>
                    <div className="prose prose-sm">
                      <div dangerouslySetInnerHTML={{ __html: selectedReport.recommendations.replace(/\n/g, '<br>') }} />
                    </div>
                  </div>
                )}
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Report Information</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-gray-600">Report ID:</span>
                      <span className="text-gray-900 ml-2">{selectedReport.id}</span>
                    </div>
                    <div>
                      <span className="font-medium text-gray-600">Session ID:</span>
                      <span className="text-gray-900 ml-2">{selectedReport.session_id}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default ReportsPage