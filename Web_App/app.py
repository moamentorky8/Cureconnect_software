import os
from flask import Flask, render_template, request, jsonify
from firebase_config import initialize_firebase, get_patient_name
from firebase_admin import db

app = Flask(__name__)

# تشغيل الربط مع فايربيز (بيقرأ من الـ Env Variables اللي حطيتها في فيرسيل)
initialize_firebase()

# 1. الصفحة الرئيسية (الداش بورد)
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # جلب اسم العميل الحقيقي من Firebase
    name = get_patient_name()
    # إرسال الاسم للـ HTML عشان يظهر "أهلاً، فلان"
    return render_template('dashboard.html', user_name=name)

# 2. استقبال أمر "صرف الجرعة" من الـ JavaScript
@app.route('/update_drawer', methods=['POST'])
def update_drawer():
    try:
        data = request.json
        drawer_num = data.get('drawer')
        
        # تحديث قيمة drawer1_open في الفايربيز لتصبح true
        ref = db.reference(f'device/drawer{drawer_num}_open')
        ref.set(True)
        
        return jsonify({"success": True, "message": "تم إرسال الأمر للجهاز"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 3. التأكد من حالة الـ SOS (بيستخدمها الـ JS للمراقبة اللحظية)
@app.route('/get_sos_status')
def get_sos_status():
    try:
        ref = db.reference('device/sos_status')
        status = ref.get()
        return jsonify({"sos_active": status})
    except:
        return jsonify({"sos_active": 0})

# 4. المساعد الصوتي (اختياري - بيرجع نص التنبيه)
@app.route('/get_voice_alert')
def get_voice_alert():
    # هنا ممكن نخليه يرجع جملة متغيرة بناءً على الوقت
    return jsonify({"text": "حان وقت تناول جرعتك الآن"})

if __name__ == '__main__':
    app.run(debug=True)
