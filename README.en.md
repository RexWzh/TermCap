# TermCap

[![Test](https://github.com/rexwzh/termcap/actions/workflows/ci.yml/badge.svg)](https://github.com/rexwzh/termcap/actions/workflows/ci.yml)
[![Docs](https://github.com/rexwzh/termcap/actions/workflows/deploy.yml/badge.svg)](https://termcap.wzhecnu.cn)
[![PyPI](https://img.shields.io/pypi/v/termcap.svg)](https://pypi.org/project/termcap/)

**TermCap** is a Unix terminal recorder written in Python that renders your command line sessions as standalone SVG animations.

## Features

- Produce lightweight and clean looking animations embeddable on a project page
- Custom color themes, terminal UI and animation controls via [SVG templates](docs/manual/termcap-templates.en.md)
- Compatible with asciinema recording format

<p align="center">
    <img src="docs/examples/awesome_window_frame_js.svg" width="80%">
</p>

## Install

TermCap works on Linux, macOS and BSD, and requires Python >= 3.8.

```bash
pip3 install --user termcap
```

## Usage

Simply start recording a terminal session with:

```bash
$ termcap record
Recording started.
Enter "exit" command or Control-D to end.
```

You are now in a subshell where you can type your commands as usual.
Once you are done, exit the shell to end the recording:

```bash
$ exit
✓ 录制完成，时长: 10.5秒，共 42 个事件
Recording ended, cast file is /tmp/termcap_exp5nsr4.cast
```

Finally, render the recording to an SVG animation:

```bash
$ termcap render /tmp/termcap_exp5nsr4.cast animation.svg
Rendering started
✓ 渲染完成
Rendering ended, SVG animation is animation.svg
```

You can then use your favorite web browser to play the animation:

```bash
$ firefox animation.svg
```

## License

**MIT License**

## Author

- **termcap**: rexwzh (1073853456@qq.com)
