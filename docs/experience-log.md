# Hermes 使用经验日志

> 自动生成 by Hermes Cron Job — 2026-07-19

---

## 2026-07-19

### 踩坑记录
- [session-continuity] Hermes session 之间没有共享记忆，用户发现这是一大缺陷 → 已提交 session 持久化方案（Gateway 级别 + CLI 级别保存），PR: https://github.com/NousResearch/hermes-agent/pull/67272
- [session-search] session_search 默认 FTS5 搜索是 AND 语义，多词查询需用 OR 连接才能覆盖更广
- [course-notes-fusion] 子 agent 的 vision_analyze 结果可能完全产生幻觉（编造文字、错误天干地支）→ 主 agent 必须亲自验证 OCR 内容，不能反复重试同一个子 agent

### 新发现
- [session-continuity] Session 持久化方案已文档化：Gateway 级别 `_auto_save_session()` + CLI 级别 `_pre_save_session_from_db()`，触发点包括 session 超时、gateway 重启、/new /reset 命令
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

### Skill 更新
- 无新增更新

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

## 2026-07-16 ~ 2026-07-14（汇总自之前经验日志）

### 踩坑记录
- [GitHub同步] git push 超时 → 改用 `git push --timeout 120` 或分步操作
- [Cron] 定时任务 broken pipe → 检查 gateway 健康状态
- [pdd-edit] 编辑页面有必填属性不填无法提交；修改后必须立即提交否则丢失
- [pdd-price] 不同 SKU 进货价不同，定价前必须确认进货价

### 新发现
- [八字] 过三关 = 用速断 skill 做直断验证，不是做格局判定+用神忌神的详细分析（那是 Phase 2-3）
- [八字审核] 正官格的食伤是忌神不是用神；偏印格中正官是忌神不是用神
- [八字断语] 断语必须完整：需要前置条件+结论，不能只引用结论部分

---

## 跨期通用经验教训（从 Skills 提取）

### OCR/视觉相关
- **vision_analyze 的结果不能直接信任，必须交叉验证**（analyze-image skill）
- 深色背景课件用 vision_analyze 必定幻觉 → 直接调 Xiaomi API OCR
- 2000px slice height 是课件 OCR 最佳切片高度，不要压缩原图
- brew 安装的 llama-mtmd-cli 需要 `--jinja` 参数

### 子 Agent 管理
- 子 agent 的 vision 结果可能完全编造 → 主 agent 必须亲自验证
- 主 agent 发现子 agent 幻觉时应立即接管，不要反复重试同一个子 agent
- "查看分析"按钮有重复索引（最新作品区和近期作品区都会显示）

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

### 配置/环境
- Config 变更必须用 `hermes config set` CLI，不能直接编辑 YAML
- Python + MSYS 中文编码陷阱：format 字符串中的中文字符会导致 ValueError
- cron job 中 `execute_code` 被禁止，需用 terminal 执行 Python
- Microsoft Graph webhook 订阅 72 小时过期不会自动续期
- Teams 会议 transcript 不是会议结束后立即可用，需等 2-5 分钟
