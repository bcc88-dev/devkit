"""devkit tools - CLI utilities."""

import typer
import shutil
import subprocess
import json
import shlex
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.prompt import Confirm

tools_app = typer.Typer(
    name="tools",
    help="CLI utility commands",
    no_args_is_help=True,
)


@tools_app.command("git-summary")
def git_summary():
    """Show a summary of the current git repo."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-20"],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        commits = result.stdout.strip()
        result2 = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        branch = result2.stdout.strip()

        # Count by author
        result3 = subprocess.run(
            ["git", "shortlog", "-s", "-n", "--all"],
            capture_output=True, text=True, cwd=Path.cwd()
        )
        authors = result3.stdout.strip()

        rprint(f"[bold cyan]Git Summary[/]")
        rprint(f"  Branch: [green]{branch}[/]")
        rprint(f"  Recent commits:")
        for line in commits.split("\n")[:5]:
            rprint(f"    {line}")
        if authors:
            rprint(f"\n  Contributors:")
            for line in authors.split("\n")[:5]:
                rprint(f"    {line}")
    except FileNotFoundError:
        rprint("[red]Not a git repository or git not found.[/]")


@tools_app.command("docker-clean")
def docker_clean(dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be removed")):
    """Clean up unused Docker resources."""
    try:
        # Check docker is available
        subprocess.run(["docker", "info"], capture_output=True, check=True)

        actions = [
            ("docker system prune -f", "Prune unused containers, networks, images"),
            ("docker volume prune -f", "Prune unused volumes"),
            ("docker builder prune -f", "Prune build cache"),
        ]

        if dry_run:
            rprint("[yellow]Dry run - would execute:[/]")
            for cmd, desc in actions:
                rprint(f"  [cyan]{cmd}[/] - {desc}")
        else:
            rprint("[bold]Cleaning Docker...[/]")
            for cmd, desc in actions:
                rprint(f"  [dim]{desc}...[/]")
                r = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
                if r.returncode == 0:
                    for line in r.stdout.strip().split("\n"):
                        if "Total" in line or line.strip():
                            rprint(f"    [green]{line.strip()}[/]")
                else:
                    rprint(f"    [red]{r.stderr.strip()}[/]")
            rprint("[green]✓ Docker cleanup complete[/]")
    except (subprocess.CalledProcessError, FileNotFoundError):
        rprint("[red]Docker not available on this system.[/]")


@tools_app.command("disk")
def disk_analysis(path: str = typer.Argument(".", help="Directory to analyze")):
    """Show disk usage by directory."""
    target = Path(path).expanduser().resolve()
    if not target.is_dir():
        rprint(f"[red]{target} is not a directory[/]")
        raise typer.Exit(1)

    rprint(f"[bold]Disk usage: {target}[/]")
    try:
        result = subprocess.run(
            f"du -sh {shlex.quote(str(target))}/* 2>/dev/null | sort -rh | head -15",
            capture_output=True, text=True, timeout=10, shell=True
        )
        lines = result.stdout.strip().split("\n")
        lines.sort(key=lambda x: x.split("\t")[0] if "\t" in x else "0", reverse=True)

        table = Table(box=None)
        table.add_column("Size", style="cyan")
        table.add_column("Path")

        for line in lines[:15]:
            if "\t" in line:
                size, item = line.split("\t", 1)
                table.add_row(size, item)

        if lines:
            rprint(table)
        else:
            rprint("  [dim](empty)[/]")
    except Exception as e:
        rprint(f"[red]{e}[/]")


@tools_app.command("todo")
def scan_todo(path: str = typer.Argument(".", help="Directory to scan")):
    """Find TODO/FIXME/HACK comments in code."""
    target = Path(path).expanduser().resolve()
    rprint(f"[bold]Scanning for comments in {target}[/]")

    try:
        result = subprocess.run(
            ["grep", "-rn", "--include=", "-e", "TODO", "-e", "FIXME", "-e", "HACK", "-e", "XXX",
             str(target)],
            capture_output=True, text=True, timeout=30
        )

        # Filter to only Python/JS/TS/Go/Rust files
        exts = (".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp")
        lines = result.stdout.strip().split("\n")
        matches = [l for l in lines if any(l.endswith(e) or f"{e}:" in l for e in exts) or any(f":{e}:" in l for e in exts)]

        if not matches:
            rprint("  [green]No TODO/FIXME/HACK comments found[/]")
            return

        for line in matches[:30]:
            rprint(f"  {line}")

        if len(matches) > 30:
            rprint(f"  [dim]... and {len(matches) - 30} more[/]")
    except FileNotFoundError:
        rprint("[red]grep not found[/]")
