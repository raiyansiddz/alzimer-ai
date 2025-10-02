import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/api';

// AVLT Test Component for Blind Users
const AVLTTestBlind = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [testConfig, setTestConfig] = useState(null);
  const [currentTrial, setCurrentTrial] = useState(1);
  const [wordsRecalled, setWordsRecalled] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [testResultId, setTestResultId] = useState(null);
  const recognition = useRef(null);
  const speechSynthesis = window.speechSynthesis;

  useEffect(() => {
    initializeTest();
    setupSpeechRecognition();
  }, []);

  const setupSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = true;
      recognition.current.interimResults = true;
      recognition.current.lang = 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        
        // Process recalled words
        const words = transcript.toLowerCase().split(/\s+/).filter(word => word.length > 0);
        setWordsRecalled(words);
      };

      recognition.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        speak("Sorry, I had trouble hearing you. Please try again.");
      };
    }
  };

  const initializeTest = async () => {
    try {
      const response = await api.post('/api/cognitive-tests/blind/avlt/start', {
        user_id: localStorage.getItem('user_id'),
        session_id: sessionId,
        trial_number: currentTrial
      });
      
      setTestConfig(response.data.test_config);
      setTestResultId(response.data.test_result_id);
      
      speak("Welcome to the Auditory Verbal Learning Test. I will read you 15 words. Listen carefully and try to remember them all.");
      
      setTimeout(() => {
        presentWords(response.data.test_config.words_presented);
      }, 3000);
    } catch (error) {
      console.error('Error initializing test:', error);
      speak("Sorry, there was an error starting the test. Please try again.");
    }
  };

  const speak = (message) => {
    if (speechSynthesis) {
      speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 0.8;
      utterance.pitch = 1.0;
      speechSynthesis.speak(utterance);
    }
  };

  const presentWords = async (words) => {
    setIsPlaying(true);
    speak("Here are the words:");
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    for (let i = 0; i < words.length; i++) {
      speak(words[i]);
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    
    setIsPlaying(false);
    speak("Now tell me all the words you can remember. Say 'done' when you're finished.");
    startListening();
  };

  const startListening = () => {
    if (recognition.current) {
      setIsListening(true);
      recognition.current.start();
    }
  };

  const stopListening = () => {
    if (recognition.current) {
      setIsListening(false);
      recognition.current.stop();
    }
  };

  const submitRecall = async () => {
    stopListening();
    
    try {
      const response = await api.post('/api/cognitive-tests/blind/avlt/submit', {
        user_id: localStorage.getItem('user_id'),
        session_id: sessionId,
        words_recalled: wordsRecalled,
        response_times: [], // Would track actual response times
        trial_number: currentTrial
      });
      
      const { score, max_score, next_trial } = response.data;
      speak(`You recalled ${score} out of ${max_score} words correctly.`);
      
      if (next_trial && currentTrial < 5) {
        setTimeout(() => {
          setCurrentTrial(currentTrial + 1);
          setWordsRecalled([]);
          speak(`Let's try trial ${currentTrial + 1}. I'll read the same words again.`);
          setTimeout(() => {
            presentWords(testConfig.words_presented);
          }, 3000);
        }, 3000);
      } else {
        setTimeout(() => {
          speak("Great job! You've completed the Auditory Verbal Learning Test. Moving to the next test.");
          navigate(`/tests/blind/digit-span/${sessionId}`);
        }, 3000);
      }
    } catch (error) {
      console.error('Error submitting recall:', error);
      speak("There was an error processing your response. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6" role="main">
      <div className="max-w-4xl mx-auto text-center">
        <div className="sr-only">
          <h1>Auditory Verbal Learning Test - Trial {currentTrial}</h1>
          <p>Listen to the words and recall as many as you can</p>
        </div>

        {/* Visual Status Indicator */}
        <div className="mb-8">
          <div className={`w-32 h-32 mx-auto mb-6 rounded-full flex items-center justify-center ${
            isPlaying ? 'bg-blue-500 animate-pulse' :
            isListening ? 'bg-red-500 animate-pulse' :
            'bg-gray-600'
          }`}>
            <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              {isPlaying ? (
                <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.82L5.66 14H2a1 1 0 01-1-1V7a1 1 0 011-1h3.66l2.723-2.82a1 1 0 011.617-.104z" clipRule="evenodd" />
              ) : isListening ? (
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              ) : (
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              )}
            </svg>
          </div>
          
          <h2 className="text-3xl font-bold mb-4">Trial {currentTrial} of 5</h2>
          
          <div className="text-xl mb-6">
            {isPlaying && "🔊 Presenting words..."}
            {isListening && "🎤 Listening for your response..."}
            {!isPlaying && !isListening && "Ready"}
          </div>
        </div>

        {/* Words Recalled Display */}
        {wordsRecalled.length > 0 && (
          <div className="mb-8 p-6 bg-gray-800 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Words I heard you say:</h3>
            <div className="flex flex-wrap gap-3 justify-center">
              {wordsRecalled.map((word, index) => (
                <span key={index} className="px-4 py-2 bg-blue-600 rounded-full text-lg">
                  {word}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="space-y-4">
          {!isPlaying && !isListening && (
            <button
              onClick={startListening}
              className="px-8 py-4 bg-green-600 hover:bg-green-700 rounded-lg text-xl font-semibold"
            >
              Start Recalling Words
            </button>
          )}
          
          {isListening && (
            <div className="space-y-4">
              <button
                onClick={submitRecall}
                className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-xl font-semibold mr-4"
              >
                I'm Done - Submit Response
              </button>
              <button
                onClick={stopListening}
                className="px-8 py-4 bg-red-600 hover:bg-red-700 rounded-lg text-xl font-semibold"
              >
                Stop Listening
              </button>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-12 p-6 bg-gray-800 rounded-lg text-left max-w-2xl mx-auto">
          <h3 className="text-lg font-semibold mb-3">Instructions:</h3>
          <ul className="space-y-2 text-gray-300">
            <li>• Listen carefully to all 15 words</li>
            <li>• Try to remember as many as possible</li>
            <li>• Say the words out loud when prompted</li>
            <li>• Words can be in any order</li>
            <li>• Click "I'm Done" when finished</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Digit Span Test Component for Blind Users
const DigitSpanTestBlind = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [testConfig, setTestConfig] = useState(null);
  const [currentSequence, setCurrentSequence] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userResponse, setUserResponse] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isPresenting, setIsPresenting] = useState(false);
  const [testResultId, setTestResultId] = useState(null);
  const [sequences, setSequences] = useState([]);
  const [results, setResults] = useState([]);
  const recognition = useRef(null);

  useEffect(() => {
    initializeTest();
    setupSpeechRecognition();
  }, []);

  const setupSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognition.current = new SpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const numbers = transcript.match(/\d/g) || [];
        setUserResponse(numbers.map(n => parseInt(n)));
      };

      recognition.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        speak("Sorry, I had trouble hearing you. Please try again.");
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  };

  const initializeTest = async () => {
    try {
      const response = await api.post('/api/cognitive-tests/blind/digit-span/start', {
        user_id: localStorage.getItem('user_id'),
        session_id: sessionId,
        direction: 'forward'
      });
      
      setTestConfig(response.data.test_config);
      setTestResultId(response.data.test_result_id);
      setSequences(response.data.test_config.sequences);
      
      speak("Welcome to the Digit Span Test. I will say some numbers. Listen carefully and repeat them back to me in the same order.");
      
      setTimeout(() => {
        startNextSequence(0);
      }, 4000);
    } catch (error) {
      console.error('Error initializing test:', error);
      speak("Sorry, there was an error starting the test.");
    }
  };

  const speak = (message) => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(message);
      utterance.rate = 0.7;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const startNextSequence = (index) => {
    if (index >= sequences.length) {
      finishTest();
      return;
    }

    setCurrentIndex(index);
    setCurrentSequence(sequences[index]);
    setUserResponse([]);
    
    speak(`Sequence ${index + 1}. Listen to these numbers:`);
    setTimeout(() => {
      presentSequence(sequences[index]);
    }, 2000);
  };

  const presentSequence = async (sequence) => {
    setIsPresenting(true);
    
    for (let i = 0; i < sequence.length; i++) {
      speak(sequence[i].toString());
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    setIsPresenting(false);
    speak("Now repeat the numbers back to me in the same order.");
    
    setTimeout(() => {
      startListening();
    }, 1000);
  };

  const startListening = () => {
    if (recognition.current) {
      setIsListening(true);
      recognition.current.start();
    }
  };

  const submitResponse = () => {
    const correct = arraysEqual(userResponse, currentSequence);
    setResults([...results, { sequence: currentSequence, response: userResponse, correct }]);
    
    if (correct) {
      speak(`Correct! The numbers were ${currentSequence.join(', ')}.`);
    } else {
      speak(`Not quite right. The numbers were ${currentSequence.join(', ')}, but you said ${userResponse.join(', ')}.`);
    }
    
    setTimeout(() => {
      startNextSequence(currentIndex + 1);
    }, 3000);
  };

  const arraysEqual = (a, b) => {
    return a.length === b.length && a.every((val, index) => val === b[index]);
  };

  const finishTest = async () => {
    const maxSpan = results.reduce((max, result, index) => {
      return result.correct ? index + 3 : max; // Starting at length 3
    }, 0);
    
    try {
      const response = await api.post('/api/cognitive-tests/blind/digit-span/submit', {
        user_id: localStorage.getItem('user_id'),
        session_id: sessionId,
        sequences_attempted: sequences,
        sequences_correct: results.map(r => r.correct),
        max_span_achieved: maxSpan
      });
      
      speak(`Great job! Your maximum digit span is ${maxSpan} digits. Moving to the next test.`);
      
      setTimeout(() => {
        navigate(`/tests/blind/category-fluency/${sessionId}`);
      }, 4000);
    } catch (error) {
      console.error('Error submitting results:', error);
      speak("There was an error processing your results.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-4xl mx-auto text-center">
        <div className="sr-only">
          <h1>Digit Span Test - Forward Direction</h1>
          <p>Listen to number sequences and repeat them back</p>
        </div>

        {/* Status Display */}
        <div className="mb-8">
          <div className={`w-32 h-32 mx-auto mb-6 rounded-full flex items-center justify-center ${
            isPresenting ? 'bg-blue-500 animate-pulse' :
            isListening ? 'bg-red-500 animate-pulse' :
            'bg-gray-600'
          }`}>
            <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              {isPresenting ? (
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              ) : isListening ? (
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              ) : (
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              )}
            </svg>
          </div>
          
          <h2 className="text-3xl font-bold mb-4">
            Digit Span Test - Sequence {currentIndex + 1} of {sequences.length}
          </h2>
          
          <div className="text-xl mb-6">
            {isPresenting && "🔊 Presenting numbers..."}
            {isListening && "🎤 Listening for your response..."}
            {!isPresenting && !isListening && "Ready"}
          </div>
        </div>

        {/* Current Sequence Display (for reference) */}
        {currentSequence.length > 0 && !isPresenting && (
          <div className="mb-8 p-6 bg-gray-800 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Sequence length: {currentSequence.length}</h3>
            {userResponse.length > 0 && (
              <div>
                <p className="text-lg mb-2">Your response:</p>
                <div className="text-2xl font-mono">
                  {userResponse.join(' - ')}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Control Buttons */}
        <div className="space-y-4">
          {!isPresenting && !isListening && userResponse.length === 0 && (
            <div className="text-lg text-gray-300">
              Listen for the number sequence...
            </div>
          )}
          
          {!isPresenting && !isListening && userResponse.length > 0 && (
            <button
              onClick={submitResponse}
              className="px-8 py-4 bg-green-600 hover:bg-green-700 rounded-lg text-xl font-semibold"
            >
              Submit Response
            </button>
          )}

          {isListening && (
            <div className="text-lg text-blue-300 animate-pulse">
              Say the numbers you heard...
            </div>
          )}
        </div>

        {/* Progress */}
        <div className="mt-12">
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300" 
              style={{ width: `${((currentIndex) / sequences.length) * 100}%` }}
            ></div>
          </div>
          <p className="mt-2 text-gray-400">
            Progress: {currentIndex} of {sequences.length} sequences
          </p>
        </div>

        {/* Instructions */}
        <div className="mt-12 p-6 bg-gray-800 rounded-lg text-left max-w-2xl mx-auto">
          <h3 className="text-lg font-semibold mb-3">Instructions:</h3>
          <ul className="space-y-2 text-gray-300">
            <li>• Listen carefully to each sequence of numbers</li>
            <li>• Repeat them back in the same order you heard them</li>
            <li>• Speak clearly and at a normal pace</li>
            <li>• The sequences will get longer as you progress</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export { AVLTTestBlind, DigitSpanTestBlind };