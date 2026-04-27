import os
import requests
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# --- 1. إعدادات الأمان والمفاتيح ---
# استخدام قيمة افتراضية لتجنب توقف السيرفر إذا لم يجد المفتاح
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "CureConnect_2026_Secure_Key")
FIREBASE_WEB_API_KEY = os.environ.get("FIREBASE_WEB_API_KEY")

# --- 2. تهيئة فايربيز (الإصلاح الجذري لخطأ 500) ---
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            # الحل النهائي لمشكلة السطر الجديد في الـ Private Key
            raw_private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
            private_key = raw_private_key.replace("\\n", "\n")
            
            # التأكد من وجود البيانات الأساسية قبل المحاولة
            project_id = os.environ.get("FIREBASE_PROJECT_ID")
            client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
            database_url = os.environ.get("FIREBASE_DATABASE_URL")

            if not all([project_id, private_key, client_email, database_url]):
                print("⚠️ Missing Firebase Environment Variables!")
                return

            creds_dict = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": private_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print("🚀 CureConnect Engine: Connected Successfully!")
        except Exception as e:
            # طباعة الخطأ في الـ Logs يساعدك جداً في Vercel لمعرفة السبب الحقيقي
            print(f"⚠️ Firebase Initialization Error: {str(e)}")

initialize_firebase()

def is_logged_in():
    return 'user_id' in session

# --- 3. قتالة الـ .html والـ index.html (إصلاح مسارات التنقل) ---

@app.route('/index.html')
@app.route('/index')
def home_redirect():
    return redirect(url_for('index'), code=301)

@app.route('/about-us.html')
def about_us_redirect():
    return redirect(url_for('about_us'), code=301)

@app.route('/services.html')
def services_redirect():
    return redirect(url_for('services'), code=301)

@app.route('/login.html')
def login_redirect():
    return redirect(url_for('login'), code=301)

# --- 4. المسارات الأساسية ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/about-us')
def about_us():
    return render_template('about-us.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in(): return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        try:
            # إضافة timeout لتجنب انتظار السيرفر طويلاً (مما يسبب خطأ 504 أو 500)
            response = requests.post(auth_url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=7)
            data = response.json()
            if response.status_code == 200:
                session.permanent = True
                session['user_id'] = data['localId']
                session['email'] = data['email']
                return redirect(url_for('dashboard'))
            else:
                error = "بيانات الدخول غير صحيحة."
        except Exception:
            error = "فشل الاتصال بخادم المصادقة."
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in(): return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
        try:
            res = requests.post(auth_url, json={"email": email, "password": password, "returnSecureToken": True}, timeout=7)
            if res.status_code == 200:
                data = res.json()
                session['user_id'] = data['localId']
                session['email'] = email
                return redirect(url_for('patient_data'))
            else:
                error = "فشل إنشاء الحساب، قد يكون البريد مستخدم بالفعل."
        except Exception:
            error = "خطأ في الشبكة."
    return render_template('register.html', error=error)

@app.route('/patient_data')
def patient_data():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('patient_data.html')

@app.route('/save_patient_data', methods=['POST'])
def save_patient_data():
    if not is_logged_in(): return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        # تأكد من أن الـ DatabaseURL مهيأ بشكل صحيح في initialize_firebase
        data = {
            "name": request.form.get('name'),
            "email": session['email'],
            "location": {"lat": 31.2001, "lng": 29.9187},
            "medical_info": {
                "age": request.form.get('age'),
                "blood_type": request.form.get('blood_type'),
                "phone": request.form.get('phone'),
                "chronic_diseases": [d.strip() for d in request.form.get('diseases', '').split(',') if d.strip()]
            }
        }
        db.reference(f'users/{user_id}').set(data)
        return redirect(url_for('dashboard'))
    except Exception as e:
        # بدلاً من كراش للسيرفر، نعرض الخطأ بشكل بسيط أو نسجله
        print(f"Database Save Error: {str(e)}")
        return "حدث خطأ أثناء حفظ البيانات، يرجى المحاولة لاحقاً."

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        user_data = db.reference(f'users/{user_id}').get()
        if not user_data:
            return redirect(url_for('patient_data'))
        
        return render_template('dashboard.html', 
                               user_name=user_data.get('name', 'User'), 
                               user_email=session['email'],
                               location=user_data.get('location', {"lat": 31.2, "lng": 29.9}),
                               medical=user_data.get('medical_info', {}))
    except Exception:
        return render_template('dashboard.html', error="فشل مزامنة البيانات")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # تأكد من قراءة البورت من البيئة ليتوافق مع Vercel/Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
