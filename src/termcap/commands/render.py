import sys
from pathlib import Path

import click
from rich.console import Console

from termcap.commands.common import get_default_settings
from termcap.parser.asciicast import read_records
from termcap.renderer import render_animation, render_still_frames


def register_render_command(main):
    @main.command()
    @click.argument("input_file")
    @click.argument("output_path", required=False)
    @click.option("-D", "--loop-delay", type=int, help="Delay between animation loops (ms)")
    @click.option("-m", "--min-duration", type=int, help="Minimum frame duration (ms)")
    @click.option("-M", "--max-duration", type=int, help="Maximum frame duration (ms)")
    @click.option("-s", "--still-frames", is_flag=True, help="Output still frames instead of animation")
    @click.option("-t", "--template", help="SVG template to use")
    def render(input_file, output_path, loop_delay, min_duration, max_duration, still_frames, template):
        defaults = get_default_settings()

        if template is None:
            template = defaults["template"]
        if min_duration is None:
            min_duration = defaults["min_duration"]
        if max_duration is None:
            max_duration = defaults["max_duration"]
        if loop_delay is None:
            loop_delay = defaults["loop_delay"]

        if output_path is None:
            input_path = Path(input_file)
            if still_frames:
                output_path = str(input_path.parent / f"{input_path.stem}_frames")
            else:
                output_path = str(input_path.with_suffix(".svg"))

        console = Console()
        records_iter = read_records(input_file)
        try:
            header = next(records_iter)
        except StopIteration:
            click.echo("Error: Empty input file", err=True)
            sys.exit(1)

        if still_frames:
            with console.status("正在渲染 SVG...", spinner="dots"):
                render_still_frames(
                    records_iter,
                    header,
                    output_path,
                    template,
                    min_duration,
                    max_duration,
                    loop_delay,
                )
            console.print("✓ 渲染完成")
            click.echo(f"Rendering ended, SVG frames are located at {output_path}")
        else:
            with console.status("正在渲染 SVG...", spinner="dots"):
                render_animation(
                    records_iter,
                    header,
                    output_path,
                    template,
                    min_duration,
                    max_duration,
                    loop_delay,
                )
            console.print("✓ 渲染完成")
            click.echo(f"Rendering ended, SVG animation is {output_path}")
