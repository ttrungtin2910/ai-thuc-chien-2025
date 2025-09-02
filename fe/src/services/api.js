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

// Chatbot API
export const chatbotAPI = {
  sendMessage: async (message) => {
    const response = await api.post('/api/chatbot/message', { message });
    return response.data;
  }
};

export default api;
