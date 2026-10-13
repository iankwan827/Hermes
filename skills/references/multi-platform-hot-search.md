# 多平台热搜 API 直查

> 当 anysearch CLI 不可用或需要实时热搜数据时，可直接调用以下公开 API。

## 抖音热榜

```
GET https://www.douyin.com/aweme/v1/web/hot/search/list/
Headers: User-Agent + Referer: https://www.douyin.com/
```

**响应结构**：
- `data.word_list[]` — 热榜（含 hot_value, label）
- `data.trending_list[]` — 实时上升热点

**label 含义**：1=新, 2=热, 3=爆, 8=荐, 9=挑战, 16=广告

**Node.js 解析**：
```js
const data = JSON.parse(body);
const words = data.data.word_list || [];
words.slice(0,20).forEach((w,i) => {
  console.log(`${i+1}. ${w.word} (${w.hot_value})`);
});
```

---

## 微博热搜

```
GET https://weibo.com/ajax/side/hotSearch
Headers: User-Agent + Referer: https://weibo.com/
```

**响应结构**：
- `data.realtime[]` — 热搜列表（含 note, num, is_hot, is_new, is_fei）

**标签**：is_hot=[热], is_new=[新], is_fei=[沸]

**Node.js 解析**：
```js
const list = data.data?.realtime || [];
list.slice(0,20).forEach((w,i) => {
  console.log(`${i+1}. ${w.note} (${w.num})`);
});
```

---

## 百度热搜

```
GET https://top.baidu.com/board?tab=realtime
Headers: User-Agent
```

**注意**：返回 HTML，需正则或 DOM 解析提取 `"word":"xxx"` 字段。

**Node.js 解析**：
```js
const matches = html.match(/"word":"([^"]+)"/g) || [];
matches.slice(0,20).forEach((m,i) => {
  const word = m.replace(/"word":"/, '').replace(/"$/, '');
  console.log(`${i+1}. ${word}`);
});
```

---

## 今日头条热榜

```
GET https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc
Headers: User-Agent + Referer: https://www.toutiao.com/
```

**响应结构**：
- `data[]` — 热榜（含 Title 字段）

**Node.js 解析**：
```js
const list = data.data || [];
list.slice(0,20).forEach((w,i) => {
  console.log(`${i+1}. ${w.Title}`);
});
```

---

## 知乎热榜

```
GET https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20
Headers: User-Agent + Referer: https://www.zhihu.com/
```

**注意**：可能需要登录态，匿名请求可能返回空数据。如需使用，考虑 OpenCLI 复用 Chrome 登录态。

---

## 热搜话题深度调研：搜狗微信搜索

拿到热搜列表后，用户通常需要了解具体话题的内容。推荐用搜狗微信搜索（公众号文章优先收录，时效性强）。

```
GET https://weixin.sogou.com/weixin?type=2&query=<关键词>
Headers: User-Agent
```

**Node.js 解析**（已验证可用）：
```js
async function sogouSearch(query) {
  const url = 'https://weixin.sogou.com/weixin?type=2&query=' + encodeURIComponent(query);
  const html = await fetch(url, { headers: { 'User-Agent': '...' } });
  const results = [];
  // 标题
  const titleRegex = /<h3[^>]*>[\s\S]*?<a[^>]*>([\s\S]*?)<\/a>/g;
  // 摘要
  const descRegex = /<p[^>]*class="txt-info"[^>]*>([\s\S]*?)<\/p>/g;
  let m;
  while ((m = titleRegex.exec(html)) !== null && results.length < 3) {
    const title = m[1].replace(/<[^>]+>/g, '').trim();
    if (title.length > 5) results.push({ title });
  }
  let idx = 0;
  while ((m = descRegex.exec(html)) !== null && idx < results.length) {
    const desc = m[1].replace(/<[^>]+>/g, '').trim();
    if (results[idx]) results[idx].desc = desc.substring(0, 200);
    idx++;
  }
  return results;
}
```

**备选：新浪新闻 API**（偏财经/时政，娱乐/社会话题覆盖弱）：
```
GET https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=15&page=1
响应：result.data[].title + result.data[].intro
```

### 调研流程（已验证）

1. 用上方热榜 API 并行抓取 4 个平台（抖音/微博/头条/百度）
2. 汇总去重，按热度排序
3. 用户选定话题后，逐个用搜狗微信搜索查详情
4. 搜狗无结果时，可尝试关键词变体（如"周冬雨 话剧 台词"→"周冬雨 话剧 2026"）
5. 极新的话题（当天刚出）可能所有搜索引擎都还没收录，如实告知用户

### 已知失败的方案（不要重试）

| 方案 | 失败原因 |
|------|----------|
| Baidu search via curl | 返回HTML但正则提取不到可用snippet |
| Bing search via curl | 同上，解析不出结果 |
| Toutiao search API | data字段返回空数组 |
| delegate_task 子agent搜索 | mimo-v2.5 provider报401 API key错误 |

---

## 使用建议

1. **默认用 Node.js 解析**（Windows 上 Python 有 SRE module mismatch，不要用 Python）
2. **不需要 OpenCLI**：热搜 API 和搜狗搜索都是公开的，无需登录态
3. **需要登录态的场景**：知乎热榜、小红书搜索 → 用 OpenCLI 复用 Chrome 登录态
4. **并行抓取**：多个平台可同时 curl，最后汇总
5. **anysearch CLI 额度有限**：免费额度用完后会报 `user_daily_quota_exhausted`，回退到直接 API 调用

---

## 更新记录

- **2026-06-18**：新增搜狗微信搜索调研流程、已知失败方案、anysearch额度提醒。实测4平台热搜+搜狗深度调研完整链路。
- **2026-06-17**：首次添加，实测通过 4 个平台（抖音/微博/百度/头条）。知乎需登录态。
