作者扒视频：用户只要低粉爆款库90条URL对应的爆款视频，不是每个作者主页前10个视频（之前错误展开到758个，用户质疑"咋有那么多"）。正确流程：用low_fan_urls.txt的90条URL直接下载。进度文件：`D:/hermes-agent/文案/作者扒视频进度.md`。
§
Web系统：八字排盘三栏布局，Gateway API:8642，Node.js中转。性能：Session-ID持久化+启动预热+串行执行。过滤"不中"正则/不中/。Skill:ziduan/sales-steps/muku/kongwang/orchestrator/web-gateway。2030=庚戌（火库），大运甲辰（水库），辰戌冲双库齐开。过三关遇到女命(gender=F)必须额外加载bazi-fukeshengyu skill扫流产/剖腹产/子宫卵巢断语。八字巳月=5月5日立夏~6月5日芒种（不是6月）。
§
写完文案必须自动跑video-content-audit审核，不等用户提醒（用户原话"你没跑skill啊"）。引用热搜事件必须确认时间线（几月、第几轮、谁赢谁输），不能凭印象写。审核是内建流程不是可选步骤。
§
小米API：tool消息不支持多模态，config加`agent.image_input_mode: text`。文案存`D:/hermes-agent/文案/`，命名`YYYY-MM-DD_主题.md`。八字十神性格：比劫=犟，偏财=倔。取象：庚金伤官=生殖系统（刀剑→快），取象直接对应不绕生克。
§
栋笃笑文案：用阿强做叙事载体（铺垫→反转→吐槽）。用直接吐槽/叙述体，不用对话体。每句话推进内容不重复。用户说"看"是只读不动手，"接着说"就保留已确认内容往下写新的，不重复不加对话。开头第一句是选题。
§
用户喜欢"争议性开头"（"99%的人都理解错了"）。中间太平时加钩子：1)共鸣"你系唔系都试过？" 2)反面案例（笑点）3)冲突对比型（"迟到一次记一世，帮十次忘光"比权威佐证更有力）。开头要埋伏笔（"99%的人都是会这样"），不说结论。
§
八字排盘：23:00-23:59算第二天子时（日期+1，hour=0）。generate_bazi_analysis.js已自动处理。
§
用户有爆款开头库（61条AI类），存于D:/hermes-agent/文案/爆款开头库.md。写文案阶段2必须从这个库里筛选匹配的开头，不能自己编。原版skill在E:\Users\Administrator\.claude\skills\目录下，不要乱改hermes版。用户打比方是教角度不是素材——只取抽象概念不用具体内容。
§
⚠️写skill前必须先加载skill-creator（E:/Users/Administrator/AppData/Local/hermes/skills/skill-creator/SKILL.md），按Claude标准写。⚠️改完skill/重要文件必须推GitHub同步Mac：cd /e/Users/Administrator/hermes-repo && git add . && git commit -m "xxx" && git push origin main（冲突时用--force）。Mac拉取：git pull。memory同步文件：docs/memory-sync.md。
§
OpenCLI：先`opencli daemon status`，断开就restart。给用户命令时直接给，不加bash/zsh前缀，不解释为什么用这个shell。用户多次纠正过度解释和多余前缀。
§
dbs-video-workflow：必须完整跑4阶段不能跳步。阶段2开头用模板库套用。部分段落用直接吐槽/旁白（不要全对话体）。比喻简洁不重复。用户多次修正角度，直接改不argue。
§
Mac SSH连不上（port 22 refused），不要SSH到Mac。看GitHub仓库：https://github.com/iankwan827/Hermes。⚠️审核文案必须按字数估时长（粤语4字/秒），超90秒不能标通过。
§
栋笃笑喜剧节奏：反转/punchline要一句话打完，不要拆成多段铺垫再给结论。用户原话"我这句就是一句话，你别拆开说"。越短越自然越好笑。用户给的结构框架就是终稿结构，不要自作主张加段落。
§
八字取象：庚金做伤官=生殖系统（不需要绕金生水）。逻辑：庚金=刀剑→锐利→快。取象从五行本质出发，不要混取象逻辑和生克逻辑。例：己土日主，庚金是伤官（己土生庚金，异性=伤官）。用户教的，不是我自己推的。
§
Mac上操作：不要加bash前缀，直接给命令就行。用户用zsh，命令直接跑没问题。用户原话"为啥要打开Terminal""你为啥老喜欢加bash呢"。
§
用户纠正：杀Python进程时不要杀自己（Hermes agent也是Python进程），必须先看进程列表确认是哪个再杀，绝对不能用`killall python`或类似方式误杀自己。正确做法：先`ps aux | grep`找目标PID，再用PID精准kill。