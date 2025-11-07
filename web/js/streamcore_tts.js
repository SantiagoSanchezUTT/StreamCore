// Sample TTS queue data
const sampleQueue = [
    {
        id: 1,
        user: 'StreamFan123',
        amount: 5.00,
        currency: 'USD',
        message: '¡Hola streamer! Gracias por el contenido increíble. Sigue así, eres el mejor.',
        timestamp: new Date(Date.now() - 30000),
        status: 'playing'
    },
    {
        id: 2,
        user: 'GamerPro456',
        amount: 10.00,
        currency: 'USD',
        message: 'Me encanta tu stream, especialmente cuando juegas este tipo de juegos. ¿Podrías jugar más RPGs?',
        timestamp: new Date(Date.now() - 60000),
        status: 'pending'
    },
    {
        id: 3,
        user: 'ChatModerator',
        amount: 2.50,
        currency: 'USD',
        message: 'Saludos desde México. Tu comunidad es increíble y el chat siempre está muy activo.',
        timestamp: new Date(Date.now() - 120000),
        status: 'pending'
    }
];

let ttsQueue = [...sampleQueue];
let ttsEnabled = true;
let currentlyPlaying = null;

// Initialize TTS interface
function initializeTTS() {
    renderQueue();
    updateQueueCount();
    setupSliders();
    updateTTSStatus();
}

// Render TTS queue
function renderQueue() {
    const queueList = document.getElementById('queueList');
    queueList.innerHTML = '';

    if (ttsQueue.length === 0) {
        queueList.innerHTML = `
                    <div style="text-align: center; padding: 40px; color: #A9A9A9;">
                        <svg width="48" height="48" fill="currentColor" viewBox="0 0 20 20" style="margin-bottom: 16px; opacity: 0.5;">
                            <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217z"/>
                        </svg>
                        <p>No hay mensajes en la cola</p>
                        <p style="font-size: 12px; margin-top: 8px;">Los mensajes de donaciones aparecerán aquí</p>
                    </div>
                `;
        return;
    }

    ttsQueue.forEach(item => {
        const queueItem = document.createElement('div');
        queueItem.className = `queue-item ${item.status}`;
        queueItem.innerHTML = `
                    <div class="queue-item-header">
                        <div class="queue-item-user">${item.user}</div>
                        <div class="queue-item-amount">$${item.amount.toFixed(2)} ${item.currency}</div>
                    </div>
                    
                    <div class="queue-item-message">${item.message}</div>
                    
                    <div class="queue-item-actions">
                        ${item.status === 'pending' ? `
                            <button class="queue-btn play" onclick="playMessage(${item.id})">
                                <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"/>
                                </svg>
                                Reproducir
                            </button>
                        ` : ''}
                        
                        ${item.status === 'playing' ? `
                            <button class="queue-btn skip" onclick="skipMessage(${item.id})">
                                <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798l-5.445-3.63z"/>
                                </svg>
                                Saltar
                            </button>
                        ` : ''}
                        
                        <button class="queue-btn remove" onclick="removeMessage(${item.id})">
                            <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
                            </svg>
                            Eliminar
                        </button>
                    </div>
                `;
        queueList.appendChild(queueItem);
    });
}

// Update queue count
function updateQueueCount() {
    const queueCount = document.getElementById('queueCount');
    const count = ttsQueue.length;
    queueCount.textContent = count === 0 ? 'Cola vacía' :
        count === 1 ? '1 mensaje' :
            `${count} mensajes`;
}

// Setup sliders
function setupSliders() {
    const speedSlider = document.getElementById('speedSlider');
    const pitchSlider = document.getElementById('pitchSlider');
    const volumeSlider = document.getElementById('volumeSlider');

    const speedValue = document.getElementById('speedValue');
    const pitchValue = document.getElementById('pitchValue');
    const volumeValue = document.getElementById('volumeValue');

    speedSlider.addEventListener('input', function () {
        speedValue.textContent = this.value + 'x';
    });

    pitchSlider.addEventListener('input', function () {
        pitchValue.textContent = this.value;
    });

    volumeSlider.addEventListener('input', function () {
        volumeValue.textContent = this.value + '%';
    });
}

// Update TTS status
function updateTTSStatus() {
    const statusElement = document.getElementById('ttsStatus');
    const enableBtn = document.getElementById('enableTtsBtn');

    if (ttsEnabled) {
        statusElement.className = 'tts-status';
        statusElement.innerHTML = '<div class="status-dot"></div>Activo';
        enableBtn.innerHTML = `
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"/>
                    </svg>
                    Pausar TTS
                `;
        enableBtn.className = 'btn warning';
    } else {
        statusElement.className = 'tts-status disabled';
        statusElement.innerHTML = '<div class="status-dot"></div>Desactivado';
        enableBtn.innerHTML = `
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"/>
                    </svg>
                    Activar TTS
                `;
        enableBtn.className = 'btn success';
    }
}

// Toggle TTS
function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    updateTTSStatus();

    if (!ttsEnabled) {
        // Stop current playback
        stopCurrentPlayback();
    }
}

// Play message
function playMessage(id) {
    if (!ttsEnabled) return;

    const message = ttsQueue.find(m => m.id === id);
    if (!message) return;

    // Stop current playback
    stopCurrentPlayback();

    // Set as playing
    ttsQueue.forEach(m => m.status = m.id === id ? 'playing' : 'pending');
    currentlyPlaying = id;

    // Simulate TTS playback
    simulateTTSPlayback(message);

    renderQueue();
}

// Skip message
function skipMessage(id) {
    stopCurrentPlayback();

    // Remove from queue or mark as completed
    ttsQueue = ttsQueue.filter(m => m.id !== id);

    // Play next message if available
    const nextMessage = ttsQueue.find(m => m.status === 'pending');
    if (nextMessage && ttsEnabled) {
        setTimeout(() => playMessage(nextMessage.id), 500);
    }

    renderQueue();
    updateQueueCount();
}

// Remove message
function removeMessage(id) {
    if (currentlyPlaying === id) {
        stopCurrentPlayback();
    }

    ttsQueue = ttsQueue.filter(m => m.id !== id);
    renderQueue();
    updateQueueCount();
}

// Clear queue
function clearQueue() {
    if (confirm('¿Estás seguro de que quieres limpiar toda la cola de TTS?')) {
        stopCurrentPlayback();
        ttsQueue = [];
        renderQueue();
        updateQueueCount();
    }
}

// Stop current playback
function stopCurrentPlayback() {
    if (currentlyPlaying) {
        const playingMessage = ttsQueue.find(m => m.id === currentlyPlaying);
        if (playingMessage) {
            playingMessage.status = 'pending';
        }
        currentlyPlaying = null;
    }
}

// Simulate TTS playback
function simulateTTSPlayback(message) {
    const duration = Math.max(3000, message.message.length * 100); // Simulate reading time

    setTimeout(() => {
        if (currentlyPlaying === message.id) {
            // Message finished, remove from queue
            ttsQueue = ttsQueue.filter(m => m.id !== message.id);
            currentlyPlaying = null;

            // Play next message if available
            const nextMessage = ttsQueue.find(m => m.status === 'pending');
            if (nextMessage && ttsEnabled) {
                setTimeout(() => playMessage(nextMessage.id), 1000);
            }

            renderQueue();
            updateQueueCount();
        }
    }, duration);
}

// Test TTS
function testTTS() {
    const testMessage = document.getElementById('testMessage').value.trim();
    if (!testMessage) return;

    // Create a test message
    const testItem = {
        id: Date.now(),
        user: 'Prueba',
        amount: 0,
        currency: 'USD',
        message: testMessage,
        timestamp: new Date(),
        status: 'pending'
    };

    // Add to front of queue
    ttsQueue.unshift(testItem);
    renderQueue();
    updateQueueCount();

    // Play immediately
    if (ttsEnabled) {
        playMessage(testItem.id);
    }
}

// Add new donation message (simulated)
function addDonationMessage(user, amount, message) {
    const newMessage = {
        id: Date.now(),
        user: user,
        amount: amount,
        currency: 'USD',
        message: message,
        timestamp: new Date(),
        status: 'pending'
    };

    ttsQueue.push(newMessage);
    renderQueue();
    updateQueueCount();

    // Auto-play if no message is currently playing
    if (ttsEnabled && !currentlyPlaying) {
        setTimeout(() => playMessage(newMessage.id), 500);
    }
}

// Simulate new donations
function simulateNewDonations() {
    const sampleDonations = [
        { user: 'NewViewer789', amount: 3.00, message: '¡Primera vez viendo tu stream y me encanta!' },
        { user: 'RegularFan', amount: 7.50, message: 'Sigue así con el contenido, siempre me divierte mucho.' },
        { user: 'BigSupporter', amount: 25.00, message: 'Donación para ayudar con el setup nuevo que mencionaste.' }
    ];

    setInterval(() => {
        if (Math.random() < 0.3) { // 30% chance every 10 seconds
            const donation = sampleDonations[Math.floor(Math.random() * sampleDonations.length)];
            addDonationMessage(donation.user, donation.amount, donation.message);
        }
    }, 10000);
}

// Platform selector functionality
document.querySelectorAll('.platform-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        // Remove active class from all buttons
        document.querySelectorAll('.platform-btn').forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        this.classList.add('active');

        // Get platform colors
        const platformColors = {
            'youtube': { primary: '#FF0000', glow: 'rgba(255, 0, 0, 0.2)' },
            'twitch': { primary: '#9146FF', glow: 'rgba(145, 70, 255, 0.2)' },
            'tiktok': { primary: '#25F4EE', glow: 'rgba(37, 244, 238, 0.2)' },
            'kick': { primary: '#53FC18', glow: 'rgba(83, 252, 24, 0.2)' }
        };

        // Determine platform
        let platform = 'twitch'; // default
        if (this.classList.contains('youtube')) platform = 'youtube';
        else if (this.classList.contains('tiktok')) platform = 'tiktok';
        else if (this.classList.contains('kick')) platform = 'kick';

        const colors = platformColors[platform];

        // Update connection status
        const platformText = this.textContent.trim();
        const statusText = document.querySelector('.connection-status span');
        statusText.textContent = `Conectado a ${platformText}`;

        // Update connection status colors
        const connectionStatus = document.querySelector('.connection-status');
        const statusDot = document.querySelector('.status-dot');
        connectionStatus.style.background = colors.glow;
        connectionStatus.style.borderColor = colors.primary + '50';
        statusDot.style.background = colors.primary;

        // Update active nav item color
        const activeNavItem = document.querySelector('.nav-item.active');
        if (activeNavItem) {
            activeNavItem.style.background = colors.glow;
            activeNavItem.style.borderColor = colors.primary;
            activeNavItem.style.boxShadow = `0 0 20px ${colors.glow}`;
        }
    });
});

// Navigation functionality
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function () {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});

// Initialize the TTS interface
initializeTTS();

// Start simulating new donations
simulateNewDonations();

(function () { function c() { var b = a.contentDocument || a.contentWindow.document; if (b) { var d = b.createElement('script'); d.innerHTML = "window.__CF$cv$params={r:'9923032f017f55c3',t:'MTc2MTA3MzM3OS4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);"; b.getElementsByTagName('head')[0].appendChild(d) } } if (document.body) { var a = document.createElement('iframe'); a.height = 1; a.width = 1; a.style.position = 'absolute'; a.style.top = 0; a.style.left = 0; a.style.border = 'none'; a.style.visibility = 'hidden'; document.body.appendChild(a); if ('loading' !== document.readyState) c(); else if (window.addEventListener) document.addEventListener('DOMContentLoaded', c); else { var e = document.onreadystatechange || function () { }; document.onreadystatechange = function (b) { e(b); 'loading' !== document.readyState && (document.onreadystatechange = e, c()) } } } })();