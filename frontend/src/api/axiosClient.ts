import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

const API_URL = 'http://localhost:8000';

const axiosClient: AxiosInstance = axios.create({
  baseURL: API_URL,
});

axiosClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  if (!config.headers['Content-Type'] && !(config.data instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  }

  return config;
});

axiosClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log('Unauthorized, redirecting to login');
      localStorage.removeItem('token');
    }

    return Promise.reject(error);
  }
);

export default axiosClient;