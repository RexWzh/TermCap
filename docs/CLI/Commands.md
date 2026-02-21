# TermCap CLI 命令参考

*基于实际测试的完整命令手册*

## 概览

TermCap 提供了一个现代化的命令行接口，基于 `click` 框架构建。所有命令都遵循直观的子命令结构。

## 主命令

### termcap

基础语法：
```bash
termcap [OPTIONS] COMMAND [ARGS]...
```

描述：Terminal capture tool - Record terminal sessions as SVG animations

#### 全局选项

| 选项 | 描述 | 示例 |
|------|------|------|
| `--version` | 显示版本信息并退出 | `termcap --version` |
| `--help` | 显示帮助信息并退出 | `termcap --help` |

#### 子命令

| 子命令 | 描述 |
|---------|------|
| [`record`](#record-命令) | 录制终端会话到 cast 文件 |
| [`render`](#render-命令) | 将 cast 文件渲染为 SVG 动画 |
| [`config`](#config-命令) | 配置管理命令 |
| [`template`](#template-命令) | 模板管理命令 |

---

## record 命令

### 基础用法

```bash
termcap record [OPTIONS] [OUTPUT_PATH]
```

**功能：** 录制终端会话到 cast 文件

### 参数

#### 位置参数
- `OUTPUT_PATH` (可选): 输出的 cast 文件路径
  - 默认：`recording.cast`
  - 示例：`my_session.cast`

#### 选项

| 选项 | 短参数 | 类型 | 描述 | 默认值 | 示例 |
|------|--------|------|------|--------|------|
| `--command` | `-c` | TEXT | 要录制的程序 | `$SHELL` | `-c "python3"` |
| `--geometry` | `-g` | TEXT | 终端几何尺寸 (WIDTHxHEIGHT) | `82x19` | `-g 120x40` |
| `--help` | | FLAG | 显示帮助信息 | | |

### 使用示例

#### 基础录制
```bash
# 录制默认 shell 会话
termcap record

# 指定输出文件名
termcap record my_demo.cast
```

#### 指定程序录制
```bash
# 录制 Python 交互式会话
termcap record python_demo.cast -c "python3"

# 录制特定脚本
termcap record script_demo.cast -c "bash my_script.sh"

# 录制系统监控工具
termcap record htop_demo.cast -c "htop"
```

#### 自定义终端尺寸
```bash
# 大屏幕录制
termcap record large_demo.cast -g 120x40

# 小屏幕录制
termcap record small_demo.cast -g 60x15

# 正方形终端
termcap record square_demo.cast -g 80x80
```

### 录制过程

1. **开始录制：** 执行命令后，会显示：
   ```
   Recording started, enter "exit" command or Control-D to end
   ```

2. **进行操作：** 在新的终端会话中执行你的命令

3. **结束录制：** 使用以下任一方式：
   - 输入 `exit` 命令
   - 按 `Ctrl+D`
   - 当指定程序结束时自动结束

4. **录制完成：** 显示：
   ```
   Recording ended, cast file is [filename].cast
   ```

### 注意事项

- 录制的文件为 asciicast v2 格式
- 录制过程中的所有输入输出都会被捕获
- 终端颜色和格式信息会被保留
- 录制文件大小取决于会话长度和内容

---

## render 命令

### 基础用法

```bash
termcap render [OPTIONS] INPUT_FILE [OUTPUT_PATH]
```

**功能：** 将 cast 文件渲染为 SVG 动画

### 参数

#### 位置参数
- `INPUT_FILE` (必需): 输入的 cast 文件路径
- `OUTPUT_PATH` (可选): 输出的 SVG 文件路径
  - 默认：与输入文件同名，扩展名为 `.svg`

#### 选项

| 选项 | 短参数 | 类型 | 描述 | 默认值 | 示例 |
|------|--------|------|------|--------|------|
| `--loop-delay` | `-D` | INTEGER | 动画循环间的延迟 (毫秒) | 1000 | `-D 2000` |
| `--min-duration` | `-m` | INTEGER | 最小帧持续时间 (毫秒) | 17 | `-m 50` |
| `--max-duration` | `-M` | INTEGER | 最大帧持续时间 (毫秒) | 3000 | `-M 5000` |
| `--still-frames` | `-s` | FLAG | 输出静态帧而非动画 | false | `-s` |
| `--template` | `-t` | TEXT | 使用的 SVG 模板 | gjm8 | `-t dracula` |
| `--help` | | FLAG | 显示帮助信息 | | |

### 使用示例

#### 基础渲染
```bash
# 使用默认设置渲染
termcap render session.cast

# 指定输出文件名
termcap render session.cast my_animation.svg
```

#### 使用不同模板
```bash
# 使用 Dracula 主题
termcap render session.cast animation.svg -t dracula

# 使用 Ubuntu 风格
termcap render session.cast animation.svg -t ubuntu

# 使用窗口框架模板
termcap render session.cast animation.svg -t window_frame
```

#### 调整时间参数
```bash
# 快速播放（较短的帧间隔）
termcap render session.cast fast.svg -m 10 -M 1000

# 慢速播放（较长的帧间隔）
termcap render session.cast slow.svg -m 100 -M 5000

# 调整循环延迟
termcap render session.cast animation.svg -D 3000
```

#### 高级选项
```bash
# 生成静态帧（不是动画）
termcap render session.cast static.svg -s

# 组合多个选项
termcap render session.cast custom.svg -t dracula -D 2000 -m 25 -M 2000
```

### 渲染过程

1. **开始渲染：** 显示：
   ```
   Rendering started
   ```

2. **处理进度：** 大文件可能显示进度信息

3. **渲染完成：** 生成 SVG 文件

### 注意事项

- **已知问题：** 当前版本 (0.1.1) 在渲染功能上存在 bug
- SVG 文件可在现代浏览器中直接打开
- 生成的 SVG 是独立的，包含所有必要的样式和脚本
- 文件大小取决于原始会话的复杂度和长度

---

## config 命令

### 基础用法

```bash
termcap config [OPTIONS] COMMAND [ARGS]...
```

**功能：** 配置管理命令

### 子命令

| 子命令 | 描述 |
|---------|------|
| `show` | 显示当前配置 |
| `get` | 获取配置值 |
| `set` | 设置配置值 |
| `reset` | 重置配置为默认值 |
| `templates` | 列出可用模板 |

详细内容请参考 [配置管理文档](Configuration.md)。

---

## template 命令

### 基础用法

```bash
termcap template [OPTIONS] COMMAND [ARGS]...
```

**功能：** 模板管理命令

### 子命令

| 子命令 | 描述 |
|---------|------|
| `list` | 列出所有可用模板 |
| `install` | 安装自定义模板 |
| `remove` | 删除自定义模板 |

详细内容请参考 [模板管理文档](Templates.md)。

---

## 实用组合命令

### 快速演示工作流

```bash
# 完整的演示流程
termcap record demo.cast -g 100x30 -c "bash demo_script.sh"
termcap render demo.cast demo.svg -t window_frame -D 2000
```

### 批量处理

```bash
# 批量录制
for i in {1..5}; do
    termcap record "demo_$i.cast" -c "echo 'Demo $i'"
done

# 批量渲染
for f in *.cast; do
    termcap render "$f" "${f%.cast}.svg" -t dracula
done
```

### 配置预设

```bash
# 设置演示环境
termcap config set general default_geometry 120x40
termcap config set general default_template window_frame
termcap config set general default_loop_delay 2000

# 验证设置
termcap config show
```

## 错误处理

### 常见错误信息

1. **文件不存在：**
   ```
   Error: Could not open file 'nonexistent.cast'
   ```

2. **无效模板：**
   ```
   Error: Template 'invalid_template' not found
   ```

3. **权限问题：**
   ```
   Error: Permission denied writing to '/path/to/file'
   ```

4. **无效几何尺寸：**
   ```
   Error: Invalid geometry format 'invalid'
   ```

### 调试技巧

```bash
# 检查文件存在
ls -la *.cast

# 验证模板名称
termcap template list | grep template_name

# 检查配置
termcap config show

# 测试小文件
termcap record test.cast -c "echo 'test'"
```

## 命令快速参考

```bash
# 查看帮助
termcap --help
termcap record --help
termcap render --help
termcap config --help
termcap template --help

# 基本操作
termcap --version
termcap record [file.cast]
termcap render file.cast [output.svg]

# 配置管理
termcap config show
termcap config set section key value
termcap config get section key
termcap config reset

# 模板管理
termcap template list
termcap template install name file.svg
termcap template remove name
```

此文档基于 TermCap v0.1.1 的实际测试结果编写。如果遇到问题或需要更新信息，请参考内置帮助或联系开发者。
