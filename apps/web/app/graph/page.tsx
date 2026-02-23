"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import { toast } from "sonner";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

function colorFor(type: string) {
  const map: Record<string, string> = {
    customer: "#2563eb",
    account: "#059669",
    transfer: "#7c3aed",
    alert: "#dc2626",
    case: "#d97706",
  };
  return map[type] || "#334155";
}

export default function GraphPage() {
  const [customerId, setCustomerId] = useState("");
  const [graph, setGraph] = useState<any>(null);
  const [selected, setSelected] = useState<any>(null);
  const [detail, setDetail] = useState<any>(null);
  const [filters, setFilters] = useState({ customer: true, account: true, transfer: true, alert: true, case: true });
  const [running, setRunning] = useState(false);
  const [msg, setMsg] = useState("");

  const width = 1100;
  const height = 650;

  async function load() {
    setMsg("");
    setSelected(null);
    setDetail(null);
    try {
      const g = await api(`/graph/customer/${customerId}`);
      const nodes = g.nodes.map((n: any, i: number) => ({
        ...n,
        x: 120 + (i % 10) * 70,
        y: 100 + Math.floor(i / 10) * 55,
        vx: 0,
        vy: 0,
      }));
      setGraph({ nodes, edges: g.edges });
    } catch (e: any) {
      setMsg(String(e.message || e));
    }
  }

  const filtered = useMemo(() => {
    if (!graph) return null;
    const allowed = new Set(Object.entries(filters).filter(([, v]) => v).map(([k]) => k));
    const nodes = graph.nodes.filter((n: any) => allowed.has(n.type));
    const setIds = new Set(nodes.map((n: any) => n.id));
    const edges = graph.edges.filter((e: any) => setIds.has(e.from) && setIds.has(e.to));
    return { nodes, edges };
  }, [graph, filters]);

  useEffect(() => {
    let alive = true;
    async function fetchDetail() {
      if (!selected) { setDetail(null); return; }
      try {
        if (selected.type === "transfer") {
          const d = await api(`/transfers/${selected.id}`);
          if (alive) setDetail(d);
        } else if (selected.type === "account") {
          const bal = await api(`/accounts/${selected.id}/balances`);
          if (alive) setDetail({ balances: bal });
        } else if (selected.type === "alert") {
          const d = await api(`/fraud/alerts/${selected.id}`);
          if (alive) setDetail(d);
        } else if (selected.type === "case") {
          const d = await api(`/cases/${selected.id}`);
          if (alive) setDetail(d);
        } else {
          if (alive) setDetail(null);
        }
      } catch (e: any) {
        if (alive) setDetail({ error: String(e.message || e) });
      }
    }
    fetchDetail();
    return () => { alive = false; };
  }, [selected]);

  useEffect(() => {
    if (!graph || !filtered || running) return;
    setRunning(true);
    let raf: any = null;
    const kRepel = 9000;
    const kSpring = 0.003;
    const springLen = 130;
    const damping = 0.85;

    function step() {
      const nodes = filtered.nodes;
      const edges = filtered.edges;
      const idToNode = new Map(nodes.map((n: any) => [n.id, n]));

      for (const n of nodes) { n.fx = 0; n.fy = 0; }

      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const dist2 = dx*dx + dy*dy + 0.01;
          const f = kRepel / dist2;
          const inv = 1 / Math.sqrt(dist2);
          const fx = f * dx * inv, fy = f * dy * inv;
          a.fx += fx; a.fy += fy;
          b.fx -= fx; b.fy -= fy;
        }
      }

      for (const e of edges) {
        const s = idToNode.get(e.from), t = idToNode.get(e.to);
        if (!s || !t) continue;
        const dx = t.x - s.x, dy = t.y - s.y;
        const dist = Math.sqrt(dx*dx + dy*dy) + 0.01;
        const diff = dist - springLen;
        const f = kSpring * diff;
        s.fx += f * dx; s.fy += f * dy;
        t.fx -= f * dx; t.fy -= f * dy;
      }

      for (const n of nodes) {
        n.vx = (n.vx + n.fx) * damping;
        n.vy = (n.vy + n.fy) * damping;
        n.x = Math.max(20, Math.min(width - 20, n.x + n.vx));
        n.y = Math.max(20, Math.min(height - 20, n.y + n.vy));
      }

      const pos = new Map(nodes.map((n: any) => [n.id, { x: n.x, y: n.y, vx: n.vx, vy: n.vy }]));
      for (const n of graph.nodes) {
        const p = pos.get(n.id);
        if (p) { n.x = p.x; n.y = p.y; n.vx = p.vx; n.vy = p.vy; }
      }

      setGraph({ nodes: [...graph.nodes], edges: graph.edges });
      raf = requestAnimationFrame(step);
    }

    raf = requestAnimationFrame(step);
    const stop = setTimeout(() => { cancelAnimationFrame(raf); setRunning(false); }, 1800);
    return () => { clearTimeout(stop); if (raf) cancelAnimationFrame(raf); setRunning(false); };
  }, [graph, filtered]);

  function toggle(t: keyof typeof filters) {
    setFilters((prev) => ({ ...prev, [t]: !prev[t] }));
  }

  async function createCaseForAlert() {
    if (!selected || selected.type !== "alert") return;
    try {
      const iso = new Date(Date.now() + 60 * 60 * 1000).toISOString();
      await api("/cases", { method: "POST", body: JSON.stringify({ alert_id: selected.id, priority: "HIGH", sla_due_at: iso }) });
      toast.success("Case created (1h SLA)");
    } catch (e: any) {
      toast.error(String(e.message || e));
    }
  }

  return (
    <div className="grid gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Graph</h1>
          <p className="text-sm text-muted-foreground">Customer → Accounts → Transfers → Alerts → Cases</p>
        </div>
        {running && <Badge variant="secondary">layouting…</Badge>}
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Load customer graph</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <Input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="customer_id" className="w-[520px]" />
          <Button onClick={load}>Load</Button>
          {msg && <div className="text-sm text-red-500">{msg}</div>}
        </CardContent>
      </Card>

      {filtered && (
        <div className="grid gap-4 md:grid-cols-[1fr_420px]">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Canvas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3 text-sm mb-3">
                {(["customer","account","transfer","alert","case"] as const).map((t) => (
                  <label key={t} className="flex items-center gap-2">
                    <input type="checkbox" checked={(filters as any)[t]} onChange={() => toggle(t)} />
                    <span style={{ color: colorFor(t) }}>{t}</span>
                  </label>
                ))}
              </div>

              <svg width={width} height={height} className="border rounded-md bg-card">
                {filtered.edges.map((e: any, idx: number) => {
                  const s = filtered.nodes.find((n: any) => n.id === e.from);
                  const t = filtered.nodes.find((n: any) => n.id === e.to);
                  if (!s || !t) return null;
                  return <line key={idx} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#cbd5e1" strokeWidth="1" />;
                })}

                {filtered.nodes.map((n: any) => (
                  <g key={n.id} style={{ cursor: "pointer" }} onClick={() => setSelected(n)}>
                    <circle cx={n.x} cy={n.y} r={12} fill={colorFor(n.type)} />
                    <text x={n.x + 16} y={n.y + 4} fontSize="11" fill="#0f172a">{String(n.label).slice(0, 28)}</text>
                  </g>
                ))}
              </svg>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Node details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {!selected && <div className="text-sm text-muted-foreground">Select a node.</div>}

              {selected && (
                <>
                  <div className="text-sm">
                    <div><b>Type:</b> {selected.type}</div>
                    <div><b>ID:</b> <span className="font-mono text-xs">{selected.id}</span></div>
                    <div className="mt-1"><b>Label:</b> {String(selected.label)}</div>
                  </div>

                  {selected?.meta?.href && (
                    <Button asChild variant="outline">
                      <a href={selected.meta.href}>Open link</a>
                    </Button>
                  )}

                  {selected.type === "alert" && (
                    <Button onClick={createCaseForAlert}>Create Case (1h SLA)</Button>
                  )}

                  <Separator />

                  <div className="text-sm font-medium">Live detail</div>
                  <ScrollArea className="h-[220px] rounded-md border bg-muted p-2">
                    <pre className="text-xs">{detail ? JSON.stringify(detail, null, 2) : "—"}</pre>
                  </ScrollArea>

                  <div className="text-sm font-medium">Meta</div>
                  <ScrollArea className="h-[200px] rounded-md border bg-muted p-2">
                    <pre className="text-xs">{JSON.stringify(selected.meta, null, 2)}</pre>
                  </ScrollArea>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
