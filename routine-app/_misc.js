// ============================================================
// MISC — Ideal Week Renderer + Editor
// ============================================================
(function initMiscPage() {
    'use strict';

    const STORAGE_KEY = 'idealWeek_v2';

    const C = {
        deepWork: { dot: '#00c9a0', label: 'Deep Work' },
        work: { dot: '#fbbf24', label: 'Work' },
        exercise: { dot: '#fb923c', label: 'Exercise' },
        personal: { dot: '#f472b6', label: 'Personal' },
        windDown: { dot: '#a78bfa', label: 'Wind Down' },
        routine: { dot: 'rgba(255,255,255,0.3)', label: 'Routine' },
        kids: { dot: '#38bdf8', label: 'Kids' },
        nap: { dot: '#c084fc', label: 'Nap' },
        cannabis: { dot: '#4ade80', label: 'Cannabis' },
    };

    const CAT_KEYS = Object.keys(C);

    // ── Default data ──────────────────────────────────────────
    const DEFAULT_WEEK = [
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
                { time: '20:30', label: '🌿 Cannabis — 2.5h before sleep', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
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
                { time: '20:30', label: '🌿 Cannabis — 2.5h before sleep', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
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
                { time: '20:30', label: '🌿 Cannabis + week review', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · pure rest', cat: 'windDown' },
                { time: '21:30', label: 'Reading — no screens', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early reset for Monday', cat: 'windDown' },
            ]
        }
    ];

    // ── Data persistence ──────────────────────────────────────
    function loadWeek() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) return JSON.parse(stored);
        } catch (e) { /* fall through */ }
        return JSON.parse(JSON.stringify(DEFAULT_WEEK));
    }

    function saveWeek(week) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(week));
    }

    let WEEK = loadWeek();
    let editingDay = -1; // index of day being edited, -1 = none

    // ── Dirty-state guard ─────────────────────────────────────
    function setDirtyGuard(isDirty) {
        window.onbeforeunload = isDirty
            ? () => 'You have unsaved changes to your Ideal Week. Leave anyway?'
            : null;
    }

    // ── Category dropdown HTML ────────────────────────────────
    function catOptions(selected) {
        return CAT_KEYS.map(k =>
            `<option value="${k}" ${k === selected ? 'selected' : ''}>${C[k].label}</option>`
        ).join('');
    }

    // ── Renderer ──────────────────────────────────────────────
    function renderIdealWeek() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        grid.innerHTML = WEEK.map((dayData, dayIdx) => {
            const { day, type, note, blocks } = dayData;
            const isOff = type === 'OFF DAY';
            const isEditing = editingDay === dayIdx;

            // --- Edit mode ---
            if (isEditing) {
                const blockRows = blocks.map((b, bIdx) => {
                    const dot = C[b.cat]?.dot || 'rgba(255,255,255,0.3)';
                    return `
                    <div class="iw-edit-row" data-bidx="${bIdx}" style="display:flex; gap:6px; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                        <input type="text" value="${b.time}" class="iw-input iw-time" style="width:52px; font-size:0.75rem; font-family:'VT323',monospace;" placeholder="HH:MM">
                        <select class="iw-input iw-cat" style="width:90px; font-size:0.72rem;">
                            ${catOptions(b.cat)}
                        </select>
                        <input type="text" value="${b.label.replace(/"/g, '&quot;')}" class="iw-input iw-label" style="flex:1; font-size:0.78rem;" placeholder="Activity label">
                        <button class="iw-btn-icon iw-del-block" title="Remove" data-bidx="${bIdx}" style="color:#f87171; background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.15);">✕</button>
                    </div>`;
                }).join('');

                const typeBg = isOff ? 'rgba(0,200,160,0.08)' : 'rgba(251,191,36,0.08)';
                const typeBorder = isOff ? 'rgba(0,200,160,0.2)' : 'rgba(251,191,36,0.25)';
                const typeColor = isOff ? 'var(--accent-green)' : '#fbbf24';

                return `
                <div class="iw-card-editing" data-day="${dayIdx}" style="background:rgba(4,18,18,0.75); border:1px solid var(--accent-green); border-radius:4px; padding:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                        <div style="display:flex; gap:6px; align-items:center;">
                            <input type="text" value="${type}" class="iw-input iw-type-input" style="width:120px; font-size:0.7rem; text-align:center;">
                        </div>
                    </div>
                    <div style="margin-bottom:8px;">
                        <input type="text" value="${(note || '').replace(/"/g, '&quot;')}" class="iw-input iw-note-input" style="width:100%; font-size:0.75rem; font-style:italic;" placeholder="Day note (optional)">
                    </div>
                    <div class="iw-edit-blocks">${blockRows}</div>
                    <div style="display:flex; gap:8px; margin-top:10px; justify-content:space-between; flex-wrap:wrap;">
                        <button class="iw-btn iw-add-block" data-day="${dayIdx}" style="font-size:0.75rem;">+ Add Block</button>
                        <div style="display:flex; gap:6px;">
                            <button class="iw-btn iw-save-day" data-day="${dayIdx}" style="background:rgba(0,200,160,0.15); border-color:rgba(0,200,160,0.3); color:#00c9a0;">✓ Save</button>
                            <button class="iw-btn iw-cancel-day" data-day="${dayIdx}" style="background:rgba(248,113,113,0.08); border-color:rgba(248,113,113,0.15); color:#f87171;">Cancel</button>
                        </div>
                    </div>
                </div>`;
            }

            // --- View mode ---
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
            <div style="background:rgba(4,18,18,0.6); border:1px solid var(--glass-border); border-radius:4px; padding:1rem; transition:border-color 0.15s; position:relative;"
                 onmouseover="this.style.borderColor='var(--glass-border-hot)'"
                 onmouseout="this.style.borderColor='var(--glass-border)'">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span style="font-size:0.7rem; padding:2px 8px; background:${typeBg}; border:1px solid ${typeBorder}; color:${typeColor}; border-radius:2px;">${type}</span>
                        <button class="iw-btn-icon iw-edit-day" data-day="${dayIdx}" title="Edit ${day}" style="color:var(--accent-green); background:rgba(0,200,160,0.08); border:1px solid rgba(0,200,160,0.15);">✎</button>
                    </div>
                </div>
                ${noteHtml}
                <div>${rows}</div>
            </div>`;
        }).join('');

        // -- Attach event listeners --
        attachListeners();
    }

    // ── Event delegation ──────────────────────────────────────
    function attachListeners() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        // Remove old listener to avoid stacking
        grid.removeEventListener('click', handleGridClick);
        grid.addEventListener('click', handleGridClick);
    }

    function handleGridClick(e) {
        const target = e.target;

        // Edit day
        if (target.classList.contains('iw-edit-day')) {
            editingDay = parseInt(target.dataset.day);
            setDirtyGuard(true);
            renderIdealWeek();
            return;
        }

        // Cancel edit
        if (target.classList.contains('iw-cancel-day')) {
            editingDay = -1;
            setDirtyGuard(false);
            WEEK = loadWeek(); // revert unsaved changes
            renderIdealWeek();
            return;
        }

        // Save day
        if (target.classList.contains('iw-save-day')) {
            saveDayFromDOM(parseInt(target.dataset.day));
            return;
        }

        // Add block
        if (target.classList.contains('iw-add-block')) {
            const dayIdx = parseInt(target.dataset.day);
            const card = target.closest('.iw-card-editing');
            const blocksContainer = card.querySelector('.iw-edit-blocks');
            const newIdx = blocksContainer.querySelectorAll('.iw-edit-row').length;
            const newRow = document.createElement('div');
            newRow.className = 'iw-edit-row';
            newRow.dataset.bidx = newIdx;
            newRow.style.cssText = 'display:flex; gap:6px; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.04);';
            newRow.innerHTML = `
                <input type="text" value="" class="iw-input iw-time" style="width:52px; font-size:0.75rem; font-family:'VT323',monospace;" placeholder="HH:MM">
                <select class="iw-input iw-cat" style="width:90px; font-size:0.72rem;">
                    ${catOptions('routine')}
                </select>
                <input type="text" value="" class="iw-input iw-label" style="flex:1; font-size:0.78rem;" placeholder="Activity label">
                <button class="iw-btn-icon iw-del-block" title="Remove" style="color:#f87171; background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.15);">✕</button>
            `;
            blocksContainer.appendChild(newRow);
            newRow.querySelector('.iw-time').focus();
            return;
        }

        // Delete block
        if (target.classList.contains('iw-del-block')) {
            target.closest('.iw-edit-row').remove();
            return;
        }
    }

    // ── Save from DOM ─────────────────────────────────────────
    function saveDayFromDOM(dayIdx) {
        const card = document.querySelector(`.iw-card-editing[data-day="${dayIdx}"]`);
        if (!card) return;

        const typeInput = card.querySelector('.iw-type-input');
        const noteInput = card.querySelector('.iw-note-input');
        const rows = card.querySelectorAll('.iw-edit-row');

        const blocks = [];
        rows.forEach(row => {
            const time = row.querySelector('.iw-time')?.value.trim();
            const cat = row.querySelector('.iw-cat')?.value;
            const label = row.querySelector('.iw-label')?.value.trim();
            if (time && label) {
                blocks.push({ time, label, cat: cat || 'routine' });
            }
        });

        // Sort by time
        blocks.sort((a, b) => {
            const ta = a.time.replace(':', '').padStart(4, '0');
            const tb = b.time.replace(':', '').padStart(4, '0');
            return ta.localeCompare(tb);
        });

        WEEK[dayIdx].type = typeInput?.value.trim() || WEEK[dayIdx].type;

        const newNote = noteInput?.value.trim() || '';
        if (!newNote && WEEK[dayIdx].note) {
            if (!confirm('Clear the day note? This cannot be undone.')) return;
        }
        WEEK[dayIdx].note = newNote;
        WEEK[dayIdx].blocks = blocks;

        saveWeek(WEEK);
        setDirtyGuard(false);
        editingDay = -1;
        renderIdealWeek();
    }

    // ── Reset to defaults ─────────────────────────────────────
    window._resetIdealWeek = function () {
        if (confirm('Reset all days to the original Ideal Week? Your edits will be lost.')) {
            localStorage.removeItem(STORAGE_KEY);
            WEEK = JSON.parse(JSON.stringify(DEFAULT_WEEK));
            editingDay = -1;
            renderIdealWeek();
        }
    };

    // ── Inject editor styles ──────────────────────────────────
    function injectStyles() {
        if (document.getElementById('iw-edit-styles')) return;
        const style = document.createElement('style');
        style.id = 'iw-edit-styles';
        style.textContent = `
            .iw-input {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 3px;
                color: var(--text-primary, #e8f0f2);
                padding: 4px 6px;
                font-family: 'Inter', sans-serif;
                outline: none;
                transition: border-color 0.15s;
            }
            .iw-input:focus {
                border-color: rgba(0,200,160,0.4);
            }
            .iw-input::placeholder {
                color: rgba(255,255,255,0.2);
            }
            select.iw-input {
                cursor: pointer;
            }
            select.iw-input option {
                background: #0d1520;
                color: #e8f0f2;
            }
            .iw-btn {
                background: rgba(64,224,208,0.08);
                border: 1px solid rgba(64,224,208,0.15);
                border-radius: 3px;
                color: var(--text-secondary, rgba(232,240,242,0.55));
                padding: 5px 12px;
                font-size: 0.75rem;
                font-family: 'Inter', sans-serif;
                cursor: pointer;
                transition: all 0.15s;
            }
            .iw-btn:hover {
                border-color: rgba(64,224,208,0.35);
                color: var(--text-primary, #e8f0f2);
            }
            .iw-btn-icon {
                width: 24px; height: 24px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 3px;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.15s;
                padding: 0;
                line-height: 1;
                flex-shrink: 0;
            }
            .iw-btn-icon:hover {
                filter: brightness(1.3);
            }
        `;
        document.head.appendChild(style);
    }

    // ── Boot ──────────────────────────────────────────────────
    function boot() {
        injectStyles();
        renderIdealWeek();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
