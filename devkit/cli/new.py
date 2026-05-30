"""devkit new - project scaffold generator."""

import typer
from pathlib import Path
from rich import print as rprint
from rich.prompt import Prompt

from devkit.templates.registry import list_templates, render_template

new_app = typer.Typer(
    name="new",
    help="Scaffold a new project from a template",
    no_args_is_help=True,
)


@new_app.command("list")
def list_templates_cmd():
    """List available project templates."""
    templates = list_templates()
    if not templates:
        rprint("[yellow]No templates found.[/]")
        return
    rprint("[bold]Available templates:[/]")
    for t in templates:
        rprint(f"  [green]{t['name']}[/] - {t['description']}")


@new_app.command("create")
def create_project(
    template: str = typer.Argument(..., help="Template name"),
    project_name: str = typer.Option(None, "--name", "-n", help="Project name"),
    output_dir: str = typer.Option(".", "--output", "-o", help="Output directory"),
):
    """Scaffold a project from a template."""
    templates = list_templates()
    matching = [t for t in templates if t["name"] == template]
    if not matching:
        rprint(f"[red]Template '{template}' not found.[/]")
        rprint("Available:", ", ".join(t["name"] for t in templates))
        raise typer.Exit(1)

    tpl = matching[0]
    name = project_name or Prompt.ask("Project name", default="my-project")
    dest = Path(output_dir) / name

    if dest.exists():
        rprint(f"[red]Directory {dest} already exists.[/]")
        overwrite = Prompt.ask("Overwrite?", choices=["y", "n"], default="n")
        if overwrite != "y":
            rprint("[yellow]Aborted.[/]")
            raise typer.Exit()

    render_template(template, name, dest)
    rprint(f"\n[green]✓[/] Project [bold]{name}[/] created at [cyan]{dest}[/]")
    rprint(f"  cd {dest}")
    rprint(f"  # Follow README.md to get started")
