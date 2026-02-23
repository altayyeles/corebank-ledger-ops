
'use client';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { api } from '../../lib/api';

export default function TransferDetail() {
  const { id } = useParams();
  const { data, error } = useSWR(`/transfers/${id}`, api);
  return (
    <main>
      <h2>Transfer {id}</h2>
      {error && <p style={{ color:'red' }}>{String(error.message)}</p>}
      {!data && <p>Loading...</p>}
      {data && (
        <div style={{ border:'1px solid #eee', padding: 12 }}>
          <div><b>Status:</b> {data.status}</div>
          <div><b>Amount:</b> {data.amount} {data.currency}</div>
          <div><b>From:</b> {data.from_account_id}</div>
          <div><b>To:</b> {data.to_account_id}</div>
          <div><b>Created:</b> {data.created_at}</div>
        </div>
      )}
    </main>
  );
}
