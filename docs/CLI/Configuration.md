# TermCap 配置管理

*基于实际配置测试的完整指南*

## 概览

TermCap 使用 TOML 格式的配置文件，通过 `platformdirs` 库管理跨平台的配置目录。所有配置都可以通过命令行进行管理。

## 配置文件位置

### 按操作系统分类

| 操作系统 | 配置文件路径 | 模板目录 |
|------------|-------------------|----------|
| **Linux** | `~/.config/termcap/config.toml` | `~/.config/termcap/templates/` |
| **macOS** | `~/Library/Application Support/termcap/config.toml` | `~/Library/Application Support/termcap/templates/` |
| **Windows** | `%APPDATA%\\termcap\\config.toml` | `%APPDATA%\\termcap\\templates\\` |

### 查看实际路径

```bash
# 查看当前系统的配置路径
termcap config show
```

**实际输出示例（Linux）：**
```
Configuration file: /home/username/.config/termcap/config.toml
Templates directory: /home/username/.config/termcap/templates
```

## 配置结构

### 默认配置文件

```toml
[general]
default_template = "gjm8"
default_geometry = "82x19"
default_min_duration = 17
default_max_duration = 3000
default_loop_delay = 1000

[templates]
custom_templates_enabled = true
builtin_templates_enabled = true

[output]
default_output_dir = "~/termcap_recordings"
auto_timestamp = true
```

### 配置项详解

#### [general] 一般设置

| 配置项 | 类型 | 默认值 | 描述 | 示例值 |
|---------|------|--------|------|--------|
| `default_template` | string | "gjm8" | 默认使用的 SVG 模板 | "dracula", "ubuntu" |
| `default_geometry` | string | "82x19" | 默认终端尺寸 (宽度x高度) | "120x40", "80x24" |
| `default_min_duration` | integer | 17 | 最小帧持续时间 (毫秒) | 10, 25, 50 |
| `default_max_duration` | integer | 3000 | 最大帧持续时间 (毫秒) | 2000, 5000 |
| `default_loop_delay` | integer | 1000 | 动画循环延迟 (毫秒) | 500, 2000, 3000 |

#### [templates] 模板设置

| 配置项 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| `custom_templates_enabled` | boolean | true | 是否启用自定义模板 |
| `builtin_templates_enabled` | boolean | true | 是否启用内置模板 |

#### [output] 输出设置

| 配置项 | 类型 | 默认值 | 描述 |
|---------|------|--------|------|
| `default_output_dir` | string | "~/termcap_recordings" | 默认输出目录 |
| `auto_timestamp` | boolean | true | 是否自动添加时间戳 |

## 命令行配置管理

### 查看配置

#### 显示全部配置
```bash
termcap config show
```

**实际输出示例：**
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

#### 获取单个配置项
```bash
# 语法
termcap config get SECTION KEY

# 示例
termcap config get general default_template
termcap config get general default_geometry
termcap config get templates custom_templates_enabled
termcap config get output default_output_dir
```

**示例输出：**
```bash
$ termcap config get general default_template
gjm8

$ termcap config get general default_geometry
82x19
```

### 修改配置

#### 设置配置项
```bash
# 语法
termcap config set SECTION KEY VALUE

# 修改默认模板
termcap config set general default_template dracula

# 修改终端尺寸
termcap config set general default_geometry 120x40

# 修改时间参数
termcap config set general default_min_duration 25
termcap config set general default_max_duration 2000
termcap config set general default_loop_delay 2000

# 修改输出设置
termcap config set output default_output_dir "~/my_recordings"
termcap config set output auto_timestamp false

# 修改模板设置
termcap config set templates custom_templates_enabled false
```

#### 验证修改
```bash
# 验证单个设置
termcap config get general default_template

# 或查看全部配置
termcap config show
```

### 重置配置

```bash
# 重置所有配置为默认值
termcap config reset

# 确认重置成功
termcap config show
```

**注意：** 重置操作会删除所有自定义设置，请谨慎使用。

## 实用配置场景

### 场景 1：演示环境

适用于会议演示或教学场合：

```bash
# 设置大屏幕尺寸
termcap config set general default_geometry 120x40

# 选择明显的模板
termcap config set general default_template window_frame

# 设置较长的循环延迟（给观众时间观看）
termcap config set general default_loop_delay 3000

# 设置适中的帧持续时间
termcap config set general default_min_duration 50
termcap config set general default_max_duration 2000
```

### 场景 2：快速开发调试

适用于快速录制和测试：

```bash
# 使用紧凑尺寸
termcap config set general default_geometry 80x24

# 选择简洁模板
termcap config set general default_template gjm8

# 设置快速播放
termcap config set general default_min_duration 10
termcap config set general default_max_duration 1000
termcap config set general default_loop_delay 500
```

### 场景 3：高质量输出

适用于正式文档或公开分享：

```bash
# 使用精美模板
termcap config set general default_template dracula

# 设置合适尺寸
termcap config set general default_geometry 100x30

# 优化动画参数
termcap config set general default_min_duration 25
termcap config set general default_max_duration 3000
termcap config set general default_loop_delay 2000
```

## 配置文件手动编辑

如果喜欢手动编辑，可以直接修改 TOML 文件：

### 1. 找到配置文件
```bash
# 查看配置文件路径
termcap config show | head -1
```

### 2. 编辑配置文件
```bash
# Linux/macOS
nano ~/.config/termcap/config.toml
# 或
vim ~/.config/termcap/config.toml

# Windows
notepad %APPDATA%\\termcap\\config.toml
```

### 3. 验证修改
```bash
# 检查配置是否正确加载
termcap config show
```

### 示例自定义配置

```toml
# 自定义演示配置
[general]
default_template = "window_frame"
default_geometry = "120x40"
default_min_duration = 50
default_max_duration = 2000
default_loop_delay = 3000

[templates]
custom_templates_enabled = true
builtin_templates_enabled = true

[output]
default_output_dir = "~/demo_recordings"
auto_timestamp = true

# 新增自定义选项（实验性）
[experimental]
enable_fast_mode = false
verbose_output = true
```

## 配置的优先级

配置的优先级从高到低：

1. **命令行参数** - 直接在命令中指定的参数
2. **配置文件** - `config.toml` 中的设置
3. **默认值** - 程序内置的默认值

### 示例：优先级演示

```bash
# 配置文件中设置
termcap config set general default_template dracula
termcap config set general default_geometry 100x30

# 命令行参数会覆盖配置文件的设置
termcap record demo.cast -g 120x40  # 使用 120x40，不是 100x30
termcap render demo.cast demo.svg -t ubuntu  # 使用 ubuntu，不是 dracula
```

## 故障排除

### 常见问题

#### 1. 配置文件不存在
**现象：** 第一次运行时找不到配置文件
**解决：** 程序会自动创建默认配置文件

```bash
# 手动创建配置目录
mkdir -p ~/.config/termcap/

# 运行任意 config 命令来初始化
termcap config show
```

#### 2. 配置文件损坏
**现象：** TOML 解析错误
**解决：** 重置配置

```bash
# 备份现有配置
cp ~/.config/termcap/config.toml ~/.config/termcap/config.toml.backup

# 重置为默认配置
termcap config reset
```

#### 3. 权限问题
**现象：** 无法写入配置文件
**解决：** 检查目录权限

```bash
# Linux/macOS
sudo chown -R $USER ~/.config/termcap/
chmod -R 755 ~/.config/termcap/
```

#### 4. 无效的配置值
**现象：** 设置不生效或报错
**解决：** 检查配置值格式

```bash
# 检查当前配置
termcap config show

# 重新设置正确值
termcap config set general default_geometry "80x24"  # 注意引号
termcap config set general default_min_duration 17  # 数值不需引号
termcap config set templates custom_templates_enabled true  # 布尔值
```

### 调试命令

```bash
# 检查配置文件路径和内容
termcap config show

# 检查特定配置项
termcap config get general default_template

# 检查文件权限
ls -la ~/.config/termcap/

# 查看配置文件原始内容
cat ~/.config/termcap/config.toml
```

## 最佳实践

### 1. 备份重要配置
```bash
# 备份配置文件
cp ~/.config/termcap/config.toml ~/.config/termcap/config.backup.toml

# 或者定期备份
cp ~/.config/termcap/config.toml ~/backup/termcap-config-$(date +%Y%m%d).toml
```

### 2. 使用版本控制
```bash
# 将配置文件加入 Git 版本控制
cp ~/.config/termcap/config.toml ~/dotfiles/termcap-config.toml
cd ~/dotfiles
git add termcap-config.toml
git commit -m "Add TermCap configuration"
```

### 3. 环境相关配置
```bash
# 创建不同环境的配置脚本

# work-setup.sh
#!/bin/bash
termcap config set general default_template "gjm8"
termcap config set general default_geometry "80x24"
termcap config set general default_loop_delay 1000

# demo-setup.sh
#!/bin/bash
termcap config set general default_template "window_frame"
termcap config set general default_geometry "120x40"
termcap config set general default_loop_delay 3000
```

### 4. 验证配置

在重要工作之前，始终验证配置：

```bash
# 快速验证脚本
#!/bin/bash
echo "=== TermCap 配置验证 ==="
echo "Default template: $(termcap config get general default_template)"
echo "Default geometry: $(termcap config get general default_geometry)"
echo "Templates enabled: $(termcap config get templates builtin_templates_enabled)"
echo "Configuration file: $(termcap config show | head -1)"
echo "=== 验证完成 ==="
```

这个配置管理文档将帮助你充分利用 TermCap 的灵活配置系统，根据不同需求进行个性化设置。
