
'use client';
import { useState } from 'react';
import { api } from '../lib/api';

export default function TransferPage() {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [amount, setAmount] = useState('5000.00');
  const [msg, setMsg] = useState('');

  async function go() {
    setMsg('');
    try {
      const idk = crypto.randomUUID();
      const t = await api('/transfers', { method:'POST', headers:{ 'Idempotency-Key': idk }, body: JSON.stringify({ from_account_id: from, to_account_id: to, amount, currency:'TRY', transfer_type:'INTERNAL' }) });
      await api(`/transfers/${t.id}/authorize`, { method:'POST' });
      setMsg(`Created & authorized ${t.id}. Worker will settle and create master alert.`);
    } catch (e) { setMsg(String(e.message||e)); }
  }

  return (
    <main>
      <h2>Create Transfer</h2>
      <label>From account_id</label>
      <input value={from} onChange={(e)=>setFrom(e.target.value)} style={{ width:'100%', padding:8, maxWidth:520 }} />
      <label>To account_id</label>
      <input value={to} onChange={(e)=>setTo(e.target.value)} style={{ width:'100%', padding:8, maxWidth:520, marginTop:6 }} />
      <label>Amount</label>
      <input value={amount} onChange={(e)=>setAmount(e.target.value)} style={{ width:'100%', padding:8, maxWidth:220, marginTop:6 }} />
      <div style={{ marginTop: 10 }}>
        <button onClick={go} style={{ padding:10 }}>Create & Authorize</button>
      </div>
      {msg && <p style={{ marginTop: 12 }}>{msg}</p>}
    </main>
  );
}
