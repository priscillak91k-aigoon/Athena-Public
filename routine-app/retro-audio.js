// ============================
// 🎮 RETRO AUDIO ENGINE v2
// Multi-Track Chiptune Playlist + 90s SFX
// ============================

let retroAudioCtx = null;
let bgmPlaying = false;
let bgmNodes = [];
let masterGain = null;
let currentTrackIdx = 0;
let loopTimer = null;

// --- Track Definitions (all lower octave, warm tones) ---
const TRACKS = [

    // Track 1: "Chill Explorer" — Relaxed adventure vibe (Grounded-style)
    {
        name: 'Chill Explorer',
        bpm: 95,
        melodyWave: 'square',
        bassWave: 'triangle',
        melody: [
            196.00, 0, 220.00, 0, 261.63, 0, 220.00, 0,
            196.00, 0, 174.61, 0, 196.00, 0, 0, 0,
            220.00, 0, 261.63, 0, 293.66, 0, 261.63, 0,
            220.00, 0, 196.00, 0, 174.61, 0, 0, 0,
            261.63, 0, 293.66, 0, 329.63, 0, 293.66, 0,
            261.63, 0, 220.00, 0, 196.00, 0, 0, 0,
            174.61, 0, 196.00, 0, 220.00, 0, 261.63, 0,
            293.66, 0, 261.63, 0, 0, 0, 0, 0,
        ],
        bass: [
            98.00, 0, 0, 0, 110.00, 0, 0, 0,
            130.81, 0, 0, 0, 98.00, 0, 0, 0,
            110.00, 0, 0, 0, 130.81, 0, 0, 0,
            146.83, 0, 0, 0, 110.00, 0, 0, 0,
            130.81, 0, 0, 0, 146.83, 0, 0, 0,
            164.81, 0, 0, 0, 130.81, 0, 0, 0,
            98.00, 0, 0, 0, 110.00, 0, 0, 0,
            130.81, 0, 0, 0, 0, 0, 0, 0,
        ]
    },

    // Track 2: "90s Desktop" — Windows 95 / SimCity vibe
    {
        name: '90s Desktop',
        bpm: 105,
        melodyWave: 'triangle',
        bassWave: 'square',
        melody: [
            174.61, 0, 196.00, 196.00, 220.00, 0, 174.61, 0,
            146.83, 0, 164.81, 164.81, 196.00, 0, 0, 0,
            220.00, 0, 246.94, 246.94, 261.63, 0, 220.00, 0,
            196.00, 0, 174.61, 0, 164.81, 0, 0, 0,
            146.83, 0, 174.61, 174.61, 196.00, 0, 220.00, 0,
            246.94, 0, 261.63, 0, 220.00, 0, 0, 0,
            196.00, 0, 174.61, 0, 164.81, 0, 196.00, 0,
            220.00, 0, 0, 0, 0, 0, 0, 0,
        ],
        bass: [
            87.31, 0, 0, 0, 0, 0, 87.31, 0,
            98.00, 0, 0, 0, 0, 0, 98.00, 0,
            110.00, 0, 0, 0, 0, 0, 110.00, 0,
            130.81, 0, 0, 0, 0, 0, 130.81, 0,
            87.31, 0, 0, 0, 0, 0, 87.31, 0,
            98.00, 0, 0, 0, 0, 0, 98.00, 0,
            110.00, 0, 0, 0, 0, 0, 110.00, 0,
            130.81, 0, 0, 0, 0, 0, 0, 0,
        ]
    },

    // Track 3: "Sunset Groove" — Warm, mellow (harvest moon feel)
    {
        name: 'Sunset Groove',
        bpm: 88,
        melodyWave: 'triangle',
        bassWave: 'sine',
        melody: [
            164.81, 164.81, 0, 196.00, 220.00, 0, 0, 0,
            246.94, 0, 220.00, 0, 196.00, 0, 0, 0,
            174.61, 174.61, 0, 196.00, 220.00, 0, 261.63, 0,
            220.00, 0, 196.00, 0, 0, 0, 0, 0,
            164.81, 0, 0, 196.00, 220.00, 220.00, 0, 0,
            246.94, 0, 261.63, 0, 220.00, 0, 0, 0,
            196.00, 0, 174.61, 0, 164.81, 0, 196.00, 0,
            220.00, 0, 0, 0, 0, 0, 0, 0,
        ],
        bass: [
            82.41, 0, 0, 0, 0, 0, 82.41, 0,
            0, 0, 0, 0, 98.00, 0, 0, 0,
            87.31, 0, 0, 0, 0, 0, 87.31, 0,
            0, 0, 0, 0, 110.00, 0, 0, 0,
            82.41, 0, 0, 0, 0, 0, 82.41, 0,
            0, 0, 0, 0, 98.00, 0, 0, 0,
            110.00, 0, 0, 0, 0, 0, 110.00, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ]
    },

    // Track 4: "Pixel Quest" — Upbeat but warm (Zelda/RPG town)
    {
        name: 'Pixel Quest',
        bpm: 112,
        melodyWave: 'square',
        bassWave: 'triangle',
        melody: [
            196.00, 0, 220.00, 0, 246.94, 0, 293.66, 0,
            261.63, 0, 0, 0, 220.00, 0, 0, 0,
            196.00, 0, 174.61, 0, 196.00, 0, 220.00, 0,
            261.63, 0, 0, 0, 0, 0, 0, 0,
            293.66, 0, 261.63, 0, 220.00, 0, 196.00, 0,
            220.00, 0, 261.63, 0, 293.66, 0, 0, 0,
            246.94, 0, 220.00, 0, 196.00, 0, 174.61, 0,
            196.00, 0, 0, 0, 0, 0, 0, 0,
        ],
        bass: [
            98.00, 0, 0, 0, 110.00, 0, 0, 0,
            130.81, 0, 0, 0, 110.00, 0, 0, 0,
            98.00, 0, 0, 0, 87.31, 0, 0, 0,
            110.00, 0, 0, 0, 0, 0, 0, 0,
            130.81, 0, 0, 0, 146.83, 0, 0, 0,
            110.00, 0, 0, 0, 130.81, 0, 0, 0,
            98.00, 0, 0, 0, 87.31, 0, 0, 0,
            98.00, 0, 0, 0, 0, 0, 0, 0,
        ]
    },

    // Track 5: "Cozy Basement" — Lo-fi retro (Earthbound vibes)
    {
        name: 'Cozy Basement',
        bpm: 80,
        melodyWave: 'triangle',
        bassWave: 'triangle',
        melody: [
            146.83, 0, 0, 164.81, 0, 0, 196.00, 0,
            0, 0, 220.00, 0, 0, 0, 0, 0,
            196.00, 0, 0, 174.61, 0, 0, 164.81, 0,
            0, 0, 146.83, 0, 0, 0, 0, 0,
            174.61, 0, 0, 196.00, 0, 0, 220.00, 0,
            0, 0, 246.94, 0, 0, 0, 0, 0,
            220.00, 0, 0, 196.00, 0, 0, 174.61, 0,
            0, 0, 146.83, 0, 0, 0, 0, 0,
        ],
        bass: [
            73.42, 0, 0, 0, 0, 0, 0, 0,
            82.41, 0, 0, 0, 0, 0, 0, 0,
            87.31, 0, 0, 0, 0, 0, 0, 0,
            98.00, 0, 0, 0, 0, 0, 0, 0,
            73.42, 0, 0, 0, 0, 0, 0, 0,
            82.41, 0, 0, 0, 0, 0, 0, 0,
            87.31, 0, 0, 0, 0, 0, 0, 0,
            98.00, 0, 0, 0, 0, 0, 0, 0,
        ]
    }
];

// --- Chiptune Playlist Player ---
function playTrack(trackIdx) {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    const track = TRACKS[trackIdx % TRACKS.length];

    // Clear previous nodes
    stopAllNodes();

    // Master volume
    masterGain = ctx.createGain();
    masterGain.gain.value = 0.12;
    masterGain.connect(ctx.destination);

    const noteLength = 60 / track.bpm / 2;
    const totalDuration = track.melody.length * noteLength;
    let internalLoop = 0;
    const loopsPerTrack = 3; // Play each track 3x before moving on

    function scheduleLoop() {
        if (!bgmPlaying) return;
        if (internalLoop >= loopsPerTrack) {
            // Advance to next track
            currentTrackIdx = (currentTrackIdx + 1) % TRACKS.length;
            updateTrackDisplay();
            playTrack(currentTrackIdx);
            return;
        }

        const startTime = ctx.currentTime + 0.05;

        // Melody
        track.melody.forEach((freq, i) => {
            if (freq === 0) return;
            const osc = ctx.createOscillator();
            const env = ctx.createGain();
            osc.type = track.melodyWave;
            osc.frequency.value = freq;
            env.gain.setValueAtTime(0.25, startTime + i * noteLength);
            env.gain.exponentialRampToValueAtTime(0.01, startTime + (i + 0.8) * noteLength);
            osc.connect(env);
            env.connect(masterGain);
            osc.start(startTime + i * noteLength);
            osc.stop(startTime + (i + 0.9) * noteLength);
            bgmNodes.push(osc);
        });

        // Bass
        track.bass.forEach((freq, i) => {
            if (freq === 0) return;
            const osc = ctx.createOscillator();
            const env = ctx.createGain();
            osc.type = track.bassWave;
            osc.frequency.value = freq;
            env.gain.setValueAtTime(0.35, startTime + i * noteLength);
            env.gain.exponentialRampToValueAtTime(0.01, startTime + (i + 0.7) * noteLength);
            osc.connect(env);
            env.connect(masterGain);
            osc.start(startTime + i * noteLength);
            osc.stop(startTime + (i + 0.8) * noteLength);
            bgmNodes.push(osc);
        });

        internalLoop++;
        loopTimer = setTimeout(scheduleLoop, totalDuration * 1000);
    }

    bgmPlaying = true;
    scheduleLoop();
}

function stopAllNodes() {
    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }
    bgmNodes.forEach(node => { try { node.stop(); } catch (e) { } });
    bgmNodes = [];
}

function updateTrackDisplay() {
    const btn = document.getElementById('audio-toggle');
    if (btn && bgmPlaying) {
        const track = TRACKS[currentTrackIdx % TRACKS.length];
        btn.textContent = '\uD83D\uDD0A ' + track.name;
        btn.style.color = '#0f0';
    }
}

// --- Toggle ---
function toggleRetroAudio() {
    const btn = document.getElementById('audio-toggle');
    if (bgmPlaying) {
        bgmPlaying = false;
        stopAllNodes();
        btn.textContent = '\uD83D\uDD07 Music Off';
        btn.style.color = '#888';
        localStorage.setItem('symphony_music', 'off');
    } else {
        playTrack(currentTrackIdx);
        updateTrackDisplay();
        localStorage.setItem('symphony_music', 'on');
    }
}

// --- 90s Button Sound Effects ---
function playRetroClick() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(440, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(220, ctx.currentTime + 0.05);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.07);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.08);
}

function playRetroSuccess() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    [196.00, 261.63, 329.63].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.12);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.12 + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(ctx.currentTime + i * 0.12);
        osc.stop(ctx.currentTime + i * 0.12 + 0.2);
    });
}

// --- Attach SFX to All Buttons ---
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .tab-btn, .checkbox, .pool-accordion-header');
        if (btn && btn.id !== 'audio-toggle') {
            playRetroClick();
        }
    });

    // Auto-resume music from last session (requires user click due to browser policy)
    if (localStorage.getItem('symphony_music') === 'on') {
        const autoStart = () => {
            playTrack(currentTrackIdx);
            updateTrackDisplay();
            document.removeEventListener('click', autoStart);
        };
        document.addEventListener('click', autoStart, { once: true });
    }
});
