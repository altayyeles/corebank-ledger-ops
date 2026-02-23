
'use client';

import useSWR from 'swr';
import { useState } from 'react';
import { api } from '../lib/api';

export default function CasesPage() {
  const { data, mutate } = useSWR('/cases', api);
  const [msg, setMsg] = useState('');
  const [alertId, setAlertId] = useState('');
  const [sla, setSla] = useState('');

  async function create() {
    setMsg('');
    try {
      const r = await api('/cases', { method:'POST', body: JSON.stringify({ alert_id: alertId || null, sla_due_at: sla || null, priority: 'HIGH' }) });
      setMsg(`Case created: ${r.id}`);
      await mutate();
    } catch (e) { setMsg(String(e.message||e)); }
  }

  return (
    <main>
      <h2>Cases</h2>
      <div style={{ border:'1px solid #eee', padding: 12 }}>
        <h3>Create Case (set SLA in past to trigger breach)</h3>
        <label>alert_id (optional)</label>
        <input value={alertId} onChange={(e)=>setAlertId(e.target.value)} style={{ width:'100%', padding:8, maxWidth: 720 }} />
        <label>sla_due_at (ISO, optional)</label>
        <input value={sla} onChange={(e)=>setSla(e.target.value)} placeholder="2020-01-01T00:00:00+00:00" style={{ width:'100%', padding:8, maxWidth: 360, marginTop: 6 }} />
        <div style={{ marginTop: 10 }}><button onClick={create} style={{ padding:10 }}>Create</button></div>
        {msg && <p style={{ marginTop: 10 }}>{msg}</p>}
      </div>

      <h3 style={{ marginTop: 16 }}>List</h3>
      {data && data.map(c => (
        <div key={c.id} style={{ border:'1px solid #eee', padding: 12, marginTop: 10 }}>
          <div><b>{c.status}</b> — {c.id} — priority {c.priority}</div>
          <div style={{ color:'#666' }}>alert: {c.alert_id || '-'} | sla_due_at: {c.sla_due_at || '-'} | breached: {c.sla_breached}</div>
        </div>
      ))}
    </main>
  );
}
