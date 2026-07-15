# Vercel 项目详情

## 账号
- Username: guanmian0720-4262
- Team: iankwans-projects

## 项目列表

| 项目名 | 域名 | 说明 |
|--------|------|------|
| bazi-new-web | www.shiyibazi.top | 八字排盘主站（Vite+PWA，部署在 /bazi/ 子路径） |
| taigongqimen | taigongqimen.vercel.app | 奇门遁甲 |
| sanbanfu | sanbanfu.vercel.app | 三板斧 |
| sanbanfu2 | sanbanfu2.vercel.app | 三板斧2 |

## 项目源码目录

| 项目名 | 源码目录 |
|--------|---------|
| bazi-new-web | E:/SD/bazi/bazi_new_web |
| sanbanfu | E:/SD/bazi/sanbanfu |
| sanbanfu2 | E:/SD/bazi/sanbanfu/js/biao/sanbanfu2 |
| bazi | bazi-teal.vercel.app | 旧版八字（已弃用？） |

## bazi-new-web 项目结构

- 源码：`E:\SD\bazi\bazi_new_web`
- Vercel Token：存储在 .env 或系统环境变量中（不入库）
- 部署命令：`cd E:\SD\bazi\bazi_new_web && VERCEL_TOKEN=$VERCEL_TOKEN vercel --prod --yes`
- 构建工具：Vite + vite-plugin-pwa
- 构建输出：`dist/bazi/`
- Node 版本：24.x
- 部署方式：手动拖拽 / Vercel CLI

### 路由（vercel.json rewrites）
- `/bazi/*` → `/bazi/index.html`（SPA 路由）
- `/check` → `/bazi/check.html`
- `/qimen2/*` → taigongqimen.vercel.app（代理）
- `/sanbanfu/*` → sanbanfu.vercel.app（代理）
- `/sanbanfu2/*` → sanbanfu2.vercel.app（代理）

### Vite 配置关键点
- `base: '/bazi/'`（非根路径部署）
- `build.outDir: 'dist/bazi'`
- PWA manifest icon 必须用绝对路径 `/bazi/assets/icon.png`
