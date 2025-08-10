"""Click-based CLI for termcap"""
import click
import sys
import os
import tempfile
from pathlib import Path

from .config_manager import get_config_manager
from .cli_config import show_config, list_templates, reset_config
from . import config as old_config
from . import main as old_main


def get_default_settings():
    """Get default settings from config manager"""
    manager = get_config_manager()
    config = manager.load_config()
    
    return {
        'template': config['general']['default_template'],
        'geometry': config['general']['default_geometry'],
        'min_duration': config['general']['default_min_duration'],
        'max_duration': config['general']['default_max_duration'],
        'loop_delay': config['general']['default_loop_delay'],
        'command': os.environ.get('SHELL', '/bin/bash'),
    }


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """Terminal capture tool - Record terminal sessions as SVG animations"""
    if version:
        import pkg_resources
        version_str = pkg_resources.require('termcap')[0].version
        click.echo(f'termcap {version_str}')
        return
        
    if ctx.invoked_subcommand is None:
        # Legacy mode: if no subcommand, try to parse as old-style arguments
        # This maintains compatibility with the original termtosvg interface
        legacy_main(sys.argv[1:])


@main.command()
@click.argument('output_path', required=False)
@click.option('-c', '--command', help='Program to record (default: $SHELL)')
@click.option('-g', '--geometry', help='Terminal geometry (WIDTHxHEIGHT)')
def record(output_path, command, geometry):
    """Record a terminal session to a cast file"""
    defaults = get_default_settings()
    
    # Use legacy record function
    args = ['termcap', 'record']
    if output_path:
        args.append(output_path)
    if command:
        args.extend(['-c', command])
    if geometry:
        args.extend(['-g', geometry])
        
    legacy_main(args)


@main.command()
@click.argument('input_file')
@click.argument('output_path', required=False)
@click.option('-D', '--loop-delay', type=int, help='Delay between animation loops (ms)')
@click.option('-m', '--min-duration', type=int, help='Minimum frame duration (ms)')
@click.option('-M', '--max-duration', type=int, help='Maximum frame duration (ms)')
@click.option('-s', '--still-frames', is_flag=True, help='Output still frames instead of animation')
@click.option('-t', '--template', help='SVG template to use')
def render(input_file, output_path, loop_delay, min_duration, max_duration, still_frames, template):
    """Render a cast file to SVG animation"""
    args = ['termcap', 'render', input_file]
    if output_path:
        args.append(output_path)
    if loop_delay:
        args.extend(['-D', str(loop_delay)])
    if min_duration:
        args.extend(['-m', str(min_duration)])
    if max_duration:
        args.extend(['-M', str(max_duration)])
    if still_frames:
        args.append('-s')
    if template:
        args.extend(['-t', template])
        
    legacy_main(args)


@main.group()
def config():
    """Configuration management commands"""
    pass


@config.command('show')
def config_show():
    """Show current configuration"""
    show_config()


@config.command('templates')
def config_templates():
    """List available templates"""
    list_templates()


@config.command('reset')
def config_reset():
    """Reset configuration to defaults"""
    if click.confirm('Are you sure you want to reset configuration to defaults?'):
        reset_config()


@config.command('set')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def config_set(section, key, value):
    """Set a configuration value"""
    manager = get_config_manager()
    
    # Try to convert numeric values
    if value.isdigit():
        value = int(value)
    elif value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
        
    manager.set_setting(section, key, value)
    click.echo(f'Set {section}.{key} = {value}')


@config.command('get')
@click.argument('section')
@click.argument('key')
def config_get(section, key):
    """Get a configuration value"""
    manager = get_config_manager()
    value = manager.get_setting(section, key)
    if value is not None:
        click.echo(f'{section}.{key} = {value}')
    else:
        click.echo(f'Configuration key {section}.{key} not found')


@main.group()
def template():
    """Template management commands"""
    pass


@template.command('install')
@click.argument('name')
@click.argument('template_file', type=click.Path(exists=True))
def template_install(name, template_file):
    """Install a custom template"""
    manager = get_config_manager()
    try:
        manager.install_custom_template(name, Path(template_file))
        click.echo(f'Template "{name}" installed successfully')
    except Exception as e:
        click.echo(f'Error installing template: {e}', err=True)
        sys.exit(1)


@template.command('remove')
@click.argument('name')
def template_remove(name):
    """Remove a custom template"""
    manager = get_config_manager()
    try:
        if click.confirm(f'Are you sure you want to remove template "{name}"?'):
            manager.remove_custom_template(name)
            click.echo(f'Template "{name}" removed successfully')
    except Exception as e:
        click.echo(f'Error removing template: {e}', err=True)
        sys.exit(1)


@template.command('list')
def template_list():
    """List all available templates"""
    list_templates()


def legacy_main(args):
    """Run the legacy main function for backward compatibility"""
    # Import here to avoid circular imports
    try:
        # Use the original main function from the old system
        templates = old_config.default_templates()
        default_template = 'gjm8'
        default_geometry = '82x19'
        default_min_dur = 17
        default_max_dur = 3000
        default_cmd = os.environ.get('SHELL', '/bin/bash')
        default_loop_delay = 1000
        
        # Parse and execute using the old system
        subcommand, parsed_args = old_main.parse(
            args, templates, default_template, default_geometry,
            default_min_dur, default_max_dur, default_cmd, default_loop_delay
        )
        
        if subcommand is None:
            old_main.main(args)
        elif subcommand == 'record':
            old_main.record(parsed_args)
        elif subcommand == 'render':
            old_main.render(parsed_args)
            
    except SystemExit:
        # Let SystemExit pass through
        raise
    except Exception as e:
        click.echo(f'Error: {e}', err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
