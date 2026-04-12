// CureConnect Frontend Logic

// 1. دالة لفتح الدرج (صرف الجرعة)
function dispenseMedicine(drawerNumber) {
    console.log("Dispensing from drawer: " + drawerNumber);
    
    // هنبعت طلب للسيرفر (Flask) وهو اللي بيكلم Firebase
    fetch('/update_drawer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            drawer: drawerNumber,
            status: true
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("جاري فتح الدرج رقم " + drawerNumber);
        }
    })
    .catch(error => console.error('Error:', error));
}

// 2. دالة مراقبة حالة الطوارئ (SOS)
// هنخلي الموقع يسأل السيرفر كل 3 ثواني عن حالة الـ SOS
function checkSOS() {
    fetch('/get_sos_status')
    .then(response => response.json())
    .then(data => {
        const sosCard = document.querySelector('.sos-card');
        if (data.sos_active === 1) {
            // لو فيه طوارئ، هنخلي الكارت ينور أحمر ويظهر تنبيه
            sosCard.classList.add('animate-pulse', 'bg-red-600', 'text-white');
            // ممكن نشغل صوت تنبيه هنا برضه
        } else {
            sosCard.classList.remove('animate-pulse', 'bg-red-600', 'text-white');
        }
    });
}

// تشغيل المراقبة كل 3 ثواني
setInterval(checkSOS, 3000);

// 3. ربط الأزرار عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    const dispenseBtn = document.querySelector('.btn-primary');
    if (dispenseBtn) {
        dispenseBtn.addEventListener('click', function() {
            dispenseMedicine(1); // بنجرب على الدرج الأول
        });
    }
});
