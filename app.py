import os
import requests
from flask import Flask, render_template, request, session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# --- 1. إعدادات الأمان والبيئة ---
# المفتاح السري ضروري لتشفير بيانات الجلسة (Cookies)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "CureConnect_2026_Secure_Key_Deep_Hash")

# مفتاح الـ Web API من إعدادات مشروع فايربيز (ضروري للـ Auth)
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

# --- 2. تهيئة فايربيز (Firebase SDK) ---
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # معالجة مفتاح الخصوصية ليعمل بشكل صحيح على سيرفرات Vercel/Render
            raw_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
            private_key = raw_key.replace("\\n", "\n")
            
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
            print("✅ CureConnect Backend: Firebase Connected Successfully")
        except Exception as e:
            print(f"❌ Firebase Initialization Error: {e}")

initialize_firebase()

# --- 3. المسارات (Routes) ---

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # الاتصال بـ Firebase Auth API
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        try:
            res = requests.post(auth_url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=10)
            data = res.json()
            
            if res.status_code == 200:
                session['user_id'] = data['localId']
                session['email'] = data['email']
                session.permanent = True # الحفاظ على تسجيل الدخول لفترة أطول
                return redirect(url_for('dashboard'))
            else:
                # تخصيص رسائل الخطأ بناءً على رد فايربيز
                error_msg = data.get('error', {}).get('message', '')
                if "EMAIL_NOT_FOUND" in error_msg or "INVALID_PASSWORD" in error_msg:
                    error = "البريد الإلكتروني أو كلمة المرور غير صحيحة."
                else:
                    error = "حدث خطأ أثناء تسجيل الدخول. حاول مجدداً."
        except Exception:
            error = "فشل الاتصال بسيرفر الأمان. تأكد من الإنترنت."
            
    return render_template('login.html', error=error)

# إنشاء حساب جديد
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        try:
            res = requests.post(auth_url, json={"email": email, "password": password, "returnSecureToken": True})
            data = res.json()
            
            if res.status_code == 200:
                session['user_id'] = data['localId']
                session['email'] = email
                # الانتقال لصفحة إكمال البيانات الطبية للمريض
                return redirect(url_for('patient_data'))
            else:
                error = "فشل إنشاء الحساب. ربما البريد مستخدم بالفعل."
        except Exception:
            error = "حدث خطأ غير متوقع."
            
    return render_template('register.html', error=error)

# إكمال بيانات المريض (يتم توجيهه هنا بعد الـ Register)
@app.route('/patient_data', methods=['GET', 'POST'])
def patient_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        # تجميع البيانات من الفورم
        p_data = {
            "full_name": request.form.get('full_name'),
            "age": request.form.get('age'),
            "blood_type": request.form.get('blood_type'),
            "chronic_diseases": request.form.get('chronic_diseases'),
            "emergency_contact": request.form.get('emergency_contact')
        }
        # حفظ في Realtime Database
        db.reference(f'users/{user_id}/profile').set(p_data)
        return redirect(url_for('dashboard'))
        
    return render_template('patient_data.html')

# لوحة التحكم (الداشبورد)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    # جلب بيانات المستخدم لعرضها في الداشبورد
    user_profile = db.reference(f'users/{user_id}/profile').get()
    
    return render_template('dashboard.html', 
                           profile=user_profile if user_profile else {},
                           email=session.get('email'))

# استعادة كلمة المرور
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # كود إرسال إيميل إعادة التعيين عبر فايربيز
        reset_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        requests.post(reset_url, json={"requestType": "PASSWORD_RESET", "email": email})
        flash("تم إرسال تعليمات استعادة كلمة المرور إلى بريدك.")
        return redirect(url_for('login'))
    return render_template('reset_password.html')

# الخدمات
@app.route('/services')
def services():
    return render_template('services.html')

# من نحن
@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear() # مسح كل بيانات الجلسة
    return redirect(url_for('login'))

# تشغيل السيرفر
if __name__ == '__main__':
    app.run(debug=True, port=5000)
