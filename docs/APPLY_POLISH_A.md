# Enterprise Polish A Pack — Apply

Adds **Dashboard polish (A)**:
- Demo IDs card (customer/account IDs + IBANs) with copy buttons + localStorage save
- Stepper/timeline for “Bu demo ne gösteriyor?”
- KPI icons + “canlı/dikkat/kritik” pills

## Apply
1) Unzip at repo root and overwrite.
2) Ensure deps exist (one-time):

```bash
cd apps/web
npm i lucide-react
npx shadcn@latest add input button card badge separator
```

3) Restart web:
```bash
docker compose restart web
# or

docker compose up -d --build web
```

## Notes
- Demo values are pre-filled with your latest seed output but editable and saved in browser.
