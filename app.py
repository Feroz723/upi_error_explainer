"""
UPI & Banking Error Explainer - MVP
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session
from utils.error_lookup import get_error_by_input, get_error_by_slug, get_all_errors, get_related_errors_smart
from utils.ai_handler import get_ai_explanation

app = Flask(__name__)
app.secret_key = "upi-error-explainer-session-key"

# Last updated date for error database (update when errors.json changes)
LAST_UPDATED = "February 2026"


@app.route("/")
def index():
    """Home page with search box."""
    errors = get_all_errors()
    return render_template("index.html", errors=errors)


@app.route("/search", methods=["GET", "POST"])
def search():
    """Handle search form submission."""
    user_input = ""
    
    if request.method == "POST":
        user_input = request.form.get("error_input", "")
    else:
        user_input = request.args.get("error_input", "")
    
    if not user_input.strip():
        return redirect(url_for("index"))
    
    # Store original input in session for AI fallback
    session["last_search"] = user_input.strip()
    
    slug, error_data = get_error_by_input(user_input)
    
    if slug:
        return redirect(url_for("error_page", error_slug=slug))
    else:
        return redirect(url_for("error_page", error_slug="not-found"))


@app.route("/error/<error_slug>")
def error_page(error_slug):
    """Display explanation for a specific error."""
    
    # URL canonicalization: redirect uppercase to lowercase
    if error_slug != error_slug.lower():
        return redirect(url_for("error_page", error_slug=error_slug.lower()), code=301)
    
    # Handle not-found with AI fallback
    if error_slug == "not-found":
        # Try AI explanation using last search
        user_input = session.get("last_search", "")
        
        if user_input:
            ai_data = get_ai_explanation(user_input)
            if ai_data:
                # AI found an explanation
                ai_data["code"] = user_input.upper()
                related = get_related_errors_smart(error_slug)
                return render_template("error.html", error=ai_data, slug=error_slug, ai_generated=True, related_errors=related, last_updated=LAST_UPDATED)
        
        # No AI result - show 404
        return render_template("404.html", searched=True), 404
    
    # Try static lookup
    error_data = get_error_by_slug(error_slug)
    
    if error_data:
        related = get_related_errors_smart(error_slug)
        return render_template("error.html", error=error_data, slug=error_slug, ai_generated=False, related_errors=related, last_updated=LAST_UPDATED)
    else:
        # Unknown slug - try AI
        ai_data = get_ai_explanation(error_slug)
        if ai_data:
            ai_data["code"] = error_slug.upper()
            related = get_related_errors_smart(error_slug)
            return render_template("error.html", error=ai_data, slug=error_slug, ai_generated=True, related_errors=related, last_updated=LAST_UPDATED)
        
        return render_template("404.html", searched=False), 404


@app.route("/feedback")
def feedback():
    """Handle feedback links (no-op for now, just redirect back)."""
    helpful = request.args.get("ok", "")
    error_slug = request.args.get("error", "")
    
    # Log to console (future: store in database)
    if helpful == "1":
        print(f"[FEEDBACK] Helpful: {error_slug}")
    elif helpful == "0":
        print(f"[FEEDBACK] Not helpful: {error_slug}")
    
    # Redirect back to error page or home
    if error_slug and error_slug != "not-found":
        return redirect(url_for("error_page", error_slug=error_slug))
    return redirect(url_for("index"))


@app.route("/robots.txt")
def robots():
    """Serve robots.txt for crawlers."""
    return "User-agent: *\nAllow: /\n", 200, {"Content-Type": "text/plain"}


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template("404.html", searched=False), 404


if __name__ == "__main__":
    app.run(debug=True)
