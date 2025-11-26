// streamcore_tts.js - TTS Híbrido (WebAudio + Backend Control)

// Cola de TTS
let ttsQueue = []; // { id, user, message, audio, status: 'pending'|'playing' }
let currentlyPlayingId = null;
let ttsEnabled = true;

// Audio / WebAudio (Solo para pruebas locales en navegador)
let audioCtx = null;
let gainNode = null;
let currentSource = null;

// Valores de control (por defecto)
let controlVolume = 0.8; // 0.0 .. 1.0
let controlSpeed = 1.0;  // 0.5 .. 2.0
let controlPitchSemitones = 0; // -12 .. +12

// ----------------- COMUNICACIÓN CON BACKEND (NUEVO) -----------------
function sendConfigToBackend() {
    // Esta función envía los valores de los sliders a Python
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.update_tts_settings({
            volume: controlVolume, 
            speed: controlSpeed,
            pitch: controlPitchSemitones
        }).catch(err => console.log("Error enviando config al backend:", err));
    }
}

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

// ----------------- REPRODUCCIÓN (LÓGICA HÍBRIDA) -----------------
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

        // [MODIFICACIÓN IMPORTANTE]
        // Si NO hay audio Base64, asumimos que el Backend (Python) lo está reproduciendo.
        // Aquí solo mostramos la animación visual para no duplicar el sonido.
        if(!base64Audio){
            console.log("Audio gestionado por Backend (Segundo plano). Modo visual activo.");
            
            // Calculamos duración visual estimada (100ms por letra + 1s base)
            const estimatedDuration = 1000 + (next.message.length * 100);

            setTimeout(() => {
                finishCurrentAndContinue(next.id);
            }, estimatedDuration);
            
            return; // SALIR AQUÍ: No reproducir nada en el navegador
        }

        // [SI HAY AUDIO] (Ej: Botón de prueba "Test TTS")
        // Reproducimos usando el navegador
        const response = await fetch(base64Audio);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

        if(currentSource){
            currentSource.stop();
        }

        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        
        // Aplicamos efectos locales (Solo funcionan en pruebas web)
        source.playbackRate.value = controlSpeed;
        source.detune.value = controlPitchSemitones * 100; 
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
    // Si estamos reproduciendo audio web (Test), lo detenemos
    if(currentlyPlayingId===id && currentSource){
        currentSource.stop();
        currentSource = null;
    }
    // Si es backend, no podemos detener el audio de python desde aquí fácilmente,
    // pero limpiamos la UI inmediatamente.
    
    finishCurrentAndContinue(id);
}

function removeTTS(id){
    // Si intentamos borrar algo que no se está reproduciendo
    if (currentlyPlayingId !== id) {
        ttsQueue = ttsQueue.filter(i=>i.id!==id);
        updateQueueUI();
    } else {
        skipTTS(id);
    }
}

// ----------------- Sliders / Controles -----------------
function applyControlsPro(){
    // Aplica cambios al audio web actual (si hay uno sonando)
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
            applyControlsPro();     // Visual/Web
            sendConfigToBackend();  // Enviar a Python
        });
        // Cargar valor inicial
        controlSpeed = parseFloat(speedSlider.value) || controlSpeed;
        if(speedValue) speedValue.textContent = controlSpeed.toFixed(1)+'x';
    }

    if(pitchSlider){
        pitchSlider.addEventListener('input', function(){
            controlPitchSemitones = parseInt(this.value,10)||0;
            if(pitchValue) pitchValue.textContent = `${controlPitchSemitones} st`;
            applyControlsPro();
            sendConfigToBackend();
        });
        controlPitchSemitones = parseInt(pitchSlider.value,10)||controlPitchSemitones;
        if(pitchValue) pitchValue.textContent = `${controlPitchSemitones} st`;
    }

    if(volumeSlider){
        volumeSlider.addEventListener('input', function(){
            // Convertir 0-100 a 0.0-1.0
            controlVolume = Math.max(0, Math.min(1, parseFloat(this.value)/100));
            if(volumeValue) volumeValue.textContent = Math.round(controlVolume*100)+'%';
            applyControlsPro();     // Visual/Web
            sendConfigToBackend();  // Enviar a Python (¡Importante!)
        });
        controlVolume = volumeSlider.value ? Math.max(0, Math.min(1, parseFloat(volumeSlider.value)/100)) : controlVolume;
        if(volumeValue) volumeValue.textContent = Math.round(controlVolume*100)+'%';
    }

    // Enviar configuración inicial al arrancar
    setTimeout(sendConfigToBackend, 1000);
}

// ----------------- Eventos pywebview -----------------
window.addEventListener("tts:new", async (ev) => {
    try {
        const data = ev.detail || {};
        const user = data.user || 'Anon';
        const message = data.message || '';
        const audio = data.audio || null; // Si es null, es modo Backend
        enqueueTTS(user, message, audio);
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

    // Solicitamos a la API que genere el audio y nos lo devuelva (Base64)
    // para probarlo aquí mismo en el navegador.
    const res = await window.pywebview.api.generate_tts(text);
    
    if(!res || !res.success || !res.data) return alert("No se pudo generar el TTS.");

    enqueueTTS('Prueba', text, res.data);
}