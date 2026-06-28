---
name: boss-job-search
description: "Boss直聘求职搜索。用boss-agent-cli工具搜索岗位、查看详情、保存结果。"
triggers:
  - "找工作"
  - "搜岗位"
  - "Boss直聘"
  - "求职"
  - "应聘"
---

# Boss直聘求职搜索 Skill

## 工具

使用 `boss-agent-cli`（Python包）搜索Boss直聘岗位。

### 安装

```bash
# 在独立venv中安装（避免Python环境冲突）
uv venv D:/hermes-agent/.venv-boss --python 3.12
uv pip install --python D:/hermes-agent/.venv-boss/Scripts/python.exe boss-agent-cli
```

### 登录

```bash
# 需要Chrome已登录Boss直聘
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe login --cookie-source chrome
```

### 检查登录状态

```bash
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe status
```

## 搜索岗位

```bash
# 基础搜索
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe search "关键词"

# 带筛选条件
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe search "关键词" --city "北京" --salary "10-20K" --experience "1-3年"
```

## 查看岗位详情

```bash
# 用编号查看（搜索结果中的索引）
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe show <编号>

# 用security_id查看
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe detail "<security_id>"
```

## ⚠️ 关键发现

### 搜索结果解析

搜索结果返回JSON，关键字段：
- `title`: 职位名称
- `company`: 公司名称
- `salary`: 薪资
- `city` + `district`: 城市+区域
- `boss_name` + `boss_title`: HR姓名和职位
- `boss_active`: HR活跃状态
- `security_id`: 用于查看详情的ID

### 公司地址获取

Boss直聘搜索结果只有城市+区域，没有详细地址。需要用OpenCLI搜公司名获取详细地址：

```bash
opencli browser douyin open "https://www.toutiao.com/search?keyword=公司名+地址"
sleep 6
opencli browser douyin eval "document.body.innerText"
```

从搜索结果中提取：
- BOSS直聘公司页面显示的地址
- 工商信息中的注册地址

### ⚠️ 操作节奏

**用户明确要求慢一点，模拟人操作：**
- 每次搜索间隔5秒以上
- 不要连续快速请求
- 查看详情后等几秒再操作下一个

### Python环境问题

`boss.exe`依赖的Python 3.11环境可能损坏（SRE module mismatch）。解决方法：
1. 使用独立venv（`.venv-boss`）
2. 运行前加 `unset PYTHONHOME`
3. 如果还不行，用 `env -i PATH="$PATH" HOME="$HOME"` 清除环境变量

## 保存结果

搜索结果可保存为Markdown文件：

```bash
# 用 node 解析JSON并格式化
unset PYTHONHOME && D:/hermes-agent/.venv-boss/Scripts/boss.exe search "关键词" 2>/dev/null | node -e "
let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{
  const j=JSON.parse(d);
  const items=j.data||[];
  items.forEach((item,i)=>{
    console.log((i+1)+'. '+item.title);
    console.log('   公司: '+item.company);
    console.log('   薪资: '+item.salary+' | 城市: '+item.city+' '+item.district);
    console.log('   HR: '+item.boss_name+' ('+item.boss_title+') '+item.boss_active);
    console.log('');
  });
})"
```

## 完整工作流

1. 检查登录状态：`boss.exe status`
2. 搜索岗位：`boss.exe search "关键词"`
3. 查看详情：`boss.exe show <编号>`
4. 用OpenCLI获取公司详细地址
5. 保存结果到Markdown文件

## 文档

- GitHub: https://github.com/can4hou6joeng4/boss-agent-cli
- API文档: https://api.tikhub.io/openapi.json
