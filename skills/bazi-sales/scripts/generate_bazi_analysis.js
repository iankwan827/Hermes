/**
 * 生成八字排盘和完整断语分析
 * 用法: node generate_bazi_analysis.js <year> <month> <day> <hour> <gender>
 * 例: node generate_bazi_analysis.js 1987 9 12 6 M
 */

const { calculateBazi } = require('./paipan_node_core.js');
const { Gan, Zhi, Shishen, ShishenCalculator } = require('./bazi_classes.js');
const { ShishenWangShuaiCalculator } = require('./shishen_wangshuai.js');
const { BaziInterpreter } = require('./bazi_interpreter.js');
const { ShishenGeshiCalculator } = require('./shishen_geshi.js');
const fs = require('fs');
const path = require('path');

// 从命令行参数读取
const args = process.argv.slice(2);
if (args.length < 5) {
  console.error('用法: node generate_bazi_analysis.js <year> <month> <day> <hour> <gender>');
  console.error('例: node generate_bazi_analysis.js 1987 9 12 6 M');
  process.exit(1);
}

const [year, month, day, hour, genderInput] = args;
let birthHour = parseInt(hour);
let birthDay = parseInt(day);
let birthMonth = parseInt(month) - 1;
let birthYear = parseInt(year);
// 子时换日：23:00起算第二天
if (birthHour >= 23) {
  birthHour = 0;
  birthDay += 1;
}
const gender = (genderInput || '').toUpperCase() === 'F' ? 'F' : 'M';

console.log(`生成八字分析: ${year}年${month}月${day}日${hour}时 ${gender === 'F' ? '女命' : '男命'}`);

// 1. 排盘（需要Date对象）
const dateObj = new Date(birthYear, birthMonth, birthDay, birthHour, 0);
const raw = calculateBazi(dateObj, gender);
const p = raw.pillars;
const pNames = ['年', '月', '日', '时'];

// 2. 十神计算
const dayMaster = new Gan(p[2].gan, 4); // pillarIndex=4表示日干
const gans = p.map(pi => pi.gan);
// 将地支字符串转换为Zhi对象
const zhis = p.map((pi, idx) => new Zhi(pi.zhi, idx * 2 + 1)); // pillarIndex: 1=年支, 3=月支, 5=日支, 7=时支
const shishenResults = ShishenCalculator.calculateAll(dayMaster, gans, zhis, p);
const bodyStrength = raw.bodyStrength || { level: '中和' };

const classPillars = [gans[0], zhis[0], gans[1], zhis[1], gans[2], zhis[2], gans[3], zhis[3]];
ShishenWangShuaiCalculator.calculateAll(shishenResults, zhis, classPillars, bodyStrength);

const interpreter = new BaziInterpreter({
  pillars: p,
  dayMaster: p[2].gan,
  shishenResults,
  bodyStrength,
  gender,
  dayZhi: zhis[2], // 日支Zhi对象
  yearZhi: zhis[0], // 年支Zhi对象
  monthZhi: zhis[1], // 月支Zhi对象
  hourZhi: zhis[3] // 时支Zhi对象
});

// 3. 特征提取
const features = interpreter.detectAll();
const geshi = ShishenGeshiCalculator.calculate(shishenResults, p);

// 4. 生成Markdown
let mdContent = `# ${year}年${month}月${day}日${hour}时 ${gender === 'F' ? '女命' : '男命'} - 八字完整分析\n\n`;
mdContent += `**排盘时间**: ${year}年${month}月${day}日 ${hour}时\n`;
mdContent += `**性别**: ${gender === 'F' ? '女' : '男'}\n`;
mdContent += `**生成时间**: ${new Date().toLocaleString()}\n\n`;

// 四柱排盘
mdContent += `## 【四柱排盘】\n\n`;
p.forEach((pillar, i) => {
  mdContent += `**${pNames[i]}柱**: ${pillar.gan}${pillar.zhi} (${pillar.naYin})${i === 2 ? ' ← 日主' : ''}\n`;
});

// 性格分析（第一步）
mdContent += `\n## 【性格分析】\n\n`;

// 日主性格
const riZhuXingGe = {
  '甲': '甲木为参天大树，正直有主见，向上生长，有担当有魄力，但有时固执己见。',
  '乙': '乙木为花草藤蔓，柔韧灵活，善于适应环境，有亲和力，但有时优柔寡断。',
  '丙': '丙火为太阳之火，热情开朗，光明磊落，有感染力，但有时冲动急躁。',
  '丁': '丁火为灯烛之火，细腻敏感，心思缜密，有洞察力，但有时多疑猜忌。',
  '戊': '戊土为高山大地，厚重稳健，包容性强，有信用，但有时固执保守。',
  '己': '己土为田园之土，温和谦逊，细心周到，有滋养力，但有时多虑犹豫。',
  '庚': '庚金为刀剑之金，刚毅果断，有决断力，重义气，但有时冲动好斗。',
  '辛': '辛金为珠玉之金，精致细腻，有审美力，追求完美，但有时挑剔敏感。',
  '壬': '壬水为江河之水，聪明机智，有大局观，善于变通，但有时放荡不羁。',
  '癸': '癸水为雨露之水，智慧内敛，有洞察力，善于谋略，但有时多愁善感。'
};
const riZhuName = p[2].gan;
mdContent += `**日主${riZhuName}**：${riZhuXingGe[riZhuName] || '性格待分析'}\n\n`;

// 十神性格
const shiShenXingGe = {
  '伤官': '伤官旺者聪明有才华，表达能力强，有创造力，但容易恃才傲物、不服管束。',
  '食神': '食神旺者温和有福气，有口福，有艺术天分，但有时懒散安逸。',
  '正财': '正财旺者务实踏实，重视物质基础，有理财观念，但有时过于计较。',
  '偏财': '偏财旺者大方豪爽，人缘好，有投资眼光，但有时挥霍浪费。',
  '正官': '正官旺者正直守规矩，有责任感，重视名誉，但有时过于保守。',
  '七杀': '七杀旺者有魄力有胆识，敢于冒险，有领导力，但有时冲动好斗。',
  '正印': '正印旺者有学识有涵养，重感情，有贵人缘，但有时依赖心强。',
  '偏印': '偏印旺者思维独特，有悟性，对小众领域有钻研精神，但有时孤僻冷漠。',
  '比肩': '比肩旺者独立自主，有竞争意识，重朋友义气，但有时固执好胜。',
  '劫财': '劫财旺者行动力强，有冲劲，善交际，但有时冲动破财、争强好胜。'
};

// 找出透干的十神及其旺衰
const tGanShiShen = [];
shishenResults.forEach(r => {
  const name = r.shishen.getName();
  if (r.shishen.exists[0] === 1 && shiShenXingGe[name]) {
    tGanShiShen.push({ name, wang: r.shishen.isWang, desc: shiShenXingGe[name] });
  }
});

if (tGanShiShen.length > 0) {
  mdContent += `**十神性格**：\n`;
  tGanShiShen.forEach(ts => {
    mdContent += `- **${ts.name}（透干${ts.wang ? '旺' : '弱'}）**：${ts.desc}\n`;
  });
  mdContent += `\n`;
}

// 组合性格
mdContent += `**组合性格**：\n`;

// 伤官配正财
const hasShangGuan = features.some(f => f.includes('伤官'));
const hasZhengCai = features.some(f => f.includes('正财'));
if (hasShangGuan && hasZhengCai) {
  mdContent += `- **伤官配正财**：才华能变现，适合靠技术/创意/表达赚钱，有商业头脑。\n`;
}

// 官印相生
const hasGuanYin = features.some(f => f.includes('官印相生'));
if (hasGuanYin) {
  mdContent += `- **官印相生**：有责任感有学识，适合在体制内或管理岗位发展，有贵人提携。\n`;
}

// 食伤生财
const hasShiShangShengCai = features.some(f => f.includes('食伤生财'));
if (hasShiShangShengCai) {
  mdContent += `- **食伤生财**：有才华有财运，靠本事吃饭，适合技术型或创作型工作。\n`;
}

// 比肩劫财
const hasBiJie = features.some(f => f.includes('比肩'));
const hasJieCai = features.some(f => f.includes('劫财'));
if (hasBiJie && hasJieCai) {
  mdContent += `- **比肩劫财并见**：竞争意识强，朋友多但也容易有争财之象，花钱大手大脚。\n`;
} else if (hasJieCai) {
  mdContent += `- **劫财旺**：行动力强但容易冲动破财，注意朋友/合伙人争财。\n`;
}

// 伤官见官
const hasZhengGuan = features.some(f => f.includes('正官'));
if (hasShangGuan && hasZhengGuan) {
  mdContent += `- **伤官见官**：容易跟领导/体制起冲突，事业上需要柔性处理关系。\n`;
}

// 地支性格
mdContent += `\n**地支性格**：\n`;
const zhiXingGe = {
  '子': '子水为聪明机智，有谋略，但有时多变。',
  '丑': '丑土为稳重踏实，有耐心，但有时固执。',
  '寅': '寅木为有冲劲有魄力，有领导力，但有时急躁。',
  '卯': '卯木为温和有亲和力，有艺术天分，但有时优柔。',
  '辰': '辰土为有包容力，有贵人缘，但有时犹豫。',
  '巳': '巳火为有热情有才华，有感染力，但有时急躁。',
  '午': '午火为有激情有魄力，有领导力，但有时冲动。',
  '未': '未土为温和有耐心，有滋养力，但有时多虑。',
  '申': '申金为有决断力，有执行力，但有时好斗。',
  '酉': '酉金为精致有品味，有审美力，但有时挑剔。',
  '戌': '戌土为忠诚有义气，有责任感，但有时固执。',
  '亥': '亥水为有智慧有谋略，有大局观，但有时放荡。'
};

const zhiPos = ['年支', '月支', '日支', '时支'];
const zhiKeys = [p[0].zhi, p[1].zhi, p[2].zhi, p[3].zhi];
zhiKeys.forEach((z, idx) => {
  if (zhiXingGe[z]) {
    mdContent += `- **${zhiPos[idx]}${z}**：${zhiXingGe[z]}\n`;
  }
});

// 综合性格总结
mdContent += `\n**综合性格**：`;
let summaryTraits = [];
if (hasShangGuan) summaryTraits.push('聪明有才华');
if (hasZhengCai) summaryTraits.push('务实');
if (hasJieCai) summaryTraits.push('有冲劲');
if (hasZhengGuan) summaryTraits.push('有责任感');
if (features.some(f => f.includes('正印旺'))) summaryTraits.push('有学识但依赖心强');
if (features.some(f => f.includes('卯酉六冲'))) summaryTraits.push('内心有矛盾冲突');
if (features.some(f => f.includes('子卯相刑'))) summaryTraits.push('有时不按常理出牌');
mdContent += summaryTraits.join('、') + '。\n';

// 十神
mdContent += `\n## 【十神（天干）】\n\n`;
p.forEach((pillar, i) => {
  mdContent += `- ${pNames[i]}干: ${pillar.tenGod}\n`;
});

// 身强身弱
mdContent += `\n## 【身强身弱】\n\n`;
mdContent += `**结论**: ${bodyStrength.level}`;
if (geshi && geshi.length > 0) {
  mdContent += ` (${geshi.join('+')})`;
}
mdContent += `\n\n`;

// 主要特征
mdContent += `## 【主要特征】\n\n`;
features.forEach(f => {
  mdContent += `- ${f}\n`;
});

// 大运分析
if (raw.daYun && raw.daYun.length > 0) {
  mdContent += `\n## 【大运分析】\n\n`;
  raw.daYun.forEach(dy => {
    mdContent += `### ${dy.startAge}-${dy.endAge}岁（${dy.gan}${dy.zhi}）\n`;
    if (dy.description) {
      mdContent += `${dy.description}\n`;
    }
    mdContent += `\n`;
  });
}

// 保存文件
const outDir = path.join(__dirname, '..', 'references');
const outPath = path.join(outDir, `${year}${month}${day}${gender === 'F' ? '女' : '男'}命.md`);
fs.writeFileSync(outPath, mdContent, 'utf-8');

console.log(`\n✅ 八字分析已生成: ${outPath}\n`);
console.log(`排盘确认:`);
p.forEach((pillar, i) => {
  console.log(`${pNames[i]}柱: ${pillar.gan}${pillar.zhi}`);
});
console.log(`\n身强身弱: ${bodyStrength.level}`);
console.log(`主要特征: ${features.slice(0, 5).join(', ')}`);
