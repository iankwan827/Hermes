# Hermes 使用经验日志

## 2026-07-14 ~ 2026-07-17

---

### 踩坑记录

#### 🔴 严重问题

1. **vision_analyze 源码级 Bug** — `vision_tools.py` 第586行 `_supports_media_in_tool_results` 检查了 `supports_vision`（True）而非 `supports_vision_tool_messages`（False for xiaomi provider），导致 `vision_analyze` 加载工具结果中的图片失败。`browser_vision` 截图正常。曾尝试修改 auxiliary.vision 配置"修复"，但那只是巧合触发了替代代码路径。**教训：不要用配置打补丁，要读源码找根因。**
   - 来源：session_search 2026-07-14

2. **GitHub 同步脚本超时** — `github-sync.sh` 120秒超时失败。大型仓库或网络不佳时需要更长超时。
   - 来源：session_search 2026-07-16

3. **Cron job broken pipe** — 选股脚本全部成功执行，但 cron agent 投递最终报告时遇到 transient network error，报 broken pipe。**不是脚本 bug，是网络抖动。**
   - 来源：session_search 2026-07-17

#### 🟡 中等问题

4. **vision_analyze 复杂表格识别失败** — 女命分级表等复杂表格，vision_analyze 返回错误内容。**备用方案：用 tesseract OCR。**
   - 来源：session_search 2026-07-15

5. **转录稿 grep 搜索遗漏** — 50k+ 字符的转录稿，grep 可能遗漏短内容。**必须逐段阅读。**
   - 来源：session_search 2026-07-15

6. **深色背景课件 vision_analyze 必定幻觉** — 深色背景的课件截图，vision_analyze 必然产生幻觉。**必须用 Tesseract + 反转颜色。**
   - 来源：skill: course-notes-fusion

7. **录音设备冲突** — 录音进行中时，音量检测失败（设备被录音进程独占）。这是预期行为，不是录音故障。
   - 来源：session_search 2026-07-17

8. **record.py 首次保存延迟** — record.py 每5分钟保存一次文件。启动后目录为空是正常的，需等待第一个保存周期。
   - 来源：session_search 2026-07-17

#### 🟢 已验证的经验

9. **调候优先于扶抑** — 夏季出生的八字，取用神时调候（季节性调整）优先级高于扶抑（日主强弱）。Lesson 17 Case 2 验证。
   - 来源：skill: bazi-system

10. **等一天策略（Wait-one-day）** — 周二开盘价 87.5% 比周一便宜，平均多省5个百分点。
    - 来源：skill: stock-screener

---

### 新发现

| 发现 | 来源 | 日期 |
|------|------|------|
| course-notes-fusion 架构升级：Agent1 输出 JSON 骨架，Agent2+3 按"合同"填充内容，解决多页幻灯片编号混乱问题 | session_search | 2026-07-15 |
| 子 agent 的 vision_analyze 结果不可靠，必须自己逐片验证 | skill: course-notes-fusion | 2026-07-15 |
| 财经类话题标题必须用悬念钩子，不能科普式平铺直叙（视频7数据验证） | skill: video-content-audit | 2026-07-14 |
| 开头前2秒决定生死（2s跳出率>30%算法不推），推荐页<60%说明算法不感兴趣 | skill: video-content-audit | 2026-07-14 |
| lesson 20 笔记处理：课件含前一课内容时需小心去重 | session_search | 2026-07-16 |
| ffmpeg avfoundation 假录——计时器显示录了N秒但文件只有几秒，macOS 已知问题 | skill: macos-audio-recording | — |
| akshare 安装到 --user 不被 venv 的 python 看到，必须在 venv 内安装 | skill: stock-screener | — |

---

### 用户偏好更新

- **交付标准高**：一次交付完成，不要半成品承诺
- **时间估计要诚实**：不给乐观估计
- **不要反复确认**：直接执行，用户风格直接
- **笔记整理只改本地**：除非明确要求，否则不上传飞书
- **文案修改 = 最终版**：用户改过的内容就是定稿
- **23:00 后算子时**：八字排盘时，23:00 后的出生时间算次日子时
- **配置修改用 hermes config set**：不要直接编辑 yaml
- **飞书笔记必须忠实讲师原话**：不能AI改写课件原文
- **不要自作主张修改笔记文件**：用户对未经许可的修改极度敏感

---

### Skill 更新

#### course-notes-fusion（课程笔记融合）— 架构重大升级
- Agent1 从输出 markdown 改为输出 JSON 骨架（`课件结构.json`）
- Agent2+3 按 JSON"合同"填充 📋/🎙️ 内容
- 每张幻灯片的章节独立编号，解决跨页编号混乱
- 新增：子 agent vision_analyze 结果不可靠的警告

#### video-content-audit（视频文案审核）— 新增数据驱动规则
- 财经类标题必须用悬念钩子
- 开头2秒决定生死
- 推荐页比例、完播率等指标纳入审核

#### stock-screener（选股系统）— 新增46条踩坑
- CSV 前导零丢失、系统代理阻断 API、BOM 头处理
- 风险监控关键词精度要求
- B规则追踪用持久化 JSON（简单 > 复杂）
- 飞书表格卖出信号保留一周

#### macos-audio-recording（Mac 录音）— 新增经验教训
- ffmpeg avfoundation 假录问题
- Whisper MPS 稀疏张量不支持
- 粤语转录用 `--language zh` 不要用 `yue`
- 录完必须写 skill（防止下次失忆）
- 必须加载本 skill 再录音

#### dingtalk-live（钉钉直播）— 新增避坑
- Finder 窗口挡住钉钉，必须先用 AppleScript 强制前台
- Python 权限弹窗阻断自动化
- vision_analyze 对截屏识别可能严重错误

#### pdd-store（拼多多店铺）— 新增避坑
- 1688 一键铺货因 shadow DOM 无法可靠触发
- 必须确认进货价再定价
- 图片超过3MB需压缩
