% TERMCAP(1)
% rexwzh
% 2025年2月

## 概要
**termcap** [output_path] [-c COMMAND] [-D DELAY] [-g GEOMETRY] [-m MIN_DURATION] [-M MAX_DURATION] [-s] [-t TEMPLATE] [--help]

**termcap record** [output_path] [-c COMMAND] [-g GEOMETRY] [-h]

**termcap render** *input_file* [output_path] [-D DELAY] [-m MIN_DURATION] [-M MAX_DURATION] [-s] [-t TEMPLATE] [-h]

### 描述
termcap 将终端会话录制为动画 SVG 格式。

#### 命令
termcap 的默认行为是渲染 shell 会话的 SVG 动画。如果没有提供输出文件名，将自动生成一个随机的临时文件名。

##### termcap record
以 asciicast v2 格式录制终端会话。录制文件是一个文本文件，包含时间信息以及终端会话期间屏幕上显示的内容。可以编辑它来更改录制的时间或终端屏幕上显示的信息。

##### termcap render
从 asciicast v1 或 v2 格式的录制文件渲染动画 SVG。这允许以 SVG 格式渲染使用 asciinema 制作的任何录制。也可以渲染静止帧。

## 选项

#### -c, --command=COMMAND
指定要录制的程序及其可选参数。COMMAND 必须是一个字符串，列出要执行的程序以及所有可供该程序使用的参数。例如 `--command='python -h'` 将使 termcap 录制 Python 解释器的用法。如果未设置此选项，termcap 将录制由 $SHELL 环境变量指定的程序或 `/bin/sh`。

#### -D, --loop-delay=DELAY
动画两次连续循环之间的延迟持续时间（以毫秒为单位）。

##### -g, --screen-geometry=GEOMETRY
用于渲染动画的终端屏幕的几何尺寸。几何尺寸必须以列数和行数的形式给出，中间用字符 "x" 分隔。例如 "82x19" 表示 82 列 19 行的屏幕。

##### -h, --help
打印用法并退出

##### -m, --min-frame-duration=MIN_DURATION
设置帧的最小持续时间（以毫秒为单位）。持续时间小于 MIN_DURATION 毫秒的帧将与连续帧合并。termcap 的默认行为是为终端屏幕的每次更新生成一帧，但是当录制频繁更新屏幕的命令时，这会导致动画文件大小激增。强制执行最小帧持续时间有助于减少动画的帧数，从而有助于控制动画的大小。MIN_DURATION 默认为 1 毫秒。

##### -M, --max-frame-duration=MAX_DURATION
将帧的最大持续时间设置为 MAX_DURATION 毫秒。持续时间超过 MAX_DURATION 毫秒的帧，其持续时间将被减少到 MAX_DURATION。

##### -t, --template=TEMPLATE
设置用于渲染 SVG 动画的 SVG 模板。TEMPLATE 可以是默认模板之一（base16_default_dark, dracula, gjm8_play, gjm8_single_loop, gjm8, powershell, progress_bar, putty, solarized_dark, solarized_light, terminal_app, ubuntu, window_frame_js, window_frame_powershell, window_frame, xterm）或有效模板的路径。

##### -s, --still-frames
输出 SVG 格式的静止帧而不是动画 SVG。如果指定了此选项，output_path 指的是帧的目标目录。

## SVG 模板
模板使得可以通过多种方式自定义 termcap 生成的 SVG 动画，包括但不限于：

* 指定用于渲染终端会话的颜色主题和字体
* 向动画添加自定义终端窗口框架，使其看起来像真正的终端
* 添加 JavaScript 代码以暂停动画、跳转到特定帧等

有关更多详细信息，请参阅[专用手册页](termcap-templates.md)。

## 环境变量
如果未指定 `--command` 选项，termcap 将生成 SHELL 环境变量指定的 shell，如果未设置该变量，则生成 `/bin/sh`。

## 示例

录制终端会话并生成名为 `animation.svg` 的 SVG 动画：
```
termcap animation.svg
```

录制终端会话并使用特定模板渲染：
```
termcap -t ~/templates/my_template.svg
```

录制特定程序，例如带有 pretty printing 选项的 IPython：
```
termcap -c 'ipython --pprint'
```

录制具有特定屏幕几何尺寸的终端会话：
```
termcap -g 80x24 animation.svg
```

以 asciicast v2 格式录制终端会话：
```
termcap record recording.cast
```

从 asciicast 格式的录制文件渲染 SVG 动画：
```
termcap render recording.cast animation.svg
```

强制执行最小和最大帧持续时间：
```
termcap -m 17 -M 2000
```

指定动画循环之间 2 秒的延迟：
```
termcap -D 2000
```

使用特定模板渲染静止帧而不是动画 SVG：
```
termcap -s -t gjm8_play
```
