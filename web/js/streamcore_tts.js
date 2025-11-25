// streamcore_tts.js - TTS con WebAudio profesional (pitch real, speed real)

// Cola de TTS
let ttsQueue = []; // { id, user, message, audio, status: 'pending'|'playing' }
let currentlyPlayingId = null;
let ttsEnabled = true;

// Audio / WebAudio
let audioCtx = null;
let gainNode = null;
let currentSource = null;

// Valores de control (por defecto)
let controlVolume = 0.8; // 0..1
let controlSpeed = 1.0;  // multiplicador (0.5 .. 2)
let controlPitchSemitones = 0; // semitones (-12 .. +12)

// ----------------- UTILIDADES -----------------
function escapeHtml(text){
    return String(text || "").replace(/[&<>"']/g, function(m){
        return ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;" })[m];
    });
}

// ----------------- UI / Cola -----------------
function updateQueueUI(){
    const list = document.getElementById('queueList');
    const count = document.getElementById('queueCount');
    if(!list || !count) return;

    list.innerHTML = '';
    if(ttsQueue.length === 0){
        list.innerHTML = `<div style="padding:24px; color:#A9A9A9;">No hay mensajes en la cola</div>`;
        count.textContent = 'Cola vacía';
        return;
    }

    count.textContent = ttsQueue.length === 1 ? '1 mensaje' : `${ttsQueue.length} mensajes`;

    ttsQueue.forEach(item=>{
        const div = document.createElement('div');
        div.className = 'queue-item ' + (item.status || 'pending');
        div.style.padding = '12px';
        div.style.borderBottom = '1px solid rgba(255,255,255,0.03)';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="font-size:14px;">${escapeHtml(item.user)}</strong>
                <span style="font-size:12px; opacity:0.8;">${item.status === 'playing' ? 'Reproduciendo' : 'En cola'}</span>
            </div>
            <div style="margin-top:8px; font-size:13px;">${escapeHtml(item.message)}</div>
            <div style="margin-top:8px;">
                <button class="btn" onclick="skipTTS(${item.id})" style="margin-right:8px;">Saltar</button>
                <button class="btn" onclick="removeTTS(${item.id})">Eliminar</button>
            </div>
        `;
        list.appendChild(div);
    });
}

function enqueueTTS(user, message, audioBase64=null){
    const item = {
        id: Date.now() + Math.floor(Math.random()*999),
        user: user || 'Anon',
        message: message || '',
        audio: audioBase64 || null,
        status: 'pending'
    };
    ttsQueue.push(item);
    updateQueueUI();

    if(!currentlyPlayingId && ttsEnabled){
        playNextTTS();
    }
}

// ----------------- WebAudio Setup -----------------
function setupAudioSystemPro(){
    if(!audioCtx){
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    if(!gainNode){
        gainNode = audioCtx.createGain();
        gainNode.gain.value = controlVolume;
        gainNode.connect(audioCtx.destination);
    }
}

// ----------------- Reproducción profesional -----------------
async function playNextTTS(){
    if(!ttsEnabled) return;
    if(currentlyPlayingId) return;

    const next = ttsQueue.find(i=>i.status==='pending');
    if(!next) return;

    next.status = 'playing';
    currentlyPlayingId = next.id;
    updateQueueUI();

    setupAudioSystemPro();

    try {
        let base64Audio = next.audio;

        if(!base64Audio){
            if(window.pywebview && window.pywebview.api && window.pywebview.api.generate_tts){
                const res = await window.pywebview.api.generate_tts(next.message);
                if(res && res.success && res.data){
                    base64Audio = res.data;
                } else {
                    console.warn('generate_tts fallback falló', res);
                    finishCurrentAndContinue(next.id);
                    return;
                }
            } else {
                console.warn('No hay audio ni API para generar TTS');
                finishCurrentAndContinue(next.id);
                return;
            }
        }

        // Decodificar base64 a ArrayBuffer
        const response = await fetch(base64Audio);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

        // Detener cualquier audio actual
        if(currentSource){
            currentSource.stop();
        }

        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.playbackRate.value = controlSpeed;
        source.detune.value = controlPitchSemitones * 100; // pitch en cents
        source.connect(gainNode);

        source.onended = () => {
            currentSource = null;
            finishCurrentAndContinue(next.id);
        };

        currentSource = source;
        source.start();

    } catch(err){
        console.error('Error reproduciendo TTS:', err);
        finishCurrentAndContinue(next.id);
    }
}

function finishCurrentAndContinue(id){
    ttsQueue = ttsQueue.filter(i=>i.id!==id);
    currentlyPlayingId = null;
    updateQueueUI();
    setTimeout(()=>playNextTTS(), 200);
}

// ----------------- Saltar / Eliminar -----------------
function skipTTS(id){
    if(currentlyPlayingId===id && currentSource){
        currentSource.stop();
        currentSource = null;
        finishCurrentAndContinue(id);
    } else {
        ttsQueue = ttsQueue.filter(i=>i.id!==id);
        updateQueueUI();
    }
}

function removeTTS(id){
    skipTTS(id);
}

// ----------------- Sliders / Controles -----------------
function applyControlsPro(){
    if(gainNode) gainNode.gain.value = controlVolume;
    if(currentSource){
        currentSource.playbackRate.value = controlSpeed;
        currentSource.detune.value = controlPitchSemitones*100;
    }
}

function initControlsBindings(){
    const speedSlider = document.getElementById('speedSlider');
    const pitchSlider = document.getElementById('pitchSlider');
    const volumeSlider = document.getElementById('volumeSlider');

    const speedValue = document.getElementById('speedValue');
    const pitchValue = document.getElementById('pitchValue');
    const volumeValue = document.getElementById('volumeValue');

    if(speedSlider){
        speedSlider.addEventListener('input', function(){
            controlSpeed = parseFloat(this.value) || 1.0;
            if(speedValue) speedValue.textContent = controlSpeed.toFixed(1)+'x';
            applyControlsPro();
        });
        controlSpeed = parseFloat(speedSlider.value) || controlSpeed;
        if(speedValue) speedValue.textContent = controlSpeed.toFixed(1)+'x';
    }

    if(pitchSlider){
        pitchSlider.addEventListener('input', function(){
            controlPitchSemitones = parseInt(this.value,10)||0;
            if(pitchValue) pitchValue.textContent = `${controlPitchSemitones} st`;
            applyControlsPro();
        });
        controlPitchSemitones = parseInt(pitchSlider.value,10)||controlPitchSemitones;
        if(pitchValue) pitchValue.textContent = `${controlPitchSemitones} st`;
    }

    if(volumeSlider){
        volumeSlider.addEventListener('input', function(){
            controlVolume = Math.max(0, Math.min(1, parseFloat(this.value)/100));
            if(volumeValue) volumeValue.textContent = Math.round(controlVolume*100)+'%';
            applyControlsPro();
        });
        controlVolume = volumeSlider.value ? Math.max(0, Math.min(1, parseFloat(volumeSlider.value)/100)) : controlVolume;
        if(volumeValue) volumeValue.textContent = Math.round(controlVolume*100)+'%';
    }
}

// ----------------- Eventos pywebview -----------------
window.addEventListener("tts:new", async (ev) => {
    try {
        const data = ev.detail || {};
        const user = data.user || 'Anon';
        const message = data.message || '';
        const audio = data.audio || null;
        enqueueTTS(user,message,audio);
    } catch(e){ console.error('Error manejando tts:new', e); }
});

// ----------------- Inicialización -----------------
window.addEventListener('DOMContentLoaded',()=>{
    setupAudioSystemPro();
    initControlsBindings();

    const enableBtn = document.getElementById('enableTtsBtn');
    if(enableBtn){
        enableBtn.addEventListener('click', ()=>{
            ttsEnabled = !ttsEnabled;
            enableBtn.textContent = ttsEnabled ? 'Pausar TTS' : 'Activar TTS';
            if(ttsEnabled) playNextTTS();
        });
        enableBtn.textContent = ttsEnabled ? 'Pausar TTS' : 'Activar TTS';
    }

    updateQueueUI();
});

// ----------------- TEST TTS DESDE LA UI -----------------
async function testTTS(){
    const textEl = document.getElementById("testMessage");
    if(!textEl) return alert("No se encontró textarea de prueba.");
    const text = textEl.value.trim();
    if(!text) return alert("Escribe un mensaje primero.");

    if(!window.pywebview || !window.pywebview.api || !window.pywebview.api.generate_tts){
        return alert("API de TTS no disponible.");
    }

    const res = await window.pywebview.api.generate_tts(text);
    if(!res || !res.success || !res.data) return alert("No se pudo generar el TTS.");

    enqueueTTS('Prueba', text, res.data);
}
