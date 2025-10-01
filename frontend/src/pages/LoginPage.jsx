import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { authAPI } from '../lib/api'
import { Brain, Eye, EyeOff } from 'lucide-react'
import Layout from '../components/Layout'

function LoginPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    email: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authAPI.login(formData)
      localStorage.setItem('user', JSON.stringify(response.data))
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || t('common.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Layout>
      <div className="min-h-[calc(100vh-8rem)] flex items-center justify-center p-4">
        <div className="glass rounded-2xl p-8 w-full max-w-md">
          <div className="flex justify-center mb-6">
            <Brain className="w-16 h-16 text-indigo-600" />
          </div>
          
          <h1 className="text-3xl font-bold text-center mb-6 text-gray-900">
            {t('auth.login_title')}
          </h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" data-testid="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('auth.email_address')}
              </label>
              <input
                type="email"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                data-testid="email-input"
                placeholder="Enter your email address"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="login-submit-btn"
            >
              {loading ? t('common.loading') : t('auth.login_button')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              {t('auth.dont_have_account')}{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-indigo-600 font-semibold hover:underline"
                data-testid="goto-register-btn"
              >
                {t('navigation.register')}
              </button>
            </p>
          </div>

          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              Simplified authentication for demo purposes.
              <br />
              Just enter your email to log in.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default LoginPage