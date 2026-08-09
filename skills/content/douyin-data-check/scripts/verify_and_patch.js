#!/usr/bin/env node
/**
 * verify_and_patch.js — 自动对比页面数据与发展日志，输出差异并可选自动修复
 * 
 * 用法：
 *   1. 在cron job中，从eval提取数据后填入下方 pageData 对象
 *   2. 运行: node scripts/verify_and_patch.js
 *   3. 输出所有差异（播放量、点赞、评论、分享、收藏）
 *   4. 如需自动修复，加 --patch 参数: node scripts/verify_and_patch.js --patch
 * 
 * 页面列顺序: cells[8]=点赞, cells[9]=分享, cells[10]=评论, cells[11]=收藏
 * 日志列顺序: 点赞, 评论, 分享, 收藏
 * ⚠️ 评论和分享的顺序是反的！
 */

const fs = require('fs');
const path = require('path');

// ===== 配置 =====
const LOG_PATH = path.resolve(__dirname, '../references/发展日志.md');

// ===== 页面数据（从eval提取后填入）=====
// 格式: { videoId: { plays, likes, comments, shares, fav } }
// 注意: comments 和 shares 的值必须按页面原始列顺序填入
// cells[9]=分享, cells[10]=评论
const pageData = {
  // 示例（cron job中替换为实际数据）:
  // V28: { plays: 368, likes: 0, comments: 0, shares: 0, fav: 0 },
  // V27: { plays: 508, likes: 3, comments: 0, shares: 0, fav: 0 },
};

// ===== 解析发展日志表格 =====
function parseLogTable(content) {
  const lines = content.split('\n');
  const data = {};
  for (const line of lines) {
    // 匹配表格行: | V28 | 标题 | 日期 | 播放量 | ... | 点赞 | 评论 | 分享 | 收藏 | 状态 |
    const match = line.match(/^\|\s*(V\d+)\s*\|/);
    if (!match) continue;
    const vid = match[1];
    const cells = line.split('|').map(c => c.trim());
    // cells[0]="" (行首), cells[1]=V28, cells[2]=标题, cells[3]=日期, cells[4]=播放量,
    // cells[5]=完播率, cells[6]=5s完播率, cells[7]=2s跳出率, cells[8]=平均播放时长,
    // cells[9]=点赞, cells[10]=评论, cells[11]=分享, cells[12]=收藏, cells[13]=状态
    if (cells.length >= 13) {
      data[vid] = {
        plays: parseInt(cells[4].replace(/,/g, '')) || 0,
        likes: parseInt(cells[9]) || 0,
        comments: parseInt(cells[10]) || 0,
        shares: parseInt(cells[11]) || 0,
        fav: parseInt(cells[12]) || 0,
        raw: line
      };
    }
  }
  return data;
}

// ===== 对比 =====
function compare(pageData, logData) {
  const diffs = [];
  for (const [vid, page] of Object.entries(pageData)) {
    const log = logData[vid];
    if (!log) {
      diffs.push({ vid, type: 'MISSING_IN_LOG', page, log: null });
      continue;
    }
    const fields = ['plays', 'likes', 'comments', 'shares', 'fav'];
    for (const f of fields) {
      if (page[f] !== log[f]) {
        diffs.push({
          vid,
          type: 'MISMATCH',
          field: f,
          page: page[f],
          log: log[f],
          rawLine: log.raw
        });
      }
    }
  }
  return diffs;
}

// ===== 主流程 =====
const logContent = fs.readFileSync(LOG_PATH, 'utf-8');
const logData = parseLogTable(logContent);

console.log(`Parsed ${Object.keys(logData).length} videos from log`);
console.log(`Comparing ${Object.keys(pageData).length} videos from page data\n`);

if (Object.keys(pageData).length === 0) {
  console.log('⚠️  No page data entered. Fill in the pageData object at the top of this script.');
  console.log('    Extract data with: opencli browser douyin eval "..." then paste values here.');
  process.exit(0);
}

const diffs = compare(pageData, logData);

if (diffs.length === 0) {
  console.log('✅ No differences found. All data matches.');
  process.exit(0);
}

console.log(`❌ Found ${diffs.length} differences:\n`);
for (const d of diffs) {
  if (d.type === 'MISSING_IN_LOG') {
    console.log(`${d.vid}: NOT FOUND in log (page: plays=${d.page.plays})`);
  } else {
    const fieldNames = { plays: '播放量', likes: '点赞', comments: '评论', shares: '分享', fav: '收藏' };
    console.log(`${d.vid} ${fieldNames[d.field] || d.field}: log=${d.log} → page=${d.page}`);
  }
}

// 如果有 --patch 参数，生成修复命令
if (process.argv.includes('--patch')) {
  console.log('\n--- Patch commands ---');
  for (const d of diffs) {
    if (d.type === 'MISMATCH') {
      const oldLine = d.rawLine;
      // 简单替换对应字段（需要根据实际表格结构调整）
      console.log(`# ${d.vid} ${d.field}: ${d.log} → ${d.page}`);
    }
  }
  console.log('\n⚠️  Auto-patch not implemented for complex table formats.');
  console.log('    Use node.js string replacement manually for reliability.');
}
