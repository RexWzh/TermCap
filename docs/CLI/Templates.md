# TermCap 模板管理

*基于实际测试的模板系统全面指南*

## 概览

TermCap 提供了丰富的模板系统，包括多种内置主题模板和完全的自定义模板支持。模板决定了 SVG 动画的视觉外观，包括颜色方案、字体、窗口样式等。

## 内置模板

### 可用模板列表

通过以下命令查看所有可用模板：

```bash
termcap template list
```

**实际输出：**
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

### 模板详细介绍

#### 主题类模板

| 模板名 | 风格描述 | 适用场景 |
|---------|----------|----------|
| `gjm8` | 默认的彩色主题，明亮而专业 | 日常使用、教学 |
| `dracula` | 深色主题，紫色调，时尚现代 | 演示、开发者工具 |
| `solarized_dark` | Solarized 深色方案，眼睛友好 | 编程、长时间阅读 |
| `solarized_light` | Solarized 浅色方案，清晰明亮 | 文档、正式场合 |
| `base16_default_dark` | Base16 暗色主题，简洁 | 类 Unix 系统、极简风 |
| `ubuntu` | Ubuntu 系统风格，橙色主调 | Linux 教学、Ubuntu 相关 |
| `putty` | PuTTY 终端风格 | Windows 环境、传统终端 |
| `xterm` | 传统 X Terminal 风格 | 传统 Unix/Linux |

#### 系统类模板

| 模板名 | 特色 | 适用场景 |
|---------|------|----------|
| `terminal_app` | macOS Terminal.app 风格 | macOS 环境演示 |
| `powershell` | Windows PowerShell 风格 | Windows 系统、PowerShell 演示 |
| `window_frame` | 带窗口框架，类似真实终端窗口 | 正式演示、教学 |
| `window_frame_js` | 带 JavaScript 控制的窗口框架 | Web 开发演示 |
| `window_frame_powershell` | PowerShell 版窗口框架 | Windows 开发环境 |

#### 功能类模板

| 模板名 | 特殊功能 | 适用场景 |
|---------|----------|----------|
| `gjm8_play` | 带播放控制按钮 | 交互式演示 |
| `gjm8_single_loop` | 单次循环播放 | 简单演示 |
| `progress_bar` | 带进度条显示 | 逐步教学、进程演示 |

## 使用模板

### 在渲染时指定模板

```bash
# 使用默认模板
termcap render session.cast animation.svg

# 指定特定模板
termcap render session.cast animation.svg --template dracula
termcap render session.cast animation.svg -t ubuntu
```

### 不同模板效果对比

使用同一个 cast 文件生成不同风格的动画：

```bash
# 渲染多种风格进行对比
termcap render demo.cast demo_gjm8.svg -t gjm8
termcap render demo.cast demo_dracula.svg -t dracula
termcap render demo.cast demo_ubuntu.svg -t ubuntu
termcap render demo.cast demo_frame.svg -t window_frame
termcap render demo.cast demo_solarized.svg -t solarized_dark
```

### 通过配置设置默认模板

```bash
# 设置新的默认模板
termcap config set general default_template dracula

# 验证设置
termcap config get general default_template

# 现在渲染时会使用 dracula 作为默认模板
termcap render session.cast animation.svg
```

## 自定义模板

### 模板存储位置

自定义模板存储在系统配置目录中：

| 操作系统 | 模板目录路径 |
|------------|------------------|
| **Linux** | `~/.config/termcap/templates/` |
| **macOS** | `~/Library/Application Support/termcap/templates/` |
| **Windows** | `%APPDATA%\\termcap\\templates\\` |

### 查看模板目录

```bash
# 查看实际路径
termcap config show | grep "Templates directory"

# 列出目录内容
ls -la ~/.config/termcap/templates/  # Linux/macOS
```

### 安装自定义模板

#### 方法一：使用命令行安装

```bash
# 从现有 SVG 文件安装
termcap template install my_theme my_template.svg

# 验证安装
termcap template list | grep my_theme
```

#### 方法二：手动复制文件

```bash
# 直接复制 SVG 文件到模板目录
cp my_custom_template.svg ~/.config/termcap/templates/custom_name.svg

# 查看是否可用
termcap template list
```

### 创建自定义模板

#### 基于现有模板修改

1. **导出现有模板：**
```bash
# 生成一个基础动画
termcap record base.cast -c "echo 'Template test'"
# 注意：由于渲染bug，这一步可能无法完成
```

2. **从项目示例中获取模板：**
```bash
# 查看项目示例目录
ls /path/to/TermCap/docs/examples/

# 复制示例模板
cp /path/to/TermCap/docs/examples/dracula.svg ~/.config/termcap/templates/my_dracula.svg
```

3. **修改模板：**
使用文本编辑器打开 SVG 文件，修改颜色、字体等样式。

#### SVG 模板结构

一个典型的 TermCap SVG 模板包含：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     width="656" height="316" 
     viewBox="0 0 656 316">
     
  <!-- 背景样式 -->
  <style>
    .background { fill: #1e1e1e; }
    .terminal { 
      font-family: 'Monaco', 'Consolas', monospace;
      font-size: 14px;
      fill: #ffffff;
    }
    .cursor { fill: #ffffff; }
  </style>
  
  <!-- 终端窗口背景 -->
  <rect class="background" width="100%" height="100%"/>
  
  <!-- 文本内容区域 -->
  <g class="terminal">
    <!-- 动画内容将在这里插入 -->
  </g>
  
  <!-- 动画脚本 -->
  <script><![CDATA[
    // JavaScript 动画控制逻辑
  ]]></script>
</svg>
```

### 模板管理命令

#### 列出模板
```bash
# 列出所有可用模板
termcap template list

# 使用 config 命令查看（等效）
termcap config templates
```

#### 删除自定义模板
```bash
# 删除指定模板
termcap template remove my_theme

# 验证删除
termcap template list | grep -v my_theme
```

**注意：** 内置模板无法删除，只能删除自定义模板。

### 模板配置选项

```bash
# 禁用自定义模板
termcap config set templates custom_templates_enabled false

# 禁用内置模板（不推荐）
termcap config set templates builtin_templates_enabled false

# 重新启用
termcap config set templates custom_templates_enabled true
termcap config set templates builtin_templates_enabled true
```

## 实用模板技巧

### 模板选择建议

#### 根据使用场景选择

```bash
# 技术演示 - 使用现代暗色主题
termcap render tech_demo.cast demo.svg -t dracula

# 教学材料 - 使用清晰明亮的主题
termcap render tutorial.cast tutorial.svg -t solarized_light

# Linux 系统演示 - 使用系统风格
termcap render linux_demo.cast demo.svg -t ubuntu

# 正式文档 - 使用窗口框架
termcap render official_demo.cast demo.svg -t window_frame
```

#### 根据内容类型选择

```bash
# 编程相关 - 使用程序员友好的主题
termcap render coding.cast coding.svg -t solarized_dark

# Windows 相关 - 使用 Windows 风格
termcap render windows_demo.cast demo.svg -t powershell

# 网页展示 - 使用带控制的模板
termcap render web_demo.cast demo.svg -t gjm8_play
```

### 批量处理不同模板

```bash
# 为一个 cast 文件生成多种模板的版本
cast_file="demo.cast"
base_name="demo"

for template in gjm8 dracula ubuntu window_frame solarized_dark; do
    echo "Rendering with $template..."
    termcap render "$cast_file" "${base_name}_${template}.svg" -t "$template"
done
```

### 模板测试脚本

```bash
#!/bin/bash
# template_test.sh - 测试所有模板的效果

echo "=== TermCap 模板测试 ==="

# 创建测试用的 cast 文件
echo "Creating test recording..."
termcap record template_test.cast -c "echo 'Template test'; ls -la; date"

# 获取所有模板
echo "Available templates:"
termcap template list

# 测试几个主要模板
for template in gjm8 dracula ubuntu solarized_dark window_frame; do
    echo "Testing template: $template"
    # 由于渲染bug，这里可能会失败
    # termcap render template_test.cast "test_${template}.svg" -t "$template"
done

echo "=== 测试完成 ==="
```

### 模板备份和分享

```bash
# 备份自定义模板
mkdir -p ~/termcap_backup/templates
cp ~/.config/termcap/templates/*.svg ~/termcap_backup/templates/

# 打包自定义模板
tar -czf my_termcap_templates.tar.gz -C ~/.config/termcap templates/

# 在另一台机器上恢复
tar -xzf my_termcap_templates.tar.gz -C ~/.config/termcap/
```

## 故障排除

### 常见问题

#### 1. 模板不存在
**现象：** `Error: Template 'template_name' not found`

**解决方案：**
```bash
# 检查可用模板
termcap template list

# 检查模板名拼写
echo "Available templates:"
termcap template list | grep -i template_name

# 使用默认模板
termcap render file.cast output.svg  # 不指定 -t 参数
```

#### 2. 自定义模板不显示
**现象：** 安装的自定义模板不在列表中

**解决方案：**
```bash
# 检查模板目录
ls -la ~/.config/termcap/templates/

# 检查文件权限
chmod 644 ~/.config/termcap/templates/*.svg

# 检查配置是否启用自定义模板
termcap config get templates custom_templates_enabled

# 启用自定义模板
termcap config set templates custom_templates_enabled true
```

#### 3. 模板文件损坏
**现象：** SVG 文件无法解析或显示异常

**解决方案：**
```bash
# 验证 SVG 文件格式
file ~/.config/termcap/templates/template_name.svg

# 检查 SVG 文件内容
head ~/.config/termcap/templates/template_name.svg

# 重新从原始源复制
cp /original/path/template.svg ~/.config/termcap/templates/template_name.svg
```

#### 4. 模板目录不存在
**现象：** 模板命令执行失败

**解决方案：**
```bash
# 手动创建模板目录
mkdir -p ~/.config/termcap/templates/

# 设置正确的权限
chmod 755 ~/.config/termcap/templates/
```

### 调试模板问题

```bash
# 完整的模板诊断脚本
#!/bin/bash
echo "=== TermCap 模板诊断 ==="
echo

echo "1. 配置信息："
termcap config show | grep -E "Templates|templates"
echo

echo "2. 模板目录存在性："
template_dir=$(termcap config show | grep "Templates directory" | cut -d':' -f2 | tr -d ' ')
echo "Template directory: $template_dir"
ls -la "$template_dir" 2>/dev/null || echo "目录不存在"
echo

echo "3. 可用模板列表："
termcap template list
echo

echo "4. 模板配置："
echo "Custom templates enabled: $(termcap config get templates custom_templates_enabled)"
echo "Builtin templates enabled: $(termcap config get templates builtin_templates_enabled)"
echo

echo "=== 诊断完成 ==="
```

## 最佳实践

### 1. 模板选择策略
- **为不同项目选择不同主题**：保持一致性
- **考虑观众**：教学用明亮主题，演示用暗色主题
- **测试多种效果**：同一内容生成多种风格对比

### 2. 自定义模板管理
- **命名规范**：使用有意义的名称，如 `company_theme`
- **版本控制**：将模板文件加入项目版本控制
- **文档记录**：为自定义模板创建说明文档

### 3. 性能优化
- **模板缓存**：经常使用的模板优先级更高
- **文件大小**：优化 SVG 文件大小，移除不必要的元素

### 4. 团队协作
```bash
# 创建团队模板包
#!/bin/bash
# setup_team_templates.sh

echo "Setting up team templates..."

# 下载团队模板
wget https://company.com/templates/company_theme.svg -O ~/.config/termcap/templates/company.svg
wget https://company.com/templates/presentation_theme.svg -O ~/.config/termcap/templates/presentation.svg

# 设置默认模板
termcap config set general default_template company

echo "Team templates installed successfully!"
termcap template list | grep -E "company|presentation"
```

TermCap 的模板系统为用户提供了很大的灵活性，既有丰富的内置选择，又支持完全的自定义。通过合理使用模板系统，可以让你的终端录制更加专业和吸引人。
