/* CureConnect - Intelligent Real-time Control System 2026
   Professional Dashboard Logic & Firebase Integration
*/

// --- 1. Constants & Configurations ---
const REFRESH_INTERVAL = 7000; // 7 seconds for optimal performance
const SPEECH_LANG = 'en-US';   // Updated to English as requested

// --- 2. Medicine Dispensing Logic ---
/**
 * Triggers the hardware to open a specific medicine slot.
 * @param {number} drawerNumber - The ID of the compartment (1-8)
 */
async function dispenseMedicine(drawerNumber) {
    console.log(`[CureConnect] Requesting dispense from Slot: ${drawerNumber}`);

    try {
        const response = await fetch('/update_drawer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drawer: drawerNumber })
        });

        const data = await response.json();

        if (data.success) {
            console.log(`✅ Success: Slot ${drawerNumber} opened.`);
            showNotification(`Opening Slot ${drawerNumber}...`, 'success');
        } else {
            console.error(`❌ Failed: ${data.error}`);
            showNotification(data.error || "Action Failed", 'error');
            if (data.error === "Unauthorized") window.location.href = "/login";
        }
    } catch (error) {
        console.error('[CureConnect] Server Connection Error:', error);
        showNotification("Server connection error!", 'error');
    }
}

// --- 3. Real-time Monitoring (SOS & GPS) ---
/**
 * Fetches latest status from Firebase via Backend and updates UI.
 */
async function updateRealTimeData() {
    try {
        const response = await fetch('/get_sos_status');
        const data = await response.json();

        // --- A. SOS Status Update ---
        const sosIndicator = document.getElementById('sos-indicator');
        const sosText = document.getElementById('sos-text');

        if (data.sos_active === 1 || data.sos_active === true) {
            // Alert Mode
            if (sosIndicator) {
                sosIndicator.className = "p-4 mb-6 rounded-2xl bg-red-600 text-white animate-pulse shadow-lg shadow-red-200";
                sosText.innerText = "🚨 ALERT: PATIENT NEEDS HELP!";
            }
            // Trigger automatic voice alert during emergency
            playVoiceAlert("Emergency alert, the patient requested immediate assistance.");
        } else {
            // Secure Mode
            if (sosIndicator) {
                sosIndicator.className = "p-4 mb-6 rounded-2xl bg-gray-50 text-gray-400 border border-gray-100";
                sosText.innerText = "System Secure";
            }
        }

        // --- B. GPS Tracking Update ---
        if (data.location && data.location.lat && data.location.lng) {
            const mapIframe = document.getElementById('google-map');
            if (mapIframe) {
                // Using HTTPS for secure connection on Vercel
                const newSrc = `https://maps.google.com/maps?q=${data.location.lat},${data.location.lng}&z=15&output=embed`;

                if (mapIframe.src !== newSrc) {
                    mapIframe.src = newSrc;
                    console.log("📍 Patient location updated on map.");
                }
            }
        }
    } catch (error) {
        console.error('[CureConnect] Error fetching real-time data:', error);
    }
}

// --- 4. Smart Voice Assistant ---
/**
 * Speaks out alerts or notifications using Web Speech API.
 * @param {string} customText - Optional specific text to speak
 */
function playVoiceAlert(customText = null) {
    if (customText) {
        speak(customText);
    } else {
        fetch('/get_voice_alert')
            .then(res => res.json())
            .then(data => {
                if (data.text) speak(data.text);
            })
            .catch(err => console.error("Voice Assistant Error:", err));
    }
}

function speak(text) {
    // Check if browser supports speech
    if ('speechSynthesis' in window) {
        const msg = new SpeechSynthesisUtterance(text);
        msg.lang = SPEECH_LANG;
        msg.rate = 0.9; // Natural speed
        window.speechSynthesis.cancel(); // Clear previous queue
        window.speechSynthesis.speak(msg);
    }
}

// --- 5. UI Helpers ---
function showNotification(message, type) {
    // If you have a toast library like SweetAlert, use it here. 
    // Otherwise, a simple log or custom floating div.
    console.log(`[Notification] ${type.toUpperCase()}: ${message}`);
}

// --- 6. Event Listeners & Initialization ---

// Global Click Listener for Voice Assistant Button
document.addEventListener('click', (e) => {
    if (e.target.closest('.ai-mic-btn') || e.target.closest('button[onclick="playVoiceAlert()"]')) {
        playVoiceAlert();
    }
});

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 CureConnect Dashboard Ready!");
    updateRealTimeData();

    // Set Interval for Real-time data
    setInterval(updateRealTimeData, REFRESH_INTERVAL);
});