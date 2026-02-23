"use client";

import React, { createContext, useContext, useEffect, useMemo, useState } from "react";

type Lang = "tr" | "en";

type Dict = Record<string, string>;

const TR: Dict = {
  "app.title": "corebank-ledger-ops",
  "app.subtitle": "Kurumsal operasyon paneli (ledger • TM • case/SLA • DLQ)",
  "nav.dashboard": "Gösterge Paneli",
  "nav.accounts": "Hesaplar",
  "nav.transfer": "Transfer",
  "nav.ledger": "Muhasebe",
  "nav.alerts": "Uyarılar",
  "nav.alertHistory": "Uyarı Geçmişi",
  "nav.cases": "Vaka",
  "nav.sla": "SLA",
  "nav.notifications": "Bildirimler",
  "nav.graph": "Graf",
  "top.enterprise": "Kurumsal Dashboard",
  "top.login": "Giriş",

  "dash.title": "Operasyon Paneli",
  "dash.desc": "Settlement → Ledger posting → TM master alerts → Case/SLA → Notifications/DLQ",
  "dash.kpi.newAlerts": "YENİ Uyarılar",
  "dash.kpi.escalated": "ESKALASYON",
  "dash.kpi.slaBreaches": "SLA İhlalleri",
  "dash.kpi.dlq": "DLQ (FAILED)",
  "dash.kpi.newHint": "Triage bekleyen master alert",
  "dash.kpi.escHint": "Öncelikli inceleme",
  "dash.kpi.slaHint": "Süresi aşmış vakalar",
  "dash.kpi.dlqHint": "Manuel requeue bekleyen",

  "dash.quick": "Hızlı İşlemler",
  "dash.btn.createTransfer": "Transfer Oluştur",
  "dash.btn.viewAlerts": "Uyarıları Gör",
  "dash.btn.openGraph": "Grafı Aç",
  "dash.btn.openDlq": "DLQ Aç",

  "dash.what": "Bu demo ne gösteriyor?",
  "dash.step1": "Transfer oluştur & authorize → outbox event üretilir",
  "dash.step2": "Worker settle eder → journal entry yazar → bakiyeleri günceller",
  "dash.step3": "TM kuralları çalışır → transfer başına 1 master alert (reason codes)",
  "dash.step4": "Vaka aç → SLA breach tespiti → outbox → bildirim kuyruğu",
  "dash.step5": "Retry/backoff → FAILED (DLQ) → UI'dan requeue",

  "common.search": "Ara…",
  "alerts.title": "Uyarılar",
  "alerts.desc": "Transfer başına tek master alert + reason codes + triage aksiyonları.",
  "alerts.filterStatus": "Durum",
  "alerts.search": "Reason / transfer / top_reason ara",

  "notifs.title": "Bildirimler",
  "notifs.desc": "Queue state + DLQ + requeue (ops akışı).",
  "notifs.search": "Kanal/alıcı/hata ara",
  "tabs.all": "TÜMÜ",
  "tabs.failed": "FAILED (DLQ)",

  "graph.title": "Graf",
  "graph.desc": "Müşteri → Hesap → Transfer → Uyarı → Vaka",
  "graph.load": "Müşteri grafını yükle",
  "graph.btn.load": "Yükle",
  "graph.details": "Düğüm Detayı",
  "graph.openLink": "Bağlantıyı aç",
  "graph.createCase": "Vaka Oluştur (1s SLA)",
  "graph.liveDetail": "Canlı detay",
  "graph.meta": "Meta",
};

const EN: Dict = {
  "app.title": "corebank-ledger-ops",
  "app.subtitle": "Enterprise ops dashboard (ledger • TM • case/SLA • DLQ)",
  "nav.dashboard": "Dashboard",
  "nav.accounts": "Accounts",
  "nav.transfer": "Transfer",
  "nav.ledger": "Ledger",
  "nav.alerts": "Alerts",
  "nav.alertHistory": "Alert History",
  "nav.cases": "Cases",
  "nav.sla": "SLA",
  "nav.notifications": "Notifications",
  "nav.graph": "Graph",
  "top.enterprise": "Enterprise Dashboard",
  "top.login": "Login",

  "dash.title": "Ops Dashboard",
  "dash.desc": "Settlement → Ledger posting → TM master alerts → Case/SLA → Notifications/DLQ",
  "dash.kpi.newAlerts": "NEW Alerts",
  "dash.kpi.escalated": "ESCALATED",
  "dash.kpi.slaBreaches": "SLA Breaches",
  "dash.kpi.dlq": "DLQ (FAILED)",
  "dash.kpi.newHint": "Master alerts waiting triage",
  "dash.kpi.escHint": "High priority triage",
  "dash.kpi.slaHint": "Cases exceeded due time",
  "dash.kpi.dlqHint": "Notifications needing requeue",

  "dash.quick": "Quick actions",
  "dash.btn.createTransfer": "Create Transfer",
  "dash.btn.viewAlerts": "View Alerts",
  "dash.btn.openGraph": "Open Graph",
  "dash.btn.openDlq": "Open DLQ",

  "dash.what": "What this demo shows",
  "dash.step1": "Create & authorize transfer → outbox event is produced",
  "dash.step2": "Worker settles → posts journal entry → updates balances",
  "dash.step3": "TM rules evaluate → one master alert per transfer with reason codes",
  "dash.step4": "Create case → SLA breach detection → outbox → notifications queue",
  "dash.step5": "Retry/backoff → FAILED (DLQ) → requeue from UI",

  "common.search": "Search…",
  "alerts.title": "Alerts",
  "alerts.desc": "Master alerts per transfer + reason codes + triage actions.",
  "alerts.filterStatus": "Status",
  "alerts.search": "Search reason / transfer / top_reason",

  "notifs.title": "Notifications",
  "notifs.desc": "Queue state + DLQ + requeue (ops workflow).",
  "notifs.search": "Search channel/recipient/error",
  "tabs.all": "ALL",
  "tabs.failed": "FAILED (DLQ)",

  "graph.title": "Graph",
  "graph.desc": "Customer → Accounts → Transfers → Alerts → Cases",
  "graph.load": "Load customer graph",
  "graph.btn.load": "Load",
  "graph.details": "Node details",
  "graph.openLink": "Open link",
  "graph.createCase": "Create Case (1h SLA)",
  "graph.liveDetail": "Live detail",
  "graph.meta": "Meta",
};

const Ctx = createContext<{ lang: Lang; setLang: (l: Lang) => void; t: (k: string) => string }>({
  lang: "tr",
  setLang: () => {},
  t: (k) => k,
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>("tr");

  useEffect(() => {
    const saved = typeof window !== "undefined" ? (localStorage.getItem("lang") as Lang | null) : null;
    if (saved === "tr" || saved === "en") setLang(saved);
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") localStorage.setItem("lang", lang);
  }, [lang]);

  const dict = lang === "tr" ? TR : EN;
  const t = useMemo(() => (k: string) => dict[k] ?? k, [dict]);

  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>;
}

export function useI18n() {
  return useContext(Ctx);
}
