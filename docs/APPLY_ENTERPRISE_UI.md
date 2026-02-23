# Enterprise UI Pack (shadcn/ui) — Apply

This pack upgrades the Web UI to a more **enterprise dashboard** look:
- Real shadcn theme tokens in `globals.css` (restores modern look)
- Sidebar + topbar app shell
- Dark mode (next-themes)
- Dashboard KPI cards using existing API endpoints
- Upgraded Alerts / Notifications / Graph pages (search, better layout)

## 1) Install deps (one-time)
Run inside `apps/web`:

```bash
npm i next-themes lucide-react
npx shadcn@latest add button card badge table separator tabs input select skeleton scroll-area sheet dropdown-menu sonner
```

## 2) Copy files
Unzip this pack at repo root. Overwrite existing files.

## 3) Remove old JS pages
If you still have these, remove or rename them to avoid route conflicts:
- apps/web/app/layout.js
- apps/web/app/page.js

## 4) Restart web
```bash
docker compose restart web
# or

docker compose up -d --build web
```
