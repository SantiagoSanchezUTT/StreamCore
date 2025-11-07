// Sample commands data
const sampleCommands = [
    {
        id: 1,
        name: '!social',
        type: 'text',
        response: 'Sígueme en mis redes: Twitter @streamer | Instagram @streamer | Discord: discord.gg/streamer',
        cooldown: 30,
        permission: 'everyone',
        active: true,
        uses: 342,
        lastUsed: '2 min'
    },
    {
        id: 2,
        name: '!comandos',
        type: 'text',
        response: 'Comandos disponibles: !social, !horario, !discord, !contador, !uptime',
        cooldown: 15,
        permission: 'everyone',
        active: true,
        uses: 156,
        lastUsed: '5 min'
    },
    {
        id: 3,
        name: '!contador',
        type: 'counter',
        response: 'Muertes en el juego: {count}',
        cooldown: 0,
        permission: 'moderators',
        active: true,
        uses: 89,
        lastUsed: '1 min'
    },
    {
        id: 4,
        name: '!horario',
        type: 'text',
        response: 'Stream todos los días de 20:00 a 24:00 (GMT-5)',
        cooldown: 60,
        permission: 'everyone',
        active: true,
        uses: 234,
        lastUsed: '8 min'
    },
    {
        id: 5,
        name: '!discord',
        type: 'text',
        response: 'Únete a nuestro Discord: discord.gg/streamcore',
        cooldown: 45,
        permission: 'subscribers',
        active: true,
        uses: 178,
        lastUsed: '3 min'
    },
    {
        id: 6,
        name: '!uptime',
        type: 'timer',
        response: 'Stream activo por: {time}',
        cooldown: 10,
        permission: 'everyone',
        active: false,
        uses: 67,
        lastUsed: '15 min'
    }
];

let commands = [...sampleCommands];
let editingCommand = null;

// Render commands
function renderCommands(commandsToRender = commands) {
    const grid = document.getElementById('commandsGrid');
    grid.innerHTML = '';

    commandsToRender.forEach(command => {
        const commandCard = document.createElement('div');
        commandCard.className = 'command-card';
        commandCard.innerHTML = `
                    <div class="command-header">
                        <div>
                            <div class="command-name">${command.name}</div>
                            <div class="command-type">${getTypeLabel(command.type)}</div>
                        </div>
                        <div class="command-toggle ${command.active ? 'active' : ''}" onclick="toggleCommand(${command.id})"></div>
                    </div>
                    
                    <div class="command-response">${command.response}</div>
                    
                    <div class="command-stats">
                        <div class="command-stat">
                            <svg class="command-stat-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            ${command.uses} usos
                        </div>
                        <div class="command-stat">
                            <svg class="command-stat-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"/>
                            </svg>
                            ${command.cooldown}s cooldown
                        </div>
                        <div class="command-stat">
                            <svg class="command-stat-icon" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"/>
                            </svg>
                            ${getPermissionLabel(command.permission)}
                        </div>
                    </div>
                    
                    <div class="command-actions">
                        <button class="command-btn edit" onclick="editCommand(${command.id})">
                            <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/>
                            </svg>
                            Editar
                        </button>
                        <button class="command-btn delete" onclick="confirmDeleteCommand(${command.id})">
                            <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                                <path fill-rule="evenodd" d="M4 5a2 2 0 012-2h8a2 2 0 012 2v10a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 112 0v4a1 1 0 11-2 0V9zm4 0a1 1 0 112 0v4a1 1 0 11-2 0V9z"/>
                            </svg>
                            Eliminar
                        </button>
                    </div>
                `;
        grid.appendChild(commandCard);
    });
}

function getTypeLabel(type) {
    const labels = {
        'text': 'Texto',
        'counter': 'Contador',
        'timer': 'Temporizador',
        'moderation': 'Moderación'
    };
    return labels[type] || type;
}

function getPermissionLabel(permission) {
    const labels = {
        'everyone': 'Todos',
        'subscribers': 'Subs',
        'moderators': 'Mods',
        'streamer': 'Streamer'
    };
    return labels[permission] || permission;
}

// Modal functions
function openCommandModal(command = null) {
    const modal = document.getElementById('commandModal');
    const form = document.getElementById('commandForm');
    const title = document.getElementById('modalTitle');
    const deleteBtn = document.getElementById('deleteBtn');

    editingCommand = command;

    if (command) {
        title.textContent = 'Editar Comando';
        document.getElementById('commandName').value = command.name;
        document.getElementById('commandType').value = command.type;
        document.getElementById('commandResponse').value = command.response;
        document.getElementById('commandCooldown').value = command.cooldown;
        document.getElementById('commandPermission').value = command.permission;
        document.getElementById('commandActive').checked = command.active;
        deleteBtn.style.display = 'block';
    } else {
        title.textContent = 'Nuevo Comando';
        form.reset();
        document.getElementById('commandActive').checked = true;
        deleteBtn.style.display = 'none';
    }

    modal.classList.add('active');
}

function closeCommandModal() {
    document.getElementById('commandModal').classList.remove('active');
    editingCommand = null;
}

function editCommand(id) {
    const command = commands.find(c => c.id === id);
    if (command) {
        openCommandModal(command);
    }
}

function confirmDeleteCommand(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este comando?')) {
        commands = commands.filter(c => c.id !== id);
        renderCommands();
    }
}

function deleteCommand() {
    if (editingCommand && confirm('¿Estás seguro de que quieres eliminar este comando?')) {
        commands = commands.filter(c => c.id !== editingCommand.id);
        renderCommands();
        closeCommandModal();
    }
}

function toggleCommand(id) {
    const command = commands.find(c => c.id === id);
    if (command) {
        command.active = !command.active;
        renderCommands();
    }
}

// Form submission
document.getElementById('commandForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('commandName').value,
        type: document.getElementById('commandType').value,
        response: document.getElementById('commandResponse').value,
        cooldown: parseInt(document.getElementById('commandCooldown').value),
        permission: document.getElementById('commandPermission').value,
        active: document.getElementById('commandActive').checked
    };

    if (editingCommand) {
        // Update existing command
        const index = commands.findIndex(c => c.id === editingCommand.id);
        if (index !== -1) {
            commands[index] = { ...commands[index], ...formData };
        }
    } else {
        // Add new command
        const newCommand = {
            id: Date.now(),
            ...formData,
            uses: 0,
            lastUsed: 'Nunca'
        };
        commands.push(newCommand);
    }

    renderCommands();
    closeCommandModal();
});

// Search and filter functionality
document.getElementById('searchInput').addEventListener('input', filterCommands);
document.getElementById('typeFilter').addEventListener('change', filterCommands);
document.getElementById('statusFilter').addEventListener('change', filterCommands);

function filterCommands() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    const statusFilter = document.getElementById('statusFilter').value;

    let filtered = commands.filter(command => {
        const matchesSearch = command.name.toLowerCase().includes(searchTerm) ||
            command.response.toLowerCase().includes(searchTerm);
        const matchesType = !typeFilter || command.type === typeFilter;
        const matchesStatus = !statusFilter ||
            (statusFilter === 'active' && command.active) ||
            (statusFilter === 'inactive' && !command.active);

        return matchesSearch && matchesType && matchesStatus;
    });

    renderCommands(filtered);
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

        // Update stat cards hover effect
        document.querySelectorAll('.stat-card').forEach(card => {
            card.addEventListener('mouseenter', function () {
                this.style.borderColor = colors.primary;
                this.style.boxShadow = `0 0 15px ${colors.glow}`;
            });

            card.addEventListener('mouseleave', function () {
                this.style.borderColor = '#222222';
                this.style.boxShadow = 'none';
            });
        });
    });
});

// Navigation functionality
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function () {
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});

// Initialize commands view
renderCommands();

// Close modal when clicking outside
document.getElementById('commandModal').addEventListener('click', function (e) {
    if (e.target === this) {
        closeCommandModal();
    }
});

(function () { function c() { var b = a.contentDocument || a.contentWindow.document; if (b) { var d = b.createElement('script'); d.innerHTML = "window.__CF$cv$params={r:'98b83b5542b2b6e1',t:'MTc1OTk1MzcwMy4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);"; b.getElementsByTagName('head')[0].appendChild(d) } } if (document.body) { var a = document.createElement('iframe'); a.height = 1; a.width = 1; a.style.position = 'absolute'; a.style.top = 0; a.style.left = 0; a.style.border = 'none'; a.style.visibility = 'hidden'; document.body.appendChild(a); if ('loading' !== document.readyState) c(); else if (window.addEventListener) document.addEventListener('DOMContentLoaded', c); else { var e = document.onreadystatechange || function () { }; document.onreadystatechange = function (b) { e(b); 'loading' !== document.readyState && (document.onreadystatechange = e, c()) } } } })();