import os
from flask import Flask, render_template, request, jsonify
from firebase_config import initialize_firebase, get_patient_name
from firebase_admin import db

app = Flask(__name__)

# تشغيل الربط مع فايربيز
initialize_firebase()

# 1. الصفحة الرئيسية (الداش بورد)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # جلب البيانات الأساسية من Firebase
    name = get_patient_name()
    
    # جلب إحداثيات الموقع (GPS)
    location_ref = db.reference('users/u1/location')
    location = location_ref.get()
    
    # لو مفيش لوكيشن في الداتابيز، هنحط لوكيشن افتراضي (مثلاً الإسكندرية)
    if not location:
        location = {"lat": 31.2001, "lng": 29.9187}
        
    # جلب البيانات الطبية (Patient Info)
    medical_ref = db.reference('users/u1/medical_info')
    medical_info = medical_ref.get()
    
    return render_template('dashboard.html', 
                           user_name=name, 
                           location=location,
                           medical=medical_info)

# 2. استقبال أمر "صرف الجرعة" لـ 8 أدراج
@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    try:
        data = request.json
        drawer_num = data.get('drawer') # ده رقم من 1 لـ 8
        
        # تحديث الدرج المحدد في الفايربيز
        ref = db.reference(f'device/drawers/d{drawer_num}_open')
        ref.set(True)
        
        return jsonify({"success": True, "message": f"تم فتح درج {drawer_num}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 3. التأكد من حالة الـ SOS وموقع المريض اللحظي
@app.route('/get_sos_status')
def get_sos_status():
    try:
        # بنجيب حالة الـ SOS واللوكيشن مع بعض عشان نحدث الخريطة لو المريض اتحرك
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
