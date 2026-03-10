// ============================================================
// MISC — Ideal Week Renderer
// ============================================================
(function initMiscPage() {
    'use strict';

    const C = {
        deepWork: { dot: '#00c9a0' },
        work: { dot: '#fbbf24' },
        exercise: { dot: '#fb923c' },
        personal: { dot: '#f472b6' },
        windDown: { dot: '#a78bfa' },
        routine: { dot: 'rgba(255,255,255,0.3)' },
        kids: { dot: '#38bdf8' },
        nap: { dot: '#c084fc' }, // soft purple — nap time
    };

    // ── Design Principles ─────────────────────────────────────
    // • Night sleep = ~6h on weekdays (kids at 6:30, sleep at midnight)
    // • Nap compensates: EVERY weekday needs a recovery nap
    // • Sat/Sun: sleep in to 9 AM (~9h) = no nap needed
    // • Weekday mornings 6:30–8:30 = kids (non-negotiable)
    // • Deep work window: 9:00 AM onwards on weekdays
    // • Exercise: off days after nap, or pre-shift on Fri/Sat
    // • Quinn: morning walk (post-drop-off weekdays) + afternoon walk always
    // • Mag Glycinate: 9 PM always · no screens 10 PM · sleep by midnight

    const WEEK = [

        // ── MONDAY — Work 12:00–18:00 ────────────────────────
        // Only window for nap is before noon shift — tight but doable
        {
            day: 'Monday', type: 'WORK 12–6 PM',
            note: 'Sleep first. Nap takes the prime morning slot — catch up on 6h night. Light admin after.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast in peace + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk (30 min)', cat: 'personal' },
                { time: '9:20', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '11:20', label: 'Wake · light admin / messages / quick tasks', cat: 'routine' },
                { time: '11:40', label: 'Shower · pack meals · travel prep', cat: 'routine' },
                { time: '12:00', label: '► BP SHIFT', cat: 'work' },
                { time: '18:00', label: 'Shift ends', cat: 'work' },
                { time: '18:15', label: 'Quinn decompression walk', cat: 'personal' },
                { time: '18:45', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: 'Admin · planning · light tasks', cat: 'routine' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '21:30', label: 'Reading — no screens', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early as possible', cat: 'windDown' },
            ]
        },

        // ── TUESDAY — Off ─────────────────────────────────────
        {
            day: 'Tuesday', type: 'OFF DAY',
            note: 'Best day. Deep work → nap → gym. Full recovery stack.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast in peace + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — Block 1 (90 min)', cat: 'deepWork' },
                { time: '10:45', label: '10 min break · stretch · water', cat: 'routine' },
                { time: '11:00', label: 'DEEP WORK — Block 2 (60 min)', cat: 'deepWork' },
                { time: '12:00', label: 'Shutdown · lunch', cat: 'routine' },
                { time: '12:30', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:30', label: 'Wake · water · short walk to wake up', cat: 'routine' },
                { time: '15:00', label: 'GYM — heavy lift or sprint session', cat: 'exercise' },
                { time: '16:30', label: 'Shower + protein', cat: 'routine' },
                { time: '17:00', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:30', label: 'Light tasks · admin · messages', cat: 'routine' },
                { time: '18:30', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: 'Free time — recharge, social, TV', cat: 'personal' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },

        // ── WEDNESDAY — Off ───────────────────────────────────
        {
            day: 'Wednesday', type: 'OFF DAY',
            note: 'Same as Tuesday. Optional: swap gym for Rock Orchestra evening.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — Block 1 (90 min)', cat: 'deepWork' },
                { time: '10:45', label: 'Break · stretch · water', cat: 'routine' },
                { time: '11:00', label: 'DEEP WORK — Block 2 (60 min)', cat: 'deepWork' },
                { time: '12:00', label: 'Shutdown · lunch', cat: 'routine' },
                { time: '12:30', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:30', label: 'Wake · water', cat: 'routine' },
                { time: '15:00', label: 'GYM or active recovery', cat: 'exercise' },
                { time: '16:30', label: 'Shower + protein', cat: 'routine' },
                { time: '17:00', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:30', label: 'Admin / life tasks', cat: 'routine' },
                { time: '18:30', label: 'Dinner + kids', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: 'Free time', cat: 'personal' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },

        // ── THURSDAY — Off ────────────────────────────────────
        {
            day: 'Thursday', type: 'OFF DAY',
            note: 'Prep day. Nap → gym → meal prep ready for weekend shifts.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — 2 h block', cat: 'deepWork' },
                { time: '11:15', label: 'Shutdown · review week', cat: 'routine' },
                { time: '11:30', label: 'Lunch', cat: 'routine' },
                { time: '12:00', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:00', label: 'Wake · water', cat: 'routine' },
                { time: '14:30', label: 'GYM or outdoor activity', cat: 'exercise' },
                { time: '16:00', label: 'Shower + protein', cat: 'routine' },
                { time: '16:30', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:00', label: 'Errands · life admin', cat: 'routine' },
                { time: '18:00', label: '🍳 MEAL PREP — Fri/Sat/Sun shifts', cat: 'routine' },
                { time: '19:15', label: 'Dinner + kids', cat: 'routine' },
                { time: '20:30', label: 'Kids bedtime', cat: 'kids' },
                { time: '21:00', label: 'Mag Glycinate · early wind-down', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early for weekend', cat: 'windDown' },
            ]
        },

        // ── FRIDAY — Work 14:45–23:00 ─────────────────────────
        // Nap replaces gym (gym is on Tue/Wed/Thu/Sat)
        {
            day: 'Friday', type: 'WORK 2:45–11 PM',
            note: 'Nap replaces gym today — gym on off days covers it. Nap is the priority.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — 1.5 h block', cat: 'deepWork' },
                { time: '10:45', label: 'Shutdown · wrap deep work', cat: 'routine' },
                { time: '11:00', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '13:00', label: 'Wake · shower · pack shift meals', cat: 'routine' },
                { time: '13:45', label: 'Lunch', cat: 'routine' },
                { time: '14:00', label: 'Quinn quick walk · fresh air', cat: 'personal' },
                { time: '14:15', label: 'Travel to BP', cat: 'routine' },
                { time: '14:45', label: '► BP SHIFT', cat: 'work' },
                { time: '23:00', label: 'Shift ends · straight home', cat: 'work' },
                { time: '23:20', label: 'Mag Glycinate · no screens', cat: 'windDown' },
                { time: '23:45', label: '💤 SLEEP — midnight hard cap', cat: 'windDown' },
            ]
        },

        // ── SATURDAY — Work 14:45–23:00 ──────────────────────
        // Sleep in to 9 AM — no nap needed
        {
            day: 'Saturday', type: 'WORK 2:45–11 PM',
            note: 'Sleep in to 9 AM = full recovery. No nap needed. Morning is yours.',
            blocks: [
                { time: '9:00', label: 'Wake (sleep in) · NAC + water', cat: 'routine' },
                { time: '9:15', label: 'Relaxed breakfast', cat: 'routine' },
                { time: '9:45', label: 'Quinn morning walk', cat: 'personal' },
                { time: '10:15', label: 'DEEP WORK — 90 min block', cat: 'deepWork' },
                { time: '11:45', label: 'GYM — lift or sprint', cat: 'exercise' },
                { time: '13:00', label: 'Shower + protein', cat: 'routine' },
                { time: '13:30', label: 'Lunch · pack shift meals', cat: 'routine' },
                { time: '14:00', label: 'Quinn short walk · prep for shift', cat: 'personal' },
                { time: '14:15', label: 'Travel to BP', cat: 'routine' },
                { time: '14:45', label: '► BP SHIFT', cat: 'work' },
                { time: '23:00', label: 'Shift ends · straight home', cat: 'work' },
                { time: '23:15', label: 'Mag Glycinate · decompress', cat: 'windDown' },
                { time: '23:45', label: '💤 SLEEP — midnight hard cap', cat: 'windDown' },
            ]
        },

        // ── SUNDAY — Work 11:00–17:00 ─────────────────────────
        // Sleep in to 9 AM — no nap needed
        {
            day: 'Sunday', type: 'WORK 11 AM–5 PM',
            note: 'Sleep in to 9 AM. Shortest shift. Earliest sleep target — reset for Monday.',
            blocks: [
                { time: '9:00', label: 'Wake (sleep in) · NAC + water', cat: 'routine' },
                { time: '9:15', label: 'Relaxed Sunday breakfast', cat: 'routine' },
                { time: '9:45', label: 'Quinn morning walk', cat: 'personal' },
                { time: '10:15', label: 'Shower · get ready · pack bag', cat: 'routine' },
                { time: '10:30', label: 'Travel to BP', cat: 'routine' },
                { time: '11:00', label: '► BP SHIFT', cat: 'work' },
                { time: '17:00', label: 'Shift ends', cat: 'work' },
                { time: '17:20', label: 'Quinn evening walk — decompress', cat: 'personal' },
                { time: '18:00', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: '📋 Week review · set Monday intentions', cat: 'routine' },
                { time: '21:00', label: 'Mag Glycinate · pure rest', cat: 'windDown' },
                { time: '21:30', label: 'Reading — no screens', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early reset for Monday', cat: 'windDown' },
            ]
        }
    ];

    // ── Renderer ──────────────────────────────────────────────
    function renderIdealWeek() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        grid.innerHTML = WEEK.map(({ day, type, note, blocks }) => {
            const isOff = type === 'OFF DAY';

            const rows = blocks.map(b => {
                const dot = C[b.cat]?.dot || 'rgba(255,255,255,0.3)';
                const isSleep = b.label.includes('💤');
                const isNap = b.cat === 'nap' && b.label.includes('NAP');
                const isKids = b.cat === 'kids';
                const isDeep = b.cat === 'deepWork';
                const textColor = isSleep ? '#a78bfa'
                    : isNap ? '#c084fc'
                        : isKids ? '#38bdf8'
                            : isDeep ? '#00c9a0'
                                : 'var(--text-secondary)';
                const bold = (isSleep || isNap || isKids) ? 'font-weight:600;' : '';
                return `
                <div style="display:flex; gap:0.5rem; align-items:flex-start; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="font-size:0.71rem; color:var(--text-dim); min-width:42px; font-family:'VT323',monospace; flex-shrink:0; padding-top:2px;">${b.time}</span>
                    <span style="width:3px; height:3px; border-radius:50%; background:${dot}; flex-shrink:0; margin-top:7px;"></span>
                    <span style="font-size:0.81rem; color:${textColor}; line-height:1.4; ${bold}">${b.label}</span>
                </div>`;
            }).join('');

            const noteHtml = note
                ? `<p style="font-size:0.75rem; color:var(--text-dim); font-style:italic; margin:0 0 0.6rem; padding:3px 8px; border-left:2px solid var(--glass-border); line-height:1.5;">${note}</p>`
                : '';

            const typeBg = isOff ? 'rgba(0,200,160,0.08)' : 'rgba(251,191,36,0.08)';
            const typeBorder = isOff ? 'rgba(0,200,160,0.2)' : 'rgba(251,191,36,0.25)';
            const typeColor = isOff ? 'var(--accent-green)' : '#fbbf24';

            return `
            <div style="background:rgba(4,18,18,0.6); border:1px solid var(--glass-border); border-radius:4px; padding:1rem; transition:border-color 0.15s;"
                 onmouseover="this.style.borderColor='var(--glass-border-hot)'"
                 onmouseout="this.style.borderColor='var(--glass-border)'">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                    <span style="font-size:0.7rem; padding:2px 8px; background:${typeBg}; border:1px solid ${typeBorder}; color:${typeColor}; border-radius:2px;">${type}</span>
                </div>
                ${noteHtml}
                <div>${rows}</div>
            </div>`;
        }).join('');
    }

    function boot() { renderIdealWeek(); }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
