# TR UI Pack (Enterprise) — Apply

This pack localizes the Enterprise UI to **Turkish by default**, with an optional language toggle (TR/EN).

## 1) Prereqs
- You already applied the Enterprise UI pack.
- Install deps (one time):

```bash
cd apps/web
npm i next-themes lucide-react
npx shadcn@latest add dropdown-menu
```

## 2) Copy files
Unzip at repo root and overwrite.

## 3) Restart web
```bash
docker compose restart web
# or

docker compose up -d --build web
```

## What changes
- Adds `I18nProvider` and `LanguageToggle`
- Updates layout + AppShell + Dashboard strings
