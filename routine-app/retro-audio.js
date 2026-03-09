// ============================
// 🌿 AMBIENT AUDIO ENGINE v3
// Calming ambient BGM + soft UI sounds
// ============================

let retroAudioCtx = null;
let bgmPlaying = false;
let bgmNodes = [];
let masterGain = null;
let currentTrackIdx = 0;
let loopTimer = null;

// ── Ambient Pad Engine ────────────────────────────────────────
// Uses:  sine-wave sustained chord layers, slow movement,
//        a feedback delay for warmth, and low-pass filter for haze.

const AMBIENT_TRACKS = [
    {
        name: 'Northern Light',
        // D minor pentatonic — slow, airy, wide
        chords: [
            [146.83, 220.00, 293.66],   // Dm
            [164.81, 220.00, 329.63],   // F
            [174.61, 261.63, 349.23],   // G
            [146.83, 220.00, 293.66],   // Dm
        ],
        melody: [587.33, 659.25, 698.46, 587.33, 523.25, 493.88, 523.25, 587.33],
        barLen: 6.0,           // seconds per chord
        melStepLen: 3.0
    },
    {
        name: 'Deep Water',
        // C pentatonic — very low, deep
        chords: [
            [130.81, 196.00, 261.63],
            [146.83, 220.00, 293.66],
            [123.47, 185.00, 246.94],
            [130.81, 196.00, 261.63],
        ],
        melody: [523.25, 587.33, 523.25, 493.88, 440.00, 493.88, 523.25, 587.33],
        barLen: 7.0,
        melStepLen: 3.5
    },
    {
        name: 'Stillness',
        // G major pentatonic — open, airy
        chords: [
            [196.00, 293.66, 392.00],
            [220.00, 329.63, 440.00],
            [246.94, 329.63, 392.00],
            [196.00, 293.66, 392.00],
        ],
        melody: [784.00, 880.00, 784.00, 698.46, 659.25, 698.46, 784.00, 880.00],
        barLen: 8.0,
        melStepLen: 4.0
    }
];

// Build a reverb-like convolver from a noise impulse
function createReverb(ctx, duration = 2.5, decay = 2.0) {
    const sr = ctx.sampleRate;
    const length = sr * duration;
    const impulse = ctx.createBuffer(2, length, sr);
    for (let c = 0; c < 2; c++) {
        const data = impulse.getChannelData(c);
        for (let i = 0; i < length; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
        }
    }
    const conv = ctx.createConvolver();
    conv.buffer = impulse;
    return conv;
}

function playAmbientTrack(trackIdx) {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    const track = AMBIENT_TRACKS[trackIdx % AMBIENT_TRACKS.length];

    stopAllNodes();

    // Signal chain: oscBus → filter → reverb(wet) + dry → master
    masterGain = ctx.createGain();
    masterGain.gain.value = 0.09;
    masterGain.connect(ctx.destination);

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 1800;
    filter.Q.value = 0.6;
    filter.connect(masterGain);

    const reverb = createReverb(ctx, 3.0, 2.5);
    const reverbGain = ctx.createGain();
    reverbGain.gain.value = 0.55;
    reverb.connect(reverbGain);
    reverbGain.connect(masterGain);

    // Bus for wet path
    const wetBus = ctx.createGain();
    wetBus.gain.value = 1;
    wetBus.connect(filter);
    wetBus.connect(reverb);

    let playCount = 0;
    const loopsPerTrack = 2;

    function scheduleLoop() {
        if (!bgmPlaying) return;
        if (playCount >= loopsPerTrack) {
            currentTrackIdx = (currentTrackIdx + 1) % AMBIENT_TRACKS.length;
            updateTrackDisplay();
            playAmbientTrack(currentTrackIdx);
            return;
        }

        const now = ctx.currentTime + 0.1;
        const { chords, melody, barLen, melStepLen } = track;
        const totalLen = chords.length * barLen;

        // Pad chords — slow sustained sine tones with long crossfade
        chords.forEach((chord, ci) => {
            const barStart = now + ci * barLen;
            const barEnd = barStart + barLen + 0.6; // slight overlap for crossfade
            chord.forEach(freq => {
                const osc = ctx.createOscillator();
                const env = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.value = freq;
                // add a tiny detuned twin for warmth
                const osc2 = ctx.createOscillator();
                osc2.type = 'sine';
                osc2.frequency.value = freq * 1.003;
                const attack = Math.min(1.2, barLen * 0.18);
                const release = Math.min(1.5, barLen * 0.25);
                env.gain.setValueAtTime(0, barStart);
                env.gain.linearRampToValueAtTime(0.28, barStart + attack);
                env.gain.setValueAtTime(0.28, barEnd - release);
                env.gain.linearRampToValueAtTime(0, barEnd);
                [osc, osc2].forEach(o => { o.connect(env); o.start(barStart); o.stop(barEnd + 0.1); bgmNodes.push(o); });
                env.connect(wetBus);
            });
        });

        // Slow melody layer (very soft, high octave, every melStepLen seconds)
        melody.forEach((freq, mi) => {
            const noteStart = now + mi * melStepLen;
            if (noteStart >= now + totalLen) return;
            const osc = ctx.createOscillator();
            const env = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            const noteDur = melStepLen * 0.85;
            env.gain.setValueAtTime(0, noteStart);
            env.gain.linearRampToValueAtTime(0.10, noteStart + 0.3);
            env.gain.setValueAtTime(0.10, noteStart + noteDur - 0.5);
            env.gain.linearRampToValueAtTime(0, noteStart + noteDur);
            osc.connect(env);
            env.connect(wetBus);
            osc.start(noteStart);
            osc.stop(noteStart + noteDur + 0.1);
            bgmNodes.push(osc);
        });

        playCount++;
        loopTimer = setTimeout(scheduleLoop, totalLen * 1000);
    }

    bgmPlaying = true;
    scheduleLoop();
}

function stopAllNodes() {
    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }
    bgmNodes.forEach(n => { try { n.stop(); } catch (e) { } });
    bgmNodes = [];
}

function updateTrackDisplay() {
    const btn = document.getElementById('audio-toggle');
    if (btn && bgmPlaying) {
        const track = AMBIENT_TRACKS[currentTrackIdx % AMBIENT_TRACKS.length];
        btn.textContent = '🔊 ' + track.name;
        btn.style.color = 'var(--accent-green, #00c9a0)';
    }
}

function toggleRetroAudio() {
    const btn = document.getElementById('audio-toggle');
    if (bgmPlaying) {
        bgmPlaying = false;
        stopAllNodes();
        if (btn) { btn.textContent = '🔇 Music Off'; btn.style.color = '#555'; }
        localStorage.setItem('symphony_music', 'off');
    } else {
        playAmbientTrack(currentTrackIdx);
        updateTrackDisplay();
        localStorage.setItem('symphony_music', 'on');
    }
}

// ── Soft UI Click Sound ───────────────────────────────────────
function playRetroClick() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    // A soft, rounded "plink" — sine wave with fast decay
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1050, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(820, ctx.currentTime + 0.06);
    gain.gain.setValueAtTime(0.06, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.14);
}

function playRetroSuccess() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    // Three soft rising sine tones — gentle success chime
    [523.25, 659.25, 783.99].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        const t = ctx.currentTime + i * 0.1;
        gain.gain.setValueAtTime(0.06, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.3);
    });
}

// ── Wire SFX + Auto-resume ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .tab-btn, .checkbox');
        if (btn && btn.id !== 'audio-toggle') {
            playRetroClick();
        }
    });

    if (localStorage.getItem('symphony_music') === 'on') {
        const autoStart = () => {
            playAmbientTrack(currentTrackIdx);
            updateTrackDisplay();
            document.removeEventListener('click', autoStart);
        };
        document.addEventListener('click', autoStart, { once: true });
    }
});
