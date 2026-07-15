# Vercel 项目清单

## 项目列表

| 项目名 | 域名 | 源码位置 | 说明 |
|--------|------|----------|------|
| bazi-new-web | www.shiyibazi.top / shiyibazi.top | E:\SD\bazi\bazi_new_web | 八字排盘主站，Vite + PWA，子路径 /bazi/ |
| sanbanfu | sanbanfu.vercel.app | E:\SD\bazi\sanbanfu | 三板斧，纯静态 JS，直接上传 dist |
| sanbanfu2 | sanbanfu2.vercel.app | E:\SD\bazi\sanbanfu\js\biao\sanbanfu2 | 三板斧 v2 |
| taigongqimen | taigongqimen.vercel.app | — | 奇门遁甲 |
| bazi | bazi-teal.vercel.app | — | 旧版八字（已弃用） |

## 认证

用户 Vercel 账号：guanmian0720-4262 (iankwans-projects)
Token 创建页面：https://vercel.com/account/tokens

```bash
VERCEL_TOKEN=<token> vercel whoami
```

## 部署命令

### bazi-new-web（Vite 项目，需 build）
```bash
cd E:/SD/bazi/bazi_new_web
VERCEL_TOKEN=<token> vercel pull --yes
VERCEL_TOKEN=<token> vercel --prod --yes --name bazi-new-web
```

### sanbanfu（纯静态，直接上传）
```bash
cd E:/SD/bazi/sanbanfu
VERCEL_TOKEN=<token> vercel --prod --yes --name sanbanfu
```

## 别名更新

部署后如果自定义域名仍指向旧版本：
```bash
# 查看当前指向
VERCEL_TOKEN=<token> vercel inspect https://<domain>

# 更新到最新
VERCEL_TOKEN=<token> vercel promote <new-deployment-url> --yes
```

## bazi-new-web 的 vercel.json 路由

该项目托管多个子应用，通过 rewrites 路由：
- `/bazi/*` → 本地 bazi 应用
- `/qimen2/*` → 代理到 taigongqimen.vercel.app
- `/sanbanfu/*` → 代理到 sanbanfu.vercel.app
- `/sanbanfu2/*` → 代理到 sanbanfu2.vercel.app

## 历史踩坑记录

### sanbanfu 项目（2026-07-15）
- `js/biao/bazi_logic.js` 第100行：孤立 `*/`（无匹配 `/*`）→ 语法错误 → GAN/TEN_GODS 全部 undefined
- `js/bazi_logic.js` 第590行：同样的孤立 `*/`
- `js/bazi_logic.js` 第1771行：`WX_RELATION` 被 `/* */` 注释掉 → 运行时 undefined
- `js/biao/喜用忌.js` 第139行：IIFE `calculate` 函数缺少关闭 `}` → 括号深度不为0
- `js/god_strength.js`：`WangShuaiEngine.calculate()` 返回 `{ detail, summary }` 对象，但调用方直接当数组用 `.filter()` → 需取 `.detail` 属性

### bazi-new-web 项目（2026-07-15）
- `vite.config.js`：PWA manifest icon 路径用相对路径 `assets/icon.png` → 子路径部署时 404 → 改为 `/bazi/assets/icon.png`
- `js/bazi_logic.js`：`calculateMarriageStatus` 缺少 `export` → 调用方拿到 undefined
