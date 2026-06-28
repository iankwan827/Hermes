# boss-agent-cli 使用指南

> 安装时间：2026-06-28
> 版本：v1.14.0
> 来源：https://github.com/can4hou6joeng4/boss-agent-cli

## 安装

```bash
# 必须用干净的Python环境，不能用系统Python（PYTHONHOME指向坏掉的3.11）
cd /d/hermes-agent
uv venv .venv-boss --python 3.12
.venv-boss/Scripts/activate
uv pip install boss-agent-cli
```

## 使用

```bash
# ⚠️ 必须设置 PYTHONHOME="" 防止加载坏掉的Python 3.11库
cd /d/hermes-agent && PYTHONHOME="" .venv-boss/Scripts/boss.exe <command>
```

## 常用命令

```bash
# 检查登录状态（用daemon status代替doctor，doctor经常超时）
PYTHONHOME="" .venv-boss/Scripts/boss.exe status

# 搜索岗位
PYTHONHOME="" .venv-boss/Scripts/boss.exe search "关键词"
PYTHONHOME="" .venv-boss/Scripts/boss.exe search "关键词" --city "北京" --salary "10-20K"

# 查看岗位详情
PYTHONHOME="" .venv-boss/Scripts/boss.exe detail <security_id>
PYTHONHOME="" .venv-boss/Scripts/boss.exe show <index>  # 按搜索结果序号查看

# 登录
PYTHONHOME="" .venv-boss/Scripts/boss.exe login --cookie-source chrome
```

## 注意事项

1. **PYTHONHOME必须清空**：系统PYTHONHOME指向坏掉的Python 3.11，不清空会报SRE module mismatch
2. **搜索频率控制**：Boss直聘有反爬风控，连续搜索会被拦截（code 36）。搜索间隔至少5秒
3. **搜索结果用node解析**：JSON输出用 `| node -e "..."` 解析比Python更可靠
4. **security_id是动态的**：每次搜索返回的security_id不同，不能缓存
5. **show命令用索引**：搜索结果按顺序编号，用 `show <index>` 查看详情

## 搜索参数

```bash
# 基础搜索
boss search "国学 命理"

# 带筛选条件
boss search "命理" --city "北京" --salary "10-20K" --experience "1-3年"

# 查看搜索结果详情
boss show 3  # 查看第3条结果
```

## 工作流程

1. `boss status` 确认登录状态
2. `boss search "关键词"` 搜索岗位
3. `boss show <index>` 查看感兴趣的岗位详情
4. 手动到Boss直聘官网投递/沟通（CLI不支持自动投递）

## 数据输出格式

搜索结果JSON结构：
```json
{
  "ok": true,
  "data": [
    {
      "job_id": "...",
      "title": "岗位名称",
      "company": "公司名称",
      "salary": "10-15K",
      "city": "北京",
      "district": "朝阳区",
      "experience": "1-3年",
      "education": "本科",
      "boss_name": "张女士",
      "boss_title": "HR",
      "boss_active": "在线",
      "security_id": "..."  // 用于detail/show命令
    }
  ],
  "pagination": { "page": 1, "has_more": true, "total": 15 }
}
```
