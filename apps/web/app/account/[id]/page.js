
'use client';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { api } from '../../lib/api';

export default function AccountDetail() {
  const { id } = useParams();
  const { data: bal, error } = useSWR(`/accounts/${id}/balances`, api);
  return (
    <main>
      <h2>Account {id}</h2>
      {error && <p style={{ color:'red' }}>{String(error.message)}</p>}
      {bal && <p><b>Ledger:</b> {bal.ledger_balance} — <b>Available:</b> {bal.available_balance}</p>}
    </main>
  );
}
