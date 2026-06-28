# boss-agent-cli 使用记录

> 安装时间：2026年6月28日
> 版本：1.14.0
> 来源：https://github.com/can4hou6joeng4/boss-agent-cli

## 安装过程

遇到了Python环境冲突问题（PYTHONHOME指向坏掉的Python 3.11），解决方案：

```bash
# 创建独立venv
cd D:/hermes-agent
uv venv .venv-boss --python 3.12
uv pip install --system boss-agent-cli  # 装到系统Python 3.10
# 实际装到了 E:/Python/Scripts/boss.exe

# 使用时必须清除PYTHONHOME
PYTHONHOME="" .venv-boss/Scripts/boss.exe --help
```

## 已验证的功能

```bash
# 登录（需要Chrome打开Boss直聘并登录）
PYTHONHOME="" .venv-boss/Scripts/boss.exe login --cookie-source chrome

# 搜索岗位
PYTHONHOME="" .venv-boss/Scripts/boss.exe search "国学 命理"

# 查看岗位详情
PYTHONHOME="" .venv-boss/Scripts/boss.exe show 5

# 检查登录状态
PYTHONHOME="" .venv-boss/Scripts/boss.exe status
```

## 注意事项

- 每次搜索间隔5-8秒，模拟人操作
- 搜索频率过高会触发风控（BOSS直聘返回 code 36）
- 风控后需要等待一段时间才能恢复
- 公司地址需要用OpenCLI打开网页搜索（Boss CLI不返回详细地址）
