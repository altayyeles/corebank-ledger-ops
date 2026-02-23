
'use client';
import { useState } from 'react';
import { api } from '../lib/api';

export default function AlertHistoryPage() {
  const [alertId, setAlertId] = useState('');
  const [items, setItems] = useState([]);
  const [msg, setMsg] = useState('');

  async function load() {
    setMsg('');
    try {
      const data = await api(`/fraud/alerts/${alertId}/history`);
      setItems(data);
    } catch (e) { setMsg(String(e.message||e)); }
  }

  return (
    <main>
      <h2>Alert History</h2>
      <input value={alertId} onChange={(e)=>setAlertId(e.target.value)} placeholder="alert_id" style={{ width: 520, padding: 8 }} />
      <button onClick={load} style={{ padding: 10, marginLeft: 8 }}>Load</button>
      {msg && <p style={{ color:'red' }}>{msg}</p>}
      {items.map(h => (
        <div key={h.id} style={{ border:'1px solid #eee', padding: 12, marginTop: 10 }}>
          <div><b>{h.from_status}</b> → <b>{h.to_status}</b></div>
          <div style={{ color:'#666', fontSize: 12 }}>{h.created_at} by {h.changed_by_user_id || '-'}</div>
          {h.note && <div style={{ marginTop: 4 }}>{h.note}</div>}
        </div>
      ))}
    </main>
  );
}
