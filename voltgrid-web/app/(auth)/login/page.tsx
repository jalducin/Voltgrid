'use client';

import { useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import api, { API_BASE_URL } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { loadSession, applyTheme } from '@/lib/auth';
import { Button, Input, Label, Card } from '@/components/ui';
import type { AuthTokens } from '@/lib/types';

export default function LoginPage() {
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      // El endpoint de login espera x-www-form-urlencoded.
      const body = new URLSearchParams();
      body.append('username', email);
      body.append('password', password);

      const { data } = await api.post<AuthTokens>('/auth/login', body, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      setTokens(data.access_token, data.refresh_token);

      const { org } = await loadSession();
      applyTheme(org.primary_color);
      router.replace('/dashboard');
    } catch {
      setError('Credenciales inválidas. Verifica tu correo y contraseña.');
    } finally {
      setLoading(false);
    }
  }

  // Navega al flujo SSO del proveedor seleccionado.
  function handleSso(provider: 'google' | 'microsoft') {
    window.location.href = `${API_BASE_URL}/auth/sso/${provider}/login`;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gray-900">VoltGrid</h1>
          <p className="mt-1 text-sm text-gray-500">
            Inicia sesión para gestionar tus estaciones
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="email">Correo electrónico</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@correo.com"
              autoComplete="email"
              required
            />
          </div>
          <div>
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? 'Entrando…' : 'Entrar'}
          </Button>
        </form>

        <div className="my-5 flex items-center gap-3">
          <span className="h-px flex-1 bg-gray-200" />
          <span className="text-xs text-gray-400">o continúa con</span>
          <span className="h-px flex-1 bg-gray-200" />
        </div>

        <div className="space-y-2">
          <Button
            type="button"
            variant="secondary"
            className="w-full"
            onClick={() => handleSso('google')}
          >
            Entrar con Google
          </Button>
          <Button
            type="button"
            variant="secondary"
            className="w-full"
            onClick={() => handleSso('microsoft')}
          >
            Entrar con Microsoft
          </Button>
        </div>
      </Card>
    </main>
  );
}
