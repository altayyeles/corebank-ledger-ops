# UI Upgrade Pack (shadcn/ui) — Apply Instructions

This pack contains **ready-to-copy** files to upgrade the Web UI to a shadcn/ui dashboard style.

## Prereqs
- You already ran `npx shadcn@latest init` (New York + Zinc).
- You added components (button/card/badge/table/...)

## How to apply
1) Unzip at repo root (so it merges into `apps/web/...`)
2) Overwrite when prompted
3) Restart web:

```bash
docker compose restart web
# or
docker compose up -d --build web
```

## Files provided
- apps/web/app/layout.tsx
- apps/web/app/globals.css
- apps/web/components/top-nav.tsx
- apps/web/app/page.tsx
- apps/web/app/alerts/page.tsx
- apps/web/app/notifications/page.tsx
- apps/web/app/graph/page.tsx

## Notes
If you still use `layout.js/page.js` files, remove them or rename to avoid route conflicts.
