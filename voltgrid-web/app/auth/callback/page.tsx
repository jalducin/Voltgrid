'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { loadSession, applyTheme } from '@/lib/auth';

// Recibe los tokens del SSO en el hash de la URL, los guarda y redirige.
export default function AuthCallbackPage() {
  const router = useRouter();
  const setTokens = useAuthStore((s) => s.setTokens);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const hash = window.location.hash.startsWith('#')
      ? window.location.hash.slice(1)
      : window.location.hash;
    const params = new URLSearchParams(hash);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');

    if (!accessToken || !refreshToken) {
      setError('No se recibieron los tokens de autenticación.');
      return;
    }

    setTokens(accessToken, refreshToken);

    loadSession()
      .then(({ org }) => {
        applyTheme(org.primary_color);
        router.replace('/dashboard');
      })
      .catch(() => {
        setError('No se pudo cargar la sesión. Intenta de nuevo.');
      });
  }, [router, setTokens]);

  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      {error ? (
        <div className="text-center">
          <p className="text-red-600">{error}</p>
          <a href="/login" className="mt-2 inline-block text-sm text-[var(--primary)] underline">
            Volver al inicio de sesión
          </a>
        </div>
      ) : (
        <p className="text-gray-500">Procesando inicio de sesión…</p>
      )}
    </main>
  );
}
