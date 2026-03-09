// ============================================================
// MISC — Ideal Week Renderer
// ============================================================
(function initMiscPage() {
    'use strict';

    // ── Colour tokens ─────────────────────────────────────────
    const C = {
        deepWork: { bg: 'rgba(0,200,160,0.10)', border: '#00c9a0', dot: '#00c9a0' },
        work: { bg: 'rgba(251,191,36,0.10)', border: '#fbbf24', dot: '#fbbf24' },
        exercise: { bg: 'rgba(251,146,60,0.10)', border: '#fb923c', dot: '#fb923c' },
        personal: { bg: 'rgba(244,114,182,0.10)', border: '#f472b6', dot: '#f472b6' },
        windDown: { bg: 'rgba(167,139,250,0.10)', border: '#a78bfa', dot: '#a78bfa' },
        routine: { bg: 'rgba(255,255,255,0.03)', border: 'rgba(255,255,255,0.12)', dot: 'rgba(255,255,255,0.3)' },
    };

    // ── Ideal Week Data ───────────────────────────────────────
    const WEEK = [
        {
            day: 'Monday', type: 'WORK 12–6 PM',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water + electrolytes', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + morning supps (D3, K2, Fish Oil)', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:00 AM', label: '☕ Last caffeine window (cut at 10 AM)', cat: 'routine' },
                { time: '8:15 AM', label: 'DEEP WORK — 2.75 h block', cat: 'deepWork' },
                { time: '11:00 AM', label: 'Shower · get ready · pack meals', cat: 'routine' },
                { time: '11:45 AM', label: 'Travel to BP', cat: 'routine' },
                { time: '12:00 PM', label: 'BP SHIFT', cat: 'work' },
                { time: '6:00 PM', label: 'Home · decompress walk with Quinn', cat: 'personal' },
                { time: '6:30 PM', label: 'Dinner (high protein, light carbs)', cat: 'routine' },
                { time: '7:30 PM', label: 'Free time / low-stimulus screen', cat: 'personal' },
                { time: '9:00 PM', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '10:00 PM', label: 'Reading / journalling — no screens', cat: 'windDown' },
                { time: '11:00 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Tuesday', type: 'OFF DAY',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:00 AM', label: '☕ Coffee window', cat: 'routine' },
                { time: '8:15 AM', label: 'DEEP WORK — 3.5 h block', cat: 'deepWork' },
                { time: '11:45 AM', label: 'Break · Quinn time or walk', cat: 'personal' },
                { time: '12:00 PM', label: 'Lunch (protein first, carbs after)', cat: 'routine' },
                { time: '1:00 PM', label: 'EXERCISE — heavy lift or sprint', cat: 'exercise' },
                { time: '2:30 PM', label: 'Shower + recovery (electrolytes)', cat: 'routine' },
                { time: '3:00 PM', label: 'Admin / errands / light tasks', cat: 'routine' },
                { time: '4:30 PM', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '5:00 PM', label: 'Project work or creative block', cat: 'deepWork' },
                { time: '6:30 PM', label: 'Dinner', cat: 'routine' },
                { time: '7:30 PM', label: 'Free time', cat: 'personal' },
                { time: '9:00 PM', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '10:00 PM', label: 'Reading — no screens', cat: 'windDown' },
                { time: '11:30 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Wednesday', type: 'OFF DAY',
            note: 'Mirror of Tuesday. Optional variation: longer creative block in PM.',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:15 AM', label: 'DEEP WORK — 3.5 h block', cat: 'deepWork' },
                { time: '11:45 AM', label: 'Lunch break', cat: 'routine' },
                { time: '1:00 PM', label: 'EXERCISE — hypertrophy or walk', cat: 'exercise' },
                { time: '2:30 PM', label: 'Shower + recovery', cat: 'routine' },
                { time: '3:00 PM', label: 'Admin / errands', cat: 'routine' },
                { time: '4:30 PM', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '5:30 PM', label: 'Creative / project time', cat: 'deepWork' },
                { time: '6:30 PM', label: 'Dinner', cat: 'routine' },
                { time: '7:30 PM', label: 'Free time / social', cat: 'personal' },
                { time: '9:00 PM', label: 'Mag Glycinate · wind down', cat: 'windDown' },
                { time: '11:30 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Thursday', type: 'OFF DAY',
            note: 'Optional: active recovery day — lighter exercise, more admin batch.',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:15 AM', label: 'DEEP WORK — 3 h block', cat: 'deepWork' },
                { time: '11:30 AM', label: 'Lunch + admin batch', cat: 'routine' },
                { time: '1:00 PM', label: 'Light exercise or rest day', cat: 'exercise' },
                { time: '2:30 PM', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '3:00 PM', label: 'Projects / learning', cat: 'deepWork' },
                { time: '5:30 PM', label: 'Meal prep for Fri–Sun', cat: 'routine' },
                { time: '6:30 PM', label: 'Dinner', cat: 'routine' },
                { time: '7:30 PM', label: 'Free time', cat: 'personal' },
                { time: '9:00 PM', label: 'Mag Glycinate · wind down', cat: 'windDown' },
                { time: '11:30 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Friday', type: 'WORK 2:45–11 PM',
            note: 'Morning is protected deep work. Exercise before shift.',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:00 AM', label: 'DEEP WORK — 2 h block', cat: 'deepWork' },
                { time: '10:00 AM', label: 'EXERCISE — gym or sprint', cat: 'exercise' },
                { time: '11:30 AM', label: 'Shower + post-workout protein', cat: 'routine' },
                { time: '12:00 PM', label: 'Lunch + prep for shift', cat: 'routine' },
                { time: '1:30 PM', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '2:15 PM', label: 'Travel to BP', cat: 'routine' },
                { time: '2:45 PM', label: 'BP SHIFT', cat: 'work' },
                { time: '11:00 PM', label: 'Shift ends · travel home', cat: 'routine' },
                { time: '11:15 PM', label: 'Mag Glycinate · decompress', cat: 'windDown' },
                { time: '11:45 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Saturday', type: 'WORK 2:45–11 PM',
            note: 'Same structure as Friday. Morning is yours.',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:00 AM', label: 'DEEP WORK — 2 h block', cat: 'deepWork' },
                { time: '10:00 AM', label: 'EXERCISE or active recovery', cat: 'exercise' },
                { time: '11:30 AM', label: 'Shower + lunch prep', cat: 'routine' },
                { time: '12:30 PM', label: 'Lunch · low-key morning', cat: 'routine' },
                { time: '1:30 PM', label: 'Quinn walk + fresh air', cat: 'personal' },
                { time: '2:15 PM', label: 'Travel to BP', cat: 'routine' },
                { time: '2:45 PM', label: 'BP SHIFT', cat: 'work' },
                { time: '11:00 PM', label: 'Home · Mag Glycinate', cat: 'windDown' },
                { time: '11:45 PM', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Sunday', type: 'WORK 11 AM–5 PM',
            note: 'Shortest shift. Evening is full recovery.',
            blocks: [
                { time: '6:30 AM', label: 'Wake · NAC + water', cat: 'routine' },
                { time: '7:00 AM', label: 'Breakfast + supps', cat: 'routine' },
                { time: '7:30 AM', label: 'Quinn morning walk', cat: 'personal' },
                { time: '8:00 AM', label: 'DEEP WORK — 1.5 h (light admin)', cat: 'deepWork' },
                { time: '9:30 AM', label: 'Shower · get ready', cat: 'routine' },
                { time: '10:30 AM', label: 'Travel to BP', cat: 'routine' },
                { time: '11:00 AM', label: 'BP SHIFT', cat: 'work' },
                { time: '5:00 PM', label: 'Shift ends', cat: 'routine' },
                { time: '5:30 PM', label: 'Quinn decompression walk', cat: 'personal' },
                { time: '6:00 PM', label: 'Dinner (easy Sunday meal)', cat: 'routine' },
                { time: '7:00 PM', label: 'Week review · plan Monday', cat: 'routine' },
                { time: '8:00 PM', label: 'Free time · pure rest', cat: 'personal' },
                { time: '9:00 PM', label: 'Mag Glycinate · early wind down', cat: 'windDown' },
                { time: '10:30 PM', label: '💤 SLEEP TARGET (early!)', cat: 'windDown' },
            ]
        }
    ];

    // ── Renderer ──────────────────────────────────────────────
    function renderIdealWeek() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        grid.innerHTML = WEEK.map(({ day, type, note, blocks }) => {
            const isWork = type.startsWith('WORK');
            const rows = blocks.map(b => {
                const col = C[b.cat];
                return `
                <div style="display:flex; gap:0.6rem; align-items:baseline; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="font-size:0.72rem; color:var(--text-dim); min-width:58px; font-family:'VT323',monospace; letter-spacing:0.5px;">${b.time}</span>
                    <span style="width:3px; height:3px; border-radius:50%; background:${col.dot}; flex-shrink:0; margin-top:6px;"></span>
                    <span style="font-size:0.82rem; color:var(--text-secondary); line-height:1.4;">${b.label}</span>
                </div>`;
            }).join('');

            const noteHtml = note
                ? `<div style="font-size:0.75rem; color:var(--text-dim); font-style:italic; margin-bottom:0.75rem; padding:4px 8px; border-left:2px solid var(--glass-border); line-height:1.5;">${note}</div>`
                : '';

            return `
            <div style="background:rgba(4,18,18,0.55); border:1px solid var(--glass-border); border-radius:4px; padding:1rem; display:flex; flex-direction:column; gap:0.35rem; transition:border-color 0.15s;" onmouseover="this.style.borderColor='var(--glass-border-hot)'" onmouseout="this.style.borderColor='var(--glass-border)'">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                    <span style="font-size:0.72rem; padding:2px 8px; background:${isWork ? 'rgba(251,191,36,0.12)' : 'rgba(0,200,160,0.08)'}; border:1px solid ${isWork ? 'rgba(251,191,36,0.25)' : 'rgba(0,200,160,0.2)'}; color:${isWork ? '#fbbf24' : 'var(--accent-green)'}; border-radius:2px; letter-spacing:0.5px;">${type}</span>
                </div>
                ${noteHtml}
                <div style="display:flex; flex-direction:column;">${rows}</div>
            </div>`;
        }).join('');
    }

    // ── Boot ──────────────────────────────────────────────────
    function boot() {
        renderIdealWeek();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
