"""
Patch: Add Task Pool panel with drag-to-schedule to the Schedule page.
Run from: routine-app/ directory
"""
import re, sys, os

JS_FILE = os.path.join(os.path.dirname(__file__), 'symphony-app.js')

with open(JS_FILE, 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Add LS_TODAY_EXTRAS constant after LS_EVENTS ──────────────────────────
OLD_LS = "    const LS_EVENTS = 'symphony_yearly_events_v1';"
NEW_LS = """    const LS_EVENTS = 'symphony_yearly_events_v1';
    const LS_TODAY_EXTRAS = 'symphony_today_extras_v1';
    function loadTodayExtras() { try { return JSON.parse(localStorage.getItem(LS_TODAY_EXTRAS) || '{}'); } catch { return {}; } }
    function saveTodayExtras(d) { localStorage.setItem(LS_TODAY_EXTRAS, JSON.stringify(d)); }"""

if OLD_LS not in src:
    print('ERROR: LS_EVENTS anchor not found'); sys.exit(1)
src = src.replace(OLD_LS, NEW_LS, 1)

# ── 2. Give each block a class + data-slot and add today-extras display ───────
OLD_BLOCK_RENDER = """        if (blocks.length === 0) {
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
        }"""

NEW_BLOCK_RENDER = """        const todayExtras = loadTodayExtras();
        const extrasForDay = todayExtras[dayName] || [];

        if (blocks.length === 0) {
            html += `<div class="sched-drop-zone" data-slot="unscheduled" style="background:rgba(52,211,153,0.04); border:1px dashed rgba(52,211,153,0.2); border-radius:6px; padding:2rem; text-align:center; color:var(--text-secondary);">No template set for ${dayName}. Go to Planner → Template to add blocks.</div>`;
        } else {
            html += `<div style="display:flex; flex-direction:column; gap:6px;">`;
            blocks.forEach(b => {
                const ci = typeof b.colour === 'number' ? b.colour : 0;
                const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                const dur = calcDuration(b.start, b.end);
                const slotExtras = extrasForDay.filter(e => e.slot === b.start);
                html += `<div class="sched-block-wrap">`;
                html += `<div class="sched-drop-zone" data-slot="${b.start}" style="background:${c.bg}; border-left:3px solid ${c.border}; border-radius:4px; padding:10px 14px; display:flex; align-items:center; gap:12px; transition: outline 0.15s;">`;
                html += `<div style="text-align:right; min-width:90px; font-size:0.82rem; color:var(--text-secondary);">${b.start} \u2013 ${b.end}</div>`;
                html += `<div style="flex:1;"><div style="font-size:1rem; font-weight:bold;">${b.label}</div>${dur ? `<div style="font-size:0.75rem; color:${c.border}; opacity:0.7;">${dur}</div>` : ''}</div>`;
                html += `</div>`;
                if (slotExtras.length > 0) {
                    slotExtras.forEach(ex => {
                        html += `<div class="sched-extra-task" data-extra-id="${ex.id}" data-day="${dayName}" style="margin-left:24px; margin-top:3px; background:rgba(155,89,255,0.08); border-left:3px solid var(--accent-magenta,#c084fc); border-radius:4px; padding:6px 12px; display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">`;
                        html += `<span>\u2937 ${ex.label}</span>`;
                        html += `<span class="remove-extra-btn" data-extra-id="${ex.id}" data-day="${dayName}" style="cursor:pointer; color:rgba(255,255,255,0.3); font-size:1rem; line-height:1; padding:0 4px;">\u00d7</span>`;
                        html += `</div>`;
                    });
                }
                html += `</div>`;
            });
            html += `</div>`;
        }
        // Unscheduled extras (dropped without a specific slot)
        const unscheduledExtras = extrasForDay.filter(e => e.slot === 'unscheduled');
        if (unscheduledExtras.length > 0) {
            html += `<div style="margin-top:8px; display:flex; flex-direction:column; gap:4px;">`;
            unscheduledExtras.forEach(ex => {
                html += `<div class="sched-extra-task" data-extra-id="${ex.id}" data-day="${dayName}" style="margin-left:24px; background:rgba(155,89,255,0.08); border-left:3px solid var(--accent-magenta,#c084fc); border-radius:4px; padding:6px 12px; display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">`;
                html += `<span>\u2937 ${ex.label}</span>`;
                html += `<span class="remove-extra-btn" data-extra-id="${ex.id}" data-day="${dayName}" style="cursor:pointer; color:rgba(255,255,255,0.3); font-size:1rem; line-height:1; padding:0 4px;">\u00d7</span>`;
                html += `</div>`;
            });
            html += `</div>`;
        }"""

if OLD_BLOCK_RENDER not in src:
    print('ERROR: block render anchor not found'); sys.exit(1)
src = src.replace(OLD_BLOCK_RENDER, NEW_BLOCK_RENDER, 1)

# ── 3. After the nav wire-up, add drop zone wiring + renderTaskPool call ──────
OLD_WIRE = """        // Wire nav
        container.querySelector('#sched-prev')?.addEventListener('click', () => { schedDayOffset--; renderScheduleDayBlocks(); });
        container.querySelector('#sched-next')?.addEventListener('click', () => { schedDayOffset++; renderScheduleDayBlocks(); });
        container.querySelector('#sched-today')?.addEventListener('click', () => { schedDayOffset = 0; renderScheduleDayBlocks(); });
    }"""

NEW_WIRE = """        // Wire nav
        container.querySelector('#sched-prev')?.addEventListener('click', () => { schedDayOffset--; renderScheduleDayBlocks(); });
        container.querySelector('#sched-next')?.addEventListener('click', () => { schedDayOffset++; renderScheduleDayBlocks(); });
        container.querySelector('#sched-today')?.addEventListener('click', () => { schedDayOffset = 0; renderScheduleDayBlocks(); });

        // Wire drop zones
        container.querySelectorAll('.sched-drop-zone').forEach(zone => {
            zone.addEventListener('dragover', e => { e.preventDefault(); zone.style.outline = '2px dashed var(--accent-magenta,#c084fc)'; });
            zone.addEventListener('dragleave', () => { zone.style.outline = ''; });
            zone.addEventListener('drop', e => {
                e.preventDefault();
                zone.style.outline = '';
                const taskId = e.dataTransfer.getData('taskId');
                const taskLabel = e.dataTransfer.getData('taskLabel');
                if (!taskId) return;
                const slot = zone.dataset.slot || 'unscheduled';
                const extras = loadTodayExtras();
                if (!extras[dayName]) extras[dayName] = [];
                // Avoid duplicates
                if (extras[dayName].some(ex => ex.id === taskId && ex.slot === slot)) return;
                extras[dayName].push({ id: taskId, label: taskLabel, slot });
                saveTodayExtras(extras);
                renderScheduleDayBlocks();
            });
        });

        // Wire remove buttons
        container.querySelectorAll('.remove-extra-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const extras = loadTodayExtras();
                const day = btn.dataset.day;
                if (extras[day]) extras[day] = extras[day].filter(e => e.id !== btn.dataset.extraId);
                saveTodayExtras(extras);
                renderScheduleDayBlocks();
            });
        });

        // Render task pool below
        renderTaskPool(container.closest('#today') || container);
    }"""

if OLD_WIRE not in src:
    print('ERROR: nav wire anchor not found'); sys.exit(1)
src = src.replace(OLD_WIRE, NEW_WIRE, 1)

# ── 4. Add renderTaskPool function after renderScheduleDayBlocks ──────────────
INSERT_AFTER = """    function renderRecurringDisplay() {"""

TASK_POOL_FN = r"""    async function renderTaskPool(schedContainer) {
        // Remove any existing pool
        const existing = schedContainer.querySelector('#schedule-task-pool');
        if (existing) existing.remove();

        let tasks = [];
        try {
            const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true&select=id,title,priority_color,time_target`, {
                headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
            });
            if (resp.ok) tasks = await resp.json();
        } catch(e) { console.warn('Task pool fetch failed', e); return; }

        const lastDone = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');

        // Sort: never-done first, then oldest-done first
        tasks.sort((a, b) => {
            const da = lastDone[a.id] ? new Date(lastDone[a.id]) : new Date(0);
            const db = lastDone[b.id] ? new Date(lastDone[b.id]) : new Date(0);
            return da - db;
        });

        const pool = document.createElement('div');
        pool.id = 'schedule-task-pool';
        pool.style.cssText = 'margin-top:1.75rem; font-family:"VT323",monospace;';

        let html = `<div style="font-size:1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.6rem; letter-spacing:1px;">\\u{1F4CB} TASK POOL <span style="font-size:0.72rem; color:var(--text-secondary); font-weight:normal;">\u2014 drag onto a time block above</span></div>`;
        html += `<div style="display:flex; flex-wrap:wrap; gap:8px;">`;

        tasks.forEach(task => {
            const lastDoneTs = lastDone[task.id] ? new Date(lastDone[task.id]) : null;
            const daysSince = lastDoneTs ? Math.floor((Date.now() - lastDoneTs) / 86400000) : null;
            const lastDoneLabel = daysSince === null ? 'never done' : daysSince === 0 ? 'done today' : `${daysSince}d ago`;
            const isDoneToday = daysSince === 0;

            let colorBorder = 'rgba(255,255,255,0.15)';
            if (task.priority_color === 'RED') colorBorder = 'var(--accent-red,#ef4444)';
            if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange,#f97316)';
            if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green,#34d399)';

            // Escape label for data attribute
            const safeLabel = task.title.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

            html += `<div class="pool-task-card" draggable="true" data-task-id="${task.id}" data-task-label="${safeLabel}" style="background:rgba(0,0,0,0.3); border:1px solid ${colorBorder}; border-radius:6px; padding:7px 12px; cursor:grab; opacity:${isDoneToday ? '0.4' : '1'}; min-width:120px; max-width:200px; user-select:none;">`;
            html += `<div style="font-size:0.88rem; font-weight:bold; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${task.title}</div>`;
            html += `<div style="font-size:0.7rem; color:var(--text-secondary); margin-top:2px;">\u{1F550} ${lastDoneLabel}</div>`;
            html += `</div>`;
        });

        html += `</div>`;
        pool.innerHTML = html;
        schedContainer.appendChild(pool);

        // Wire drag start on pool cards
        pool.querySelectorAll('.pool-task-card').forEach(card => {
            card.addEventListener('dragstart', e => {
                e.dataTransfer.setData('taskId', card.dataset.taskId);
                e.dataTransfer.setData('taskLabel', card.dataset.taskLabel);
                card.style.opacity = '0.3';
            });
            card.addEventListener('dragend', () => {
                card.style.opacity = card.dataset.taskId ? (card.style.opacity === '0.3' ? '1' : card.style.opacity) : '1';
                // Refresh to restore correct done-today opacity
                renderTaskPool(schedContainer);
            });
        });
    }

    function renderRecurringDisplay() {"""

if INSERT_AFTER not in src:
    print('ERROR: renderRecurringDisplay anchor not found'); sys.exit(1)
src = src.replace(INSERT_AFTER, TASK_POOL_FN, 1)

with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(src)

print('Patch applied successfully.')
