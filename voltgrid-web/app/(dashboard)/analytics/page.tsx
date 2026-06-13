'use client';

import { useCallback, useEffect, useState } from 'react';
import api, { API_BASE_URL } from '@/lib/api';
import { getAccessToken } from '@/lib/store';
import {
  Button,
  Card,
  Input,
  Label,
  Select,
  StatCard,
  statusLabels,
} from '@/components/ui';
import type {
  AnalyticsFilters,
  KPISummary,
  StationStatus,
} from '@/lib/types';

const STATUSES: StationStatus[] = [
  'available',
  'occupied',
  'offline',
  'maintenance',
];

const emptyFilters: AnalyticsFilters = {
  date_from: '',
  date_to: '',
  location: '',
  min_capacity: '',
  max_capacity: '',
  status: '',
};

// Construye los query params descartando valores vacíos.
function buildParams(filters: AnalyticsFilters): Record<string, string> {
  const params: Record<string, string> = {};
  (Object.keys(filters) as Array<keyof AnalyticsFilters>).forEach((key) => {
    const value = filters[key];
    if (value) params[key] = value;
  });
  return params;
}

export default function AnalyticsPage() {
  const [filters, setFilters] = useState<AnalyticsFilters>(emptyFilters);
  const [data, setData] = useState<KPISummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // Cada cambio de filtro dispara una petición al backend (no filtrado en cliente).
  const fetchKpis = useCallback(async () => {
    setLoading(true);
    try {
      const { data: kpis } = await api.get<KPISummary>('/analytics/kpis', {
        params: buildParams(filters),
      });
      setData(kpis);
      setError(null);
    } catch {
      setError('No se pudieron cargar los indicadores.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchKpis();
  }, [fetchKpis]);

  function update(key: keyof AnalyticsFilters, value: string) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  // Descarga el CSV usando fetch con Bearer y blob para forzar la descarga.
  async function handleExport() {
    setExporting(true);
    try {
      const query = new URLSearchParams(buildParams(filters)).toString();
      const url = `${API_BASE_URL}/analytics/export.csv${query ? `?${query}` : ''}`;
      const token = getAccessToken();
      const res = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      if (!res.ok) throw new Error('export failed');
      const blob = await res.blob();
      const link = document.createElement('a');
      const objectUrl = URL.createObjectURL(blob);
      link.href = objectUrl;
      link.download = 'analytics.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(objectUrl);
    } catch {
      setError('No se pudo exportar el CSV.');
    } finally {
      setExporting(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <Button variant="secondary" onClick={handleExport} disabled={exporting}>
          {exporting ? 'Exportando…' : 'Exportar CSV'}
        </Button>
      </div>

      {/* Filtros. */}
      <Card>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <Label htmlFor="date_from">Desde</Label>
            <Input
              id="date_from"
              type="date"
              value={filters.date_from}
              onChange={(e) => update('date_from', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="date_to">Hasta</Label>
            <Input
              id="date_to"
              type="date"
              value={filters.date_to}
              onChange={(e) => update('date_to', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="location">Ubicación</Label>
            <Input
              id="location"
              value={filters.location}
              onChange={(e) => update('location', e.target.value)}
              placeholder="Ciudad, zona…"
            />
          </div>
          <div>
            <Label htmlFor="min_capacity">Capacidad mín. (kW)</Label>
            <Input
              id="min_capacity"
              type="number"
              value={filters.min_capacity}
              onChange={(e) => update('min_capacity', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="max_capacity">Capacidad máx. (kW)</Label>
            <Input
              id="max_capacity"
              type="number"
              value={filters.max_capacity}
              onChange={(e) => update('max_capacity', e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="status">Estado</Label>
            <Select
              id="status"
              value={filters.status}
              onChange={(e) => update('status', e.target.value)}
            >
              <option value="">Todos</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {statusLabels[s]}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </Card>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {/* Tarjetas de KPI. */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Total de estaciones"
          value={data?.total_stations ?? '—'}
        />
        <StatCard
          label="kWh entregados"
          value={data ? data.total_kwh.toLocaleString('es-MX') : '—'}
        />
        <StatCard
          label="Sesiones activas"
          value={data?.active_sessions ?? '—'}
        />
        <StatCard
          label="Uptime promedio"
          value={data ? `${data.avg_uptime_pct.toFixed(1)}%` : '—'}
        />
      </div>

      {/* Tabla por estación. */}
      <Card className="overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="border-b border-gray-200 bg-gray-50 text-left text-gray-600">
            <tr>
              <th className="px-4 py-3 font-medium">Estación</th>
              <th className="px-4 py-3 font-medium">Uptime</th>
              <th className="px-4 py-3 font-medium">kWh entregados</th>
              <th className="px-4 py-3 font-medium">Sesiones activas</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {loading ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                  Cargando…
                </td>
              </tr>
            ) : !data || data.stations.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                  Sin datos para los filtros seleccionados.
                </td>
              </tr>
            ) : (
              data.stations.map((s) => (
                <tr key={s.station_id} className="text-gray-800">
                  <td className="px-4 py-3">{s.name}</td>
                  <td className="px-4 py-3">{s.uptime_pct.toFixed(1)}%</td>
                  <td className="px-4 py-3">
                    {s.kwh_delivered.toLocaleString('es-MX')}
                  </td>
                  <td className="px-4 py-3">{s.active_sessions}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
