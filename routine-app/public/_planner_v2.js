
// ============================================================
// PLANNER ENGINE v2 — Named Blocks + Recurring Tasks + Yearly
// ============================================================
(function initPlannerV2() {
    'use strict';

    // ── Constants ──────────────────────────────────────────
    const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const DAYS_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const BLOCK_COLOURS = [
        { name: 'Coral', bg: 'rgba(239,68,68,0.22)', border: '#ef4444', dot: '#ef4444' },
        { name: 'Orange', bg: 'rgba(249,115,22,0.22)', border: '#f97316', dot: '#f97316' },
        { name: 'Amber', bg: 'rgba(245,158,11,0.22)', border: '#f59e0b', dot: '#f59e0b' },
        { name: 'Green', bg: 'rgba(52,211,153,0.22)', border: '#34d399', dot: '#34d399' },
        { name: 'Sky', bg: 'rgba(56,189,248,0.22)', border: '#38bdf8', dot: '#38bdf8' },
        { name: 'Blue', bg: 'rgba(96,165,250,0.22)', border: '#60a5fa', dot: '#60a5fa' },
        { name: 'Violet', bg: 'rgba(167,139,250,0.22)', border: '#a78bfa', dot: '#a78bfa' },
        { name: 'Pink', bg: 'rgba(244,114,182,0.22)', border: '#f472b6', dot: '#f472b6' },
    ];
    const FREE_COLOUR = { bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.12)', dot: 'rgba(255,255,255,0.3)' };
    const EVENT_COLOURS = ['#f472b6', '#60a5fa', '#34d399', '#f97316', '#a78bfa', '#facc15', '#22d3ee', '#ef4444'];
    const DUE_DAYS = DAYS;

    // ── Storage helpers ────────────────────────────────────
    const LS_TEMPLATES = 'symphony_templates_v1';
    const LS_RECURRING = 'symphony_recurring_v1';
    const LS_EVENTS = 'symphony_yearly_events_v1';

    function loadTemplates() { try { return JSON.parse(localStorage.getItem(LS_TEMPLATES) || '{}'); } catch { return {}; } }
    function saveTemplates(d) { localStorage.setItem(LS_TEMPLATES, JSON.stringify(d)); }
    function loadRecurring() { try { return JSON.parse(localStorage.getItem(LS_RECURRING) || '[]'); } catch { return []; } }
    function saveRecurring(d) { localStorage.setItem(LS_RECURRING, JSON.stringify(d)); }
    function loadEvents() { try { return JSON.parse(localStorage.getItem(LS_EVENTS) || '[]'); } catch { return []; } }
    function saveEvents(d) { localStorage.setItem(LS_EVENTS, JSON.stringify(d)); }

    // ── Date utils ─────────────────────────────────────────
    function localDateStr(dt) {
        return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
    }
    function daysSince(dateStr) {
        if (!dateStr) return null;
        const diff = Date.now() - new Date(dateStr + 'T00:00:00').getTime();
        return Math.floor(diff / 86400000);
    }
    function friendlyDate(dateStr) {
        if (!dateStr) return '—';
        const d = new Date(dateStr + 'T00:00:00');
        return `${DAYS_SHORT[d.getDay() === 0 ? 6 : d.getDay() - 1]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
    }
    function todayDowName() {
        const dow = new Date().getDay();
        return DAYS[dow === 0 ? 6 : dow - 1];
    }

    // ── Planner view state ─────────────────────────────────
    let plannerSection = 'template';
    let yearlyYear = new Date().getFullYear();

    // ── Modal state ────────────────────────────────────────
    let blockModal = { day: null, blockId: null };
    let eventModal = { dateStr: null, eventId: null };
    let selectedBlockColour = 0;
    let selectedEventColour = EVENT_COLOURS[0];

    // ── Colour swatches ────────────────────────────────────
    function renderColourPicker(containerId, colours, selectedIdx, onSelect) {
        const el = document.getElementById(containerId);
        if (!el) return;
        el.innerHTML = '';
        colours.forEach((c, i) => {
            const swatch = document.createElement('div');
            const bg = typeof c === 'string' ? c : c.border;
            swatch.style.cssText = `width:22px;height:22px;border-radius:50%;background:${bg};cursor:pointer;border:2px solid ${i === selectedIdx ? '#fff' : 'transparent'};transition:border 0.15s;`;
            swatch.title = typeof c === 'string' ? c : c.name;
            swatch.addEventListener('click', () => { onSelect(i); renderColourPicker(containerId, colours, i, onSelect); });
            el.appendChild(swatch);
        });
    }

    // ─────────────────────────────────────────────────────
    // TEMPLATE EDITOR
    // ─────────────────────────────────────────────────────
    function renderTemplateEditor() {
        const container = document.getElementById('planner-template-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayDay = todayDowName();

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">📋 WEEKLY TEMPLATE</div>`;

        DAYS.forEach(day => {
            const blocks = (templates[day] || []).slice().sort((a, b) => a.start.localeCompare(b.start));
            const isToday = day === todayDay;

            html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; min-height:42px;">`;
            // Day label
            html += `<div style="width:96px; min-width:96px; font-weight:bold; font-size:0.95rem; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'}; border-left:3px solid ${isToday ? 'var(--accent-green)' : 'rgba(255,255,255,0.15)'}; padding-left:8px;">${day}</div>`;

            // Block strip
            html += `<div style="flex:1; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">`;

            if (blocks.length === 0) {
                html += `<div style="background:${FREE_COLOUR.bg}; border:1px dashed ${FREE_COLOUR.border}; border-radius:16px; padding:6px 14px; font-size:0.82rem; color:rgba(255,255,255,0.35); cursor:pointer; user-select:none;" data-add-block="${day}">🕓 Free all day — click to add block</div>`;
            } else {
                // Render each block as a pill
                blocks.forEach(b => {
                    const ci = typeof b.colour === 'number' ? b.colour : 0;
                    const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                    const duration = calcDuration(b.start, b.end);
                    html += `<div class="template-block" data-day="${day}" data-bid="${b.id}" style="background:${c.bg}; border:1px solid ${c.border}; border-radius:16px; padding:6px 14px; font-size:0.85rem; cursor:pointer; user-select:none; display:flex; align-items:center; gap:6px; transition:opacity 0.15s; white-space:nowrap;">`;
                    html += `<span style="width:8px;height:8px;border-radius:50%;background:${c.dot};display:inline-block;flex-shrink:0;"></span>`;
                    html += `<span style="font-weight:bold;">${b.label}</span>`;
                    html += `<span style="opacity:0.6; font-size:0.78rem;">${b.start}–${b.end}${duration ? ' · ' + duration : ''}</span>`;
                    html += `</div>`;
                });
                // Add button at end of strip
                html += `<button data-add-block="${day}" style="background:rgba(52,211,153,0.1); border:1px dashed var(--accent-green); color:var(--accent-green); border-radius:16px; padding:5px 12px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">+ block</button>`;
            }

            html += `</div></div>`;

            // Subtle separator
            if (day !== 'Sunday') {
                html += `<div style="height:1px; background:rgba(255,255,255,0.06); margin:0 0 0 104px; margin-bottom:2px;"></div>`;
            }
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire block clicks (edit)
        container.querySelectorAll('.template-block').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.day, el.dataset.bid));
        });
        // Wire add buttons
        container.querySelectorAll('[data-add-block]').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.addBlock, null));
        });
    }

    function calcDuration(start, end) {
        if (!start || !end) return '';
        const [sh, sm] = start.split(':').map(Number);
        const [eh, em] = end.split(':').map(Number);
        const mins = (eh * 60 + em) - (sh * 60 + sm);
        if (mins <= 0) return '';
        if (mins < 60) return `${mins}m`;
        const h = Math.floor(mins / 60), m = mins % 60;
        return m ? `${h}h ${m}m` : `${h}h`;
    }

    // ── Block Modal ────────────────────────────────────────
    function openBlockModal(day, blockId) {
        blockModal = { day, blockId };
        const modal = document.getElementById('block-modal');
        const titleEl = document.getElementById('block-modal-title');
        const labelEl = document.getElementById('block-label');
        const startEl = document.getElementById('block-start');
        const endEl = document.getElementById('block-end');
        const delBtn = document.getElementById('block-modal-delete');
        if (!modal) return;

        const templates = loadTemplates();
        const blocks = templates[day] || [];
        const block = blockId ? blocks.find(b => b.id === blockId) : null;

        titleEl.textContent = block ? `Edit Block — ${day}` : `Add Block — ${day}`;
        labelEl.value = block ? block.label : '';
        startEl.value = block ? block.start : '07:00';
        endEl.value = block ? block.end : '08:00';
        selectedBlockColour = block ? (block.colour || 0) : 0;
        delBtn.style.display = block ? 'inline-block' : 'none';

        renderColourPicker('block-colour-picker', BLOCK_COLOURS, selectedBlockColour, idx => { selectedBlockColour = idx; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeBlockModal() {
        const modal = document.getElementById('block-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveBlock() {
        const label = document.getElementById('block-label').value.trim();
        const start = document.getElementById('block-start').value;
        const end = document.getElementById('block-end').value;
        if (!label) { alert('Please enter a block name.'); return; }
        const templates = loadTemplates();
        if (!templates[blockModal.day]) templates[blockModal.day] = [];
        const blocks = templates[blockModal.day];
        if (blockModal.blockId) {
            const idx = blocks.findIndex(b => b.id === blockModal.blockId);
            if (idx >= 0) blocks[idx] = { ...blocks[idx], label, start, end, colour: selectedBlockColour };
        } else {
            blocks.push({ id: Date.now().toString(), label, start, end, colour: selectedBlockColour });
        }
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    function deleteBlock() {
        if (!blockModal.blockId) return;
        const templates = loadTemplates();
        const blocks = templates[blockModal.day] || [];
        const idx = blocks.findIndex(b => b.id === blockModal.blockId);
        if (idx >= 0) blocks.splice(idx, 1);
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    // ─────────────────────────────────────────────────────
    // RECURRING TASKS MANAGER
    // ─────────────────────────────────────────────────────
    function renderRecurringManager() {
        const container = document.getElementById('planner-recurring-manager');
        if (!container) return;
        const tasks = loadRecurring();
        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">🔁 RECURRING TASKS</div>`;

        // Add form
        html += `<div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.25rem; align-items:center;">`;
        html += `<input id="rt-title" type="text" placeholder="Task name..." style="flex:2 1 160px; padding:0.35rem 0.6rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<select id="rt-freq" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<option value="weekly">Weekly</option><option value="monthly">Monthly</option></select>`;
        html += `<select id="rt-dueday" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        DAYS.forEach(d => { html += `<option value="${d}">${d}</option>`; });
        html += `</select>`;
        html += `<button id="rt-add-btn" style="padding:0.35rem 1rem; background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.95rem; cursor:pointer; border-radius:3px; font-weight:bold;">+ Add</button>`;
        html += `</div>`;

        // Render two lists
        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            const label = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:1rem;">`;
            html += `<div style="font-size:0.85rem; color:var(--text-secondary); font-weight:bold; margin-bottom:0.4rem; letter-spacing:1px;">${label}</div>`;
            if (list.length === 0) {
                html += `<div style="color:rgba(255,255,255,0.3); font-style:italic; font-size:0.85rem; padding:0.4rem 0;">No ${freq} tasks yet.</div>`;
            } else {
                list.forEach(t => {
                    const ago = daysSince(t.lastDone);
                    const agoText = ago === null ? 'Never done' : ago === 0 ? 'Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                    const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Last done: never';
                    const dueLabel = freq === 'weekly' && t.dueDay ? ` · due by ${t.dueDay}` : '';
                    html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">`;
                    html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.08); border-radius:4px; padding:6px 10px;">`;
                    html += `<div style="font-size:0.9rem; font-weight:bold;">${t.title}<span style="opacity:0.45; font-size:0.78rem;">${dueLabel}</span></div>`;
                    html += `<div style="font-size:0.75rem; color:var(--text-secondary); margin-top:1px;">${lastText}</div>`;
                    html += `</div>`;
                    html += `<button class="rt-delete-btn" data-rtid="${t.id}" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.4); color:#ef4444; border-radius:3px; padding:3px 8px; font-family:'VT323',monospace; font-size:0.85rem; cursor:pointer;">✕</button>`;
                    html += `</div>`;
                });
            }
            html += `</div>`;
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire add
        const addBtn = container.querySelector('#rt-add-btn');
        if (addBtn) addBtn.addEventListener('click', () => {
            const title = container.querySelector('#rt-title').value.trim();
            const freq = container.querySelector('#rt-freq').value;
            const dueDay = container.querySelector('#rt-dueday').value;
            if (!title) return;
            const tasks = loadRecurring();
            tasks.push({ id: Date.now().toString(), title, freq, dueDay: freq === 'weekly' ? dueDay : null, lastDone: null, history: [] });
            saveRecurring(tasks);
            renderRecurringManager();
            renderRecurringDisplay();
        });
        // Wire deletes
        container.querySelectorAll('.rt-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring().filter(t => t.id !== btn.dataset.rtid);
                saveRecurring(tasks);
                renderRecurringManager();
                renderRecurringDisplay();
            });
        });
        // Wire freq toggle for dueday visibility
        const freqSel = container.querySelector('#rt-freq');
        const dueSel = container.querySelector('#rt-dueday');
        if (freqSel && dueSel) {
            freqSel.addEventListener('change', () => {
                dueSel.style.display = freqSel.value === 'weekly' ? 'inline-block' : 'none';
            });
        }
    }

    // ─────────────────────────────────────────────────────
    // YEARLY WALL
    // ─────────────────────────────────────────────────────
    function renderYearlyWall() {
        const container = document.getElementById('planner-yearly-grid');
        if (!container) return;

        const events = loadEvents();
        const todayStr = localDateStr(new Date());
        const nowYear = new Date().getFullYear();
        const MCOLS = ['#60a5fa', '#a78bfa', '#f472b6', '#fb923c', '#facc15', '#34d399', '#22d3ee', '#818cf8', '#f87171', '#4ade80', '#fbbf24', '#c084fc'];

        function daysInMonth(mi) { return new Date(yearlyYear, mi + 1, 0).getDate(); }
        function dateStr(mi, d) {
            if (d > daysInMonth(mi)) return null;
            return `${yearlyYear}-${String(mi + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        }
        function getEventsForDate(str) {
            if (!str) return [];
            const [y, m, d] = str.split('-').map(Number);
            return events.filter(ev => {
                if (ev.recurrence === 'annual') return ev.month === m && ev.day === d;
                return ev.date === str;
            });
        }

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Year nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.5rem; margin-bottom:1rem;">`;
        html += `<button id="yearly-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="font-size:1.8rem; font-weight:bold; color:var(--accent-yellow); letter-spacing:2px;">📌 ${yearlyYear}</div>`;
        html += `<button id="yearly-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;
        html += `<div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.75rem;">Click any date to add/edit an event.</div>`;

        html += `<div style="overflow-x:auto;"><table style="border-collapse:collapse; width:100%; table-layout:fixed; min-width:520px; font-family:'VT323',monospace;">`;

        // Month header row
        html += `<thead><tr>`;
        html += `<th style="width:30px; min-width:30px; padding:3px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.08); color:var(--text-secondary); font-size:0.7rem; text-align:center;">#</th>`;
        MONTHS.forEach((name, mi) => {
            const isCur = mi === new Date().getMonth() && yearlyYear === nowYear;
            html += `<th style="padding:4px 2px; background:${isCur ? 'rgba(52,211,153,0.12)' : 'rgba(0,0,0,0.4)'}; border:1px solid ${isCur ? 'rgba(52,211,153,0.4)' : 'rgba(255,255,255,0.08)'}; color:${isCur ? 'var(--accent-green)' : MCOLS[mi]}; font-size:0.82rem; font-weight:bold; text-align:center; letter-spacing:1px;">${name}</th>`;
        });
        html += `</tr></thead><tbody>`;

        // Day rows 1–31
        for (let d = 1; d <= 31; d++) {
            const altRow = d % 2 === 0;
            html += `<tr>`;
            html += `<td style="padding:1px 3px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.06); color:var(--text-secondary); font-size:0.72rem; text-align:center; font-weight:bold;">${d}</td>`;
            MONTHS.forEach((_, mi) => {
                const str = dateStr(mi, d);
                const isToday = str === todayStr;
                const isValid = str !== null;
                const evs = isValid ? getEventsForDate(str) : [];
                let isWeekend = false;
                if (isValid) {
                    const dow = new Date(str + 'T00:00:00').getDay();
                    isWeekend = dow === 0 || dow === 6;
                }
                const bg = isToday ? 'rgba(52,211,153,0.18)'
                    : !isValid ? 'rgba(0,0,0,0.3)'
                        : isWeekend ? 'rgba(255,255,255,0.025)'
                            : altRow ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.1)';
                const bdr = isToday ? '1px solid rgba(52,211,153,0.5)' : '1px solid rgba(255,255,255,0.05)';
                const glow = isToday ? 'box-shadow:inset 0 0 0 1px rgba(52,211,153,0.4);' : '';

                let inner = '';
                if (!isValid) {
                    inner = `<div style="width:100%;height:100%;background:repeating-linear-gradient(45deg,rgba(255,255,255,0.015) 0,rgba(255,255,255,0.015) 1px,transparent 1px,transparent 4px);"></div>`;
                } else if (evs.length > 0) {
                    evs.slice(0, 2).forEach(ev => {
                        inner += `<div style="background:${ev.color}22; border-left:2px solid ${ev.color}; border-radius:1px; padding:0 2px; font-size:0.58rem; line-height:1.4; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${ev.emoji || ''} ${ev.label}</div>`;
                    });
                }

                const cursor = isValid ? 'cursor:pointer;' : 'cursor:default;';
                html += `<td class="yearly-cell" data-date="${str || ''}" data-valid="${isValid ? '1' : '0'}"
                    style="padding:1px; background:${bg}; border:${bdr}; height:24px; vertical-align:top; overflow:hidden; ${cursor} ${glow} transition:background 0.1s;"
                    title="${str || 'n/a'}">
                    ${inner}
                </td>`;
            });
            html += `</tr>`;
        }
        html += `</tbody></table></div></div>`;
        container.innerHTML = html;

        // Year nav
        container.querySelector('#yearly-prev').addEventListener('click', () => { yearlyYear--; renderYearlyWall(); });
        container.querySelector('#yearly-next').addEventListener('click', () => { yearlyYear++; renderYearlyWall(); });

        // Cell clicks
        container.querySelectorAll('.yearly-cell').forEach(cell => {
            if (cell.dataset.valid !== '1') return;
            cell.addEventListener('mouseenter', () => { cell.style.background = 'rgba(52,211,153,0.1)'; });
            cell.addEventListener('mouseleave', () => { cell.style.background = ''; });
            cell.addEventListener('click', () => openEventModal(cell.dataset.date));
        });
    }

    // ── Event Modal ────────────────────────────────────────
    function openEventModal(dateStr_arg) {
        const modal = document.getElementById('event-modal');
        const titleEl = document.getElementById('event-modal-title');
        const labelEl = document.getElementById('event-label');
        const emojiEl = document.getElementById('event-emoji');
        const annualEl = document.getElementById('event-annual');
        const delBtn = document.getElementById('event-modal-delete');
        if (!modal) return;

        const [y, m, d] = dateStr_arg.split('-').map(Number);
        const events = loadEvents();
        // Find existing event on this specific date
        const existing = events.find(ev => ev.recurrence === 'once' ? ev.date === dateStr_arg : (ev.month === m && ev.day === d));

        eventModal = { dateStr: dateStr_arg, eventId: existing ? existing.id : null };
        titleEl.textContent = existing
            ? `Edit Event — ${MONTHS[m - 1]} ${d}`
            : `Add Event — ${MONTHS[m - 1]} ${d}`;
        labelEl.value = existing ? existing.label : '';
        emojiEl.value = existing ? (existing.emoji || '📅') : '📅';
        annualEl.checked = existing ? existing.recurrence === 'annual' : false;
        selectedEventColour = existing ? existing.color : EVENT_COLOURS[0];
        delBtn.style.display = existing ? 'inline-block' : 'none';

        renderColourPicker('event-colour-picker', EVENT_COLOURS, EVENT_COLOURS.indexOf(selectedEventColour) || 0, idx => { selectedEventColour = EVENT_COLOURS[idx]; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeEventModal() {
        const modal = document.getElementById('event-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveEvent() {
        const label = document.getElementById('event-label').value.trim();
        const emoji = document.getElementById('event-emoji').value;
        const annual = document.getElementById('event-annual').checked;
        if (!label) { alert('Please enter an event name.'); return; }
        const [y, m, d] = eventModal.dateStr.split('-').map(Number);
        const events = loadEvents();
        const newEv = { id: eventModal.eventId || Date.now().toString(), label, emoji, color: selectedEventColour, recurrence: annual ? 'annual' : 'once' };
        if (annual) { newEv.month = m; newEv.day = d; }
        else { newEv.date = eventModal.dateStr; }
        const idx = events.findIndex(e => e.id === newEv.id);
        if (idx >= 0) events[idx] = newEv; else events.push(newEv);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    function deleteEvent() {
        if (!eventModal.eventId) return;
        const events = loadEvents().filter(e => e.id !== eventModal.eventId);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    // ─────────────────────────────────────────────────────
    // SCHEDULE PAGE — Day display + Recurring Tasks
    // ─────────────────────────────────────────────────────
    let schedDayOffset = 0;

    function renderScheduleDisplay() {
        renderScheduleDayBlocks();
        renderRecurringDisplay();
    }

    function renderScheduleDayBlocks() {
        const container = document.getElementById('schedule-week-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayStr = localDateStr(new Date());

        const viewDate = new Date();
        viewDate.setDate(viewDate.getDate() + schedDayOffset);
        const viewDow = viewDate.getDay();
        const dayName = DAYS[viewDow === 0 ? 6 : viewDow - 1];
        const isToday = localDateStr(viewDate) === todayStr;

        const blocks = (templates[dayName] || []).slice().sort((a, b) => a.start.localeCompare(b.start));

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.25rem; margin-bottom:1.25rem;">`;
        html += `<button id="sched-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="text-align:center; min-width:200px;">`;
        html += `<div style="font-size:1.6rem; font-weight:bold; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'};">${dayName}${isToday ? ' <span style="font-size:0.7rem;">← TODAY</span>' : ''}</div>`;
        html += `<div style="font-size:0.82rem; color:var(--text-secondary);">${viewDate.getDate()}/${viewDate.getMonth() + 1}/${viewDate.getFullYear()}</div>`;
        if (!isToday) { html += `<button id="sched-today" style="margin-top:3px; background:none; border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.78rem; padding:1px 10px; cursor:pointer; border-radius:2px;">↩ Today</button>`; }
        html += `</div>`;
        html += `<button id="sched-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;

        // Blocks
        if (blocks.length === 0) {
            html += `<div style="background:rgba(52,211,153,0.04); border:1px solid rgba(52,211,153,0.15); border-radius:6px; padding:2rem; text-align:center; color:var(--text-secondary);">No template set for ${dayName}. Go to Planner → Template to add blocks.</div>`;
        } else {
            html += `<div style="display:flex; flex-direction:column; gap:6px;">`;
            blocks.forEach(b => {
                const ci = typeof b.colour === 'number' ? b.colour : 0;
                const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                const dur = calcDuration(b.start, b.end);
                html += `<div style="background:${c.bg}; border-left:3px solid ${c.border}; border-radius:4px; padding:10px 14px; display:flex; align-items:center; gap:12px;">`;
                html += `<div style="text-align:right; min-width:90px; font-size:0.82rem; color:var(--text-secondary);">${b.start} – ${b.end}</div>`;
                html += `<div style="flex:1;"><div style="font-size:1rem; font-weight:bold;">${b.label}</div>${dur ? `<div style="font-size:0.75rem; color:${c.border}; opacity:0.7;">${dur}</div>` : ''}</div>`;
                html += `</div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
        container.innerHTML = html;

        // Wire nav
        container.querySelector('#sched-prev')?.addEventListener('click', () => { schedDayOffset--; renderScheduleDayBlocks(); });
        container.querySelector('#sched-next')?.addEventListener('click', () => { schedDayOffset++; renderScheduleDayBlocks(); });
        container.querySelector('#sched-today')?.addEventListener('click', () => { schedDayOffset = 0; renderScheduleDayBlocks(); });
    }

    function renderRecurringDisplay() {
        // Find or create the recurring display container in schedule section
        let container = document.getElementById('schedule-recurring-display');
        if (!container) {
            const schedGrid = document.getElementById('schedule-week-grid');
            if (!schedGrid) return;
            container = document.createElement('div');
            container.id = 'schedule-recurring-display';
            container.style.marginTop = '1.5rem';
            schedGrid.parentNode.insertBefore(container, schedGrid.nextSibling);
        }

        const tasks = loadRecurring();
        if (tasks.length === 0) { container.innerHTML = ''; return; }

        const todayStr = localDateStr(new Date());
        const todayDow = new Date().getDay(); // 0=Sun
        const todayDayName = DAYS[todayDow === 0 ? 6 : todayDow - 1];
        // Which Monday started this week?
        const monday = new Date();
        const dayOfWeek = monday.getDay();
        const daysToMon = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        monday.setDate(monday.getDate() - daysToMon);
        const weekStartStr = localDateStr(monday);

        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px; border-top:1px solid rgba(255,255,255,0.08); padding-top:1rem;">🔁 RECURRING TASKS</div>`;

        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            if (list.length === 0) return;
            const freqLabel = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:0.75rem;">`;
            html += `<div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.35rem; letter-spacing:1px;">${freqLabel}</div>`;
            list.forEach(t => {
                const ago = daysSince(t.lastDone);
                const agoText = ago === null ? 'Never done' : ago === 0 ? '✓ Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Never done';

                // Overdue logic for weekly tasks
                let overdue = false;
                if (freq === 'weekly' && t.dueDay) {
                    const dueIdx = DAYS.indexOf(t.dueDay);
                    const curIdx = DAYS.indexOf(todayDayName);
                    const doneSinceWeekStart = t.lastDone && t.lastDone >= weekStartStr;
                    overdue = !doneSinceWeekStart && curIdx >= dueIdx;
                }

                const doneToday = t.lastDone === todayStr;
                const dueLabel = freq === 'weekly' && t.dueDay ? ` <span style="opacity:0.5; font-size:0.78rem;">· due by ${t.dueDay}</span>` : '';

                html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">`;
                html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid ${overdue ? 'rgba(239,68,68,0.4)' : 'rgba(255,255,255,0.07)'}; border-radius:4px; padding:7px 10px;">`;
                html += `<div style="font-size:0.92rem; font-weight:bold;">${t.title}${dueLabel}${overdue ? ' <span style="color:#ef4444; font-size:0.75rem;">⚠ OVERDUE</span>' : ''}</div>`;
                html += `<div style="font-size:0.75rem; color:${doneToday ? 'var(--accent-green)' : 'var(--text-secondary)'}; margin-top:1px;">${lastText}</div>`;
                html += `</div>`;
                if (!doneToday) {
                    html += `<button class="rt-done-btn" data-rtid="${t.id}" style="background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); border-radius:3px; padding:5px 10px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">✓ Done</button>`;
                } else {
                    html += `<div style="color:var(--accent-green); font-size:0.82rem; padding:5px 8px;">✓</div>`;
                }
                html += `</div>`;
            });
            html += `</div>`;
        });
        html += `</div>`;
        container.innerHTML = html;

        // Wire done buttons
        container.querySelectorAll('.rt-done-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring();
                const t = tasks.find(t => t.id === btn.dataset.rtid);
                if (!t) return;
                t.lastDone = todayStr;
                if (!t.history) t.history = [];
                t.history.push(todayStr);
                saveRecurring(tasks);
                renderRecurringDisplay();
                renderRecurringManager();
            });
        });
    }

    // ─────────────────────────────────────────────────────
    // PLANNER VIEW SWITCHING
    // ─────────────────────────────────────────────────────
    function switchPlannerView(view) {
        plannerSection = view;
        const tmplBtn = document.getElementById('planner-view-template');
        const yearlyBtn = document.getElementById('planner-view-yearly');
        const tmplSec = document.getElementById('planner-template-section');
        const yearlySec = document.getElementById('planner-yearly-section');
        const ACTIVE = { background: 'rgba(52,211,153,0.2)', borderColor: 'var(--accent-green)', color: 'var(--accent-green)', fontWeight: 'bold' };
        const INACTIVE = { background: 'rgba(0,0,0,0.2)', borderColor: 'var(--glass-border)', color: 'var(--text-secondary)', fontWeight: 'normal' };
        const applyStyle = (btn, s) => { if (!btn) return; Object.assign(btn.style, s); };

        if (view === 'yearly') {
            applyStyle(tmplBtn, INACTIVE);
            applyStyle(yearlyBtn, ACTIVE);
            if (tmplSec) tmplSec.style.display = 'none';
            if (yearlySec) yearlySec.style.display = 'block';
            renderYearlyWall();
        } else {
            applyStyle(tmplBtn, ACTIVE);
            applyStyle(yearlyBtn, INACTIVE);
            if (tmplSec) tmplSec.style.display = 'block';
            if (yearlySec) yearlySec.style.display = 'none';
            renderTemplateEditor();
            renderRecurringManager();
        }
    }

    // ─────────────────────────────────────────────────────
    // INIT
    // ─────────────────────────────────────────────────────
    function boot() {
        // Planner view toggles
        document.getElementById('planner-view-template')?.addEventListener('click', () => switchPlannerView('template'));
        document.getElementById('planner-view-yearly')?.addEventListener('click', () => switchPlannerView('yearly'));

        // Block modal buttons
        document.getElementById('block-modal-save')?.addEventListener('click', saveBlock);
        document.getElementById('block-modal-delete')?.addEventListener('click', deleteBlock);
        document.getElementById('block-modal-cancel')?.addEventListener('click', closeBlockModal);
        document.getElementById('block-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeBlockModal(); });

        // Event modal buttons
        document.getElementById('event-modal-save')?.addEventListener('click', saveEvent);
        document.getElementById('event-modal-delete')?.addEventListener('click', deleteEvent);
        document.getElementById('event-modal-cancel')?.addEventListener('click', closeEventModal);
        document.getElementById('event-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeEventModal(); });

        // Hook planner tab
        document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
            btn.addEventListener('click', () => {
                const t = btn.getAttribute('data-tab');
                if (t === 'planner') { switchPlannerView(plannerSection); }
                if (t === 'today') { renderScheduleDisplay(); }
            });
        });

        // Initial render
        switchPlannerView('template');
        renderScheduleDisplay();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
// --- End Planner Engine v2 ---
