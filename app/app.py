# app.py
# Flask app with Jinja templates for:
# - Privacy Policy URL:        GET  /privacy
# - User Data Deletion page:   GET  /data-deletion   (instructions + optional form)
# - Deletion request endpoint: POST /data-deletion/request  (stores request in memory)
#
# Run:
#   pip install flask
#   export FLASK_APP=app.py  # (Windows PowerShell: $env:FLASK_APP="app.py")
#   flask run --host=0.0.0.0 --port=5000
#
# Meta URLs to paste:
#   Privacy Policy URL:   https://YOUR_DOMAIN/privacy
#   User Data Deletion:   https://YOUR_DOMAIN/data-deletion

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = "change-me"  # needed for flash messages

# ---- EDIT THESE ----
BUSINESS_NAME = "Dietlhousing"
CONTACT_EMAIL = "contact@dietlhousing.de"
COUNTRY = "Germany"
RETENTION_PERIOD = "12 months"
# --------------------

# Simple in-memory store (OK for Meta requirement demos; for production use a DB)
DELETION_REQUESTS = []


@app.get("/")
def home():
    return redirect(url_for("privacy"))


@app.get("/privacy")
def privacy():
    return render_template(
        "privacy.html",
        business=BUSINESS_NAME,
        email=CONTACT_EMAIL,
        country=COUNTRY,
        retention=RETENTION_PERIOD,
        last_updated=datetime.utcnow().strftime("%Y-%m-%d"),
    )


@app.get("/data-deletion")
def data_deletion():
    return render_template(
        "data_deletion.html",
        business=BUSINESS_NAME,
        email=CONTACT_EMAIL,
        last_updated=datetime.utcnow().strftime("%Y-%m-%d"),
    )


@app.post("/data-deletion/request")
def data_deletion_request():
    identifier = (request.form.get("identifier") or "").strip()
    channel = (request.form.get("channel") or "").strip()
    notes = (request.form.get("notes") or "").strip()

    if not identifier:
        flash("Please enter the email or phone number you used.", "error")
        return redirect(url_for("data_deletion"))

    req_id = str(uuid.uuid4())
    DELETION_REQUESTS.append(
        {
            "request_id": req_id,
            "identifier": identifier,
            "channel": channel,
            "notes": notes,
            "status": "received",
            "created_utc": datetime.utcnow().isoformat() + "Z",
        }
    )

    flash(f"Request received. Your request ID is {req_id}. We will process it within 30 days.", "success")
    return redirect(url_for("data_deletion"))


# Optional: simple admin view (protect this in real life!)
@app.get("/admin/deletion-requests")
def admin_deletion_requests():
    return render_template(
        "admin_deletion_requests.html",
        business=BUSINESS_NAME,
        requests=list(reversed(DELETION_REQUESTS)),
    )


if __name__ == "__main__":
    app.run(debug=True)