"""Click-based CLI for termcap"""
import click

from termcap.commands import register_commands


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def main(ctx, version):
    """Terminal capture tool - Record terminal sessions as SVG animations"""
    if version:
        try:
            from importlib.metadata import version as get_version

            version_str = get_version("termcap")
        except ImportError:
            import pkg_resources

            version_str = pkg_resources.require("termcap")[0].version
        click.echo(f"termcap {version_str}")
        return


register_commands(main)


if __name__ == "__main__":
    main()
