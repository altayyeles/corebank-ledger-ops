"use client";

import Link from "next/link";
import useSWR from "swr";
import { useMemo, useState } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

import { DataTable } from "@/components/data-table";
import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";

function statusVariant(status?: string) {
  const s = (status || "").toUpperCase();
  if (s === "NEW") return "destructive";
  if (s === "ACK") return "secondary";
  if (s === "IN_REVIEW") return "secondary";
  if (s === "ESCALATED") return "default";
  if (s === "CLOSED") return "outline";
  return "outline";
}

function severityVariant(sev?: string) {
  const s = (sev || "").toUpperCase();
  if (s === "HIGH") return "destructive";
  if (s === "MEDIUM") return "secondary";
  return "outline";
}

type AlertRow = {
  id: string;
  severity: string;
  status: string;
  reason: string;
  score: string;
  transfer_id?: string;
  explain?: any;
};

export default function AlertsPage() {
  const [status, setStatus] = useState("NEW");
  const { data, error, mutate, isLoading } = useSWR(`/fraud/alerts?status=${status}`, api);

  const rows: AlertRow[] = useMemo(() => (Array.isArray(data) ? data : []), [data]);

  async function act(id: string, action: "ack" | "escalate" | "close") {
    try {
      await api(`/fraud/alerts/${id}/${action}`, {
        method: "POST",
        body: JSON.stringify({ note: `${action} via ui` }),
      });
      toast.success(`Alert ${action.toUpperCase()} ok`);
      await mutate();
    } catch (e: any) {
      toast.error(String(e?.message || e));
    }
  }

  const columns: ColumnDef<AlertRow>[] = [
    {
      accessorKey: "severity",
      header: ({ column }) => (
        <Button variant="ghost" size="sm" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Severity <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => <Badge variant={severityVariant(row.original.severity)}>{row.original.severity}</Badge>,
    },
    {
      accessorKey: "status",
      header: ({ column }) => (
        <Button variant="ghost" size="sm" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Status <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => <Badge variant={statusVariant(row.original.status)}>{row.original.status}</Badge>,
    },
    {
      accessorKey: "reason",
      header: "Reason",
      cell: ({ row }) => (
        <div className="max-w-[420px] truncate" title={row.original.reason}>
          {row.original.reason}
        </div>
      ),
    },
    {
      accessorKey: "score",
      header: ({ column }) => (
        <div className="text-right">
          <Button variant="ghost" size="sm" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
            Score <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        </div>
      ),
      cell: ({ row }) => <div className="text-right tabular-nums">{row.original.score}</div>,
    },
    {
      accessorKey: "transfer_id",
      header: "Transfer",
      cell: ({ row }) =>
        row.original.transfer_id ? (
          <Link className="text-primary underline" href={`/transfer/${row.original.transfer_id}`}>
            {String(row.original.transfer_id).slice(0, 8)}…
          </Link>
        ) : (
          <span className="text-muted-foreground">-</span>
        ),
    },
    {
      id: "top_reason",
      header: "Top Reason",
      cell: ({ row }) => (
        <span className="font-mono text-xs">{row.original.explain?.top_reason_code || "-"}</span>
      ),
    },
    {
      id: "actions",
      header: () => <div className="text-right">Actions</div>,
      cell: ({ row }) => (
        <div className="flex justify-end gap-2">
          <Button size="sm" variant="secondary" onClick={() => act(row.original.id, "ack")}>ACK</Button>
          <Button size="sm" onClick={() => act(row.original.id, "escalate")}>ESC</Button>
          <Button size="sm" variant="outline" onClick={() => act(row.original.id, "close")}>CLOSE</Button>
          <Button asChild size="sm" variant="ghost">
            <Link href={`/alert-history?alert_id=${row.original.id}`}>History</Link>
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Uyarılar</h1>
          <p className="text-sm text-muted-foreground">Filtrele, sırala ve sayfalayarak triage yap.</p>
        </div>
        <div className="w-[220px]">
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder="Durum" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NEW">NEW</SelectItem>
              <SelectItem value="ACK">ACK</SelectItem>
              <SelectItem value="ESCALATED">ESCALATED</SelectItem>
              <SelectItem value="CLOSED">CLOSED</SelectItem>
              <SelectItem value="IN_REVIEW">IN_REVIEW</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Alert DataTable</CardTitle>
        </CardHeader>
        <CardContent>
          {error && <div className="text-sm text-red-500">{String((error as any)?.message || error)}</div>}

          {isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          ) : (
            <DataTable columns={columns} data={rows} globalFilterPlaceholder="Reason / transfer / top_reason ara…" />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
