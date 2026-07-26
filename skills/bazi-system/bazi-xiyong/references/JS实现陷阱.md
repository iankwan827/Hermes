# JS/HTML实现八字软件的常见陷阱

## 变量作用域问题

### 问题：函数内定义的变量，其他函数访问不到

```javascript
// ❌ 错误：tongguanMedicine定义在renderYongShen内部
function renderYongShen() {
  let tongguanMedicine = '水'; // 其他函数访问不到
}

// ✅ 正确：定义为全局变量
let tongguanMedicine = ''; // 在文件顶部定义
function renderYongShen() {
  tongguanMedicine = '水'; // 赋值
}
function renderStrengthSummary() {
  console.log(tongguanMedicine); // 可以访问
}
```

### 解决方案：关键变量必须定义为全局变量

```javascript
// 文件顶部定义全局变量
let sandeLevel = '';      // 三得法结果
let tongguanMedicine = ''; // 通关用神
let bingyaoMedicine = ''; // 病药用神
let currentResult = null;  // 排盘结果
```

## pi.hidden 对象数组问题

### 问题：pi.hidden是对象数组，不是字符串数组

```javascript
// ❌ 错误：直接用ganWx(h)
p.forEach(pi => {
  (pi.hidden || []).forEach(h => {
    const hwx = ganWx(h); // h是对象{stem:"戊",...}，不是字符串
  });
});

// ✅ 正确：用h.stem
p.forEach(pi => {
  (pi.hidden || []).forEach(h => {
    const hStem = typeof h === 'string' ? h : (h.stem || '');
    const hwx = ganWx(hStem);
  });
});
```

## WX_WANGXIANG查找问题

### 问题：WX_WANGXIANG按月支五行查，不是按月支查

```javascript
// ❌ 错误：用monthZhi
const monthStatus = (WX_WANGXIANG[monthZhi] || {})[wx];

// ✅ 正确：用monthWx（月支五行）
const monthWx = zhiWx(monthZhi);
const monthStatus = (WX_WANGXIANG[monthWx] || {})[wx];
```

## CHANG_SHENG天干key问题

### 问题：CHANG_SHENG按天干查，不是按五行查

```javascript
// ❌ 错误：用五行
const cs = (CHANG_SHENG['木'] || {})[zhi]; // 不存在

// ✅ 正确：用天干（阳干或日主天干）
const cs = (CHANG_SHENG['庚'] || {})[zhi]; // 庚金
```

## 五行相生映射写反

### 问题：shengMap写反了

```javascript
// ❌ 错误：木生水（错）
const shengMap = { '木':'水', '火':'木', ... };

// ✅ 正确：水生木（水→木）
const shengMap = { '水':'木', '木':'火', '火':'土', '土':'金', '金':'水' };
```

## 十神映射错误

### 问题：印星和食伤搞反

```javascript
// ❌ 错误：印星是日主生的五行
const shengWx = shengMap[dayWx]; // 这是食伤，不是印星！

// ✅ 正确：印星是生我的五行（反向查找）
const shengWx = Object.entries(shengMap).find(([k, v]) => v === dayWx)?.[0] || '';
```

## 变量文档化

### 必须记录的变量信息

每个关键变量必须记录：
1. 变量名
2. 数据内容
3. 数据来源
4. 赋值位置（哪一行）
5. 使用位置（哪些函数）

### 示例：变量数据字典

```
| 变量名 | 数据 | 来源 | 赋值位置 | 使用位置 |
|--------|------|------|---------|---------|
| sandeLevel | 三得法结果 | computeSanDe() | line 477 | renderTab2, renderStrengthSummary |
| bingyaoMedicine | 病药用神五行 | renderYongShen() | line 1166 | renderYongShen, renderStrengthSummary |
```

**关键原则：已计算的结果直接用，不要重新算。**
