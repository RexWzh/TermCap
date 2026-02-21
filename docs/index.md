# TermCap

**TermCap** 是一个用 Python 编写的 Unix 终端录制工具，可以将你的命令行会话渲染为独立的 SVG 动画。

## 特性

- 生成轻量级且外观整洁的动画，可嵌入到项目页面中
- 通过 [SVG 模板](manual/termcap-templates.md) 支持自定义颜色主题、终端 UI 和动画控制
- 兼容 asciinema 录制格式

<p align="center">
    <img src="examples/awesome_window_frame_js.svg" width="80%">
</p>

## 安装

TermCap 兼容 Linux、macOS 和 BSD 操作系统，需要 Python >= 3.5，可以使用 pip 安装：

```bash
pip3 install --user termcap
```

## 使用方法

只需使用以下命令开始录制终端会话：

```bash
$ termcap
Recording started, enter "exit" command or Control-D to end
```

现在你处于一个子 shell 中，可以像往常一样输入命令。
完成后，退出 shell 即可结束录制：

```bash
$ exit
Recording ended, file is /tmp/termcap_exp5nsr4.svg
```

最后，使用你喜欢的 Web 浏览器播放动画：

```bash
$ firefox /tmp/termcap_exp5nsr4.svg
```
