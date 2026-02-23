
'use client';
import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@demo.local');
  const [password, setPassword] = useState('Admin123!');
  const [msg, setMsg] = useState('');

  async function submit(e) {
    e.preventDefault();
    setMsg('');
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const res = await fetch(`${API_BASE}/auth/login`, { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body: form.toString() });
    const data = await res.json();
    if (!res.ok) { setMsg(data?.detail || 'Login failed'); return; }
    localStorage.setItem('token', data.access_token);
    setMsg('Logged in');
  }

  return (
    <main>
      <h2>Login</h2>
      <form onSubmit={submit} style={{ maxWidth: 360 }}>
        <label>Email</label>
        <input value={email} onChange={(e)=>setEmail(e.target.value)} style={{ width:'100%', padding:8, margin:'6px 0 12px' }} />
        <label>Password</label>
        <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} style={{ width:'100%', padding:8, margin:'6px 0 12px' }} />
        <button style={{ padding:10 }}>Login</button>
      </form>
      {msg && <p style={{ marginTop: 12 }}>{msg}</p>}
    </main>
  );
}
