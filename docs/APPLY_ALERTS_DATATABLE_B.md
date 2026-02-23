# Alerts DataTable Pack (B) — Apply

Upgrades Alerts page to a real **enterprise DataTable** (filter + sort + pagination) using TanStack Table.

## 1) Install deps (one-time)
```bash
cd apps/web
npm i @tanstack/react-table
npx shadcn@latest add table input button
```

## 2) Copy files
Unzip at repo root and overwrite.

## 3) Restart web
```bash
docker compose restart web
# or

docker compose up -d --build web
```
