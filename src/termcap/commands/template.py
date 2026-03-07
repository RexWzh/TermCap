import sys
from pathlib import Path

import click

from termcap.cli_config import list_templates
from termcap.config import get_config_manager


def register_template_commands(main):
    @main.group()
    def template():
        pass

    @template.command("install")
    @click.argument("name")
    @click.argument("template_file", type=click.Path(exists=True))
    def template_install(name, template_file):
        manager = get_config_manager()
        try:
            manager.install_custom_template(name, Path(template_file))
            click.echo(f'Template "{name}" installed successfully')
        except Exception as e:
            click.echo(f"Error installing template: {e}", err=True)
            sys.exit(1)

    @template.command("remove")
    @click.argument("name")
    def template_remove(name):
        manager = get_config_manager()
        try:
            if click.confirm(f'Are you sure you want to remove template "{name}"?'):
                manager.remove_custom_template(name)
                click.echo(f'Template "{name}" removed successfully')
        except Exception as e:
            click.echo(f"Error removing template: {e}", err=True)
            sys.exit(1)

    @template.command("list")
    def template_list():
        list_templates()
