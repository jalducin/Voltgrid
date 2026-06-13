import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, Org } from './types';

// Estado global de sesión y whitelabel. Persistido en localStorage.
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  org: Org | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: User | null) => void;
  setOrg: (org: Org | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      org: null,
      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),
      setUser: (user) => set({ user }),
      setOrg: (org) => set({ org }),
      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          org: null,
        }),
    }),
    {
      name: 'voltgrid-auth',
      storage: createJSONStorage(() =>
        typeof window !== 'undefined'
          ? window.localStorage
          : // Storage neutro en SSR para evitar acceso a window.
            {
              getItem: () => null,
              setItem: () => undefined,
              removeItem: () => undefined,
            },
      ),
    },
  ),
);

// Accesos directos para uso fuera de componentes React (ej. interceptores Axios).
export const getAccessToken = (): string | null =>
  useAuthStore.getState().accessToken;

export const getRefreshToken = (): string | null =>
  useAuthStore.getState().refreshToken;
