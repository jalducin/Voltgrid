'use client';

import { useState } from 'react';
import { useWebSocket } from '@/lib/useWebSocket';
import { Card, Select, StatusBadge, statusLabels } from '@/components/ui';
import type { Station, StationStatus } from '@/lib/types';

const STATUSES: StationStatus[] = [
  'available',
  'occupied',
  'offline',
  'maintenance',
];

interface StationCardProps {
  station: Station;
  canEdit: boolean;
  onChangeStatus: (id: string, status: StationStatus) => Promise<void>;
}

// Tarjeta de estación con estado en vivo (WebSocket) y selector de estado.
export function StationCard({
  station,
  canEdit,
  onChangeStatus,
}: StationCardProps) {
  const [status, setStatus] = useState<StationStatus>(station.status);
  const [saving, setSaving] = useState(false);

  // Actualización en vivo del estado vía WebSocket.
  const wsState = useWebSocket(station.id, (msg) => {
    if (msg.station_id === station.id) {
      setStatus(msg.status);
    }
  });

  async function handleSelect(next: StationStatus) {
    const previous = status;
    setStatus(next);
    setSaving(true);
    try {
      await onChangeStatus(station.id, next);
    } catch {
      // Revertimos si falla.
      setStatus(previous);
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-gray-900">{station.name}</h3>
          <p className="text-sm text-gray-500">{station.location}</p>
        </div>
        <StatusBadge status={status} />
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>{station.max_kw} kW</span>
        <span
          className={`text-xs ${
            wsState === 'open' ? 'text-green-600' : 'text-gray-400'
          }`}
          title={wsState === 'open' ? 'En vivo' : 'Sin conexión en vivo'}
        >
          {wsState === 'open' ? '● En vivo' : '○ Sondeo'}
        </span>
      </div>

      {canEdit && (
        <Select
          value={status}
          disabled={saving}
          onChange={(e) => handleSelect(e.target.value as StationStatus)}
          aria-label={`Cambiar estado de ${station.name}`}
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {statusLabels[s]}
            </option>
          ))}
        </Select>
      )}
    </Card>
  );
}
