import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';

// Non-Educated User Dashboard - Simple Icons + Voice
const NonEducatedDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [currentActivity, setCurrentActivity] = useState(null);
  const [progress, setProgress] = useState([]);
  const [showingHelp, setShowingHelp] = useState(false);

  useEffect(() => {
    loadProgress();
    speak("Welcome! This is your brain health check. Tap the big green button to start, or tap help for assistance.");
  }, []);

  const speak = (message) => {
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 0.8; // Slower speech
      utterance.pitch = 1.1; // Slightly higher pitch
      window.speechSynthesis.speak(utterance);
    }
  };

  const loadProgress = async () => {
    try {
      const response = await api.get(`/api/progress/user/${user.id}`);
      setProgress(response.data || []);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  const startTest = async () => {
    speak("Starting your brain health check. We'll play some fun games together!");
    
    try {
      const sessionData = {
        user_id: user.id,
        session_type: 'comprehensive_non_educated',
      };
      
      const response = await api.post('/api/test-sessions', sessionData);
      navigate(`/tests/non-educated/simple-memory/${response.data.id}`);
    } catch (error) {
      console.error('Error starting test:', error);
      speak("Oops! Something went wrong. Please try again.");
    }
  };

  const showProgress = () => {
    if (progress.length > 0) {
      const latest = progress[0];
      const score = Math.round(latest.score);
      const message = score >= 80 ? 
        `Great job! Your score is ${score} out of 100. You're doing very well!` :
        score >= 60 ? 
          `Good work! Your score is ${score} out of 100. Keep practicing!` :
          `Your score is ${score} out of 100. Don't worry, we can work together to improve!`;
      speak(message);
    } else {
      speak("You haven't done any brain health checks yet. Tap the big green button to start your first one!");
    }
  };

  const showHelp = () => {
    setShowingHelp(true);
    speak("Here's how to use this app: The big green button starts your brain health check. The blue button shows your results. The yellow button gives you help. Tap anywhere to go back.");
  };

  const hideHelp = () => {
    setShowingHelp(false);
    speak("Welcome back to the main screen.");
  };

  if (showingHelp) {
    return (
      <div 
        className="min-h-screen bg-gradient-to-b from-yellow-200 to-yellow-300 p-4 cursor-pointer"
        onClick={hideHelp}
      >
        <div className="max-w-4xl mx-auto text-center py-12">
          <div className="text-8xl mb-8">❓</div>
          <h1 className="text-6xl font-bold text-gray-900 mb-8">Help</h1>
          
          <div className="bg-white rounded-3xl p-12 shadow-lg mb-8">
            <div className="space-y-8">
              <div className="flex items-center justify-center space-x-6">
                <div className="text-6xl">🟢</div>
                <div className="text-left">
                  <h3 className="text-4xl font-bold mb-2">Green Button</h3>
                  <p className="text-2xl text-gray-700">Starts your brain health check</p>
                </div>
              </div>
              
              <div className="flex items-center justify-center space-x-6">
                <div className="text-6xl">🔵</div>
                <div className="text-left">
                  <h3 className="text-4xl font-bold mb-2">Blue Button</h3>
                  <p className="text-2xl text-gray-700">Shows your test results</p>
                </div>
              </div>
              
              <div className="flex items-center justify-center space-x-6">
                <div className="text-6xl">🟡</div>
                <div className="text-left">
                  <h3 className="text-4xl font-bold mb-2">Yellow Button</h3>
                  <p className="text-2xl text-gray-700">Gives you help and instructions</p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="text-3xl text-gray-800 font-semibold">
            Tap anywhere to go back
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-200 to-purple-200 p-4">
      <div className="max-w-4xl mx-auto text-center py-12">
        {/* Welcome Message */}
        <div className="mb-12">
          <div className="text-8xl mb-4">🧠</div>
          <h1 className="text-6xl font-bold text-gray-900 mb-4">Brain Health Check</h1>
          <p className="text-3xl text-gray-700 font-medium">Welcome, {user.name}!</p>
        </div>

        {/* Main Actions - Large, Colorful Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* Start Test Button */}
          <button
            onClick={startTest}
            onMouseEnter={() => speak("Start your brain health check")}
            className="bg-green-500 hover:bg-green-600 text-white rounded-3xl p-12 shadow-2xl transform hover:scale-105 transition-all duration-200 border-8 border-green-300"
          >
            <div className="text-8xl mb-4">🎯</div>
            <div className="text-4xl font-bold mb-2">START</div>
            <div className="text-2xl">Begin Brain Check</div>
          </button>

          {/* Progress Button */}
          <button
            onClick={showProgress}
            onMouseEnter={() => speak("See your test results")}
            className="bg-blue-500 hover:bg-blue-600 text-white rounded-3xl p-12 shadow-2xl transform hover:scale-105 transition-all duration-200 border-8 border-blue-300"
          >
            <div className="text-8xl mb-4">
              {progress.length > 0 ? 
                (progress[0].score >= 80 ? '⭐' : progress[0].score >= 60 ? '👍' : '💪') 
                : '📊'
              }
            </div>
            <div className="text-4xl font-bold mb-2">RESULTS</div>
            <div className="text-2xl">
              {progress.length > 0 ? `Score: ${Math.round(progress[0].score)}%` : 'No tests yet'}
            </div>
          </button>

          {/* Help Button */}
          <button
            onClick={showHelp}
            onMouseEnter={() => speak("Get help and instructions")}
            className="bg-yellow-500 hover:bg-yellow-600 text-white rounded-3xl p-12 shadow-2xl transform hover:scale-105 transition-all duration-200 border-8 border-yellow-300"
          >
            <div className="text-8xl mb-4">❓</div>
            <div className="text-4xl font-bold mb-2">HELP</div>
            <div className="text-2xl">Get Instructions</div>
          </button>
        </div>

        {/* Encouraging Messages */}
        <div className="bg-white rounded-3xl p-8 shadow-lg">
          <div className="text-6xl mb-4">🌟</div>
          <h2 className="text-4xl font-bold text-gray-900 mb-4">You're Doing Great!</h2>
          <p className="text-2xl text-gray-700 leading-relaxed">
            {progress.length > 0 ? 
              `You've completed ${progress.length} brain health check${progress.length > 1 ? 's' : ''}. Keep up the excellent work!` :
              "Ready for your first brain health check? It's easy and fun!"
            }
          </p>
        </div>

        {/* Audio Feedback Indicator */}
        <div className="mt-8">
          <div className="flex items-center justify-center space-x-4 text-2xl text-gray-700">
            <div className="w-6 h-6 bg-green-400 rounded-full animate-pulse"></div>
            <span>Voice instructions are ON</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Educated User Dashboard - Standard Professional Interface
const EducatedDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [progress, setProgress] = useState([]);
  const [testHistory, setTestHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('3months');
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  useEffect(() => {
    loadData();
  }, [selectedTimeframe]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [progressResponse, historyResponse] = await Promise.all([
        api.get(`/api/progress/user/${user.id}?timeframe=${selectedTimeframe}`),
        api.get(`/api/test-sessions/user/${user.id}?limit=10`)
      ]);
      setProgress(progressResponse.data || []);
      setTestHistory(historyResponse.data || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startComprehensiveAssessment = async () => {
    try {
      const sessionData = {
        user_id: user.id,
        session_type: 'comprehensive_educated',
      };
      
      const response = await api.post('/api/test-sessions', sessionData);
      navigate(`/tests/educated/full-moca/${response.data.id}`);
    } catch (error) {
      console.error('Error starting comprehensive assessment:', error);
    }
  };

  const startSpecificTest = (testType) => {
    navigate(`/tests/educated/${testType}`);
  };

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading your cognitive assessment dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Cognitive Assessment Dashboard</h1>
          <p className="text-gray-600">Comprehensive cognitive monitoring and analysis</p>
        </header>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Tests Completed</p>
                <p className="text-2xl font-bold text-gray-900">{testHistory.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Latest Score</p>
                <p className="text-2xl font-bold text-gray-900">
                  {progress.length > 0 ? `${Math.round(progress[0].score)}%` : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center">
              <div className={`p-2 rounded-lg ${
                progress.length > 0 && progress[0].risk_level === 'low' ? 'bg-green-100' :
                progress.length > 0 && progress[0].risk_level === 'medium' ? 'bg-yellow-100' : 'bg-red-100'
              }`}>
                <svg className={`w-6 h-6 ${
                  progress.length > 0 && progress[0].risk_level === 'low' ? 'text-green-600' :
                  progress.length > 0 && progress[0].risk_level === 'medium' ? 'text-yellow-600' : 'text-red-600'
                }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Risk Level</p>
                <p className="text-2xl font-bold text-gray-900 capitalize">
                  {progress.length > 0 ? progress[0].risk_level : 'Unknown'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Next Test</p>
                <p className="text-sm font-bold text-gray-900">
                  {testHistory.length > 0 && testHistory[0].next_recommended_date 
                    ? formatDate(testHistory[0].next_recommended_date)
                    : 'Schedule Now'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Assessment Actions */}
          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Start New Assessment</h2>
            
            <div className="space-y-4">
              <button
                onClick={startComprehensiveAssessment}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200"
              >
                <div className="flex items-center justify-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Comprehensive Assessment (45 min)
                </div>
              </button>

              <button
                onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                <div className="flex items-center justify-center">
                  <svg className={`w-5 h-5 mr-2 transform transition-transform ${showAdvancedOptions ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                  Advanced Options
                </div>
              </button>

              {showAdvancedOptions && (
                <div className="mt-4 space-y-2 border-t pt-4">
                  <button
                    onClick={() => startSpecificTest('moca')}
                    className="w-full text-left py-2 px-4 hover:bg-gray-50 rounded transition-colors"
                  >
                    MoCA Assessment Only (15 min)
                  </button>
                  <button
                    onClick={() => startSpecificTest('mmse')}
                    className="w-full text-left py-2 px-4 hover:bg-gray-50 rounded transition-colors"
                  >
                    MMSE Assessment Only (10 min)
                  </button>
                  <button
                    onClick={() => startSpecificTest('trail-making')}
                    className="w-full text-left py-2 px-4 hover:bg-gray-50 rounded transition-colors"
                  >
                    Trail Making Test (10 min)
                  </button>
                  <button
                    onClick={() => startSpecificTest('stroop')}
                    className="w-full text-left py-2 px-4 hover:bg-gray-50 rounded transition-colors"
                  >
                    Stroop Test (10 min)
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Recent Test History */}
          <div className="bg-white rounded-lg p-6 shadow-sm border">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Recent Assessments</h2>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="1month">Last Month</option>
                <option value="3months">Last 3 Months</option>
                <option value="6months">Last 6 Months</option>
                <option value="1year">Last Year</option>
              </select>
            </div>

            <div className="space-y-4">
              {testHistory.slice(0, 5).map((session, index) => (
                <div key={session.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">
                        {session.session_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(session.started_at)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-lg font-semibold text-gray-900">
                        {Math.round(session.overall_score || 0)}%
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        getRiskLevelColor(session.overall_risk_level)
                      }`}>
                        {session.overall_risk_level?.toUpperCase() || 'PENDING'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}

              {testHistory.length === 0 && (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-gray-500 mb-4">No assessments completed yet</p>
                  <button
                    onClick={startComprehensiveAssessment}
                    className="text-blue-600 hover:text-blue-700 font-medium"
                  >
                    Start your first assessment
                  </button>
                </div>
              )}

              {testHistory.length > 0 && (
                <button
                  onClick={() => navigate('/reports')}
                  className="w-full mt-4 text-blue-600 hover:text-blue-700 font-medium py-2 border border-blue-200 hover:border-blue-300 rounded-lg transition-colors"
                >
                  View Detailed Reports
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Progress Chart - Would integrate with a charting library */}
        <div className="mt-8 bg-white rounded-lg p-6 shadow-sm border">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Progress Trends</h2>
          
          {progress.length > 1 ? (
            <div className="h-64 flex items-center justify-center border border-gray-200 rounded-lg bg-gray-50">
              <div className="text-center">
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-gray-600">Progress chart would be displayed here</p>
                <p className="text-sm text-gray-500">Trend: {progress[0].trend || 'Stable'}</p>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center border border-gray-200 rounded-lg bg-gray-50">
              <div className="text-center">
                <p className="text-gray-600 mb-2">Complete more assessments to see trends</p>
                <button
                  onClick={startComprehensiveAssessment}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Start Assessment
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export { NonEducatedDashboard, EducatedDashboard };