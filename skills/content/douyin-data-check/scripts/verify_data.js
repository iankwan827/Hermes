#!/usr/bin/env node
// verify_data.js — Compare page data vs development log table
// Usage: Fill in pageData from eval extraction, then run: node verify_data.js
// Output: lists all discrepancies between page data and log table rows

const fs = require('fs');
const path = require('path');

const logPath = path.join(__dirname, '..', 'references', '发展日志.md');
const log = fs.readFileSync(logPath, 'utf-8');

// === FILL IN PAGE DATA (from eval extraction results) ===
const pageData = {
  // Example:
  // V28: {plays:368, likes:0, shares:0, comments:0, fav:0},
  // V27: {plays:506, likes:3, shares:0, comments:0, fav:0},
};

if (Object.keys(pageData).length === 0) {
  console.log('ERROR: Fill in pageData first. See verify_data.js source.');
  process.exit(1);
}

// Parse log table rows
// Format: | V28 | title | date | plays | comp | 5s | 2s | avg | likes | comments | shares | fav | status |
const tableRows = log.split('\n').filter(l => l.match(/^\| V\d+/));
const discrepancies = [];

tableRows.forEach(row => {
  const match = row.match(/\| (V\d+) \|/);
  if (!match) return;
  const vid = match[1];
  const cells = row.split('|').map(c => c.trim());
  // Cell indices: [0]='', [1]=Vxx, [2]=title, [3]=date, [4]=plays, [5]=comp,
  // [6]=5s, [7]=2s, [8]=avg, [9]=likes, [10]=comments, [11]=shares, [12]=fav, [13]=status
  const logPlays = parseInt(cells[4].replace(/,/g, ''));
  const logLikes = parseInt(cells[9]);
  const logComments = parseInt(cells[10]);
  const logShares = parseInt(cells[11]);
  const logFav = parseInt(cells[12]);

  const pd = pageData[vid];
  if (!pd) return;

  const diffs = [];
  if (logPlays !== pd.plays) diffs.push('plays:' + logPlays + '->' + pd.plays);
  if (logLikes !== pd.likes) diffs.push('likes:' + logLikes + '->' + pd.likes);
  if (logComments !== pd.comments) diffs.push('comments:' + logComments + '->' + pd.comments);
  if (logShares !== pd.shares) diffs.push('shares:' + logShares + '->' + pd.shares);
  if (logFav !== pd.fav) diffs.push('fav:' + logFav + '->' + pd.fav);

  if (diffs.length > 0) {
    discrepancies.push(vid + ': ' + diffs.join(', '));
  }
});

console.log('Discrepancies found: ' + discrepancies.length);
discrepancies.forEach(d => console.log(d));
if (discrepancies.length === 0) console.log('All data matches.');
