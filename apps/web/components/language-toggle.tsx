"use client";

import { Languages } from "lucide-react";
import { useI18n } from "@/components/i18n-provider";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";

export default function LanguageToggle() {
  const { lang, setLang } = useI18n();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" aria-label="Language">
          <Languages className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setLang("tr")}>Türkçe {lang === "tr" ? "✓" : ""}</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setLang("en")}>English {lang === "en" ? "✓" : ""}</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
