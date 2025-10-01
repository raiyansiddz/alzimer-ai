import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import api from '../services/api';
import { Circle, Square, Triangle, Star, Loader2 } from 'lucide-react';

const PATTERN = [
  { shape: 'circle', icon: Circle },
  { shape: 'square', icon: Square },
  { shape: 'circle', icon: Circle },
  { shape: 'square', icon: Square },
];

const OPTIONS = [
  { shape: 'Circle', icon: Circle, color: 'blue' },
  { shape: 'Square', icon: Square, color: 'green' },
  { shape: 'Triangle', icon: Triangle, color: 'purple' },
  { shape: 'Star', icon: Star, color: 'orange' },
];

export const PatternTest = () => {
  const navigate = useNavigate();
  const { userId, saveTestResult, setCurrentTest, trackInteraction } = useAssessment();
  const [startTime, setStartTime] = useState(null);
  const [loading, setLoading] = useState(false);
  const [phase, setPhase] = useState('instruction');

  useEffect(() => {
    if (!userId) {
      navigate('/');
    }
  }, [userId, navigate]);

  const handleStart = () => {
    setPhase('test');
    setStartTime(Date.now());
    trackInteraction('pattern_test_started');
  };

  const handleAnswerSelect = async (answer) => {
    setLoading(true);
    try {
      const responseTime = Date.now() - startTime;
      
      const result = await api.submitPatternTest({
        user_id: userId,
        user_answer: answer,
        response_time_ms: responseTime
      });

      saveTestResult('pattern', result);
      trackInteraction('pattern_test_completed', { 
        answer,
        is_correct: result.is_correct,
        response_time: responseTime 
      });
      setCurrentTest('clock');
      navigate('/clock');
    } catch (error) {
      console.error('Pattern test submission failed:', error);
      alert('Failed to submit test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <TestLayout
      title="Pattern Recognition Test"
      description="Identify the next shape in the pattern"
      progress={33.2}
    >
      <div className="space-y-8">
        {phase === 'instruction' && (
          <div className="text-center space-y-6">
            <div className="text-lg text-gray-700 space-y-4">
              <p>You will see a pattern of shapes.</p>
              <p>Your task is to identify which shape comes next.</p>
            </div>
            <button
              onClick={handleStart}
              className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all"
              data-testid="start-pattern-btn"
            >
              Start Test
            </button>
          </div>
        )}

        {phase === 'test' && (
          <div className="space-y-8">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">
                What comes next in this pattern?
              </h3>
              
              {/* Pattern Display */}
              <div className="flex items-center justify-center gap-4 mb-4 flex-wrap">
                {PATTERN.map((item, idx) => {
                  const Icon = item.icon;
                  return (
                    <div key={idx} className="flex items-center">
                      <div className="p-6 bg-gray-100 rounded-lg border-2 border-gray-300">
                        <Icon className="w-16 h-16 text-gray-700" />
                      </div>
                      <span className="text-3xl mx-2 text-gray-400">→</span>
                    </div>
                  );
                })}
                <div className="p-6 bg-blue-100 rounded-lg border-2 border-blue-400 border-dashed">
                  <span className="text-5xl text-blue-600">?</span>
                </div>
              </div>
            </div>

            {/* Answer Options */}
            <div className="mt-12">
              <h4 className="text-xl font-semibold text-gray-700 mb-4 text-center">
                Select the next shape:
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
                {OPTIONS.map((option) => {
                  const Icon = option.icon;
                  return (
                    <button
                      key={option.shape}
                      onClick={() => handleAnswerSelect(option.shape)}
                      disabled={loading}
                      className={`p-8 bg-white border-2 rounded-lg hover:border-${option.color}-500 hover:bg-${option.color}-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed group`}
                      data-testid={`option-${option.shape.toLowerCase()}`}
                    >
                      <Icon className={`w-20 h-20 mx-auto text-${option.color}-600 group-hover:scale-110 transition-transform`} />
                      <p className="mt-3 font-semibold text-gray-700">{option.shape}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            {loading && (
              <div className="flex items-center justify-center gap-2 text-blue-600 mt-6">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing your answer...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </TestLayout>
  );
};