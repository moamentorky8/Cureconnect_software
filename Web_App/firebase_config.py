import os
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    """
    نسخة احترافية لتهيئة Firebase تدعم بيئة Vercel Serverless
    """
    try:
        # 1. التأكد أن التطبيق لم يتم تهيئته مسبقاً لمنع خطأ الـ Duplicate App
        if not firebase_admin._apps:
            
            # 2. جلب القيم والتأكد من وجودها قبل أي معالجة
            project_id = os.environ.get("FIREBASE_PROJECT_ID")
            private_key = os.environ.get("FIREBASE_PRIVATE_KEY")
            client_email = os.environ.get("FIREBASE_CLIENT_EMAIL")
            database_url = os.environ.get("FIREBASE_DATABASE_URL")
            private_key_id = os.environ.get("FIREBASE_PRIVATE_KEY_ID")

            # 3. فحص نقدي: لو فيه حاجة ناقصة السيرفر هيفضل شغال بس الفايربيز مش هيتصل
            if not all([project_id, private_key, client_email, database_url]):
                print("❌ CRITICAL: Missing Firebase Environment Variables!")
                return False

            # 4. معالجة الـ Private Key (أهم خطوة للـ Deployment)
            # بنشيل أي علامات تنصيص زيادة ممكن تكون جت بالخطأ ونعالج السطور الجديدة
            clean_key = private_key.strip().replace('"', '')
            if "\\n" in clean_key:
                clean_key = clean_key.replace("\\n", "\n")

            firebase_creds = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": private_key_id,
                "private_key": clean_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_provider_x509_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
            
            # 5. التهيئة الفعلية
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print("✅ Firebase initialized successfully in Vercel!")
            return True
        return True
    except Exception as e:
        print(f"🔥 Firebase Initialization Error: {str(e)}")
        return False

def get_patient_name():
    """جلب اسم المريض مع معالجة الأخطاء اللحظية"""
    try:
        # محاولة التهيئة لو لسه محصلتش
        if initialize_firebase():
            ref = db.reference('users/u1/name')
            name = ref.get()
            return name if name else "مؤمن تركي" # اسمك الافتراضي لو مفيش داتا
        return "Offline Mode"
    except Exception as e:
        print(f"⚠️ Error fetching name: {str(e)}")
        return "CureConnect User"
