import React, { useState } from 'react';
import { Keyboard, Mic } from 'lucide-react';
import { SimpleVoiceRecorder } from './VoiceRecorder';

export const HybridInput = ({ 
  onTextSubmit, 
  onVoiceSubmit, 
  placeholder = 'Type your answer...', 
  label = 'Your Answer',
  multiline = false 
}) => {
  const [inputMode, setInputMode] = useState('text'); // 'text' or 'voice'
  const [textValue, setTextValue] = useState('');

  const handleTextSubmit = () => {
    if (textValue.trim() && onTextSubmit) {
      onTextSubmit(textValue);
    }
  };

  const handleVoiceRecording = (blob) => {
    if (onVoiceSubmit) {
      onVoiceSubmit(blob);
    }
  };

  return (
    <div className="space-y-4">
      <label className="text-lg font-semibold text-gray-700">{label}</label>
      
      {/* Mode Toggle */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setInputMode('text')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            inputMode === 'text'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          data-testid="text-mode-btn"
        >
          <Keyboard className="w-4 h-4" />
          Type
        </button>
        <button
          onClick={() => setInputMode('voice')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            inputMode === 'voice'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          data-testid="voice-mode-btn"
        >
          <Mic className="w-4 h-4" />
          Speak
        </button>
      </div>

      {/* Input Area */}
      {inputMode === 'text' ? (
        <div className="space-y-3">
          {multiline ? (
            <textarea
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              placeholder={placeholder}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="text-input"
            />
          ) : (
            <input
              type="text"
              value={textValue}
              onChange={(e) => setTextValue(e.target.value)}
              placeholder={placeholder}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              data-testid="text-input"
              onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
            />
          )}
          <button
            onClick={handleTextSubmit}
            disabled={!textValue.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            data-testid="submit-text-btn"
          >
            Submit
          </button>
        </div>
      ) : (
        <div className="flex justify-center py-8">
          <SimpleVoiceRecorder onRecordingComplete={handleVoiceRecording} />
        </div>
      )}
    </div>
  );
};