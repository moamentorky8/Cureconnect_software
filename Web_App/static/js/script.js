/* CureConnect - Real-time Control System
   Main Script for Dashboard Interaction
*/

// 1. دالة صرف الجرعة (تتعامل مع الـ 8 أدراج)
function dispenseMedicine(drawerNumber) {
    console.log("طلب صرف جرعة من الدرج رقم: " + drawerNumber);
    
    // إرسال طلب للسيرفر
    fetch('/update_drawer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            drawer: drawerNumber
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // إظهار تنبيه شيك للمستخدم
            alert("✅ " + data.message);
        } else {
            alert("❌ فشل إرسال الأمر: " + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("⚠️ خطأ في الاتصال بالسيرفر");
    });
}

// 2. دالة تحديث حالة الموقع (SOS والـ GPS) بشكل تلقائي
function updateRealTimeData() {
    fetch('/get_sos_status')
    .then(response => response.json())
    .then(data => {
        // --- تحديث حالة الـ SOS ---
        const sosCard = document.querySelector('.sos-card');
        if (data.sos_active === 1) {
            sosCard.classList.add('bg-red-600', 'text-white', 'animate-pulse');
            sosCard.querySelector('p').innerText = "🚨 تنبيه: المريض يحتاج مساعدة فوراً!";
        } else {
            sosCard.classList.remove('bg-red-600', 'text-white', 'animate-pulse');
            sosCard.querySelector('p').innerText = "النظام يعمل بشكل مستقر، لا يوجد تنبيهات حالياً.";
        }

        // --- تحديث الخريطة إذا تغير اللوكيشن ---
        if (data.location) {
            const mapIframe = document.getElementById('google-map');
            const newSrc = `https://maps.google.com/maps?q=${data.location.lat},${data.location.lng}&z=15&output=embed`;
            
            // تحديث الخريطة فقط إذا تغيرت الإحداثيات لتجنب الـ Flickering
            if (mapIframe.src !== newSrc) {
                mapIframe.src = newSrc;
                console.log("تم تحديث موقع المريض على الخريطة");
            }
        }
    })
    .catch(error => console.error('Error fetching real-time data:', error));
}

// 3. المساعد الصوتي (تشغيل تنبيه صوتي عند الحاجة)
const voiceBtn = document.querySelector('.ai-mic-btn');
if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        fetch('/get_voice_alert')
        .then(response => response.json())
        .then(data => {
            const msg = new SpeechSynthesisUtterance(data.text);
            msg.lang = 'ar-SA'; // لغة عربية
            window.speechSynthesis.speak(msg);
        });
    });
}

// --- بدء المراقبة اللحظية كل 5 ثواني ---
setInterval(updateRealTimeData, 5000);

// --- تهيئة الصفحة عند التحميل ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("CureConnect Dashboard Ready!");
    updateRealTimeData(); // تحديث فوري عند الفتح
});
