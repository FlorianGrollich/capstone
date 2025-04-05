import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import store from '../store';
import {logout, selectToken} from '../features/Auth/slices/authState';

const API_URL = 'http://localhost:8000/api';

const axiosClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

axiosClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = selectToken(store.getState().authState);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

axiosClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.log('Unauthorized, redirecting to login');
      store.dispatch(logout());
    }

    return Promise.reject(error);
  }
);

export default axiosClient;