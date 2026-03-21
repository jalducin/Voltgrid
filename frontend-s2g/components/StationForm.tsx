// components/StationForm.tsx
import React, { useState, ChangeEvent, FormEvent } from 'react'

interface StationFormProps {
  onSubmit: (data: {
    name: string
    location: string
    max_kw: number
    status: string
  }) => void
}

export default function StationForm({ onSubmit }: StationFormProps) {
  const [form, setForm] = useState({
    name: '',
    location: '',
    max_kw: '',
    status: 'activo'
  })

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onSubmit({
      name: form.name,
      location: form.location,
      max_kw: parseFloat(form.max_kw),
      status: form.status
    })
    setForm({ name: '', location: '', max_kw: '', status: 'activo' })
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-5 gap-2">
      <input
        name="name"
        placeholder="Nombre"
        value={form.name}
        onChange={handleChange}
        className="border p-2 rounded"
        required
      />
      <input
        name="location"
        placeholder="Ubicación"
        value={form.location}
        onChange={handleChange}
        className="border p-2 rounded"
        required
      />
      <input
        name="max_kw"
        type="number"
        step="0.1"
        placeholder="kW"
        value={form.max_kw}
        onChange={handleChange}
        className="border p-2 rounded"
        required
      />
      <select
        name="status"
        value={form.status}
        onChange={handleChange}
        className="border p-2 rounded"
      >
        <option value="activo">Activo</option>
        <option value="inactivo">Inactivo</option>
      </select>
      <button type="submit" className="bg-blue-500 text-white p-2 rounded">
        Registrar
      </button>
    </form>
  )
}
