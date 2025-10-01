import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/v1`;

export const api = {
  // Registration
  registerUser: async (userData) => {
    const response = await axios.post(`${API}/registration`, userData);
    return response.data;
  },

  getUser: async (userId) => {
    const response = await axios.get(`${API}/user/${userId}`);
    return response.data;
  },

  // Memory Test
  submitMemoryTest: async (formData) => {
    const response = await axios.post(`${API}/memory`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Pattern Test
  submitPatternTest: async (data) => {
    const response = await axios.post(`${API}/pattern`, data);
    return response.data;
  },

  // Clock Test
  submitClockTest: async (data) => {
    const response = await axios.post(`${API}/clock`, data);
    return response.data;
  },

  // Speech Test
  submitSpeechTest: async (formData) => {
    const response = await axios.post(`${API}/speech`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Behavioral
  submitBehavioral: async (data) => {
    const response = await axios.post(`${API}/behavioral`, data);
    return response.data;
  },

  // Reports
  generateReport: async (data) => {
    const response = await axios.post(`${API}/report`, data);
    return response.data;
  },

  getReports: async (userId) => {
    const response = await axios.get(`${API}/report/${userId}`);
    return response.data;
  }
};

export default api;