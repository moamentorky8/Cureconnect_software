import os
import sys
from flask import Flask, render_template, request, jsonify

# 1. إجبار السيرفر على رؤية المجلد الرئيسي (Root) حيث يوجد firebase_config.py
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

# 2. استيراد الدوال (بدون try عشان لو مش موجودة السيرفر يدي Error واضح وصريح)
from firebase_config import initialize_firebase, get_patient_name
from firebase_admin import db

app = Flask(__name__)

# 3. تهيئة الاتصال بفايربيز
try:
    initialize_firebase()
    print("✅ CureConnect: Firebase connected via app.py")
except Exception as e:
    print(f"❌ Firebase Boot Error: {e}")

# --- المسارات (Routes) ---

@app.route('/')
@app.route('/dashboard')
def dashboard():
    try:
        # جلب البيانات الأساسية
        name = get_patient_name()
        
        # إحداثيات افتراضية (الإسكندرية)
        location = {"lat": 31.2001, "lng": 29.9187}
        medical_info = None

        # جلب البيانات الحية من الداتابيز
        if db:
            loc_ref = db.reference('users/u1/location')
            db_loc = loc_ref.get()
            if db_loc: 
                location = db_loc
            
            med_ref = db.reference('users/u1/medical_info')
            medical_info = med_ref.get()
        
        return render_template('dashboard.html', 
                               user_name=name, 
                               location=location,
                               medical=medical_info)
    except Exception as e:
        # في حالة وجود خطأ في الرندر أو البيانات، اطبعه بوضوح
        return f"<h1 style='color:red'>Server Error:</h1><p>{str(e)}</p>", 500

@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    try:
        data = request.json
        drawer_num = data.get('drawer')
        if db:
            db.reference(f'device/drawers/d{drawer_num}_open').set(True)
            return jsonify({"success": True, "message": f"تم فتح درج {drawer_num}"})
        return jsonify({"success": False, "error": "Database not connected"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/get_sos_status')
def get_sos_status():
    try:
        if db:
            sos = db.reference('device/sos_status').get()
            loc = db.reference('users/u1/location').get()
            return jsonify({"sos_active": sos, "location": loc})
        return jsonify({"sos_active": 0})
    except:
        return jsonify({"sos_active": 0})

@app.route('/get_voice_alert')
def get_voice_alert():
    return jsonify({"text": "حان وقت تناول جرعتك الآن"})

if __name__ == '__main__':
    app.run(debug=True)
