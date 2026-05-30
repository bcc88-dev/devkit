"""devkit config - manage settings."""

import typer
from pathlib import Path
from rich import print as rprint

config_app = typer.Typer(
    name="config",
    help="Manage devkit configuration",
    no_args_is_help=True,
)

CONFIG_DIR = Path.home() / ".devkit"


def _ensure_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@config_app.command("set")
def set_key(
    key: str = typer.Argument(..., help="Config key (e.g. github_token, openai_key)"),
    value: str = typer.Argument(..., help="Value to set"),
):
    """Set a config value."""
    _ensure_config()
    (CONFIG_DIR / key).write_text(value)
    rprint(f"[green]✓[/] Saved [bold]{key}[/]")


@config_app.command("get")
def get_key(
    key: str = typer.Argument(..., help="Config key"),
):
    """Get a config value."""
    path = CONFIG_DIR / key
    if path.exists():
        rprint(path.read_text().strip())
    else:
        rprint(f"[red]Key '{key}' not found[/]")

@config_app.command("list")
def list_keys():
    """List all stored keys."""
    _ensure_config()
    keys = list(CONFIG_DIR.iterdir())
    if not keys:
        rprint("[dim]No config keys set[/]")
        return
    for k in keys:
        rprint(f"  [green]{k.name}[/]")
