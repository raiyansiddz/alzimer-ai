import i18n from 'i18next'
import Backend from 'i18next-http-backend'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'

// Import translations
import enTranslation from './locales/en.json'
import hiTranslation from './locales/hi.json'
import hiEnTranslation from './locales/hi-en.json'
import taTranslation from './locales/ta.json'
import teTranslation from './locales/te.json'
import bnTranslation from './locales/bn.json'
import mrTranslation from './locales/mr.json'
import guTranslation from './locales/gu.json'
import esTranslation from './locales/es.json'
import frTranslation from './locales/fr.json'
import deTranslation from './locales/de.json'
import zhTranslation from './locales/zh.json'
import arTranslation from './locales/ar.json'

const resources = {
  en: { translation: enTranslation },
  hi: { translation: hiTranslation },
  'hi-en': { translation: hiEnTranslation },
  ta: { translation: taTranslation },
  te: { translation: teTranslation },
  bn: { translation: bnTranslation },
  mr: { translation: mrTranslation },
  gu: { translation: guTranslation },
  es: { translation: esTranslation },
  fr: { translation: frTranslation },
  de: { translation: deTranslation },
  zh: { translation: zhTranslation },
  ar: { translation: arTranslation }
}

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    
    interpolation: {
      escapeValue: false
    },
    
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage']
    }
  })

export default i18n