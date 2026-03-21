// components/Login.tsx
import { useState, ChangeEvent, FormEvent } from 'react'
import api from '../utils/api'

export default function Login() {
  const [user, setUser] = useState({ username: '', password: '' })
  const [error, setError] = useState<string | null>(null)

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setUser({ ...user, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const params = new URLSearchParams()
      params.append('username', user.username)
      params.append('password', user.password)

      const res = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      localStorage.setItem('token', res.data.access_token)
      window.location.reload()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded shadow-md w-full max-w-sm"
      >
        <h2 className="text-xl font-bold mb-4">Iniciar Sesión</h2>
        {error && <p className="text-red-500 mb-2">{error}</p>}
        <input
          name="username"
          type="email"
          placeholder="Email"
          value={user.username}
          onChange={handleChange}
          required
          className="w-full mb-3 p-2 border rounded"
        />
        <input
          name="password"
          type="password"
          placeholder="Password"
          value={user.password}
          onChange={handleChange}
          required
          className="w-full mb-4 p-2 border rounded"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white p-2 rounded"
        >
          Login
        </button>
      </form>
    </div>
  )
}
