'use client';

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { Station } from '@/lib/types';

// Gráfica de barras de la capacidad (max_kw) por estación.
export function StationChart({ stations }: { stations: Station[] }) {
  const data = stations.map((s) => ({ name: s.name, max_kw: s.max_kw }));

  if (data.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500">
        No hay estaciones para graficar.
      </p>
    );
  }

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} unit=" kW" width={56} />
          <Tooltip formatter={(value: number) => [`${value} kW`, 'Capacidad']} />
          <Bar dataKey="max_kw" fill="var(--primary)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
