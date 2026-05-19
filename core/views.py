import json
import os
import uuid
import hashlib
import time
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import TTSConversion
import asyncio
import edge_tts
from gtts import gTTS
import tempfile

# ============================================================
# Voice Database - Mirroring TTSMaker's voice catalog
# ============================================================

VOICES = {
    "en": {
        "United States": [
            {"id": 147, "name": "🔥Peter-🇺🇸United States Male (Hot + Unlimited)", "unlimited": True},
            {"id": 148, "name": "🔥Alayna-🇺🇸United States Female (Hot + Unlimited)", "unlimited": True},
            {"id": 1480, "name": "Alayna-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","customerservice","newscast","angry","cheerful","sad","excited","friendly","terrified","shouting","unfriendly","whispering","hopeful"]},
            {"id": 178, "name": "🔥Chloe-🇺🇸United States Female (Hot + Unlimited)", "unlimited": True},
            {"id": 666, "name": "🔥Mia-🗺️Classic Female Voice (Long Text + Unlimited)", "unlimited": True},
            {"id": 777, "name": "🔥Miles-🇺🇸United States Male (Slow + Unlimited)", "unlimited": True},
            {"id": 778, "name": "🔥Tiffani-🇺🇸United States Female (Slow + Unlimited)", "unlimited": True},
            {"id": 779, "name": "🔥Howard-🗺️Global Male Voice (Slow + Unlimited)", "unlimited": True},
            {"id": 780, "name": "🔥Araceli-🗺️Global Female Voice (Slow + Unlimited)", "unlimited": True},
            {"id": 781, "name": "🔥Mary-🇺🇸United States Female (Slow + Unlimited)", "unlimited": True},
            {"id": 785, "name": "🔥Jessica-🇺🇸United States Female (Slow + Unlimited)", "unlimited": True},
            {"id": 788, "name": "🔥Alfie-🇺🇸United States Male (Slow + Unlimited)", "unlimited": True},
            {"id": 663, "name": "🔥David-🗺️Classic Male Voice (Long Text + Unlimited)", "unlimited": True},
            {"id": 179, "name": "🔥Noah-🇺🇸United States Male (Hot + Unlimited)", "unlimited": True},
            {"id": 146, "name": "🔥Mia-🇺🇸United States Female (Hot + Unlimited)", "unlimited": True},
            {"id": 1300, "name": "Elizabeth-🇺🇸United States Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1301, "name": "Alicia-🇺🇸United States Female", "unlimited": False},
            {"id": 1302, "name": "Evelyn-🇺🇸United States Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1303, "name": "Amelia-🇺🇸United States Female", "unlimited": False},
            {"id": 1304, "name": "Amanda-🇺🇸United States Female", "unlimited": False},
            {"id": 1305, "name": "Ariana-🇺🇸United States Female", "unlimited": False},
            {"id": 1306, "name": "Jackson-🇺🇸United States Male", "unlimited": False},
            {"id": 1307, "name": "GeniusGirl-🇺🇸United States Female", "unlimited": False},
            {"id": 1308, "name": "Stefan-🇺🇸United States Male", "unlimited": False},
            {"id": 1309, "name": "Lily-🇺🇸United States Female", "unlimited": False},
            {"id": 1777, "name": "Miles-🇺🇸United States Male (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1778, "name": "Tiffani-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1781, "name": "Mary-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1785, "name": "Jessica-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 1788, "name": "Alfie-🇺🇸United States Male (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2001, "name": "Derek-🗺️General Male Voice", "unlimited": False},
            {"id": 2002, "name": "Dinah-🗺️General Female", "unlimited": False},
            {"id": 2003, "name": "Byron-🗺️General Male", "unlimited": False},
            {"id": 2004, "name": "Lizzie-🗺️General Female", "unlimited": False},
            {"id": 2490, "name": "Kylie-🇺🇸United States Male (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2491, "name": "Aubrey-🇺🇸United States Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2560, "name": "Gary-🇺🇸United States Male", "unlimited": False},
            {"id": 2567, "name": "Ryan-🇺🇸United States Male (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2568, "name": "Lauren-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2569, "name": "Anthony-🇺🇸United States Male (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2570, "name": "Taylor-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2575, "name": "Taylor-🇺🇸United States Male (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2576, "name": "Megan-🇺🇸United States Female (V2 Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2588, "name": "🧒Emma-🇺🇸United States Female Child", "unlimited": False},
            {"id": 2589, "name": "🧒Lily-🇺🇸United States Female Child", "unlimited": False},
            {"id": 2590, "name": "🧒David-🇺🇸United States Male Child", "unlimited": False},
            {"id": 2591, "name": "🧒Victoria-🇺🇸United States Female Child", "unlimited": False},
            {"id": 2593, "name": "Matthew-🇺🇸United States Male", "unlimited": False},
            {"id": 2594, "name": "Olivia-🇺🇸United States Female", "unlimited": False},
            {"id": 2595, "name": "Ethan-🇺🇸United States Male (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2596, "name": "Bran-🇺🇸United States Male", "unlimited": False},
            {"id": 2598, "name": "Ashe-🇺🇸United States Female", "unlimited": False},
            {"id": 2599, "name": "Christ-🇺🇸United States Male", "unlimited": False},
            {"id": 2700, "name": "Liam-🇺🇸United States Male", "unlimited": False},
            {"id": 2702, "name": "Ethan-🇺🇸United States Male", "unlimited": False},
            {"id": 2704, "name": "Jackson-🇺🇸United States Male", "unlimited": False},
            {"id": 2708, "name": "Mason-🇺🇸United States Male", "unlimited": False},
            {"id": 2710, "name": "Michael-🇺🇸United States Male", "unlimited": False},
            {"id": 2712, "name": "James-🇺🇸United States Male", "unlimited": False},
            {"id": 2714, "name": "Jacob-🇺🇸United States Male", "unlimited": False},
            {"id": 14801, "name": "Alayna-🇺🇸United States Female (V2 Fast)", "unlimited": False},
            {"id": 27001, "name": "Liam-🇺🇸United States Male (V2 Fast)", "unlimited": False},
        ],
        "United Kingdom": [
            {"id": 1310, "name": "Anna-🇬🇧United Kingdom Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2401, "name": "Alison-🇬🇧United Kingdom Female Child", "unlimited": False},
            {"id": 2402, "name": "Robert-🇬🇧United Kingdom Male (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2403, "name": "Jennifer-🇬🇧United Kingdom Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2404, "name": "Sarah-🇬🇧United Kingdom Female", "unlimited": False},
            {"id": 2405, "name": "David-🇬🇧United Kingdom Male", "unlimited": False},
            {"id": 2493, "name": "Peyton-🇬🇧Global Female (Multi-Emotion)", "unlimited": False, "emotions": ["assistant","chat","angry","cheerful","sad","excited","friendly"]},
            {"id": 2503, "name": "Abbi-🇬🇧United Kingdom Female", "unlimited": False},
            {"id": 2504, "name": "Alfie-🇬🇧United Kingdom Male", "unlimited": False},
            {"id": 2802, "name": "David-🇬🇧United Kingdom Male", "unlimited": False},
            {"id": 2804, "name": "Noah-🇬🇧United Kingdom Male", "unlimited": False},
            {"id": 2550, "name": "Cecily-🇬🇧United Kingdom Female (Multi-Language)", "unlimited": False},
            {"id": 2551, "name": "Quinton-🇬🇧United Kingdom Male (Multi-Language)", "unlimited": False},
        ],
        "Australia": [
            {"id": 1311, "name": "Henry-🇦🇺Australia Male", "unlimited": False},
            {"id": 2505, "name": "Natasha-🇦🇺Australian Female", "unlimited": False},
            {"id": 2506, "name": "William-🇦🇺Australian Male", "unlimited": False},
            {"id": 2901, "name": "Emily-🇦🇺Australian Female", "unlimited": False},
            {"id": 2902, "name": "Henry-🇦🇺Australian Male", "unlimited": False},
        ],
        "Canada": [
            {"id": 2521, "name": "Elisa-🇨🇦Canada Female", "unlimited": False},
            {"id": 2522, "name": "Alex-🇨🇦Canada Male", "unlimited": False},
        ],
        "Ireland": [
            {"id": 2571, "name": "Grace-🇮🇪Ireland Female", "unlimited": False},
            {"id": 2572, "name": "Owen-🇮🇪Ireland Male", "unlimited": False},
        ],
        "New Zealand": [
            {"id": 2541, "name": "Lily-🇳🇿New Zealand Female", "unlimited": False},
            {"id": 2542, "name": "Mark-🇳🇿New Zealand Male", "unlimited": False},
        ],
        "Singapore": [
            {"id": 2507, "name": "Wayne-🇸🇬Singapore Male", "unlimited": False},
            {"id": 2508, "name": "Luna-🇸🇬Singapore Female", "unlimited": False},
        ],
        "India": [
            {"id": 2509, "name": "Prabhat-🇮🇳India Male", "unlimited": False},
            {"id": 2510, "name": "Neerja-🇮🇳India Female", "unlimited": False},
            {"id": 2525, "name": "Hima-🇮🇳India Female", "unlimited": False},
        ],
        "Kenya": [
            {"id": 2530, "name": "Kevin-🇰🇪Kenya Male", "unlimited": False},
            {"id": 2531, "name": "Ruth-🇰🇪Kenya Female", "unlimited": False},
        ],
        "Nigeria": [
            {"id": 2533, "name": "Samuel-🇳🇬Nigeria Male", "unlimited": False},
            {"id": 2534, "name": "Abigail-🇳🇬Nigeria Female", "unlimited": False},
        ],
        "Tanzania": [
            {"id": 2535, "name": "Hamisi-🇹🇿Tanzania Male", "unlimited": False},
            {"id": 2536, "name": "Faraja-🇹🇿Tanzania Female", "unlimited": False},
        ],
        "South Africa": [
            {"id": 2537, "name": "Sipho-🇿🇦South Africa Male", "unlimited": False},
            {"id": 2538, "name": "Gugu-🇿🇦South Africa Female", "unlimited": False},
        ],
        "Philippines": [
            {"id": 2528, "name": "Samuel-🇵🇭Philippines Male", "unlimited": False},
            {"id": 2529, "name": "Diana-🇵🇭Philippines Female", "unlimited": False},
        ],
        "Hong Kong": [
            {"id": 2511, "name": "Sam-🇭🇰Hong Kong Male", "unlimited": False},
            {"id": 2512, "name": "Yan-🇭🇰Hong Kong Female", "unlimited": False},
        ],
        "Multilingual": [
            {"id": 2660, "name": "Alayna-🇺🇸United States Female (Multi-Language)", "unlimited": False},
            {"id": 2661, "name": "Clyde-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2662, "name": "Liora-🇺🇸United States Female (Multi-Language)", "unlimited": False},
            {"id": 2663, "name": "Fable-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2664, "name": "Maris-🇺🇸United States Female (Multi-Language)", "unlimited": False},
            {"id": 2665, "name": "Whitaker-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2666, "name": "Liam-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2667, "name": "Selene-🇺🇸United States Female (Multi-Language)", "unlimited": False},
            {"id": 2668, "name": "Selene-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2669, "name": "Lennox-🇺🇸United States Female (Multi-Language)", "unlimited": False},
            {"id": 2760, "name": "Avalon-🇺🇸United States Male (Multi-Language)", "unlimited": False},
            {"id": 2761, "name": "Indigo-🇺🇸United States Female (Multi-Language)", "unlimited": False},
        ],
    },
    "ar": {
        "Arabic": [
            {"id": 5001, "name": "أحمد-🇸🇦Arabic Male", "unlimited": False},
            {"id": 5002, "name": "فاطمة-🇸🇦Arabic Female", "unlimited": False},
            {"id": 5003, "name": "عمر-🇸🇦Arabic Male", "unlimited": False},
            {"id": 5004, "name": "ليلى-🇸🇦Arabic Female", "unlimited": False},
        ]
    },
    "fr": {
        "France": [
            {"id": 6001, "name": "Pierre-🇫🇷French Male", "unlimited": False},
            {"id": 6002, "name": "Sophie-🇫🇷French Female", "unlimited": False},
            {"id": 6003, "name": "Jean-🇫🇷French Male", "unlimited": False},
            {"id": 6004, "name": "Marie-🇫🇷French Female", "unlimited": False},
        ]
    },
    "de": {
        "Germany": [
            {"id": 7001, "name": "Hans-🇩🇪German Male", "unlimited": False},
            {"id": 7002, "name": "Anna-🇩🇪German Female", "unlimited": False},
        ]
    },
    "es": {
        "Spain": [
            {"id": 8001, "name": "Carlos-🇪🇸Spanish Male", "unlimited": False},
            {"id": 8002, "name": "Maria-🇪🇸Spanish Female", "unlimited": False},
            {"id": 8003, "name": "Juan-🇪🇸Spanish Male", "unlimited": False},
            {"id": 8004, "name": "Elena-🇪🇸Spanish Female", "unlimited": False},
        ]
    },
    "ja": {
        "Japan": [
            {"id": 9001, "name": "田中-🇯🇵Japanese Male", "unlimited": False},
            {"id": 9002, "name": "鈴木-🇯🇵Japanese Female", "unlimited": False},
            {"id": 9003, "name": "佐藤-🇯🇵Japanese Male", "unlimited": False},
            {"id": 9004, "name": "高橋-🇯🇵Japanese Female", "unlimited": False},
        ]
    },
    "ko": {
        "Korea": [
            {"id": 10001, "name": "민수-🇰🇷Korean Male", "unlimited": False},
            {"id": 10002, "name": "지은-🇰🇷Korean Female", "unlimited": False},
        ]
    },
    "zh": {
        "China": [
            {"id": 11001, "name": "王伟-🇨🇳Chinese Male", "unlimited": False},
            {"id": 11002, "name": "李娜-🇨🇳Chinese Female", "unlimited": False},
            {"id": 11003, "name": "张强-🇨🇳Chinese Male", "unlimited": False},
            {"id": 11004, "name": "刘芳-🇨🇳Chinese Female", "unlimited": False},
        ]
    },
    "pt": {
        "Brazil/Portugal": [
            {"id": 12001, "name": "João-🇧🇷Portuguese Male", "unlimited": False},
            {"id": 12002, "name": "Ana-🇧🇷Portuguese Female", "unlimited": False},
        ]
    },
    "it": {
        "Italy": [
            {"id": 13001, "name": "Marco-🇮🇹Italian Male", "unlimited": False},
            {"id": 13002, "name": "Sofia-🇮🇹Italian Female", "unlimited": False},
        ]
    },
    "ru": {
        "Russia": [
            {"id": 14001, "name": "Алексей-🇷🇺Russian Male", "unlimited": False},
            {"id": 14002, "name": "Екатерина-🇷🇺Russian Female", "unlimited": False},
        ]
    },
    "tr": {
        "Turkey": [
            {"id": 15001, "name": "Mehmet-🇹🇷Turkish Male", "unlimited": False},
            {"id": 15002, "name": "Ayşe-🇹🇷Turkish Female", "unlimited": False},
        ]
    },
    "hi": {
        "India (Hindi)": [
            {"id": 16001, "name": "राहुल-🇮🇳Hindi Male", "unlimited": False},
            {"id": 16002, "name": "प्रिया-🇮🇳Hindi Female", "unlimited": False},
        ]
    },
}

LANGUAGES = [
    {"code": "en", "name": "English", "flag": "🇺🇸"},
    {"code": "zh", "name": "中文 (Chinese)", "flag": "🇨🇳"},
    {"code": "es", "name": "Español (Spanish)", "flag": "🇪🇸"},
    {"code": "pt", "name": "Português (Portuguese)", "flag": "🇧🇷"},
    {"code": "de", "name": "Deutsch (German)", "flag": "🇩🇪"},
    {"code": "fr", "name": "Français (French)", "flag": "🇫🇷"},
    {"code": "it", "name": "Italiano (Italian)", "flag": "🇮🇹"},
    {"code": "tr", "name": "Türkçe (Turkish)", "flag": "🇹🇷"},
    {"code": "ru", "name": "Русский (Russian)", "flag": "🇷🇺"},
    {"code": "ja", "name": "日本語 (Japanese)", "flag": "🇯🇵"},
    {"code": "ko", "name": "한국어 (Korean)", "flag": "🇰🇷"},
    {"code": "ar", "name": "العربية (Arabic)", "flag": "🇸🇦"},
    {"code": "hi", "name": "हिंदी (Hindi)", "flag": "🇮🇳"},
    {"code": "vi", "name": "Tiếng Việt (Vietnamese)", "flag": "🇻🇳"},
    {"code": "th", "name": "ไทย (Thai)", "flag": "🇹🇭"},
    {"code": "id", "name": "Bahasa Indonesia", "flag": "🇮🇩"},
    {"code": "ms", "name": "Bahasa Melayu", "flag": "🇲🇾"},
    {"code": "fi", "name": "Suomi (Finnish)", "flag": "🇫🇮"},
    {"code": "sv", "name": "Svenska (Swedish)", "flag": "🇸🇪"},
    {"code": "nb", "name": "Norsk (Norwegian)", "flag": "🇳🇴"},
    {"code": "da", "name": "Dansk (Danish)", "flag": "🇩🇰"},
    {"code": "ro", "name": "Română (Romanian)", "flag": "🇷🇴"},
    {"code": "hu", "name": "Magyar (Hungarian)", "flag": "🇭🇺"},
    {"code": "pl", "name": "Polski (Polish)", "flag": "🇵🇱"},
    {"code": "nl", "name": "Nederlands (Dutch)", "flag": "🇳🇱"},
    {"code": "cs", "name": "Čeština (Czech)", "flag": "🇨🇿"},
    {"code": "uk", "name": "Українська (Ukrainian)", "flag": "🇺🇦"},
    {"code": "hr", "name": "Hrvatski (Croatian)", "flag": "🇭🇷"},
    {"code": "el", "name": "Ελληνικά (Greek)", "flag": "🇬🇷"},
    {"code": "sk", "name": "Slovenčina (Slovak)", "flag": "🇸🇰"},
    {"code": "bg", "name": "Български (Bulgarian)", "flag": "🇧🇬"},
    {"code": "sl", "name": "Slovenščina (Slovenian)", "flag": "🇸🇮"},
    {"code": "ca", "name": "Català (Catalan)", "flag": "🇪🇸"},
    {"code": "ga", "name": "Gaeilge (Irish)", "flag": "🇮🇪"},
    {"code": "lt", "name": "Lietuvių (Lithuanian)", "flag": "🇱🇹"},
    {"code": "mt", "name": "Malti (Maltese)", "flag": "🇲🇹"},
    {"code": "et", "name": "Eesti (Estonian)", "flag": "🇪🇪"},
    {"code": "is", "name": "Íslenska (Icelandic)", "flag": "🇮🇸"},
    {"code": "lv", "name": "Latviešu (Latvian)", "flag": "🇱🇻"},
    {"code": "fa", "name": "فارسی (Persian)", "flag": "🇮🇷"},
    {"code": "sw", "name": "Kiswahili (Swahili)", "flag": "🇹🇿"},
    {"code": "bn", "name": "বাংলা (Bengali)", "flag": "🇧🇩"},
    {"code": "ur", "name": "اردو (Urdu)", "flag": "🇵🇰"},
    {"code": "ta", "name": "தமிழ் (Tamil)", "flag": "🇮🇳"},
    {"code": "mr", "name": "मराठी (Marathi)", "flag": "🇮🇳"},
    {"code": "te", "name": "తెలుగు (Telugu)", "flag": "🇮🇳"},
    {"code": "gu", "name": "ગુજરાતી (Gujarati)", "flag": "🇮🇳"},
    {"code": "ml", "name": "മലയാളം (Malayalam)", "flag": "🇮🇳"},
    {"code": "kn", "name": "ಕನ್ನಡ (Kannada)", "flag": "🇮🇳"},
    {"code": "he", "name": "עברית (Hebrew)", "flag": "🇮🇱"},
]

SUPPORTED_LANGUAGES = [lang["code"] for lang in LANGUAGES]

EMOTION_STYLES = [
    "assistant", "chat", "customerservice", "newscast",
    "angry", "cheerful", "sad", "excited",
    "friendly", "terrified", "shouting", "unfriendly",
    "whispering", "hopeful"
]


def get_voices_for_language(language_code):
    """Get all voices for a given language code"""
    return VOICES.get(language_code, {})


def build_voice_index():
    """Build a flat voice index by ID for quick lookups"""
    index = {}
    for lang_code, regions in VOICES.items():
        for region, voices in regions.items():
            for v in voices:
                index[v["id"]] = {
                    **v,
                    "language": lang_code,
                    "region": region
                }
    return index


VOICE_INDEX = build_voice_index()


# ============================================================
# Views
# ============================================================

def index(request):
    """Main TTS conversion page - mirrors TTSMaker.com homepage"""
    context = {
        'languages': LANGUAGES,
        'voices': VOICES,
        'emotion_styles': EMOTION_STYLES,
        'default_lang': 'en',
        'free_char_limit': settings.FREE_CHAR_LIMIT,
    }
    return render(request, 'core/index.html', context)


def blog(request):
    """Blog page"""
    return render(request, 'core/blog.html')


def api_docs(request):
    """API documentation page"""
    return render(request, 'core/api_docs.html')


def privacy(request):
    """Privacy policy page"""
    return render(request, 'core/privacy.html')


def terms(request):
    """Terms of service page"""
    return render(request, 'core/terms.html')


# ============================================================
# API Endpoints (mirroring TTSMaker v2 API)
# ============================================================

@csrf_exempt
@require_http_methods(["GET", "POST"])
def voices_api(request):
    """
    GET /api/voices/?language=en
    Mirror of TTSMaker's /v2/get-voice-list endpoint
    """
    language = request.GET.get('language', None)

    if language and language not in SUPPORTED_LANGUAGES:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "LANGUAGE_NOT_SUPPORTED",
            "msg": f"Language '{language}' is not supported.",
        }, status=400)

    voices_detailed = []
    voices_id_list = []

    if language:
        lang_voices = get_voices_for_language(language)
        for region, voice_list in lang_voices.items():
            for v in voice_list:
                voices_detailed.append({
                    "id": v["id"],
                    "name": v["name"],
                    "language": language,
                    "text_characters_limit": 20000 if v.get("unlimited") else 5000,
                    "unlimited": v.get("unlimited", False),
                    **({"is_support_emotion": True, "support_emotion_key_list": v.get("emotions", [])} if "emotions" in v else {})
                })
                voices_id_list.append(v["id"])
    else:
        for lang_code, regions in VOICES.items():
            for region, voice_list in regions.items():
                for v in voice_list:
                    voices_detailed.append({
                        "id": v["id"],
                        "name": v["name"],
                        "language": lang_code,
                        "text_characters_limit": 20000 if v.get("unlimited") else 5000,
                        "unlimited": v.get("unlimited", False),
                        **({"is_support_emotion": True, "support_emotion_key_list": v.get("emotions", [])} if "emotions" in v else {})
                    })
                    voices_id_list.append(v["id"])

    return JsonResponse({
        "error_code": 0,
        "error_summary": "",
        "msg": "Query the list of voices successfully.",
        "language": language or "all",
        "support_language_list": SUPPORTED_LANGUAGES,
        "voices_id_list": voices_id_list,
        "voices_count": len(voices_id_list),
        "voices_detailed_list": voices_detailed,
    })


@csrf_exempt
@require_http_methods(["POST"])
def tts_api(request):
    """
    POST /api/tts/
    Mirror of TTSMaker's /v2/create-tts-order endpoint
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "POST_FIELD_ERROR",
            "msg": "Invalid JSON. Post data fields are incomplete.",
        }, status=400)

    text = data.get('text', '').strip()
    voice_id = data.get('voice_id', None)
    audio_format = data.get('audio_format', 'mp3')
    audio_speed = float(data.get('audio_speed', 1.0))
    audio_volume = float(data.get('audio_volume', 1.0))
    audio_pitch = float(data.get('audio_pitch', 1.0))
    audio_hq = data.get('audio_high_quality', 0)
    pause_time = int(data.get('text_paragraph_pause_time', 0))
    emotion_key = data.get('emotion_style_key', '')
    emotion_intensity = float(data.get('emotion_intensity', 1.0))

    # Validate required fields
    if not text or voice_id is None:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "POST_FIELD_ERROR",
            "msg": "Post data fields are incomplete. Please check post fields.",
        }, status=400)

    # Validate voice_id
    voice_id = int(voice_id)
    if voice_id not in VOICE_INDEX:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "VOICE_ID_ERROR",
            "msg": "Voice id does not exist or has been disabled.",
        }, status=400)

    voice_data = VOICE_INDEX[voice_id]

    # Validate text length
    max_chars = 20000 if voice_data.get('unlimited') else 5000
    if len(text) > max_chars:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "TEXT_LENGTH_ERROR",
            "msg": f"Text length exceeds maximum {max_chars} characters.",
        }, status=400)

    # Validate audio format
    if audio_format not in ['mp3', 'wav', 'ogg', 'aac', 'opus']:
        audio_format = 'mp3'

    # Validate speed range
    audio_speed = max(0.5, min(2.0, audio_speed))
    audio_volume = max(0.1, min(2.0, audio_volume))

    # Process text - handle break tags and paragraph pauses
    text = text.replace('[[break=', '[[break_placeholder=')

    if pause_time > 0:
        lines = text.split('\n')
        break_tag = f' ... '  # Simulate pause
        text = break_tag.join(lines)

    if pause_time == -1:
        text = ''.join(text.split('\n'))

    # Generate unique filename
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    filename = f"tts_{timestamp}_{unique_id}.{audio_format}"

    # Process text for TTS
    clean_text = text.replace('[[break_placeholder=', '[[break=')
    import re
    clean_text = re.sub(r'\[\[break=\d+\]\]', ' ', clean_text)

    # Generate TTS using gTTS (free Google TTS) as primary engine
    output_path = os.path.join(settings.MEDIA_ROOT, 'audio', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        # Use gTTS - map language for best quality
        tts_lang = voice_data.get('language', 'en')
        if tts_lang == 'zh':
            tts_lang = 'zh-CN'

        tts = gTTS(text=clean_text, lang=tts_lang, slow=(audio_speed < 0.8))
        tts.save(output_path)

        file_size = os.path.getsize(output_path)

        # Create conversion record
        conversion = TTSConversion(
            text=text,
            language=tts_lang,
            voice_id=str(voice_id),
            speed=audio_speed,
            volume=audio_volume,
            audio_file=f'audio/{filename}',
            file_format=audio_format,
            file_size=file_size,
            ip_address=request.META.get('REMOTE_ADDR', '')
        )
        conversion.save()

        # Build download URL
        download_url = request.build_absolute_uri(f'/api/download/{filename}')

        return JsonResponse({
            "error_code": 0,
            "error_summary": "",
            "msg": "TTS Task Executed Successfully",
            "tts_task_characters_count": len(text),
            "audio_download_url": download_url,
            "audio_download_backup_url": download_url,
            "audio_file_format": audio_format,
            "current_timestamp": timestamp,
            "audio_file_expiration_timestamp": timestamp + 7200,
            "conversion_id": str(conversion.id),
            "account_status": {
                "quota_characters": settings.FREE_CHAR_LIMIT,
                "characters_used": len(text),
                "available_quota": settings.FREE_CHAR_LIMIT - len(text),
                "subscription_period": "week",
                "subscription_next_reset_timestamp": int(time.time()) + 604800,
            }
        })

    except Exception as e:
        return JsonResponse({
            "error_code": -1,
            "error_summary": "ERROR_TTS_FAILED",
            "msg": f"The conversion failed. Server error: {str(e)}",
        }, status=500)


def download_audio(request, filename):
    """Download generated audio file"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'audio', filename)

    if not os.path.exists(file_path):
        raise Http404("Audio file not found or expired")

    response = FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
