import axios from 'axios';

type ClientMeta = {
  client: string;
  timestamp: number;
  [key: string]: any;
};

const DEFAULT_BASE_URL = import.meta.env.VITE_ENGRAM_API_URL || 'http://localhost:8000/api/v1';

export const getBaseUrl = () => {
  return localStorage.getItem('engram_base_url') || DEFAULT_BASE_URL;
};

export const setBaseUrl = (url: string) => {
  localStorage.setItem('engram_base_url', url);
};

const buildClient = () => {
  const client = axios.create({ baseURL: getBaseUrl() });
  const token = localStorage.getItem('engram_token') || localStorage.getItem('engram_eat');
  if (token) {
    client.defaults.headers.Authorization = `Bearer ${token}`;
  }
  return client;
};

export const auth = {
  login: async (email: string, password: string) => {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    const response = await buildClient().post('/auth/login', params);
    localStorage.setItem('engram_token', response.data.access_token);
    return response.data;
  },
  signup: async (data: any) => {
    const response = await buildClient().post('/auth/signup', data);
    return response.data;
  },
  generateEat: async () => {
    const response = await buildClient().post('/auth/tokens/generate-eat');
    localStorage.setItem('engram_eat', response.data.eat);
    return response.data.eat;
  },
};

export const tasks = {
  submit: async (command: string, metadata?: ClientMeta) => {
    const eat = localStorage.getItem('engram_eat');
    if (!eat) throw new Error('Missing EAT. Please generate one first.');
    const response = await buildClient().post(
      '/tasks/submit',
      { command, metadata },
      { headers: { Authorization: `Bearer ${eat}` } }
    );
    return response.data;
  },
  get: async (taskId: string) => {
    const response = await buildClient().get(`/tasks/${taskId}`);
    return response.data;
  },
  list: async (limit = 10) => {
    const response = await buildClient().get('/tasks', { params: { limit } });
    return response.data;
  },
};

export const discovery = {
  getAgents: async () => {
    const response = await buildClient().get('/discover');
    return response.data;
  },
};

export default buildClient;
