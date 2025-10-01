import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import { HybridInput } from '../components/assessment/HybridInput';
import api from '../services/api';
import { Clock, Loader2 } from 'lucide-react';

const TARGET_WORDS = ['Apple', 'Ball', 'Cat', 'Dog', 'Elephant'];
const WAIT_TIME = 120; // 2 minutes in seconds

export const MemoryTest = () => {
  const navigate = useNavigate();
  const { userId, saveTestResult, setCurrentTest, trackInteraction } = useAssessment();
  const [phase, setPhase] = useState('instruction'); // instruction, memorize, wait, recall
  const [timeLeft, setTimeLeft] = useState(WAIT_TIME);
  const [startTime, setStartTime] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) {
      navigate('/');
    }
  }, [userId, navigate]);

  useEffect(() => {
    if (phase === 'wait' && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else if (phase === 'wait' && timeLeft === 0) {
      setPhase('recall');
    }
  }, [phase, timeLeft]);

  const handleStartMemorize = () => {
    setPhase('memorize');
    trackInteraction('memory_test_started');
  };

  const handleStartWait = () => {
    setPhase('wait');
    setStartTime(Date.now());
    trackInteraction('memory_waiting_started');
  };

  const handleRecallSubmit = async (text, isVoice = false) => {
    setLoading(true);
    try {
      const responseTime = Date.now() - startTime;
      
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('response_time_ms', responseTime);
      
      if (isVoice) {
        formData.append('audio_file', text);
      } else {
        formData.append('response_text', text);
      }

      const result = await api.submitMemoryTest(formData);
      saveTestResult('memory', result);
      trackInteraction('memory_test_completed', { score: result.score });
      setCurrentTest('pattern');
      navigate('/pattern');
    } catch (error) {
      console.error('Memory test submission failed:', error);
      alert('Failed to submit test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <TestLayout
      title="Memory Test"
      description="Test your ability to recall information"
      progress={16.6}
    >
      <div className="space-y-6">
        {phase === 'instruction' && (
          <div className="text-center space-y-6">
            <div className="text-lg text-gray-700 space-y-4">
              <p>In this test, you will:</p>
              <ol className="text-left list-decimal list-inside space-y-2 max-w-2xl mx-auto">
                <li>See 5 words to remember</li>
                <li>Wait for 2 minutes</li>
                <li>Recall as many words as you can</li>
              </ol>
            </div>
            <button
              onClick={handleStartMemorize}
              className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all"
              data-testid="start-memory-btn"
            >
              Begin Test
            </button>
          </div>
        )}

        {phase === 'memorize' && (
          <div className="text-center space-y-8">
            <h3 className="text-2xl font-bold text-gray-800">Remember these words:</h3>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
              {TARGET_WORDS.map((word, idx) => (
                <div
                  key={idx}
                  className="p-6 bg-blue-100 border-2 border-blue-300 rounded-lg text-2xl font-bold text-blue-800"
                  data-testid={`word-${idx}`}
                >
                  {word}
                </div>
              ))}
            </div>
            <button
              onClick={handleStartWait}
              className="px-8 py-4 bg-green-600 text-white text-lg font-semibold rounded-lg hover:bg-green-700 transition-all"
              data-testid="start-wait-btn"
            >
              I've Memorized Them
            </button>
          </div>
        )}

        {phase === 'wait' && (
          <div className="text-center space-y-6">
            <Clock className="w-24 h-24 mx-auto text-blue-600 animate-pulse" />
            <h3 className="text-3xl font-bold text-gray-800">{formatTime(timeLeft)}</h3>
            <p className="text-lg text-gray-600">
              Please wait while the timer counts down.
              <br />
              Try to keep the words in your mind!
            </p>
          </div>
        )}

        {phase === 'recall' && (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-800 text-center">
              Time's up! What words do you remember?
            </h3>
            <HybridInput
              label="Enter the words you remember (separated by commas)"
              placeholder="Example: Apple, Ball, Cat"
              multiline={true}
              onTextSubmit={(text) => handleRecallSubmit(text, false)}
              onVoiceSubmit={(blob) => handleRecallSubmit(blob, true)}
            />
            {loading && (
              <div className="flex items-center justify-center gap-2 text-blue-600">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing your response...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </TestLayout>
  );
};