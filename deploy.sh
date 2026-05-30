#!/usr/bin/env bash
# Deploy the SaaS Starter landing page
# Usage: bash deploy.sh [github-pages|vercel|serve]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LANDING_DIR="$SCRIPT_DIR/landing"
REPO_NAME="saas-starter"

serve_local() {
  echo " [*] Serving landing page at http://localhost:8081"
  echo "    Press Ctrl+C to stop"
  cd "$LANDING_DIR"
  python3 -m http.server 8081
}

github_pages() {
  echo " [*] Deploying to GitHub Pages..."
  
  # Check if gh CLI is available
  if ! command -v gh &>/dev/null; then
    echo " [!] gh CLI not found. Install it first: https://cli.github.com/"
    exit 1
  fi

  # Check if logged in
  if ! gh auth status &>/dev/null; then
    echo " [!] Not logged into GitHub. Run: gh auth login"
    exit 1
  fi

  # Create repo if it doesn't exist
  if ! gh repo view "$REPO_NAME" &>/dev/null; then
    echo " [+] Creating GitHub repo: $REPO_NAME"
    gh repo create "$REPO_NAME" --public --description "SaaS Starter Kit - Next.js + Supabase + Stripe Boilerplate"
  fi

  # Init git and push
  cd "$LANDING_DIR"
  if [ ! -d .git ]; then
    git init
    git checkout -b main
  fi
  git add .
  git commit -m "Initial landing page" 2>/dev/null || true
  git remote add origin "https://github.com/$(gh api user -q .login)/$REPO_NAME.git" 2>/dev/null || true
  git push -u origin main --force

  # Enable GitHub Pages
  gh api "repos/$(gh api user -q .login)/$REPO_NAME/pages" \
    -X POST \
    -f source.branch=main \
    -f source.path=/ 2>/dev/null || true

  echo ""
  echo " [✓] Deployed! Your landing page is live at:"
  echo "     https://$(gh api user -q .login).github.io/$REPO_NAME"
}

case "${1:-serve}" in
  serve)
    serve_local
    ;;
  github-pages)
    github_pages
    ;;
  vercel)
    echo " [*] Deploying to Vercel..."
    npx vercel --cwd "$LANDING_DIR" --yes
    ;;
  *)
    echo "Usage: $0 [serve|github-pages|vercel]"
    exit 1
    ;;
esac
