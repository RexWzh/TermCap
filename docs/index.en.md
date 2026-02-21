# TermCap

**TermCap** is a Unix terminal recorder written in Python that renders your command line sessions as standalone SVG animations.

## Features

- Produce lightweight and clean looking animations embeddable on a project page
- Custom color themes, terminal UI and animation controls via [SVG templates](manual/termcap-templates.md)
- Compatible with asciinema recording format

<p align="center">
    <img src="../examples/awesome_window_frame_js.svg" width="80%">
</p>

## Install

TermCap is compatible with Linux, macOS and BSD OSes, requires Python >= 3.5 and can be installed using pip:

```bash
pip3 install --user termcap
```

## Usage

Simply start recording a terminal session with:

```bash
$ termcap
Recording started, enter "exit" command or Control-D to end
```

You are now in a subshell where you can type your commands as usual.
Once you are done, exit the shell to end the recording:

```bash
$ exit
Recording ended, file is /tmp/termcap_exp5nsr4.svg
```

Finally, use your favorite web browser to play the animation:

```bash
$ firefox /tmp/termcap_exp5nsr4.svg
```
