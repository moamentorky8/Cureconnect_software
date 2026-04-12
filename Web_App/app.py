import os
from flask import Flask, render_template, request, jsonify
# استيراد الدوال مع محاولة معالجة الخطأ
try:
    from firebase_config import initialize_firebase, get_patient_name
except ImportError as e:
    print(f"❌ Import Error: {e}")

try:
    from firebase_admin import db
except ImportError:
    db = None

app = Flask(__name__)

# محاولة تشغيل الربط مع فايربيز داخل محرك السيرفر
with app.app_context():
    try:
        initialize_firebase()
    except Exception as e:
        print(f"❌ Firebase Boot Error: {e}")

# 1. الصفحة الرئيسية (الداش بورد)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    try:
        # جلب البيانات الأساسية
        name = get_patient_name()
        
        # التأكد أن db شغال
        location = {"lat": 31.2001, "lng": 29.9187} # افتراضي
        medical_info = None

        if db:
            location_ref = db.reference('users/u1/location')
            db_location = location_ref.get()
            if db_location:
                location = db_location
            
            medical_ref = db.reference('users/u1/medical_info')
            medical_info = medical_ref.get()
        
        return render_template('dashboard.html', 
                               user_name=name, 
                               location=location,
                               medical=medical_info)
    except Exception as e:
        return f"حدث خطأ في السيرفر: {str(e)}", 500

# 2. استقبال أمر "صرف الجرعة"
@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    if not db: return jsonify({"success": False, "error": "Database not connected"})
    try:
        data = request.json
        drawer_num = data.get('drawer')
        ref = db.reference(f'device/drawers/d{drawer_num}_open')
        ref.set(True)
        return jsonify({"success": True, "message": f"تم فتح درج {drawer_num}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 3. حالة الـ SOS
@app.route('/get_sos_status')
def get_sos_status():
    if not db: return jsonify({"sos_active": 0})
    try:
        sos_ref = db.reference('device/sos_status')
        loc_ref = db.reference('users/u1/location')
        return jsonify({
            "sos_active": sos_ref.get(),
            "location": loc_ref.get()
        })
    except:
        return jsonify({"sos_active": 0})

# 4. المساعد الصوتي
@app.route('/get_voice_alert')
def get_voice_alert():
    return jsonify({"text": "حان وقت تناول جرعتك الآن"})

if __name__ == '__main__':
    app.run(debug=True)
