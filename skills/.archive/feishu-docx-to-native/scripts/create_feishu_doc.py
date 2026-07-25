#!/usr/bin/env python3
"""
Markdown → 飞书原生文档转换器（Apple风格）
- callout块作为容器，内容嵌套在里面
- 课件内容 → 浅蓝色callout + 📌
- 讲师解读 → 浅橙色callout + 💬

用法：python3 create_feishu_doc.py [markdown文件路径]
"""
import json, urllib.request, re, time, sys

# === 配置 ===
TOKEN_FILE = '/Users/guanmian/.hermes/profiles/main/feishu_user_token.json'
FOLDER_TOKEN = 'G3sFfLWiYlb7Z5dGUAbcNVotnqc'

# === Token管理 ===
def get_token():
    with open(TOKEN_FILE) as f:
        return json.load(f)['access_token']

def refresh_token():
    with open(TOKEN_FILE) as f:
        data = json.load(f)
    with open('/tmp/feishu_app_secret.txt') as f:
        app_secret = f.read().strip()
    body = json.dumps({
        "grant_type": "refresh_token",
        "refresh_token": data['refresh_token'],
        "app_id": "cli_aa933b5e9ef85cd2",
        "app_secret": app_secret
    }).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/authen/v1/oidc/refresh_access_token",
        data=body,
        headers={'Content-Type': 'application/json'}
    )
    resp = json.loads(urllib.request.urlopen(req).read())
    if resp.get('code') == 0:
        new_data = resp['data']
        with open(TOKEN_FILE, 'w') as f:
            json.dump(new_data, f, indent=2)
        print("✅ Token已刷新")
        return new_data['access_token']
    else:
        print(f"❌ 刷新失败: {resp}")
        return data['access_token']

def api_call(method, url, body=None, retries=2):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        if result.get('code') == 0:
            return result
        print(f"API错误: {result.get('msg', result)}")
        return result
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        if err.get('code') == 99991668 and retries > 0:
            print("Token过期，刷新中...")
            new_token = refresh_token()
            headers['Authorization'] = f'Bearer {new_token}'
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            resp = urllib.request.urlopen(req)
            return json.loads(resp.read())
        print(f"HTTP错误: {err}")
        return err

def create_blocks(doc_id, blocks, index=-1):
    """批量创建blocks"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
    body = {"children": blocks}
    if index >= 0:
        body["index"] = index
    return api_call('POST', url, body)

def create_child_block(doc_id, parent_id, blocks):
    """在指定parent block下创建子block"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children"
    body = {"children": blocks}
    return api_call('POST', url, body)

# === Markdown解析 ===
def parse_md(md_text):
    """解析markdown为结构化blocks"""
    blocks = []
    lines = md_text.split('\n')
    i = 0
    
    # 表格状态
    in_table = False
    table_rows = []
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        # 跳过空行
        if not line:
            if in_table and table_rows:
                blocks.append(('table', table_rows))
                table_rows = []
                in_table = False
            i += 1
            continue
        
        # 表格行
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            # 跳过分隔行
            if all(re.match(r'^[-:]+$', c) for c in cells):
                i += 1
                continue
            in_table = True
            table_rows.append(cells)
            i += 1
            continue
        
        # 表格结束
        if in_table and table_rows:
            blocks.append(('table', table_rows))
            table_rows = []
            in_table = False
        
        # Callout标记（优先于普通标题检测）
        if line.startswith('### 📋 课件内容') or line.startswith('📋 **课件内容**'):
            content_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i].rstrip()
                if next_line.startswith('### 🎙️') or next_line.startswith('🎙️') or next_line.startswith('#') or next_line.startswith('### 📋'):
                    break
                if next_line:
                    content_lines.append(next_line)
                i += 1
            blocks.append(('callout_blue', '\n'.join(content_lines)))
            continue
        
        if line.startswith('### 🎙️ 讲师解读') or line.startswith('🎙️ **讲师解读**'):
            content_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i].rstrip()
                if next_line.startswith('### 📋') or next_line.startswith('📋') or next_line.startswith('#') or next_line.startswith('### 🎙️'):
                    break
                if next_line:
                    content_lines.append(next_line)
                i += 1
            blocks.append(('callout_orange', '\n'.join(content_lines)))
            continue
        
        # 标题
        if line.startswith('#'):
            m = re.match(r'^(#{1,6})\s+(.*)', line)
            if m:
                level = len(m.group(1))
                text = m.group(2).strip()
                blocks.append(('heading', level, text))
                i += 1
                continue
        
        # 普通段落
        # 收集连续的非空行作为一个段落
        para_lines = []
        while i < len(lines):
            l = lines[i].rstrip()
            if not l or l.startswith('#') or l.startswith('|') or l.startswith('📋') or l.startswith('🎙️'):
                break
            para_lines.append(l)
            i += 1
        if para_lines:
            blocks.append(('paragraph', '\n'.join(para_lines)))
    
    # 处理末尾表格
    if in_table and table_rows:
        blocks.append(('table', table_rows))
    
    return blocks

def make_text_elements(text):
    """将文本转换为飞书text元素，处理粗体"""
    elements = []
    # 分割粗体
    parts = re.split(r'(\*\*.*?\*\*)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            elements.append({
                "text_run": {
                    "content": part[2:-2],
                    "text_element_style": {"bold": True}
                }
            })
        else:
            elements.append({
                "text_run": {
                    "content": part,
                    "text_element_style": {}
                }
            })
    return elements

def md_to_blocks(content, style='blue'):
    """将内容转换为飞书block列表"""
    blocks = []
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 子标题
        if line.startswith('### '):
            blocks.append({
                "block_type": 5,
                "heading3": {"elements": make_text_elements(line[4:])}
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 4,
                "heading2": {"elements": make_text_elements(line[3:])}
            })
        elif line.startswith('# '):
            blocks.append({
                "block_type": 3,
                "heading1": {"elements": make_text_elements(line[2:])}
            })
        else:
            blocks.append({
                "block_type": 2,
                "text": {"elements": make_text_elements(line)}
            })
    return blocks

def build_doc(md_text):
    """主构建函数"""
    parsed = parse_md(md_text)
    
    # 创建文档
    result = api_call('POST', 'https://open.feishu.cn/open-apis/docx/v1/documents', {
        "folder_token": FOLDER_TOKEN,
        "title": "拾易八字·第二期第一课·完整笔记"
    })
    if result.get('code') != 0:
        print(f"❌ 创建文档失败: {result}")
        return None
    doc_id = result['data']['document']['document_id']
    print(f"✅ 文档已创建: {doc_id}")
    
    # 逐个处理parsed blocks
    total = len(parsed)
    for idx, (block_type, *args) in enumerate(parsed):
        print(f"[{idx+1}/{total}] {block_type}...", end=' ')
        
        if block_type == 'heading':
            level, text = args
            block_type_map = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8}
            heading_key = {1: 'heading1', 2: 'heading2', 3: 'heading3',
                          4: 'heading4', 5: 'heading5', 6: 'heading6'}
            bt = block_type_map.get(level, 4)
            hk = heading_key.get(level, 'heading2')
            result = create_blocks(doc_id, [{
                "block_type": bt,
                hk: {"elements": make_text_elements(text)}
            }])
            print("✓" if result.get('code') == 0 else "✗")
        
        elif block_type == 'paragraph':
            content = args[0]
            # 多行段落拆成多个text blocks
            para_blocks = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    para_blocks.append({
                        "block_type": 2,
                        "text": {"elements": make_text_elements(line)}
                    })
            if para_blocks:
                result = create_blocks(doc_id, para_blocks)
                print("✓" if result.get('code') == 0 else "✗")
            else:
                print("跳过空段落")
        
        elif block_type in ('callout_blue', 'callout_orange'):
            content = args[0]
            if not content.strip():
                print("跳过空callout")
                continue
            
            color = 'blue' if block_type == 'callout_blue' else 'orange'
            emoji = 'pushpin' if color == 'blue' else 'speech_balloon'
            bg = 3 if color == 'blue' else 5  # 浅蓝=3, 浅橙=5
            border = 3 if color == 'blue' else 5
            
            # 创建callout容器
            result = create_blocks(doc_id, [{
                "block_type": 19,
                "callout": {
                    "background_color": bg,
                    "border_color": border,
                    "emoji_id": emoji
                }
            }])
            if result.get('code') != 0:
                print("✗ callout创建失败")
                continue
            
            callout_id = result['data']['children'][0]['block_id']
            
            # 往callout里添加内容
            child_blocks = md_to_blocks(content, color)
            if child_blocks:
                result = create_child_block(doc_id, callout_id, child_blocks)
                print("✓" if result.get('code') == 0 else "✗")
            else:
                print("✓ (空)")
        
        elif block_type == 'table':
            rows = args[0]
            # 表格用纯文本展示
            table_text = []
            for row in rows:
                table_text.append(' | '.join(row))
            result = create_blocks(doc_id, [{
                "block_type": 2,
                "text": {"elements": make_text_elements('\n'.join(table_text))}
            }])
            print("✓" if result.get('code') == 0 else "✗")
        
        time.sleep(0.3)  # 避免限流
    
    return doc_id

# === 主程序 ===
if __name__ == '__main__':
    md_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/guanmian/Pictures/八字课/第一课/2期第一课_完整笔记.md'
    with open(md_path) as f:
        md_text = f.read()
    
    doc_id = build_doc(md_text)
    if doc_id:
        print(f"\n🎉 完成！文档链接：https://tcnin8cetmo5.feishu.cn/docx/{doc_id}")
