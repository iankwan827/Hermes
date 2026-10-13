# PDD后台OpenCLI操作技术笔记

> 实测日期：2026-06-02
> 商品：轻版750g硅胶厨具套装木柄十四件套（ID: 961686680929）

## 商品编辑页（完整编辑，推荐用这个）

**⚠️ "编辑" vs "修改价格"：** 用户明确要求用"编辑"进完整编辑页面，不是"修改价格"弹窗。"修改价格"只是快速改价，"编辑"能看到所有SKU、图片、标题等完整信息。

### 打开方式
商品列表页 → 点"操作"列的"编辑"链接 → **会在新标签打开编辑页**

### URL格式
```
https://mms.pinduoduo.com/goods/goods_add/index?id={商品内部ID}&goods_id={商品ID}&type=edit
```
示例：`goods_add/index?id=193080285009&goods_id=961686680929&type=edit`

### 编辑页结构（3个tab）
1. **基本信息** — 商品轮播图（5/10张）、商品标题（60字限制）、品牌/材质等属性
2. **规格与库存** — SKU规格列表 + 价格及库存表格（**价格改这里**）
3. **服务与承诺** — 发货时间、退换货政策等

### 规格与库存tab
- 上半部分：商品规格（如"尺寸"），列出所有SKU规格选项（白色14件套、粉色14件套等）
- 下半部分：**价格及库存表格**，每个SKU一行，包含拼单价和单买价输入框
- 输入框同样是React controlled input，需要用nativeInputValueSetter设值

### 操作流程
```bash
# 1. 打开商品列表
opencli browser pdd open "https://mms.pinduoduo.com/goods/goods_list"

# 2. 找到"编辑"链接并点击（会在新标签打开）
opencli browser pdd find --role link --name "编辑"
opencli browser pdd click <ref>

# 3. 切换到新标签
opencli browser pdd tab list  # 找到新标签的page ID

# 4. 滚动到价格区域
opencli browser pdd eval "(function() { const divs = document.querySelectorAll('div'); for(const d of divs) { if(d.textContent.includes('价格及库存') && d.offsetHeight > 0) { d.scrollIntoView(); return 'scrolled'; } } return 'not found'; })()"

# 5. 修改SKU价格（React input）
opencli browser pdd eval "(function() { const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; const inputs = document.querySelectorAll('input[placeholder=请输入]'); for(const i of inputs) { const val = parseFloat(i.value); if(!isNaN(val) && val > 0 && val < 100) { nativeInputValueSetter.call(i, (val + 8).toFixed(2)); i.dispatchEvent(new Event('input', { bubbles: true })); } } return 'done'; })()"
```

## 商品列表页

URL: `https://mms.pinduoduo.com/goods/goods_list`

### 打开方式
```bash
opencli browser pdd open "https://mms.pinduoduo.com/goods/goods_list"
```

### 找到"修改价格"链接
```bash
# 方法1：用find找
opencli browser pdd find --role link --name "修改价格"

# 方法2：用state grep
opencli browser pdd state 2>&1 | grep "修改价格"

# 方法3：用text click（多个匹配时用ref）
opencli browser pdd click --text "修改价格"
# 返回semantic_ambiguous时，取最后一个ref（actual link）
opencli browser pdd click <ref>
```

### 找到"编辑"链接
同上，`--text "编辑"` 也会返回多个匹配，取最后一个ref。

## 改价弹窗

### 打开方式
点击"修改价格"后弹出modal，标题"修改价格"。

### 弹窗内元素
- 警告横幅（可能有草稿箱/营销冲突警告）
- 批量修改区域：下拉选"全部尺寸" + "按金额加减"/"按百分比" + 输入框 + "批量修改"按钮
- SKU表格：规格信息 | 当前拼单价 | 改后拼单价 | 改后单买价
- 底部："提交改价"按钮 + "取消"按钮

### React输入框操作
PDD后台用React controlled input，不能直接设值。

**正确方式：nativeInputValueSetter**
```javascript
const input = document.querySelector('input[data-testid=beast-core-inputNumber-htmlInput]');
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
  window.HTMLInputElement.prototype, 'value'
).set;
nativeInputValueSetter.call(input, '8');
input.dispatchEvent(new Event('input', { bubbles: true }));
```

**也可以用OpenCLI type命令：**
```bash
opencli browser pdd click <ref>  # 先聚焦
opencli browser pdd type <ref> "8"
```

### "加/减"radio按钮
位置：输入框左侧，两个span "加" 和 "减"

**问题：** 点击"加"后状态可能不持久，导致批量修改方向反了。
**解决：** 每次批量修改前检查当前选中状态。可以通过截图或检查DOM确认。

### 批量修改按钮
```bash
opencli browser pdd find --role button --name "批量修改"
opencli browser pdd click <ref>
```

### 提交改价按钮
文本是"提交改价"不是"提交修改"！
```bash
opencli browser pdd find --role button --name "提交改价"
opencli browser pdd click <ref>
```

## 警告处理

### 草稿箱警告（黄色）
内容：「该商品在「草稿箱」中有正在编辑的版本，如果确认修改当前价格，将自动删除草稿」
处理：关闭弹窗（点X），先去处理草稿

### 营销中警告（红色）
内容：「该商品在「营销中」中正在编辑的版本，如果确认修改价格，将自动撤销优惠券」
处理：用户需确认是否继续

## 实测SKU数据（硅胶厨具套装）

| 规格ID | 规格信息 | 当前拼单价 |
|--------|----------|-----------|
| 1910692987659 | 白色14件套 匀托+煎蛋器 | 30.24 |
| 1910692987660 | 粉色14件套 匀托+煎蛋器 | 30.24 |
| 1910692987661 | 卡其色14件套 匀托+煎蛋器 | 30.24 |
| 1910692987662 | 黄色14件套 匀托+煎蛋器 | 30.24 |
| 1910692987663 | 绿色14件套 匀托+煎蛋器 | 30.24 |
| 1910692987664 | （另一种） | 28.08 |
| 1910692987665 | （另一种） | 28.08 |

参考价：64.48元
1688拿货价：16-22元（1件起批）

## 常见坑

1. **ref stale** — PDD页面动态加载，ref在state和click之间可能变化。必须每次click前刷新state
2. **批量修改不生效** — 可能是"加/减"方向错了，或者React input值没正确设置
3. **提交改价按钮找不到** — 文本是"提交改价"不是"商品修改"
4. **弹窗关不掉** — X按钮可能是SVG元素，需要用dispatchEvent MouseEvent click
5. **页面白屏** — 有时导航后页面不加载，需要重新open URL
6. **OpenCLI session频繁断开** — PDD后台操作耗时较长时，OpenCLI的Browser Bridge session会断开（`Target tab is not part of the current browser session`）。对策：重要操作（如改价）尽量一次性完成，避免中间做太多无关操作；session断开后需要重新open URL并导航到目标页面
7. **Camofox不能访问PDD** — PDD检测到非Chrome浏览器会显示"我们检测到您的浏览器不是chrome浏览器"并拦截。必须用OpenCLI（复用Chrome登录态）
8. **"修改价格" vs "编辑"** — "修改价格"只是快速改价弹窗，功能有限；"编辑"打开完整编辑页面，能看到所有SKU、图片、标题。用户明确要求用"编辑"
9. **必填属性阻塞提交** — 编辑页有很多必填属性（品牌、重要材质种类、手柄材质等），1688铺货过来的商品这些属性为空。**如果提交按钮点了没反应，90%是必填属性没填。** 需要先填写属性再改价提交
10. **硅胶厨具套装的必填属性值** — 品牌→无品牌、重要材质种类→硅胶、手柄材质→木。其他产品类似，根据实际材质填写
11. **编辑页session更容易断开** — 编辑页比商品列表页更重（React组件多），session断开概率更高。关键操作（填属性→改价→提交）要快速连续完成
12. **session断开=修改丢失** — 未提交的修改不会保存，session断开后所有改动白费。必须在一次session内完成所有操作并提交
