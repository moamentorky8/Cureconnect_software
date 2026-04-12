import os
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    """
    تهيئة الاتصال بفايربيز بشكل آمن تماماً بدون كتابة مفاتيح في الكود.
    سيتم جلب البيانات من Environment Variables في Vercel.
    """
    # التأكد أن التطبيق لم يتم تهيئته مسبقاً (مهم جداً لبيئة Vercel)
    if not firebase_admin._apps:
        try:
            # تجميع بيانات المفتاح من متغيرات البيئة المحمية
            # لاحظ أننا نستخدم os.getenv لجلب القيم
            firebase_creds = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            # تسجيل الدخول باستخدام قاموس البيانات بدلاً من ملف JSON خارجي
            cred = credentials.Certificate(firebase_creds)
            
            firebase_admin.initialize_app(cred, {
                'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
            })
            print("Connected to CureConnect Firebase Securely!")
            
        except Exception as e:
            print(f"Firebase Initialization Error: {e}")

def get_patient_name():
    """جلب اسم المريض بشكل آمن"""
    try:
        initialize_firebase()
        ref = db.reference('users/u1/name')
        name = ref.get()
        return name if name else "عميل جديد"
    except Exception as e:
        print(f"Error: {e}")
        return "خطأ في الاتصال"
