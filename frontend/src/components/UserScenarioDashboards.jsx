import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';

// Blind User Dashboard - Voice-First Interface
const BlindUserDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [isListening, setIsListening] = useState(false);
  const [currentMessage, setCurrentMessage] = useState('');
  const [testSession, setTestSession] = useState(null);
  const speechSynthesis = window.speechSynthesis;
  const speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = useRef(null);

  useEffect(() => {
    // Initialize speech recognition
    if (speechRecognition) {
      recognition.current = new speechRecognition();
      recognition.current.continuous = true;
      recognition.current.interimResults = true;
      recognition.current.lang = user.language || 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        handleVoiceCommand(transcript.toLowerCase());
      };

      recognition.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
    }

    // Welcome message
    speak("Welcome to your cognitive assessment dashboard. Say 'help' for available commands or 'start test' to begin your assessment.");

    return () => {
      if (recognition.current) {
        recognition.current.stop();
      }
    };
  }, []);

  const speak = (message) => {
    if (speechSynthesis) {
      speechSynthesis.cancel(); // Cancel any ongoing speech
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = user.preferences?.voice_speed || 1.0;
      utterance.voice = speechSynthesis.getVoices().find(voice => 
        voice.gender === (user.preferences?.voice_gender || 'female')
      ) || speechSynthesis.getVoices()[0];
      speechSynthesis.speak(utterance);
    }
  };

  const startListening = () => {
    if (recognition.current && !isListening) {
      setIsListening(true);
      recognition.current.start();
      speak("I'm listening. Please speak your command.");
    }
  };

  const stopListening = () => {
    if (recognition.current && isListening) {
      setIsListening(false);
      recognition.current.stop();
    }
  };

  const handleVoiceCommand = async (command) => {
    setCurrentMessage(command);
    
    if (command.includes('help')) {
      speak("Available commands: Start test to begin cognitive assessment, Check progress to hear your results, Schedule next test, or Repeat instructions.");
    } else if (command.includes('start test') || command.includes('begin assessment')) {
      await startNewTestSession();
    } else if (command.includes('check progress') || command.includes('my results')) {
      speak("Checking your latest test results. Please wait.");
      await checkProgress();
    } else if (command.includes('schedule') || command.includes('next test')) {
      speak("Your next recommended test is scheduled based on your risk level. I'll provide details after your current assessment.");
    } else if (command.includes('repeat') || command.includes('again')) {
      speak("Welcome to your cognitive assessment dashboard. Available commands are: Start test, Check progress, Schedule next test, or Help for more information.");
    } else {
      speak("I didn't understand that command. Say 'help' to hear available options.");
    }
  };

  const startNewTestSession = async () => {
    try {
      speak("Starting your cognitive assessment. This will include memory tests, attention tasks, and speech analysis. The entire session takes about 30 minutes.");
      
      const sessionData = {
        user_id: user.id,
        session_type: 'comprehensive_blind',
      };
      
      const response = await api.post('/api/test-sessions', sessionData);
      setTestSession(response.data);
      
      speak("Test session created. Starting with the Auditory Verbal Learning Test. You will hear 15 words. Listen carefully and remember them.");
      
      // Navigate to first test
      navigate(`/tests/blind/avlt/${response.data.id}`);
    } catch (error) {
      console.error('Error starting test session:', error);
      speak("Sorry, there was an error starting your test. Please try again or contact support.");
    }
  };

  const checkProgress = async () => {
    try {
      const response = await api.get(`/api/progress/user/${user.id}`);
      const progress = response.data;
      
      if (progress && progress.length > 0) {
        const latest = progress[0];
        speak(`Your latest test score was ${Math.round(latest.score)} percent. Your risk level is ${latest.risk_level}. ${latest.trend === 'improving' ? 'Your performance is improving.' : latest.trend === 'declining' ? 'We noticed some decline in performance.' : 'Your performance is stable.'}`); 
      } else {
        speak("You haven't completed any tests yet. Say 'start test' to begin your first assessment.");
      }
    } catch (error) {
      console.error('Error checking progress:', error);
      speak("Sorry, I couldn't retrieve your progress information. Please try again later.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6" role="main" aria-label="Blind User Dashboard">
      {/* Hidden visual elements for screen readers */}
      <div className="sr-only">
        <h1>Cognitive Assessment Dashboard for Blind Users</h1>
        <p>This is a voice-controlled interface. Use voice commands to navigate.</p>
      </div>

      {/* Voice Control Interface */}
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-center max-w-2xl">
          <div 
            className={`w-32 h-32 mx-auto mb-8 rounded-full flex items-center justify-center transition-all duration-300 ${
              isListening ? 'bg-red-500 animate-pulse' : 'bg-blue-500'
            }`}
            role="status"
            aria-label={isListening ? "Listening for voice command" : "Ready to listen"}
          >
            <svg 
              className="w-16 h-16" 
              fill="currentColor" 
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
            </svg>
          </div>

          <h2 className="text-2xl font-bold mb-4" role="heading" aria-level="2">
            Voice Control Active
          </h2>

          {currentMessage && (
            <div className="mb-4 p-4 bg-gray-800 rounded-lg" role="status">
              <p className="text-lg">Last command: "{currentMessage}"</p>
            </div>
          )}

          <div className="space-y-4">
            <button
              onClick={isListening ? stopListening : startListening}
              className={`px-8 py-4 rounded-lg text-lg font-semibold transition-colors ${
                isListening 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
              aria-label={isListening ? "Stop listening" : "Start listening"}
            >
              {isListening ? 'Stop Listening' : 'Start Listening'}
            </button>

            <div className="text-sm text-gray-400 mt-6" role="region" aria-label="Voice commands help">
              <p className="font-semibold mb-2">Voice Commands:</p>
              <ul className="space-y-1 text-left max-w-md mx-auto">
                <li>• "Start test" - Begin cognitive assessment</li>
                <li>• "Check progress" - Hear your latest results</li>
                <li>• "Schedule next test" - Get scheduling information</li>
                <li>• "Help" - Hear all available commands</li>
                <li>• "Repeat" - Repeat welcome message</li>
              </ul>
            </div>
          </div>

          {/* Audio feedback for interactions */}
          <div className="mt-8" role="region" aria-label="System status">
            <div className="flex items-center justify-center space-x-4">
              <div className={`w-3 h-3 rounded-full ${
                isListening ? 'bg-red-400 animate-ping' : 'bg-green-400'
              }`} aria-hidden="true"></div>
              <span className="text-sm">
                {isListening ? 'Listening for commands...' : 'Ready for voice commands'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Emergency navigation (hidden, accessible via screen reader) */}
      <div className="sr-only">
        <nav role="navigation" aria-label="Emergency navigation">
          <button onClick={() => navigate('/tests')} aria-label="Go to tests page">Tests</button>
          <button onClick={() => navigate('/reports')} aria-label="Go to reports page">Reports</button>
          <button onClick={() => navigate('/')} aria-label="Go to home page">Home</button>
        </nav>
      </div>
    </div>
  );
};

// Weak Vision User Dashboard - Large Text + Voice Support
const WeakVisionDashboard = ({ user }) => {
  const navigate = useNavigate();
  const [highContrast, setHighContrast] = useState(user.preferences?.high_contrast || false);
  const [textSize, setTextSize] = useState(user.preferences?.text_size || 'large');
  const [voiceGuidance, setVoiceGuidance] = useState(user.preferences?.voice_guidance || true);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
    if (voiceGuidance) {
      speak("Welcome to your cognitive assessment dashboard. All text is large and high contrast for easier reading.");
    }
  }, []);

  const speak = (message) => {
    if (voiceGuidance && window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = user.preferences?.voice_speed || 0.9;
      window.speechSynthesis.speak(utterance);
    }
  };

  const loadProgress = async () => {
    try {
      const response = await api.get(`/api/progress/user/${user.id}`);
      setProgress(response.data || []);
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const startTest = async () => {
    speak("Starting your cognitive assessment with large text and high contrast display.");
    
    try {
      const sessionData = {
        user_id: user.id,
        session_type: 'comprehensive_weak_vision',
      };
      
      const response = await api.post('/api/test-sessions', sessionData);
      navigate(`/tests/weak-vision/mmse/${response.data.id}`);
    } catch (error) {
      console.error('Error starting test:', error);
      speak("Sorry, there was an error starting your test.");
    }
  };

  const textSizeClasses = {
    large: 'text-2xl',
    xlarge: 'text-3xl', 
    xxlarge: 'text-4xl'
  };

  const buttonSizeClasses = {
    large: 'px-8 py-4 text-xl',
    xlarge: 'px-10 py-6 text-2xl',
    xxlarge: 'px-12 py-8 text-3xl'
  };

  const containerClasses = `min-h-screen p-8 ${
    highContrast 
      ? 'bg-black text-white' 
      : 'bg-white text-gray-900'
  }`;

  return (
    <div className={containerClasses}>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-12">
          <h1 className={`font-bold mb-4 ${textSize === 'large' ? 'text-5xl' : textSize === 'xlarge' ? 'text-6xl' : 'text-7xl'}`}>
            Cognitive Assessment Dashboard
          </h1>
          
          <div className="flex flex-wrap gap-4 mb-6">
            <button
              onClick={() => setHighContrast(!highContrast)}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold transition-colors ${
                highContrast 
                  ? 'bg-white text-black hover:bg-gray-200'
                  : 'bg-gray-900 text-white hover:bg-gray-700'
              }`}
              onMouseEnter={() => voiceGuidance && speak(highContrast ? "Switch to normal contrast" : "Switch to high contrast")}
            >
              {highContrast ? 'Normal Contrast' : 'High Contrast'}
            </button>
            
            <button
              onClick={() => setVoiceGuidance(!voiceGuidance)}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold ${
                highContrast
                  ? 'bg-gray-800 text-white hover:bg-gray-700'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
              onMouseEnter={() => speak(voiceGuidance ? "Turn off voice guidance" : "Turn on voice guidance")}
            >
              Voice: {voiceGuidance ? 'ON' : 'OFF'}
            </button>
            
            <select
              value={textSize}
              onChange={(e) => setTextSize(e.target.value)}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold ${
                highContrast
                  ? 'bg-gray-800 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
              onFocus={() => voiceGuidance && speak("Text size options")}
            >
              <option value="large">Large Text</option>
              <option value="xlarge">Extra Large</option>
              <option value="xxlarge">Super Large</option>
            </select>
          </div>
        </header>

        {/* Main Actions */}
        <section className="mb-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className={`p-8 rounded-xl border-4 ${
              highContrast ? 'border-white bg-gray-900' : 'border-gray-300 bg-gray-50'
            }`}>
              <h2 className={`${textSizeClasses[textSize]} font-bold mb-6`}>Start New Assessment</h2>
              <p className={`${textSize === 'large' ? 'text-lg' : textSize === 'xlarge' ? 'text-xl' : 'text-2xl'} mb-8 leading-relaxed`}>
                Begin your comprehensive cognitive assessment with tests adapted for vision accessibility.
              </p>
              <button
                onClick={startTest}
                className={`w-full ${buttonSizeClasses[textSize]} rounded-lg font-bold transition-colors ${
                  highContrast
                    ? 'bg-white text-black hover:bg-gray-200'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
                onMouseEnter={() => voiceGuidance && speak("Start new cognitive assessment")}
              >
                Start Assessment
              </button>
            </div>

            <div className={`p-8 rounded-xl border-4 ${
              highContrast ? 'border-white bg-gray-900' : 'border-gray-300 bg-gray-50'
            }`}>
              <h2 className={`${textSizeClasses[textSize]} font-bold mb-6`}>Your Progress</h2>
              {loading ? (
                <p className={`${textSize === 'large' ? 'text-lg' : textSize === 'xlarge' ? 'text-xl' : 'text-2xl'}`}>Loading...</p>
              ) : progress.length > 0 ? (
                <div>
                  <p className={`${textSize === 'large' ? 'text-lg' : textSize === 'xlarge' ? 'text-xl' : 'text-2xl'} mb-4`}>
                    Latest Score: <span className="font-bold text-3xl">{Math.round(progress[0].score)}%</span>
                  </p>
                  <p className={`${textSize === 'large' ? 'text-lg' : textSize === 'xlarge' ? 'text-xl' : 'text-2xl'} mb-4`}>
                    Risk Level: <span className={`font-bold ${
                      progress[0].risk_level === 'low' ? 'text-green-500' :
                      progress[0].risk_level === 'medium' ? 'text-yellow-500' : 'text-red-500'
                    }`}>{progress[0].risk_level.toUpperCase()}</span>
                  </p>
                  <button
                    onClick={() => navigate('/reports')}
                    className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold ${
                      highContrast
                        ? 'bg-gray-700 text-white hover:bg-gray-600'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                    onMouseEnter={() => voiceGuidance && speak("View detailed reports")}
                  >
                    View Reports
                  </button>
                </div>
              ) : (
                <p className={`${textSize === 'large' ? 'text-lg' : textSize === 'xlarge' ? 'text-xl' : 'text-2xl'}`}>
                  No assessments completed yet. Start your first test!
                </p>
              )}
            </div>
          </div>
        </section>

        {/* Navigation */}
        <nav className="border-t-4 pt-8" style={{borderColor: highContrast ? 'white' : '#d1d5db'}}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => navigate('/tests')}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold transition-colors ${
                highContrast
                  ? 'bg-gray-800 text-white hover:bg-gray-700'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
              onMouseEnter={() => voiceGuidance && speak("Go to tests page")}
            >
              All Tests
            </button>
            
            <button
              onClick={() => navigate('/reports')}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold transition-colors ${
                highContrast
                  ? 'bg-gray-800 text-white hover:bg-gray-700'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
              onMouseEnter={() => voiceGuidance && speak("Go to reports page")}
            >
              Reports
            </button>
            
            <button
              onClick={() => navigate('/')}
              className={`${buttonSizeClasses[textSize]} rounded-lg font-semibold transition-colors ${
                highContrast
                  ? 'bg-gray-800 text-white hover:bg-gray-700'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
              onMouseEnter={() => voiceGuidance && speak("Go to home page")}
            >
              Home
            </button>
          </div>
        </nav>
      </div>
    </div>
  );
};

export { BlindUserDashboard, WeakVisionDashboard };