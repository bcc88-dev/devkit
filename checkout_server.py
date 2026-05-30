"""Stripe Checkout server for SaaS Starter Kit sales.

Usage:
  export STRIPE_SECRET_KEY=sk_live_...
  export STRIPE_WEBHOOK_SECRET=whsec_...
  python checkout_server.py
"""

import os
import json
import stripe
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "price_placeholder")
DOMAIN = os.environ.get("DOMAIN", "http://localhost:8080")

HTML_SUCCESS = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Payment Successful</title>
<style>
  body { font-family: system-ui; background: #0f172a; color: #e2e8f0; display: flex;
         justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
  .card { background: #1e293b; padding: 3rem; border-radius: 16px; text-align: center; max-width: 500px; }
  .check { font-size: 4rem; color: #22c55e; margin-bottom: 1rem; }
  .btn { display: inline-block; background: #6366f1; color: white; padding: 12px 32px;
         border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 1.5rem; }
</style></head>
<body>
  <div class="card">
    <div class="check">✓</div>
    <h1>Payment Successful!</h1>
    <p>Your download will start automatically. If it doesn't, click the button below.</p>
    <a href="/download" class="btn">Download SaaS Starter Kit</a>
  </div>
  <script>
    setTimeout(() => { window.location.href = '/download'; }, 3000);
  </script>
</body>
</html>"""

HTML_CANCEL = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Payment Cancelled</title>
<style>
  body { font-family: system-ui; background: #0f172a; color: #e2e8f0; display: flex;
         justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
  .card { background: #1e293b; padding: 3rem; border-radius: 16px; text-align: center; max-width: 500px; }
  .btn { display: inline-block; background: #6366f1; color: white; padding: 12px 32px;
         border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 1.5rem; }
</style></head>
<body>
  <div class="card">
    <h1>Payment Cancelled</h1>
    <p>No charge was made. You can try again whenever you're ready.</p>
    <a href="https://bcc88-dev.github.io/saas-starter-kit/" class="btn">Back to Landing Page</a>
  </div>
</body>
</html>"""


class CheckoutHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/success":
            self.send_html(200, HTML_SUCCESS)
        elif parsed.path == "/cancel":
            self.send_html(200, HTML_CANCEL)
        elif parsed.path == "/download":
            self.serve_file()
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/create-checkout":
            self.create_checkout()
        elif parsed.path == "/webhook":
            self.handle_webhook()
        else:
            self.send_json(404, {"error": "not found"})

    def create_checkout(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        data = json.loads(body) if content_length else {}

        try:
            checkout = stripe.checkout.Session.create(
                line_items=[{"price": PRICE_ID, "quantity": 1}],
                mode="payment",
                success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{DOMAIN}/cancel",
                customer_email=data.get("email"),
                metadata={"product": "saas-starter-kit"},
            )
            self.send_json(200, {"url": checkout.url})
        except Exception as e:
            self.send_json(400, {"error": str(e)})

    def handle_webhook(self):
        payload = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        sig = self.headers.get("Stripe-Signature", "")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig, os.environ.get("STRIPE_WEBHOOK_SECRET", "")
            )
            if event["type"] == "checkout.session.completed":
                session = event["data"]["object"]
                print(f"Payment succeeded: {session.get('id')} — email: {session.get('customer_email')}")
                # In production: send download link via email
            self.send_json(200, {"received": True})
        except stripe.error.SignatureVerificationError:
            self.send_json(400, {"error": "invalid signature"})
        except Exception as e:
            self.send_json(400, {"error": str(e)})

    def serve_file(self):
        zip_path = os.path.join(os.path.dirname(__file__), "landing", "saas-starter.zip")
        if not os.path.exists(zip_path):
            self.send_json(404, {"error": "file not found"})
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", 'attachment; filename="saas-starter-kit.zip"')
        self.end_headers()
        with open(zip_path, "rb") as f:
            self.wfile.write(f.read())

    def send_html(self, status, html):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(html.encode())

    def send_json(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[checkout] {args[0]} {args[1]} {args[2]}")


def main():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), CheckoutHandler)
    print(f"[checkout] Stripe server running on http://0.0.0.0:{port}")
    print(f"[checkout] Set STRIPE_SECRET_KEY, STRIPE_PRICE_ID, and DOMAIN env vars")
    server.serve_forever()


if __name__ == "__main__":
    main()
