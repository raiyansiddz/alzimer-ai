import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssessment } from '../context/AssessmentContext';
import { TestLayout } from '../components/assessment/TestLayout';
import { HybridInput } from '../components/assessment/HybridInput';
import api from '../services/api';
import { Loader2, BookOpen, Image as ImageIcon, Brain } from 'lucide-react';

const TASKS = [
  {
    type: 'reading',
    title: 'Reading Task',
    icon: BookOpen,
    description: 'Read the paragraph below and then summarize it in your own words',
    content: `The quick brown fox jumps over the lazy dog. This sentence contains all the letters of the alphabet. 
Reading comprehension is an important cognitive skill that involves understanding written text.`,
    prompt: 'Summarize what you just read'
  },
  {
    type: 'picture_description',
    title: 'Picture Description',
    icon: ImageIcon,
    description: 'Describe what you see in this picture',
    imageUrl: 'https://images.unsplash.com/photo-1495954484750-af469f2f9be5?w=600&h=400&fit=crop',
    prompt: 'Describe everything you see in the picture above'
  },
  {
    type: 'spontaneous',
    title: 'Personal Memory',
    icon: Brain,
    description: 'Share a memory from your childhood',
    prompt: 'Tell us about a memorable event from your childhood'
  }
];

export const SpeechTest = () => {
  const navigate = useNavigate();
  const { userId, saveTestResult, setCurrentTest, trackInteraction } = useAssessment();
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [phase, setPhase] = useState('instruction');
  const [loading, setLoading] = useState(false);
  const [completedTasks, setCompletedTasks] = useState([]);

  useEffect(() => {
    if (!userId) {
      navigate('/');
    }
  }, [userId, navigate]);

  const currentTask = TASKS[currentTaskIndex];
  const Icon = currentTask.icon;

  const handleStart = () => {
    setPhase('task');
    trackInteraction('speech_test_started', { task: currentTask.type });
  };

  const handleSubmit = async (text, isVoice = false) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('user_id', userId);
      formData.append('task_type', currentTask.type);
      
      if (isVoice) {
        formData.append('audio_file', text);
        formData.append('audio_quality', 'good');
      } else {
        formData.append('response_text', text);
      }

      const result = await api.submitSpeechTest(formData);
      
      const newCompleted = [...completedTasks, { task: currentTask.type, result }];
      setCompletedTasks(newCompleted);
      trackInteraction('speech_task_completed', { 
        task: currentTask.type,
        risk_level: result.risk_level 
      });

      if (currentTaskIndex < TASKS.length - 1) {
        setCurrentTaskIndex(currentTaskIndex + 1);
        setPhase('instruction');
      } else {
        // All tasks completed
        saveTestResult('speech', newCompleted);
        setCurrentTest('results');
        navigate('/results');
      }
    } catch (error) {
      console.error('Speech test submission failed:', error);
      alert('Failed to submit test. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const progress = 66.4 + ((currentTaskIndex + 1) / TASKS.length) * 16.8;

  return (
    <TestLayout
      title="Speech & Language Test"
      description={`Task ${currentTaskIndex + 1} of ${TASKS.length}`}
      progress={progress}
    >
      <div className="space-y-8">
        {phase === 'instruction' && (
          <div className="text-center space-y-6">
            <Icon className="w-20 h-20 mx-auto text-blue-600" />
            <h3 className="text-2xl font-bold text-gray-800">{currentTask.title}</h3>
            <p className="text-lg text-gray-700 max-w-2xl mx-auto">
              {currentTask.description}
            </p>
            <button
              onClick={handleStart}
              className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all"
              data-testid="start-speech-task-btn"
            >
              Start Task
            </button>
          </div>
        )}

        {phase === 'task' && (
          <div className="space-y-6">
            {/* Task Content */}
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              {currentTask.content && (
                <div className="text-lg text-gray-800 whitespace-pre-line leading-relaxed">
                  {currentTask.content}
                </div>
              )}
              {currentTask.imageUrl && (
                <div className="flex justify-center">
                  <img 
                    src={currentTask.imageUrl} 
                    alt="Picture to describe" 
                    className="max-w-full rounded-lg shadow-lg"
                  />
                </div>
              )}
            </div>

            {/* Response Input */}
            <HybridInput
              label={currentTask.prompt}
              placeholder="Type or speak your response..."
              multiline={true}
              onTextSubmit={(text) => handleSubmit(text, false)}
              onVoiceSubmit={(blob) => handleSubmit(blob, true)}
            />

            {loading && (
              <div className="flex items-center justify-center gap-2 text-blue-600">
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing your response...</span>
              </div>
            )}

            {/* Progress Indicator */}
            <div className="text-center text-sm text-gray-600">
              Task {currentTaskIndex + 1} of {TASKS.length}
            </div>
          </div>
        )}
      </div>
    </TestLayout>
  );
};