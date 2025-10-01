import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import { DrawingCanvas } from '../components/assessment/DrawingCanvas';
import api from '../services/api';
import { Loader2 } from 'lucide-react';

export const ClockTest = () => {
  const navigate = useNavigate();
  const { userId, saveTestResult, setCurrentTest, trackInteraction } = useAssessment();
  const [phase, setPhase] = useState('instruction');
  const [startTime, setStartTime] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!userId) {
      navigate('/');
    }
  }, [userId, navigate]);

  const handleStart = () => {
    setPhase('drawing');
    setStartTime(Date.now());
    trackInteraction('clock_test_started');
  };

  const handleDrawingSave = async (imageDataURL) => {
    setLoading(true);
    try {
      const responseTime = Date.now() - startTime;
      
      const result = await api.submitClockTest({
        user_id: userId,
        image_base64: imageDataURL,
        response_time_ms: responseTime,
        image_metadata: {
          width: 600,
          height: 600,
          format: 'png'
        }
      });

      saveTestResult('clock', result);
      trackInteraction('clock_test_completed', { response_time: responseTime });
      setCurrentTest('speech');
      navigate('/speech');
    } catch (error) {
      console.error('Clock test submission failed:', error);
      alert('Failed to submit test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <TestLayout
      title="Clock Drawing Test"
      description="Draw a clock showing 10:30"
      progress={49.8}
    >
      <div className="space-y-8">
        {phase === 'instruction' && (
          <div className="text-center space-y-6">
            <div className="text-lg text-gray-700 space-y-4">
              <p className="font-semibold text-2xl text-gray-800">Draw a Clock</p>
              <p>You will be asked to draw a clock on the canvas.</p>
              <p>Include all 12 numbers and set the time to <strong>10:30</strong></p>
              <ol className="text-left list-decimal list-inside space-y-2 max-w-2xl mx-auto">
                <li>Draw a circle for the clock face</li>
                <li>Add all 12 numbers (1-12) in their correct positions</li>
                <li>Draw the hour hand pointing to 10</li>
                <li>Draw the minute hand pointing to 6 (30 minutes)</li>
              </ol>
            </div>
            <button
              onClick={handleStart}
              className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all"
              data-testid="start-clock-btn"
            >
              Start Drawing
            </button>
          </div>
        )}

        {phase === 'drawing' && (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-800">
                Draw a clock showing <span className="text-blue-600">10:30</span>
              </h3>
              <p className="text-gray-600 mt-2">
                Use your mouse or finger to draw on the canvas below
              </p>
            </div>
            
            <div className="flex justify-center">
              <DrawingCanvas onSave={handleDrawingSave} width={600} height={600} />
            </div>

            {loading && (
              <div className="flex items-center justify-center gap-2 text-blue-600 mt-6">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing your drawing...</span>
              </div>
            )}
          </div>
        )}
      </div>
    </TestLayout>
  );
};