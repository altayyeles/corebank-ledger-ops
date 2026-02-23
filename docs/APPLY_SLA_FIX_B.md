# B Paketi — SLA Sayfası Crash Fix + Enterprise Görünüm

Bu paket şunları düzeltir:
- `data.map is not a function` hatasını kesin olarak önler (Array.isArray guard)
- SLA ekranını shadcn enterprise tasarıma taşır (Card + Table + Badge)
- Beklenmeyen API cevabını ekranda debug JSON olarak gösterir

## Kurulum
1) Zip'i repo köküne çıkar ve overwrite et.
2) Gerekli shadcn component'leri yoksa (bir defalık):

```bash
cd apps/web
npx shadcn@latest add card table badge skeleton
```

3) Web'i yeniden başlat:

```bash
docker compose restart web
# veya

docker compose up -d --build web
```
