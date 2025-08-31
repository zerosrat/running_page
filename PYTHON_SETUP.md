# Python 环境设置说明

## 问题描述

由于 macOS 系统的安全限制，系统 Python 不允许直接安装包，会出现以下错误：

```
This environment is externally managed
```

## 解决方案：使用虚拟环境

### 1. 激活虚拟环境

```bash
# 对于 fish shell（推荐）
source venv/bin/activate.fish

# 对于 bash/zsh
source venv/bin/activate
```

### 2. 验证环境

激活后，命令行前面会显示 `(venv)`，表示虚拟环境已激活。

### 3. 使用 Python 脚本

现在可以正常运行 Python 脚本了：

```bash
# 同步 Garmin 数据
python run_page/garmin_sync.py

# 生成 SVG 图表
python run_page/gen_svg.py --from-db --type github --output assets/github.svg
```

### 4. 退出虚拟环境

```bash
deactivate
```

## 常用命令

- 安装依赖：`pip install -r requirements.txt`
- 更新依赖：`pip install --upgrade -r requirements.txt`
- 添加新依赖：`pip install package_name`

## 注意事项

- 每次使用 Python 脚本前都需要先激活虚拟环境
- 虚拟环境文件夹 `venv/` 已经添加到 `.gitignore`
