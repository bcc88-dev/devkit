"""devkit data - fetch dev data from APIs."""

import typer
import httpx
from datetime import datetime
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel

data_app = typer.Typer(
    name="data",
    help="Fetch dev data (HN, GitHub, etc.)",
    no_args_is_help=True,
)

HN_BASE = "https://hacker-news.firebaseio.com/v0"


@data_app.command("hn-top")
def hn_top(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of stories"),
):
    """Fetch top Hacker News stories."""
    rprint("[dim]Fetching top HN stories...[/]")
    resp = httpx.get(f"{HN_BASE}/topstories.json", timeout=10)
    ids = resp.json()[:limit]

    table = Table(title=f"[bold]Top {limit} Hacker News[/]", box=None)
    table.add_column("#", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Author", style="yellow")

    for i, story_id in enumerate(ids, 1):
        story = httpx.get(f"{HN_BASE}/item/{story_id}.json", timeout=10).json()
        if story and story.get("title"):
            table.add_row(
                str(i),
                story.get("title", "?")[:60],
                str(story.get("score", 0)),
                story.get("by", "?"),
            )

    rprint(table)


@data_app.command("hn-new")
def hn_new(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of stories"),
):
    """Fetch newest Hacker News stories."""
    rprint("[dim]Fetching newest HN stories...[/]")
    resp = httpx.get(f"{HN_BASE}/newstories.json", timeout=10)
    ids = resp.json()[:limit]

    table = Table(title=f"[bold]Newest {limit} Hacker News[/]", box=None)
    table.add_column("#", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Score", style="green")
    table.add_column("Author", style="yellow")

    for i, story_id in enumerate(ids, 1):
        story = httpx.get(f"{HN_BASE}/item/{story_id}.json", timeout=10).json()
        if story and story.get("title"):
            table.add_row(
                str(i),
                story.get("title", "?")[:60],
                str(story.get("score", 0)),
                story.get("by", "?"),
            )

    rprint(table)


@data_app.command("hn-comments")
def hn_comments(
    story_id: int = typer.Argument(..., help="HN story/item ID"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of top comments"),
):
    """Fetch comments for a HN story."""
    rprint(f"[dim]Fetching comments for HN item #{story_id}...[/]")
    story = httpx.get(f"{HN_BASE}/item/{story_id}.json", timeout=10).json()
    if not story:
        rprint("[red]Story not found.[/]")
        raise typer.Exit(1)

    rprint(f"\n[bold cyan]{story.get('title', 'untitled')}[/]")
    rprint(f"  by [yellow]{story.get('by', '?')}[/] | Score: [green]{story.get('score', 0)}[/]")

    kids = story.get("kids", [])[:limit]
    if not kids:
        rprint("  [dim]No comments[/]")
        return

    for kid_id in kids:
        comment = httpx.get(f"{HN_BASE}/item/{kid_id}.json", timeout=10).json()
        if comment and comment.get("text"):
            from html import unescape
            text = unescape(comment["text"])[:300]
            rprint(f"\n  [yellow]{comment.get('by', '?')}[/]:")
            rprint(f"  {text}")


@data_app.command("github-trending")
def github_trending(
    language: str = typer.Option(None, "--lang", "-l", help="Language filter"),
    since: str = typer.Option("daily", "--since", "-s", help="daily|weekly|monthly"),
):
    """Fetch trending GitHub repositories."""
    rprint("[dim]Fetching GitHub trending...[/]")

    params = {"since": since}
    if language:
        params["language"] = language

    # Use the unofficial trending API
    try:
        # Scrape from GitHub trending page
        import re
        resp = httpx.get(
            f"https://github.com/trending/{language or ''}?since={since}",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
        )
        html = resp.text

        # Parse repo articles
        repos = []
        for match in re.finditer(
            r'href="/([^/"]+)/([^/"]+)"[^>]*>[^<]*</a>.*?'
            r'class="Link--muted">\s*([0-9,]+)\s*</a>.*?'
            r'class="Link--muted">\s*([0-9,]+)\s*</a>',
            html, re.DOTALL
        ):
            repos.append({
                "author": match.group(1),
                "name": match.group(2),
                "description": "",
                "stars": match.group(3).replace(",", ""),
                "forks": match.group(4).replace(",", ""),
            })

        if not repos:
            # Simpler fallback: just extract repo links
            for m in re.finditer(r'<h2[^>]*>.*?href="/([^/"]+)/([^/"]+)"', html):
                name = m.group(1) + "/" + m.group(2)
                if name not in [r["author"] + "/" + r["name"] for r in repos]:
                    repos.append({"author": m.group(1), "name": m.group(2), "description": "", "stars": "?", "forks": "?"})

    except Exception as e:
        rprint(f"[red]Could not fetch trending: {e}[/]")
        raise typer.Exit(1)

    table = Table(title=f"[bold]Trending GitHub ({since})[/]", box=None)
    table.add_column("#", style="dim")
    table.add_column("Repo", style="cyan")
    table.add_column("⭐ Stars", style="green")
    table.add_column("Forks", style="yellow")
    table.add_column("Description", style="white", no_wrap=False)

    for i, repo in enumerate(repos[:10], 1):
        table.add_row(
            str(i),
            f"{repo.get('author', '?')}/{repo.get('name', '?')}",
            f"{repo.get('stars', 0):,}",
            f"{repo.get('forks', 0):,}",
            (repo.get("description") or "")[:60],
        )

    rprint(table)
