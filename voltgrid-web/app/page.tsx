'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

// Redirige a /dashboard o /login según exista un token de acceso.
export default function HomePage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);

  useEffect(() => {
    router.replace(accessToken ? '/dashboard' : '/login');
  }, [accessToken, router]);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-gray-500">Cargando…</p>
    </main>
  );
}
