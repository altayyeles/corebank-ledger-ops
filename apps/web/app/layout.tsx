import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { cn } from "@/lib/utils";
import { Toaster } from "@/components/ui/sonner";
import { ThemeProvider } from "@/components/theme-provider";
import AppShell from "@/components/app-shell/app-shell";
import { I18nProvider } from "@/components/i18n-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "corebank-ledger-ops (V10)",
  description: "Enterprise banking ops dashboard: ledger, TM alerts, cases, SLA, DLQ.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr" suppressHydrationWarning>
      <body className={cn(inter.className, "min-h-screen bg-background text-foreground")}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <I18nProvider>
            <AppShell>{children}</AppShell>
            <Toaster richColors />
          </I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
