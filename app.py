import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyrebase
from dotenv import load_dotenv

load_dotenv(".env.local")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "cureconnect-dev-secret-change-in-prod")

# ── Firebase configuration ──────────────────────────────────────────────────
firebase_config = {
    "apiKey":            os.getenv("FIREBASE_API_KEY"),
    "authDomain":        os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL":       os.getenv("FIREBASE_DATABASE_URL"),
    "projectId":         os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket":     os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId":             os.getenv("FIREBASE_APP_ID"),
}

firebase  = pyrebase.initialize_app(firebase_config)
auth_fb   = firebase.auth()
db        = firebase.database()

# ── Auth helpers ────────────────────────────────────────────────────────────
def is_logged_in():
    return "user_id" in session and "id_token" in session


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_logged_in():
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if is_logged_in():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# ── Login ────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        try:
            user = auth_fb.sign_in_with_email_and_password(email, password)
            session["user_id"]  = user["localId"]
            session["id_token"] = user["idToken"]
            session["email"]    = email

            # Fetch display name from Firebase if stored
            user_data = db.child("users").child(user["localId"]).child("profile").get(user["idToken"]).val()
            session["display_name"] = (user_data or {}).get("name", email.split("@")[0])

            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            error_msg = str(e)
            if "INVALID_PASSWORD" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
                flash("Invalid email or password.", "danger")
            elif "TOO_MANY_ATTEMPTS" in error_msg:
                flash("Too many failed attempts. Please try again later.", "danger")
            else:
                flash("Login failed. Please check your credentials.", "danger")

    return render_template("login.html")


# ── Register ─────────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if is_logged_in():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email     = request.form.get("email", "").strip()
        password  = request.form.get("password", "")
        password2 = request.form.get("confirm_password", "")

        if password != password2:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        try:
            user = auth_fb.create_user_with_email_and_password(email, password)
            session["user_id"]      = user["localId"]
            session["id_token"]     = user["idToken"]
            session["email"]        = email
            session["display_name"] = email.split("@")[0]
            session["new_user"]     = True          # flag: profile not yet completed

            flash("Account created! Please complete your profile.", "success")
            # Redirect new users straight to patient data form
            return redirect(url_for("patient_data"))

        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                flash("An account with that email already exists.", "danger")
            elif "WEAK_PASSWORD" in error_msg:
                flash("Password is too weak. Use at least 6 characters.", "danger")
            else:
                flash("Registration failed. Please try again.", "danger")

    return render_template("register.html")


# ── Patient Data ──────────────────────────────────────────────────────────────
@app.route("/patient_data", methods=["GET", "POST"])
@login_required
def patient_data():
    user_id  = session["user_id"]
    id_token = session["id_token"]

    if request.method == "POST":
        medical_info = {
            "name":          request.form.get("name", "").strip(),
            "age":           request.form.get("age", "").strip(),
            "blood_type":    request.form.get("blood_type", "").strip(),
            "gender":        request.form.get("gender", "").strip(),
            "phone":         request.form.get("phone", "").strip(),
            "address":       request.form.get("address", "").strip(),
            "medical_notes": request.form.get("medical_notes", "").strip(),
            "allergies":     request.form.get("allergies", "").strip(),
            "medications":   request.form.get("medications", "").strip(),
            "medical_status": "Profile Complete",
        }

        profile = {
            "name":  medical_info["name"],
            "email": session.get("email", ""),
        }

        try:
            # Save under users/{user_id}/medical_info
            db.child("users").child(user_id).child("medical_info").set(medical_info, id_token)
            # Also store a slim profile node for quick reads
            db.child("users").child(user_id).child("profile").set(profile, id_token)

            session["display_name"] = medical_info["name"] or session["display_name"]
            session.pop("new_user", None)

            flash("Profile saved successfully!", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error saving data: {str(e)}", "danger")

    # Pre-fill form if data already exists
    existing = None
    try:
        existing = db.child("users").child(user_id).child("medical_info").get(id_token).val()
    except Exception:
        pass

    return render_template("patient_data.html", data=existing or {})


# ── Dashboard ─────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user_id  = session["user_id"]
    id_token = session["id_token"]

    medical_info = {}
    try:
        medical_info = db.child("users").child(user_id).child("medical_info").get(id_token).val() or {}
    except Exception:
        pass

    user_name      = medical_info.get("name") or session.get("display_name", "User")
    medical_status = medical_info.get("medical_status", "Incomplete – please complete your profile")

    return render_template(
        "dashboard.html",
        user_name=user_name,
        medical_status=medical_status,
        medical_info=medical_info,
        email=session.get("email", ""),
    )


# ── Reset Password ────────────────────────────────────────────────────────────
@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        try:
            auth_fb.send_password_reset_email(email)
            flash("Password reset email sent. Check your inbox.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("Could not send reset email. Check the address and try again.", "danger")

    return render_template("reset_password.html")


# ── Logout ────────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("You've been logged out.", "info")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
