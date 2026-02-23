/**
 * Symphony 2.0 - App Logic & State Manager
 */

document.addEventListener('DOMContentLoaded', () => {
    // ---------------------------------------------------------
    // 1. Security & Lock Screen
    // ---------------------------------------------------------
    const CORRECT_PASSWORD = "symphony2026";
    const lockScreen = document.getElementById('lock-screen');
    const appContent = document.getElementById('app-content');
    const passwordInput = document.getElementById('password-input');
    const unlockBtn = document.getElementById('unlock-btn');
    const passwordError = document.getElementById('password-error');

    function checkAuth() {
        if (localStorage.getItem('symphony_v2_auth') === 'true') {
            lockScreen.style.display = 'none';
            appContent.style.display = 'flex';
            initDashboard();
        } else {
            lockScreen.style.display = 'flex';
            appContent.style.display = 'none';
        }
    }

    unlockBtn.addEventListener('click', () => {
        if (passwordInput.value === CORRECT_PASSWORD) {
            localStorage.setItem('symphony_v2_auth', 'true');
            passwordError.style.display = 'none';
            checkAuth();
        } else {
            passwordError.style.display = 'block';
            passwordInput.value = '';
            passwordInput.focus();
        }
    });

    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') unlockBtn.click();
    });

    checkAuth();

    // ---------------------------------------------------------
    // 2. Global State & Initialization
    // ---------------------------------------------------------
    let appState = window.SymphonyData;

    function initDashboard() {
        // Set Date
        const dateOptions = { weekday: 'long', month: 'short', day: 'numeric' };
        document.getElementById('current-date-display').textContent = new Date().toLocaleDateString('en-US', dateOptions);

        // Set Mode
        document.getElementById('current-mode-display').textContent = `Mode: ${appState.activeMode}`;

        // Generate Dynamic Timeline
        appState.timeline = window.generateTodayTimeline();

        // Load Persisted Data (Merge logic)
        loadPersistedState();

        // Render everything
        renderTimeline();
        renderWeekOverview();
        renderChecklist('daily-pool-list', appState.pools.daily, 'pools.daily');
        renderChecklist('weekly-reset-list', appState.pools.weekly, 'pools.weekly');
        renderChecklist('monthly-audit-list', appState.pools.monthly, 'pools.monthly');
        renderChecklist('supplement-stack-list', appState.bioProtocols.supplements, 'bio.supplements');
        renderChecklist('dog-training-list', appState.bioProtocols.dogTraining, 'bio.dogTraining');
        renderWorkouts();

        // Tab Setup
        setupTabs();

        // AI Sync Setup
        setupAISync();
    }

    // ---------------------------------------------------------
    // 3. Tab Navigation
    // ---------------------------------------------------------
    function setupTabs() {
        const tabs = document.querySelectorAll('.nav-btn');
        const contents = document.querySelectorAll('.tab-content');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));

                tab.classList.add('active');
                document.getElementById(tab.dataset.tab).classList.add('active');
            });
        });
    }

    // ---------------------------------------------------------
    // 4. Persistence Engine (Save to LocalStorage by ID)
    // ---------------------------------------------------------
    function saveState() {
        // We only save the completion status mapping by ID to prevent mismatches
        const completionMap = {};

        appState.timeline.forEach(item => completionMap[item.id] = item.completed);
        ['daily', 'weekly', 'monthly'].forEach(pool => {
            appState.pools[pool].forEach(item => completionMap[item.id] = item.completed);
        });
        appState.bioProtocols.supplements.forEach(item => completionMap[item.id] = item.completed);
        appState.bioProtocols.dogTraining.forEach(item => completionMap[item.id] = item.completed);

        localStorage.setItem('symphony_v2_state', JSON.stringify(completionMap));
        updateProgress();
    }

    function loadPersistedState() {
        const saved = JSON.parse(localStorage.getItem('symphony_v2_state') || '{}');

        appState.timeline.forEach(item => { if (saved[item.id] !== undefined) item.completed = saved[item.id]; });
        ['daily', 'weekly', 'monthly'].forEach(pool => {
            appState.pools[pool].forEach(item => { if (saved[item.id] !== undefined) item.completed = saved[item.id]; });
        });
        appState.bioProtocols.supplements.forEach(item => { if (saved[item.id] !== undefined) item.completed = saved[item.id]; });
        appState.bioProtocols.dogTraining.forEach(item => { if (saved[item.id] !== undefined) item.completed = saved[item.id]; });
    }

    // ---------------------------------------------------------
    // 5. Renderers
    // ---------------------------------------------------------
    function renderTimeline() {
        const container = document.getElementById('dynamic-timeline');
        container.innerHTML = '';

        appState.timeline.forEach(item => {
            const el = document.createElement('div');
            el.className = `timeline-item ${item.completed ? 'completed' : ''}`;

            const tagsHtml = item.tags.map(tag => {
                const colorClass = tag === "Health" || tag === "Bio" ? 'health' : (tag === "Workout" ? 'focus' : '');
                return `<span class="tag ${colorClass}">${tag}</span>`;
            }).join('');

            el.innerHTML = `
                <span class="timeline-time">${item.time}</span>
                <div class="timeline-content">
                    <div class="timeline-title">${item.title}</div>
                    <div class="timeline-desc">${item.desc}</div>
                    <div class="tags">${tagsHtml}</div>
                </div>
            `;

            el.addEventListener('click', () => {
                item.completed = !item.completed;
                el.classList.toggle('completed');
                saveState();
            });

            container.appendChild(el);
        });
        updateProgress();
    }

    function renderWeekOverview() {
        // Render custom notes
        const notesContainer = document.getElementById('weekly-notes-container');
        if (appState.weeklyNotes && appState.weeklyNotes.length > 0) {
            notesContainer.innerHTML = `<strong style="display:block; margin-bottom: 0.5rem; color: #EAB308;">⚠️ Custom Notes & Appointments:</strong>` +
                appState.weeklyNotes.map(n => `• ${n}`).join('<br>');
            notesContainer.style.display = 'block';
        } else {
            notesContainer.style.display = 'none';
        }

        // Render week grid
        const grid = document.getElementById('week-grid');
        grid.innerHTML = '';
        if (appState.weekOverview) {
            appState.weekOverview.forEach(day => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.padding = '1.25rem';
                card.innerHTML = `
                    <h3 style="display:flex; justify-content:space-between; align-items: center; margin-bottom: 0.5rem;">
                        ${day.day} 
                        <span class="badge ${day.type === 'work' ? 'focus' : 'info'}">${day.type.toUpperCase()}</span>
                    </h3>
                    <p class="subtext" style="color: rgba(255,255,255,0.8);">${day.focus}</p>
                `;
                grid.appendChild(card);
            });
        }
    }

    function renderChecklist(containerId, listArray, categoryName) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        listArray.forEach(item => {
            const li = document.createElement('li');
            if (item.completed) li.classList.add('completed');

            li.innerHTML = `
                <div class="checkbox"></div>
                <div class="task-text">${item.text}</div>
            `;

            li.addEventListener('click', () => {
                item.completed = !item.completed;
                li.classList.toggle('completed');
                saveState();
            });

            container.appendChild(li);
        });
    }

    function renderWorkouts() {
        const grid = document.getElementById('workout-dashboard');
        grid.innerHTML = '';

        appState.longevityWorkouts.forEach(workout => {
            const card = document.createElement('div');
            card.className = 'card workout-card';

            const exHtml = workout.exercises.map(ex => `<li>${ex}</li>`).join('');

            card.innerHTML = `
                <h3>${workout.day}</h3>
                <div class="workout-meta">${workout.type} • ${workout.meta}</div>
                <ul class="workout-exercises">
                    ${exHtml}
                </ul>
                <button class="btn ai-btn" style="align-self: flex-start; margin-top: 1rem; font-size: 0.8rem; padding: 0.5rem 1rem;">
                    Log Completion
                </button>
            `;
            grid.appendChild(card);
        });
    }

    function updateProgress() {
        const total = appState.timeline.length;
        const completed = appState.timeline.filter(t => t.completed).length;
        const percent = total > 0 ? Math.round((completed / total) * 100) : 0;

        document.getElementById('timeline-progress-bar').style.width = `${percent}%`;
        document.getElementById('timeline-progress-text').textContent = `${percent}%`;
    }

    // ---------------------------------------------------------
    // 6. AI Sync Export
    // ---------------------------------------------------------
    function setupAISync() {
        document.getElementById('ai-sync-btn').addEventListener('click', (e) => {
            const btn = e.currentTarget;

            const completedTimeline = appState.timeline.filter(t => t.completed).map(t => t.title);
            const missedTimeline = appState.timeline.filter(t => !t.completed).map(t => t.title);

            const syncString = `[AI SYNC] Mode: ${appState.activeMode}. ` +
                `Timeline ${document.getElementById('timeline-progress-text').textContent} done. ` +
                `Missed: ${missedTimeline.length ? missedTimeline.join(', ') : 'None'}. ` +
                `Please adjust my schedule for tomorrow based on this.`;

            navigator.clipboard.writeText(syncString).then(() => {
                const originalText = btn.innerHTML;
                btn.innerHTML = `<span class="icon">✅</span> Copied to Clipboard`;
                btn.style.color = '#10B981';
                btn.style.borderColor = '#10B981';

                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.color = '';
                    btn.style.borderColor = '';
                }, 3000);
            });
        });
    }

});
