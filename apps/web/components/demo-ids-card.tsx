
"use client";

import * as React from "react";
import { toast } from "sonner";
import { Copy, Save } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

type DemoIds = {
  customerId: string;
  accountAId: string;
  accountAIban: string;
  accountBId: string;
  accountBIban: string;
};

const DEFAULTS: DemoIds = {
  customerId: "e8b4ee95-bd9d-4980-8eb2-8ab3594fc381",
  accountAId: "0f71a592-d5f3-44ce-9a24-1904f483e109",
  accountAIban: "TR760673359681419646467802",
  accountBId: "1a05a6b9-a7c2-47e8-8e44-604912e277e3",
  accountBIban: "TR208281875166015502929771",
};

const LS_KEY = "corebank_demo_ids_v10";

function safeParse(json: string | null): DemoIds | null {
  if (!json) return null;
  try {
    const v = JSON.parse(json);
    if (!v) return null;
    return {
      customerId: String(v.customerId || ""),
      accountAId: String(v.accountAId || ""),
      accountAIban: String(v.accountAIban || ""),
      accountBId: String(v.accountBId || ""),
      accountBIban: String(v.accountBIban || ""),
    };
  } catch {
    return null;
  }
}

async function copyToClipboard(label: string, value: string) {
  try {
    await navigator.clipboard.writeText(value);
    toast.success(`${label} kopyalandı`);
  } catch {
    toast.error("Kopyalama başarısız (tarayıcı izinleri?)");
  }
}

export default function DemoIdsCard() {
  const [ids, setIds] = React.useState<DemoIds>(DEFAULTS);

  React.useEffect(() => {
    const saved = safeParse(localStorage.getItem(LS_KEY));
    if (saved) setIds({ ...DEFAULTS, ...saved });
  }, []);

  function update<K extends keyof DemoIds>(k: K, v: string) {
    setIds((prev) => ({ ...prev, [k]: v }));
  }

  function save() {
    localStorage.setItem(LS_KEY, JSON.stringify(ids));
    toast.success("Demo ID'ler kaydedildi");
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between gap-3">
          <CardTitle className="text-base">Demo Bilgileri (Kopyala & Yapıştır)</CardTitle>
          <Button variant="outline" size="sm" onClick={save}>
            <Save className="mr-2 h-4 w-4" /> Kaydet
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Seed çıktısından gelen değerleri buraya yapıştırabilirsin. Kayıtlar tarayıcıda saklanır.
        </p>

        <div className="grid gap-2">
          <div className="text-xs text-muted-foreground">Customer ID</div>
          <div className="flex gap-2">
            <Input value={ids.customerId} onChange={(e) => update("customerId", e.target.value)} />
            <Button
              variant="secondary"
              size="icon"
              onClick={() => copyToClipboard("Customer ID", ids.customerId)}
              aria-label="Copy customer id"
            >
              <Copy className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <Separator />

        <div className="grid gap-3 md:grid-cols-2">
          <div className="space-y-2">
            <div className="text-sm font-medium">Account A</div>
            <div className="text-xs text-muted-foreground">Account ID</div>
            <div className="flex gap-2">
              <Input value={ids.accountAId} onChange={(e) => update("accountAId", e.target.value)} />
              <Button variant="secondary" size="icon" onClick={() => copyToClipboard("Account A ID", ids.accountAId)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <div className="text-xs text-muted-foreground">IBAN</div>
            <div className="flex gap-2">
              <Input value={ids.accountAIban} onChange={(e) => update("accountAIban", e.target.value)} />
              <Button variant="secondary" size="icon" onClick={() => copyToClipboard("Account A IBAN", ids.accountAIban)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <div className="text-sm font-medium">Account B</div>
            <div className="text-xs text-muted-foreground">Account ID</div>
            <div className="flex gap-2">
              <Input value={ids.accountBId} onChange={(e) => update("accountBId", e.target.value)} />
              <Button variant="secondary" size="icon" onClick={() => copyToClipboard("Account B ID", ids.accountBId)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <div className="text-xs text-muted-foreground">IBAN</div>
            <div className="flex gap-2">
              <Input value={ids.accountBIban} onChange={(e) => update("accountBIban", e.target.value)} />
              <Button variant="secondary" size="icon" onClick={() => copyToClipboard("Account B IBAN", ids.accountBIban)}>
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
