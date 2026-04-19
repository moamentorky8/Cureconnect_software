import os
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# --- 1. إعدادات الأمان والمفاتيح ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "CureConnect_2026_Secure_Key")
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

# --- 2. تهيئة قاعدة بيانات فايربيز (Firebase Admin SDK) ---
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # معالجة المفتاح الخاص ليعمل على سيرفرات Vercel بشكل صحيح
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

# تنفيذ عملية التهيئة عند بدء التشغيل
initialize_firebase()

# --- 3. الدوال المساعدة (Helpers) ---
def is_logged_in():
    """التحقق من حالة تسجيل الدخول"""
    return 'user_id' in session

# --- 4. المسارات الأساسية (Core Routes) ---

@app.route('/')
def index():
    """الصفحة الرئيسية - يتم تحويل المستخدم للداشبورد لو مسجل دخول"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/about-us')
def about_us():
    """صفحة من نحن - المسار الصافي"""
    return render_template('about-us.html')

@app.route('/services')
def services():
    """صفحة الخدمات - المسار الصافي"""
    return render_template('services.html')

# --- 5. نظام المصادقة (Authentication System) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول باستخدام Firebase Auth"""
    if is_logged_in(): 
        return redirect(url_for('dashboard'))
        
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
                session['user_name'] = data.get('displayName', 'User')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Email or Password. Please try again."
        except Exception as e:
            error = f"Connection Error: {str(e)}"
            
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """إنشاء حساب جديد"""
    if is_logged_in(): 
        return redirect(url_for('dashboard'))
        
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
                return redirect(url_for('patient_data'))
            else:
                error = data.get('error', {}).get('message', 'Registration Failed.')
        except Exception:
            error = "Network Error. Please check your connection."
            
    return render_template('register.html', error=error)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """استعادة كلمة المرور"""
    message, error = None, None
    if request.method == 'POST':
        email = request.form.get('email')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        payload = {"requestType": "PASSWORD_RESET", "email": email}
        try:
            res = requests.post(auth_url, json=payload, timeout=10)
            if res.status_code == 200:
                message = "A password recovery link has been sent to your email."
            else:
                error = "Email address not found in our records."
        except:
            error = "Network error. Please try again later."
    return render_template('reset_password.html', message=message, error=error)

# --- 6. إدارة بيانات المريض (Patient Management) ---

@app.route('/patient_data')
def patient_data():
    """شاشة إدخال البيانات الأولية"""
    if not is_logged_in(): 
        return redirect(url_for('login'))
    return render_template('patient_data.html')

@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    """حفظ بيانات المريض في Realtime Database"""
    if not is_logged_in(): 
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        name = request.form.get('name')
        age = request.form.get('age')
        blood_type = request.form.get('blood_type')
        phone = request.form.get('phone')
        diseases = request.form.get('diseases', '').split(',')
        
        # هيكل البيانات في فايربيز
        patient_record = {
            "name": name,
            "email": session['email'],
            "location": {"lat": 31.2001, "lng": 29.9187}, # إحداثيات افتراضية للإسكندرية
            "medical_info": {
                "age": age,
                "blood_type": blood_type,
                "phone": phone,
                "chronic_diseases": [d.strip() for d in diseases if d.strip()]
            },
            "sos_active": False
        }
        
        db.reference(f'users/{user_id}').set(patient_record)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Database Sync Error: {str(e)}"

# --- 7. لوحة التحكم (User Dashboard) ---

@app.route('/dashboard')
def dashboard():
    """عرض بيانات المستخدم وحالة الجهاز"""
    if not is_logged_in(): 
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    try:
        user_data = db.reference(f'users/{user_id}').get()
        
        # لو المستخدم جديد ومالوش بيانات، نرجعه لشاشة البيانات
        if not user_data:
            return redirect(url_for('patient_data'))
        
        return render_template('dashboard.html', 
                               user_name=user_data.get('name', 'User'), 
                               user_email=session['email'],
                               location=user_data.get('location', {"lat": 31.2, "lng": 29.9}),
                               medical=user_data.get('medical_info', {}))
    except Exception as e:
        print(f"Dashboard Load Error: {e}")
        return render_template('dashboard.html', error="Error fetching data from server.")

# --- 8. واجهات البرمجة (Internal APIs) ---

@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    """فتح درج معين من خلال الموقع"""
    if not is_logged_in(): 
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        drawer_num = request.json.get('drawer')
        # تحديث حالة الدرج في الجهاز المرتبط بالمستخدم
        db.reference(f'device/{session["user_id"]}/drawers/d{drawer_num}_open').set(True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_sos_status')
def get_sos_status():
    """جلب حالة الطوارئ والموقع الحالي"""
    if not is_logged_in(): 
        return jsonify({"sos_active": False})
    try:
        user_id = session['user_id']
        data = db.reference(f'users/{user_id}/sos_active').get()
        location = db.reference(f'users/{user_id}/location').get()
        return jsonify({"sos_active": data, "location": location})
    except:
        return jsonify({"sos_active": False})

# --- 9. إنهاء الجلسة (Session End) ---

@app.route('/logout')
def logout():
    """تسجيل الخروج ومسح الـ Session"""
    session.clear()
    return redirect(url_for('login'))

# --- 10. تشغيل التطبيق ---
if __name__ == '__main__':
    # تشغيل السيرفر على البورت المحدد من البيئة أو 5000 افتراضيًا
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
