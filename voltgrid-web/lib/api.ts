import axios, {
  AxiosError,
  AxiosHeaders,
  type InternalAxiosRequestConfig,
} from 'axios';
import { useAuthStore, getAccessToken, getRefreshToken } from './store';
import type { AuthTokens } from './types';

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Marca interna para evitar reintentar el refresh más de una vez por petición.
interface RetriableConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Adjunta el Bearer en cada petición.
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    const headers = AxiosHeaders.from(config.headers);
    headers.set('Authorization', `Bearer ${token}`);
    config.headers = headers;
  }
  return config;
});

// Cierra la sesión y redirige al login.
function forceLogout(): void {
  useAuthStore.getState().logout();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

// Ante un 401 intenta refrescar el token UNA sola vez y reintenta la petición.
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      // No intentamos refrescar el propio endpoint de refresh.
      !original.url?.includes('/auth/refresh')
    ) {
      original._retry = true;
      const refreshToken = getRefreshToken();

      if (!refreshToken) {
        forceLogout();
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post<AuthTokens>(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken },
        );
        useAuthStore
          .getState()
          .setTokens(data.access_token, data.refresh_token);

        const headers = AxiosHeaders.from(original.headers);
        headers.set('Authorization', `Bearer ${data.access_token}`);
        original.headers = headers;
        return api(original);
      } catch (refreshError) {
        forceLogout();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  },
);

export default api;
