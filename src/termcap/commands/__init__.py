from termcap.commands.config import register_config_commands
from termcap.commands.record import register_record_command
from termcap.commands.render import register_render_command
from termcap.commands.replay import register_replay_command
from termcap.commands.template import register_template_commands


def register_commands(main):
    register_record_command(main)
    register_replay_command(main)
    register_render_command(main)
    register_config_commands(main)
    register_template_commands(main)
