import os
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# 1. تكوين المفاتيح السرية
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "CureConnect_2026_Secure_Key")
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

# 2. تهيئة فايربيز (النسخة الاحترافية لـ Vercel)
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")
            creds_dict = {
                "type": "service_account",
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": private_key,
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.environ.get("FIREBASE_DATABASE_URL")
            })
            print("🚀 CureConnect Engine: Connected Successfully!")
        except Exception as e:
            print(f"⚠️ Firebase Initialization Error: {e}")

initialize_firebase()

# --- Helpers ---
def is_logged_in():
    return 'user_id' in session

# --- Routes ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# 1. تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in(): return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            response = requests.post(auth_url, json=payload, timeout=10)
            data = response.json()
            if response.status_code == 200:
                session.permanent = True
                session['user_id'] = data['localId']
                session['email'] = data['email']
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Email or Password."
        except:
            error = "Connection Timeout."
    return render_template('login.html', error=error)

# 2. إنشاء حساب جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in(): return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        try:
            response = requests.post(auth_url, json=payload, timeout=10)
            data = response.json()
            if response.status_code == 200:
                session['user_id'] = data['localId']
                session['email'] = email
                # توجيه المستخدم لصفحة إدخال بيانات المريض فوراً بعد التسجيل
                return redirect(url_for('patient_data'))
            else:
                error = data.get('error', {}).get('message', 'Registration Failed.')
        except:
            error = "Network Error."
    return render_template('register.html', error=error)

# 3. شاشة إدخال بيانات المريض (لأول مرة)
@app.route('/patient_data')
def patient_data():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('patient_data.html')

# 4. حفظ بيانات المريض في الـ Database
@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    if not is_logged_in(): return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        name = request.form.get('name')
        age = request.form.get('age')
        blood_type = request.form.get('blood_type')
        phone = request.form.get('phone')
        diseases = request.form.get('diseases', '').split(',')
        
        db.reference(f'users/{user_id}').set({
            "name": name,
            "email": session['email'],
            "location": {"lat": 31.2001, "lng": 29.9187}, # موقع افتراضي (Alexandria)
            "medical_info": {
                "age": age,
                "blood_type": blood_type,
                "phone": phone,
                "chronic_diseases": [d.strip() for d in diseases if d.strip()]
            }
        })
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Database Error: {e}"

# 5. استعادة كلمة المرور
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    message, error = None, None
    if request.method == 'POST':
        email = request.form.get('email')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        try:
            res = requests.post(auth_url, json=payload, timeout=10)
            if res.status_code == 200:
                message = "Recovery link sent to your email!"
            else:
                error = "Email not found."
        except:
            error = "Network error."
    return render_template('reset_password.html', message=message, error=error)

# 6. الداشبورد (عرض البيانات والتحكم)
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        user_data = db.reference(f'users/{user_id}').get()
        if not user_data:
            # لو الحساب لسه ملوش داتا يروح يكملها
            return redirect(url_for('patient_data'))
        
        return render_template('dashboard.html', 
                               user_name=user_data.get('name'), 
                               user_email=session['email'],
                               location=user_data.get('location'),
                               medical=user_data.get('medical_info'))
    except:
        return render_template('dashboard.html', error="Sync Error")

# 7. API: تحكم الأدراج (ESP32 Interface)
@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    if not is_logged_in(): return jsonify({"success": False}), 401
    try:
        drawer_num = request.json.get('drawer')
        db.reference(f'device/{session["user_id"]}/drawers/d{drawer_num}_open').set(True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 8. تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)