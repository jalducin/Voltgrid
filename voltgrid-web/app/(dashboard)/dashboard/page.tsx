'use client';

import { useCallback, useEffect, useState, type FormEvent } from 'react';
import api from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { Button, Card, Input, Label, Select, statusLabels } from '@/components/ui';
import { StationCard } from '@/components/StationCard';
import { StationChart } from '@/components/StationChart';
import type { Station, StationStatus, StationCreate } from '@/lib/types';

const STATUSES: StationStatus[] = [
  'available',
  'occupied',
  'offline',
  'maintenance',
];

const emptyForm: StationCreate = {
  name: '',
  location: '',
  max_kw: 50,
  lat: null,
  lng: null,
};

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const canEdit =
    user?.role === 'operator' ||
    user?.role === 'org_admin' ||
    user?.role === 'superadmin';

  const [stations, setStations] = useState<Station[]>([]);
  const [statusFilter, setStatusFilter] = useState<StationStatus | ''>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<StationCreate>(emptyForm);
  const [creating, setCreating] = useState(false);

  // Carga estaciones desde el backend aplicando el filtro de estado.
  const fetchStations = useCallback(async () => {
    try {
      const { data } = await api.get<Station[]>('/stations', {
        params: statusFilter ? { status: statusFilter } : undefined,
      });
      setStations(data);
      setError(null);
    } catch {
      setError('No se pudieron cargar las estaciones.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  // El filtro de estado dispara una nueva petición al backend.
  useEffect(() => {
    setLoading(true);
    fetchStations();
  }, [fetchStations]);

  // Fallback a sondeo cada 10 s (el estado en vivo lo maneja cada tarjeta por WS).
  useEffect(() => {
    const id = setInterval(fetchStations, 10000);
    return () => clearInterval(id);
  }, [fetchStations]);

  async function handleChangeStatus(id: string, status: StationStatus) {
    await api.patch(`/stations/${id}/status`, { new_status: status });
    setStations((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status } : s)),
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreating(true);
    try {
      await api.post<Station>('/stations', form);
      setForm(emptyForm);
      await fetchStations();
    } catch {
      setError('No se pudo crear la estación.');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Estaciones</h1>
        <div className="w-48">
          <Select
            value={statusFilter}
            onChange={(e) =>
              setStatusFilter(e.target.value as StationStatus | '')
            }
            aria-label="Filtrar por estado"
          >
            <option value="">Todos los estados</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {statusLabels[s]}
              </option>
            ))}
          </Select>
        </div>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Formulario de alta (operator+). */}
      {canEdit && (
        <Card>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">
            Nueva estación
          </h2>
          <form
            onSubmit={handleCreate}
            className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
          >
            <div>
              <Label htmlFor="name">Nombre</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>
            <div>
              <Label htmlFor="location">Ubicación</Label>
              <Input
                id="location"
                value={form.location}
                onChange={(e) =>
                  setForm({ ...form, location: e.target.value })
                }
                required
              />
            </div>
            <div>
              <Label htmlFor="max_kw">Capacidad (kW)</Label>
              <Input
                id="max_kw"
                type="number"
                min={1}
                value={form.max_kw}
                onChange={(e) =>
                  setForm({ ...form, max_kw: Number(e.target.value) })
                }
                required
              />
            </div>
            <div className="flex items-end">
              <Button type="submit" className="w-full" disabled={creating}>
                {creating ? 'Creando…' : 'Crear estación'}
              </Button>
            </div>
          </form>
        </Card>
      )}

      {/* Gráfica de capacidad. */}
      <Card>
        <h2 className="mb-2 text-lg font-semibold text-gray-900">
          Capacidad por estación
        </h2>
        <StationChart stations={stations} />
      </Card>

      {/* Listado de estaciones. */}
      {loading ? (
        <p className="text-gray-500">Cargando estaciones…</p>
      ) : stations.length === 0 ? (
        <p className="text-gray-500">No hay estaciones que coincidan.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {stations.map((station) => (
            <StationCard
              key={station.id}
              station={station}
              canEdit={canEdit}
              onChangeStatus={handleChangeStatus}
            />
          ))}
        </div>
      )}
    </div>
  );
}
