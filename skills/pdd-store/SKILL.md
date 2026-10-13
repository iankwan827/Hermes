---
name: pdd-store
description: 拼多多个人店全自动开店流程。从选品到上架到运营，Hermes可完成95%的工作。
version: 1.7.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ecommerce, pinduoduo, dropshipping, automation]
---

# 拼多多个人店全自动开店 Skill

## 触发条件

用户提到以下关键词时触发：
- 拼多多、PDD、开店、电商、选品、货源、代发

## 核心理念

Hermes 可完成约 60% 的开店工作（选品、图片、文案），用户需手动完成：
1. 注册店铺（身份证实名）
2. 去1688开通一键铺货功能
3. 在1688手动点一键铺货
4. 在PDD编辑页面填写必填属性、上传图片、改价并提交
5. 1688 付款（涉及资金）

## 用户偏好（必须遵守）

- **不要用 vision_analyze 看图** — Xiaomi Token Plan 有 api-key 问题
- **不要纠结图片问题** — 用户说过"不要纠结那个图片"，遇到图片问题快速解决或跳过
- **不要给不切实际的时间估算** — 实际耗时多少就如实说
- **不要一直问确认** — 用户说过"你先跑"，先做再汇报
- **资料要完整再交付** — 用户说"交付标准要求高：不接受部分完成+承诺后续补上"
- **⚠️ 不要没提交就关页面！** 用户原话："你逻辑有问题，你没点提交，重新打开不就没保存了吗"。修改后必须先提交再离开
- **1688链接必须验证** — 不能直接用搜索结果的链接，必须用 OpenCLI 确认商品内容
- **SKU图必须找全** — 每个规格都要有对应图片，不能只找一张通用图
- **定价文档要写清楚每个SKU** — 规格名+拼单价+原价+库存+对应图片
- **文案图用PIL白底黑字** — 用户明确说"把文字变成图片就好了"，不需要AI生图
- **选品要避免撞品** — 不要只搜大品类，要搜细分品类+热搜词找蓝海
- **产品内容不能搞混** — 每个产品的文案/图片必须对应正确，不能交叉使用

## 关键工具：OpenCLI

**1688反爬很强，Camofox也被拦。必须用OpenCLI：**

```bash
# 安装
npm install -g @jackwener/opencli

# 搜索商品
opencli 1688 search "关键词" --limit 5

# 获取商品详情（含图片URL）
opencli 1688 item <offer_id>

# 下载商品图片
opencli 1688 download <offer_id> --output ./images

# 查看店铺信息
opencli 1688 store <shop_id>
```

**前提：Chrome必须登录1688**（OpenCLI复用浏览器登录态）

## 完整工作流

### 用户操作（手动，Hermes不可替代）
1. 注册拼多多个人店（身份证实名）
2. 去1688开通一键铺货功能
3. 在1688手动点一键铺货
4. 在PDD编辑页面填写必填属性（品牌→无品牌、重要材质种类、手柄材质等）
5. 在PDD编辑页面上传换好背景的图片
6. 在PDD编辑页面修改价格并提交
7. 1688付款（涉及资金安全）

### Hermes操作（自动化）
1. 选品+验证+记录进货价
2. 用Gemini换图片背景
3. 压缩超3MB的图片

### 后续运营（手动操作）

#### 客服话术
```
生成20个场景的自动回复模板：
- 售前咨询（材质/尺寸/发货时间）
- 物流问题（查快递/催发货）
- 退换货（质量问题/不想要了）
- 好评引导
```

#### 推广文案
```
1. 活动报名文案（9.9特卖/秒杀/百亿补贴）
2. 广告标题（每个产品3条）
3. 多多进宝佣金设置（20-30%）
```

#### 数据监控
```
浏览器定时打开拼多多后台：
- 读取流量/销量/转化率
- 监控竞品数据
- 异常报警（差评/退款率高）
```

## 经验教训

### 一键铺货
- **1688一键铺货因shadow DOM组件无法可靠触发** — sl-checkbox/sl-button是web component，OpenCLI的click和JS eval都无法可靠操作
- **用户操作流程：注册店铺→开通1688一键铺货→手动点一键铺货→Hermes换图**

### 编辑页面操作
- **编辑页面有必填属性** — 品牌、重要材质种类、手柄材质等不填无法提交，铺货过来的商品这些属性是空的
- **编辑页面URL格式** — `goods_add/index?id={id}&goods_id={goods_id}&type=edit`，从商品列表点"编辑"会开新标签
- **修改后必须立即提交** — 否则重新打开页面全部丢失

### 价格修改
- **必须确认进货价再定价** — 用opencli 1688 item查看每个SKU的具体价格，不能瞎改
- **不同SKU进货价可能不同** — 如电子秤1000g=9.31元，3000g=11元
- **定价要考虑用户认知** — 量程大的应该贵，不能只按成本定价

### 图片处理
- **有文字标签的图片换背景时要保留文字** — prompt必须强调"Keep all text/labels EXACTLY as they are"
- **图片超过3MB需压缩** — PDD要求图片3MB以内，用PIL的quality参数压缩

### OpenCLI稳定性
- **OpenCLI session频繁断开** — 操作PDD后台时session不稳定，复杂操作让用户手动
- **Camofox不能访问PDD后台** — PDD检测到非Chrome浏览器会拦截，必须用OpenCLI

## 自动化率评估

| 流程 | 替代程度 | 方式 |
|------|---------|------|
| 选品+找货源 | 90% | OpenCLI搜1688 |
| 一键铺货 | 0% | shadow DOM限制，必须用户手动 |
| 编辑页面操作 | 0% | OpenCLI session不稳定，必须用户手动 |
| 图片二次创作 | 85% | Gemini换背景/加文字 |
| 客服话术 | 75% | AI生成模板 |
| 推广文案 | 90% | AI写活动文案 |
| 数据监控 | 80% | 浏览器读后台 |

**总体自动化率：~60%**

## 产出文件模板

```
pdd_store/
├── 00_总索引.md          # 资料包总览
├── 01_选品调研.md        # 热销爆款清单+1688链接
├── 04_货源清单.md        # 1688供应商+利润
├── 05_定价策略.md        # 每个SKU价格方案
├── 06_图片二次创作.md    # 换背景/加文字方案
├── 07_客服话术.md        # 自动回复模板
├── 08_推广文案.md        # 活动+广告文案
└── images/               # 主图目录
```

## 注意事项

- 1688价格需实际验证，本清单为参考价
- 主图需要用Gemini生成（参考ecommerce-image skill）
- 前7天是新手期，重点保证48小时发货率
- 先用多多进宝免费推，有销量再开直通车
- **店铺名禁用词**：物美、优质、精品、名牌、官方、旗舰、专卖、专营等
- **个人店分类限制**：不能卖食品、药品、美妆、3C数码（需要资质）

## PDD后台编辑页面操作指南

### 进入编辑页
- 商品列表 → 操作列 → 点击"编辑" → 自动打开新标签页
- 编辑页URL格式：`/goods/goods_add/index?id={商品id}&goods_id={goods_id}&type=edit`
- 左侧有3个选项卡：基本信息、规格与库存、服务与承诺

### 改价流程
1. 点击"规格与库存"选项卡
2. 滚动到底部"价格及库存"区域
3. 每个SKU有两列价格输入框：拼单价、单买价
4. 用React nativeInputValueSetter修改值（直接设value不触发React状态更新）
5. **必须先填写所有必填属性才能提交**（品牌→无品牌、重要材质种类→硅胶、手柄材质→木）
6. 点"提交"按钮保存（不是"保存草稿"）

### ⚠️ 必填属性阻塞提交（实测确认）
1688铺货过来的商品，以下属性为空，不填无法提交：
- **品牌** → 选"无品牌"
- **重要材质种类** → 根据产品选（硅胶厨具选"硅胶"）
- **手柄材质** → 根据产品选（木柄选"木"）
- 还有其他几十个"请选择"的属性字段，部分可跳过
- **如果提交按钮点了没反应，90%是必填属性没填**

### React组件交互技巧
```javascript
// 修改input值（绕过React状态管理）
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '新值');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

### OpenCLI session不稳定
- 频繁断开，需要重新打开页面
- shadow DOM组件（sl-checkbox, sl-button）无法通过OpenCLI可靠点击
- 建议：关键操作（如提交）用eval直接调用DOM方法
- **编辑页面session更容易断开**（页面重、React组件多），关键操作要快速完成
- **如果session断了，之前的修改全部丢失**（未提交的修改不会保存）

## 拼多多个人店商品分类参考

| 产品类型 | 分类路径 |
|---------|---------|
| 厨房工具套装 | 厨房/烹饪用具 > 烹饪用具 > 烹饪工具套装 |
| 手机防水袋 | 手机配件 > 手机防水袋/套 |
| 厨房电子秤 | 厨房/烹饪用具 > 厨房秤/计量工具 |
| 清洁抹布 | 家居日用 > 清洁工具 > 抹布/百洁布 |
| 按摩梳 | 个人护理 > 梳子/按摩器 |
| 收纳用品 | 家居日用 > 收纳整理 > 收纳箱/盒 |
| 创意家居 | 家居日用 > 创意家居 > 摆件/装饰 |

## 工作流程补充

- 选品不要只搜数据，要实际去拼多多后台/APP看热销榜
- 找货源要实际点进1688链接验证价格和代发政策
- 用户说"别老纠结X"时，立即停止该话题转向下一步
- 自动化率评估要实事求是，不要过度承诺
- 直通车不要第一天就开，先做基础（评价+销量）
- 凌晨1-7点关闭投放（转化率低于5%）
- 不要频繁改价（影响权重）

## 1688 货源验证流程（重要）

**⚠️ 必须用 OpenCLI，不要用浏览器自动化**

搜索到的1688链接**不能直接使用**，必须：
1. 用 `opencli 1688 search "关键词"` 搜索产品
2. 用 `opencli 1688 item <id>` 获取商品详情（确认价格、规格、卖家）
3. 用 `opencli 1688 download <id>` 下载商品图片（验证外观）
4. 确认商品跟目标一致后，再写入货源清单
5. 标注实际价格和供应商信息

**原因：** 1688有强反爬机制，Camofox浏览器也会被拦截。OpenCLI 复用 Chrome 登录态可以绕过。

**OpenCLI 安装：**
```bash
npm install -g @jackwener/opencli
```

## 1688 一键铺货技术难点（实测记录）

**1688的"确认店铺"弹窗使用 shadow DOM web component（sl-checkbox / sl-button），有以下问题：**

1. `opencli browser pdd click --text "立即铺货"` 可以点普通按钮，但 **无法点中 shadow DOM 内的 sl-button/sl-checkbox**
2. JS `el.click()` 对 shadow DOM 组件不触发实际逻辑
3. `el.shadowRoot.querySelector('input').click()` 能改变 checked 状态，但 **不触发 sl-change 事件**，铺货逻辑不生效
4. Camofox 被 1688 反爬直接拦截（"unusual traffic"），不可用

**目前结论：** 1688一键铺货通过自动化有技术障碍，用户手动操作更快（几秒）。后续可研究 Playwright 的 `elementHandle.click()` 或 CDP 的 `Input.dispatchMouseEvent` 按坐标点击来绕过。

## 自动化能力边界

以下流程Hermes都可以自动化（用户纠正后补充）：
- ✅ 后台数据分析：浏览器打开拼多多商家后台直接读取
- ✅ 确认发货：浏览器操作后台回填快递单号
- ✅ 客服回复：浏览器监控消息+AI生成回复
- ✅ 退货处理：转发1688供应商地址给买家
- ❌ 1688付款：涉及资金安全，必须人工

## 文字转图片模板（详情页用）

```python
from PIL import Image, ImageDraw, ImageFont

def create_text_image(title, lines, filename, font_path='C:/Windows/Fonts/msyh.ttc'):
    """生成白底黑字的文案图片，用于拼多多详情页"""
    width = 750
    padding = 30
    line_height = 36
    
    title_font = ImageFont.truetype(font_path, 30)
    content_font = ImageFont.truetype(font_path, 20)
    
    # 精确计算高度（防止截断）
    height = padding + 50 + 20 + len(lines) * line_height + 60
    
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    y = padding
    draw.text((padding, y), title, fill='black', font=title_font)
    y += 50
    draw.line([(padding, y), (width - padding, y)], fill='gray', width=2)
    y += 20
    
    for line in lines:
        draw.text((padding, y), line, fill='black', font=content_font)
        y += line_height
    
    img.save(filename, quality=95)
```

**使用场景：**
- 把上架文案.md的文字做成图片
- 用户看图复制文字粘贴到拼多多
- 比手动打字快，比AI生图稳定

## 参考资料

- `references/28秘诀速查表.md` — 八字铁口直断28秘诀，过三关必备
- `references/pdd-backend-opencli.md` — PDD后台OpenCLI操作技术笔记（React输入框、改价弹窗、警告处理、实测SKU数据）

## 工具链

| 工具 | 用途 |
|------|------|
| anysearch | 搜拼多多热销数据、1688供应商 |
| **OpenCLI** | **1688商品搜索/详情/图片下载 + PDD后台操作（绕过反爬，必须用这个）** |
| Gemini | 产品图片二次创作（换背景/加文字） |
| PIL/Pillow | 文字转图片（白底黑字详情页） |

### 拼多多自动上架工具限制

拼多多服务市场的"店管家_分销代发"等工具：
- ✅ 支持：订单自动同步、自动发货、物流回传
- ❌ 限制：**只能统一设倍数（如1.5倍），不能单独设每个产品价格**
- 解决方案：先用工具批量上架，再去拼多多后台逐个改价

### OpenCLI操作PDD后台实测发现

**编辑页面操作：**
- URL格式：`goods_add/index?id=<listing_id>&goods_id=<goods_id>&type=edit`
- 点"编辑"会开新标签，需要切到新tab操作
- 必填属性不填=提交无反应（品牌→无品牌、重要材质种类→硅胶、手柄材质→木）
- React组件用 `nativeInputValueSetter` 才能更新值
- **修改后必须立即提交，否则重新打开页面全部丢失**

**1688一键铺货：**
- 1688的"确认店铺"弹窗用 sl-checkbox/sl-button（shadow DOM组件）
- OpenCLI的 `click --text` 无法点中shadow DOM组件
- JS `el.click()` 在shadow DOM上不触发真正的事件
- 结论：一键铺货暂不支持自动化，需用户手动操作

**Gemini图片换背景：**
- .env文件位置：`~/AppData/Local/hermes/.env`
- Python脚本需手动加载.env才能拿到API key
- 用 `urllib.request` 调PackyAPI Gemini端点，不要用 `requests`（SSL问题）
- 20张图批量处理约需2-3分钟

#### 1688相关
- **搜索结果的链接不能直接用** — 必须用OpenCLI的`1688 item`验证商品内容，否则链接和产品不对应
- **OpenCLI是1688的神器** — 复用Chrome登录态，能绕过反爬，获取商品详情、价格、图片
- **每个SKU要对应不同图片** — 3件套/8件套/12件套的预览图不能用同一张
- **备2-3家供应商** — 防止一家断货没法发货
- **先买样品验证质量** — 不要直接大批量下单
- **1688一键铺货的shadow DOM问题** — 1688铺货弹窗用sl-checkbox/slabutton等shadow DOM组件，OpenCLI的ref点击和JS eval `.click()`都无法可靠操作。实测`opencli browser pdd eval`遍历shadow root找到元素并click可以触发，但checkbox状态可能不生效。**目前最可靠的方式是用户手动在Chrome里点一键铺货**（几秒钟的事）
- **1688商品详情可获取每个SKU价格** — `opencli 1688 item <id>` 返回的 price_tiers 只显示区间，需要用 `opencli browser pdd open` 打开1688详情页，然后用eval提取每个SKU的精确价格（格式：`规格名¥价格库存数量`）

### 上架相关
- **品牌选"无品牌"** — 个人店家居日用品不需要品牌授权
- **24小时发货有风险** — 1688供应商不一定能24小时发，先选48小时
- **SKU默认选中利润款** — 不要默认选引流款，容易亏本
- **原价设拼单价的1.5-2倍** — 显示有折扣，吸引买家拼团
- **库存必须≥1688 MOQ** — 供应商起订量是1件就设1件，是5件就设5件，不能低于起订量

### 图片相关
- **不要用MiniMax subject_ref** — 一定会变形产品，不能用于电商图最终交付
- **Gemini换背景更稳定** — 传原图+prompt，一步换背景，主体100%不变
- **文字转图片用PIL更稳定** — 不依赖API，白底黑字清晰好读
- **Gemini生图需要PackyAPI key** — 必须配置OPENAI_API_KEY环境变量才能调用Gemini换背景。没有key就只能用PIL做简单处理或让用户手动换图
- **用户要的是"保持商品不变，图的风格不变"** — 换背景时不要改变产品外观、色调、整体风格，只替换背景元素

### 定价相关
- **铺货价格=拿货价，必须加价！** 1688价+运费+平台费+利润=PDD售价
- **定价要考虑用户认知** — 用户觉得"量程越大应该越贵"，500g高精度虽然成本高但量程小，定价不能比1000g贵。要站在买家角度想价格逻辑
- **引流价吸引点击，利润价赚钱** — 不要把所有价格都设很低
- **套餐价提高客单价** — 2只装/3只装比单只更划算
- **利润率目标50%+** — 1688拿货价通常很低，定价不要太保守
- **定价文档要写清楚每个SKU** — 1688拿货价+运费+平台费+利润=PDD售价
- **不同产品需要不同倍数** — 硅胶厨具1.1倍、清洁抹布5倍、按摩梳13倍，统一倍数会导致部分产品亏本

### PDD后台操作相关
- **⚠️ 修改后必须先提交再离开！** 用户原话："你逻辑有问题，你没点提交，重新打开不就没保存了吗"。每次重新打开页面都是原始价格，之前的所有修改全部丢失。操作顺序：修改 → 提交 → 确认成功 → 才能关闭/离开
- **⚠️ 编辑页比改价弹窗更可靠** — 改价弹窗的"加/减"radio按钮点击状态不持久，容易方向反了。编辑页（规格与库存tab）可以直接改每个SKU的价格，更直观可靠
- **⚠️ 编辑页操作顺序** — 1.点"编辑"开新标签 → 2.切到新tab → 3.先填必填属性（品牌/材质）→ 4.再改价格 → 5.最后点提交。不要先改价格再填属性，否则提交不了
- **⚠️ .env文件需手动加载** — Python脚本调Gemini API时，环境变量(OPENAI_API_KEY)不在shell里。必须先读取`~/AppData/Local/hermes/.env`加载到`os.environ`。这在子任务中尤其重要
- **OpenCLI ref极其容易stale** — PDD后台页面动态加载频繁，`state`输出的ref在下一次`click`时可能已经变了。**必须每次click前重新跑`state`或`find`获取最新ref**，不能缓存ref跨操作使用
- **React组件输入框不响应直接设值** — PDD后台用React controlled input，直接`input.value = x`不触发状态更新。必须用 `nativeInputValueSetter` 绕过：`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input, '8'); input.dispatchEvent(new Event('input',{bubbles:true}))` 才能让React感知到变化
- **"加/减"radio按钮点击状态不持久** — 点击"加"后可能实际仍处于"减"状态，导致批量修改方向反了（30.24→22.24而不是38.24）。**每次批量修改前必须确认当前选中的是"加"**，可以通过检查输入框前缀或截图确认。**推荐直接用编辑页面逐个改价**，比改价弹窗更可靠
- **改价弹窗流程** — 点"修改价格"→弹出modal→用"批量修改"下拉选"按金额加减"→输入金额→点"批量修改"按钮→点"提交改价"。注意：按钮文本是"提交改价"不是"提交修改"
- **改价弹窗可能有草稿箱/营销警告** — 草稿箱警告（黄色）需先关闭再操作；营销中警告（红色）表示修改价格会自动撤销优惠券，需用户确认
- **Camofox不能访问PDD后台** — PDD检测到非Chrome浏览器会拦截，必须用OpenCLI（复用Chrome登录态）

### 其他
- **OpenCLI可能限流** — 1688搜索/详情接口偶尔会返回空结果，重试或换关键词即可
- **店铺名禁用词** — 物美、优质、精品、名牌、官方、旗舰等不能用，"优选"可以用
- **不要频繁改价** — 影响权重
- **直通车不要第一天就开** — 先做基础（评价+销量）
- **凌晨1-7点关闭投放** — 转化率低于5%
- **⚠️ PDD商品分类可能有误** — 1688铺货过来的商品分类不一定准确（如手机防水袋被分到3C数码配件而不是运动户外）。PDD后台商品体检会提示分类有误，需要手动修改
- **⚠️ Gemini API可能返回503** — PackyAPI的Gemini端点在高负载时返回503（system memory overloaded）。解决：等几分钟重试，或切换到gemini-2.5-flash-image（轻量模型）

## 相关技能

- ecommerce-image: 产品图片二次创作
- anysearch: 数据搜索
- camofox-auto-start: 浏览器自动化
- analyze-image: 验证下载的1688图片是否正确

## 自动化工具（推荐）

**店管家_分销代发**（拼多多服务市场）：
- 1688商品自动铺货到拼多多（不用手动上架）
- 有订单自动在1688下单
- 供应商发货后自动回填单号
- 自动生成白底图、标题违禁词过滤
- 7天免费试用：https://fuwu.pinduoduo.com/service-market/service-detail?detailId=11983
- 月销9万+，评分4.2

**1688端工具：**
- 代发助手王（金牌工具）— 比自动分销（银牌）功能更全
- 入口：1688商品详情 → 代发 → 一键铺货 → 选代发助手王
