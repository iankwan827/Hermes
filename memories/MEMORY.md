抖音：查全量视频用「内容管理→作品管理」，别用「近期作品」（只显示7天）。小号评论触发二次推流（1条≈1500播放）。视频1.5分钟内。口播提示（）嵌正文，标题15-20字标签≤5个。⚠️查视频数据必须先读发展日志再查创作者中心，用户有12+视频不要以为只有5个。
Chrome CDP：config用`ws://127.0.0.1:9222`。不要指定`--user-data-dir`（用户在E盘），否则丢失登录态。快捷方式已加CDP参数。
§
Web系统：八字排盘三栏布局，Gateway API:8642，Node.js中转。性能：Session-ID持久化+启动预热+串行执行。过滤"不中"正则/不中/。Skill:ziduan/sales-steps/muku/kongwang/orchestrator/web-gateway。2030=庚戌（火库），大运甲辰（水库），辰戌冲双库齐开。过三关遇到女命(gender=F)必须额外加载bazi-fukeshengyu skill扫流产/剖腹产/子宫卵巢断语。八字巳月=5月5日立夏~6月5日芒种（不是6月）。
§
写完文案必须自动跑video-content-audit审核，不等用户提醒（用户原话"你没跑skill啊"）。引用热搜事件必须确认时间线（几月、第几轮、谁赢谁输），不能凭印象写。审核是内建流程不是可选步骤。
§
电商图：Gemini原生编辑>rembg合成。PackyAPI端点www.packyapi.com。
§
粤语金句不要直接写，用剧情/对话体现。文案时间线必须符合现实逻辑。质检需检查每个叙事转折点前是否有钩子。粤语用词：叛逆→反骨（"反骨"才是粤语词）。标签中热搜话题必须原样保留（吃搜索流量），不能替换成内容关键词。
§
栋笃笑文案：用户用"阿强"（朋友角色）做叙事载体——铺垫→反转→吐槽→引出主题。经典黄子华对话体。开头第一句必须是选题（"开头第一句肯定是我们选的那句选题啊"），阿强故事紧跟着展开。可系列化（金价暴跌→A股大跌，阿强连续亏钱）。
§
用户喜欢"争议性开头"（"99%的人都理解错了"）。中间太平时加钩子：1)共鸣"你系唔系都试过？" 2)反面案例（笑点）3)冲突对比型（"迟到一次记一世，帮十次忘光"比权威佐证更有力）。开头要埋伏笔（"99%的人都是会这样"），不说结论。
§
小红书：用/search_result/链接（带xsec_token），不用/explore/（触发扫码）。仿人操作：间隔3-8秒，每分钟≤5次eval，每5篇暂停10-15秒。Chrome已登录。
§
八字：23点后算次日子时。generate_bazi_analysis.js已自动处理。
§
用户痛点：文案简洁；视频50秒-1分30秒。⚠️用户改完文案就是终版。
§
⚠️写skill前先加载skill-creator。改完文件推GitHub：先设代理`git config http.proxy http://127.0.0.1:7897`，再add/commit/push，用完unset。仓库：E:/Users/Administrator/AppData/Local/hermes。
§
⚠️用户发的素材/库必须当次session保存成文件（D:/hermes-agent/文案/），不能只在对话里用。发了3-4次爆款开头库都丢了，用户frustrated。"从库里选"→先搜文件是否存在。
§
⚠️搜网页/热点用OpenCLI复用Chrome登录态。提到"热搜"默认抖音（API: douyin.com/aweme/v1/web/hot/search/list/，免登录）。OpenCLI default session已登录抖音可搜话题详情。用户做共鸣类内容，不追体育/娱乐热搜。站点适配器148个。
§
dbs-video-workflow：必须完整跑4阶段不能跳步。阶段2用模板库。⚠️多期文案写完必须逐期交叉检查逻辑矛盾，不能只看相邻两期（用户原话"你没发现前面几期和后面几期有矛盾吗"）。用户多次修正角度，直接改不argue。
§
Vercel CLI：`VERCEL_TOKEN=*** vercel --prod --yes`部署。⚠️域名不自动更新需`vercel promote`。bazi源码:E:\SD\bazi\bazi_new_web。
§
文案写作：用户给的比喻/故事是用来教我理解角度的，不是写进文案的。要区分"解释给我听"和"写进脚本"。用户说"我用XX故事讲解给你听，不是让你写出来"时，只取角度不取内容。
§
Vercel：CLI用VERCEL_TOKEN env var。⚠️部署后域名不自动更新需`vercel promote`。bazi项目:E:\SD\bazi\bazi_new_web，域名www.shiyibazi.top。
§
用户问"这是什么错误"时直接给答案，不要先搜项目文件再总结。简洁诊断 > 完整调查（除非用户明确要求调查）。