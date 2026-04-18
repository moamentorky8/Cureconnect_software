import pyrebase

# بيانات الربط الخاصة بمشروعك (هتلاقيها في إعدادات المشروع على Firebase Console)
firebaseConfig = {
    "apiKey": "AIzaSy... (اكتب الـ API Key بتاعك هنا)",
    "authDomain": "cureconnect-xxxx.firebaseapp.com",
    "databaseURL": "https://cureconnect-xxxx-default-rtdb.firebaseio.com",
    "projectId": "cureconnect-xxxx",
    "storageBucket": "cureconnect-xxxx.appspot.com",
    "messagingSenderId": "XXXXXXXXXXXX",
    "appId": "1:XXXXXXXXXXXX:web:XXXXXXXXXXXX",
    "measurementId": "G-XXXXXXXX"
}

# تهيئة التطبيق
firebase = pyrebase.initialize_app(firebaseConfig)

# تعريف الوظائف الأساسية عشان نستخدمها في app.py
auth = firebase.auth()      # المسئول عن تسجيل الدخول وإنشاء الحسابات
db = firebase.database()    # المسئول عن قاعدة البيانات (Realtime Database)
storage = firebase.storage() # لو هترفع صور أو ملفات
