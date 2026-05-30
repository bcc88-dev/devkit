"""devkit CLI - typer-based entry point."""

import typer
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="devkit",
    help="Your all-in-one developer toolkit",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Register subcommand groups
from devkit.cli.new import new_app  # noqa: E402
from devkit.cli.review import review_app  # noqa: E402
from devkit.cli.tools import tools_app  # noqa: E402
from devkit.cli.data import data_app  # noqa: E402
from devkit.cli.config import config_app  # noqa: E402
from devkit.cli.buy import buy_app  # noqa: E402

app.add_typer(new_app, name="new", help="Generate a project from a template")
app.add_typer(review_app, name="review", help="AI-powered PR review")
app.add_typer(tools_app, name="tools", help="CLI utility commands")
app.add_typer(data_app, name="data", help="Fetch dev data (HN, GitHub, etc.)")
app.add_typer(config_app, name="config", help="Manage devkit configuration")
app.add_typer(buy_app, name="buy", help="Purchase templates and products")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """DevKit — your terminal Swiss Army knife for building software."""
    if ctx.invoked_subcommand is None:
        table = Table(title="[bold cyan]devkit[/] commands", box=None)
        table.add_column("Command", style="green")
        table.add_column("Description", style="white")
        table.add_row("devkit new", "Scaffold a new project from a template")
        table.add_row("devkit review", "AI-powered PR review on GitHub")
        table.add_row("devkit tools", "CLI utilities (git, docker, etc.)")
        table.add_row("devkit data", "Fetch dev data (HN, GitHub trends)")
        table.add_row("devkit config", "Manage settings and API keys")
        rprint(table)


if __name__ == "__main__":
    app()
