# Hermes 使用经验日志

> 自动同步，基于最近3天会话数据整理。

---

## 2026-07-02

### 踩坑记录
- [飞书集成] upload_notes.py 的 refresh_token() 函数把 app_id+app_secret 放在 request body 里，但 OIDC refresh 端点要求 tenant_access_token 作为 Bearer 头 → 返回 `{"code": 20014, "message": "The app access token passed is invalid"}` → 修复：先获取 tenant_access_token，再用它作为 Bearer 头刷新 user token
- [飞书集成] tenant_token 创建的 spreadsheet 默认只有应用自己能访问，用户看不到 → 必须主动分享给用户：`POST /drive/v1/permissions/{token}/members?type=sheet`，body 含 `member_type: openid, perm: full_access`

### 新发现
- [飞书集成] tenant_token 也能创建 spreadsheet（已验证 2026-07-02），不需要 user_access_token
- [飞书集成] OAuth callback 有时收不到，tenant_token 可作为 fallback 完成大部分操作（创建表格、写入数据、创建文档），不要卡在 OAuth 上
- [飞书集成] upload_notes.py 的 🎙️ 标记和内容必须分两行，同行会导致 callout 为空显示"···"
- [飞书集成] Spreadsheet sheet_id 必须查询，不能用 "Sheet1"，否则报 "sheetId not found"
- [飞书集成] Spreadsheet 写入行数必须匹配 range，超出报 `90202 range in request is wrong`
- [飞书集成] 清空 spreadsheet 行区域不能传空数组 `[]`（报 `90215 rows equals 0`），要传等量空字符串行
- [飞书集成] 用户偏好紧凑表格格式：五行做列、维度做行（如五行性格身材表），比十天干每行一个信息密度更高

### 用户偏好更新
- 转录必须用 gemma（llama.cpp + gemma-4-E4B-it），不能用 whisper
- 笔记上传飞书：🎙️标记和内容必须分两行（🎙️ **讲师解读**\n内容），不能放同一行
- 八字内容组织：性格分类用十天干（甲乙丙丁...），不是五行（金木水火土）

### Skill 更新
- `feishu-integration` 新增 pitfalls 15-24（OAuth fallback、表格格式、权限分享、sheet_id 查询等），更新 Token Refresh Bug 修复文档

---

## 2026-07-01

### 踩坑记录
- 无新增踩坑记录

### 新发现
- 风险监控：20只持仓无重大风险事件（担保/质押/诉讼进展/解禁均属常规）

### Skill 更新
- 无

---

## 2026-06-30

### 踩坑记录
- [选股系统] 南大光电极端滑点 +15.21%，成长股追高风险显著 → 选股需区分稳健池/成长池风险差异
- [选股系统] 周一开盘平均滑点 +0.59%，日内22跌vs18涨偏弱 → 周二开盘更优（平均-0.71%，省1.29pp）

### 新发现
- 周二开盘 vs 周一：23/40只更便宜(57.5%)，平均滑点从 +0.59% 降至 -0.71%，等一天可省 1.29 个百分点
- 第二池(成长股)等待一天优势更明显：平均差异 -2.42%，vs 第一池 -0.19%

### 用户偏好更新
- 录音流程极简化：启动 → 确认 → 完事，不反复测试

---

## 2026-06-29

### 踩坑记录
- [DingTalk直播] 进房间时未使用 skill 坐标 → 用户纠正后改用 cliclick 坐标点击
- [选股系统] 第二池(成长股)追高风险显著高于第一池(稳健股)：国瓷材料 +6.99%、南大光电 +6.09%

### 新发现
- 周一开盘平均滑点 +0.59% 整体可控，但日内偏弱，追高风险在盘中暴露
- 佛塑科技大股东质押比例未披露需关注；四川黄金/株冶集团减持已完成
- 录音目录纠正：用户说"不用修正，就按本地的文件夹"，不要自作主张改路径

---

## 2026-06-28

### 踩坑记录
- [LLM Provider] 充值后 credential_pool 需手动重置 + 重启 gateway（401/402错误） → 需同时执行 config set + gateway restart
- [LLM Provider] 从 7 个 SKILL.md 新提取 26 条踩坑记录（涵盖 llm-provider-fix、dingtalk-live、teams-meeting 等）
- [历史整合] 06-17 至 06-27 历史踩坑记录整合精简 47 条

### 新发现
- LLM 401/402/403 错误有标准诊断流程，关键在于 credential_pool 重置时机

### Skill 更新
- **新建** `llm-provider-fix` skill：401/402/403 错误诊断与修复流程
- **更新** `hermes-agent` skill
- **更新** `douyin-download` skill

---

## 2026-06-27

### 踩坑记录
- 无新增踩坑记录

### 新发现
- 八字宫位分析法：分析六亲不看对应十神旺不旺，而是看宫位上的内容对十神的作用
- 选股系统 V3：评分和风险完全分离，风险是诊断工具不是门卫
- 飞书表格统一：第一池补充 N-T 列与第二池对齐
- 六合合化条件研究：紧贴力量大、隔位减半，合喜得助力 / 合忌是拖累

### Skill 更新
- `bazi-zhiduan` 新增进阶断语速查 + 修正宫位星神配合判断
- `bazi-sales-*` 8 个 agent 重构为八层体系

---

## 用户核心偏好（持续有效）

1. **录音不要反复测试**，确认录到就开始
2. 对「失忆」极度敏感 → 每次操作前必须先查现有 skill
3. **配置变更必须用 `hermes config set`**
4. 进度汇报只在 50%、80%、100% 时报告
5. 用户改完文案就是终版，不要自作主张加回删掉的内容
6. 转录必须用 gemma（llama.cpp + gemma-4-E4B-it），不能用 whisper
7. 八字性格分类用十天干，不是五行
8. 笔记上传飞书：🎙️标记和内容必须分两行
9. 飞书创建表格不是文档（spreadsheet ≠ document）
10. 用户偏好紧凑表格格式（五行做列、维度做行）

---

## 常见陷阱速查

| 陷阱 | 解决方案 |
|------|----------|
| LLM 401/402 充值后仍报错 | 重置 credential_pool + 重启 gateway |
| 飞书 bot 401 ≠ Feishu API 401 | 前者是 LLM provider 问题，后者是 token 过期 |
| 飞书 OAuth callback 收不到 | 用 tenant_token 作为 fallback |
| 飞书表格用户看不到 | 主动分享权限 `permissions/{token}/members` |
| 飞书 sheet_id 用 "Sheet1" | 必须先查询实际 sheet_id |
| 飞书 🎙️ callout 为空 | 标记和内容必须分两行 |
| 选股追高风险 | 成长池 > 稳健池，周二开盘通常优于周一 |
| 录音目录路径 | 按用户指定的本地文件夹，不要自作主张改 |
| 杀 Python 进程误杀自己 | 先 ps aux | grep 找 PID，精准 kill |
| config.yaml 直接编辑不生效 | 必须用 `hermes config set` |

---

*本日志由 Hermes 经验同步 cron 任务自动生成*
