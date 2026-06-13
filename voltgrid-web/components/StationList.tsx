// components/StationList.tsx
import React from 'react'

interface Station {
  id: number
  name: string
  location: string
  max_kw: number
  status: string
}

interface StationListProps {
  stations: Station[]
  onStatusChange: (id: number, status: string) => void
}

export default function StationList({
  stations,
  onStatusChange
}: StationListProps) {
  return (
    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      {stations.map((s) => (
        <div key={s.id} className="p-4 border rounded shadow">
          <h2 className="font-semibold">{s.name}</h2>
          <p>{s.location}</p>
          <p>{s.max_kw} kW</p>
          <select
            className="mt-2 border p-1 rounded"
            value={s.status}
            onChange={(e) => onStatusChange(s.id, e.target.value)}
          >
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </div>
      ))}
    </div>
  )
}
