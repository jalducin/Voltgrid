// pages/index.tsx
import Head from 'next/head'
import { useEffect, useState } from 'react'
import api from '../utils/api'
import Login from '../components/login'
import StationList from '../components/StationList'
import StationForm from '../components/StationForm'
import StationChart from '../components/StationChart'

export default function Home() {
  // estados
  const [stations, setStations] = useState<any[]>([])
  const [filter, setFilter] = useState<string>('all')

  // para controlar el token y el "mounted"
  const [token, setToken] = useState<string | null>(null)
  const [ready, setReady] = useState(false)

  // sólo cliente: leer el token y marcar listo
  useEffect(() => {
    const t = localStorage.getItem('token')
    setToken(t)
    setReady(true)
  }, [])

  // cuando ya estamos listos Y hay token, trae estaciones
  useEffect(() => {
    if (ready && token) {
      fetchStations(filter)
    }
  }, [ready, token, filter])

  // fetchStations
  const fetchStations = async (status = 'all') => {
    try {
      const res = await api.get(
        `/stations${status !== 'all' ? `?status=${status}` : ''}`
      )
      setStations(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const handleNew = async (data: any) => {
    await api.post('/stations', data)
    fetchStations(filter)
  }

  const handleStatusChange = async (id: number, status: string) => {
    await api.patch(`/stations/${id}`, null, { params: { new_status: status } })
    fetchStations(filter)
  }

  // Mientras Next está haciendo SSR / hydration:
  if (!ready) {
    return <div>Loading…</div>
  }

  // Si no hay token en client:
  if (!token) {
    return <Login />
  }

  // Finalmente, mostramos el dashboard
  return (
    <>
      <Head>
        <title>S2G Energy Dashboard</title>
      </Head>
      <div className="p-8">
        <h1 className="text-2xl font-bold mb-4">Estaciones de Carga</h1>
        <StationForm onSubmit={handleNew} />
        <div className="mt-4 mb-4">
          <label className="mr-2">Filtro:</label>
          <select
            className="border p-1 rounded"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">Todas</option>
            <option value="activo">Activas</option>
            <option value="inactivo">Inactivas</option>
          </select>
        </div>
        <StationChart stations={stations} />
        <StationList
          stations={stations}
          onStatusChange={handleStatusChange}
        />
      </div>
    </>
  )
}
