
'use client';
import useSWR from 'swr';
import { api } from '../lib/api';

export default function AccountsPage() {
  const { data: accounts, error } = useSWR('/accounts', api);
  return (
    <main>
      <h2>Accounts</h2>
      {error && <p style={{ color:'red' }}>{String(error.message)}</p>}
      {!accounts && <p>Loading...</p>}
      {accounts && accounts.map(a => (
        <div key={a.id} style={{ border:'1px solid #eee', padding:12, marginTop:10 }}>
          <div>{a.id} — {a.iban}</div>
          <div style={{ color:'#666' }}>
            <a href={`/account/${a.id}`}>Open</a>
          </div>
        </div>
      ))}
    </main>
  );
}
