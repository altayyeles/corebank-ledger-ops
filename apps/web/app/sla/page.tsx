"use client";

import useSWR from "swr";
import { api } from "../lib/api";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function pillVariant(n: number) {
  if (n >= 5) return "destructive";
  if (n >= 1) return "secondary";
  return "outline";
}

export default function SlaPage() {
  // API returns a list of breached cases
  const { data, error, isLoading } = useSWR("/cases/sla-breaches", api, { refreshInterval: 5000 });

  const list = Array.isArray(data) ? data : [];
  const count = list.length;

  return (
    <div className="grid gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">SLA İhlalleri</h1>
          <p className="text-sm text-muted-foreground">
            Worker 30 saniyede bir SLA kontrol eder. Süresi geçen vakalar burada görünür.
          </p>
        </div>
        <Badge variant={pillVariant(count)}>{count} kayıt</Badge>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Breach Listesi</CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="text-sm text-red-500">
              {String((error as any)?.message || error)}
            </div>
          )}

          {isLoading && (
            <div className="space-y-3">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
          )}

          {!isLoading && data && !Array.isArray(data) && (
            <div className="rounded-md border bg-muted p-3">
              <div className="text-xs text-muted-foreground mb-2">Beklenen format listeydi; debug JSON:</div>
              <pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>
            </div>
          )}

          {!isLoading && Array.isArray(data) && list.length === 0 && (
            <div className="text-sm text-muted-foreground">İhlal yok.</div>
          )}

          {!isLoading && list.length > 0 && (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Durum</TableHead>
                    <TableHead>Case ID</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>SLA Due</TableHead>
                    <TableHead>Breached At</TableHead>
                    <TableHead>Assignee</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {list.map((c: any) => (
                    <TableRow key={c.id}>
                      <TableCell>
                        <Badge variant={c.status === "CLOSED" ? "outline" : "secondary"}>{c.status}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{c.id}</TableCell>
                      <TableCell>{c.priority || "-"}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{c.sla_due_at || "-"}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{c.breached_at || "-"}</TableCell>
                      <TableCell className="text-xs text-muted-foreground">{c.assignee_user_id || "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
