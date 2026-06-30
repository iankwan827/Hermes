// 批量从低粉爆款视频提取作者信息，然后下载每个作者的主页视频
// 用法：node scripts/opencli_batch_download.js
// 前置条件：Chrome运行 + OpenCLI Browser Bridge已连接

const { execSync } = require('child_process');
const fs = require('fs');

const OUTPUT_DIR = 'D:/videos/low_fan';
const allVideos = JSON.parse(fs.readFileSync('D:/hermes-agent/文案/国学命理爆款库_v3.json', 'utf8'));
const lowFan = allVideos.filter(v => v.fans < 10000 && v.likes > 1000);

const seen = new Set();
const unique = lowFan.filter(v => { if (seen.has(v.aweme_id)) return false; seen.add(v.aweme_id); return true; });

const run = (c) => { try { return execSync(c, { encoding: 'utf8', timeout: 30000 }).trim(); } catch(e) { return ''; } };
const sleep = (ms) => execSync('sleep ' + ms / 1000);

const authorMap = {};
let downloadCount = 0;

// 第一步：提取作者信息 + 下载当前视频
for (let i = 0; i < unique.length; i++) {
  const v = unique[i];
  process.stdout.write(`[${i+1}/${unique.length}] ${v.author}...`);
  run(`opencli browser default open "https://www.douyin.com/video/${v.aweme_id}"`);
  sleep(4000);
  const result = run(`opencli browser default eval "(async () => { const a = window.location.pathname.split('/').pop(); const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'}); const d = await r.json(); const w = d.aweme_detail; if (!w) return JSON.stringify({error:1}); return JSON.stringify({nickname: w.author?.nickname, sec_uid: w.author?.sec_uid, video_url: (w.video?.play_addr?.url_list||[])[0]||''}); })()"`);
  try {
    const info = JSON.parse(result);
    if (info.sec_uid && !info.error) {
      if (!authorMap[info.sec_uid]) authorMap[info.sec_uid] = { nickname: info.nickname, videos: [] };
      if (info.video_url) {
        const safeName = info.nickname.replace(/[\\/:*?"<>|]/g, '_');
        run(`mkdir -p "${OUTPUT_DIR}/${safeName}"`);
        run(`curl -s -o "${OUTPUT_DIR}/${safeName}/${v.aweme_id}.mp4" -L "${info.video_url}" -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/"`);
        downloadCount++;
        console.log(` ✓ (${downloadCount})`);
      } else { console.log(' ✓ 无链接'); }
    } else { console.log(' ✗'); }
  } catch(e) { console.log(' ✗ parse'); }
  sleep(1000);
}

// 第二步：扒作者主页
for (const [secUid, authorInfo] of Object.entries(authorMap)) {
  console.log(`\n--- ${authorInfo.nickname} ---`);
  run(`opencli browser default open "https://www.douyin.com/user/${secUid}"`);
  sleep(5000);
  const vids = run(`opencli browser default eval "(() => { const links = Array.from(document.querySelectorAll('a[href*='/video/']')); const seen = new Set(); const ids = []; links.forEach(a => { const m = a.href.match(/\\/video\\/(\\d+)/); if (m && !seen.has(m[1])) { seen.add(m[1]); ids.push(m[1]); } }); return ids.slice(0,20).join(','); })()"`);
  if (!vids) { console.log('  无视频'); continue; }
  for (const vid of vids.split(',').filter(Boolean)) {
    run(`opencli browser default open "https://www.douyin.com/video/${vid}"`);
    sleep(3000);
    const dl = run(`opencli browser default eval "(async () => { const a = window.location.pathname.split('/').pop(); const r = await fetch('https://www.douyin.com/aweme/v1/web/aweme/detail/?aweme_id=' + a + '&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&version_name=19.6.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0', {credentials:'include'}); const d = await r.json(); const w = d.aweme_detail; if (!w) return ''; return (w.video?.play_addr?.url_list||[])[0]||''; })()"`);
    if (dl) {
      const safeName = authorInfo.nickname.replace(/[\\/:*?"<>|]/g, '_');
      run(`mkdir -p "${OUTPUT_DIR}/${safeName}"`);
      run(`curl -s -o "${OUTPUT_DIR}/${safeName}/${vid}.mp4" -L "${dl}" -H "User-Agent: Mozilla/5.0" -H "Referer: https://www.douyin.com/"`);
      downloadCount++;
    }
    sleep(1000);
  }
}
console.log(`\n完成: ${downloadCount} 个视频, 目录: ${OUTPUT_DIR}`);
