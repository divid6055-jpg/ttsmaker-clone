"""
Real voice catalog backed by edge-tts (Microsoft Azure neural voices) and gTTS.

Every voice exposed by the API maps to a real, working backend engine:

  * engine = "edge"  -> uses `edge_tts.Communicate(text, voice=edge_voice)`
                        producing high-quality MP3 output natively.
  * engine = "gtts"  -> falls back to gTTS using the `gtts_lang` field
                        (used only when edge-tts is unavailable on the host).

We deliberately ship a curated, *truthful* list. The previous version of this
project exposed hundreds of fake voice IDs that all silently fell back to a
single gTTS language. That misled users and is no longer permitted.

To extend this catalog, simply add a new entry whose `edge_voice` matches one
of the voices returned by `edge-tts --list-voices`.
"""

from __future__ import annotations

from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Languages metadata used by the UI
# ---------------------------------------------------------------------------
LANGUAGES: List[Dict] = [
    {"code": "ar", "name": "العربية (Arabic)", "flag": "🇸🇦", "rtl": True},
    {"code": "en", "name": "English", "flag": "🇺🇸"},
    {"code": "es", "name": "Español (Spanish)", "flag": "🇪🇸"},
    {"code": "fr", "name": "Français (French)", "flag": "🇫🇷"},
    {"code": "de", "name": "Deutsch (German)", "flag": "🇩🇪"},
    {"code": "it", "name": "Italiano (Italian)", "flag": "🇮🇹"},
    {"code": "pt", "name": "Português (Portuguese)", "flag": "🇧🇷"},
    {"code": "ru", "name": "Русский (Russian)", "flag": "🇷🇺"},
    {"code": "tr", "name": "Türkçe (Turkish)", "flag": "🇹🇷"},
    {"code": "ja", "name": "日本語 (Japanese)", "flag": "🇯🇵"},
    {"code": "ko", "name": "한국어 (Korean)", "flag": "🇰🇷"},
    {"code": "zh", "name": "中文 (Chinese)", "flag": "🇨🇳"},
    {"code": "hi", "name": "हिंदी (Hindi)", "flag": "🇮🇳"},
    {"code": "ur", "name": "اردو (Urdu)", "flag": "🇵🇰", "rtl": True},
    {"code": "fa", "name": "فارسی (Persian)", "flag": "🇮🇷", "rtl": True},
    {"code": "he", "name": "עברית (Hebrew)", "flag": "🇮🇱", "rtl": True},
    {"code": "nl", "name": "Nederlands (Dutch)", "flag": "🇳🇱"},
    {"code": "pl", "name": "Polski (Polish)", "flag": "🇵🇱"},
    {"code": "sv", "name": "Svenska (Swedish)", "flag": "🇸🇪"},
    {"code": "id", "name": "Bahasa Indonesia", "flag": "🇮🇩"},
    {"code": "th", "name": "ไทย (Thai)", "flag": "🇹🇭"},
    {"code": "vi", "name": "Tiếng Việt", "flag": "🇻🇳"},
]

SUPPORTED_LANGUAGES = [lang["code"] for lang in LANGUAGES]

# Languages that should render right-to-left in the UI.
RTL_LANGUAGES = {lang["code"] for lang in LANGUAGES if lang.get("rtl")}


# ---------------------------------------------------------------------------
# Curated voice catalog
# ---------------------------------------------------------------------------
# Each voice is fully described:
#   id          : stable integer ID used by the API (do not reuse numbers)
#   name        : human-readable display label
#   language    : ISO language code (matches LANGUAGES above)
#   region      : grouping label used by the UI
#   gender      : "Male" | "Female"
#   engine      : "edge" (preferred) or "gtts" (fallback only)
#   edge_voice  : exact edge-tts voice name (when engine=="edge")
#   gtts_lang   : language code to pass to gTTS as a backup
#   text_characters_limit : per-request char cap exposed to the API/UI
# ---------------------------------------------------------------------------

_RAW_VOICES: List[Dict] = [
    # ---------------- Arabic ----------------
    {"id": 1001, "name": "Hamed - Saudi Arabia Male", "language": "ar", "region": "Saudi Arabia",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-SA-HamedNeural", "gtts_lang": "ar"},
    {"id": 1002, "name": "Zariyah - Saudi Arabia Female", "language": "ar", "region": "Saudi Arabia",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-SA-ZariyahNeural", "gtts_lang": "ar"},
    {"id": 1003, "name": "Shakir - Egypt Male", "language": "ar", "region": "Egypt",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-EG-ShakirNeural", "gtts_lang": "ar"},
    {"id": 1004, "name": "Salma - Egypt Female", "language": "ar", "region": "Egypt",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-EG-SalmaNeural", "gtts_lang": "ar"},
    {"id": 1005, "name": "Jamal - Tunisia Male", "language": "ar", "region": "Tunisia",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-TN-HediNeural", "gtts_lang": "ar"},
    {"id": 1006, "name": "Reem - Tunisia Female", "language": "ar", "region": "Tunisia",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-TN-ReemNeural", "gtts_lang": "ar"},
    {"id": 1007, "name": "Moaz - Jordan Male", "language": "ar", "region": "Jordan",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-JO-TaimNeural", "gtts_lang": "ar"},
    {"id": 1008, "name": "Sana - Jordan Female", "language": "ar", "region": "Jordan",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-JO-SanaNeural", "gtts_lang": "ar"},
    {"id": 1009, "name": "Rami - Lebanon Male", "language": "ar", "region": "Lebanon",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-LB-RamiNeural", "gtts_lang": "ar"},
    {"id": 1010, "name": "Layla - Lebanon Female", "language": "ar", "region": "Lebanon",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-LB-LaylaNeural", "gtts_lang": "ar"},
    {"id": 1011, "name": "Fahed - UAE Male", "language": "ar", "region": "UAE",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-AE-HamdanNeural", "gtts_lang": "ar"},
    {"id": 1012, "name": "Fatima - UAE Female", "language": "ar", "region": "UAE",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-AE-FatimaNeural", "gtts_lang": "ar"},
    {"id": 1013, "name": "Bassel - Syria Male", "language": "ar", "region": "Syria",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-SY-LaithNeural", "gtts_lang": "ar"},
    {"id": 1014, "name": "Amany - Syria Female", "language": "ar", "region": "Syria",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-SY-AmanyNeural", "gtts_lang": "ar"},
    {"id": 1015, "name": "Ali - Iraq Male", "language": "ar", "region": "Iraq",
     "gender": "Male", "engine": "edge", "edge_voice": "ar-IQ-BasselNeural", "gtts_lang": "ar"},
    {"id": 1016, "name": "Rana - Iraq Female", "language": "ar", "region": "Iraq",
     "gender": "Female", "engine": "edge", "edge_voice": "ar-IQ-RanaNeural", "gtts_lang": "ar"},

    # ---------------- English ----------------
    {"id": 2001, "name": "Guy - United States Male", "language": "en", "region": "United States",
     "gender": "Male", "engine": "edge", "edge_voice": "en-US-GuyNeural", "gtts_lang": "en"},
    {"id": 2002, "name": "Aria - United States Female", "language": "en", "region": "United States",
     "gender": "Female", "engine": "edge", "edge_voice": "en-US-AriaNeural", "gtts_lang": "en"},
    {"id": 2003, "name": "Jenny - United States Female", "language": "en", "region": "United States",
     "gender": "Female", "engine": "edge", "edge_voice": "en-US-JennyNeural", "gtts_lang": "en"},
    {"id": 2004, "name": "Christopher - United States Male", "language": "en", "region": "United States",
     "gender": "Male", "engine": "edge", "edge_voice": "en-US-ChristopherNeural", "gtts_lang": "en"},
    {"id": 2005, "name": "Eric - United States Male", "language": "en", "region": "United States",
     "gender": "Male", "engine": "edge", "edge_voice": "en-US-EricNeural", "gtts_lang": "en"},
    {"id": 2006, "name": "Michelle - United States Female", "language": "en", "region": "United States",
     "gender": "Female", "engine": "edge", "edge_voice": "en-US-MichelleNeural", "gtts_lang": "en"},
    {"id": 2007, "name": "Ana - United States Female (Child)", "language": "en", "region": "United States",
     "gender": "Female", "engine": "edge", "edge_voice": "en-US-AnaNeural", "gtts_lang": "en"},
    {"id": 2010, "name": "Ryan - United Kingdom Male", "language": "en", "region": "United Kingdom",
     "gender": "Male", "engine": "edge", "edge_voice": "en-GB-RyanNeural", "gtts_lang": "en-uk"},
    {"id": 2011, "name": "Sonia - United Kingdom Female", "language": "en", "region": "United Kingdom",
     "gender": "Female", "engine": "edge", "edge_voice": "en-GB-SoniaNeural", "gtts_lang": "en-uk"},
    {"id": 2012, "name": "Libby - United Kingdom Female", "language": "en", "region": "United Kingdom",
     "gender": "Female", "engine": "edge", "edge_voice": "en-GB-LibbyNeural", "gtts_lang": "en-uk"},
    {"id": 2013, "name": "Maisie - United Kingdom Female (Child)", "language": "en", "region": "United Kingdom",
     "gender": "Female", "engine": "edge", "edge_voice": "en-GB-MaisieNeural", "gtts_lang": "en-uk"},
    {"id": 2020, "name": "Natasha - Australia Female", "language": "en", "region": "Australia",
     "gender": "Female", "engine": "edge", "edge_voice": "en-AU-NatashaNeural", "gtts_lang": "en-au"},
    {"id": 2021, "name": "William - Australia Male", "language": "en", "region": "Australia",
     "gender": "Male", "engine": "edge", "edge_voice": "en-AU-WilliamNeural", "gtts_lang": "en-au"},
    {"id": 2030, "name": "Liam - Canada Male", "language": "en", "region": "Canada",
     "gender": "Male", "engine": "edge", "edge_voice": "en-CA-LiamNeural", "gtts_lang": "en-ca"},
    {"id": 2031, "name": "Clara - Canada Female", "language": "en", "region": "Canada",
     "gender": "Female", "engine": "edge", "edge_voice": "en-CA-ClaraNeural", "gtts_lang": "en-ca"},
    {"id": 2040, "name": "Prabhat - India Male", "language": "en", "region": "India",
     "gender": "Male", "engine": "edge", "edge_voice": "en-IN-PrabhatNeural", "gtts_lang": "en-in"},
    {"id": 2041, "name": "Neerja - India Female", "language": "en", "region": "India",
     "gender": "Female", "engine": "edge", "edge_voice": "en-IN-NeerjaNeural", "gtts_lang": "en-in"},

    # ---------------- Spanish ----------------
    {"id": 3001, "name": "Alvaro - Spain Male", "language": "es", "region": "Spain",
     "gender": "Male", "engine": "edge", "edge_voice": "es-ES-AlvaroNeural", "gtts_lang": "es"},
    {"id": 3002, "name": "Elvira - Spain Female", "language": "es", "region": "Spain",
     "gender": "Female", "engine": "edge", "edge_voice": "es-ES-ElviraNeural", "gtts_lang": "es"},
    {"id": 3010, "name": "Jorge - Mexico Male", "language": "es", "region": "Mexico",
     "gender": "Male", "engine": "edge", "edge_voice": "es-MX-JorgeNeural", "gtts_lang": "es"},
    {"id": 3011, "name": "Dalia - Mexico Female", "language": "es", "region": "Mexico",
     "gender": "Female", "engine": "edge", "edge_voice": "es-MX-DaliaNeural", "gtts_lang": "es"},
    {"id": 3020, "name": "Tomas - Argentina Male", "language": "es", "region": "Argentina",
     "gender": "Male", "engine": "edge", "edge_voice": "es-AR-TomasNeural", "gtts_lang": "es"},
    {"id": 3021, "name": "Elena - Argentina Female", "language": "es", "region": "Argentina",
     "gender": "Female", "engine": "edge", "edge_voice": "es-AR-ElenaNeural", "gtts_lang": "es"},

    # ---------------- French ----------------
    {"id": 4001, "name": "Henri - France Male", "language": "fr", "region": "France",
     "gender": "Male", "engine": "edge", "edge_voice": "fr-FR-HenriNeural", "gtts_lang": "fr"},
    {"id": 4002, "name": "Denise - France Female", "language": "fr", "region": "France",
     "gender": "Female", "engine": "edge", "edge_voice": "fr-FR-DeniseNeural", "gtts_lang": "fr"},
    {"id": 4003, "name": "Vivienne - France Female", "language": "fr", "region": "France",
     "gender": "Female", "engine": "edge", "edge_voice": "fr-FR-VivienneMultilingualNeural", "gtts_lang": "fr"},
    {"id": 4010, "name": "Antoine - Canada (French) Male", "language": "fr", "region": "Canada",
     "gender": "Male", "engine": "edge", "edge_voice": "fr-CA-AntoineNeural", "gtts_lang": "fr-ca"},
    {"id": 4011, "name": "Sylvie - Canada (French) Female", "language": "fr", "region": "Canada",
     "gender": "Female", "engine": "edge", "edge_voice": "fr-CA-SylvieNeural", "gtts_lang": "fr-ca"},

    # ---------------- German ----------------
    {"id": 5001, "name": "Conrad - Germany Male", "language": "de", "region": "Germany",
     "gender": "Male", "engine": "edge", "edge_voice": "de-DE-ConradNeural", "gtts_lang": "de"},
    {"id": 5002, "name": "Katja - Germany Female", "language": "de", "region": "Germany",
     "gender": "Female", "engine": "edge", "edge_voice": "de-DE-KatjaNeural", "gtts_lang": "de"},
    {"id": 5003, "name": "Florian - Germany Male", "language": "de", "region": "Germany",
     "gender": "Male", "engine": "edge", "edge_voice": "de-DE-FlorianMultilingualNeural", "gtts_lang": "de"},

    # ---------------- Italian ----------------
    {"id": 6001, "name": "Diego - Italy Male", "language": "it", "region": "Italy",
     "gender": "Male", "engine": "edge", "edge_voice": "it-IT-DiegoNeural", "gtts_lang": "it"},
    {"id": 6002, "name": "Elsa - Italy Female", "language": "it", "region": "Italy",
     "gender": "Female", "engine": "edge", "edge_voice": "it-IT-ElsaNeural", "gtts_lang": "it"},
    {"id": 6003, "name": "Isabella - Italy Female", "language": "it", "region": "Italy",
     "gender": "Female", "engine": "edge", "edge_voice": "it-IT-IsabellaNeural", "gtts_lang": "it"},

    # ---------------- Portuguese ----------------
    {"id": 7001, "name": "Antonio - Brazil Male", "language": "pt", "region": "Brazil",
     "gender": "Male", "engine": "edge", "edge_voice": "pt-BR-AntonioNeural", "gtts_lang": "pt"},
    {"id": 7002, "name": "Francisca - Brazil Female", "language": "pt", "region": "Brazil",
     "gender": "Female", "engine": "edge", "edge_voice": "pt-BR-FranciscaNeural", "gtts_lang": "pt"},
    {"id": 7010, "name": "Duarte - Portugal Male", "language": "pt", "region": "Portugal",
     "gender": "Male", "engine": "edge", "edge_voice": "pt-PT-DuarteNeural", "gtts_lang": "pt-pt"},
    {"id": 7011, "name": "Raquel - Portugal Female", "language": "pt", "region": "Portugal",
     "gender": "Female", "engine": "edge", "edge_voice": "pt-PT-RaquelNeural", "gtts_lang": "pt-pt"},

    # ---------------- Russian ----------------
    {"id": 8001, "name": "Dmitry - Russia Male", "language": "ru", "region": "Russia",
     "gender": "Male", "engine": "edge", "edge_voice": "ru-RU-DmitryNeural", "gtts_lang": "ru"},
    {"id": 8002, "name": "Svetlana - Russia Female", "language": "ru", "region": "Russia",
     "gender": "Female", "engine": "edge", "edge_voice": "ru-RU-SvetlanaNeural", "gtts_lang": "ru"},

    # ---------------- Turkish ----------------
    {"id": 9001, "name": "Ahmet - Turkey Male", "language": "tr", "region": "Turkey",
     "gender": "Male", "engine": "edge", "edge_voice": "tr-TR-AhmetNeural", "gtts_lang": "tr"},
    {"id": 9002, "name": "Emel - Turkey Female", "language": "tr", "region": "Turkey",
     "gender": "Female", "engine": "edge", "edge_voice": "tr-TR-EmelNeural", "gtts_lang": "tr"},

    # ---------------- Japanese ----------------
    {"id": 10001, "name": "Keita - Japan Male", "language": "ja", "region": "Japan",
     "gender": "Male", "engine": "edge", "edge_voice": "ja-JP-KeitaNeural", "gtts_lang": "ja"},
    {"id": 10002, "name": "Nanami - Japan Female", "language": "ja", "region": "Japan",
     "gender": "Female", "engine": "edge", "edge_voice": "ja-JP-NanamiNeural", "gtts_lang": "ja"},

    # ---------------- Korean ----------------
    {"id": 11001, "name": "InJoon - Korea Male", "language": "ko", "region": "Korea",
     "gender": "Male", "engine": "edge", "edge_voice": "ko-KR-InJoonNeural", "gtts_lang": "ko"},
    {"id": 11002, "name": "SunHi - Korea Female", "language": "ko", "region": "Korea",
     "gender": "Female", "engine": "edge", "edge_voice": "ko-KR-SunHiNeural", "gtts_lang": "ko"},

    # ---------------- Chinese ----------------
    {"id": 12001, "name": "Yunxi - Mainland Male", "language": "zh", "region": "Mainland China",
     "gender": "Male", "engine": "edge", "edge_voice": "zh-CN-YunxiNeural", "gtts_lang": "zh-CN"},
    {"id": 12002, "name": "Xiaoxiao - Mainland Female", "language": "zh", "region": "Mainland China",
     "gender": "Female", "engine": "edge", "edge_voice": "zh-CN-XiaoxiaoNeural", "gtts_lang": "zh-CN"},
    {"id": 12003, "name": "Yunyang - Mainland Male (Newscast)", "language": "zh", "region": "Mainland China",
     "gender": "Male", "engine": "edge", "edge_voice": "zh-CN-YunyangNeural", "gtts_lang": "zh-CN"},
    {"id": 12010, "name": "HiuMaan - Hong Kong Female", "language": "zh", "region": "Hong Kong",
     "gender": "Female", "engine": "edge", "edge_voice": "zh-HK-HiuMaanNeural", "gtts_lang": "zh-CN"},
    {"id": 12011, "name": "HsiaoChen - Taiwan Female", "language": "zh", "region": "Taiwan",
     "gender": "Female", "engine": "edge", "edge_voice": "zh-TW-HsiaoChenNeural", "gtts_lang": "zh-TW"},

    # ---------------- Hindi ----------------
    {"id": 13001, "name": "Madhur - India Male", "language": "hi", "region": "India",
     "gender": "Male", "engine": "edge", "edge_voice": "hi-IN-MadhurNeural", "gtts_lang": "hi"},
    {"id": 13002, "name": "Swara - India Female", "language": "hi", "region": "India",
     "gender": "Female", "engine": "edge", "edge_voice": "hi-IN-SwaraNeural", "gtts_lang": "hi"},

    # ---------------- Urdu ----------------
    {"id": 14001, "name": "Asad - Pakistan Male", "language": "ur", "region": "Pakistan",
     "gender": "Male", "engine": "edge", "edge_voice": "ur-PK-AsadNeural", "gtts_lang": "ur"},
    {"id": 14002, "name": "Uzma - Pakistan Female", "language": "ur", "region": "Pakistan",
     "gender": "Female", "engine": "edge", "edge_voice": "ur-PK-UzmaNeural", "gtts_lang": "ur"},

    # ---------------- Persian ----------------
    {"id": 15001, "name": "Farid - Iran Male", "language": "fa", "region": "Iran",
     "gender": "Male", "engine": "edge", "edge_voice": "fa-IR-FaridNeural", "gtts_lang": "fa"},
    {"id": 15002, "name": "Dilara - Iran Female", "language": "fa", "region": "Iran",
     "gender": "Female", "engine": "edge", "edge_voice": "fa-IR-DilaraNeural", "gtts_lang": "fa"},

    # ---------------- Hebrew ----------------
    {"id": 16001, "name": "Avri - Israel Male", "language": "he", "region": "Israel",
     "gender": "Male", "engine": "edge", "edge_voice": "he-IL-AvriNeural", "gtts_lang": "iw"},
    {"id": 16002, "name": "Hila - Israel Female", "language": "he", "region": "Israel",
     "gender": "Female", "engine": "edge", "edge_voice": "he-IL-HilaNeural", "gtts_lang": "iw"},

    # ---------------- Dutch ----------------
    {"id": 17001, "name": "Maarten - Netherlands Male", "language": "nl", "region": "Netherlands",
     "gender": "Male", "engine": "edge", "edge_voice": "nl-NL-MaartenNeural", "gtts_lang": "nl"},
    {"id": 17002, "name": "Colette - Netherlands Female", "language": "nl", "region": "Netherlands",
     "gender": "Female", "engine": "edge", "edge_voice": "nl-NL-ColetteNeural", "gtts_lang": "nl"},

    # ---------------- Polish ----------------
    {"id": 18001, "name": "Marek - Poland Male", "language": "pl", "region": "Poland",
     "gender": "Male", "engine": "edge", "edge_voice": "pl-PL-MarekNeural", "gtts_lang": "pl"},
    {"id": 18002, "name": "Zofia - Poland Female", "language": "pl", "region": "Poland",
     "gender": "Female", "engine": "edge", "edge_voice": "pl-PL-ZofiaNeural", "gtts_lang": "pl"},

    # ---------------- Swedish ----------------
    {"id": 19001, "name": "Mattias - Sweden Male", "language": "sv", "region": "Sweden",
     "gender": "Male", "engine": "edge", "edge_voice": "sv-SE-MattiasNeural", "gtts_lang": "sv"},
    {"id": 19002, "name": "Sofie - Sweden Female", "language": "sv", "region": "Sweden",
     "gender": "Female", "engine": "edge", "edge_voice": "sv-SE-SofieNeural", "gtts_lang": "sv"},

    # ---------------- Indonesian ----------------
    {"id": 20001, "name": "Ardi - Indonesia Male", "language": "id", "region": "Indonesia",
     "gender": "Male", "engine": "edge", "edge_voice": "id-ID-ArdiNeural", "gtts_lang": "id"},
    {"id": 20002, "name": "Gadis - Indonesia Female", "language": "id", "region": "Indonesia",
     "gender": "Female", "engine": "edge", "edge_voice": "id-ID-GadisNeural", "gtts_lang": "id"},

    # ---------------- Thai ----------------
    {"id": 21001, "name": "Niwat - Thailand Male", "language": "th", "region": "Thailand",
     "gender": "Male", "engine": "edge", "edge_voice": "th-TH-NiwatNeural", "gtts_lang": "th"},
    {"id": 21002, "name": "Premwadee - Thailand Female", "language": "th", "region": "Thailand",
     "gender": "Female", "engine": "edge", "edge_voice": "th-TH-PremwadeeNeural", "gtts_lang": "th"},

    # ---------------- Vietnamese ----------------
    {"id": 22001, "name": "Nam Minh - Vietnam Male", "language": "vi", "region": "Vietnam",
     "gender": "Male", "engine": "edge", "edge_voice": "vi-VN-NamMinhNeural", "gtts_lang": "vi"},
    {"id": 22002, "name": "Hoai My - Vietnam Female", "language": "vi", "region": "Vietnam",
     "gender": "Female", "engine": "edge", "edge_voice": "vi-VN-HoaiMyNeural", "gtts_lang": "vi"},
]


# Default per-request character limit. Can be lowered by app settings, but
# never raised above this.
DEFAULT_TEXT_LIMIT = 5000


def _normalize(voice: Dict) -> Dict:
    voice = dict(voice)
    voice.setdefault("text_characters_limit", DEFAULT_TEXT_LIMIT)
    voice.setdefault("unlimited", False)
    return voice


VOICES_LIST: List[Dict] = [_normalize(v) for v in _RAW_VOICES]


def _build_voice_index() -> Dict[int, Dict]:
    return {v["id"]: v for v in VOICES_LIST}


VOICE_INDEX: Dict[int, Dict] = _build_voice_index()


def get_voice(voice_id: int) -> Optional[Dict]:
    """Return a voice descriptor for the given id, or None."""
    try:
        voice_id = int(voice_id)
    except (TypeError, ValueError):
        return None
    return VOICE_INDEX.get(voice_id)


def voices_grouped_by_language() -> Dict[str, Dict[str, List[Dict]]]:
    """Return voices grouped as {lang_code: {region: [voice, ...]}}."""
    grouped: Dict[str, Dict[str, List[Dict]]] = {}
    for v in VOICES_LIST:
        lang = v["language"]
        region = v["region"]
        grouped.setdefault(lang, {}).setdefault(region, []).append(v)
    return grouped


def voices_for_language(lang_code: str) -> Dict[str, List[Dict]]:
    """Return voices grouped by region for a specific language."""
    return voices_grouped_by_language().get(lang_code, {})


def public_voice(voice: Dict) -> Dict:
    """Return a JSON-safe public representation of a voice (no internal fields)."""
    return {
        "id": voice["id"],
        "name": voice["name"],
        "language": voice["language"],
        "region": voice["region"],
        "gender": voice["gender"],
        "engine": voice["engine"],
        "text_characters_limit": voice["text_characters_limit"],
    }
