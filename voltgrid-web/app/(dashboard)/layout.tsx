'use client';

import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/store';
import { loadSession, logout, applyTheme } from '@/lib/auth';
import { Button } from '@/components/ui';

interface NavItem {
  href: string;
  label: string;
  adminOnly?: boolean;
}

const navItems: NavItem[] = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/analytics', label: 'Analytics' },
  { href: '/scheduler', label: 'Scheduler', adminOnly: true },
  { href: '/settings', label: 'Ajustes', adminOnly: true },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const accessToken = useAuthStore((s) => s.accessToken);
  const user = useAuthStore((s) => s.user);
  const org = useAuthStore((s) => s.org);
  const [ready, setReady] = useState(false);

  // Guard: sin token redirigimos al login. Con token, aseguramos sesión + tema.
  useEffect(() => {
    if (!accessToken) {
      router.replace('/login');
      return;
    }
    if (user && org) {
      applyTheme(org.primary_color);
      setReady(true);
      return;
    }
    loadSession()
      .then(({ org: loadedOrg }) => {
        applyTheme(loadedOrg.primary_color);
        setReady(true);
      })
      .catch(() => {
        router.replace('/login');
      });
  }, [accessToken, user, org, router]);

  async function handleLogout() {
    await logout();
    router.replace('/login');
  }

  if (!accessToken || !ready) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Cargando…</p>
      </main>
    );
  }

  const isAdmin = user?.role === 'org_admin' || user?.role === 'superadmin';
  const visibleItems = navItems.filter((item) => !item.adminOnly || isAdmin);

  return (
    <div className="flex min-h-screen">
      {/* Barra lateral con identidad del tenant (whitelabel). */}
      <aside className="hidden w-64 flex-col border-r border-gray-200 bg-white md:flex">
        <div className="flex items-center gap-3 border-b border-gray-200 px-5 py-4">
          {org?.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={org.logo_url}
              alt={org.name}
              className="h-8 w-8 rounded object-contain"
            />
          ) : (
            <div className="flex h-8 w-8 items-center justify-center rounded bg-[var(--primary)] text-sm font-bold text-white">
              {(org?.name ?? 'V').charAt(0)}
            </div>
          )}
          <span className="font-semibold text-gray-900">
            {org?.name ?? 'VoltGrid'}
          </span>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {visibleItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-md px-3 py-2 text-sm font-medium ${
                  active
                    ? 'bg-[var(--primary)] text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-gray-200 px-3 py-4">
          <p className="mb-2 truncate px-3 text-xs text-gray-500">
            {user?.email}
          </p>
          <Button variant="ghost" className="w-full" onClick={handleLogout}>
            Cerrar sesión
          </Button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        {/* Barra superior para navegación móvil. */}
        <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 md:hidden">
          <span className="font-semibold text-gray-900">
            {org?.name ?? 'VoltGrid'}
          </span>
          <Button variant="ghost" onClick={handleLogout}>
            Salir
          </Button>
        </header>

        {/* Navegación móvil horizontal. */}
        <nav className="flex gap-1 overflow-x-auto border-b border-gray-200 bg-white px-2 py-2 md:hidden">
          {visibleItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium ${
                  active
                    ? 'bg-[var(--primary)] text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <main className="flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
