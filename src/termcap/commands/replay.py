import click

from termcap.player import play


def register_replay_command(main):
    @main.command()
    @click.argument("input_file")
    @click.option("-s", "--speed", type=float, default=1.0, help="Playback speed (default: 1.0)")
    @click.option("-i", "--idle-time-limit", type=float, help="Limit idle time to N seconds")
    def replay(input_file, speed, idle_time_limit):
        play(input_file, speed, idle_time_limit)
