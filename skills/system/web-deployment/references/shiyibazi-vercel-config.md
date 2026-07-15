# shiyibazi.top Vercel Configuration

## Projects

| Project | URL | Source |
|---------|-----|--------|
| bazi-new-web | www.shiyibazi.top | E:\SD\bazi\bazi_new_web |
| sanbanfu | sanbanfu.vercel.app | E:\SD\bazi\sanbanfu |
| sanbanfu2 | sanbanfu2.vercel.app | E:\SD\bazi\sanbanfu\js\biao\sanbanfu2 |
| taigongqimen | taigongqimen.vercel.app | (separate) |

## Vercel Token

Token stored in session. Use: `VERCEL_TOKEN=vcp_...Ec5j`

## bazi-new-web Structure

- Framework: Vite + vite-plugin-pwa
- Base path: `/bazi/`
- Build output: `dist/bazi/`
- Multi-app: bazi, qimen, sanbanfu all under one Vercel project
- Routing: vercel.json rewrites handle sub-path routing

### Key Files
- `vite.config.js` — Vite config with PWA plugin (manifest icons must use absolute paths)
- `vercel.json` — Headers, redirects, rewrites for all sub-projects
- `public/manifest.json` — PWA manifest (correct paths)
- `manifest.json` (root) — Used by Capacitor/Android builds

### Deploy Command
```bash
cd E:/SD/bazi/bazi_new_web && VERCEL_TOKEN=*** vercel --prod --yes --name bazi-new-web
```

After deploy, verify custom domain points to latest:
```bash
vercel inspect https://www.shiyibazi.top
# If pointing to old deployment:
vercel promote <latest-url> --yes
```

## sanbanfu Structure

- Static HTML (no build step)
- Main entry: `paipan.html` (loaded via vercel.json rewrite from `/sanbanfu/`)
- JS files loaded via `<script>` tags (no bundler)
- Known issues: stray `*/` comment markers in `js/bazi_logic.js` and `js/biao/bazi_logic.js`
- `js/biao/喜用忌.js` — IIFE pattern, watch for brace mismatches

### Deploy Command
```bash
cd E:/SD/bazi/sanbanfu && VERCEL_TOKEN=*** vercel --prod --yes --name sanbanfu
```

## Common Debugging Sequence

1. `node --check js/file.js` — find syntax errors
2. `grep -n "^/\*\|^\*/" js/file.js` — find stray comment markers
3. `curl -s "https://site.vercel.app/js/file.js" | head -5` — verify deployed version
4. `vercel inspect https://domain` — check which deployment is live
5. `vercel promote <latest-url> --yes` — fix alias if pointing to old deployment