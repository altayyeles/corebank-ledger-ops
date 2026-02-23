"use client";

import useSWR from "swr";
import { api } from "./lib/api";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ShieldAlert, Siren, TimerReset, Inbox, ArrowRight } from "lucide-react";

import DemoIdsCard from "@/components/demo-ids-card";
import Stepper from "@/components/stepper";

function Stat({
  title,
  value,
  hint,
  icon,
  tone,
}: {
  title: string;
  value: string;
  hint?: string;
  icon: React.ReactNode;
  tone?: "warn" | "danger" | "neutral";
}) {
  const badgeVariant = tone === "danger" ? "destructive" : tone === "warn" ? "secondary" : "outline";
  const badgeText = tone === "danger" ? "kritik" : tone === "warn" ? "dikkat" : "canlı";

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <Badge variant={badgeVariant} className="capitalize">{badgeText}</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-2xl font-semibold tabular-nums">{value}</div>
          <div className="text-muted-foreground">{icon}</div>
        </div>
        {hint && <p className="mt-1 text-xs text-muted-foreground">{hint}</p>}
      </CardContent>
    </Card>
  );
}

export default function Dashboard() {
  const { data: alertsNew } = useSWR("/fraud/alerts?status=NEW", api);
  const { data: alertsEsc } = useSWR("/fraud/alerts?status=ESCALATED", api);
  const { data: breaches } = useSWR("/cases/sla-breaches", api);
  const { data: notifsFailed } = useSWR("/notifications/failed", api);

  const nAlertsNew = Array.isArray(alertsNew) ? alertsNew.length : 0;
  const nAlertsEsc = Array.isArray(alertsEsc) ? alertsEsc.length : 0;
  const nBreaches = Array.isArray(breaches) ? breaches.length : 0;
  const nFailed = Array.isArray(notifsFailed) ? notifsFailed.length : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Operasyon Paneli</h1>
          <p className="text-sm text-muted-foreground">
            Settlement → Ledger posting → TM master alerts → Case/SLA → Notifications/DLQ
          </p>
        </div>
        <Badge variant="secondary">New York • Zinc • V10</Badge>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Stat title="YENİ Uyarılar" value={String(nAlertsNew)} hint="Triage bekleyen master alert" icon={<ShieldAlert className="h-5 w-5" />} tone={nAlertsNew > 0 ? "warn" : "neutral"} />
        <Stat title="ESKALASYON" value={String(nAlertsEsc)} hint="Öncelikli inceleme" icon={<Siren className="h-5 w-5" />} tone={nAlertsEsc > 0 ? "danger" : "neutral"} />
        <Stat title="SLA İhlalleri" value={String(nBreaches)} hint="Süresi aşmış vakalar" icon={<TimerReset className="h-5 w-5" />} tone={nBreaches > 0 ? "danger" : "neutral"} />
        <Stat title="DLQ (FAILED)" value={String(nFailed)} hint="Manuel requeue bekleyen" icon={<Inbox className="h-5 w-5" />} tone={nFailed > 0 ? "warn" : "neutral"} />
      </div>

      <DemoIdsCard />

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Hızlı İşlemler</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <Button asChild><a href="/transfer">Transfer Oluştur</a></Button>
          <Button asChild variant="secondary"><a href="/alerts">Uyarıları Gör</a></Button>
          <Button asChild variant="outline"><a href="/graph">Grafı Aç</a></Button>
          <Button asChild variant="outline"><a href="/notifications">DLQ Aç</a></Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Bu demo ne gösteriyor?</CardTitle>
        </CardHeader>
        <CardContent>
          <Stepper
            steps={[
              { title: "Transfer oluştur & authorize", description: "Outbox event üretilir (idempotent)." },
              { title: "Worker settle eder", description: "Journal entry yazar ve bakiyeleri günceller." },
              { title: "TM değerlendirme", description: "Reason codes ile transfer başına 1 master alert." },
              { title: "Vaka & SLA", description: "Case açılır, SLA breach tespiti yapılır." },
              { title: "Bildirim kuyruğu", description: "Retry/backoff + DLQ + UI'dan requeue." },
            ]}
          />

          <Separator className="my-4" />

          <div className="text-xs text-muted-foreground flex items-center gap-2">
            <span>Öneri:</span>
            <a className="underline" href="/transfer">Transfer</a>
            <ArrowRight className="h-4 w-4" />
            <a className="underline" href="/alerts">Uyarılar</a>
            <ArrowRight className="h-4 w-4" />
            <a className="underline" href="/graph">Graf</a>
          </div>
        </CardContent>
      </Card>

      <div className="text-xs text-muted-foreground">
        Tip: Graph sayfasında alert node seçip “Vaka Oluştur (1s SLA)” ile akışı hızlandır.
      </div>
    </div>
  );
}
