import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Brain, Home, BarChart3, FileText, User, LogOut } from 'lucide-react'
import LanguageSwitcher from './LanguageSwitcher'
import VoiceToggle from './VoiceToggle'

function Layout({ children }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()

  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isLoggedIn = !!user.id

  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/')
  }

  const navigation = [
    { name: t('navigation.home'), href: '/', icon: Home },
    { name: t('navigation.dashboard'), href: '/dashboard', icon: BarChart3, requireAuth: true },
    { name: t('navigation.tests'), href: '/tests', icon: Brain, requireAuth: true },
    { name: t('navigation.reports'), href: '/reports', icon: FileText, requireAuth: true }
  ]

  const filteredNavigation = navigation.filter(item => !item.requireAuth || isLoggedIn)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="glass border-b border-white/20">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div 
              className="flex items-center gap-2 cursor-pointer"
              onClick={() => navigate('/')}
            >
              <Brain className="w-8 h-8 text-indigo-600" />
              <span className="font-bold text-xl text-gray-900">CogniCare</span>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-6">
              {filteredNavigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <button
                    key={item.name}
                    onClick={() => navigate(item.href)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive 
                        ? 'bg-indigo-100 text-indigo-700' 
                        : 'text-gray-600 hover:text-gray-900 hover:bg-white/20'
                    }`}
                    data-testid={`nav-${item.href.replace('/', '') || 'home'}`}
                  >
                    <item.icon className="w-4 h-4" />
                    {item.name}
                  </button>
                )
              })}
            </nav>

            {/* User Actions */}
            <div className="flex items-center gap-3">
              <VoiceToggle />
              <LanguageSwitcher />
              
              {isLoggedIn ? (
                <div className="flex items-center gap-3">
                  <span className="hidden sm:block text-sm text-gray-600">
                    {user.name || t('navigation.profile')}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-all"
                    data-testid="logout-btn"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="hidden sm:block">{t('navigation.logout')}</span>
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate('/login')}
                    className="px-4 py-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors"
                    data-testid="header-login-btn"
                  >
                    {t('navigation.login')}
                  </button>
                  <button
                    onClick={() => navigate('/register')}
                    className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
                    data-testid="header-register-btn"
                  >
                    {t('navigation.register')}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="glass border-t border-white/20 mt-auto">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <Brain className="w-6 h-6 text-indigo-600" />
              <span className="text-sm text-gray-600">
                © 2025 CogniCare. AI-powered cognitive health assessment.
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>Privacy Policy</span>
              <span>Terms of Service</span>
              <span>Support</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout