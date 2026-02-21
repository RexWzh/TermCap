# TermCap 快速入门指南

*基于实际操作经验编写的完整入门教程*

## 前提条件

在开始之前，请确保已完成：
- ✅ [安装 TermCap](Installation.md)
- ✅ 验证安装：`termcap --version`

## 基础概念

### 工作流程
1. **录制** - 将终端会话录制为 `.cast` 文件
2. **渲染** - 将 `.cast` 文件转换为 SVG 动画
3. **分享** - 分享生成的 SVG 文件

### 文件格式
- **`.cast` 文件** - asciicast 格式，存储终端会话数据
- **`.svg` 文件** - 可缩放矢量图形，最终的动画输出

## 快速开始

### 第一次录制

#### 1. 开始录制

```bash
# 录制一个简单的会话
termcap record my_first_recording.cast
```

执行后，你会看到：
```
Recording started, enter "exit" command or Control-D to end
```

#### 2. 进行一些操作

在新的终端会话中，尝试一些命令：
```bash
echo "Hello, TermCap!"
ls -la
date
pwd
exit  # 或按 Ctrl+D 结束录制
```

#### 3. 录制完成

录制结束后，你会看到：
```
Recording ended, cast file is my_first_recording.cast
```

### 检查录制文件

```bash
# 查看 cast 文件信息
ls -la my_first_recording.cast

# 查看文件前几行（JSON格式）
head -3 my_first_recording.cast
```

**预期输出：**
```
{"version": 2, "width": 80, "height": 24}
[0.0, "o", "Hello, TermCap!\r\n"]
[0.000116, "o", "total 37\r\n"]
```

### 渲染为 SVG

```bash
# 使用默认模板渲染
termcap render my_first_recording.cast my_animation.svg
```

**注意：** 由于当前版本存在渲染bug，可能会遇到错误。这是已知问题，预计在下一版本修复。

## 实际演示案例

让我们创建一个更有趣的演示：

### 创建演示脚本

```bash
# 创建一个演示脚本
cat > demo.sh << 'EOF'
#!/bin/bash

echo "=== TermCap 功能演示 ==="
echo

echo "当前目录："
pwd
echo

echo "系统信息："
uname -a
echo

echo "Python 版本："
python --version
echo

echo "创建测试文件："
echo "Hello from TermCap demo!" > test.txt
echo "文件创建成功！"
cat test.txt
echo

echo "清理："
rm test.txt
echo "演示完成！"
EOF

chmod +x demo.sh
```

### 录制演示

```bash
# 录制演示脚本
termcap record demo_session.cast -c "bash demo.sh"
```

**实际录制输出：**
```
Recording started, enter "exit" command or Control-D to end
=== TermCap 功能演示 ===

当前目录：
/workspace

系统信息：
Linux matrix-agent-server-uapm-86db459fd-vqwjf 5.10.134-18.al8.x86_64

Python 版本：
Python 3.12.5

创建测试文件：
文件创建成功！
Hello from TermCap demo!

清理：
演示完成！
Recording ended, cast file is demo_session.cast
```

## 配置管理

### 查看当前配置

```bash
termcap config show
```

**实际输出：**
```
Configuration file: /home/user/.config/termcap/config.toml
Templates directory: /home/user/.config/termcap/templates

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

### 修改配置

```bash
# 修改默认几何尺寸
termcap config set general default_geometry 100x30

# 修改默认模板
termcap config set general default_template dracula

# 修改循环延迟
termcap config set general default_loop_delay 2000

# 验证修改
termcap config get general default_geometry
```

### 重置配置

```bash
# 重置为默认配置
termcap config reset

# 确认重置
termcap config show
```

## 模板管理

### 查看可用模板

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
  gjm8 (builtin)  # 默认模板
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

### 使用不同模板

```bash
# 使用 dracula 主题（一旦渲染bug修复后）
termcap render demo_session.cast demo_dracula.svg --template dracula

# 使用 ubuntu 主题
termcap render demo_session.cast demo_ubuntu.svg --template ubuntu

# 使用 window_frame 主题
termcap render demo_session.cast demo_frame.svg --template window_frame
```

## 高级录制选项

### 指定几何尺寸

```bash
# 录制更大的终端尺寸
termcap record large_demo.cast -g 120x40
```

### 指定要录制的命令

```bash
# 直接录制特定命令
termcap record python_demo.cast -c "python3"

# 录制脚本执行
termcap record script_demo.cast -c "bash my_script.sh"

# 录制交互式程序
termcap record top_demo.cast -c "top" 
```

## 实用技巧

### 1. 快速演示

创建快速演示用的别名：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias record-demo='termcap record demo-$(date +%Y%m%d-%H%M%S).cast'
alias show-templates='termcap template list'
```

### 2. 批量处理

```bash
# 批量录制多个会话
for i in {1..3}; do
    echo "Recording session $i..."
    termcap record session_$i.cast -c "echo 'This is session $i'; sleep 2"
done
```

### 3. 预设配置

为不同用途设置不同配置：

```bash
# 演示配置
termcap config set general default_geometry 100x30
termcap config set general default_template window_frame

# 教学配置
termcap config set general default_geometry 80x24
termcap config set general default_template ubuntu
```

## 常见使用场景

### 1. 技术演示

```bash
# 录制技术演示
termcap record tech_demo.cast -g 120x30
# 在录制中演示你的技术栈
```

### 2. 教学材料

```bash
# 录制教学步骤
termcap record tutorial_step1.cast -c "bash tutorial_script.sh"
```

### 3. Bug 报告

```bash
# 录制问题重现步骤
termcap record bug_reproduction.cast
# 在录制中重现问题
```

### 4. 命令行工具演示

```bash
# 演示 CLI 工具
termcap record cli_tool_demo.cast -c "my-cli-tool --help"
```

## 文件组织建议

### 目录结构

```
~/termcap_recordings/
├── demos/
│   ├── 2024-01-15_tech_demo.cast
│   └── 2024-01-15_tech_demo.svg
├── tutorials/
│   ├── python_basics.cast
│   └── git_workflow.cast
└── bug_reports/
    ├── issue_123.cast
    └── issue_123.svg
```

### 命名约定

```bash
# 推荐的文件命名
YYYY-MM-DD_description.cast
project_name_feature_demo.cast
bug_issue_number.cast
```

## 故障排除

### 录制问题

**问题：** 录制时终端响应慢
**解决：** 使用较小的几何尺寸：`-g 80x24`

**问题：** 录制文件为空
**解决：** 确保在录制会话中执行了命令

### 渲染问题

**已知问题：** 当前版本 (0.1.1) 的渲染功能存在 bug
**临时解决：** 
1. 录制功能正常工作
2. 可以查看 `.cast` 文件内容
3. 等待修复版本或联系开发者

## 下一步

完成快速入门后，你可以：

1. 阅读 [CLI 命令详解](CLI/Commands.md) 了解所有可用选项
2. 学习 [配置管理](CLI/Configuration.md) 自定义设置
3. 探索 [模板系统](CLI/Templates.md) 创建自定义主题
4. 查看 [使用示例](Examples/) 获得更多灵感
5. 了解 [高级用法](AdvancedUsage.md) 进行深度定制

## 获得帮助

- GitHub Issues: https://github.com/RexWzh/TermCap/issues
- 邮箱: 1073853456@qq.com
- 查看内置帮助: `termcap --help`
