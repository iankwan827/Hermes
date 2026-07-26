# 八字多Agent系统 Skill包

**打包时间**: 2026-07-26
**用途**: 将八字分析系统的所有skill打包，方便部署到新环境或Windows端同步

## 包含内容

### 📁 bazi-system/ (40个skill)

#### 系统架构类
| Skill | 说明 |
|-------|------|
| bazi-master | 协调器/指挥，按八层体系调度分析Agent |
| bazi-analyst | 分析Agent，读排盘JSON执行各层分析 |
| bazi-reviewer | 审核Agent，校验十神/用神/skill完整性 |
| bazi-responder | 回复Agent，读JSON用命理师视角输出 |
| bazi-exporter | 导出Agent，标准化JSON输出 |
| bazi-paipan | 排盘（含JS脚本generate_bazi_analysis.js） |
| bazi-trigger | 条件触发检测，输出trigger.json |
| bazi-finder | 定位Agent，确定分析方向 |
| bazi-baceng | 八层体系框架 |
| bazi-duanshi | 断事方法论 |

#### 基础知识类
| Skill | 说明 |
|-------|------|
| bazi-shishen | 十神分类、详解、组合（总纲） |
| bazi-dizhi | 地支关系：三会/三合/六冲/刑害 |
| bazi-sizhu | 四柱代表、宫位分析 |
| bazi-xiyong | 取喜用神（6维度交叉验证） |
| bazi-analysis-writing | 分析写作指导 |

#### 十神专题（10个）
| Skill | 十神 |
|-------|------|
| bazi-shishen-bijian | 比肩 |
| bazi-shishen-jiecai | 劫财 |
| bazi-shishen-piancai | 偏财 |
| bazi-shishen-zhengcai | 正财 |
| bazi-shishen-shishen | 食神 |
| bazi-shishen-shangguan | 伤官 |
| bazi-shishen-pianyin | 偏印 |
| bazi-shishen-zhengyin | 正印 |
| bazi-shishen-qisha | 七杀 |
| bazi-shishen-zhengguan | 正官 |
| bazi-shishen-tiangan | 十天干日元专题 |

#### 专项分析类
| Skill | 说明 |
|-------|------|
| bazi-xingge | 性格分析 |
| bazi-peiou | 配偶画像分析 |
| bazi-hunyin-tongwuxing | 上下同五行=二婚之象 |
| bazi-zhi | 痣相三板斧 |
| bazi-xinglengdan | 性冷淡八字密码 |
| bazi-xiongbu | 胸部大小判断 |
| bazi-haose | 好色格局判断 |
| bazi-shencai | 身材体型 |
| bazi-daogui | 被女倒追特征 |
| bazi-lanyin | 印星过旺与懒 |
| bazi-chuanzhuo | 穿着搭配风格 |

#### 健康类
| Skill | 说明 |
|-------|------|
| bazi-weibing | 脾胃病分析 |
| bazi-feibu | 肺部健康分析 |
| bazi-shenbing | 肾病分析 |
| bazi-xinzangbing | 心脏健康分析 |
| bazi-ganbing | 肝部健康分析 |

### 📁 bazi-sales/ (5个skill + 知识库)

| Skill | 说明 |
|-------|------|
| bazi-fukeshengyu | 女命流产/剖腹产/子宫卵巢判断 |
| bazi-zhiduan | 直断速查（28秘诀+十天干性格等） |
| bazi-sales-steps | 销售实战步骤汇总 |
| bazi-sales-agent6-lifespan | 寿命判断专家 |
| references/ | 15份知识库JSON/MD + 案例 |

### 📁 scripts/ (7个JS脚本)
- `generate_bazi_analysis.js` — 排盘主脚本
- `paipan_node_core.js` — 排盘核心逻辑
- `bazi_interpreter.js` — 解释器
- `bazi_classes.js` — 天干地支类
- `shishen_geshi.js` — 十神格式化
- `shishen_wangshuai.js` — 十神旺衰
- `verify_bazi.js` — 验证脚本

## 部署方法

### 新环境部署
```bash
cd ~/.hermes/profiles/main/skills/
tar xzf bazi-skills-package.tar.gz
# 重启 Hermes 使 skill 生效
```

### Windows端同步
```bash
cd E:/Users/Administrator/AppData/Local/hermes/skills/
tar xzf bazi-skills-package.tar.gz
```

### 依赖
- Node.js（排盘JS脚本需要）
- `node generate_bazi_analysis.js <年> <月> <日> <时> <性别(M/F)>`
