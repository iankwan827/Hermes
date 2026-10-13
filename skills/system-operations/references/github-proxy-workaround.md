# GitHub 代理绕过方案

## 背景

在中国大陆，GitHub 的 HTTPS (443端口) 经常被防火墙阻断，但 ICMP ping 正常。这导致 `git pull/push` 超时失败。

## 已验证的代理列表

| 代理 | 地址 | pull | push | 备注 |
|------|------|------|------|------|
| ghfast.top | `https://ghfast.top/https://github.com/` | ✅ | ❌ 超时 | 2026-07-06 验证 |
| SOCKS5 (Clash) | `socks5h://127.0.0.1:7897` | ✅ | ✅ | 需 +SSL_NO_VERIFY |

## 完整工作流

### 方案 A：ghfast.top 代理

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

### 方案 B：SOCKS5 本地代理（Clash）

```bash
# 确保 gitconfig 中有代理配置
# [http] proxy = socks5h://127.0.0.1:7897
# [https] proxy = socks5h://127.0.0.1:7897

# macOS + LibreSSL 可能报 SSL_ERROR_SYSCALL，即使代理连通
# 解决方案：跳过 SSL 验证
GIT_SSL_NO_VERIFY=1 git fetch origin main
GIT_SSL_NO_VERIFY=1 git pull origin main --rebase
GIT_SSL_NO_VERIFY=1 git push origin main
```

**诊断顺序**：
```bash
# 1. ping 通？
ping -c 3 github.com

# 2. 代理通？
curl -x socks5h://127.0.0.1:7897 https://github.com -o /dev/null -w "%{http_code}"

# 3. git 通？
git fetch origin main

# 4. git SSL 失败？加 NO_VERIFY
GIT_SSL_NO_VERIFY=1 git fetch origin main
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

# 检查 git 代理配置
git config --get http.proxy
git config --get https.proxy
```

## 限制

- 代理仅支持 HTTPS 协议
- push 可能超时（代理服务器对大流量有限制）
- 不适合大文件传输（LFS）

## 2026-07-24 新增：macOS SSL 验证失败

**症状**：`GIT_SSL_NO_VERIFY=1` 前 git fetch/pull 报 `LibreSSL SSL_connect: SSL_ERROR_SYSCALL in connection to github.com:443`，但 curl 通过代理访问正常。

**原因**：macOS 的 LibreSSL 与 SOCKS5 代理配合时，SSL 握手可能被中间环节中断（可能是代理软件的 TLS 检查或网络链路问题）。

**解决**：`GIT_SSL_NO_VERIFY=1` 环境变量 + git 命令。

**不影响**：此操作只影响当前 git 命令，不影响系统级 SSL 设置。git 已配置的 credential store 不受影响。
