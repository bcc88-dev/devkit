"""devkit buy - purchase templates and products."""

import typer
import webbrowser
from pathlib import Path
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel

buy_app = typer.Typer(
    name="buy",
    help="Purchase templates and products",
    no_args_is_help=True,
)

PRODUCTS = {
    "saas-starter": {
        "name": "SaaS Starter Kit",
        "price": "$69",
        "url": "https://app.gumroad.com/l/saas-starter",
        "desc": "Next.js 14 + Supabase + Stripe + Auth boilerplate",
    },
}


@buy_app.command("list")
def list_products():
    """List available products for purchase."""
    table = Table(title="[bold]Available Products[/]", box=None)
    table.add_column("Product", style="cyan")
    table.add_column("Price", style="green")
    table.add_column("Description")

    for pid, p in PRODUCTS.items():
        table.add_row(pid, p["price"], p["desc"])
    rprint(table)


@buy_app.command("purchase")
def purchase(
    product: str = typer.Argument(..., help="Product ID to purchase"),
):
    """Open the purchase page for a product."""
    if product not in PRODUCTS:
        rprint(f"[red]Unknown product: {product}[/]")
        rprint("Available:", ", ".join(PRODUCTS.keys()))
        raise typer.Exit(1)

    p = PRODUCTS[product]
    rprint(Panel.fit(
        f"[bold cyan]{p['name']}[/]\n"
        f"  Price: [green]{p['price']}[/]\n"
        f"  {p['desc']}\n\n"
        f"Opening [blue]{p['url']}[/] in your browser...",
        border_style="cyan"
    ))
    webbrowser.open(p["url"])


@buy_app.command("serve")
def serve_landing(
    host: str = typer.Option("0.0.0.0", "--host"),
    port: int = typer.Option(8081, "--port", "-p"),
):
    """Serve the product landing page locally."""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import os

    landing_dir = Path(__file__).parent.parent.parent / "landing"

    if not landing_dir.exists():
        rprint(f"[red]Landing page not found at {landing_dir}[/]")
        raise typer.Exit(1)

    os.chdir(str(landing_dir))
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    rprint(f"[green]Landing page: http://{host}:{port}[/]")
    rprint("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
