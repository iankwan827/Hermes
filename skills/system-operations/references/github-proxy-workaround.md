# GitHub 代理绕过方案

## 背景

在中国大陆，GitHub 的 HTTPS (443端口) 经常被防火墙阻断，但 ICMP ping 正常。这导致 `git pull/push` 超时失败。

## 已验证的代理列表

| 代理 | 地址 | pull | push | 备注 |
|------|------|------|------|------|
| ghfast.top | `https://ghfast.top/https://github.com/` | ✅ | ❌ 超时 | 2026-07-06 验证 |

## 完整工作流

```bash
# 设置代理（临时，仅对 git 生效）
git config --global url."https://ghfast.top/https://github.com/".insteadOf "https://github.com/"

# 拉取
git pull origin main --rebase

# 清理代理
git config --global --unset url."https://ghfast.top/https://github.com/".insteadOf

# 推送（直连）
git push origin main
```

## 其他候选代理

如果 `ghfast.top` 失效，可尝试：
- `https://ghproxy.cn/https://github.com/`
- `https://mirror.ghproxy.com/https://github.com/`

配置方式相同，替换 URL 即可。

## 诊断

```bash
# 测试代理是否可达
curl -s --connect-timeout 10 https://ghfast.top/https://github.com/iankwan827/Hermes.git/info/refs?service=git-upload-pack

# 测试直连是否可用
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 https://github.com
```

## 限制

- 代理仅支持 HTTPS 协议
- push 可能超时（代理服务器对大流量有限制）
- 不适合大文件传输（LFS）
