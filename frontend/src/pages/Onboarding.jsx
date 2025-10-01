import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import { HybridInput } from '../components/assessment/HybridInput';
import api from '../services/api';
import { Loader2 } from 'lucide-react';

export const Onboarding = () => {
  const navigate = useNavigate();
  const { setUserId, setUserName, setUserAge, setLocale, setCurrentTest, trackInteraction } = useAssessment();
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [selectedLocale, setSelectedLocale] = useState('en');
  const [loading, setLoading] = useState(false);

  const handleNameSubmit = (value) => {
    setName(value);
    setStep(2);
    trackInteraction('name_entered', { name: value });
  };

  const handleAgeSubmit = (value) => {
    const ageNum = parseInt(value);
    if (ageNum && ageNum > 0 && ageNum < 150) {
      setAge(ageNum);
      setStep(3);
      trackInteraction('age_entered', { age: ageNum });
    } else {
      alert('Please enter a valid age');
    }
  };

  const handleSubmit = async () => {
    if (!name || !age || !selectedLocale) {
      alert('Please complete all fields');
      return;
    }

    setLoading(true);
    try {
      const userData = {
        name,
        age: parseInt(age),
        locale: selectedLocale
      };

      const response = await api.registerUser(userData);
      
      setUserId(response.user_id);
      setUserName(name);
      setUserAge(age);
      setLocale(selectedLocale);
      setCurrentTest('memory');
      trackInteraction('registration_complete', userData);
      
      navigate('/memory');
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <TestLayout
      title="Welcome to Cognitive Assessment"
      description="Let's start by getting to know you"
      showBack={false}
      progress={(step / 3) * 100}
    >
      <div className="space-y-8">
        {step === 1 && (
          <div className="space-y-4">
            <HybridInput
              label="What's your name?"
              placeholder="Enter your full name"
              onTextSubmit={handleNameSubmit}
              onVoiceSubmit={(blob) => {
                // In production, transcribe the audio
                alert('Please use text input for name');
              }}
            />
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <HybridInput
              label="What's your age?"
              placeholder="Enter your age"
              onTextSubmit={handleAgeSubmit}
              onVoiceSubmit={(blob) => {
                alert('Please use text input for age');
              }}
            />
          </div>
        )}

        {step === 3 && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-gray-700">Select Your Language</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { code: 'en', name: 'English' },
                { code: 'hi', name: 'हिन्दी (Hindi)' },
                { code: 'es', name: 'Español (Spanish)' }
              ].map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    setSelectedLocale(lang.code);
                    trackInteraction('locale_selected', { locale: lang.code });
                  }}
                  className={`p-4 border-2 rounded-lg transition-all ${
                    selectedLocale === lang.code
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-blue-400'
                  }`}
                  data-testid={`locale-${lang.code}`}
                >
                  <span className="text-lg font-medium">{lang.name}</span>
                </button>
              ))}
            </div>

            <button
              onClick={handleSubmit}
              disabled={loading || !selectedLocale}
              className="w-full mt-6 px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              data-testid="start-assessment-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Starting...
                </>
              ) : (
                'Start Assessment'
              )}
            </button>

            <div className="mt-4 text-sm text-gray-600 text-center">
              <p>Name: {name}</p>
              <p>Age: {age}</p>
            </div>
          </div>
        )}
      </div>
    </TestLayout>
  );
};