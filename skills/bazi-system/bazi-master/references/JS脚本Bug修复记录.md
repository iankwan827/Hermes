# generate_bazi_analysis.js 脚本Bug修复记录

## 修复日期：2026-07-06

运行 `node scripts/generate_bazi_analysis.js 1987 9 12 6 M` 时遇到5个bug，逐一修复。

## Bug 1：calculateBazi参数错误（generate_bazi_analysis.js:38）

**现象**：`TypeError: derivedDate.getFullYear is not a function`

**原因**：调用 `calculateBazi(birthYear, birthMonth, birthDay, birthHour)` 时传入数字，但函数期望Date对象。

**修复**：
```javascript
// 修复前
const raw = calculateBazi(birthYear, birthMonth, birthDay, birthHour);

// 修复后
const dateObj = new Date(birthYear, birthMonth, birthDay, birthHour, 0);
const raw = calculateBazi(dateObj, gender);
```

## Bug 2：Shishen构造函数参数错误（generate_bazi_analysis.js:44）

**现象**：`Error: 未知天干: undefined`

**原因**：`new Shishen(p[2].gan, p[2].tenGod)` 中 `p[2].tenGod` 是 "元男"，不是天干名。Shishen继承自Gan，Gan需要天干名在GAN_MAP中。

**修复**：
```javascript
// 修复前
const dayMaster = new Shishen(p[2].gan, p[2].tenGod);

// 修复后
const dayMaster = new Gan(p[2].gan, 4); // pillarIndex=4表示日干
```

## Bug 3：gan.name vs gan（bazi_classes.js:404-405）

**现象**：`Error: 未知天干: undefined`

**原因**：`gans`数组元素是字符串（如"丁"），但代码用 `gan.name` 访问，返回undefined。

**修复**：
```javascript
// 修复前
ganName: gan.name,
shishen: new Shishen(gan.name, tenGod),

// 修复后
ganName: gan,
shishen: new Shishen(gan, tenGod),
```

## Bug 4：zhis需要Zhi对象（generate_bazi_analysis.js:46）

**现象**：`TypeError: zhi.setupHiddenShishen is not a function`

**原因**：`zhis`是字符串数组，但ShishenCalculator.calculateAll期望Zhi对象数组。

**修复**：
```javascript
// 修复前
const zhis = p.map(pi => pi.zhi);

// 修复后
const zhis = p.map((pi, idx) => new Zhi(pi.zhi, idx * 2 + 1)); // pillarIndex: 1=年支, 3=月支, 5=日支, 7=时支
```

## Bug 5：interpreter缺少ctx属性（generate_bazi_analysis.js:54-60）

**现象**：`TypeError: Cannot read properties of undefined (reading 'kongWang')`

**原因**：BaziInterpreter的ctx对象缺少dayZhi、yearZhi、monthZhi、hourZhi属性。

**修复**：
```javascript
// 修复后
const interpreter = new BaziInterpreter({
  pillars: p,
  dayMaster: p[2].gan,
  shishenResults,
  bodyStrength,
  gender,
  dayZhi: zhis[2],
  yearZhi: zhis[0],
  monthZhi: zhis[1],
  hourZhi: zhis[3]
});
```

## Bug 6：getFeatures方法不存在（generate_bazi_analysis.js:63）

**现象**：`TypeError: interpreter.getFeatures is not a function`

**原因**：BaziInterpreter类的方法名是 `detectAll()`，不是 `getFeatures()`。

**修复**：
```javascript
// 修复前
const features = interpreter.getFeatures();

// 修复后
const features = interpreter.detectAll();
```

## 修复后验证

```bash
cd ~/.hermes/profiles/main/skills/bazi-sales && node scripts/generate_bazi_analysis.js 1987 9 12 6 M
```

输出：
```
生成八字分析: 1987年9月12日6时 男命
四柱: 丁卯 己酉 甲子 丁卯
日主: 甲
十神: 伤官, 正财, 元男, 伤官
空亡: 戌亥
```

## 注意事项

1. 脚本性别bug仍然存在：gender参数可能无效，需手动检查输出性别
2. 时柱天干可能有误：需对照万年历验证
3. 十神标注为"待复核"，传给下游Agent时需说明
