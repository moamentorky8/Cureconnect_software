/* CureConnect - Real-time Control System 2026
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
            // تنبيه شيك باستخدام SweetAlert أو Alert عادي
            console.log("✅ تم إرسال الأمر بنجاح للدرج " + drawerNumber);
            // يمكنك إضافة تأثير بصري للزر هنا
        } else {
            alert("❌ فشل إرسال الأمر: " + (data.error || "تأكد من تسجيل الدخول"));
            if (data.error === "Unauthorized") window.location.href = "/login";
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
        const sosText = sosCard ? sosCard.querySelector('p') : null;
        const sosTitle = sosCard ? sosCard.querySelector('h3') : null;

        if (data.sos_active === 1 || data.sos_active === true) {
            if (sosCard) {
                sosCard.classList.add('bg-red-600', 'text-white', 'animate-pulse');
                sosCard.style.borderColor = "#b91c1c";
            }
            if (sosText) sosText.innerText = "🚨 تنبيه: المريض يحتاج مساعدة فوراً!";
            if (sosTitle) sosTitle.classList.replace('text-red-600', 'text-white');
            
            // تشغيل تنبيه صوتي تلقائي عند حالة الطوارئ
            playVoiceAlert("تنبيه، المريض يطلب المساعدة الفورية");
        } else {
            if (sosCard) {
                sosCard.classList.remove('bg-red-600', 'text-white', 'animate-pulse');
                sosCard.style.backgroundColor = ""; // يعود للستايل الخاص بـ CSS
                sosCard.style.borderColor = "";
            }
            if (sosText) sosText.innerText = "النظام يعمل بشكل مستقر، لا يوجد تنبيهات حالياً.";
            if (sosTitle) sosTitle.classList.replace('text-white', 'text-red-600');
        }

        // --- تحديث الخريطة إذا تغير اللوكيشن ---
        if (data.location && data.location.lat && data.location.lng) {
            const mapIframe = document.getElementById('google-map');
            if (mapIframe) {
                const newSrc = `https://maps.google.com/maps?q=${data.location.lat},${data.location.lng}&z=15&output=embed`;
                
                // تحديث الخريطة فقط إذا تغيرت الإحداثيات لتجنب إعادة التحميل المستمر
                if (mapIframe.src !== newSrc) {
                    mapIframe.src = newSrc;
                    console.log("📍 تم تحديث موقع المريض على الخريطة");
                }
            }
        }
    })
    .catch(error => console.error('Error fetching real-time data:', error));
}

// 3. دالة المساعد الصوتي (نظام النطق)
function playVoiceAlert(customText = null) {
    if (customText) {
        const msg = new SpeechSynthesisUtterance(customText);
        msg.lang = 'ar-SA';
        window.speechSynthesis.speak(msg);
    } else {
        fetch('/get_voice_alert')
        .then(response => response.json())
        .then(data => {
            const msg = new SpeechSynthesisUtterance(data.text);
            msg.lang = 'ar-SA';
            window.speechSynthesis.speak(msg);
        });
    }
}

// ربط زر الميكروفون
document.addEventListener('click', (e) => {
    if (e.target.closest('.ai-mic-btn')) {
        playVoiceAlert();
    }
});

// --- بدء المراقبة اللحظية كل 7 ثواني (أفضل للأداء) ---
setInterval(updateRealTimeData, 7000);

// --- تهيئة الصفحة عند التحميل ---
document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 CureConnect Dashboard Ready!");
    updateRealTimeData(); 
});
