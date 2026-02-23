
'use client';
import useSWR from 'swr';
import { api } from '../lib/api';

export default function LedgerPage() {
  const { data: tb } = useSWR('/ledger/trial-balance', api);
  const { data } = useSWR('/ledger/journal-entries', api);
  return (
    <main>
      <h2>Ledger</h2>
      {tb && <p>Total debit: {tb.total_debit} — Total credit: {tb.total_credit}</p>}
      {data && data.map(e => (
        <div key={e.id} style={{ border:'1px solid #eee', padding: 12, marginTop: 10 }}>
          <div><b>{e.entry_no}</b> — {e.description}</div>
        </div>
      ))}
    </main>
  );
}
