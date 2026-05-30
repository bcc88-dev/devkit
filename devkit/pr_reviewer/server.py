"""AI PR Review Server - receives GitHub webhooks and posts AI reviews."""

import json
import hmac
import hashlib
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from pathlib import Path

WEBHOOK_SECRET = "devkit-secret-change-in-prod"


class PRReviewHandler(BaseHTTPRequestHandler):
    """HTTP handler for GitHub webhook events."""

    def _verify_signature(self, payload_body, signature_header):
        """Verify GitHub webhook signature."""
        if not signature_header:
            return False
        expected = hmac.new(
            WEBHOOK_SECRET.encode(),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature_header)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        signature = self.headers.get("X-Hub-Signature-256", "")

        if not self._verify_signature(body, signature):
            self._respond(403, {"error": "Invalid signature"})
            return

        event = self.headers.get("X-GitHub-Event", "")
        payload = json.loads(body)

        if self.path == "/github/webhook":
            if event == "pull_request" and payload.get("action") in ("opened", "synchronize"):
                self._handle_pr(payload)
            else:
                self._respond(200, {"status": "ignored", "event": event, "action": payload.get("action")})
        else:
            self._respond(404, {"error": "Not found"})

    def _handle_pr(self, payload):
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {}).get("full_name", "unknown")
        pr_number = pr.get("number")
        pr_title = pr.get("title", "untitled")
        pr_url = pr.get("html_url", "")
        pr_diff_url = pr.get("diff_url", "")

        print(f"  PR #{pr_number} - {pr_title}")
        print(f"  {repo}")
        print(f"  Diff: {pr_diff_url}")

        # In production, you'd run AI analysis here
        # For now, we acknowledge receipt
        self._respond(200, {
            "status": "received",
            "repo": repo,
            "pr": pr_number,
            "message": f"AI review queued for PR #{pr_number}"
        })

    def _respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[PR-Reviewer] {args[0]}")


def serve(host="0.0.0.0", port=8080):
    """Start the PR review webhook server."""
    server = HTTPServer((host, port), PRReviewHandler)
    print(f"PR Review Server running on http://{host}:{port}")
    print(f"  Webhook endpoint: http://{host}:{port}/github/webhook")
    print("  Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.server_close()


if __name__ == "__main__":
    serve()
