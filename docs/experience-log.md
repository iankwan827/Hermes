# Hermes 使用经验日志

## 2026-06-02

### 踩坑记录

- [pdd-store skill] 一键铺货流程自动化失败 — 1688的"确认店铺"弹窗使用 shadow DOM web component（sl-checkbox/sl-button），OpenCLI 的 click 和 JS eval 都无法可靠触发 → 必须用户手动在 Chrome 里点一键铺货（几秒钟的事）
  - 来源：CLI session 20260602_091341

- [pdd-store skill] 编辑页面必填属性阻塞提交 — 1688铺货过来的商品属性为空（品牌、重要材质种类、手柄材质等），不填无法提交 → 必须先填写所有必填属性再改价/上传图片
  - 来源：CLI session 20260602_091341

- [pdd-store skill] React组件输入框不响应直接设值 — PDD后台用 React controlled input，直接 `input.value = x` 不触发状态更新 → 必须用 `nativeInputValueSetter` 绕过 React 拦截：`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input, '新值')` + `dispatchEvent(new Event('input',{bubbles:true}))`
  - 来源：CLI session 20260602_091341

- [pdd-store skill] OpenCLI session频繁断开 + ref容易stale — PDD后台页面动态加载频繁，ref在下一次click时可能已经变了 → 每次click前必须重新跑state获取最新ref，关键操作要快速完成
  - 来源：CLI session 20260602_091341

- [pdd-store skill] 修改后必须立即提交 — 重新打开页面全部丢失，用户原话："你逻辑有问题，你没点提交，重新打开不就没保存了吗" → 操作顺序：修改 → 提交 → 确认成功 → 才能关闭/离开
  - 来源：CLI session 20260602_091341

- [pdd-store skill] 不同SKU进货价可能不同 — 电子秤1000g=9.31元，3000g=11元 → 必须用 `opencli 1688 item` 查看每个SKU具体价格再定价，不能瞎改
  - 来源：CLI session 20260602_091341

- [video_analyze] 小米MIMO视频理解API缺少必要参数 — Hermes的video_analyze工具没有传入 `fps` 和 `media_resolution` 参数，导致视频分析失败 → 需要修改Hermes代码添加这两个参数，或等官方更新
  - 来源：CLI session 20260602_091341

- [ecommerce-image] Gemini换背景会丢失原图文字叠加 — 1688商品图常有"电池款"、规格参数等文字，Gemini默认会修改/删除文字 → prompt必须加"Keep all text/labels EXACTLY as they are"，换完后用flash模型验证
  - 来源：ecommerce-image skill 经验教训

### 新发现

- [pdd-store] PDD后台编辑页面URL格式 — `goods_add/index?id={id}&goods_id={goods_id}&type=edit`，从商品列表点"编辑"会开新标签
  - 来源：CLI session 20260602_091341

- [pdd-store] PDD商品分类可能有误 — 1688铺货过来的商品分类不一定准确（如手机防水袋被分到3C数码配件），PDD后台商品体检会提示分类有误，需要手动修改
  - 来源：CLI session 20260602_091341

- [pdd-store] "修改价格"弹窗 vs 编辑页面 — 修改价格弹窗只能改价格，编辑页面可以改价格+图片+属性，推荐用编辑页面
  - 来源：CLI session 20260602_091341

- [pdd-store] 草稿箱冲突 — 如果商品在草稿箱有编辑版本，修改价格会提示冲突，需要先处理草稿
  - 来源：CLI session 20260602_091341

- [ecommerce-image] Gemini批量换背景实测 — 20张图约2-3分钟，用gemini-3-pro-image-preview模型，prompt需明确要求保留产品不变
  - 来源：ecommerce-image skill 经验教训

- [ecommerce-image] Python urllib.request调PackyAPI比requests更稳定 — SSL兼容性更好，不要用requests库
  - 来源：ecommerce-image skill 经验教训

### 用户偏好更新

- **流程自动化边界要明确区分** — 用户要求明确哪些是Hermes自动化、哪些是用户手动，不要把失败的自动化流程写成"可以做"。pdd-store skill已更新为：Hermes做选品+换图+文案，用户手动操作铺货+编辑+付款
- **不要凭空设不存在的价格区间** — 铺货过来的SKU有固定价格范围，只能在基础上加价
- **定价要考虑用户认知** — 用户觉得"量程越大应该越贵"，不能只按成本定价
- **自动化率评估要实事求是** — pdd-store skill从80%修正为60%，反映了实际能力边界

### Skill 更新

- **pdd-store**：大幅重写，将自动化流程和用户手动流程明确分开，新增"自动化率评估"表，补充编辑页面操作React技巧、必填属性、草稿箱冲突等实战经验
  - 原因：用户指出"昨天那个拼多多的步骤有点错了"，流程描述不准确
- **ecommerce-image**：新增"文字叠加图换背景保留文字"技巧、批量处理文件大小检查、.env手动加载等经验
  - 原因：实际操作中发现Gemini默认会修改文字、图片超3MB等新问题
- **analyze-image**：新增"批量处理前必须先分析源文件夹结构"、"超大图1500px切割"、"rename_map.json混合key类型"等经验
  - 原因：478张图批量处理中遇到的实际问题

---

## 2026-06-01

### 踩坑记录

- [analyze-image skill] `vision_analyze` 内置工具在 Xiaomi Token Plan 上有 api-key header 丢失的已知问题（sync→async转换时header未保留），导致图片分析失败 → 必须用 analyze-image skill 的 Python 脚本直接调用 Xiaomi Vision API，绕过 Hermes 管道
  - **反反复复犯错**：即使已多次被告知不能用 `vision_analyze`，模型仍然会再次使用。需要在 memory 中反复强调
  - 来源：CLI session 20260601_153242（用户说"你刚刚咋又自己看图导致出错了"）+ Feishu session 20260601_113834

- [ecommerce-image] MiniMax subject_ref 一定会变形产品 — 不能用于电商图最终交付 → 用 Gemini "banana" 原生图像编辑（传入参考图+prompt，保留主体只换背景）
  - 来源：ecommerce-image skill 经验教训

- [ecommerce-image] rembg 输出底部有大量透明区域 — 产品抠图后底部有空白，不裁剪会导致"悬浮" → 必须用numpy检测alpha通道并裁剪
  - 来源：ecommerce-image skill 经验教训

- [ecommerce-image] PackyAPI base URL 有坑 — 正确是 `www.packyapi.com`，不是 `api.packyapi.com` → Gemini 端点是 `/v1beta/models/{model}:generateContent`，不是 OpenAI 的 `/v1/images/generations`
  - 来源：ecommerce-image skill 经验教训

- [camofox] 端口 9377 被占用时服务启动失败 → 先 `netstat -ano | grep 9377` 找到 PID，用 `taskkill /PID <pid> /F` 杀掉旧进程再重启
  - 来源：camofox-auto-start skill pitfalls

- [camofox] Camofox浏览器启动问题 — AI插帧（如NVIDIA Overlay的AI帧生成）可能导致node server.js启动失败或浏览器崩溃 → 关掉游戏/系统中的AI插帧功能即可
  - 来源：CLI session 20260531_120940（用户发现崩坏：星穹铁道启动崩溃的解决方案）

### 新发现

- [opencli] OpenCLI 可以绕过1688反爬 — 用 `opencli 1688 item <id>` 获取商品详情和图片URL，复用Chrome登录态，比浏览器自动化可靠
  - 来源：ecommerce-image skill 经验教训

- [ecommerce-image] Gemini图片识别 — 同一个端点，responseModalities 设为 `["TEXT"]` 只返回文字分析，可用于验证换背景后文字是否保留
  - 来源：ecommerce-image skill 经验教训

- [ecommerce-image] Clash fake IP 模式会拦截 HTTPS 连接 — 导致 SSL 错误；`requests` 库的 `verify=False` 可以绕过，`urllib.request` 更稳定
  - 来源：ecommerce-image skill 经验教训

- [content] 内容对比分析方法（关键词计数法） — 用于比较两个文档的相似度和差异
  - 来源：session_search 结果

### 用户偏好更新

- **不要纠结图片问题** — 用户说过"不要纠结那个图片"，遇到图片问题快速解决或跳过
- **先做再汇报** — 用户说过"你先跑"，不要一直问确认
- **交付标准要求高** — 不接受部分完成+承诺后续补上
- **优先搜B站视频** — 遇到技术问题（如游戏崩溃）优先搜B站视频教程，不要上来就放大招（如重装驱动）
- **资料要完整再交付** — 用户期望完整的交付，不是"大部分完成+几个失败"

### Skill 更新

- **camofox-auto-start**：启动方式从Docker改为 `node server.js`，新增端口占用处理、Windows curl兼容性
  - 原因：Docker不可用，改用本地Node.js启动
- **ecommerce-image**：新增"文字叠加图换背景"、PackyAPI接入、多角度生成、平台风格对照等完整内容
  - 原因：电商图片处理流程从零搭建

---

## 2026-05-31

### 踩坑记录

- [游戏] 崩坏：星穹铁道启动崩溃（NvPresent64.dll / NVP_Init_Vulkan Access Violation）— 崩溃日志中 NVIDIA Overlay 的 NvPresent64.dll 只是表象 → 实际解决方案是关闭游戏内的「AI 插帧」功能，不需要重装显卡驱动
  - 来源：CLI session 20260531_120940（用户自己搜索发现）
  - **教训**：遇到游戏/软件崩溃应该先搜社区（B站优先）有没有已知解法，不要直接套通用方案

### 新发现

- [skill] 没有专门精炼skill的工具 — knowledge-extraction 是从文档提取知识点，不是精炼skill。要优化skill只能手动用 `skill_manage(action='edit')` 重写
  - 来源：CLI session 20260531_120940

- [skill] 从线上课笔记提炼skill的流程 — 读课程笔记 → 提取可执行步骤和判断逻辑 → 去掉废话和重复 → 按skill规范输出（触发条件+步骤+pitfalls+验证）
  - 来源：CLI session 20260531_120940

### 用户偏好更新

- **用户更信任社区搜索而非AI建议** — 崩坏崩溃问题用户自己搜索B站就解决了，AI建议的"重装驱动"方案反而复杂
- **skill精炼需求** — 用户希望从线上课笔记直接提炼成可执行skill，比knowledge-extraction更注重可操作性

---

## 2026-05-30

### 踩坑记录

- [analyze-image] `write_file` 工具会破坏Python f-string语法 — 写入含嵌套引号的Python代码时可能产生语法错误 → 写Python脚本时用 `terminal` 工具的 heredoc 方式，不要用 `write_file`
  - 来源：analyze-image skill pitfalls

- [analyze-image] 系统Python可能不可用 — `python` 命令因 `importlib._bootstrap_external` 损坏无法导入标准库 → 始终使用 uv python
  - 来源：analyze-image skill pitfalls

- [analyze-image] `skill_manage(action='write_file')` 也会破坏Python脚本中的引号 — 实际案例：batch_ocr.py、retry_zero.py、retry_one.py 三个脚本的字符串字面量被截断 → 修改脚本后必须用 `python -m py_compile` 验证语法
  - 来源：analyze-image skill pitfalls

### 新发现

- [bazi] 八字知识库提取检查清单 — 44个原始文档的章节提取状态检查，发现部分提取和遗漏内容，建议了目标文件映射
  - 来源：CLI session 20260530_190553

- [bazi] 知识库分类标题不要太窄 — 用"伤官见官"作标题会漏掉"伤官配印"、"金水伤官"等其他组合，应该用更宽的标题（如"伤官格"）
  - 来源：analyze-image skill pitfalls

### 用户偏好更新

- **知识库组织方式** — 用户偏好十神组合分类方式（伤官格、官印格等），而不是按具体组合命名（伤官见官、官印相生等）

---

## 通用经验教训（持续积累）

### 工具使用铁律

1. **绝对不要用 `vision_analyze`** — Xiaomi Token Plan 上有 api-key header 丢失的已知问题，用 analyze-image skill 的 Python 脚本
2. **Python脚本用uv python** — 系统python不可用，路径：`E:\Users\Administrator\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe`
3. **写Python脚本不要用 `write_file`** — 会破坏f-string语法，用terminal heredoc
4. **修改脚本后必须用 `python -m py_compile` 验证** — write_file和skill_manage都可能破坏字符串
5. **.env文件需手动加载** — Python脚本直接运行拿不到环境变量，必须先读取 `~/AppData/Local/hermes/.env`
6. **OpenCLI ref容易stale** — 每次操作前必须重新获取最新ref

### 流程管理

1. **自动化能力边界要诚实** — 不要过度承诺自动化率，实际做不到的就标0%
2. **用户说"先跑"就先跑** — 不要反复确认
3. **交付必须完整** — 不接受"大部分完成+几个失败"
4. **遇到问题先搜社区** — B站视频优先，不要直接套通用方案
5. **不要纠结图片** — 用户说过的话要记住

### 文件处理

1. **长图必须切割** — 高宽比>3或高度>8000px的图片，整张发送会严重截断内容
2. **超大图先缩小** — 20M+像素用PIL缩放后再处理，否则MemoryError
3. **图片尺寸必须用PIL读取** — 不能手动解析文件头（只对PNG有效，JPEG会出错）
4. **批量处理前先分析源文件夹结构** — 不要直接跑脚本
5. **0字节文件必须主动重试** — 不要只记日志就完事
