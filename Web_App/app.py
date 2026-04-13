import os
import requests # تأكد من وجودها في requirements.txt
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)
# مفتاح سري لتشفير الجلسات (Sessions)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "cure_connect_secure_key_2026")

# مفتاح الـ Web API من Firebase (ضروري لعملية الـ Auth)
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

# --- دالة تهيئة فايربيز (نفس الكود اللي شغال عندك بدون تغيير) ---
def initialize_firebase_direct():
    if not firebase_admin._apps:
        try:
            private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            
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
            print("✅ Firebase Connected Successfully!")
        except Exception as e:
            print(f"❌ Firebase Error: {e}")

initialize_firebase_direct()

# --- دالة مساعدة للتأكد من تسجيل الدخول ---
def is_logged_in():
    return 'user_id' in session

# --- المسارات (Routes) ---

# 1. تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # التواصل مع Firebase Auth API
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            response = requests.post(auth_url, json=payload)
            data = response.json()
            if response.status_code == 200:
                session['user_id'] = data['localId']
                session['email'] = data['email']
                return redirect(url_for('dashboard'))
            else:
                error = "خطأ في البريد الإلكتروني أو كلمة المرور"
        except:
            error = "حدث خطأ في الاتصال بالخادم"
            
    return render_template('login.html', error=error)

# 2. إنشاء حساب جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('dashboard'))
        
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        
        try:
            response = requests.post(auth_url, json=payload)
            data = response.json()
            if response.status_code == 200:
                session['user_id'] = data['localId']
                session['email'] = data['email']
                return redirect(url_for('dashboard'))
            else:
                error = "فشل إنشاء الحساب (ربما الإيميل مسجل مسبقاً)"
        except:
            error = "خطأ في الاتصال"
            
    return render_template('register.html', error=error)

# 3. استعادة كلمة المرور
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    message = None
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        
        try:
            response = requests.post(auth_url, json=payload)
            if response.status_code == 200:
                message = "تم إرسال رابط تعيين كلمة المرور إلى بريدك."
            else:
                error = "البريد غير مسجل لدينا"
        except:
            error = "خطأ في الشبكة"
    return render_template('reset_password.html', message=message, error=error)

# 4. تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 5. الداش بورد (محدثة لتجلب بيانات المستخدم الحالي)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_email = session['email']
    
    try:
        # جلب البيانات من المسار الخاص بهذا اليوزر
        name = "مستخدم جديد"
        location = {"lat": 31.2001, "lng": 29.9187}
        medical_info = None

        user_ref = db.reference(f'users/{user_id}')
        data = user_ref.get()
        
        if data:
            name = data.get('name', "مستخدم جديد")
            location = data.get('location', location)
            medical_info = data.get('medical_info', None)
        
        return render_template('dashboard.html', 
                               user_name=name, 
                               user_email=user_email,
                               location=location,
                               medical=medical_info)
    except Exception as e:
        return f"🚨 Error: {str(e)}", 500

# 6. تحديث الأدراج (API)
@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    if not is_logged_in(): return jsonify({"success": False}), 401
    try:
        data = request.json
        drawer_num = data.get('drawer')
        # تخزين الطلب تحت معرف المستخدم الحالي
        db.reference(f'device/{session["user_id"]}/drawers/d{drawer_num}_open').set(True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
