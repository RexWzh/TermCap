import shlex
import sys
import time

import click
from rich.console import Console
from rich.panel import Panel

from termcap.commands.common import get_default_settings
from termcap.recorder.core import record_session
from termcap.recorder.terminal import TerminalMode, get_terminal_size


def register_record_command(main):
    @main.command()
    @click.argument("output_path", required=False)
    @click.option("-c", "--command", help="Program to record (default: $SHELL)")
    @click.option("-g", "--geometry", help="Terminal geometry (WIDTHxHEIGHT)")
    def record(output_path, command, geometry):
        defaults = get_default_settings()

        if command is None:
            command = defaults["command"]
        if output_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path = f"termcap_{timestamp}.cast"

        if geometry:
            try:
                columns, lines = map(int, geometry.split("x"))
            except ValueError:
                click.echo(f"Error: Invalid geometry '{geometry}'. Use format like '80x24'", err=True)
                sys.exit(1)
        else:
            columns, lines = get_terminal_size(sys.stdout.fileno())

        process_args = shlex.split(command)
        console = Console()
        console.print(
            Panel(
                'Recording started.\nEnter "exit" command or Control-D to end.',
                title="TermCap Recorder",
                border_style="green",
            )
        )

        start_time = time.time()
        count = 0

        with TerminalMode(sys.stdin.fileno()):
            records = record_session(process_args, columns, lines, sys.stdin.fileno(), sys.stdout.fileno())
            with open(output_path, "w") as cast_file:
                header = next(records)
                print(header.to_json_line(), file=cast_file)
                for record_item in records:
                    print(record_item.to_json_line(), file=cast_file)
                    count += 1

        duration = time.time() - start_time
        console.print(f"✓ 录制完成，时长: {duration:.1f}秒，共 {count} 个事件")
        console.print(f"Recording ended, cast file is {output_path}")
