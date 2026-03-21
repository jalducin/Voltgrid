// components/StationChart.tsx
import React from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

interface Station {
  name: string
  max_kw: number
}

interface StationChartProps {
  stations: Station[]
}

export default function StationChart({ stations }: StationChartProps) {
  const data = stations.map((s) => ({ name: s.name, kW: s.max_kw }))

  return (
    <div className="h-64 mt-6">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="kW" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
