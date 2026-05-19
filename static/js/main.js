/**
 * TTSMaker Clone - Main JavaScript
 * Mirror of TTSMaker.com functionality
 */

// ============================================================
// Global State
// ============================================================
const APP_STATE = {
    currentVoiceId: null,
    currentLanguage: 'en',
    conversionHistory: JSON.parse(localStorage.getItem('tts_history') || '[]'),
    isConverting: false,
};

// ============================================================
// Voice Database (mirrored from server)
// ============================================================
const VOICE_DATABASE = {
    en: {
        "United States": [
            {id:147,name:"🔥Peter (Hot+Unlimited)",unlimited:true},
            {id:148,name:"🔥Alayna (Hot+Unlimited)",unlimited:true},
            {id:1480,name:"Alayna (V2 Multi-Emotion)",emotions:["assistant","chat","customerservice","newscast","angry","cheerful","sad","excited","friendly","terrified","shouting","unfriendly","whispering","hopeful"]},
            {id:178,name:"🔥Chloe (Hot+Unlimited)",unlimited:true},
            {id:666,name:"🔥Mia (Long Text+Unlimited)",unlimited:true},
            {id:777,name:"🔥Miles (Slow+Unlimited)",unlimited:true},
            {id:778,name:"🔥Tiffani (Slow+Unlimited)",unlimited:true},
            {id:779,name:"🔥Howard (Slow+Unlimited)",unlimited:true},
            {id:780,name:"🔥Araceli (Slow+Unlimited)",unlimited:true},
            {id:781,name:"🔥Mary (Slow+Unlimited)",unlimited:true},
            {id:785,name:"🔥Jessica (Slow+Unlimited)",unlimited:true},
            {id:788,name:"🔥Alfie (Slow+Unlimited)",unlimited:true},
            {id:663,name:"🔥David (Long Text+Unlimited)",unlimited:true},
            {id:179,name:"🔥Noah (Hot+Unlimited)",unlimited:true},
            {id:146,name:"🔥Mia (Hot+Unlimited)",unlimited:true},
            {id:1300,name:"Elizabeth (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1301,name:"Alicia"},
            {id:1302,name:"Evelyn (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1303,name:"Amelia"},
            {id:1304,name:"Amanda"},
            {id:1305,name:"Ariana"},
            {id:1306,name:"Jackson"},
            {id:1307,name:"GeniusGirl"},
            {id:1308,name:"Stefan"},
            {id:1309,name:"Lily"},
            {id:1777,name:"Miles (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1778,name:"Tiffani (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1781,name:"Mary (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1785,name:"Jessica (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:1788,name:"Alfie (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2001,name:"Derek (General Male)"},
            {id:2002,name:"Dinah (General Female)"},
            {id:2003,name:"Byron (General Male)"},
            {id:2004,name:"Lizzie (General Female)"},
            {id:2490,name:"Kylie (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2491,name:"Aubrey (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2560,name:"Gary"},
            {id:2567,name:"Ryan (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2568,name:"Lauren (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2569,name:"Anthony (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2570,name:"Taylor-F (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2575,name:"Taylor-M (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2576,name:"Megan (V2 Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2588,name:"🧒Emma (Child)"},
            {id:2589,name:"🧒Lily (Child)"},
            {id:2590,name:"🧒David (Child)"},
            {id:2591,name:"🧒Victoria (Child)"},
            {id:2593,name:"Matthew"},
            {id:2594,name:"Olivia"},
            {id:2595,name:"Ethan (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2596,name:"Bran"},
            {id:2598,name:"Ashe"},
            {id:2599,name:"Christ"},
            {id:2700,name:"Liam"},
            {id:2702,name:"Ethan"},
            {id:2704,name:"Jackson"},
            {id:2708,name:"Mason"},
            {id:2710,name:"Michael"},
            {id:2712,name:"James"},
            {id:2714,name:"Jacob"},
            {id:14801,name:"Alayna (V2 Fast)"},
            {id:27001,name:"Liam (V2 Fast)"},
        ],
        "United Kingdom": [
            {id:1310,name:"Anna (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2401,name:"Alison (Child)"},
            {id:2402,name:"Robert (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2403,name:"Jennifer (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2404,name:"Sarah"},
            {id:2405,name:"David"},
            {id:2493,name:"Peyton (Multi-Emotion)",emotions:["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {id:2503,name:"Abbi"},
            {id:2504,name:"Alfie"},
            {id:2802,name:"David"},
            {id:2804,name:"Noah"},
            {id:2550,name:"Cecily (Multi-Language)"},
            {id:2551,name:"Quinton (Multi-Language)"},
        ],
        "Australia": [
            {id:1311,name:"Henry"},
            {id:2505,name:"Natasha"},
            {id:2506,name:"William"},
            {id:2901,name:"Emily"},
            {id:2902,name:"Henry"},
        ],
        "Canada": [
            {id:2521,name:"Elisa"},
            {id:2522,name:"Alex"},
        ],
        "Ireland": [
            {id:2571,name:"Grace"},
            {id:2572,name:"Owen"},
        ],
        "New Zealand": [
            {id:2541,name:"Lily"},
            {id:2542,name:"Mark"},
        ],
        "Singapore": [
            {id:2507,name:"Wayne"},
            {id:2508,name:"Luna"},
        ],
        "India": [
            {id:2509,name:"Prabhat"},
            {id:2510,name:"Neerja"},
            {id:2525,name:"Hima"},
        ],
        "Kenya": [
            {id:2530,name:"Kevin"},
            {id:2531,name:"Ruth"},
        ],
        "Nigeria": [
            {id:2533,name:"Samuel"},
            {id:2534,name:"Abigail"},
        ],
        "Tanzania": [
            {id:2535,name:"Hamisi"},
            {id:2536,name:"Faraja"},
        ],
        "South Africa": [
            {id:2537,name:"Sipho"},
            {id:2538,name:"Gugu"},
        ],
        "Philippines": [
            {id:2528,name:"Samuel"},
            {id:2529,name:"Diana"},
        ],
        "Hong Kong": [
            {id:2511,name:"Sam"},
            {id:2512,name:"Yan"},
        ],
        "Multilingual": [
            {id:2660,name:"Alayna (Multi-Lang)"},
            {id:2661,name:"Clyde (Multi-Lang)"},
            {id:2662,name:"Liora (Multi-Lang)"},
            {id:2663,name:"Fable (Multi-Lang)"},
            {id:2664,name:"Maris (Multi-Lang)"},
            {id:2665,name:"Whitaker (Multi-Lang)"},
            {id:2666,name:"Liam (Multi-Lang)"},
            {id:2667,name:"Selene-F (Multi-Lang)"},
            {id:2668,name:"Selene-M (Multi-Lang)"},
            {id:2669,name:"Lennox (Multi-Lang)"},
            {id:2760,name:"Avalon (Multi-Lang)"},
            {id:2761,name:"Indigo (Multi-Lang)"},
        ],
    },
    ar: {"Arabic":[
        {id:5001,name:"أحمد"},
        {id:5002,name:"فاطمة"},
        {id:5003,name:"عمر"},
        {id:5004,name:"ليلى"},
    ]},
    fr: {"France":[
        {id:6001,name:"Pierre"},
        {id:6002,name:"Sophie"},
        {id:6003,name:"Jean"},
        {id:6004,name:"Marie"},
    ]},
    de: {"Germany":[
        {id:7001,name:"Hans"},
        {id:7002,name:"Anna"},
    ]},
    es: {"Spain":[
        {id:8001,name:"Carlos"},
        {id:8002,name:"Maria"},
        {id:8003,name:"Juan"},
        {id:8004,name:"Elena"},
    ]},
    ja: {"Japan":[
        {id:9001,name:"田中 (Male)"},
        {id:9002,name:"鈴木 (Female)"},
        {id:9003,name:"佐藤 (Male)"},
        {id:9004,name:"高橋 (Female)"},
    ]},
    ko: {"Korea":[
        {id:10001,name:"민수 (Male)"},
        {id:10002,name:"지은 (Female)"},
    ]},
    zh: {"China":[
        {id:11001,name:"王伟 (Male)"},
        {id:11002,name:"李娜 (Female)"},
        {id:11003,name:"张强 (Male)"},
        {id:11004,name:"刘芳 (Female)"},
    ]},
    pt: {"Brazil/Portugal":[
        {id:12001,name:"João"},
        {id:12002,name:"Ana"},
    ]},
    it: {"Italy":[
        {id:13001,name:"Marco"},
        {id:13002,name:"Sofia"},
    ]},
    ru: {"Russia":[
        {id:14001,name:"Алексей"},
        {id:14002,name:"Екатерина"},
    ]},
    tr: {"Turkey":[
        {id:15001,name:"Mehmet"},
        {id:15002,name:"Ayşe"},
    ]},
    hi: {"India (Hindi)":[
        {id:16001,name:"राहुल"},
        {id:16002,name:"प्रिया"},
    ]},
};

// ============================================================
// DOM Elements
// ============================================================
const DOM = {
    textInput: document.getElementById('textInput'),
    charCount: document.getElementById('charCount'),
    charLimit: document.getElementById('charLimit'),
    languageSelect: document.getElementById('languageSelect'),
    voiceSelect: document.getElementById('voiceSelect'),
    convertBtn: document.getElementById('convertBtn'),
    settingsToggle: document.getElementById('settingsToggle'),
    moreSettings: document.getElementById('moreSettings'),
    settingsChevron: document.getElementById('settingsChevron'),
    speedSlider: document.getElementById('speedSlider'),
    speedValue: document.getElementById('speedValue'),
    volumeSlider: document.getElementById('volumeSlider'),
    volumeValue: document.getElementById('volumeValue'),
    audioFormat: document.getElementById('audioFormat'),
    emotionSelect: document.getElementById('emotionSelect'),
    loadingArea: document.getElementById('loadingArea'),
    loadingTimer: document.getElementById('loadingTimer'),
    resultArea: document.getElementById('resultArea'),
    audioPlayer: document.getElementById('audioPlayer'),
    downloadBtn: document.getElementById('downloadBtn'),
    resultChars: document.getElementById('resultChars'),
    resultVoiceId: document.getElementById('resultVoiceId'),
    resultTime: document.getElementById('resultTime'),
    errorArea: document.getElementById('errorArea'),
    errorMessage: document.getElementById('errorMessage'),
    historyList: document.getElementById('historyList'),
    noHistory: document.getElementById('noHistory'),
    langToggle: document.getElementById('langToggle'),
    langDropdown: document.getElementById('langDropdown'),
    mobileMenuBtn: document.getElementById('mobileMenuBtn'),
};

// ============================================================
// Voice Selection Logic
// ============================================================
function populateVoices(languageCode) {
    const langVoices = VOICE_DATABASE[languageCode] || VOICE_DATABASE['en'];
    DOM.voiceSelect.innerHTML = '';

    let firstVoiceId = null;

    for (const [region, voices] of Object.entries(langVoices)) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = region;

        for (const voice of voices) {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = voice.name;
            if (voice.unlimited) {
                option.textContent += ' ♾️';
            }
            if (voice.emotions) {
                option.textContent += ' 🎭';
            }
            optgroup.appendChild(option);

            if (firstVoiceId === null) {
                firstVoiceId = voice.id;
            }
        }

        DOM.voiceSelect.appendChild(optgroup);
    }

    if (firstVoiceId) {
        DOM.voiceSelect.value = firstVoiceId;
        APP_STATE.currentVoiceId = firstVoiceId;
        updateEmotionOptions(firstVoiceId, languageCode);
    }
}

function updateEmotionOptions(voiceId, languageCode) {
    const langVoices = VOICE_DATABASE[languageCode] || VOICE_DATABASE['en'];
    DOM.emotionSelect.innerHTML = '<option value="">Default (No Emotion)</option>';

    let voiceData = null;
    for (const [region, voices] of Object.entries(langVoices)) {
        const found = voices.find(v => v.id == voiceId);
        if (found) {
            voiceData = found;
            break;
        }
    }

    if (voiceData && voiceData.emotions) {
        for (const emotion of voiceData.emotions) {
            const option = document.createElement('option');
            option.value = emotion;
            option.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
            DOM.emotionSelect.appendChild(option);
        }
    }

    DOM.emotionSelect.style.display = '';
}

// ============================================================
// Event Handlers
// ============================================================

// Language change
DOM.languageSelect.addEventListener('change', function() {
    APP_STATE.currentLanguage = this.value;
    populateVoices(this.value);
});

// Voice change
DOM.voiceSelect.addEventListener('change', function() {
    APP_STATE.currentVoiceId = parseInt(this.value);
    updateEmotionOptions(this.value, APP_STATE.currentLanguage);
});

// Character count
DOM.textInput.addEventListener('input', function() {
    const count = this.value.length;
    const limit = parseInt(DOM.charLimit.textContent.replace(/,/g, ''));
    DOM.charCount.textContent = count.toLocaleString();

    const countEl = DOM.charCount;
    countEl.classList.remove('warning', 'danger');
    if (count > limit * 0.8) {
        countEl.classList.add('warning');
    }
    if (count > limit) {
        countEl.classList.add('danger');
    }
});

// Speed slider
DOM.speedSlider.addEventListener('input', function() {
    DOM.speedValue.textContent = parseFloat(this.value).toFixed(1) + 'x';
});

// Volume slider
DOM.volumeSlider.addEventListener('input', function() {
    DOM.volumeValue.textContent = this.value + '%';
});

// Settings toggle
DOM.settingsToggle.addEventListener('click', function() {
    const isVisible = DOM.moreSettings.style.display !== 'none';
    DOM.moreSettings.style.display = isVisible ? 'none' : 'block';
    DOM.settingsChevron.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
});

// Lang dropdown toggle
DOM.langToggle.addEventListener('click', function(e) {
    e.stopPropagation();
    DOM.langDropdown.classList.toggle('show');
});

document.addEventListener('click', function(e) {
    if (!DOM.langToggle.contains(e.target) && !DOM.langDropdown.contains(e.target)) {
        DOM.langDropdown.classList.remove('show');
    }
});

// Mobile menu
DOM.mobileMenuBtn.addEventListener('click', function() {
    const nav = document.querySelector('.nav');
    nav.classList.toggle('show');
});

// Convert button
DOM.convertBtn.addEventListener('click', convertToSpeech);

// FAQ toggle
document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', function() {
        const faqItem = this.parentElement;
        const wasOpen = faqItem.classList.contains('open');

        // Close all
        document.querySelectorAll('.faq-item').forEach(item => item.classList.remove('open'));

        // Toggle current
        if (!wasOpen) {
            faqItem.classList.add('open');
        }
    });
});

// ============================================================
// TTS Conversion
// ============================================================
async function convertToSpeech() {
    const text = DOM.textInput.value.trim();

    if (!text) {
        showError('Please enter some text to convert.');
        return;
    }

    if (!APP_STATE.currentVoiceId) {
        showError('Please select a voice.');
        return;
    }

    // Show loading
    hideResult();
    hideError();
    DOM.loadingArea.style.display = 'block';
    DOM.convertBtn.disabled = true;
    APP_STATE.isConverting = true;

    // Update steps
    updateStep(3);

    // Simulate progress
    let progressTime = 0;
    const progressInterval = setInterval(() => {
        progressTime++;
        DOM.loadingTimer.textContent = `Processing... (${progressTime}s)`;
    }, 1000);

    try {
        const speed = parseFloat(DOM.speedSlider.value);
        const volume = parseInt(DOM.volumeSlider.value) / 100;
        const format = DOM.audioFormat.value;
        const emotion = DOM.emotionSelect.value;

        const response = await fetch('/api/tts/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                voice_id: APP_STATE.currentVoiceId,
                audio_format: format,
                audio_speed: speed,
                audio_volume: volume,
                audio_high_quality: 0,
                emotion_style_key: emotion,
            }),
        });

        const data = await response.json();

        clearInterval(progressInterval);

        if (data.error_code === 0) {
            // Success
            DOM.loadingArea.style.display = 'none';
            DOM.audioPlayer.src = data.audio_download_url;
            DOM.downloadBtn.href = data.audio_download_url;
            DOM.resultChars.textContent = data.tts_task_characters_count;
            DOM.resultVoiceId.textContent = APP_STATE.currentVoiceId;
            DOM.resultTime.textContent = new Date().toLocaleTimeString();
            DOM.resultArea.style.display = 'block';
            updateStep(4);

            // Save to history
            addToHistory(text, APP_STATE.currentVoiceId, data.audio_download_url, data.tts_task_characters_count);
        } else {
            showError(data.msg || 'Conversion failed. Please try again.');
            DOM.loadingArea.style.display = 'none';
        }
    } catch (error) {
        clearInterval(progressInterval);
        DOM.loadingArea.style.display = 'none';
        showError('Network error. Please check your connection and try again. Error: ' + error.message);
    }

    DOM.convertBtn.disabled = false;
    APP_STATE.isConverting = false;
}

// ============================================================
// History Management
// ============================================================
function addToHistory(text, voiceId, audioUrl, charCount) {
    const entry = {
        id: Date.now(),
        text: text.substring(0, 100) + (text.length > 100 ? '...' : ''),
        voiceId: voiceId,
        audioUrl: audioUrl,
        charCount: charCount,
        timestamp: new Date().toISOString(),
    };

    APP_STATE.conversionHistory.unshift(entry);
    if (APP_STATE.conversionHistory.length > 50) {
        APP_STATE.conversionHistory = APP_STATE.conversionHistory.slice(0, 50);
    }

    localStorage.setItem('tts_history', JSON.stringify(APP_STATE.conversionHistory));
    renderHistory();
}

function renderHistory() {
    DOM.historyList.innerHTML = '';

    if (APP_STATE.conversionHistory.length === 0) {
        DOM.historyList.innerHTML = '<p class="no-history">No valid history records found in the last 30 minutes.</p>';
        return;
    }

    // Show only last 30 minutes
    const now = Date.now();
    const recentHistory = APP_STATE.conversionHistory.filter(entry => {
        return (now - entry.id) < 30 * 60 * 1000;
    });

    if (recentHistory.length === 0) {
        DOM.historyList.innerHTML = '<p class="no-history">No valid history records found in the last 30 minutes.</p>';
        return;
    }

    for (const entry of recentHistory) {
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `
            <div class="history-info">
                <strong>${escapeHTML(entry.text)}</strong>
                <span>Voice ID: ${entry.voiceId} | ${entry.charCount} chars</span>
                <span>${new Date(entry.timestamp).toLocaleTimeString()}</span>
            </div>
            <button class="history-play-btn" onclick="playHistoryAudio('${entry.audioUrl}')">
                <i class="fas fa-play"></i> Play
            </button>
        `;
        DOM.historyList.appendChild(item);
    }
}

function playHistoryAudio(url) {
    DOM.audioPlayer.src = url;
    DOM.audioPlayer.play();
    DOM.resultArea.style.display = 'block';
    DOM.downloadBtn.href = url;
}

// ============================================================
// Utility Functions
// ============================================================
function clearText() {
    DOM.textInput.value = '';
    DOM.charCount.textContent = '0';
    DOM.textInput.focus();
}

function pasteText() {
    navigator.clipboard.readText().then(text => {
        DOM.textInput.value = text;
        DOM.charCount.textContent = text.length.toLocaleString();
        DOM.textInput.dispatchEvent(new Event('input'));
    }).catch(err => {
        showError('Unable to paste. Please paste manually.');
    });
}

function copyShareLink() {
    const url = DOM.downloadBtn.href;
    if (url) {
        navigator.clipboard.writeText(url).then(() => {
            const btn = document.querySelector('.share-btn');
            const originalHTML = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => { btn.innerHTML = originalHTML; }, 2000);
        });
    }
}

function resetConverter() {
    hideResult();
    hideError();
    DOM.textInput.value = '';
    DOM.charCount.textContent = '0';
    DOM.loadingArea.style.display = 'none';
    DOM.convertBtn.disabled = false;
    APP_STATE.isConverting = false;
    updateStep(1);
    DOM.textInput.focus();
}

function showError(message) {
    DOM.errorMessage.textContent = message;
    DOM.errorArea.style.display = 'block';
    updateStep(1);
}

function hideError() {
    DOM.errorArea.style.display = 'none';
}

function hideResult() {
    DOM.resultArea.style.display = 'none';
}

function updateStep(stepNumber) {
    document.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active');
        if (stepNum <= stepNumber) {
            step.classList.add('active');
        }
    });
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ============================================================
// Initialization
// ============================================================
function init() {
    populateVoices(APP_STATE.currentLanguage);
    updateStep(1);
    renderHistory();

    // Enable keyboard shortcut
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter' && !APP_STATE.isConverting) {
            convertToSpeech();
        }
    });
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
