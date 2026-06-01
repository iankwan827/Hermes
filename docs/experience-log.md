# Hermes 使用经验日志

## 2026-06-01

### 踩坑记录

- [analyze-image skill] `vision_analyze` 内置工具在 Xiaomi Token Plan 上有 api-key header 丢失的已知问题（sync→async转换时header未保留），导致图片分析失败 → 必须用 analyze-image skill 的 Python 脚本直接调用 Xiaomi Vision API，绕过 Hermes 管道
  - **反反复复犯错**：即使已多次被告知不能用 `vision_analyze`，模型仍然会再次使用。需要在 memory 中反复强调
  - 来源：CLI session 20260601_153242（用户说"你刚刚咋又自己看图导致出错了"）+ Feishu session 20260601_113834

- [飞书机器人] 群里其他人 @机器人 没收到消息 → 飞书开放平台需要同时配置"事件与回调"（im.message）和"权限管理"（im:message 权限），两者缺一不可
  - 事件订阅只通知"有消息"，权限才允许读取消息内容
  - 还需检查"应用可用范围"是否包含群内所有人
  - 来源：Feishu session 20260601_113834

- [Hermes CLI TUI] "Window too small..." 错误 → 终端窗口太小，Hermes TUI 需要一定大小才能正常显示。拉大窗口或调小字体即可
  - 来源：Feishu session 20260601_113834

- [拼多多一键铺货] 一键铺货工具只能设统一价格倍数，对多产品（每个产品成本/目标价不同）基本没用 → 手动上架 + 手动改价更实际。工具的价值在于订单同步和自动发货
  - 来源：CLI session 20260601_153242

- [Python脚本写入] `write_file` 和 `skill_manage(action='write_file')` 写入含嵌套引号的 Python 代码时会破坏语法（如 f-string 中的引号被截断）→ 必须用 `terminal` 工具的 `cat > file << 'EOF'` heredoc 方式写 Python 脚本
  - 来源：analyze-image skill Pitfalls #6, #8

- [系统Python] 系统自带的 `python` 命令可能因 `importlib._bootstrap_external` 损坏无法导入标准库 → 始终使用 uv python：`E:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`
  - 来源：analyze-image skill Pitfalls #8

- [大图处理] 手动解析 PNG/JPEG 文件头获取尺寸只对 PNG 有效，JPEG 文件头结构不同 → 必须用 `Image.open(img_path).size`（PIL 格式无关）
  - 超大图（20M+像素）必须先缩放再处理，否则 MemoryError
  - 来源：analyze-image skill Pitfalls #2, #3

- [长图切割] 高宽比>3 或高度>8000px 的图片整张发送给 API 会丢失大量内容 → 必须用 `full_extract.py` 自动切割为1500-3000px段，分段提取后合并。实测长图提取量可增长150-200%
  - 超大图（宽度>5000px）用更小的切割段（1500px），否则文字模糊无法识别
  - 来源：analyze-image skill Pitfalls #4, #10

- [PackyAPI] base URL 是 `www.packyapi.com` 不是 `api.packyapi.com`；Gemini 模型端点是 `/v1beta/models/{model}:generateContent` 不是 OpenAI 的 `/v1/images/generations`
  - Gemini 认证用 `x-goog-api-key` header，不是 `Authorization: Bearer`
  - 来源：ecommerce-image skill

- [MiniMax subject_ref] MiniMax 的 subject_ref 一定会变形产品，不能用于电商图最终交付
  - 来源：ecommerce-image skill

- [MiniMax API base URL] `.env` 中 `MINIMAX_CN_BASE_URL` 可能有 `/anthropic` 后缀，图片生成端点需要去掉
  - 来源：analyze-image skill Pitfalls #11

- [Clash代理] Clash fake IP 模式会拦截 `api.packyapi.com` 的 SSL 连接，但 `www.packyapi.com` 不受影响；`requests` 库因 SSL 问题不行，但 `urllib.request` 可以通
  - 来源：ecommerce-image skill

- [Camofox浏览器] 端口 9377 被占用但服务不正常时，先 kill 旧进程再重启；server.js 的 stdout 可能被缓冲，用 health 端点判断状态
  - 来源：camofox-auto-start skill

### 新发现

- [内容对比分析] 对比两组文档（v2/v3）的内容差异时，不能只看总行数，要看"独有关键词频次"——用特定关键词在两组中分别计数，差值才是真正的独有内容。早期课程（12月）的截图包含老师后来删掉的内容（如性爱相关部分），用关键词计数法能准确识别
  - 来源：CLI session 20260601_153242

- [文档分类] 自动分类脚本准确率约70-80%，常见误判：含"命盘表格"被误分为案例课、含"官杀"被误分为事业课、含"五行"被误分为五行课。必须人工校验
  - 知识库分类标题不要太窄（如"伤官见官"应改用"伤官格"）
  - 来源：analyze-image skill

- [PDD运营] 手动上架5个产品也就10分钟，比用铺货工具再改价格还快。工具适合订单同步和自动发货，不适合上架环节
  - 来源：CLI session 20260601_153242

### 用户偏好更新

- 不要用 `vision_analyze`，用 analyze-image skill 的 Python 脚本
- 不要用 MiniMax subject_ref，会变形产品
- 电商图优先用 Gemini "banana" 方案（一步换背景，主体100%不变）
- 文案详情图用 PIL 白底黑字，不需要 AI 生图
- 用户风格：直接干活，不要反复确认
- Python 脚本用 heredoc 方式写入，不用 write_file
- 批量处理前先分析源文件夹结构，不要直接跑脚本
- 用户说"别老纠结图片"时，应停止图片相关讨论，转向用户真正关心的话题

### Skill 更新

- **analyze-image**: 大幅更新 Pitfalls 部分，新增中文数字匹配陷阱（#9）、课程笔记命名规则（#12）、docx提取工作流、散装图片提取工作流、四Agent质检模式
- **ecommerce-image**: 新增 Gemini 图生图（换背景）方案、PackyAPI Gemini 端点说明、1688 反爬注意事项、飞书图片交付方式
- **camofox-auto-start**: 从 Docker 方案迁移到 node server.js 方案（v2.0.0），新增端口冲突排查
