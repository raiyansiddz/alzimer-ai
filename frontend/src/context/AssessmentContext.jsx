import React, { createContext, useContext, useState, useEffect } from 'react';

const AssessmentContext = createContext();

export const useAssessment = () => {
  const context = useContext(AssessmentContext);
  if (!context) {
    throw new Error('useAssessment must be used within AssessmentProvider');
  }
  return context;
};

export const AssessmentProvider = ({ children }) => {
  const [userId, setUserId] = useState(null);
  const [userName, setUserName] = useState('');
  const [userAge, setUserAge] = useState(null);
  const [locale, setLocale] = useState('en');
  const [currentTest, setCurrentTest] = useState('onboarding');
  const [testResults, setTestResults] = useState({});
  const [interactions, setInteractions] = useState([]);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('assessment_state');
    if (saved) {
      const state = JSON.parse(saved);
      setUserId(state.userId);
      setUserName(state.userName);
      setUserAge(state.userAge);
      setLocale(state.locale);
      setCurrentTest(state.currentTest);
      setTestResults(state.testResults || {});
    }
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    if (userId) {
      localStorage.setItem('assessment_state', JSON.stringify({
        userId,
        userName,
        userAge,
        locale,
        currentTest,
        testResults
      }));
    }
  }, [userId, userName, userAge, locale, currentTest, testResults]);

  const saveTestResult = (testName, result) => {
    setTestResults(prev => ({
      ...prev,
      [testName]: result
    }));
  };

  const trackInteraction = (action, data = {}) => {
    setInteractions(prev => [
      ...prev,
      {
        timestamp: new Date().toISOString(),
        action,
        data,
        test: currentTest
      }
    ]);
  };

  const resetAssessment = () => {
    setUserId(null);
    setUserName('');
    setUserAge(null);
    setCurrentTest('onboarding');
    setTestResults({});
    setInteractions([]);
    localStorage.removeItem('assessment_state');
  };

  const value = {
    userId,
    setUserId,
    userName,
    setUserName,
    userAge,
    setUserAge,
    locale,
    setLocale,
    currentTest,
    setCurrentTest,
    testResults,
    saveTestResult,
    interactions,
    trackInteraction,
    resetAssessment
  };

  return (
    <AssessmentContext.Provider value={value}>
      {children}
    </AssessmentContext.Provider>
  );
};