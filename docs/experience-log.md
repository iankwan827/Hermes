# Hermes 使用经验日志

> 自动生成 by Hermes Cron Job — 2026-07-21

---

## 2026-07-21

### 踩坑记录
- [录音启动] 用户说「开始上课了开始录音」后不要追问「进去了没？」，直接执行录音并静默。用户原话「我都和你说开始上课了，你还问我进去了没有？你有病么」→ **教训：用户确认启动后，只执行不废话**（来源：session 20260721_110043）
- [执行价采集] 周二开盘价整体低于周一，平均节省5.01个百分点。等一天策略继续验证有效。星宸科技周二开盘110.00 vs 信号价91.85，追高19.76%异常高开→ **建议：追高>3%的股票考虑继续等待**（来源：session cron_fd972743a70e_20260721_093539）
- [风险监控] 本周扫描40只股票，27条公告中筛选出3条⚠️：福达合金控股股东减持计划、神火股份大股东持续减持、诺普信子公司涉新诉讼。其余24条为常规事项→ **教训：大部分公告是噪声，只报真正需要关注的**（来源：session cron_a9d626064115_20260721_090034）

### 新发现
- [八字语录] Day97-99 语录新增：七杀只做二把手（聪明不过伤官伶俐不过七杀）、辰戌冲需看库开与否影响婚姻、日支坐什么代表内心最在乎什么、客服部门找枭印最合适、七杀不会甘居人下（来源：session 20260721_110043）
- [第二十三课录音] 今天开始录第二十三课（来源：session 20260721_110043）

### 用户偏好更新
- **录音启动不追问**：用户说「开始上课了开始录音」后，直接执行录音并保持静默，不要问「进去了没？」或做多余确认（来源：session 20260721_110043）

### Skill 更新
- bazi-yulu: 追加 Day97-99 语录（5条）

---

## 2026-07-20

### 踩坑记录
- [course-notes-fusion] 笔记中八字排盘写成了复杂表格（四柱+藏干+十神+五行力量），用户明确只要一行简单格式「壬午 癸卯 丁丑 壬寅」→ **教训：记笔记只写一行八字，不搞花里胡哨的表格**（来源：session 20260720_075850）
- [browser-cdp] 访问政府网站（hrss.zhaoqing.gov.cn）需要用 Chrome CDP 模式，先杀已有 Chrome 再用临时 profile 启动 → 来源：session 20260720

### 新发现
- [执行价采集] 2026-07-20（周一）执行价采集：平均滑点 +2.18%，星宸科技 +20% 异常高开。第一池（稳健）整体表现优于第二池（成长），跨周末持有放大滑点
- [八字语录] Day96-99 语录新增：食伤人口才好但需七杀约束逻辑、官杀的威慑逻辑、食伤追星心态、印星食神佛系 vs 伤官急躁、偏印旺容易偏科

### 用户偏好更新
- **笔记格式**：八字案例只写一行（天干地支），不要做四柱表格、藏干、十神、五行力量等复杂排版。用户原话「就让你写这么简单一行，浪费了我那么多tokens」
- **肇庆一次性创业资助**：用户关注1万元资助政策，需要查具体金额和条件

### Skill 更新
- bazi-yulu: 追加 Day96-99 语录（5条）

---

## 2026-07-19

### 踩坑记录
- [session-continuity] Hermes session 之间没有共享记忆，用户发现这是一大缺陷 → 已提交 session 持久化方案（Gateway 级别 + CLI 级别保存），PR: https://github.com/NousResearch/hermes-agent/pull/67272
- [session-search] session_search 默认 FTS5 搜索是 AND 语义，多词查询需用 OR 连接才能覆盖更广
- [course-notes-fusion] 子 agent 的 vision_analyze 结果可能完全产生幻觉（编造文字、错误天干地支）→ 主 agent 必须亲自验证 OCR 内容，不能反复重试同一个子 agent
- [hermes-gateway-restart] `hermes gateway restart` 直接杀进程，不触发 graceful shutdown hooks → CLI 层面需在发 SIGTERM 前先保存 session（已实现 `_pre_save_session_from_db()`）

### 新发现
- [session-continuity] Session 持久化方案已文档化：Gateway 级别 `_auto_save_session()` + CLI 级别 `_pre_save_session_from_db()`，触发点包括 session 超时、gateway 重启、/new /reset 命令
- [session-continuity] 完整文档 `session-continuity-changes.md` 已推到个人同步仓库 `iankwan827/Hermes`，供 macOS ↔ Windows 通讯
- [八字语录] Day94-99 语录新增：食伤旺挑老板、便秘组合、羊刃查法与身强弱、地支自刑、找不到女朋友原因

### Skill 更新
- bazi-yulu: 新增 Day94-99 课程语录

---

## 2026-07-18

### 踩坑记录
- [course-notes-fusion] 课件无案例但转录稿有时，笔记必须包含转录稿案例（用户偏好）
- [GitHub同步] GitHub 同步任务曾因超时失败，需增加 timeout 设置

### 新发现
- [OCR方案] Lesson 21 深色背景课件直接调 Xiaomi API OCR，绕过 vision_analyze（后者对深色背景必定幻觉）
- [Agent协作] Agent5+Agent6 并行验证效率极高：Agent5 修正 10 处 + 标记 12 处 ⚠️，Agent6 发现 4 项遗漏
- [五阶段流程] 课程笔记五阶段流程完整跑通：Agent1→Agent7→Agent2+3→Agent5+Agent6→终稿三路合流，268 个 block 上传飞书 0 失败

---

## 2026-07-17

### 踩坑记录
- [vision_analyze] vision_tools.py 第 586 行 `_supports_media_in_tool_results` 检查了错误的属性 → **教训：要读源码找根因，不要用配置打补丁**
- [Cron] Cron 任务 broken pipe 错误 → 需检查 gateway 连接稳定性
- [pdd-store] 1688 一键铺货的 shadow DOM 组件无法可靠触发，必须用户手动操作
- [pdd-store] 店铺名禁用词：物美、优质、精品、名牌、官方等不能用；个人店不能卖食品、药品、美妆、3C 数码

### 新发现
- [course-notes-fusion] JSON 骨架架构：Agent1 先生成课程 JSON 骨架，Agent2/3 填充内容，比直接生成完整笔记更稳定
- [八字] 调候优先于扶抑：冬火夏金等极端情况需优先调候，不能机械套用扶抑法
- [bazi-geju] 三得法是初筛工具，不是最终判断（"天干无势、地支成势"会误判）；杂气月不能机械取本气为格
- [八字] 等一天策略：用户发来的课件/材料不要急于分析，先存档等第二天再处理，效果更好

### 用户偏好更新
- 课件无案例时笔记必须包含转录稿案例
- 不要用"完了""好了""停了"这类词，除非 ps 确认

### Skill 更新
- bazi-yulu: 新增课程语录条目
- douyin-download: 更新抖音下载流程
- huang-zihua-perspective: 更新黄子华视角 skill

---

## 跨期通用经验教训（从 Skills 提取）

### OCR/视觉相关
- **vision_analyze 的结果不能直接信任，必须交叉验证**（analyze-image skill）
- 深色背景课件用 vision_analyze 必定幻觉 → 直接调 Xiaomi API OCR
- 2000px slice height 是课件 OCR 最佳切片高度，不要压缩原图
- brew 安装的 llama-mtmd-cli 需要 `--jinja` 参数
- Whisper转录中文专有名词经常出错（如闾山→驴山），转录完必须校对关键术语再用

### 子 Agent 管理
- 子 agent 的 vision 结果可能完全编造 → 主 agent 必须亲自验证
- 主 agent 发现子 agent 幻觉时应立即接管，不要反复重试同一个子 agent

### Python/Node.js 调试
- pdb under pytest-xdist silently hangs → 用 `-p no:xdist`
- `PYTHONBREAKPOINT=0` 禁用所有断点
- `--inspect` vs `--inspect-brk`（后者在首行暂停）
- Port 碰撞 9229 → 用 `--inspect=0` 获取随机端口

### 八字系统
- 甲木见丁火 = 伤官（阳见阴），不是食神
- 甲木见丙火 = 食神（阳见阳），不是伤官
- 格局用神 ≠ 最终用神，必须 5 个五行逐个检查
- 大运起运年龄计算方式不同流派有差异
- 地支 index 从 0 还是从 1 开始容易搞混
- 八字巳月=5月5日立夏~6月5日芒种（不是6月）

### 配置/环境
- Config 变更必须用 `hermes config set` CLI，不能直接编辑 YAML
- Python + MSYS 中文编码陷阱：format 字符串中的中文字符会导致 ValueError
- cron job 中 `execute_code` 被禁止，需用 terminal 执行 Python
- Microsoft Graph webhook 订阅 72 小时过期不会自动续期
- Teams 会议 transcript 不是会议结束后立即可用，需等 2-5 分钟

### 用户沟通风格
- 用户说「开始上课了开始录音」后直接执行，不要追问确认
- 用户问「这是什么错误」时直接给答案，不要先搜文件再总结
- 用户改完文案就是终版，不加回删掉内容
- 用户说「我用XX故事讲解给你听」只取角度不取内容，不要写进文案
