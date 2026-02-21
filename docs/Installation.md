# TermCap 安装指南

*本指南基于实际安装测试编写*

## 系统要求

### Python 版本
- **Python 3.5 或更高版本**（推荐 3.8+）
- 支持的 Python 版本：3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12+

### 支持的操作系统
- Linux（推荐）
- macOS
- Windows（有限支持）

### 依赖库
TermCap 会自动安装以下依赖：

```
lxml      # XML/HTML 解析和处理
pyte      # 终端模拟器库
wcwidth   # Unicode 字符宽度计算
click     # 现代化 CLI 框架
platformdirs  # 跨平台目录管理
toml      # TOML 配置文件解析
```

## 安装方法

### 方法一：从 PyPI 安装（推荐）

```bash
# 基础安装
pip install termcap

# 验证安装
termcap --version
```

**实际安装日志示例：**
```
Using Python 3.12.5 environment at: /tmp/.venv
Resolving dependencies...
Prepared 4 packages in 524ms
Installing wheels...
 + pyte==0.8.2
 + termcap==0.1.1
 + toml==0.10.2
 + wcwidth==0.2.13
Installed 4 packages in 2ms
```

### 方法二：从源码安装（开发版）

```bash
# 克隆仓库
git clone https://github.com/RexWzh/TermCap.git
cd TermCap

# 可编辑安装（开发模式）
pip install -e .

# 或者标准安装
pip install .

# 验证安装
termcap --version
```

**预期输出：**
```
termcap 0.1.1
```

### 方法三：开发环境安装

如果你计划贡献代码或进行开发：

```bash
# 克隆仓库
git clone https://github.com/RexWzh/TermCap.git
cd TermCap

# 安装开发依赖
pip install -e .[dev]

# 运行测试
python -m pytest termcap/tests/
```

## 安装验证

### 1. 检查版本

```bash
termcap --version
```

应该显示：`termcap 0.1.1`

### 2. 查看帮助信息

```bash
termcap --help
```

**预期输出：**
```
Usage: termcap [OPTIONS] COMMAND [ARGS]...

  Terminal capture tool - Record terminal sessions as SVG animations

Options:
  --version  Show version and exit
  --help     Show this message and exit.

Commands:
  config    Configuration management commands
  record    Record a terminal session to a cast file
  render    Render a cast file to SVG animation
  template  Template management commands
```

### 3. 检查配置

```bash
termcap config show
```

**预期输出：**
```
Configuration file: /home/username/.config/termcap/config.toml
Templates directory: /home/username/.config/termcap/templates

Current configuration:

[general]
  default_template = gjm8
  default_geometry = 82x19
  default_min_duration = 17
  default_max_duration = 3000
  default_loop_delay = 1000

[templates]
  custom_templates_enabled = True
  builtin_templates_enabled = True

[output]
  default_output_dir = ~/termcap_recordings
  auto_timestamp = True
```

### 4. 检查可用模板

```bash
termcap template list
```

**预期输出：**
```
Available templates:
  base16_default_dark (builtin)
  dracula (builtin)
  gjm8_play (builtin)
  gjm8_single_loop (builtin)
  gjm8 (builtin)
  powershell (builtin)
  progress_bar (builtin)
  putty (builtin)
  solarized_dark (builtin)
  solarized_light (builtin)
  terminal_app (builtin)
  ubuntu (builtin)
  window_frame_js (builtin)
  window_frame_powershell (builtin)
  window_frame (builtin)
  xterm (builtin)
```

## 配置文件位置

TermCap 使用 `platformdirs` 管理配置目录：

### Linux
```
配置文件: ~/.config/termcap/config.toml
模板目录: ~/.config/termcap/templates/
```

### macOS
```
配置文件: ~/Library/Application Support/termcap/config.toml
模板目录: ~/Library/Application Support/termcap/templates/
```

### Windows
```
配置文件: %APPDATA%\termcap\config.toml
模板目录: %APPDATA%\termcap\templates\
```

## 故障排除

### 常见问题

#### 1. Python 版本不兼容

**错误：** `Requires-Python >=3.5`

**解决方案：**
```bash
# 检查 Python 版本
python --version

# 如果版本过低，安装新版本 Python
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8

# macOS
brew install python@3.8
```

#### 2. 缺少依赖库

**错误：** 缺少 `lxml` 或其他依赖

**解决方案：**
```bash
# 安装系统级依赖（Ubuntu/Debian）
sudo apt install libxml2-dev libxslt1-dev

# 重新安装
pip install --upgrade termcap
```

#### 3. 权限问题

**错误：** `Permission denied`

**解决方案：**
```bash
# 使用用户安装
pip install --user termcap

# 或者使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install termcap
```

#### 4. 配置目录权限

如果遇到配置文件创建权限问题：

```bash
# Linux/macOS
sudo chown -R $USER ~/.config/termcap/

# 或者手动创建
mkdir -p ~/.config/termcap/templates/
```

### 验证安装完整性

运行完整的安装验证脚本：

```bash
#!/bin/bash
echo "=== TermCap 安装验证 ==="
echo

echo "1. 检查版本..."
termcap --version
echo

echo "2. 检查命令可用性..."
if termcap --help > /dev/null 2>&1; then
    echo "✓ 主命令正常"
else
    echo "✗ 主命令失败"
fi

echo "3. 检查子命令..."
for cmd in record render config template; do
    if termcap $cmd --help > /dev/null 2>&1; then
        echo "✓ $cmd 命令正常"
    else
        echo "✗ $cmd 命令失败"
    fi
done

echo
echo "4. 检查配置..."
termcap config show

echo
echo "5. 检查模板..."
termcap template list | head -5

echo
echo "=== 验证完成 ==="
```

## 升级和卸载

### 升级 TermCap

```bash
# 升级到最新版本
pip install --upgrade termcap

# 检查新版本
termcap --version
```

### 卸载 TermCap

```bash
# 卸载软件包
pip uninstall termcap

# 清理配置文件（可选）
# Linux
rm -rf ~/.config/termcap/

# macOS
rm -rf "~/Library/Application Support/termcap/"

# Windows
# 手动删除 %APPDATA%\termcap 文件夹
```

安装完成后，请继续阅读 [快速入门指南](QuickStart.md) 开始使用 TermCap。
