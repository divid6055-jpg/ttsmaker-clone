/**
 * TTSMaker Clone - main client script.
 *
 * Everything here speaks to the real Django/edge-tts backend. We do NOT keep
 * a parallel mirrored voice database on the client; instead, /api/voices/ is
 * the single source of truth.
 */
(function () {
    "use strict";

    const cfg = window.TTS_CONFIG || {};
    const rtlSet = new Set(cfg.rtlLanguages || []);

    // ---- DOM refs ----
    const $ = (id) => document.getElementById(id);
    const textInput = $("textInput");
    const languageSelect = $("languageSelect");
    const voiceSelect = $("voiceSelect");
    const voiceMeta = $("voiceMeta");
    const formatSelect = $("formatSelect");
    const speedInput = $("speedInput");
    const volumeInput = $("volumeInput");
    const pitchInput = $("pitchInput");
    const speedValue = $("speedValue");
    const volumeValue = $("volumeValue");
    const pitchValue = $("pitchValue");
    const convertBtn = $("convertBtn");
    const clearBtn = $("clearBtn");
    const statusBox = $("statusBox");
    const resultBox = $("resultBox");
    const audioPlayer = $("audioPlayer");
    const downloadLink = $("downloadLink");
    const resultMeta = $("resultMeta");
    const currentChars = $("currentChars");
    const quotaInfo = $("quotaInfo");
    const htmlRoot = $("htmlRoot");

    // ---- State ----
    let voicesCache = {}; // language -> voices array

    // ---- Helpers ----
    function setStatus(message, kind = "info") {
        if (!message) {
            statusBox.hidden = true;
            statusBox.textContent = "";
            statusBox.className = "status-box";
            return;
        }
        statusBox.hidden = false;
        statusBox.textContent = message;
        statusBox.className = `status-box status-${kind}`;
    }

    function applyDirection(langCode) {
        const isRtl = rtlSet.has(langCode);
        const dir = isRtl ? "rtl" : "ltr";
        htmlRoot.setAttribute("dir", dir);
        htmlRoot.setAttribute("lang", langCode);
        // Make textarea follow the chosen language direction so Arabic/RTL
        // input renders naturally.
        textInput.setAttribute("dir", dir);
    }

    async function fetchJson(url, options = {}) {
        const res = await fetch(url, {
            headers: { "Accept": "application/json", "Content-Type": "application/json" },
            credentials: "same-origin",
            ...options,
        });
        let payload = null;
        try { payload = await res.json(); } catch (_) { /* non-JSON */ }
        return { ok: res.ok, status: res.status, payload };
    }

    function formatBytes(bytes) {
        if (!bytes) return "0 B";
        const units = ["B", "KB", "MB", "GB"];
        let i = 0;
        while (bytes >= 1024 && i < units.length - 1) { bytes /= 1024; i++; }
        return `${bytes.toFixed(1)} ${units[i]}`;
    }

    function updateCharCounter() {
        const len = textInput.value.length;
        currentChars.textContent = len;
        currentChars.style.color = (len > cfg.maxCharsPerRequest * 0.9) ? "#d97706" : "";
    }

    async function refreshQuota() {
        const { ok, payload } = await fetchJson("/api/quota/");
        if (ok && payload) {
            quotaInfo.innerHTML =
                `<i class="fas fa-chart-line" aria-hidden="true"></i> ` +
                `Daily quota: <strong>${payload.used.toLocaleString()}</strong> / ${payload.daily_limit.toLocaleString()} ` +
                `(${payload.remaining.toLocaleString()} remaining)`;
        } else {
            quotaInfo.innerHTML = `<i class="fas fa-triangle-exclamation"></i> Quota unavailable`;
        }
    }

    async function loadVoicesForLanguage(langCode) {
        applyDirection(langCode);
        voiceSelect.innerHTML = `<option>Loading...</option>`;
        voiceMeta.textContent = "";

        if (voicesCache[langCode]) {
            populateVoiceSelect(voicesCache[langCode]);
            return;
        }
        const { ok, payload } = await fetchJson(`/api/voices/?language=${encodeURIComponent(langCode)}`);
        if (!ok || !payload || payload.error_code !== 0) {
            voiceSelect.innerHTML = `<option value="">(no voices)</option>`;
            voiceMeta.textContent = "Could not load voices for this language.";
            return;
        }
        voicesCache[langCode] = payload.voices_detailed_list || [];
        populateVoiceSelect(voicesCache[langCode]);
    }

    function populateVoiceSelect(voices) {
        if (!voices.length) {
            voiceSelect.innerHTML = `<option value="">(no voices available)</option>`;
            voiceMeta.textContent = "";
            return;
        }
        // Group by region.
        const byRegion = {};
        for (const v of voices) {
            (byRegion[v.region] = byRegion[v.region] || []).push(v);
        }
        const opts = [];
        for (const region of Object.keys(byRegion).sort()) {
            opts.push(`<optgroup label="${region}">`);
            for (const v of byRegion[region]) {
                opts.push(`<option value="${v.id}" data-engine="${v.engine}" data-gender="${v.gender}">${escapeHtml(v.name)}</option>`);
            }
            opts.push(`</optgroup>`);
        }
        voiceSelect.innerHTML = opts.join("");
        onVoiceChanged();
    }

    function onVoiceChanged() {
        const opt = voiceSelect.options[voiceSelect.selectedIndex];
        if (!opt || !opt.dataset) { voiceMeta.textContent = ""; return; }
        voiceMeta.innerHTML =
            `Engine: <strong>${opt.dataset.engine || "edge"}</strong> · ` +
            `Gender: <strong>${opt.dataset.gender || "-"}</strong>`;
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, c => ({
            "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
        }[c]));
    }

    async function onConvert() {
        const text = textInput.value.trim();
        if (!text) { setStatus("Please enter some text to convert.", "warning"); return; }
        if (text.length > cfg.maxCharsPerRequest) {
            setStatus(`Text is too long. Maximum is ${cfg.maxCharsPerRequest} characters per request.`, "error");
            return;
        }
        const voiceId = voiceSelect.value;
        if (!voiceId) { setStatus("Please pick a voice.", "warning"); return; }

        const body = {
            text,
            voice_id: parseInt(voiceId, 10),
            audio_format: formatSelect.value,
            audio_speed: parseFloat(speedInput.value),
            audio_volume: parseFloat(volumeInput.value),
            audio_pitch: parseFloat(pitchInput.value),
        };

        convertBtn.disabled = true;
        convertBtn.querySelector("span").textContent = "Converting...";
        setStatus("Synthesizing audio...", "info");
        resultBox.hidden = true;

        try {
            const { ok, status, payload } = await fetchJson("/api/tts/", {
                method: "POST",
                body: JSON.stringify(body),
            });
            if (!ok || !payload || payload.error_code !== 0) {
                const msg = (payload && payload.msg) || `Request failed (HTTP ${status})`;
                setStatus(`Error: ${msg}`, "error");
                if (payload && payload.quota) {
                    quotaInfo.innerHTML =
                        `<i class="fas fa-chart-line"></i> Daily quota: ` +
                        `<strong>${payload.quota.used}</strong> / ${payload.quota.daily_limit}`;
                }
                return;
            }
            setStatus("", null);
            showResult(payload);
            await refreshQuota();
        } catch (err) {
            setStatus(`Network error: ${err.message || err}`, "error");
        } finally {
            convertBtn.disabled = false;
            convertBtn.querySelector("span").textContent = "Convert to speech";
        }
    }

    function showResult(payload) {
        resultBox.hidden = false;
        audioPlayer.src = payload.audio_download_url;
        audioPlayer.load();
        downloadLink.href = payload.audio_download_url;
        const v = payload.voice || {};
        resultMeta.innerHTML =
            `<i class="fas fa-microphone"></i> ${escapeHtml(v.name || "")} ` +
            `· <i class="fas fa-file-audio"></i> ${(payload.audio_file_format || "mp3").toUpperCase()} ` +
            `· ${formatBytes(payload.file_size_bytes)} ` +
            `· engine: <strong>${escapeHtml(payload.engine_used || "edge")}</strong>`;
        resultBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function onClear() {
        textInput.value = "";
        updateCharCounter();
        resultBox.hidden = true;
        setStatus("", null);
        textInput.focus();
    }

    function wireRange(input, valueEl) {
        const update = () => { valueEl.textContent = `${parseFloat(input.value).toFixed(1)}×`; };
        input.addEventListener("input", update);
        update();
    }

    // ---- Init ----
    document.addEventListener("DOMContentLoaded", async () => {
        textInput.addEventListener("input", updateCharCounter);
        languageSelect.addEventListener("change", e => loadVoicesForLanguage(e.target.value));
        voiceSelect.addEventListener("change", onVoiceChanged);
        convertBtn.addEventListener("click", onConvert);
        clearBtn.addEventListener("click", onClear);
        wireRange(speedInput, speedValue);
        wireRange(volumeInput, volumeValue);
        wireRange(pitchInput, pitchValue);

        // Mobile menu (graceful no-op if missing).
        const mobileMenuBtn = $("mobileMenuBtn");
        if (mobileMenuBtn) {
            mobileMenuBtn.addEventListener("click", () => {
                document.querySelector(".nav")?.classList.toggle("nav-open");
            });
        }

        updateCharCounter();
        await Promise.all([
            loadVoicesForLanguage(languageSelect.value),
            refreshQuota(),
        ]);
    });
})();
