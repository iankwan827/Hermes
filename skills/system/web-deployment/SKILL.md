---
name: web-deployment
description: |
  Vercel deployment, PWA configuration, and frontend debugging workflows.
  Covers: Vercel CLI auth/deploy/promote, Vite PWA manifest issues, Service Worker caching,
  JS module export debugging, and multi-project Vercel setups.
  Triggered by: deploying to Vercel, PWA errors, SW issues, 404 on assets, "deploy" tasks.
version: 1.0.0
created: 2026-07-15
platforms: [windows]
---

# Web Deployment & Debugging

## Vercel CLI

### Authentication

Token-based auth bypasses OAuth. Get token from https://vercel.com/account/tokens.

```bash
# Set token as env var for all subsequent vercel commands
export VERCEL_TOKEN="vcp_xxxxx"

# Verify login
vercel whoami
```

⚠️ `vercel login --token` does NOT work — the `--token` flag is rejected by the login command.

### Deploy

```bash
# Link project first (one-time)
cd /path/to/project && vercel pull --yes

# Deploy to production
vercel --prod --yes
```

### Custom Domain Alias Issue

⚠️ **Critical pitfall**: Drag-and-drop uploads and some CLI deploys do NOT automatically update the custom domain alias. The alias may point to an old deployment while `bazi-new-web.vercel.app` shows the latest.

**Symptom**: `www.shiyibazi.top` shows old code, but `bazi-new-web.vercel.app` shows new code.

**Fix**: Promote the latest deployment to production:
```bash
vercel promote <latest-deployment-url> --yes
```

**Verify**: Check which deployment the custom domain points to:
```bash
vercel inspect https://www.shiyibazi.top
```

### Multi-Project Vercel Setup

The shiyibazi.top domain hosts multiple sub-projects (bazi, qimen, sanbanfu) under one Vercel project (`bazi-new-web`). The `vercel.json` uses rewrites to route:
- `/bazi/*` → local `dist/bazi/` files
- `/qimen2/*` → `taigongqimen.vercel.app`
- `/sanbanfu/*` → `sanbanfu.vercel.app`

**When deploying bazi-new-web**: Only affects `/bazi/` paths. Other sub-projects are separate Vercel projects.

## Vite + PWA

### Manifest Icon Path Bug

When using `vite-plugin-pwa` with `base: '/bazi/'`, relative icon paths in the manifest config do NOT resolve correctly:

```js
// ❌ BROKEN — Vite PWA generates /assets/icon.png instead of /bazi/assets/icon.png
manifest: {
    icons: [{ src: 'assets/icon.png', ... }]
}

// ✅ CORRECT — Use absolute paths
manifest: {
    icons: [{ src: '/bazi/assets/icon.png', ... }]
}
```

**Why**: The PWA plugin doesn't always prepend the `base` path to manifest icon `src` values. The generated `assets/manifest-*.json` ends up with wrong paths.

### Service Worker Caching

After deploying new code, browsers may serve old cached SW files.

**Symptom**: Error references old JS filename (e.g., `ui_render-CFzwE9kN.js`) but build output has new name (`ui_render-TEIiVyi-.js`).

**Fix**: Tell user to:
1. `Ctrl + Shift + R` (hard refresh)
2. Or: DevTools → Application → Service Workers → Unregister → refresh

### Workbox Precache Icon Exclusion

If icon.png causes SW install failures, exclude it from precache:
```js
workbox: {
    globIgnores: ['**/icon.png'],
}
```

## JS Module Debugging

### Missing Export

**Symptom**: `TypeError: xxx is not a function` in minified bundle, where `xxx` is a function loaded dynamically.

**Cause**: Function defined but not exported from its module. Dynamic `import()` returns `undefined` for non-exported functions.

**Debug**: Check if the function has `export` keyword in its source file:
```bash
grep -n "function functionName" js/module.js
# If no "export" prefix, add it
```

**Fix**: Add `export` to the function definition.

### Stray Comment Markers (High-Impact Bug Pattern)

**Symptom**: `SyntaxError: Unexpected token '*'` or `Unexpected token ')'`, followed by `ReferenceError: XXX is not defined` for constants defined AFTER the syntax error.

**Root cause**: A `*/` without matching `/*`, or `/*` without matching `*/`, anywhere in a JS file. This causes the ENTIRE file to fail parsing. Constants defined before the stray marker work; everything after is undefined.

**Why it's tricky**: The browser reports the error at the stray marker location, but the USER sees "XXX is not defined" errors downstream. The real fix is the stray marker, not adding the missing variable.

**Debug pattern**:
```bash
# 1. Find stray markers (no matching pair)
grep -n "^/\*\|^\*/" js/file.js

# 2. Syntax check with Node
node --check js/file.js
# Output shows exact line of first syntax error

# 3. If syntax passes but browser still errors → browser cache issue
curl -s "https://site.vercel.app/js/file.js" | head -5
# Verify deployed version matches local
```

**Common locations**:
- Someone commented out a block with `/* ... */` but left a stray `*/` nearby
- Copy-paste left orphaned `*/` after a code block
- An IIFE's closing `})();` has extra whitespace breaking parsing

### IIFE Brace Mismatch

**Symptom**: Syntax error at the IIFE closing `})();` line, but the actual problem is a missing `}` somewhere inside the function body.

**Debug** — count brace depth programmatically:
```bash
node -e "
const fs = require('fs');
const code = fs.readFileSync('js/file.js', 'utf8');
const lines = code.split('\n');
let depth = 0;
for (let i = 0; i < lines.length; i++) {
  const prevDepth = depth;
  for (const ch of lines[i]) {
    if (ch === '{') depth++;
    if (ch === '}') depth--;
  }
  if (depth !== prevDepth) {
    console.log('L' + (i+1) + ': ' + prevDepth + '->' + depth);
  }
}
console.log('Final depth:', depth);
"
# Final depth should be 0. If 1, there's an extra unclosed {.
```

**Pattern**: If `calculate` function opens at depth 1→2, it should close at 2→1. If it closes at 3→2, there's an extra `{` inside that never closed.

### Batch Syntax Check

When a project has many JS files loaded by one HTML page:
```bash
grep 'src="js/' page.html | sed 's/.*src="\([^"]*\)".*/\1/' | sed 's/\?.*//' | while read f; do
  result=$(node --check "path/to/$f" 2>&1)
  if [ $? -ne 0 ]; then
    echo "FAIL: $f"
    echo "$result" | head -3
  fi
done
```

## Pitfalls

### Vercel CLI creates new project when deploying from subdirectory
Deploying from `dist/` directory creates a new project called "dist" instead of updating the target project. Always deploy from the project root, or use `--name` flag.

### `vercel build` vs `vercel --prod`
- `vercel build` only builds, doesn't deploy
- `vercel --prod` builds AND deploys
- Use `vercel --prod --yes` for non-interactive deployment

### Browser tool / OpenCLI may not be available
Chrome CDP port 9222 may not be open, and OpenCLI Browser Bridge extension may be disconnected. Vercel CLI with token auth is the reliable fallback for Vercel operations.
