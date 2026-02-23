"use client";

import Link from "next/link";
import { NavigationMenu, NavigationMenuItem, NavigationMenuList } from "@/components/ui/navigation-menu";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

const items = [
  { href: "/", label: "Dashboard" },
  { href: "/accounts", label: "Accounts" },
  { href: "/transfer", label: "Transfer" },
  { href: "/ledger", label: "Ledger" },
  { href: "/alerts", label: "Alerts" },
  { href: "/alert-history", label: "Alert History" },
  { href: "/cases", label: "Cases" },
  { href: "/sla", label: "SLA" },
  { href: "/notifications", label: "Notifications" },
  { href: "/graph", label: "Graph" },
];

export default function TopNav() {
  return (
    <header className="w-full border-b bg-background/80 backdrop-blur">
      <div className="container mx-auto flex h-14 items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="font-semibold tracking-tight">corebank-ledger-ops</Link>
          <span className="text-xs text-muted-foreground">v10</span>
        </div>

        <nav className="hidden md:block">
          <NavigationMenu>
            <NavigationMenuList>
              {items.map((it) => (
                <NavigationMenuItem key={it.href}>
                  <Link href={it.href} className="px-3 py-2 text-sm hover:text-primary">
                    {it.label}
                  </Link>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>
        </nav>

        <div className="flex items-center gap-2">
          <Button asChild variant="outline" size="sm">
            <Link href="/login">Login</Link>
          </Button>
        </div>
      </div>
      <Separator />
    </header>
  );
}
