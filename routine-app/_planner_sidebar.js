// ============================================================
// PLANNER SIDEBAR — Mini Cal + Tasks + Notes
// ============================================================
(function initPlannerSidebar() {
    'use strict';

    const LS_TASKS = 'symphony_planner_tasks';
    const LS_NOTES = 'symphony_planner_notes';

    // ── Mini Calendar ─────────────────────────────────
    function renderMiniCal() {
        const el = document.getElementById('planner-mini-cal');
        if (!el) return;

        const now = new Date();
        const y = now.getFullYear();
        const m = now.getMonth();
        const today = now.getDate();

        const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];
        const DAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

        const firstDow = new Date(y, m, 1).getDay(); // 0=Sun
        const daysInMonth = new Date(y, m + 1, 0).getDate();

        let html = `<div class="mini-cal-month-label">${MONTHS[m]} ${y}</div>`;
        html += `<div class="mini-cal-grid">`;

        // Day headers
        DAYS.forEach(d => {
            html += `<div class="mini-cal-day-header">${d}</div>`;
        });

        // Empty leading cells
        for (let i = 0; i < firstDow; i++) {
            html += `<div class="mini-cal-cell other-month"></div>`;
        }

        // Day cells
        for (let d = 1; d <= daysInMonth; d++) {
            const isToday = d === today;
            html += `<div class="mini-cal-cell${isToday ? ' today' : ''}">${d}</div>`;
        }

        html += `</div>`;
        el.innerHTML = html;
    }

    // ── Tasks ─────────────────────────────────────────
    function loadTasks() {
        try { return JSON.parse(localStorage.getItem(LS_TASKS) || '[]'); } catch { return []; }
    }
    function saveTasks(tasks) { localStorage.setItem(LS_TASKS, JSON.stringify(tasks)); }

    function renderTasks() {
        const list = document.getElementById('planner-task-list');
        if (!list) return;
        const tasks = loadTasks();
        list.innerHTML = tasks.map((t, i) => `
            <li class="sidebar-task-item${t.done ? ' done' : ''}" data-idx="${i}">
                <input type="checkbox" ${t.done ? 'checked' : ''}>
                <span>${escHtml(t.text)}</span>
                <button title="Remove">✕</button>
            </li>
        `).join('');

        list.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', () => {
                const idx = +cb.closest('li').dataset.idx;
                const tasks = loadTasks();
                tasks[idx].done = cb.checked;
                saveTasks(tasks);
                renderTasks();
            });
        });

        list.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = +btn.closest('li').dataset.idx;
                const tasks = loadTasks();
                tasks.splice(idx, 1);
                saveTasks(tasks);
                renderTasks();
            });
        });
    }

    function wireTaskInput() {
        const input = document.getElementById('planner-task-input');
        if (!input) return;
        input.addEventListener('keydown', e => {
            if (e.key !== 'Enter') return;
            const text = input.value.trim();
            if (!text) return;
            const tasks = loadTasks();
            tasks.push({ text, done: false });
            saveTasks(tasks);
            input.value = '';
            renderTasks();
        });
    }

    // ── Notes ─────────────────────────────────────────
    function initNotes() {
        const area = document.getElementById('planner-notes-area');
        if (!area) return;
        area.value = localStorage.getItem(LS_NOTES) || '';
        area.addEventListener('input', () => {
            localStorage.setItem(LS_NOTES, area.value);
        });
    }

    // ── Helpers ───────────────────────────────────────
    function escHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    // ── Boot ──────────────────────────────────────────
    function boot() {
        renderMiniCal();
        renderTasks();
        wireTaskInput();
        initNotes();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();
