import os
from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

# --- دالة تهيئة فايربيز (مباشرة جوه app.py لضمان التشغيل) ---
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

# تشغيل التهيئة
initialize_firebase_direct()

# --- المسارات (Routes) ---

@app.route('/')
@app.route('/dashboard')
def dashboard():
    try:
        # جلب الاسم مباشرة
        name = "مستخدم CureConnect"
        try:
            name_ref = db.reference('users/u1/name').get()
            if name_ref: name = name_ref
        except: pass

        location = {"lat": 31.2001, "lng": 29.9187}
        medical_info = None

        # جلب البيانات الحية
        try:
            loc_ref = db.reference('users/u1/location').get()
            if loc_ref: location = loc_ref
            
            med_ref = db.reference('users/u1/medical_info').get()
            if med_ref: medical_info = med_ref
        except: pass
        
        return render_template('dashboard.html', 
                               user_name=name, 
                               location=location,
                               medical=medical_info)
    except Exception as e:
        return f"🚨 Error: {str(e)}", 500

@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    try:
        data = request.json
        drawer_num = data.get('drawer')
        db.reference(f'device/drawers/d{drawer_num}_open').set(True)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
