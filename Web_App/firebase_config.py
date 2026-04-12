import os
import firebase_admin
from firebase_admin import credentials, db

def initialize_firebase():
    # التأكد أن التطبيق لم يتم تهيئته مسبقاً
    if not firebase_admin._apps:
        try:
            # جلب القيم من Environment Variables
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
            database_url = os.getenv("FIREBASE_DATABASE_URL")

            # فحص سريع: لو فيه قيمة ناقصة اطبع تحذير بدل ما تعمل Crash
            if not all([project_id, private_key, client_email, database_url]):
                print("⚠️ Error: One or more Firebase Environment Variables are missing!")
                return

            # معالجة الـ Private Key لضمان قراءة السطور الجديدة (\n) بشكل صحيح
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")

            firebase_creds = {
                "type": "service_account",
                "project_id": project_id,
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": private_key,
                "client_email": client_email,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            # تهيئة التطبيق
            cred = credentials.Certificate(firebase_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': database_url
            })
            print("✅ CureConnect: Firebase connected successfully!")
            
        except Exception as e:
            print(f"❌ Firebase Initialization Failed: {e}")

def get_patient_name():
    """جلب اسم المريض من قاعدة البيانات"""
    try:
        initialize_firebase()
        # التأكد أن التطبيق تم تهيئته قبل محاولة القراءة
        if firebase_admin._apps:
            ref = db.reference('users/u1/name')
            name = ref.get()
            return name if name else "عميل جديد"
        return "Firebase Not Ready"
    except Exception as e:
        print(f"Error fetching data: {e}")
        return "خطأ في الاتصال"
