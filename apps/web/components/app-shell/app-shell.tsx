"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bell, Cable, CircleDollarSign, GitGraph, LayoutDashboard, ListChecks, ShieldAlert, WalletCards } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import ThemeToggle from "@/components/theme-toggle";
import LanguageToggle from "@/components/language-toggle";
import { useI18n } from "@/components/i18n-provider";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const t = useI18n().t;
  const nav = [
    { href: "/", label: t("nav.dashboard"), icon: LayoutDashboard },
    { href: "/accounts", label: t("nav.accounts"), icon: WalletCards },
    { href: "/transfer", label: t("nav.transfer"), icon: CircleDollarSign },
    { href: "/ledger", label: t("nav.ledger"), icon: Cable },
    { href: "/alerts", label: t("nav.alerts"), icon: ShieldAlert },
    { href: "/alert-history", label: t("nav.alertHistory"), icon: ListChecks },
    { href: "/cases", label: t("nav.cases"), icon: ListChecks },
    { href: "/sla", label: t("nav.sla"), icon: ListChecks },
    { href: "/notifications", label: t("nav.notifications"), icon: Bell },
    { href: "/graph", label: t("nav.graph"), icon: GitGraph },
  ];

  function SideNav({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname();
    return (
      <div className="flex h-full flex-col">
        <div className="px-3 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="font-semibold tracking-tight">{t("app.title")}</Link>
            <span className="text-xs text-muted-foreground">v10</span>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">{t("app.subtitle")}</p>
        </div>
        <Separator />
        <div className="flex-1 overflow-auto px-2 py-2">
          {nav.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onNavigate}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                  active ? "bg-secondary text-foreground" : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </div>
        <Separator />
        <div className="p-3 text-xs text-muted-foreground">Tip: Graph → Alert seç → Case oluştur.</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <div className="flex">
        <aside className="hidden h-screen w-64 border-r md:block">
          <SideNav />
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-40 border-b bg-background/80 backdrop-blur">
            <div className="flex h-14 items-center justify-between px-4">
              <div className="flex items-center gap-2">
                <Sheet>
                  <SheetTrigger asChild>
                    <Button variant="outline" size="icon" className="md:hidden" aria-label="Menu">
                      <span className="text-lg">☰</span>
                    </Button>
                  </SheetTrigger>
                  <SheetContent side="left" className="p-0">
                    <SideNav onNavigate={() => {}} />
                  </SheetContent>
                </Sheet>

                <div className="hidden md:block text-sm text-muted-foreground">{t("top.enterprise")}</div>
              </div>

              <div className="flex items-center gap-2">
                <LanguageToggle />
                <ThemeToggle />
                <Button asChild variant="outline" size="sm">
                  <Link href="/login">{t("top.login")}</Link>
                </Button>
              </div>
            </div>
          </header>

          <main className="flex-1 px-4 py-6 md:px-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
