'use client';

import { useEffect, useState, type FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Button, Card, Input, Label } from '@/components/ui';
import type { SchedulerConfig } from '@/lib/types';

export default function SchedulerPage() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const isAdmin = user?.role === 'org_admin' || user?.role === 'superadmin';

  const [config, setConfig] = useState<SchedulerConfig>({
    enabled: false,
    interval_minutes: 15,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Solo org_admin: si no lo es, regresamos al dashboard.
  useEffect(() => {
    if (user && !isAdmin) {
      router.replace('/dashboard');
    }
  }, [user, isAdmin, router]);

  useEffect(() => {
    if (!isAdmin) return;
    api
      .get<SchedulerConfig>('/scheduler/config')
      .then(({ data }) => setConfig(data))
      .catch(() => setError('No se pudo cargar la configuración.'))
      .finally(() => setLoading(false));
  }, [isAdmin]);

  async function handleSave(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      await api.put('/scheduler/config', config);
      setMessage('Configuración guardada.');
    } catch {
      setError('No se pudo guardar la configuración.');
    } finally {
      setSaving(false);
    }
  }

  async function handleRunNow() {
    setRunning(true);
    setMessage(null);
    setError(null);
    try {
      await api.post('/scheduler/run-now');
      setMessage('Ejecución iniciada.');
    } catch {
      setError('No se pudo iniciar la ejecución.');
    } finally {
      setRunning(false);
    }
  }

  if (!isAdmin) return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Scheduler</h1>

      <Card className="max-w-lg">
        {loading ? (
          <p className="text-gray-500">Cargando…</p>
        ) : (
          <form onSubmit={handleSave} className="space-y-4">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={config.enabled}
                onChange={(e) =>
                  setConfig({ ...config, enabled: e.target.checked })
                }
                className="h-4 w-4 accent-[var(--primary)]"
              />
              <span className="text-sm font-medium text-gray-700">
                Habilitar ejecución programada
              </span>
            </label>

            <div>
              <Label htmlFor="interval">Intervalo (minutos)</Label>
              <Input
                id="interval"
                type="number"
                min={1}
                value={config.interval_minutes}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    interval_minutes: Number(e.target.value),
                  })
                }
                required
              />
            </div>

            {message && <p className="text-sm text-green-600">{message}</p>}
            {error && <p className="text-sm text-red-600">{error}</p>}

            <div className="flex gap-3">
              <Button type="submit" disabled={saving}>
                {saving ? 'Guardando…' : 'Guardar'}
              </Button>
              <Button
                type="button"
                variant="secondary"
                onClick={handleRunNow}
                disabled={running}
              >
                {running ? 'Ejecutando…' : 'Ejecutar ahora'}
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
