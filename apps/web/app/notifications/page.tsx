"use client";

import useSWR from "swr";
import { useMemo, useState } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

function statusVariant(status?: string) {
  const s = (status || "").toUpperCase();
  if (s === "SENT") return "default";
  if (s === "RETRY") return "secondary";
  if (s === "FAILED") return "destructive";
  return "outline";
}

export default function NotificationsPage() {
  const [tab, setTab] = useState<"all" | "failed">("all");
  const [q, setQ] = useState("");
  const endpoint = tab === "failed" ? "/notifications/failed" : "/notifications";
  const { data, error, mutate, isLoading } = useSWR(endpoint, api, { refreshInterval: 5000 });
  const rows = useMemo(() => (Array.isArray(data) ? data : []), [data]);

  const filtered = useMemo(() => {
    const list = tab === "failed" ? rows.filter((r: any) => r.status === "FAILED") : rows;
    if (!q) return list;
    const qq = q.toLowerCase();
    return list.filter((n: any) =>
      String(n.recipient || "").toLowerCase().includes(qq) ||
      String(n.channel || "").toLowerCase().includes(qq) ||
      String(n.last_error || "").toLowerCase().includes(qq)
    );
  }, [rows, q, tab]);

  async function requeue(id: string) {
    try {
      await api(`/notifications/${id}/requeue`, { method: "POST" });
      toast.success("Requeued");
      await mutate();
    } catch (e: any) {
      toast.error(String(e?.message || e));
    }
  }

  return (
    <div className="grid gap-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Notifications</h1>
          <p className="text-sm text-muted-foreground">Queue states + DLQ + requeue (enterprise ops workflow).</p>
        </div>
        <Input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search channel/recipient/error" className="w-[320px]" />
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Notification queue</CardTitle>
        </CardHeader>
        <CardContent>
          {error && <div className="text-sm text-red-500">{String((error as any)?.message || error)}</div>}

          <Tabs value={tab} onValueChange={(v) => setTab(v as any)}>
            <TabsList>
              <TabsTrigger value="all">ALL</TabsTrigger>
              <TabsTrigger value="failed">FAILED (DLQ)</TabsTrigger>
            </TabsList>

            <TabsContent value={tab} className="mt-4">
              {isLoading ? (
                <div className="space-y-3">
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-8 w-full" />
                  <Skeleton className="h-8 w-full" />
                </div>
              ) : (
                <>
                  {filtered.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No notifications.</div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Channel</TableHead>
                          <TableHead>Recipient</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Attempts</TableHead>
                          <TableHead>Next Attempt</TableHead>
                          <TableHead>Last Error</TableHead>
                          <TableHead className="text-right">Action</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filtered.map((n: any) => (
                          <TableRow key={n.id}>
                            <TableCell className="font-medium">{n.channel}</TableCell>
                            <TableCell className="max-w-[260px] truncate" title={n.recipient}>{n.recipient}</TableCell>
                            <TableCell><Badge variant={statusVariant(n.status)}>{n.status}</Badge></TableCell>
                            <TableCell className="text-right tabular-nums">{n.attempt_count}/{n.max_attempts}</TableCell>
                            <TableCell className="text-xs text-muted-foreground">{n.next_attempt_at || "-"}</TableCell>
                            <TableCell className="max-w-[260px] truncate text-xs text-muted-foreground" title={n.last_error || ""}>{n.last_error || "-"}</TableCell>
                            <TableCell className="text-right">
                              {n.status === "FAILED" ? (
                                <Button size="sm" onClick={() => requeue(n.id)}>Requeue</Button>
                              ) : (
                                <span className="text-xs text-muted-foreground">-</span>
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
