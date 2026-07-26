const { calculateBazi } = require('./paipan_node_core.js');
const { Gan, Zhi, Shishen, ShishenCalculator } = require('./bazi_classes.js');
const { ShishenWangShuaiCalculator } = require('./shishen_wangshuai.js');
const { BaziInterpreter } = require('./bazi_interpreter.js');
const { ShishenGeshiCalculator } = require('./shishen_geshi.js');
const fs = require('fs');

// 1987年9月12日06时，男
const birthDate = new Date(1987, 8, 12, 6, 0, 0); // 月份是0-indexed
const gender = 'M';

console.log('\n╔════════════════════════════════════════════╗');
console.log('║       八字完整验算过程                      ║');
console.log('╚════════════════════════════════════════════╝\n');

console.log('【输入信息】');
console.log('出生时间：1987年9月12日 06时');
console.log('性别：男');
console.log('\n【正在计算...】\n');

// 核心计算
const raw = calculateBazi(birthDate, gender);
const p = raw.pillars;

// 初始化
const gans = [
  new Gan(p[0].gan, 0),
  new Gan(p[1].gan, 2),
  new Gan(p[2].gan, 4),
  new Gan(p[3].gan, 6)
];
const zhis = [
  new Zhi(p[0].zhi, 1),
  new Zhi(p[1].zhi, 3),
  new Zhi(p[2].zhi, 5),
  new Zhi(p[3].zhi, 7)
];

zhis.forEach((z, i) => {
  z.setupHiddenShishen(p[i].hidden || []);
  z.kongWang = p[i].kongWang || [];
  z.shenSha = p[i].shenSha || [];
});

const dayMaster = new Shishen(p[2].gan, p[2].tenGod);
const shishenResults = ShishenCalculator.calculateAll(dayMaster, gans, zhis, p);
const bodyStrength = raw.bodyStrength || { level: '中和' };

const classPillars = [gans[0], zhis[0], gans[1], zhis[1], gans[2], zhis[2], gans[3], zhis[3]];
ShishenWangShuaiCalculator.calculateAll(shishenResults, zhis, classPillars, bodyStrength);

const interpreter = new BaziInterpreter({
  shishenResults, pillars: p, dayMaster,
  yearZhi: zhis[0], monthZhi: zhis[1], dayZhi: zhis[2], hourZhi: zhis[3],
  getAllGans: () => gans, getAllZhis: () => zhis, bodyStrength
});
const features = interpreter.detectAll();

const geshiResults = ShishenGeshiCalculator.calculate(shishenResults);

// 输出排盘
console.log('【四柱排盘】');
const pNames = ['年', '月', '日', '时'];
p.forEach((pillar, i) => {
  console.log(`${pNames[i]}柱：${pillar.gan}${pillar.zhi} (${pillar.naYin}${i === 2 ? ' ← 日主' : ''})`);
});

console.log('\n【十神（天干）】');
p.forEach((pillar, i) => {
  console.log(`${pNames[i]}干：${pillar.tenGod}`);
});

console.log('\n【藏干十神】');
zhis.forEach((z, i) => {
  const hidden = z.getAllHiddenGansWithShishen().map(h => `${h.gan}(${h.shishen})`).join(', ');
  console.log(`${pNames[i]}支 (${z.name})：${hidden || '无'}`);
});

console.log('\n【十神旺衰表】');
console.log('十神   | 旺/衰 | 受制 | 用忌');
console.log('-------|-------|------|------');
shishenResults.forEach(r => {
  const s = r.shishen;
  console.log(`${s.getName().padEnd(4)} | ${(s.isWang ? '旺' : '衰').padEnd(4)} | ${(s.isShouZhi ? '是' : '否').padEnd(3)} | ${s.xiYong || '闲'}`);
});

console.log('\n【身强身弱】');
console.log(`结论：${bodyStrength.level}`);

console.log('\n【特征检测】');
if (features.length > 0) {
  for (let i = 0; i < features.length; i += 3) {
    console.log(features.slice(i, i + 3).join('  |  '));
  }
} else {
  console.log('无显著特征');
}

console.log('\n【格局分析】');
if (geshiResults.patterns && geshiResults.patterns.length > 0) {
  geshiResults.patterns.forEach(p => {
    console.log(`• ${p}`);
  });
} else {
  console.log('无特殊格局');
}

console.log('\n【大运流年概览】');
if (raw.daYunList && raw.daYunList.length > 0) {
  console.log(`当前大运：${raw.currentDaYun ? raw.currentDaYun.ganZhi + ' (' + raw.currentDaYun.age + '岁)' : '计算中'}`);
  console.log(`未来大运：`);
  raw.daYunList.slice(0, 3).forEach(dy => {
    console.log(`  • ${dy.ganZhi} (${dy.startAge}-${dy.startAge + 9}岁)`);
  });
}

// 构造完整的baziData供后续分析使用
const baziData = {
  metadata: {
    gender: '男',
    birth_date: '1987/9/12 6:00:00',
    calculation_time: new Date().toLocaleString()
  },
  pillars: p.map((pillar, i) => ({
    name: pNames[i],
    gan: pillar.gan,
    zhi: pillar.zhi,
    nayyin: pillar.naYin,
    ten_god_gan: pillar.tenGod,
    hidden_gans: zhis[i].getAllHiddenGansWithShishen(),
    kong_wang: zhis[i].kongWang,
    shen_sha: zhis[i].shenSha
  })),
  day_master: {
    name: dayMaster.name,
    element: dayMaster.wx,
    ten_god: dayMaster.relationToDayMaster
  },
  dynamics: {
    body_strength: bodyStrength.level,
    features: features,
    geshi: geshiResults.patterns,
  },
  ten_gods: shishenResults.map(r => ({
    name: r.shishen.getName(),
    gan: r.ganName,
    is_wang: r.shishen.isWang === 1,
    is_constrained: r.shishen.isShouZhi === 1,
    utility: r.shishen.xiYong,
    presence: {
      in_stems: r.exists[0] === 1,
      in_branches: r.exists[1] === 1
    }
  }))
};

// 保存数据供分析
fs.writeFileSync('bazi_verify.json', JSON.stringify(baziData, null, 2), 'utf8');

console.log('\n=====================================\n');
console.log('✅ 排盘数据已保存至 bazi_verify.json');
console.log('📊 开始加载知识库进行断语分析...\n');

// ========== 开始断语分析 ==========

console.log('╔════════════════════════════════════════════╗');
console.log('║       根据JSON知识库的断语应用             ║');
console.log('╚════════════════════════════════════════════╝\n');

// 01 事业
console.log('【01 事业分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const hasOfficial = shishenResults.find(r => r.shishen.getName() === '正官');
const hasSeven = shishenResults.find(r => r.shishen.getName() === '七杀');
const hasPrinting = shishenResults.find(r => ['正印', '偏印'].includes(r.shishen.getName()));
const hasWealth = shishenResults.find(r => ['正财', '偏财'].includes(r.shishen.getName()));
const hasFood = shishenResults.find(r => ['食神', '伤官'].includes(r.shishen.getName()));

if (hasOfficial && hasOfficial.shishen.xiYong === '用') {
  console.log('✓ 正官为用：仕途平稳，易得上级赏识，适合按部就班发展');
}
if (hasSeven && hasSeven.shishen.xiYong === '用') {
  console.log('✓ 七杀为用：权力欲强，适合有挑战性、高回报的领域');
}
if (hasPrinting && hasPrinting.shishen.xiYong === '用') {
  console.log('✓ 印星为用：智慧过人，易得贵人相助，适合专业技术与学术领域');
}
if (hasFood && hasFood.shishen.xiYong === '用') {
  console.log('✓ 食伤为用：创造力强，适合需要表达与创新的领域');
}

if (bodyStrength.level === '身强') {
  console.log('✓ 身强：确定个人能力强、能独当一面，适合创业、管理');
} else if (bodyStrength.level === '身弱') {
  console.log('✓ 身弱：需辅助、适合团队协作');
}

// 02 财运
console.log('\n【02 财运分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const wealth = shishenResults.find(r => ['正财', '偏财'].includes(r.shishen.getName()));
if (bodyStrength.level === '身强' && wealth && wealth.shishen.isWang) {
  console.log('✓ 身强财旺：日主能量充足，能承受大量财富，容易富贵');
}
if (wealth && wealth.shishen.xiYong === '用') {
  console.log('✓ 财星为用：追求财富的动力强，为事业提供物质基础');
}
if (hasFood && hasFood.shishen.isWang && wealth) {
  console.log('✓ 食伤生财：财源滚滚，赚钱机会多');
}

// 03 婚姻
console.log('\n【03 婚姻感情分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const dayZhi = p[2].zhi;
const dayGan = p[2].gan;
console.log(`日柱：${dayGan}${dayZhi}`);
if (features.includes('日柱同五行')) {
  console.log('⚠ 日柱同五行：婚姻缘分可能较薄，需后天经营');
}
const wealthForMale = shishenResults.find(r => r.shishen.getName() === '正财');
if (wealthForMale && wealthForMale.shishen.xiYong === '用') {
  console.log('✓ 正财为用（男命）：配偶贤惠持家、务实稳重、重视家庭');
}

// 04 学业
console.log('\n【04 学业分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const printing = shishenResults.find(r => ['正印', '偏印'].includes(r.shishen.getName()));
if (printing && printing.shishen.xiYong === '用' && printing.shishen.isWang) {
  console.log('✓ 印星为用且旺相：学历必高，学习能力强');
}
const foodShang = shishenResults.find(r => ['食神', '伤官'].includes(r.shishen.getName()));
if (foodShang && foodShang.shishen.xiYong === '用') {
  console.log('✓ 食伤为用：聪明外露，成绩顶尖');
}
if (hasOfficial && printing && hasOfficial.shishen.xiYong === '用') {
  console.log('✓ 官印相生：学习自觉，师长助力，考试必成功');
}

// 05 子女
console.log('\n【05 子女分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log('（男命看正官为女儿，七杀为儿子）');
if (hasOfficial && hasOfficial.shishen.xiYong === '用' && hasOfficial.shishen.isWang) {
  console.log('✓ 正官为用且旺相：女儿优秀孝顺');
}
if (hasSeven && hasSeven.shishen.xiYong === '用' && hasSeven.shishen.isWang) {
  console.log('✓ 七杀为用且旺相：儿子优秀有出息');
}

// 06 健康
console.log('\n【06 健康分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`日主五行：${dayMaster.wx}`);
const wuxingMap = {'木': '肝胆', '火': '心脑血管', '土': '脾胃', '金': '肺呼吸', '水': '肾泌尿'};
console.log(`对应脏腑：${wuxingMap[dayMaster.wx]}`);

// 07 性格
console.log('\n【07 性格分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const yearGan = p[0].gan;
const hourGan = p[3].gan;
console.log(`年干：${yearGan}，时干：${hourGan}`);
if (yearGan === hourGan) {
  console.log(`✓ 两头挂（${yearGan}）：最强特质体现`);
}
const stemTraits = {
  '甲': '参天大树，向阳生长 - 直率、有主见、进取心强',
  '乙': '藤蔓花草，柔韧纠缠 - 柔和、聪慧、适应力强',
  '丙': '太阳之火，热烈坦率 - 热情、坦率、外向、乐观',
  '丁': '灯火之火，温柔内敛 - 内敛、敏感、温柔',
  '戊': '高山之土，厚重稳实 - 踏实、诚恳、稳重',
  '己': '田园之土，细心谨慎 - 细心、谨慎、有计划',
  '庚': '刀剑之金，刚直锋利 - 直爽、有主见、刚强',
  '辛': '珠宝之金，精致敏感 - 精致、敏感、聪慧',
  '壬': '江河之水，聪慧流动 - 聪慧、机智、热情',
  '癸': '雨露之水，柔和包容 - 温柔、包容、敏感'
};
console.log(`日元（${dayGan}）性格：${stemTraits[dayGan]}`);

// 08 父母
console.log('\n【08 父母分析】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
if (printing && printing.shishen.xiYong === '用' && printing.shishen.isWang) {
  console.log('✓ 印星为用且旺相：与父母关系和睦，得父母助力');
}

// 09 命理技法
console.log('\n【09 命理技法】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`✓ 身强身弱：${bodyStrength.level}`);
console.log(`✓ 五行平衡需检查各十神强弱`);
if (raw.interactions && raw.interactions.stems) {
  console.log(`✓ 天干刑冲合会：${JSON.stringify(raw.interactions.stems).substring(0, 50)}...`);
}

// 10 风水
console.log('\n【10 风水阳宅】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
const orientMap = {'木': '东方', '火': '南方', '土': '中央', '金': '西方', '水': '北方'};
const colorMap = {'木': '绿色', '火': '红色', '土': '黄色', '金': '白/金色', '水': '蓝/黑色'};
console.log(`✓ 日主五行（${dayMaster.wx}）宜选${orientMap[dayMaster.wx]}`);
console.log(`✓ 装修配色建议：${colorMap[dayMaster.wx]}`);

// 11 神煞
console.log('\n【11 神煞特煞】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
let hasShenSha = false;
zhis.forEach((z, i) => {
  if (z.shenSha && z.shenSha.length > 0) {
    console.log(`${pNames[i]}支神煞：${z.shenSha.join('、')}`);
    hasShenSha = true;
  }
});
if (!hasShenSha) {
  console.log('未发现特殊神煞');
}

// 12 十干
console.log('\n【12 十干】');
console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
console.log(`日元：${dayGan}${dayMaster.wx} - ${stemTraits[dayGan]}`);

console.log('\n╔════════════════════════════════════════════╗');
console.log('║           验算完成！                        ║');
console.log('╚════════════════════════════════════════════╝\n');
