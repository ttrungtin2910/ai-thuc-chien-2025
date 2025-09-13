import axios from 'axios';
import Cookies from 'js-cookie';

// Tạo axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor để thêm token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor để xử lý lỗi
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token hết hạn, redirect về login
      Cookies.remove('access_token');
      Cookies.remove('user_info');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
  
  logout: () => {
    Cookies.remove('access_token');
    Cookies.remove('user_info');
  }
};

// Documents API
export const documentsAPI = {
  getDocuments: async () => {
    const response = await api.get('/api/documents');
    return response.data;
  },
  
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  bulkUploadDocuments: async (formData) => {
    const response = await api.post('/api/documents/bulk-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/api/documents/${documentId}`);
    return response.data;
  }
};

// Chatbot API - Enhanced for Virtual Assistant
export const chatbotAPI = {
  sendMessage: async (messageData) => {
    // Support both old string format and new object format
    const payload = typeof messageData === 'string' 
      ? { message: messageData }
      : messageData;
    
    const response = await api.post('/api/chatbot/message', payload);
    return response.data;
  },

  getSessionInfo: async (sessionId) => {
    const response = await api.get(`/api/chatbot/session/${sessionId}`);
    return response.data;
  },

  getChatHistory: async (sessionId, limit = 20) => {
    const response = await api.get(`/api/chatbot/history/${sessionId}?limit=${limit}`);
    return response.data;
  },

  createNewSession: async () => {
    const response = await api.post('/api/chatbot/session/new');
    return response.data;
  },

  deleteSession: async (sessionId) => {
    const response = await api.delete(`/api/chatbot/session/${sessionId}`);
    return response.data;
  },

  getUserSessions: async () => {
    const response = await api.get('/api/chatbot/sessions');
    return response.data;
  },

  getChatbotStatus: async () => {
    const response = await api.get('/api/chatbot/status');
    return response.data;
  },

  cleanupOldSessions: async () => {
    const response = await api.post('/api/chatbot/cleanup');
    return response.data;
  }
};

export default api;
