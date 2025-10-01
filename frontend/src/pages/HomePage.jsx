import { useNavigate } from 'react-router-dom'
import { Brain, Users, Activity, TrendingUp } from 'lucide-react'

function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16 fade-in">
          <div className="flex justify-center mb-6">
            <Brain className="w-20 h-20 text-indigo-600" />
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-4">
            Dementia Detection System
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Comprehensive cognitive assessment platform with AI-powered analysis
          </p>
          <button
            onClick={() => navigate('/register')}
            className="glass px-8 py-4 rounded-xl text-lg font-semibold text-indigo-600 hover:bg-white/20 transition-all transform hover:scale-105"
            data-testid="get-started-btn"
          >
            Get Started
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="glass rounded-2xl p-8 fade-in" style={{animationDelay: '0.1s'}}>
            <Users className="w-12 h-12 text-indigo-600 mb-4" />
            <h3 className="text-2xl font-bold mb-3 text-gray-900">For All Users</h3>
            <p className="text-gray-700">
              Accessible interfaces for blind, weak vision, non-educated, and educated users
            </p>
          </div>

          <div className="glass rounded-2xl p-8 fade-in" style={{animationDelay: '0.2s'}}>
            <Activity className="w-12 h-12 text-purple-600 mb-4" />
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Comprehensive Tests</h3>
            <p className="text-gray-700">
              Cognitive, speech, and behavioral assessments tailored to your needs
            </p>
          </div>

          <div className="glass rounded-2xl p-8 fade-in" style={{animationDelay: '0.3s'}}>
            <TrendingUp className="w-12 h-12 text-pink-600 mb-4" />
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Track Progress</h3>
            <p className="text-gray-700">
              Monitor cognitive health over time with detailed reports and visualizations
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-16 text-center">
          <div className="glass rounded-2xl p-12 max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold mb-4 text-gray-900">Ready to Begin?</h2>
            <p className="text-gray-700 mb-8 text-lg">
              Create your account and start your cognitive health journey today
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => navigate('/register')}
                className="bg-indigo-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-all transform hover:scale-105"
                data-testid="register-btn"
              >
                Register Now
              </button>
              <button
                onClick={() => navigate('/login')}
                className="glass-dark text-white px-8 py-3 rounded-xl font-semibold hover:bg-black/30 transition-all"
                data-testid="login-btn"
              >
                Login
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
