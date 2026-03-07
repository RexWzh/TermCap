import click

from termcap.cli_config import list_templates, reset_config, show_config
from termcap.config import get_config_manager


def register_config_commands(main):
    @main.group()
    def config():
        pass

    @config.command("show")
    def config_show():
        show_config()

    @config.command("templates")
    def config_templates():
        list_templates()

    @config.command("reset")
    def config_reset():
        if click.confirm("Are you sure you want to reset configuration to defaults?"):
            reset_config()

    @config.command("set")
    @click.argument("section")
    @click.argument("key")
    @click.argument("value")
    def config_set(section, key, value):
        manager = get_config_manager()
        if value.isdigit():
            value = int(value)
        elif value.lower() in ("true", "false"):
            value = value.lower() == "true"
        manager.set_setting(section, key, value)
        click.echo(f"Set {section}.{key} = {value}")

    @config.command("get")
    @click.argument("section")
    @click.argument("key")
    def config_get(section, key):
        manager = get_config_manager()
        value = manager.get_setting(section, key)
        if value is not None:
            click.echo(f"{section}.{key} = {value}")
        else:
            click.echo(f"Configuration key {section}.{key} not found")
