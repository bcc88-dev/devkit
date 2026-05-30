"""devkit review server command."""

import typer
import os
from pathlib import Path
from rich import print as rprint

from devkit.pr_reviewer.server import serve as run_server

review_app = typer.Typer(
    name="review",
    help="AI-powered PR review",
    no_args_is_help=True,
)


@review_app.command("pr")
def review_pr(
    repo: str = typer.Argument(..., help="owner/repo"),
    pr_number: int = typer.Argument(..., help="PR number"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub PAT (or GH_TOKEN env)"),
):
    """Review a specific PR with AI analysis."""
    import httpx
    import json

    gh_token = token or os.environ.get("GH_TOKEN")
    if not gh_token:
        cfg = Path.home() / ".devkit" / "github_token"
        if cfg.exists():
            gh_token = cfg.read_text().strip()

    if not gh_token:
        rprint("[red]No GitHub token found. Set GH_TOKEN env, --token flag, or run [bold]devkit config set github_token TOKEN[/][/]")
        raise typer.Exit(1)

    headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github.v3+json"}
    api = "https://api.github.com"

    # Get PR info
    rprint(f"[dim]Fetching PR #{pr_number} from {repo}...[/]")
    resp = httpx.get(f"{api}/repos/{repo}/pulls/{pr_number}", headers=headers, timeout=15)
    if resp.status_code != 200:
        rprint(f"[red]Failed: {resp.status_code} - {resp.text}[/]")
        raise typer.Exit(1)

    pr = resp.json()
    rprint(f"  [bold]{pr['title']}[/] by [yellow]{pr['user']['login']}[/]")
    rprint(f"  +{pr.get('additions',0)} / -{pr.get('deletions',0)} lines")

    # Get the diff
    diff_resp = httpx.get(pr['diff_url'], headers=headers, timeout=15)
    diff = diff_resp.text

    # Analyze
    files = diff.count("diff --git")
    adds = sum(1 for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++"))
    rems = sum(1 for l in diff.split("\n") if l.startswith("-") and not l.startswith("---"))

    issues = []
    if "TODO" in diff:
        issues.append("⚠ TODO comments left in code")
    if "console.log" in diff or "print(" in diff:
        issues.append("⚠ Debug print/console.log statements")
    if "password" in diff.lower() or "secret" in diff.lower() or "token" in diff.lower():
        issues.append("🔴 Possible secrets exposed in diff!")

    from rich.panel import Panel
    rprint(Panel.fit(
        f"[bold cyan]Review: PR #{pr_number}[/]\n\n"
        f"[green]+{adds}[/] / [red]-{rems}[/] lines in [cyan]{files}[/] files\n\n"
        + ("\n".join(f"  {i}" for i in issues) if issues else "  [green]No obvious issues[/]"),
        border_style="cyan"
    ))

    # File list
    rprint("\n[bold]Files:[/]")
    for line in diff.split("\n"):
        if line.startswith("+++ b/") or line.startswith("--- a/"):
            continue
        if line.startswith("diff --git"):
            fname = line.split()[-1].replace("b/", "", 1)
            rprint(f"  [cyan]{fname}[/]")


@review_app.command("server")
def start_server(
    host: str = typer.Option("0.0.0.0", "--host", help="Listen host"),
    port: int = typer.Option(8080, "--port", "-p", help="Listen port"),
):
    """Start the PR review webhook server."""
    rprint(f"[bold cyan]Starting PR Review Server[/]")
    rprint(f"  Webhook: http://{host}:{port}/github/webhook")
    rprint("  Ctrl+C to stop\n")
    run_server(host=host, port=port)


@review_app.command("webhook")
def setup_webhook(
    repo: str = typer.Argument(..., help="owner/repo"),
    webhook_url: str = typer.Argument(..., help="Your server URL (e.g. https://your-server.com)"),
    token: str = typer.Option(None, "--token", "-t", help="GitHub PAT"),
):
    """Install a webhook on a repo for auto-PR review."""
    import httpx
    gh_token = token or os.environ.get("GH_TOKEN")
    if not gh_token:
        rprint("[red]GitHub token required[/]")
        raise typer.Exit(1)

    payload = {
        "name": "web",
        "active": True,
        "events": ["pull_request"],
        "config": {
            "url": f"{webhook_url}/github/webhook",
            "content_type": "json",
        }
    }

    resp = httpx.post(
        f"https://api.github.com/repos/{repo}/hooks",
        headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github.v3+json"},
        json=payload,
        timeout=15,
    )

    if resp.status_code == 201:
        rprint(f"[green]✓[/] Webhook installed on [cyan]{repo}[/]")
        rprint(f"  Events: pull_request → {webhook_url}/github/webhook")
    else:
        rprint(f"[red]Failed: {resp.status_code} - {resp.text}[/]")
