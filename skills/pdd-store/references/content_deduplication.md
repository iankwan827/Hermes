# 内容去重与对比方法

> 适用场景：对比两版本文档（如上课截图版 vs 老师整理版），找出独有内容

## 常见错误

❌ 只按文件名判断重复
❌ 只看文件总行数判断内容多少
❌ 用 SequenceMatcher 比较整个文件（噪声太大）

## 正确方法：关键词频率对比

```python
import os

v2_dir = 'v2/docs'
v3_dir = 'v3/docs'

# 读取v2所有内容
v2_all = ""
for f in os.listdir(v2_dir):
    if f.endswith('.md'):
        with open(f'{v2_dir}/{f}', 'r', encoding='utf-8', errors='ignore') as fh:
            v2_all += fh.read() + "\n"

# 定义要追踪的关键词
keywords = ['性爱', '阴茎', '尺寸', '流产', '剖腹产', '子宫', '恋爱脑', ...]

# 统计v3每个文件的独有内容
for v3_file in sorted(os.listdir(v3_dir)):
    if not v3_file.endswith('.md'):
        continue
    with open(f'{v3_dir}/{v3_file}', 'r', encoding='utf-8', errors='ignore') as fh:
        v3_content = fh.read()
    
    unique_count = 0
    for kw in keywords:
        v3_count = v3_content.count(kw)
        v2_count = v2_all.count(kw)
        if v3_count > v2_count:
            unique_count += (v3_count - v2_count)
    
    if unique_count > 0:
        print(f'{v3_file}: {unique_count}次独有')
```

## 关键认知

1. **截图版（v3）往往比整理版（v2）内容更多**
   - v3 = 上课时截的图，包含老师后来删掉的内容
   - v2 = 老师整理后发的长图，已经删减过

2. **敏感内容在v3中有，v2中没有**
   - 性爱/尺寸判断/流产/剖腹产等内容被老师删除
   - 但用户截图保留了这些内容

3. **哈希文件名的文件需要内容分析**
   - 不能只看文件名判断类型
   - 需要读取内容判断是图片提取/课程/其他

4. **独有内容按关键词频率排序**
   - 不是按文件大小排序
   - 关键词出现次数越多，独有内容越多

## 应用场景

- 对比课程笔记的不同版本
- 找出老师删除的内容
- 合并多个来源的知识点
- 去重后整理完整知识库
