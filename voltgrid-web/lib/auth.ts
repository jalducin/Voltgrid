import api from './api';
import { useAuthStore } from './store';
import type { User, Org } from './types';

// Carga el usuario actual y su organización (whitelabel) y los guarda en el store.
export async function loadSession(): Promise<{ user: User; org: Org }> {
  const [meRes, orgRes] = await Promise.all([
    api.get<User>('/auth/me'),
    api.get<Org>('/orgs/me'),
  ]);
  useAuthStore.getState().setUser(meRes.data);
  useAuthStore.getState().setOrg(orgRes.data);
  return { user: meRes.data, org: orgRes.data };
}

// Cierra la sesión llamando al backend y limpiando el store.
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout');
  } catch {
    // Aunque falle en el servidor, limpiamos localmente.
  }
  useAuthStore.getState().logout();
}

// Aplica el color primario del whitelabel como variable CSS.
export function applyTheme(primaryColor: string | null | undefined): void {
  if (typeof document === 'undefined') return;
  const color = primaryColor || '#16a34a';
  document.documentElement.style.setProperty('--primary', color);
}
