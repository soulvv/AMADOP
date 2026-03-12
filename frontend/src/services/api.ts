import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost';

export const authAPI = axios.create({
  baseURL: `${API_BASE_URL}:8001`,
});

export const postAPI = axios.create({
  baseURL: `${API_BASE_URL}:8002`,
});

export const commentAPI = axios.create({
  baseURL: `${API_BASE_URL}:8003`,
});

export const notificationAPI = axios.create({
  baseURL: `${API_BASE_URL}:8004`,
});

// Add token to requests
const addAuthToken = (config: any) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

postAPI.interceptors.request.use(addAuthToken);
commentAPI.interceptors.request.use(addAuthToken);
notificationAPI.interceptors.request.use(addAuthToken);
