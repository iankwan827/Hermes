---
name: vercel-deploy
description: "Vercel 项目部署和故障排查。CLI token 认证、部署到现有项目、Vite PWA 构建问题修复。触发方式：Vercel 部署、vercel login、404 icon、SW 注册失败、manifest 路径错误。"
tags: [vercel, deploy, vite, pwa, system]
version: 1.0.0
created: 2026-07-15
platforms: [windows]
---

# Vercel 部署与故障排查

Vercel CLI 操作 + Vite PWA 项目构建部署 + 常见前端部署问题排查。

---

## 一、Vercel CLI 认证

### Token 认证（推荐，免 OAuth 交互）

```bash
# ⚠️ --token 不能和 login 一起用
# ❌ vercel login --token xxx  → 报错

# ✅ 用环境变量（Token 见 references/user-vercel-projects.md）
VERCEL_TOKEN=vcp_89...Ec5j vercel whoami
VERCEL_TOKEN=vcp_89...Ec5j vercel projects ls
```

**获取 Token**：浏览器打开 https://vercel.com/account/tokens → Create Token

### 快速部署（一键命令）

```bash
# 八字排盘
cd "E:/SD/bazi/bazi_new_web" && VERCEL_TOKEN=*** vercel --prod --yes

# 三板斧
cd "E:/SD/bazi/sanbanfu" && VERCEL_TOKEN=*** vercel --prod --yes
```

### OAuth 登录（需要浏览器交互）

```bash
vercel login
# 给出链接 + code → 用户在浏览器打开授权
# ⚠️ CLI 必须保持运行等待回调，不能中断
# ⚠️ 浏览器授权成功 ≠ CLI 登录成功，CLI 必须收到回调才算
```

**Pitfall**：如果 PowerShell 里 `vercel login` 超时或被中断，浏览器授权了但 CLI 没收到 token，需要重新 login。

---

## 二、部署到现有项目

### 标准流程

```bash
cd /path/to/project

# 1. 拉取项目设置（必须，否则 CLI 不知道部署到哪个项目）
VERCEL_TOKEN=<token> vercel pull --yes

# 2. 部署到生产环境
VERCEL_TOKEN=<token> vercel --prod --name <project-name>
```

### ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| "No Project Settings found locally" | 没有 `.vercel/project.json` | 先跑 `vercel pull --yes` |
| 部署到了错误的项目 | 从子目录 deploy，CLI 自动创建新项目 | 回到项目根目录，用 `--name` 指定 |
| "Did you mean to deploy the subdirectory?" | CLI 检测到子目录有 build 输出 | 确认 cwd 是项目根目录 |

### 删除误创建的项目

```bash
echo "y" | VERCEL_TOKEN=<token> vercel project rm <project-name>
```

---

## 三、Vite + PWA 项目构建

### 项目结构（典型）

```
project/
├── vite.config.js          # Vite 配置（含 PWA 插件）
├── package.json            # "build": "vite build"
├── public/                 # 静态资源（原样复制到 dist）
│   ├── manifest.json
│   └── assets/icon.png
├── dist/                   # 构建输出（Vercel 部署这个）
│   └── bazi/
│       ├── index.html
│       ├── sw.js           # Workbox 生成
│       ├── manifest.json
│       └── assets/
│           └── manifest-*.json  # Vite PWA 插件生成
└── .vercel/
    └── project.json        # vercel pull 生成
```

### ⚠️ 关键 Pitfall：非根路径部署时 icon 路径必须绝对

当 `vite.config.js` 设置了 `base: '/bazi/'`（非根路径部署）时：

```js
// ❌ 错误：相对路径，PWA 插件不会拼上 base
manifest: {
    icons: [{ src: 'assets/icon.png', ... }]
}

// ✅ 正确：绝对路径
manifest: {
    icons: [{ src: '/bazi/assets/icon.png', ... }]
}
```

**症状**：浏览器报 `GET /assets/icon.png 404`，SW 注册失败。
**根因**：Vite PWA 插件生成的 `assets/manifest-*.json` 里 icon 路径是 `/assets/icon.png`（缺少 `/bazi/` 前缀）。

### 紧急修复（不重新构建）

如果线上已经出问题，可以直接改 `dist/` 里的文件再部署：

```bash
# 找到 PWA 生成的 manifest
ls dist/bazi/assets/manifest-*.json

# 改 icon 路径（用 patch 工具）
# 把 /assets/icon.png → /bazi/assets/icon.png
```

---

## 四、Service Worker 问题排查

### 常见 SW 错误

| 错误 | 含义 |
|------|------|
| `SW unregistered` | SW 注册失败 |
| `Only the active worker can claim clients` | SW 不是当前活跃 worker，无法 claim |
| `GET /assets/icon.png 404` | manifest 引用的 icon 文件不存在 |
| `Cache cleared: workbox-precache-v2-*` | Workbox 清除了旧缓存 |

### 排查步骤

1. **检查 icon 路径**：打开 DevTools → Application → Manifest → 看 icon URL 是否 404
2. **检查 SW 文件**：DevTools → Application → Service Workers → 看状态
3. **检查 precache 列表**：看 `sw.js` 里 `precacheAndRoute` 的 URL 列表
4. **强制更新**：DevTools → Application → Service Workers → Unregister → Ctrl+Shift+R

### Vercel SW 缓存 Headers

在 `vercel.json` 中为 SW 设置正确 headers：

```json
{
    "source": "/bazi/sw.js",
    "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" },
        { "key": "Service-Worker-Allowed", "value": "/bazi/" }
    ]
}
```

`Service-Worker-allowed` 头告诉浏览器这个 SW 可以控制 `/bazi/` 路径下的页面。

---

## 五、Vite 动态导入 + Missing Export 调试

### 问题模式

`ui_render.js` 通过 `await import('./bazi_logic.js')` 动态加载逻辑模块，把导出的函数赋值给局部变量。如果某个函数忘记加 `export`，动态导入拿到的是 `undefined`，运行时调用就报 `TypeError: xxx is not a function`。

minified 后变量名被压缩（如 `y2 is not a function`），无法直接定位。

### 排查步骤

1. 看报错的 minified 文件名（如 `ui_render-xxx.js`）
2. 找对应的源文件（`js/ui_render.js`）
3. 找它 `await import(...)` 导入的模块（如 `bazi_logic.js`）
4. 在源模块里 grep 报错函数名，确认有 `export` 关键字
5. 常见遗漏：`function xxx(...)` 而非 `export function xxx(...)`

### 修复

```bash
# 在源模块里加 export
grep -n "function calculateMarriageStatus" js/bazi_logic.js
# 改为 export function calculateMarriageStatus(...)
```

---

## Pitfalls

- ⚠️ `vercel login --token` 不可用，必须用 `VERCEL_TOKEN=<token>` 环境变量
- ⚠️ `vercel pull --yes` 是部署到现有项目的前提，没有它 CLI 不知道目标项目
- ⚠️ 从子目录 deploy 会创建新项目，必须回到项目根目录
- ⚠️ Vite PWA 插件的 icon 路径：非根部署时必须用绝对路径 `/base/assets/icon.png`
- ⚠️ `dist/` 是构建输出，改了源码必须重新 build 才会生效（除非直接改 dist 文件紧急修复）
- ⚠️ 浏览器 OAuth 授权成功 ≠ CLI 登录成功，CLI 必须保持运行接收回调
- ⚠️ 动态 `import()` 的模块里，函数必须有 `export`，否则 minified 后报 "is not a function"
- ⚠️ 项目有多个 manifest.json（根目录、public/、dist 内 Vite 生成的），改一个不够，需全部一致
- 💡 用户偏好：agent 应直接用 CLI 部署，不要让用户手动拖文件到 Vercel
- ⚠️ `vercel --prod` 部署后，自定义域名别名可能仍指向旧部署。用 `vercel inspect https://domain` 检查，必要时 `vercel promote <latest-url> --yes` 手动更新
- ⚠️ 从 `dist/` 子目录部署会创建名为 "dist" 的新项目，必须从项目根目录部署或用 `--name` 指定
- ⚠️ 语法错误（如孤立 `*/`、IIFE 缺 `}`）会导致整个文件解析失败，后续所有变量 undefined。排查顺序：先 `node --check` 找语法错误，再查具体变量
