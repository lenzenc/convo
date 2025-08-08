import axios, { AxiosResponse } from 'axios';
import {
  ViewInfo,
  QueryResponse,
  HealthStatus,
} from '@/types';

const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000' 
  : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.data) {
      throw new Error(error.response.data.error || error.response.data.detail || 'API Error');
    }
    throw new Error(error.message || 'Network Error');
  }
);

export class ApiService {
  static async getHealth(): Promise<HealthStatus> {
    const response = await api.get<HealthStatus>('/health');
    return response.data;
  }

  static async getViews(): Promise<ViewInfo[]> {
    const response = await api.get<ViewInfo[]>('/views');
    return response.data;
  }

  static async getViewDetails(viewName: string): Promise<ViewInfo> {
    const response = await api.get<ViewInfo>(`/views/${viewName}`);
    return response.data;
  }

  static async executeView<T = any>(
    viewName: string,
    params?: { limit?: number }
  ): Promise<QueryResponse<T>> {
    const response = await api.get<QueryResponse<T>>(
      `/views/${viewName}/execute`,
      { params }
    );
    return response.data;
  }

  static async query<T = any>(
    question: string,
    options?: { debug?: boolean }
  ): Promise<QueryResponse<T>> {
    const response = await api.get<QueryResponse<T>>('/query', {
      params: { q: question, debug: options?.debug },
    });
    return response.data;
  }

  static async postQuery<T = any>(
    question: string,
    options?: { debug?: boolean }
  ): Promise<QueryResponse<T>> {
    const response = await api.post<QueryResponse<T>>('/query', {
      question,
      debug: options?.debug,
    });
    return response.data;
  }
}

export default ApiService;