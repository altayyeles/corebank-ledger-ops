'use client';
import useSWR from 'swr';
import { api } from '../lib/api';

export default function SlaPage() {
  const { data, error } = useSWR('/cases/sla-breaches', api, { refreshInterval: 5000 });

  const list = Array.isArray(data) ? data : [];

  return (
    <main>
      <h2>SLA İhlalleri</h2>
      <p>Worker 30 saniyede bir kontrol eder.</p>

      {error && <p style={{ color: 'red' }}>{String(error.message || error)}</p>}

      {!data && <p>Yükleniyor...</p>}

      {data && !Array.isArray(data) && (
        <pre style={{ background:'#111', color:'#eee', padding:12, borderRadius:8, overflowX:'auto' }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      )}

      {Array.isArray(data) && list.length === 0 && <p>İhlal yok.</p>}

      {Array.isArray(data) && list.map((c) => (
        <div key={c.id} style={{ border:'1px solid #333', padding:12, marginTop:10, borderRadius:8 }}>
          <div><b>{c.status}</b> — {c.id}</div>
          <div style={{ color:'#aaa' }}>sla_due_at: {c.sla_due_at} | breached_at: {c.breached_at}</div>
        </div>
      ))}
    </main>
  );
}