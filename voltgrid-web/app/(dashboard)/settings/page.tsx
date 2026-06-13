'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { applyTheme } from '@/lib/auth';
import { Button, Card, Input, Label } from '@/components/ui';
import type { Org, OrgUpdate } from '@/lib/types';

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const org = useAuthStore((s) => s.org);
  const setOrg = useAuthStore((s) => s.setOrg);
  const isAdmin = user?.role === 'org_admin' || user?.role === 'superadmin';

  const [form, setForm] = useState<OrgUpdate>({
    name: '',
    logo_url: '',
    primary_color: '#16a34a',
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Solo org_admin.
  useEffect(() => {
    if (user && !isAdmin) {
      router.replace('/dashboard');
    }
  }, [user, isAdmin, router]);

  // Precargamos el formulario con los datos actuales de la organización.
  useEffect(() => {
    if (org) {
      setForm({
        name: org.name ?? '',
        logo_url: org.logo_url ?? '',
        primary_color: org.primary_color ?? '#16a34a',
      });
    }
  }, [org]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const { data } = await api.patch<Org>('/orgs/me', form);
      setOrg(data);
      applyTheme(data.primary_color);
      setMessage('Cambios guardados.');
    } catch {
      setError('No se pudieron guardar los cambios.');
    } finally {
      setSaving(false);
    }
  }

  if (!isAdmin) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Ajustes</h1>

      <Card className="max-w-lg">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">
          Personalización (whitelabel)
        </h2>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <Label htmlFor="name">Nombre de la organización</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </div>
          <div>
            <Label htmlFor="logo_url">URL del logo</Label>
            <Input
              id="logo_url"
              type="url"
              value={form.logo_url}
              onChange={(e) => setForm({ ...form, logo_url: e.target.value })}
              placeholder="https://…"
            />
          </div>
          <div>
            <Label htmlFor="primary_color">Color primario</Label>
            <div className="flex items-center gap-3">
              <input
                id="primary_color"
                type="color"
                value={form.primary_color}
                onChange={(e) =>
                  setForm({ ...form, primary_color: e.target.value })
                }
                className="h-10 w-14 cursor-pointer rounded border border-gray-300"
              />
              <Input
                value={form.primary_color}
                onChange={(e) =>
                  setForm({ ...form, primary_color: e.target.value })
                }
                className="max-w-[10rem]"
              />
            </div>
          </div>

          {message && <p className="text-sm text-green-600">{message}</p>}
          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={saving}>
            {saving ? 'Guardando…' : 'Guardar cambios'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
