import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { authAPI } from '../lib/api'
import { Brain } from 'lucide-react'
import Layout from '../components/Layout'

function RegisterPage() {
  const navigate = useNavigate()
  const { t } = useTranslation()
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    age: '',
    education_level: '',
    vision_type: '',
    language: 'en'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const payload = {
        ...formData,
        age: formData.age ? parseInt(formData.age) : null
      }
      const response = await authAPI.register(payload)
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
            {t('auth.register_title')}
          </h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" data-testid="error-message">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.email_address')}
              </label>
              <input
                type="email"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                data-testid="email-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.full_name')}
              </label>
              <input
                type="text"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
                data-testid="name-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('common.age')}
              </label>
              <input
                type="number"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.age}
                onChange={(e) => setFormData({...formData, age: e.target.value})}
                data-testid="age-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.education_level')}
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.education_level}
                onChange={(e) => setFormData({...formData, education_level: e.target.value})}
                data-testid="education-select"
              >
                <option value="">{t('common.select')}</option>
                <option value="non_educated">{t('auth.education_options.non_educated')}</option>
                <option value="primary">{t('auth.education_options.primary')}</option>
                <option value="secondary">{t('auth.education_options.secondary')}</option>
                <option value="graduate">{t('auth.education_options.graduate')}</option>
                <option value="postgraduate">{t('auth.education_options.postgraduate')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.vision_status')}
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.vision_type}
                onChange={(e) => setFormData({...formData, vision_type: e.target.value})}
                data-testid="vision-select"
              >
                <option value="">{t('common.select')}</option>
                <option value="normal">{t('auth.vision_options.normal')}</option>
                <option value="weak_vision">{t('auth.vision_options.weak_vision')}</option>
                <option value="blind">{t('auth.vision_options.blind')}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('auth.language_preference')}
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                value={formData.language}
                onChange={(e) => setFormData({...formData, language: e.target.value})}
                data-testid="language-select"
              >
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="ta">தமிழ் (Tamil)</option>
                <option value="te">తెలుగు (Telugu)</option>
                <option value="bn">বাংলা (Bengali)</option>
                <option value="mr">मराठी (Marathi)</option>
                <option value="gu">ગુજરાતી (Gujarati)</option>
                <option value="es">Español</option>
                <option value="fr">Français</option>
                <option value="de">Deutsch</option>
                <option value="zh">中文 (Chinese)</option>
                <option value="ar">العربية (Arabic)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition-all disabled:opacity-50"
              data-testid="submit-btn"
            >
              {loading ? t('common.loading') : t('auth.register_button')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              {t('auth.already_have_account')}{' '}
              <button
                onClick={() => navigate('/login')}
                className="text-indigo-600 font-semibold hover:underline"
                data-testid="goto-login-btn"
              >
                {t('navigation.login')}
              </button>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default RegisterPage