"""Template registry - manages project templates."""

import json
import shutil
from pathlib import Path
from jinja2 import Template
from importlib.resources import files

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def list_templates():
    """List available templates with metadata."""
    templates = []
    for tdir in TEMPLATES_DIR.iterdir():
        if tdir.is_dir() and (tdir / "template.json").exists():
            meta = json.loads((tdir / "template.json").read_text())
            templates.append({"name": tdir.name, **meta})
    return sorted(templates, key=lambda t: t.get("name", ""))


def render_template(template_name: str, project_name: str, dest: Path):
    """Render a template into a destination directory."""
    tdir = TEMPLATES_DIR / template_name
    if not tdir.exists():
        raise ValueError(f"Template {template_name} not found")

    meta = json.loads((tdir / "template.json").read_text())
    context = {
        "project_name": project_name,
        "project_slug": project_name.replace("-", "_").replace(" ", "_"),
        "project_kebab": project_name.replace("_", "-").replace(" ", "-"),
        **meta.get("defaults", {}),
    }

    for file in tdir.rglob("*"):
        if file.is_dir() or file.name == "template.json":
            continue

        rel_path = file.relative_to(tdir)
        rel_str = str(rel_path)

        # Template filenames
        if rel_str.endswith(".j2"):
            rel_str = rel_str[:-3]  # strip .j2

        dest_path = dest / rel_str

        # Handle filename templates too
        jinja_file = Template(rel_str)
        dest_path = dest / jinja_file.render(**context)

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        content = file.read_text()
        if file.suffix in (".j2", ".md", ".json", ".yaml", ".yml", ".toml", ".env"):
            tmpl = Template(content)
            content = tmpl.render(**context)

        dest_path.write_text(content)

    # Make scripts executable
    for script in dest.rglob("*.sh"):
        script.chmod(0o755)
