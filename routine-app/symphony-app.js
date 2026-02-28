document.addEventListener('DOMContentLoaded', () => {
    // --- Accordion Toggle via Event Delegation ---
    // Placed at the very top of DOMContentLoaded to ensure registration
    // even if subsequent initialization functions fail silently.
    document.body.addEventListener('click', (e) => {
        // Bio Tab Accordion
        const bioHeader = e.target.closest('.bio-accordion-header');
        if (bioHeader) {
            const targetId = bioHeader.getAttribute('data-bio-panel');
            if (!targetId) return;
            const body = document.getElementById(targetId);
            const toggle = bioHeader.querySelector('.bio-toggle');
            if (!body || !toggle) return;

            const isOpen = bioHeader.classList.contains('expanded');
            if (isOpen) {
                body.style.display = 'none';
                bioHeader.classList.remove('expanded');
                toggle.textContent = '►';
            } else {
                body.style.display = 'block';
                bioHeader.classList.add('expanded');
                toggle.textContent = '▼';
            }
            return;
        }

        // Supplement Timing Sub-Accordion
        const suppHeader = e.target.closest('.supp-timing-header');
        if (suppHeader) {
            const targetId = suppHeader.getAttribute('data-supp-body');
            if (!targetId) return;
            const body = document.getElementById(targetId);
            const toggle = suppHeader.querySelector('.supp-toggle');
            if (!body || !toggle) return;

            const isOpen = suppHeader.classList.contains('expanded');
            if (isOpen) {
                body.style.display = 'none';
                suppHeader.classList.remove('expanded');
                toggle.textContent = '►';
            } else {
                body.style.display = 'block';
                suppHeader.classList.add('expanded');
                toggle.textContent = '▼';
            }
            return;
        }
    });

    // --- Supabase Global Configuration ---
    const SUPABASE_URL = "https://ezvptctdfcddoybownml.supabase.co";
    const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6dnB0Y3RkZmNkZG95Ym93bm1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NDgzNzAsImV4cCI6MjA4NzMyNDM3MH0.u_t44hY_YCwwtbWCIrQKf7EnUZDrja1q4zUFT0MXNOs";

    // Auth & Lock Screen Logic
    const CORRECT_PASSWORD = "quinn15405";
    const lockScreen = document.getElementById('lock-screen');
    const appContent = document.getElementById('app-content');
    const passwordInput = document.getElementById('password-input');
    const unlockBtn = document.getElementById('unlock-btn');
    const passwordError = document.getElementById('password-error');

    function checkAuth() {
        if (localStorage.getItem('symphony_auth') === 'true') {
            lockScreen.style.display = 'none';
            appContent.style.display = 'flex';
        } else {
            lockScreen.style.display = 'flex';
            appContent.style.display = 'none';
        }
    }

    // --- Financial Calculations (NZ) ---
    // Helper: compute NZ net income for a given weekly gross
    function computeNZNetWeekly(grossWeekly) {
        const kiwiSaverRate = 0.03;
        const annualizedGross = grossWeekly * 52;

        // KiwiSaver
        const weeklyKiwiSaver = grossWeekly * kiwiSaverRate;

        // Student Loan (12% over $438/week threshold)
        const slThreshold = 438.00;
        let weeklyStudentLoan = 0;
        if (grossWeekly > slThreshold) {
            weeklyStudentLoan = (grossWeekly - slThreshold) * 0.12;
        }

        // PAYE Tax (M Tax Code)
        let annualizedTax = 0;
        if (annualizedGross <= 15600) {
            annualizedTax = annualizedGross * 0.105;
        } else if (annualizedGross <= 53500) {
            annualizedTax = (15600 * 0.105) + ((annualizedGross - 15600) * 0.175);
        } else if (annualizedGross <= 78100) {
            annualizedTax = (15600 * 0.105) + ((53500 - 15600) * 0.175) + ((annualizedGross - 53500) * 0.30);
        } else {
            annualizedTax = (15600 * 0.105) + ((53500 - 15600) * 0.175) + ((78100 - 53500) * 0.30) + ((annualizedGross - 78100) * 0.33);
        }

        const accLevy = annualizedGross * 0.0139;
        const weeklyPayeAndAcc = (annualizedTax + accLevy) / 52;

        const totalDeductions = weeklyPayeAndAcc + weeklyStudentLoan + weeklyKiwiSaver;
        const netWeekly = grossWeekly - totalDeductions;

        return { netWeekly, weeklyPayeAndAcc, weeklyStudentLoan, weeklyKiwiSaver, annualizedGross };
    }

    // Global reference so budget builder can use it
    window.currentNetWeekly = 0;

    function calculateFinance() {
        // User Variables
        const baseHourlyRate = 24.00;

        const hoursInput = document.getElementById('input-hours');
        const holidayInput = document.getElementById('input-holiday');

        const hoursWorked = hoursInput ? parseFloat(hoursInput.value) || 0 : 28.5;
        const isHoliday = holidayInput ? holidayInput.classList.contains('checked') : false;

        const hourlyRate = isHoliday ? baseHourlyRate * 1.5 : baseHourlyRate;

        // Base Calculations
        const grossWeekly = hourlyRate * hoursWorked;
        const result = computeNZNetWeekly(grossWeekly);

        const formatCurrency = (num) => '$' + num.toFixed(2);
        const formatCurrencyRound = (num) => '$' + Math.round(num).toLocaleString();

        // Update existing DOM elements
        document.getElementById('finance-hours').innerText = hoursWorked + ' hrs';
        document.getElementById('finance-gross').innerText = formatCurrency(grossWeekly);
        document.getElementById('finance-tax').innerText = '-' + formatCurrency(result.weeklyPayeAndAcc);
        document.getElementById('finance-sl').innerText = '-' + formatCurrency(result.weeklyStudentLoan);
        document.getElementById('finance-ks').innerText = '-' + formatCurrency(result.weeklyKiwiSaver);
        document.getElementById('finance-net-pay').innerText = formatCurrency(result.netWeekly);

        // Store for budget summary
        window.currentNetWeekly = result.netWeekly;

        // --- Yearly Income Projection ---
        // Baseline: 28.5h/wk at $24/hr (non-holiday)
        const baselineGrossWeekly = 24.00 * 28.5;
        const baseline = computeNZNetWeekly(baselineGrossWeekly);
        const baselineAnnualNet = baseline.netWeekly * 52;

        // Current: at whatever hours/rate they entered
        const currentAnnualNet = result.netWeekly * 52;

        const yearlyBaseGrossEl = document.getElementById('finance-yearly-baseline-gross');
        const yearlyBaseNetEl = document.getElementById('finance-yearly-baseline-net');
        const yearlyCurrentGrossEl = document.getElementById('finance-yearly-current-gross');
        const yearlyCurrentNetEl = document.getElementById('finance-yearly-current-net');
        const yearlyDiffEl = document.getElementById('finance-yearly-diff');

        if (yearlyBaseGrossEl) yearlyBaseGrossEl.innerText = formatCurrencyRound(baselineGrossWeekly * 52);
        if (yearlyBaseNetEl) yearlyBaseNetEl.innerText = formatCurrencyRound(baselineAnnualNet);
        if (yearlyCurrentGrossEl) yearlyCurrentGrossEl.innerText = formatCurrencyRound(grossWeekly * 52);
        if (yearlyCurrentNetEl) yearlyCurrentNetEl.innerText = formatCurrencyRound(currentAnnualNet);

        if (yearlyDiffEl) {
            const diff = currentAnnualNet - baselineAnnualNet;
            if (Math.abs(diff) < 1) {
                yearlyDiffEl.innerText = 'At baseline hours';
            } else if (diff > 0) {
                yearlyDiffEl.innerHTML = `<span style="color: var(--accent-green);">+${formatCurrencyRound(diff)}/yr</span> above baseline`;
            } else {
                yearlyDiffEl.innerHTML = `<span style="color: var(--accent-red);">${formatCurrencyRound(diff)}/yr</span> below baseline`;
            }
        }

        // Update budget summary if expenses are loaded
        if (typeof window.updateBudgetSummary === 'function') {
            window.updateBudgetSummary();
        }

        // Initialize/Update Pie Chart
        const ctx = document.getElementById('financePieChart').getContext('2d');
        if (window.financeChartInstance) {
            window.financeChartInstance.destroy();
        }

        window.financeChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Net Pay', 'PAYE & ACC', 'Student Loan', 'KiwiSaver (3%)'],
                datasets: [{
                    data: [result.netWeekly, result.weeklyPayeAndAcc, result.weeklyStudentLoan, result.weeklyKiwiSaver],
                    backgroundColor: [
                        'rgba(52, 211, 153, 0.8)', // Green (Net)
                        'rgba(239, 68, 68, 0.8)',  // Red (Tax)
                        'rgba(245, 158, 11, 0.8)', // Orange (SL)
                        'rgba(56, 189, 248, 0.8)'  // Blue (KS)
                    ],
                    borderColor: 'rgba(15, 23, 42, 1)',
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#94a3b8',
                            font: { size: 11 }
                        }
                    }
                },
                cutout: '65%'
            }
        });
    }

    calculateFinance();

    const hoursInput = document.getElementById('input-hours');
    if (hoursInput) {
        hoursInput.addEventListener('input', calculateFinance);
    }

    const holidayInput = document.getElementById('input-holiday');
    if (holidayInput) {
        holidayInput.addEventListener('click', () => {
            holidayInput.classList.toggle('checked');
            calculateFinance();
        });
    }

    unlockBtn.addEventListener('click', () => {
        if (passwordInput.value === CORRECT_PASSWORD) {
            localStorage.setItem('symphony_auth', 'true');
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

    // --- Tab Navigation Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    function activateTab(tabId) {
        const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
        if (!targetBtn) return;

        // Remove active style from all tabs and hide all contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => {
            c.classList.remove('active');
            c.style.display = 'none';
        });

        // Add active style to the matched tab
        targetBtn.classList.add('active');

        // Show target content
        const targetContent = document.getElementById(tabId);
        if (targetContent) {
            targetContent.classList.add('active');
            targetContent.style.display = 'block';
        }
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            activateTab(targetId);
            localStorage.setItem('symphony_active_tab', targetId);
        });
    });

    // Persist active tab across refreshes
    const savedTab = localStorage.getItem('symphony_active_tab') || 'today';
    activateTab(savedTab);

    // Explicitly hide non-active tabs on load to be safe
    tabContents.forEach(c => {
        if (!c.classList.contains('active')) {
            c.style.display = 'none';
        }
    });

    // --- Quick Add Logic ---
    const quickAddInput = document.getElementById('quick-add-input');
    const quickAddBtn = document.getElementById('quick-add-btn');
    const quickAddCategory = document.getElementById('quick-add-category');
    const quickAddPriority = document.getElementById('quick-add-priority');

    async function handleQuickAdd() {
        const title = quickAddInput.value.trim();
        if (!title) return;

        const category = quickAddCategory ? quickAddCategory.value : 'Unscheduled';
        const priorityColor = quickAddPriority ? quickAddPriority.value : 'ORANGE';

        quickAddBtn.innerText = "⏳";
        quickAddBtn.style.pointerEvents = "none";

        const newTask = {
            title: title,
            points: 2,
            priority_color: priorityColor,
            time_target: category,
            is_active: true
        };

        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify([newTask])
            });

            if (response.ok) {
                quickAddInput.value = '';
                await fetchTasksAndRenderTimeline();
            } else {
                console.error("Failed to add quick task:", response.statusText);
                alert("Failed to add task.");
            }
        } catch (err) {
            console.error("Network error adding task:", err);
        } finally {
            quickAddBtn.innerText = "Add";
            quickAddBtn.style.pointerEvents = "auto";
        }
    }

    if (quickAddBtn) quickAddBtn.addEventListener('click', handleQuickAdd);
    if (quickAddInput) quickAddInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuickAdd();
    });

    // --- Pool Add Item Handlers (Weekly/Monthly/Backlog) ---
    function setupPoolAddButton(inputId, btnId, timeTarget) {
        const input = document.getElementById(inputId);
        const btn = document.getElementById(btnId);
        if (!input || !btn) return;

        async function addPoolItem() {
            const title = input.value.trim();
            if (!title) return;
            btn.innerText = '⏳';
            btn.style.pointerEvents = 'none';
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify([{ title, points: 2, priority_color: 'GREEN', time_target: timeTarget, is_active: true }])
                });
                if (response.ok) {
                    input.value = '';
                    await fetchTasksAndRenderTimeline();
                } else {
                    console.error('Failed to add pool item:', response.statusText);
                }
            } catch (err) {
                console.error('Network error adding pool item:', err);
            } finally {
                btn.innerText = '+';
                btn.style.pointerEvents = 'auto';
            }
        }

        btn.addEventListener('click', addPoolItem);
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') addPoolItem(); });
    }

    setupPoolAddButton('pool-week-input', 'pool-week-add-btn', 'Weekly');
    setupPoolAddButton('pool-longterm-input', 'pool-longterm-add-btn', 'Monthly');
    setupPoolAddButton('pool-future-input', 'pool-future-add-btn', 'Unscheduled');

    // Store our dynamically fetched tasks here
    let dynamicTasks = [];

    // Drag and Drop State
    let draggedTaskObj = null;

    // --- Dynamic Drag and Drop Logic ---
    async function fetchTasksAndRenderTimeline() {
        try {
            // First time UI setup
            setupDragAndDropZones();

            // Fetch ALL active tasks for the universal Task Pool
            const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true&select=*`, {
                method: 'GET',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                dynamicTasks = await response.json();
                renderDraggableTimeline();
            } else {
                console.error("Failed to fetch tasks list:", response.statusText);
            }
        } catch (error) {
            console.error("Network error fetching tasks:", error);
        }
    }

    function renderDraggableTimeline() {
        // Clear only task cards from drop zones, preserving add-item forms
        document.querySelectorAll('.drop-zone').forEach(zone => {
            zone.querySelectorAll('.draggable-task').forEach(t => t.remove());
        });

        // Categorization helper: determine which pool a task belongs to
        function getPoolId(task) {
            const tt = (task.time_target || '').trim();

            // Legacy fallback: remap "Evening" to a proper time slot
            if (tt === 'Evening') {
                task.time_target = '06:00 PM';
                return 'timeline';
            }

            // If it matches a specific time slot (e.g. "08:00 AM"), it goes on the timeline
            if (/^\d{2}:\d{2}\s*(AM|PM)$/i.test(tt)) return 'timeline';

            // If it matches a time range (e.g. "06:30 AM - 08:30 AM"), it also goes on the timeline
            if (/^\d{2}:\d{2}\s*(AM|PM)\s*-\s*\d{2}:\d{2}\s*(AM|PM)$/i.test(tt)) return 'timeline-span';

            // Daily tasks
            if (tt === 'Daily Flexible') return 'pool-today';

            // This week tasks
            if (tt === 'Weekly' || tt === 'Weekly (3x)' || tt === 'Moveable') return 'pool-week';

            // Long-term
            if (tt === 'Monthly') return 'pool-longterm';

            // Everything else (Unscheduled, empty, null, new quick-add tasks)
            return 'pool-future';
        }

        // Helper: parse "06:30 AM" into minutes since midnight for comparison
        function timeToMinutes(timeStr) {
            const match = timeStr.trim().match(/(\d{2}):(\d{2})\s*(AM|PM)/i);
            if (!match) return -1;
            let hours = parseInt(match[1]);
            const minutes = parseInt(match[2]);
            const period = match[3].toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            return hours * 60 + minutes;
        }

        // Helper: convert minutes since midnight back to "HH:MM AM/PM" format
        function minutesToTime(totalMins) {
            let h = Math.floor(totalMins / 60);
            const m = totalMins % 60;
            const period = h >= 12 ? 'PM' : 'AM';
            if (h > 12) h -= 12;
            if (h === 0) h = 12;
            return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')} ${period}`;
        }

        // Helper: get the start time and duration of a task from its time_target
        function parseTaskTiming(timeTarget) {
            const tt = (timeTarget || '').trim();
            const rangeMatch = tt.match(/^(\d{2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{2}:\d{2}\s*(?:AM|PM))$/i);
            if (rangeMatch) {
                const startMins = timeToMinutes(rangeMatch[1]);
                const endMins = timeToMinutes(rangeMatch[2]);
                return { startTime: rangeMatch[1].trim(), startMins, endMins, duration: endMins - startMins };
            }
            const singleMatch = tt.match(/^(\d{2}:\d{2}\s*(?:AM|PM))$/i);
            if (singleMatch) {
                const startMins = timeToMinutes(singleMatch[1]);
                return { startTime: singleMatch[1].trim(), startMins, endMins: startMins + 30, duration: 30 };
            }
            return null;
        }

        // Adjust task duration by delta minutes, update local state, persist, and re-render
        async function adjustTaskDuration(taskId, deltaMins) {
            const task = dynamicTasks.find(t => t.id === taskId);
            if (!task) return;
            const timing = parseTaskTiming(task.time_target);
            if (!timing) return;

            let newEndMins = timing.endMins + deltaMins;
            // Minimum duration: 15 minutes
            if (newEndMins - timing.startMins < 15) return;
            // Maximum: don't go past midnight (24:00 = 1440 mins)
            if (newEndMins > 1440) return;

            const newEndTime = minutesToTime(newEndMins);
            if (newEndMins - timing.startMins <= 30) {
                // Single slot — revert to simple format
                task.time_target = timing.startTime;
            } else {
                task.time_target = `${timing.startTime} - ${newEndTime}`;
            }
            renderDraggableTimeline();

            // Persist to Supabase
            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${taskId}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ time_target: task.time_target })
                });
            } catch (e) {
                console.warn('Failed to persist duration change:', e);
            }
        }

        // Track counts per section for badge display
        const counts = { 'pool-today': 0, 'pool-week': 0, 'pool-longterm': 0, 'pool-future': 0 };

        dynamicTasks.forEach(task => {
            // Create the draggable card
            const el = document.createElement('div');
            el.className = 'draggable-task';
            el.draggable = true;
            el.dataset.id = task.id;

            // Visual indicator for priority color
            let colorBorder = 'var(--glass-border)';
            if (task.priority_color === 'RED') colorBorder = 'var(--accent-red)';
            if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange)';
            if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green)';

            el.style.borderLeft = `3px solid ${colorBorder}`;

            const poolId = getPoolId(task);
            const isOnTimeline = (poolId === 'timeline' || poolId === 'timeline-span');
            const timing = isOnTimeline ? parseTaskTiming(task.time_target) : null;
            const durationLabel = timing ? `${timing.duration}m` : '';

            el.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="display: flex; align-items: flex-start; gap: 8px;">
                        ${isOnTimeline ? `<div class="checkbox completion-toggle" style="margin-top: 2px;" title="Mark Complete"></div>` : ''}
                        <div class="task-title" style="font-size: 0.95rem; font-weight: bold; transition: all 0.2s;">
                            ${task.title} <span style="font-size:0.8rem; color:var(--accent-blue); font-weight: normal;">[+${task.points} pts]</span>
                        </div>
                    </div>
                    <button class="task-delete-btn" data-task-id="${task.id}" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: red; font-weight: bold; font-size: 0.9rem; cursor: pointer; padding: 0 5px; line-height: 1.2;" title="Delete task">×</button>
                </div>
                ${task.description ? `<div class="task-desc" style="font-size: 0.8rem;">${task.description}</div>` : ''}
                <div style="margin-top: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.65rem; padding: 2px 6px;">${t}</span>`).join('')}
                    </div>
                    ${isOnTimeline ? `
                    <div class="duration-controls" style="display: flex; align-items: center; gap: 4px; font-size: 0.75rem;">
                        <button class="dur-minus" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: #000000; width: 24px; height: 24px; border-radius: 0; cursor: pointer; font-weight: bold; font-size: 1rem; line-height: 1; font-family: 'VT323', monospace;">−</button>
                        <span class="dur-label" style="color: #0000ff; font-weight: 600; min-width: 32px; text-align: center; font-family: 'VT323', monospace;">${durationLabel}</span>
                        <button class="dur-plus" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: #000000; width: 24px; height: 24px; border-radius: 0; cursor: pointer; font-weight: bold; font-size: 1rem; line-height: 1; font-family: 'VT323', monospace;">+</button>
                    </div>` : ''}
                </div>
            `;

            // Attach duration control listeners
            const durMinus = el.querySelector('.dur-minus');
            const durPlus = el.querySelector('.dur-plus');
            if (durMinus) durMinus.addEventListener('click', (e) => { e.stopPropagation(); adjustTaskDuration(task.id, -15); });
            if (durPlus) durPlus.addEventListener('click', (e) => { e.stopPropagation(); adjustTaskDuration(task.id, 15); });

            // Attach completion toggle
            const completeBtn = el.querySelector('.completion-toggle');
            if (completeBtn) {
                // Determine initial state
                let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                const lastDoneIso = lastDoneDates[task.id];
                const isCompletedToday = lastDoneIso && (new Date(lastDoneIso).toDateString() === new Date().toDateString());

                if (isCompletedToday) {
                    completeBtn.classList.add('checked');
                    el.querySelector('.task-title').style.opacity = '0.5';
                    el.querySelector('.task-title').style.textDecoration = 'line-through';
                }

                completeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    completeBtn.classList.toggle('checked');
                    const isChecked = completeBtn.classList.contains('checked');

                    const titleEl = el.querySelector('.task-title');
                    if (isChecked) {
                        titleEl.style.opacity = '0.5';
                        titleEl.style.textDecoration = 'line-through';
                        // Save last done date
                        lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        lastDoneDates[task.id] = new Date().toISOString();
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        // Re-render trackers
                        renderWeeklyMonthlyTracker();
                    } else {
                        titleEl.style.opacity = '1';
                        titleEl.style.textDecoration = 'none';
                        // Remove last done date if un-toggled (optional, but good for correcting mistakes)
                        lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        delete lastDoneDates[task.id];
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        renderWeeklyMonthlyTracker();
                    }
                });
            }

            // Attach delete handler
            const deleteBtn = el.querySelector('.task-delete-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (!confirm(`Delete "${task.title}"?`)) return;
                    deleteBtn.innerText = "⏳";
                    try {
                        const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${task.id}`, {
                            method: 'DELETE',
                            headers: {
                                'apikey': SUPABASE_ANON_KEY,
                                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                            }
                        });

                        if (response.ok || response.status === 204) {
                            dynamicTasks = dynamicTasks.filter(t => t.id !== task.id);
                            renderDraggableTimeline();
                        } else {
                            console.error("Failed to delete task", response.statusText);
                            alert("Failed to delete task");
                            deleteBtn.innerText = "×";
                        }
                    } catch (err) {
                        console.error("Network error deleting task:", err);
                        alert("Network error. Try again.");
                        deleteBtn.innerText = "×";
                    }
                });
            }

            // Attach drag events
            el.addEventListener('dragstart', (e) => {
                el.classList.add('dragging');
                draggedTaskObj = task;
                e.dataTransfer.setData('text/plain', task.id);
            });

            el.addEventListener('dragend', () => {
                el.classList.remove('dragging');
                draggedTaskObj = null;
            });


            // Route to the correct container (using poolId cached above)

            if (poolId === 'timeline') {
                const targetZone = document.querySelector(`.drop-zone[data-time="${task.time_target}"]`);
                if (targetZone) {
                    targetZone.appendChild(el);
                } else {
                    // Fallback: time slot doesn't exist on the timeline, put in Today
                    const fallback = document.getElementById('pool-today');
                    if (fallback) fallback.appendChild(el);
                    counts['pool-today']++;
                }
            } else if (poolId === 'timeline-span') {
                // Multi-hour task: parse start and end, span across slots
                const parts = task.time_target.split('-').map(s => s.trim());
                const startTime = parts[0];
                const endTime = parts[1];
                const startMinutes = timeToMinutes(startTime);
                const endMinutes = timeToMinutes(endTime);

                const startSlot = document.querySelector(`.time-slot[data-time="${startTime}"]`);
                const timelineContainer = document.getElementById('today-timeline');
                if (startSlot && timelineContainer) {
                    const allSlots = Array.from(document.querySelectorAll('.time-slot'));
                    const startIdx = allSlots.findIndex(s => s.dataset.time === startTime);
                    let endIdx = allSlots.findIndex(s => timeToMinutes(s.dataset.time) >= endMinutes);
                    if (endIdx === -1) endIdx = allSlots.length;

                    for (let i = startIdx; i < endIdx && i < allSlots.length; i++) {
                        const zone = allSlots[i].querySelector('.drop-zone');
                        if (zone) {
                            zone.style.background = 'rgba(56, 189, 248, 0.05)';
                            zone.style.borderColor = 'rgba(56, 189, 248, 0.2)';
                        }
                    }

                    timelineContainer.style.position = 'relative';

                    const rangeBadge = document.createElement('div');
                    rangeBadge.style.cssText = 'font-size: 0.7rem; color: var(--accent-blue); margin-top: 4px;';
                    rangeBadge.textContent = startTime + ' \u2192 ' + endTime;
                    el.appendChild(rangeBadge);

                    timelineContainer.appendChild(el);

                    requestAnimationFrame(() => {
                        const timelineRect = timelineContainer.getBoundingClientRect();
                        const startRect = startSlot.getBoundingClientRect();
                        const lastSlotIdx = Math.min(endIdx - 1, allSlots.length - 1);
                        const endSlotRect = allSlots[lastSlotIdx].getBoundingClientRect();
                        const topOffset = startRect.top - timelineRect.top;
                        const spanHeight = endSlotRect.bottom - startRect.top;
                        el.style.position = 'absolute';
                        el.style.top = topOffset + 'px';
                        el.style.left = '85px';
                        el.style.right = '0';
                        el.style.height = spanHeight + 'px';
                        el.style.zIndex = '5';
                        el.style.background = 'rgba(56, 189, 248, 0.12)';
                        el.style.border = '2px solid rgba(56, 189, 248, 0.4)';
                        el.style.borderRadius = '6px';
                        el.style.padding = '0.5rem';
                        el.style.boxSizing = 'border-box';
                        el.style.backdropFilter = 'blur(4px)';
                    });
                } else {
                    const fallback = document.getElementById('pool-today');
                    if (fallback) fallback.appendChild(el);
                    counts['pool-today']++;
                }
            } else {
                const container = document.getElementById(poolId);
                if (container) container.appendChild(el);
                if (counts[poolId] !== undefined) counts[poolId]++;
            }
        });

        // Update section headers with task counts
        document.querySelectorAll('.pool-accordion-header').forEach(header => {
            const poolId = header.getAttribute('data-pool');
            const count = counts[poolId];
            if (count !== undefined) {
                const label = header.querySelector('span:first-child');
                // Add count badge
                const existingBadge = header.querySelector('.pool-count');
                if (existingBadge) existingBadge.remove();
                const badge = document.createElement('span');
                badge.className = 'pool-count';
                badge.textContent = ` (${count})`;
                label.appendChild(badge);
            }
        });

        // Progress update
        document.getElementById('today-progress').style.width = '0%';

        // Highlight current time slot and auto-scroll to it
        const now = new Date();
        const nowMins = now.getHours() * 60 + now.getMinutes();
        const allTimeSlots = document.querySelectorAll('.time-slot[data-time]');
        let closestSlot = null;
        allTimeSlots.forEach(slot => {
            slot.classList.remove('current-time');
            const slotTime = slot.dataset.time;
            const slotMins = timeToMinutes(slotTime);
            if (slotMins >= 0 && slotMins <= nowMins) {
                closestSlot = slot;
            }
        });
        if (closestSlot) {
            closestSlot.classList.add('current-time');
            // Auto-scroll to current time (only on initial load)
            if (!window._timelineScrolled) {
                window._timelineScrolled = true;
                setTimeout(() => closestSlot.scrollIntoView({ behavior: 'smooth', block: 'center' }), 300);
            }
        }

        // Render Weekly/Monthly Tracker immediately after timeline is built
        renderWeeklyMonthlyTracker();

        // Setup drag-and-drop after rendering
        setupDragAndDropZones();
    }

    function setupDragAndDropZones() {
        const dropZones = document.querySelectorAll('.drop-zone');

        dropZones.forEach(zone => {
            // Skip zones that already have drag handlers (prevents stacking)
            if (zone.dataset.dragReady) return;
            zone.dataset.dragReady = 'true';

            zone.addEventListener('dragover', e => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', e => {
                e.preventDefault();
                zone.classList.remove('drag-over');

                const draggingEl = document.querySelector('.dragging');
                if (draggingEl && draggedTaskObj) {
                    draggedTaskObj.time_target = zone.dataset.time;
                    // Defer re-render to avoid conflicts during drag event
                    setTimeout(() => renderDraggableTimeline(), 0);
                }
            });
        });

        // Setup the "Lock In Schedule" Button
        const lockBtn = document.getElementById('lock-in-btn');
        if (lockBtn) {
            // Remove old listeners by cloning
            const newBtn = lockBtn.cloneNode(true);
            lockBtn.parentNode.replaceChild(newBtn, lockBtn);
            newBtn.addEventListener('click', lockInSchedule);
        }
    }

    async function lockInSchedule() {
        const lockBtn = document.getElementById('lock-in-btn');
        const originalText = lockBtn.innerText;
        lockBtn.innerText = '\u23f3 Syncing...';
        lockBtn.style.opacity = '0.7';
        lockBtn.style.pointerEvents = 'none';

        try {
            const updates = dynamicTasks.map(t => ({
                id: t.id,
                time_target: t.time_target
            }));

            const patchPromises = updates.map(update => {
                return fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${update.id}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ time_target: update.time_target })
                });
            });

            const responses = await Promise.all(patchPromises);
            const allOk = responses.every(r => r.ok);

            if (allOk) {
                lockBtn.innerText = '\u2705 Locked In';
                lockBtn.style.background = 'var(--glass-bg)';
                lockBtn.style.color = 'var(--accent-green)';
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
                setTimeout(() => {
                    lockBtn.innerText = originalText;
                    lockBtn.style.background = 'var(--accent-green)';
                    lockBtn.style.color = '#000';
                    lockBtn.style.opacity = '1';
                    lockBtn.style.pointerEvents = 'auto';
                }, 3000);
            } else {
                console.error('Failed to commit schedule bulk update');
                lockBtn.innerText = '\u274c Sync Failed';
                if (typeof playRetroError === 'function') playRetroError();
            }
        } catch (error) {
            console.error('Network error locking in schedule:', error);
            lockBtn.innerText = '\u274c Network Error';
            if (typeof playRetroError === 'function') playRetroError();
        }
    }

    function renderWeeklyMonthlyTracker() {
        const weeklyList = document.getElementById('weekly-list');
        const monthlyList = document.getElementById('monthly-list');
        if (!weeklyList || !monthlyList) return;

        weeklyList.innerHTML = '';
        monthlyList.innerHTML = '';

        const lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');

        // Helper to format dates cleanly
        const formatDate = (isoStr) => {
            if (!isoStr) return 'Never';
            const d = new Date(isoStr);
            return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }); // e.g., 25 Mar
        };

        // Filter for tracking tasks
        const trackingTasks = dynamicTasks.filter(t => {
            const tt = (t.time_target || '').trim();
            return ['Weekly', 'Weekly (3x)', 'Monthly'].includes(tt);
        });

        trackingTasks.forEach(task => {
            const tt = (task.time_target || '').trim();
            const lastDone = formatDate(lastDoneDates[task.id]);

            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.alignItems = 'center';
            li.innerHTML = `
                <div class="task-content">
                    <strong>${task.title}</strong>
                    ${task.tags ? `<br><span class="tag" style="font-size:0.65rem;">${task.tags.join(', ')}</span>` : ''}
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; border: 1px solid var(--glass-border);">
                    <span style="color: var(--text-secondary);">Last Done:</span> <span style="font-weight:bold; color: var(--accent-green);">${lastDone}</span>
                </div>
            `;

            if (tt === 'Monthly') {
                monthlyList.appendChild(li);
            } else {
                weeklyList.appendChild(li);
            }
        });

        // If nothing was found, put a placeholder
        if (weeklyList.innerHTML === '') weeklyList.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No weekly tasks found.</li>';
        if (monthlyList.innerHTML === '') monthlyList.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No monthly tasks found.</li>';
    }

    // --- Accordion Toggle Logic ---
    document.querySelectorAll('.pool-accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const poolId = header.getAttribute('data-pool');
            const body = document.getElementById(poolId);
            const toggle = header.querySelector('.pool-toggle');

            if (body.style.display === 'none') {
                body.style.display = 'block';
                header.classList.add('expanded');
                toggle.textContent = '▼';
            } else {
                body.style.display = 'none';
                header.classList.remove('expanded');
                toggle.textContent = '►';
            }
        });
    });

    function setupDragAndDropZones() {
        const dropZones = document.querySelectorAll('.drop-zone');

        dropZones.forEach(zone => {
            zone.addEventListener('dragover', e => {
                e.preventDefault(); // allow dropping
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', e => {
                e.preventDefault();
                zone.classList.remove('drag-over');

                const draggingEl = document.querySelector('.dragging');
                if (draggingEl && draggedTaskObj) {
                    // Visually move the element
                    zone.appendChild(draggingEl);

                    // Update the local object state to match the new zone
                    draggedTaskObj.time_target = zone.dataset.time;
                }
            });
        });

        // Setup the "Lock In Schedule" Button
        const lockBtn = document.getElementById('lock-in-btn');
        if (lockBtn) {
            lockBtn.addEventListener('click', lockInSchedule);
        }
    }

    async function lockInSchedule() {
        const lockBtn = document.getElementById('lock-in-btn');
        const originalText = lockBtn.innerText;
        lockBtn.innerText = "⏳ Syncing...";
        lockBtn.style.opacity = '0.7';
        lockBtn.style.pointerEvents = 'none';

        try {
            // Create a payload of all tasks and their current `time_target` from the local array
            const updates = dynamicTasks.map(t => ({
                id: t.id,
                time_target: t.time_target
            }));

            // Supabase REST Bulk Upsert often fails if we don't pass the complete row data to satisfy NOT NULL constraints
            // (even with merge-duplicates) because it evaluates the insert payload first.
            // Using a Promise.all of individual PATCH requests is safest since we're only updating 5-10 items max.

            const patchPromises = updates.map(update => {
                return fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${update.id}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ time_target: update.time_target })
                });
            });

            const responses = await Promise.all(patchPromises);

            // Check if any failed
            const allOk = responses.every(r => r.ok);

            if (allOk) {
                lockBtn.innerText = "✅ Locked In";
                lockBtn.style.background = "var(--glass-bg)";
                lockBtn.style.color = "var(--accent-green)";
                setTimeout(() => {
                    lockBtn.innerText = originalText;
                    lockBtn.style.background = "var(--accent-green)";
                    lockBtn.style.color = "#000";
                    lockBtn.style.opacity = '1';
                    lockBtn.style.pointerEvents = 'auto';
                }, 3000);
            } else {
                console.error("Failed to commit schedule bulk update:", await response.text());
                lockBtn.innerText = "❌ Sync Failed";
            }
        } catch (error) {
            console.error("Network error locking in schedule:", error);
            lockBtn.innerText = "❌ Network Error";
        }
    }

    // Populate Lists
    const createListItems = (items, containerId) => {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        // Load list state
        const savedListState = JSON.parse(localStorage.getItem('symphony_list_state_' + containerId) || '{}');

        items.forEach((itemObj, index) => {
            // Handle both simple strings and objects with points/sync data
            const text = typeof itemObj === 'string' ? itemObj : itemObj.text;
            const pointsLabel = (typeof itemObj === 'object' && itemObj.points) ? ` <span style="font-size:0.8rem; color:var(--accent-blue);">[+${itemObj.points} pts]</span>` : '';

            const suppSyncAttr = (typeof itemObj === 'object' && itemObj.suppSync) ? `data-supp-sync="${itemObj.suppSync}" data-supp-dose="${itemObj.suppDose || 1}"` : '';

            const li = document.createElement('li');
            const isCompleted = savedListState[index];

            if (isCompleted) {
                li.classList.add('completed');
            }

            li.innerHTML = `
                <div class="checkbox ${isCompleted ? 'checked' : ''}" ${suppSyncAttr}></div>
                <div class="task-content">${text}${pointsLabel}</div>
            `;

            li.querySelector('.checkbox').addEventListener('click', function () {
                const wasChecked = this.classList.contains('checked');
                this.classList.toggle('checked');
                const isNowChecked = this.classList.contains('checked');

                const parent = this.parentElement;
                parent.classList.toggle('completed');

                // Save state
                savedListState[index] = isNowChecked;
                localStorage.setItem('symphony_list_state_' + containerId, JSON.stringify(savedListState));

                if (containerId === 'daily-list') updatePoints();

                // Trigger Supplement Sync if newly checked
                if (!wasChecked && isNowChecked && window.triggerSuppSync) {
                    const syncName = this.getAttribute('data-supp-sync');
                    const syncDose = parseInt(this.getAttribute('data-supp-dose')) || 1;
                    if (syncName) {
                        window.triggerSuppSync(syncName, syncDose);
                    }
                }
            });

            container.appendChild(li);
        });
    };

    // --- Ideas / Bucket List Setup (Supabase-backed) ---
    async function initIdeasPage() {
        const attachListListener = (inputId, btnId, listId, listType) => {
            const input = document.getElementById(inputId);
            const btn = document.getElementById(btnId);
            const list = document.getElementById(listId);
            const LOCAL_KEY = `symphony_ideas_${listType}`;

            if (!input || !btn || !list) return;

            let items = []; // [{id, text, completed, sort_order}]

            // Fetch from Supabase, fallback to localStorage (safe: won't clobber local data)
            async function fetchItems() {
                try {
                    const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_ideas?list_type=eq.${listType}&order=sort_order.asc,created_at.asc`, {
                        headers: {
                            'apikey': SUPABASE_ANON_KEY,
                            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                        }
                    });
                    if (resp.ok) {
                        const supabaseData = await resp.json();
                        const localData = localStorage.getItem(LOCAL_KEY);
                        const localItems = localData ? JSON.parse(localData) : [];
                        if (supabaseData.length > 0) {
                            items = supabaseData;
                            localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        } else if (localItems.length > 0) {
                            items = localItems;
                            console.info(`Ideas (${listType}): Supabase empty, keeping local data`);
                        } else {
                            items = [];
                        }
                    } else {
                        throw new Error(`HTTP ${resp.status}`);
                    }
                } catch (e) {
                    console.warn(`Ideas (${listType}): Supabase fetch failed, using localStorage:`, e);
                    const local = localStorage.getItem(LOCAL_KEY);
                    if (local) items = JSON.parse(local);
                }
            }

            function renderItems() {
                list.innerHTML = '';
                if (items.length === 0) {
                    list.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No items yet — add one above!</li>';
                    return;
                }
                items.forEach((item, index) => {
                    const li = document.createElement('li');
                    if (item.completed) li.classList.add('completed');

                    li.innerHTML = `
                        <div class="checkbox ${item.completed ? 'checked' : ''}"></div>
                        <div class="task-content" style="flex-grow: 1;">${item.text}</div>
                        <button class="delete-btn" data-index="${index}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.2rem; margin-left: 10px;" title="Delete item">×</button>
                    `;

                    li.querySelector('.checkbox').addEventListener('click', async function () {
                        this.classList.toggle('checked');
                        this.parentElement.classList.toggle('completed');
                        items[index].completed = !items[index].completed;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        // Sync to Supabase
                        if (items[index].id) {
                            try {
                                await fetch(`${SUPABASE_URL}/rest/v1/symphony_ideas?id=eq.${items[index].id}`, {
                                    method: 'PATCH',
                                    headers: {
                                        'apikey': SUPABASE_ANON_KEY,
                                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                                        'Content-Type': 'application/json',
                                        'Prefer': 'return=minimal'
                                    },
                                    body: JSON.stringify({ completed: items[index].completed, updated_at: new Date().toISOString() })
                                });
                            } catch (e) { console.warn('Failed to sync checkbox to Supabase:', e); }
                        }
                    });

                    li.querySelector('.delete-btn').addEventListener('click', async function () {
                        const removedItem = items.splice(index, 1)[0];
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        renderItems();
                        // Delete from Supabase
                        if (removedItem && removedItem.id) {
                            try {
                                await fetch(`${SUPABASE_URL}/rest/v1/symphony_ideas?id=eq.${removedItem.id}`, {
                                    method: 'DELETE',
                                    headers: {
                                        'apikey': SUPABASE_ANON_KEY,
                                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                                    }
                                });
                            } catch (e) { console.warn('Failed to delete from Supabase:', e); }
                        }
                    });

                    list.appendChild(li);
                });
            }

            async function handleAdd() {
                const text = input.value.trim();
                if (!text) return;

                const newItem = {
                    list_type: listType,
                    text: text,
                    completed: false,
                    sort_order: items.length
                };

                // Optimistic local add
                items.push(newItem);
                localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                renderItems();
                input.value = '';

                // Persist to Supabase
                try {
                    const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_ideas`, {
                        method: 'POST',
                        headers: {
                            'apikey': SUPABASE_ANON_KEY,
                            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify(newItem)
                    });
                    if (resp.ok) {
                        // Re-fetch to get the real ID from Supabase
                        await fetchItems();
                        renderItems();
                    }
                } catch (e) {
                    console.warn('Failed to save idea to Supabase:', e);
                }

                if (typeof playRetroClick === 'function') playRetroClick();
            }

            btn.addEventListener('click', handleAdd);
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleAdd();
            });

            // Initialize: fetch and render
            return fetchItems().then(() => {
                // Seed bucket list default if completely empty (first use)
                if (items.length === 0 && listType === 'bucket') {
                    items = [{ text: "Walk the full Pineapple Track", completed: false, sort_order: 0 }];
                }
                renderItems();
            });
        };

        await Promise.all([
            attachListListener('quick-add-bucket', 'quick-add-bucket-btn', 'bucket-list', 'bucket'),
            attachListListener('quick-add-braindump', 'quick-add-braindump-btn', 'braindump-list', 'braindump')
        ]);
    }

    initIdeasPage();

    // Populate Workout Grid
    const populateWorkout = () => {
        const grid = document.getElementById('workout-grid');
        grid.innerHTML = '';

        workoutPlan.forEach(workout => {
            const card = document.createElement('div');
            card.className = 'sub-panel workout-card';

            let exercisesHtml = workout.exercises.map(ex => `<li>${ex}</li>`).join('');

            card.innerHTML = `
                <h3>${workout.day}</h3>
                <div class="workout-focus">${workout.focus}</div>
                <ul class="workout-list">
                    ${exercisesHtml}
                </ul>
            `;
            grid.appendChild(card);
        });
    };

    // ── Local Time Helper ──
    function getLocalDayDateString(d = new Date()) {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const FOOD_LOG_KEY = `symphony_food_log_${getLocalDayDateString()}`;
    const FOOD_RECIPES_KEY = 'symphony_food_recipes';
    const FOOD_HISTORY_KEY = 'symphony_food_history'; // localStorage backup for chart data
    const MY_FOODS_KEY = 'symphony_my_foods'; // persistent food history + favorites

    // ── DNA-Personalized Targets ──
    // Based on: TCF7L2 C/T, KLF14 A/A, 9p21 G/G, ACTN3 C/T, ADRB2 G/G, CRP=9
    const DNA_TARGETS = {
        calories: { min: 1800, max: 2400, label: 'Calories (KLF14 tight margin)' },
        protein: { min: 120, max: 999, label: 'Protein (ACTN3 hybrid muscle)' },
        carbs: { min: 0, max: 150, label: 'Carbs (TCF7L2 pancreas limit)' },
        fats: { min: 0, max: 80, label: 'Fats (9p21 artery risk)' },
        fiber: { min: 25, max: 999, label: 'Fiber (Gut barrier / CRP=9)' },
        sugars: { min: 0, max: 30, label: 'Sugars (TCF7L2 + KLF14)' },
        sodium: { min: 0, max: 2.3, label: 'Sodium (< 2300mg)' }
    };

    // ── LocalStorage helpers ──
    function getDailyFoodLog() {
        const stored = localStorage.getItem(FOOD_LOG_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveFoodLog(logArr) {
        localStorage.setItem(FOOD_LOG_KEY, JSON.stringify(logArr));
    }
    function getRecipes() {
        const stored = localStorage.getItem(FOOD_RECIPES_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveRecipes(arr) {
        localStorage.setItem(FOOD_RECIPES_KEY, JSON.stringify(arr));
    }
    function getFoodHistory() {
        const stored = localStorage.getItem(FOOD_HISTORY_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveFoodHistory(arr) {
        localStorage.setItem(FOOD_HISTORY_KEY, JSON.stringify(arr));
    }
    function getMyFoods() {
        const stored = localStorage.getItem(MY_FOODS_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveMyFoods(arr) {
        localStorage.setItem(MY_FOODS_KEY, JSON.stringify(arr));
    }
    function addToMyFoods(food) {
        // food = selectedFood shape: { name, brand, per100g, servingSize, servingG, qtyLabel, qtyG }
        if (!food || !food.name) return;
        const myFoods = getMyFoods();
        const existing = myFoods.find(f => f.name === food.name && (f.brand || '') === (food.brand || ''));
        if (existing) {
            existing.useCount = (existing.useCount || 1) + 1;
            existing.lastUsed = new Date().toISOString();
        } else {
            myFoods.push({
                name: food.name,
                brand: food.brand || '',
                per100g: food.per100g,
                servingSize: food.servingSize,
                servingG: food.servingG,
                qtyLabel: food.qtyLabel || null,
                qtyG: food.qtyG || null,
                favorite: false,
                lastUsed: new Date().toISOString(),
                useCount: 1
            });
        }
        saveMyFoods(myFoods);
    }
    function toggleMyFoodFavorite(name, brand) {
        const myFoods = getMyFoods();
        const item = myFoods.find(f => f.name === name && (f.brand || '') === (brand || ''));
        if (item) {
            item.favorite = !item.favorite;
            saveMyFoods(myFoods);
        }
    }

    // ── Nutrient scaling ──
    function scaleNutrients(per100g, amountG) {
        const factor = amountG / 100;
        return {
            calories: Math.round((per100g.calories || 0) * factor),
            protein: Math.round((per100g.protein || 0) * factor * 10) / 10,
            carbs: Math.round((per100g.carbs || 0) * factor * 10) / 10,
            fats: Math.round((per100g.fats || 0) * factor * 10) / 10,
            sugars: Math.round((per100g.sugars || 0) * factor * 10) / 10,
            fiber: Math.round((per100g.fiber || 0) * factor * 10) / 10,
            sodium: Math.round((per100g.sodium || 0) * factor * 100) / 100
        };
    }

    function calculateDailyTotals(logArr) {
        return logArr.reduce((totals, item) => {
            totals.calories += item.calories || 0;
            totals.protein += item.protein || 0;
            totals.carbs += item.carbs || 0;
            totals.fats += item.fats || 0;
            totals.sugars += item.sugars || 0;
            totals.fiber += item.fiber || 0;
            totals.sodium += item.sodium || 0;
            return totals;
        }, { calories: 0, protein: 0, carbs: 0, fats: 0, sugars: 0, fiber: 0, sodium: 0 });
    }

    // ── DNA Grading Engine ──
    function gradeDailyIntake(totals) {
        let score = 100;
        const breakdown = [];

        const checks = [
            { key: 'calories', value: Math.round(totals.calories), unit: '' },
            { key: 'protein', value: Math.round(totals.protein * 10) / 10, unit: 'g' },
            { key: 'carbs', value: Math.round(totals.carbs * 10) / 10, unit: 'g' },
            { key: 'fats', value: Math.round(totals.fats * 10) / 10, unit: 'g' },
            { key: 'fiber', value: Math.round(totals.fiber * 10) / 10, unit: 'g' },
            { key: 'sugars', value: Math.round(totals.sugars * 10) / 10, unit: 'g' },
            { key: 'sodium', value: Math.round(totals.sodium * 100) / 100, unit: 'g' }
        ];

        checks.forEach(c => {
            const t = DNA_TARGETS[c.key];
            let status = 'pass';
            let penalty = 0;

            if (c.value < t.min) {
                const deficit = ((t.min - c.value) / t.min) * 100;
                penalty = Math.min(20, Math.round(deficit / 5) * 3);
                status = penalty > 10 ? 'fail' : 'warn';
            } else if (c.value > t.max) {
                const excess = ((c.value - t.max) / t.max) * 100;
                penalty = Math.min(25, Math.round(excess / 5) * 3);
                status = penalty > 10 ? 'fail' : 'warn';
            }

            score -= penalty;
            breakdown.push({
                label: t.label,
                value: `${c.value}${c.unit}`,
                target: c.key === 'protein' || c.key === 'fiber'
                    ? `≥ ${t.min}${c.unit}`
                    : c.key === 'calories'
                        ? `${t.min}-${t.max}`
                        : `≤ ${t.max}${c.unit}`,
                status,
                penalty
            });
        });

        score = Math.max(0, Math.min(100, score));

        let grade;
        if (score >= 95) grade = 'A+';
        else if (score >= 88) grade = 'A';
        else if (score >= 80) grade = 'B+';
        else if (score >= 72) grade = 'B';
        else if (score >= 64) grade = 'C+';
        else if (score >= 55) grade = 'C';
        else if (score >= 45) grade = 'D';
        else grade = 'F';

        return { grade, score, breakdown };
    }

    function gradeToNumber(grade) {
        const map = { 'A+': 5, 'A': 4.5, 'B+': 4, 'B': 3.5, 'C+': 3, 'C': 2.5, 'D': 1.5, 'F': 0.5 };
        return map[grade] || 0;
    }

    function getGradeColor(grade) {
        if (grade.startsWith('A')) return '#22c55e';
        if (grade.startsWith('B')) return '#38bdf8';
        if (grade.startsWith('C')) return '#fbbf24';
        if (grade === 'D') return '#f97316';
        return '#ef4444';
    }

    // ── Render Functions ──
    function renderFoodDashboard() {
        const log = getDailyFoodLog();
        const totals = calculateDailyTotals(log);

        // Dashboard tiles
        document.getElementById('food-dash-calories').innerText = Math.round(totals.calories);
        document.getElementById('food-dash-protein').innerText = `${Math.round(totals.protein)}g`;
        document.getElementById('food-dash-carbs').innerText = `${Math.round(totals.carbs)}g`;
        document.getElementById('food-dash-fats').innerText = `${Math.round(totals.fats)}g`;

        // Live DNA grade
        if (log.length > 0) {
            const result = gradeDailyIntake(totals);
            const badge = document.getElementById('food-grade-badge');
            const scoreEl = document.getElementById('food-grade-score');
            badge.innerText = result.grade;
            badge.style.color = getGradeColor(result.grade);
            badge.style.textShadow = `0 0 12px ${getGradeColor(result.grade)}50`;
            scoreEl.innerText = `${result.score}/100 points`;

            // Grade breakdown
            const breakdownEl = document.getElementById('food-grade-breakdown');
            if (breakdownEl) {
                breakdownEl.innerHTML = result.breakdown.map(b => {
                    const icon = b.status === 'pass' ? '✅' : b.status === 'warn' ? '⚠️' : '❌';
                    const color = b.status === 'pass' ? 'var(--accent-green)' : b.status === 'warn' ? 'var(--accent-yellow)' : 'var(--accent-red)';
                    return `<div style="display: flex; justify-content: space-between; padding: 0.25rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05);">
                        <span>${icon} ${b.label}</span>
                        <span style="color: ${color}; font-weight: 600;">${b.value} <span style="font-weight: 400; color: var(--text-secondary);">(${b.target})</span></span>
                    </div>`;
                }).join('');
            }
        }

        // Doughnut chart
        const canvas = document.getElementById('foodMacroChart');
        if (canvas && totals.protein + totals.carbs + totals.fats > 0) {
            const ctx = canvas.getContext('2d');
            if (window.foodChartInstance) window.foodChartInstance.destroy();
            window.foodChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Protein', 'Carbs', 'Fats'],
                    datasets: [{
                        data: [Math.round(totals.protein), Math.round(totals.carbs), Math.round(totals.fats)],
                        backgroundColor: ['rgba(56,189,248,0.8)', 'rgba(251,191,36,0.8)', 'rgba(239,68,68,0.8)'],
                        borderColor: 'rgba(15,23,42,1)',
                        borderWidth: 2,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    cutout: '65%'
                }
            });
        }

        // Food log list
        const listEl = document.getElementById('food-log-list');
        if (listEl) {
            listEl.innerHTML = '';
            if (log.length === 0) {
                listEl.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No food logged yet today</li>';
            }
            log.forEach((item, index) => {
                const li = document.createElement('li');
                li.style.flexDirection = 'column';
                li.style.alignItems = 'flex-start';
                li.innerHTML = `
                    <div style="display: flex; justify-content: space-between; width: 100%; cursor: pointer;" onclick="document.getElementById('food-details-${index}').style.display = document.getElementById('food-details-${index}').style.display === 'none' ? 'block' : 'none'">
                        <div>
                            <span style="font-size: 0.75rem; color: var(--text-secondary); margin-right: 0.5rem;">${item.timestamp}</span>
                            <strong style="color: var(--text-primary);">${item.name}</strong>
                            <span style="font-size: 0.7rem; color: var(--accent-blue);">${item.amount}${item.unit || 'g'}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">
                            ${item.calories} kcal | ${Math.round(item.protein)}P ${Math.round(item.carbs)}C ${Math.round(item.fats)}F
                        </div>
                    </div>
                    <div id="food-details-${index}" style="display: none; width: 100%; margin-top: 0.4rem; padding-top: 0.4rem; border-top: 1px dashed var(--glass-border); font-size: 0.75rem; color: var(--text-secondary);">
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.3rem;">
                            <span>Sugars: ${Math.round(item.sugars * 10) / 10}g</span>
                            <span>Fiber: ${Math.round(item.fiber * 10) / 10}g</span>
                            <span>Sodium: ${Math.round(item.sodium * 1000)}mg</span>
                        </div>
                        <button class="delete-food-btn" data-index="${index}" style="margin-top: 0.4rem; background: transparent; border: 1px solid var(--accent-red); color: var(--accent-red); padding: 2px 8px; border-radius: 4px; cursor: pointer; font-family: 'VT323', monospace;">Remove</button>
                    </div>
                `;
                listEl.appendChild(li);
            });

            document.querySelectorAll('.delete-food-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const idx = parseInt(e.target.getAttribute('data-index'));
                    let currentLog = getDailyFoodLog();
                    currentLog.splice(idx, 1);
                    saveFoodLog(currentLog);
                    renderFoodDashboard();
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });
        }
    }

    // ── Recipes rendering ──
    function renderRecipes() {
        const recipes = getRecipes();
        const list = document.getElementById('food-recipes-list');
        if (!list) return;
        list.innerHTML = '';
        if (recipes.length === 0) {
            list.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem; padding: 0.25rem 0;">No recipes saved yet</div>';
            return;
        }
        recipes.forEach((recipe, idx) => {
            const totals = calculateDailyTotals(recipe.items);
            const div = document.createElement('div');
            div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.8rem;';
            div.innerHTML = `
                <div>
                    <strong style="color: var(--text-primary);">${recipe.name}</strong>
                    <span style="color: var(--text-secondary);"> (${recipe.items.length} items, ${Math.round(totals.calories)} kcal)</span>
                </div>
                <div style="display: flex; gap: 0.3rem;">
                    <button class="log-recipe-btn" data-idx="${idx}" style="padding: 2px 6px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: var(--accent-green); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">Log</button>
                    <button class="delete-recipe-btn" data-idx="${idx}" style="padding: 2px 6px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: var(--accent-red); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">×</button>
                </div>
            `;
            list.appendChild(div);
        });

        // Log recipe handlers
        document.querySelectorAll('.log-recipe-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                const recipe = recipes[idx];
                const currentLog = getDailyFoodLog();
                recipe.items.forEach(item => {
                    currentLog.push({
                        ...item,
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                        fromRecipe: recipe.name
                    });
                });
                saveFoodLog(currentLog);
                renderFoodDashboard();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        });

        // Delete recipe handlers
        document.querySelectorAll('.delete-recipe-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                const allRecipes = getRecipes();
                allRecipes.splice(idx, 1);
                saveRecipes(allRecipes);
                renderRecipes();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        });
    }

    // ── Historical Charts ──
    function renderGradeChart(days = 14) {
        const history = getFoodHistory();
        const canvas = document.getElementById('gradeHistoryChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        // Get last N days
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        const filtered = history.filter(h => new Date(h.date) >= cutoff).sort((a, b) => new Date(a.date) - new Date(b.date));

        if (window.gradeChartInstance) window.gradeChartInstance.destroy();

        const labels = filtered.map(h => {
            const d = new Date(h.date);
            return `${d.getDate()}/${d.getMonth() + 1}`;
        });

        const scores = filtered.map(h => gradeToNumber(h.grade));
        const colors = filtered.map(h => getGradeColor(h.grade));

        window.gradeChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Grade',
                    data: scores,
                    borderColor: 'rgba(56,189,248,0.8)',
                    backgroundColor: 'rgba(56,189,248,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0, max: 5.5,
                        ticks: {
                            callback: v => {
                                const map = { 5: 'A+', 4.5: 'A', 4: 'B+', 3.5: 'B', 3: 'C+', 2.5: 'C', 1.5: 'D', 0.5: 'F' };
                                return map[v] || '';
                            },
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8', font: { size: 10 } },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const item = filtered[ctx.dataIndex];
                                return item ? `${item.grade} (${item.score}/100)` : '';
                            }
                        }
                    }
                }
            }
        });
    }

    function renderMacroHistoryChart() {
        const history = getFoodHistory();
        const canvas = document.getElementById('macroHistoryChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const sorted = history.sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-30);

        if (window.macroHistChartInstance) window.macroHistChartInstance.destroy();

        const labels = sorted.map(h => {
            const d = new Date(h.date);
            return `${d.getDate()}/${d.getMonth() + 1}`;
        });

        window.macroHistChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Protein', data: sorted.map(h => Math.round(h.totals?.protein || 0)), backgroundColor: 'rgba(56,189,248,0.7)' },
                    { label: 'Carbs', data: sorted.map(h => Math.round(h.totals?.carbs || 0)), backgroundColor: 'rgba(251,191,36,0.7)' },
                    { label: 'Fats', data: sorted.map(h => Math.round(h.totals?.fats || 0)), backgroundColor: 'rgba(239,68,68,0.7)' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                    y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } }
            }
        });
    }

    // ── Supabase sync helpers ──
    async function saveDayToSupabase(dateStr, items, totals, grade, score) {
        try {
            // First check if an entry exists for this date
            const getResp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_food_log?date=eq.${dateStr}&select=id`, {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                }
            });
            const existing = await getResp.json();

            if (existing && existing.length > 0) {
                // Update existing
                const id = existing[0].id;
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_food_log?id=eq.${id}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ items, totals, grade, grade_score: score })
                });
                return resp.ok;
            } else {
                // Insert new
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_food_log`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ date: dateStr, items, totals, grade, grade_score: score })
                });
                return resp.ok;
            }
        } catch (e) {
            console.error('Supabase food log save failed:', e);
            return false;
        }
    }

    async function fetchHistoryFromSupabase(days = 30) {
        try {
            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - days);
            const dateStr = getLocalDayDateString(cutoff);

            const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_food_log?date=gte.${dateStr}&select=date,grade,grade_score,totals&order=date.asc`, {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                }
            });
            if (resp.ok) {
                const data = await resp.json();
                // Sync to localStorage for offline
                const history = data.map(d => ({ date: d.date, grade: d.grade, score: d.grade_score, totals: d.totals }));
                saveFoodHistory(history);
                return history;
            }
        } catch (e) {
            console.error('Supabase history fetch failed, using localStorage:', e);
        }
        return getFoodHistory();
    }

    async function saveRecipeToSupabase(recipe) {
        try {
            const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_food_recipes`, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify(recipe)
            });
            return resp.ok;
        } catch (e) {
            console.error('Supabase recipe save failed:', e);
            return false;
        }
    }

    // ── My Foods panel render ──
    function renderMyFoods() {
        const favList = document.getElementById('my-foods-favorites-list');
        const recentList = document.getElementById('my-foods-recent-list');
        if (!favList || !recentList) return;

        const myFoods = getMyFoods();
        const favorites = myFoods.filter(f => f.favorite).sort((a, b) => (b.useCount || 0) - (a.useCount || 0));
        const recents = [...myFoods].sort((a, b) => new Date(b.lastUsed) - new Date(a.lastUsed)).slice(0, 20);

        function renderList(container, items, emptyMsg) {
            container.innerHTML = '';
            if (items.length === 0) {
                container.innerHTML = `<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem; padding: 0.25rem 0;">${emptyMsg}</div>`;
                return;
            }
            items.forEach(food => {
                const div = document.createElement('div');
                div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.8rem;';
                const p = food.per100g;
                div.innerHTML = `
                    <div style="flex: 1; min-width: 0;">
                        <strong style="color: var(--text-primary);">${food.name}</strong>
                        ${food.brand ? `<span style="font-size: 0.7rem; color: var(--text-secondary);"> ${food.brand}</span>` : ''}
                        <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 1px;">
                            ${p.calories} kcal/100g · ${Math.round(food.useCount || 1)}× logged
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.3rem; flex-shrink: 0;">
                        <button class="my-foods-fav-btn" data-name="${food.name}" data-brand="${food.brand || ''}" style="padding: 2px 6px; background: none; border: 1px solid rgba(251,191,36,0.3); color: ${food.favorite ? '#fbbf24' : 'var(--text-secondary)'}; font-size: 0.85rem; cursor: pointer; border-radius: 3px;" title="${food.favorite ? 'Remove from favorites' : 'Add to favorites'}">${food.favorite ? '⭐' : '☆'}</button>
                        <button class="my-foods-add-btn" data-name="${food.name}" data-brand="${food.brand || ''}" style="padding: 2px 6px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: var(--accent-green); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">+ Log</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        renderList(favList, favorites, 'No favorites yet — tap ☆ on a food to pin it here');
        renderList(recentList, recents, 'No history yet — log food to build your list');

        // Favorite toggle handlers
        document.querySelectorAll('.my-foods-fav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                toggleMyFoodFavorite(btn.getAttribute('data-name'), btn.getAttribute('data-brand'));
                renderMyFoods();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        });

        // Re-log handlers (expose selectedFood setter via window for the render callback)
        document.querySelectorAll('.my-foods-add-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const name = btn.getAttribute('data-name');
                const brand = btn.getAttribute('data-brand');
                const food = myFoods.find(f => f.name === name && (f.brand || '') === (brand || ''));
                if (!food) return;
                // Trigger the portion picker with this food
                if (window._symphonySelectFood) {
                    window._symphonySelectFood(food);
                }
            });
        });
    }

    // ── Main init ──
    function initFoodAnalytics() {
        renderFoodDashboard();
        renderRecipes();
        renderMyFoods();
        renderGradeChart(14);

        // Portion picker state
        let selectedFood = null; // { product, per100g: {cal,pro,carb,fat,...}, servingSize }

        const searchInput = document.getElementById('food-search-input');
        const resultsContainer = document.getElementById('food-autocomplete-results');
        const portionPicker = document.getElementById('food-portion-picker');
        const portionAmount = document.getElementById('portion-amount');
        const portionUnit = document.getElementById('portion-unit');
        const portionPreview = document.getElementById('portion-preview');
        const portionServingBtn = document.getElementById('portion-serving-btn');
        const portionAddBtn = document.getElementById('portion-add-btn');
        const portionCancelBtn = document.getElementById('portion-cancel-btn');
        const portionFoodName = document.getElementById('portion-food-name');

        let searchTimeout;
        let buildingRecipe = false;
        let recipeItems = [];

        // ── Built-in Common Foods Database (per 100g values) ──
        // qtyLabel = natural unit name, qtyG = grams per 1 unit (for quantity-based input)
        const COMMON_FOODS = [
            { name: 'Egg (whole, boiled)', brand: 'Whole Food', cal: 155, pro: 12.6, carb: 1.1, fat: 10.6, sugar: 1.1, fiber: 0, sodium: 0.124, serving: '1 large (50g)', servingG: 50, qtyLabel: 'egg', qtyG: 50 },
            { name: 'Egg (whole, scrambled)', brand: 'Whole Food', cal: 149, pro: 10.0, carb: 1.6, fat: 11.1, sugar: 1.4, fiber: 0, sodium: 0.145, serving: '1 large (61g)', servingG: 61, qtyLabel: 'egg', qtyG: 61 },
            { name: 'Egg (whole, fried)', brand: 'Whole Food', cal: 196, pro: 13.6, carb: 0.8, fat: 15.3, sugar: 0.4, fiber: 0, sodium: 0.207, serving: '1 large (46g)', servingG: 46, qtyLabel: 'egg', qtyG: 46 },
            { name: 'Egg (whole, raw)', brand: 'Whole Food', cal: 143, pro: 12.6, carb: 0.7, fat: 9.5, sugar: 0.4, fiber: 0, sodium: 0.140, serving: '1 large (50g)', servingG: 50, qtyLabel: 'egg', qtyG: 50 },
            { name: 'Egg White (raw)', brand: 'Whole Food', cal: 52, pro: 10.9, carb: 0.7, fat: 0.2, sugar: 0.7, fiber: 0, sodium: 0.166, serving: '1 large (33g)', servingG: 33, qtyLabel: 'egg white', qtyG: 33 },
            { name: 'Chicken Breast (grilled)', brand: 'Whole Food', cal: 165, pro: 31.0, carb: 0, fat: 3.6, sugar: 0, fiber: 0, sodium: 0.074, serving: '1 breast (172g)', servingG: 172, qtyLabel: 'breast', qtyG: 172 },
            { name: 'Chicken Thigh (skin off)', brand: 'Whole Food', cal: 209, pro: 26.0, carb: 0, fat: 10.9, sugar: 0, fiber: 0, sodium: 0.084, serving: '1 thigh (116g)', servingG: 116, qtyLabel: 'thigh', qtyG: 116 },
            { name: 'Salmon (baked)', brand: 'Whole Food', cal: 208, pro: 20.4, carb: 0, fat: 13.4, sugar: 0, fiber: 0, sodium: 0.059, serving: '1 fillet (154g)', servingG: 154, qtyLabel: 'fillet', qtyG: 154 },
            { name: 'Tuna (canned in water)', brand: 'Whole Food', cal: 116, pro: 25.5, carb: 0, fat: 0.8, sugar: 0, fiber: 0, sodium: 0.338, serving: '1 can (165g)', servingG: 165, qtyLabel: 'can', qtyG: 165 },
            { name: 'Beef Mince (lean)', brand: 'Whole Food', cal: 250, pro: 26.1, carb: 0, fat: 15.4, sugar: 0, fiber: 0, sodium: 0.075, serving: '100g', servingG: 100 },
            { name: 'Beef Steak (sirloin)', brand: 'Whole Food', cal: 271, pro: 26.1, carb: 0, fat: 17.3, sugar: 0, fiber: 0, sodium: 0.054, serving: '1 steak (200g)', servingG: 200, qtyLabel: 'steak', qtyG: 200 },
            { name: 'Bacon (cooked)', brand: 'Whole Food', cal: 541, pro: 37.0, carb: 1.4, fat: 42.0, sugar: 0, fiber: 0, sodium: 2.310, serving: '3 slices (34g)', servingG: 34, qtyLabel: 'rasher', qtyG: 11 },
            { name: 'White Rice (cooked)', brand: 'Whole Food', cal: 130, pro: 2.7, carb: 28.2, fat: 0.3, sugar: 0, fiber: 0.4, sodium: 0.001, serving: '1 cup (158g)', servingG: 158, qtyLabel: 'cup', qtyG: 158 },
            { name: 'Brown Rice (cooked)', brand: 'Whole Food', cal: 112, pro: 2.3, carb: 23.5, fat: 0.8, sugar: 0.4, fiber: 1.8, sodium: 0.005, serving: '1 cup (195g)', servingG: 195, qtyLabel: 'cup', qtyG: 195 },
            { name: 'Oats (rolled, dry)', brand: 'Whole Food', cal: 389, pro: 16.9, carb: 66.3, fat: 6.9, sugar: 0, fiber: 10.6, sodium: 0.002, serving: '1/2 cup (40g)', servingG: 40, qtyLabel: 'serve (½ cup)', qtyG: 40 },
            { name: 'White Bread', brand: 'Whole Food', cal: 265, pro: 9.4, carb: 49.2, fat: 3.2, sugar: 5.0, fiber: 2.7, sodium: 0.491, serving: '1 slice (25g)', servingG: 25, qtyLabel: 'slice', qtyG: 25 },
            { name: 'Wholemeal Bread', brand: 'Whole Food', cal: 247, pro: 13.0, carb: 41.3, fat: 3.4, sugar: 5.6, fiber: 6.0, sodium: 0.450, serving: '1 slice (28g)', servingG: 28, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Pasta (cooked)', brand: 'Whole Food', cal: 131, pro: 5.0, carb: 25.0, fat: 1.1, sugar: 0.6, fiber: 1.8, sodium: 0.001, serving: '1 cup (140g)', servingG: 140, qtyLabel: 'cup', qtyG: 140 },
            { name: 'Potato (boiled)', brand: 'Whole Food', cal: 87, pro: 1.9, carb: 20.1, fat: 0.1, sugar: 0.9, fiber: 1.8, sodium: 0.005, serving: '1 medium (150g)', servingG: 150, qtyLabel: 'potato', qtyG: 150 },
            { name: 'Kumara / Sweet Potato (baked)', brand: 'Whole Food', cal: 90, pro: 2.0, carb: 20.1, fat: 0.1, sugar: 6.5, fiber: 3.3, sodium: 0.036, serving: '1 medium (130g)', servingG: 130, qtyLabel: 'kumara', qtyG: 130 },
            { name: 'Banana', brand: 'Whole Food', cal: 89, pro: 1.1, carb: 22.8, fat: 0.3, sugar: 12.2, fiber: 2.6, sodium: 0.001, serving: '1 medium (118g)', servingG: 118, qtyLabel: 'banana', qtyG: 118 },
            { name: 'Apple', brand: 'Whole Food', cal: 52, pro: 0.3, carb: 13.8, fat: 0.2, sugar: 10.4, fiber: 2.4, sodium: 0.001, serving: '1 medium (182g)', servingG: 182, qtyLabel: 'apple', qtyG: 182 },
            { name: 'Orange', brand: 'Whole Food', cal: 47, pro: 0.9, carb: 11.8, fat: 0.1, sugar: 9.4, fiber: 2.4, sodium: 0, serving: '1 medium (131g)', servingG: 131, qtyLabel: 'orange', qtyG: 131 },
            { name: 'Avocado', brand: 'Whole Food', cal: 160, pro: 2.0, carb: 8.5, fat: 14.7, sugar: 0.7, fiber: 6.7, sodium: 0.007, serving: '1/2 avocado (68g)', servingG: 68, qtyLabel: 'half', qtyG: 68 },
            { name: 'Broccoli (steamed)', brand: 'Whole Food', cal: 35, pro: 2.4, carb: 7.2, fat: 0.4, sugar: 1.4, fiber: 3.3, sodium: 0.041, serving: '1 cup (91g)', servingG: 91, qtyLabel: 'cup', qtyG: 91 },
            { name: 'Spinach (raw)', brand: 'Whole Food', cal: 23, pro: 2.9, carb: 3.6, fat: 0.4, sugar: 0.4, fiber: 2.2, sodium: 0.079, serving: '1 cup (30g)', servingG: 30, qtyLabel: 'cup', qtyG: 30 },
            { name: 'Carrot (raw)', brand: 'Whole Food', cal: 41, pro: 0.9, carb: 9.6, fat: 0.2, sugar: 4.7, fiber: 2.8, sodium: 0.069, serving: '1 medium (61g)', servingG: 61, qtyLabel: 'carrot', qtyG: 61 },
            { name: 'Tomato (raw)', brand: 'Whole Food', cal: 18, pro: 0.9, carb: 3.9, fat: 0.2, sugar: 2.6, fiber: 1.2, sodium: 0.005, serving: '1 medium (123g)', servingG: 123, qtyLabel: 'tomato', qtyG: 123 },
            { name: 'Onion (raw)', brand: 'Whole Food', cal: 40, pro: 1.1, carb: 9.3, fat: 0.1, sugar: 4.2, fiber: 1.7, sodium: 0.004, serving: '1 medium (110g)', servingG: 110, qtyLabel: 'onion', qtyG: 110 },
            { name: 'Milk (whole)', brand: 'Whole Food', cal: 61, pro: 3.2, carb: 4.8, fat: 3.3, sugar: 5.1, fiber: 0, sodium: 0.043, serving: '1 cup (244ml)', servingG: 244, qtyLabel: 'cup', qtyG: 244 },
            { name: 'Milk (trim / skim)', brand: 'Whole Food', cal: 34, pro: 3.4, carb: 5.1, fat: 0.1, sugar: 5.1, fiber: 0, sodium: 0.042, serving: '1 cup (244ml)', servingG: 244, qtyLabel: 'cup', qtyG: 244 },
            { name: 'Greek Yoghurt (plain)', brand: 'Whole Food', cal: 97, pro: 9.0, carb: 3.6, fat: 5.0, sugar: 3.2, fiber: 0, sodium: 0.047, serving: '1 pot (170g)', servingG: 170, qtyLabel: 'pot', qtyG: 170 },
            { name: 'Cheese (cheddar)', brand: 'Whole Food', cal: 402, pro: 24.9, carb: 1.3, fat: 33.1, sugar: 0.5, fiber: 0, sodium: 0.621, serving: '1 slice (28g)', servingG: 28, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Butter', brand: 'Whole Food', cal: 717, pro: 0.9, carb: 0.1, fat: 81.1, sugar: 0.1, fiber: 0, sodium: 0.011, serving: '1 tbsp (14g)', servingG: 14, qtyLabel: 'tbsp', qtyG: 14 },
            { name: 'Peanut Butter', brand: 'Whole Food', cal: 588, pro: 25.1, carb: 20.0, fat: 50.4, sugar: 9.2, fiber: 6.0, sodium: 0.459, serving: '2 tbsp (32g)', servingG: 32, qtyLabel: 'tbsp', qtyG: 16 },
            { name: 'Almonds', brand: 'Whole Food', cal: 579, pro: 21.2, carb: 21.6, fat: 49.9, sugar: 4.4, fiber: 12.5, sodium: 0.001, serving: '1/4 cup (35g)', servingG: 35, qtyLabel: 'handful', qtyG: 35 },
            { name: 'Olive Oil', brand: 'Whole Food', cal: 884, pro: 0, carb: 0, fat: 100, sugar: 0, fiber: 0, sodium: 0.002, serving: '1 tbsp (14ml)', servingG: 14, qtyLabel: 'tbsp', qtyG: 14 },
            { name: 'Honey', brand: 'Whole Food', cal: 304, pro: 0.3, carb: 82.4, fat: 0, sugar: 82.1, fiber: 0.2, sodium: 0.004, serving: '1 tbsp (21g)', servingG: 21, qtyLabel: 'tbsp', qtyG: 21 },
            { name: 'Sugar (white)', brand: 'Whole Food', cal: 387, pro: 0, carb: 100, fat: 0, sugar: 100, fiber: 0, sodium: 0.001, serving: '1 tsp (4g)', servingG: 4, qtyLabel: 'tsp', qtyG: 4 },
            { name: 'Protein Powder (whey)', brand: 'Supplement', cal: 120, pro: 24.0, carb: 3.0, fat: 1.5, sugar: 1.5, fiber: 0, sodium: 0.160, serving: '1 scoop (30g)', servingG: 30, qtyLabel: 'scoop', qtyG: 30 },
            { name: 'Baked Beans (canned)', brand: 'Whole Food', cal: 94, pro: 5.2, carb: 14.5, fat: 0.4, sugar: 5.3, fiber: 5.5, sodium: 0.362, serving: '1 cup (254g)', servingG: 254, qtyLabel: 'cup', qtyG: 254 },
            { name: 'Chickpeas (canned)', brand: 'Whole Food', cal: 164, pro: 8.9, carb: 27.4, fat: 2.6, sugar: 4.8, fiber: 7.6, sodium: 0.007, serving: '1 cup (240g)', servingG: 240, qtyLabel: 'cup', qtyG: 240 },
            { name: 'Toast (white, buttered)', brand: 'Whole Food', cal: 313, pro: 8.0, carb: 42.0, fat: 12.0, sugar: 4.5, fiber: 2.0, sodium: 0.500, serving: '1 slice (35g)', servingG: 35, qtyLabel: 'slice', qtyG: 35 },
            { name: 'Sausage (pork)', brand: 'Whole Food', cal: 301, pro: 18.0, carb: 0, fat: 25.0, sugar: 0, fiber: 0, sodium: 0.749, serving: '1 link (75g)', servingG: 75, qtyLabel: 'sausage', qtyG: 75 },
            { name: 'Ham (deli sliced)', brand: 'Whole Food', cal: 145, pro: 21.0, carb: 3.5, fat: 5.5, sugar: 0, fiber: 0, sodium: 1.203, serving: '3 slices (84g)', servingG: 84, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Mushrooms (raw)', brand: 'Whole Food', cal: 22, pro: 3.1, carb: 3.3, fat: 0.3, sugar: 2.0, fiber: 1.0, sodium: 0.005, serving: '1 cup (70g)', servingG: 70, qtyLabel: 'cup', qtyG: 70 },
            { name: 'Capsicum / Bell Pepper', brand: 'Whole Food', cal: 31, pro: 1.0, carb: 6.0, fat: 0.3, sugar: 4.2, fiber: 2.1, sodium: 0.004, serving: '1 medium (119g)', servingG: 119, qtyLabel: 'pepper', qtyG: 119 },
            { name: 'Lettuce (iceberg)', brand: 'Whole Food', cal: 14, pro: 0.9, carb: 3.0, fat: 0.1, sugar: 2.0, fiber: 1.2, sodium: 0.010, serving: '1 cup (72g)', servingG: 72, qtyLabel: 'cup', qtyG: 72 },
            { name: 'Mango', brand: 'Whole Food', cal: 60, pro: 0.8, carb: 15.0, fat: 0.4, sugar: 13.7, fiber: 1.6, sodium: 0.001, serving: '1 cup (165g)', servingG: 165, qtyLabel: 'mango', qtyG: 200 },
            { name: 'Strawberries', brand: 'Whole Food', cal: 32, pro: 0.7, carb: 7.7, fat: 0.3, sugar: 4.9, fiber: 2.0, sodium: 0.001, serving: '1 cup (152g)', servingG: 152, qtyLabel: 'cup', qtyG: 152 },
            { name: 'Blueberries', brand: 'Whole Food', cal: 57, pro: 0.7, carb: 14.5, fat: 0.3, sugar: 10.0, fiber: 2.4, sodium: 0.001, serving: '1 cup (148g)', servingG: 148, qtyLabel: 'cup', qtyG: 148 },
        ];

        // ── Search ──
        if (searchInput && resultsContainer) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                if (query.length < 2) { resultsContainer.style.display = 'none'; return; }

                searchTimeout = setTimeout(async () => {
                    resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: #94a3b8; font-size: 0.85rem;">Searching...</div>';
                    resultsContainer.style.display = 'block';

                    // 1) Search built-in common foods first (instant, always works)
                    const q = query.toLowerCase();
                    const localMatches = COMMON_FOODS.filter(f => f.name.toLowerCase().includes(q));

                    resultsContainer.innerHTML = '';

                    if (localMatches.length > 0) {
                        // Header for local results
                        const header = document.createElement('div');
                        header.style.cssText = 'padding: 0.4rem 0.75rem; font-size: 0.7rem; color: var(--accent-green); text-transform: uppercase; font-weight: 700; border-bottom: 1px solid rgba(52,211,153,0.15);';
                        header.textContent = '🥚 Whole Foods';
                        resultsContainer.appendChild(header);

                        localMatches.forEach(food => {
                            const resDiv = document.createElement('div');
                            resDiv.style.cssText = 'padding: 0.65rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;';
                            resDiv.className = 'food-result-item';
                            resDiv.innerHTML = `
                                <div style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">${food.name} <span style="font-size: 0.7rem; color: var(--accent-green);">${food.brand}</span></div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                                    per 100g: ${food.cal} kcal | ${food.pro}P ${food.carb}C ${food.fat}F
                                    <span style="color: var(--accent-blue);"> · Serving: ${food.serving}</span>
                                </div>
                            `;
                            resDiv.addEventListener('click', () => {
                                selectedFood = {
                                    name: food.name, brand: food.brand,
                                    per100g: { calories: food.cal, protein: food.pro, carbs: food.carb, fats: food.fat, sugars: food.sugar, fiber: food.fiber, sodium: food.sodium },
                                    servingSize: food.serving, servingG: food.servingG, ingredients: '',
                                    qtyLabel: food.qtyLabel || null, qtyG: food.qtyG || null
                                };
                                portionFoodName.innerText = food.name;
                                // Switch to quantity mode if food has a natural unit
                                if (food.qtyLabel && food.qtyG) {
                                    portionAmount.value = 1;
                                    portionAmount.step = 1;
                                    portionAmount.min = 0.5;
                                    portionUnit.innerHTML = `<option value="qty">× ${food.qtyLabel}${food.qtyLabel.endsWith('s') ? '' : '(s)'} (${food.qtyG}g ea)</option><option value="g">grams</option>`;
                                    portionUnit.value = 'qty';
                                } else {
                                    portionAmount.value = food.servingG || 100;
                                    portionAmount.step = 1;
                                    portionAmount.min = 1;
                                    portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
                                }
                                portionServingBtn.style.display = 'none';
                                updatePortionPreview();
                                portionPicker.style.display = 'block';
                                resultsContainer.style.display = 'none';
                            });
                            resultsContainer.appendChild(resDiv);
                        });
                    }

                    // 2) Also search Open Food Facts for branded/packaged products
                    if (query.length >= 3) {
                        try {
                            const response = await fetch(`https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=6`);
                            const data = await response.json();

                            if (data.products && data.products.length > 0) {
                                // Add header for packaged products
                                const offHeader = document.createElement('div');
                                offHeader.style.cssText = 'padding: 0.4rem 0.75rem; font-size: 0.7rem; color: var(--accent-blue); text-transform: uppercase; font-weight: 700; border-bottom: 1px solid rgba(56,189,248,0.15); margin-top: 0.25rem;';
                                offHeader.textContent = '📦 Packaged Products (Open Food Facts)';
                                resultsContainer.appendChild(offHeader);

                                data.products.forEach(product => {
                                    if (!product.nutriments || (!product.nutriments['energy-kcal_100g'] && !product.nutriments['energy-kcal'])) return;

                                    const n = product.nutriments;
                                    const per100g = {
                                        calories: Math.round(n['energy-kcal_100g'] || n['energy-kcal'] || 0),
                                        protein: Math.round((n['proteins_100g'] || n.proteins || 0) * 10) / 10,
                                        carbs: Math.round((n['carbohydrates_100g'] || n.carbohydrates || 0) * 10) / 10,
                                        fats: Math.round((n['fat_100g'] || n.fat || 0) * 10) / 10,
                                        sugars: Math.round((n['sugars_100g'] || n.sugars || 0) * 10) / 10,
                                        fiber: Math.round((n['fiber_100g'] || n.fiber || 0) * 10) / 10,
                                        sodium: Math.round((n['sodium_100g'] || n.sodium || 0) * 100) / 100
                                    };
                                    const servingSize = product.serving_size || null;
                                    const servingG = product.serving_quantity || null;

                                    const desc = product.product_name || 'Unknown Product';
                                    const brand = product.brands || '';

                                    const resDiv = document.createElement('div');
                                    resDiv.style.cssText = 'padding: 0.65rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;';
                                    resDiv.className = 'food-result-item';
                                    resDiv.innerHTML = `
                                    <div style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">${desc} <span style="font-size: 0.7rem; color: #94a3b8;">${brand}</span></div>
                                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                                        per 100g: ${per100g.calories} kcal | ${per100g.protein}P ${per100g.carbs}C ${per100g.fats}F
                                        ${servingSize ? `<span style="color: var(--accent-blue);"> · Serving: ${servingSize}</span>` : ''}
                                    </div>
                                `;

                                    resDiv.addEventListener('click', () => {
                                        selectedFood = {
                                            name: desc, brand, per100g, servingSize, servingG,
                                            ingredients: product.ingredients_text || '',
                                            qtyLabel: null, qtyG: null
                                        };
                                        portionFoodName.innerText = `${desc}${brand ? ' (' + brand + ')' : ''}`;
                                        // Reset to grams mode for packaged products
                                        portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
                                        portionAmount.step = 1;
                                        portionAmount.min = 1;
                                        portionAmount.value = 100;
                                        portionServingBtn.style.display = servingSize ? 'inline-block' : 'none';
                                        portionServingBtn.innerText = servingSize ? `1 Serving (${servingSize})` : '1 Serving';
                                        updatePortionPreview();
                                        portionPicker.style.display = 'block';
                                        resultsContainer.style.display = 'none';
                                        searchInput.value = '';
                                        if (typeof playRetroClick === 'function') playRetroClick();
                                    });

                                    resultsContainer.appendChild(resDiv);
                                });
                            }
                        } catch (error) {
                            console.error('Food Search Error:', error);
                        }
                    }

                    // If no results at all from either source
                    if (resultsContainer.children.length === 0) {
                        resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: var(--text-secondary); font-size: 0.85rem;">No results found. Try a different search term.</div>';
                    }
                }, 300);
            });

            document.addEventListener('click', (e) => {
                if (e.target !== searchInput && !resultsContainer.contains(e.target)) {
                    resultsContainer.style.display = 'none';
                }
            });
        }

        // ── Portion controls ──
        function getResolvedGrams() {
            const amt = parseFloat(portionAmount.value) || 0;
            const unit = portionUnit.value;
            if (unit === 'qty' && selectedFood && selectedFood.qtyG) {
                return amt * selectedFood.qtyG;
            }
            return amt;
        }

        function updatePortionPreview() {
            if (!selectedFood) return;
            const grams = getResolvedGrams();
            const scaled = scaleNutrients(selectedFood.per100g, grams);
            const unit = portionUnit.value;
            const suffix = (unit === 'qty' && selectedFood.qtyLabel) ? ` (${Math.round(grams)}g)` : '';
            portionPreview.innerText = `${scaled.calories} kcal | ${scaled.protein}P ${scaled.carbs}C ${scaled.fats}F${suffix}`;
        }

        if (portionAmount) portionAmount.addEventListener('input', updatePortionPreview);
        if (portionUnit) portionUnit.addEventListener('change', () => {
            // When switching between qty and grams, adjust the value
            if (portionUnit.value === 'g' && selectedFood && selectedFood.qtyG) {
                portionAmount.value = getResolvedGrams();
                portionAmount.step = 1;
                portionAmount.min = 1;
            } else if (portionUnit.value === 'qty' && selectedFood && selectedFood.qtyG) {
                portionAmount.value = 1;
                portionAmount.step = 1;
                portionAmount.min = 0.5;
            }
            updatePortionPreview();
        });

        if (portionServingBtn) {
            portionServingBtn.addEventListener('click', () => {
                if (selectedFood && selectedFood.servingG) {
                    portionAmount.value = selectedFood.servingG;
                    updatePortionPreview();
                }
            });
        }

        if (portionCancelBtn) {
            portionCancelBtn.addEventListener('click', () => {
                portionPicker.style.display = 'none';
                selectedFood = null;
            });
        }

        // Expose a function so My Foods panel can open the portion picker
        window._symphonySelectFood = function (food) {
            selectedFood = {
                name: food.name, brand: food.brand || '',
                per100g: food.per100g,
                servingSize: food.servingSize, servingG: food.servingG,
                ingredients: '',
                qtyLabel: food.qtyLabel || null, qtyG: food.qtyG || null
            };
            portionFoodName.innerText = food.name;
            if (food.qtyLabel && food.qtyG) {
                portionAmount.value = 1;
                portionAmount.step = 1;
                portionAmount.min = 0.5;
                portionUnit.innerHTML = `<option value="qty">× ${food.qtyLabel}${food.qtyLabel.endsWith('s') ? '' : '(s)'} (${food.qtyG}g ea)</option><option value="g">grams</option>`;
                portionUnit.value = 'qty';
            } else {
                portionAmount.value = food.servingG || 100;
                portionAmount.step = 1;
                portionAmount.min = 1;
                portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
            }
            portionServingBtn.style.display = 'none';
            updatePortionPreview();
            portionPicker.style.display = 'block';
        };

        if (portionAddBtn) {
            portionAddBtn.addEventListener('click', () => {
                if (!selectedFood) return;
                const grams = getResolvedGrams();
                const unit = portionUnit.value;
                const displayAmt = parseFloat(portionAmount.value) || 1;
                const displayUnit = (unit === 'qty' && selectedFood.qtyLabel) ? selectedFood.qtyLabel + (displayAmt !== 1 ? 's' : '') : unit;
                const scaled = scaleNutrients(selectedFood.per100g, grams);

                const logEntry = {
                    name: selectedFood.name,
                    amount: displayAmt,
                    unit: displayUnit,
                    grams: Math.round(grams),
                    ...scaled,
                    ingredients: selectedFood.ingredients,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                };

                // Auto-save to My Foods history
                addToMyFoods(selectedFood);

                if (buildingRecipe) {
                    // Add to recipe builder instead
                    recipeItems.push({ ...logEntry, per100g: selectedFood.per100g });
                    renderRecipeBuilder();
                } else {
                    const currentLog = getDailyFoodLog();
                    currentLog.push(logEntry);
                    saveFoodLog(currentLog);
                    renderFoodDashboard();
                }

                portionPicker.style.display = 'none';
                selectedFood = null;
                renderMyFoods();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        }

        // ── Recipe system ──
        const recipesHeader = document.querySelector('[data-pool="food-recipes"]');
        const recipesPanel = document.getElementById('food-recipes-panel');
        if (recipesHeader && recipesPanel) {
            recipesHeader.addEventListener('click', () => {
                const open = recipesPanel.style.display !== 'none';
                recipesPanel.style.display = open ? 'none' : 'block';
                recipesHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
            });
        }

        // ── My Foods accordion ──
        const myFoodsHeader = document.querySelector('[data-pool="my-foods"]');
        const myFoodsPanel = document.getElementById('my-foods-panel');
        if (myFoodsHeader && myFoodsPanel) {
            myFoodsHeader.addEventListener('click', () => {
                const open = myFoodsPanel.style.display !== 'none';
                myFoodsPanel.style.display = open ? 'none' : 'block';
                myFoodsHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
            });
        }

        const createRecipeBtn = document.getElementById('create-recipe-btn');
        const recipeBuilder = document.getElementById('recipe-builder');
        const recipeCloseBtn = document.getElementById('recipe-builder-close');
        const saveRecipeBtn = document.getElementById('save-recipe-btn');

        if (createRecipeBtn) {
            createRecipeBtn.addEventListener('click', () => {
                buildingRecipe = true;
                recipeItems = [];
                recipeBuilder.style.display = 'block';
                document.getElementById('recipe-name-input').value = '';
                renderRecipeBuilder();
            });
        }

        if (recipeCloseBtn) {
            recipeCloseBtn.addEventListener('click', () => {
                buildingRecipe = false;
                recipeItems = [];
                recipeBuilder.style.display = 'none';
            });
        }

        function renderRecipeBuilder() {
            const list = document.getElementById('recipe-items-list');
            const totalsEl = document.getElementById('recipe-totals');
            if (!list) return;

            if (recipeItems.length === 0) {
                list.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">Search and add foods above</li>';
                totalsEl.innerText = '';
                return;
            }

            list.innerHTML = recipeItems.map((item, i) =>
                `<li style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span>${item.name} (${item.amount}${item.unit})</span>
                    <span style="color: var(--text-secondary);">${item.calories} kcal</span>
                </li>`
            ).join('');

            const totals = calculateDailyTotals(recipeItems);
            totalsEl.innerText = `Total: ${Math.round(totals.calories)} kcal | ${Math.round(totals.protein)}P ${Math.round(totals.carbs)}C ${Math.round(totals.fats)}F`;
        }

        if (saveRecipeBtn) {
            saveRecipeBtn.addEventListener('click', () => {
                const name = document.getElementById('recipe-name-input').value.trim();
                if (!name || recipeItems.length === 0) return;

                const recipe = { name, items: recipeItems };
                const allRecipes = getRecipes();
                allRecipes.push(recipe);
                saveRecipes(allRecipes);
                saveRecipeToSupabase(recipe); // async background save

                buildingRecipe = false;
                recipeItems = [];
                recipeBuilder.style.display = 'none';
                renderRecipes();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }

        // ── Analyze & Save button ──
        const runAuditBtn = document.getElementById('run-food-audit-btn');
        if (runAuditBtn) {
            runAuditBtn.addEventListener('click', async () => {
                const log = getDailyFoodLog();
                if (log.length === 0) {
                    alert('No food logged yet today.');
                    return;
                }

                runAuditBtn.innerHTML = '<span class="icon">⏳</span> Analyzing...';

                const totals = calculateDailyTotals(log);
                const result = gradeDailyIntake(totals);
                const today = getLocalDayDateString();

                // Save to history (localStorage)
                const history = getFoodHistory();
                const existingIdx = history.findIndex(h => h.date === today);
                const entry = { date: today, grade: result.grade, score: result.score, totals };
                if (existingIdx >= 0) history[existingIdx] = entry;
                else history.push(entry);
                saveFoodHistory(history);

                // Save to Supabase
                await saveDayToSupabase(today, log, totals, result.grade, result.score);

                // Refresh charts
                renderGradeChart(14);
                renderFoodDashboard();

                runAuditBtn.innerHTML = '<span class="icon">✅</span> Saved!';
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
                setTimeout(() => {
                    runAuditBtn.innerHTML = '<span class="icon">🔍</span> Analyze & Save to History';
                }, 2000);
            });
        }

        // ── Grade range buttons (7d / 14d / 30d) ──
        document.querySelectorAll('.grade-range-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.grade-range-btn').forEach(b => {
                    b.style.background = 'rgba(56,189,248,0.2)';
                    b.style.color = 'var(--accent-blue)';
                });
                btn.style.background = 'rgba(56,189,248,0.4)';
                btn.style.color = '#fff';
                renderGradeChart(parseInt(btn.getAttribute('data-days')));
            });
        });

        // ── Collapsible macro history ──
        const macroHeader = document.getElementById('macro-history-header');
        const macroBody = document.getElementById('macro-history-body');
        let macroLoaded = false;
        if (macroHeader && macroBody) {
            macroHeader.addEventListener('click', () => {
                const open = macroBody.style.display !== 'none';
                macroBody.style.display = open ? 'none' : 'block';
                macroHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
                if (!open && !macroLoaded) {
                    renderMacroHistoryChart();
                    macroLoaded = true;
                }
            });
        }

        // Fetch Supabase history in background for charts
        fetchHistoryFromSupabase(30).then(() => renderGradeChart(14));
    }

    // Initialize View
    // initChart();
    // renderTimeline();
    // createListItems(dailyCandidates, 'daily-list');
    // createListItems(weeklyMonthly.weekly, 'weekly-list');
    // createListItems(weeklyMonthly.monthly, 'monthly-list');

    // Create dog tasks (Referencing lines 726-734 block instead to avoid duplicate let/const error)

    // --- Bio Tracking Integration ---
    const MOCK_BLOOD_DATA = [
        { marker: 'Platelets', value: '509 x 10e9/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'WBC', value: '12.6 x 10e9/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'Ferritin', value: '205 ug/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'CRP', value: '9 mg/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'TSH', value: '0.37 mIU/L', status: 'Borderline Low', color: 'var(--accent-yellow)' }
    ];

    const MEDICAL_ALERTS = [
        {
            gene: 'HLA-B27',
            risk: 'Ankylosing Spondylitis / Autoimmune Joint Fusion',
            action: 'ALERT: Massive genetic liability. The moment you experience chronic, unexplainable lower back pain or morning joint stiffness, you must immediately report this HLA-B27 finding to a Rheumatologist to prevent spinal fusion.'
        },
        {
            gene: '9p21 (CDKN2A/B)',
            risk: 'Coronary Artery Disease (Heart Attack Risk)',
            action: 'Your coronary arteries are genetically prone to stiffening and retaining plaque. You must keep your ApoB blood levels <60 mg/dL for life. Aggressive Zone 2 cardio is mandatory.'
        },
        {
            gene: 'CYP3A4 (T/C)',
            risk: 'Rapid Drug Metabolizer (Statins/Testosterone)',
            action: 'Your liver is a hyper-active incinerator. If prescribing a statin for your 9p21 heart gene, warn your doctor that standard starting doses will likely be destroyed before working. You require tailored dosing.'
        },
        {
            gene: 'MTHFR (A/G)',
            risk: 'Homocysteine Vascular Damage',
            action: 'Vitamin conversion runs at ~65% speed. Avoid synthetic Folic Acid; take L-Methylfolate. Request a Homocysteine blood test to ensure levels are < 9 µmol/L to prevent artery scratching.'
        }
    ];

    const GENETIC_HACKS = [
        {
            gene: 'ADRB2 (G/G)',
            trait: 'Power/Sprint Fat Burning',
            advice: 'Stop jogging to lose fat. Your specific beta-2 receptors dictate that heavy, explosive weightlifting or high-intensity sprints will shred body fat drastically faster than steady-state cardio.'
        },
        {
            gene: 'COMT (G/G)',
            trait: 'The Warrior (Fast Dopamine Clearance)',
            advice: 'You violent sweep dopamine away. You require high-stakes environments or intense physical stress to feel "awake". Caffeine and L-Tyrosine are highly effective.'
        },
        {
            gene: 'COL5A1 (C/T)',
            trait: 'Brittle Tendons & Achilles Risk',
            advice: 'Abandon explosive plyometrics (box jumps). Perform Heavy Slow Resistance (HSR) training— specifically 4-5 second eccentric lowering phases—to purposefully thicken your tendons.'
        },
        {
            gene: 'CYP1A2 (A/C)',
            trait: 'Ultra-Slow Caffeine Clearance',
            advice: 'A strict 10:00 AM hard cutoff for ALL caffeine is mandatory. A 2 PM coffee means 50% of the drug is still bound to your receptors at midnight, utterly destroying deep sleep.'
        },
        {
            gene: 'SIRT1 (C/C)',
            trait: 'Disrupted Circadian Aging',
            advice: 'You physically cannot handle shifting sleep schedules. Pulling all-nighters or rotating shift work will shred your telomeres and induce rapid biological aging. Wake up at the exact same hour daily.'
        },
        {
            gene: 'ACTN3 (C/T)',
            trait: 'Hybrid Muscle Fibers',
            advice: 'Perfectly mixed 50/50 muscle fiber. Your body responds incredibly well to hybrid training (Crossfit, Hyrox, MMA) building heavy muscle mass AND deep VO2 max simultaneously.'
        }
    ];

    function initBioTracking() {
        // Render Blood Markers
        const bloodList = document.getElementById('blood-marker-list');
        if (bloodList) {
            bloodList.innerHTML = '';
            MOCK_BLOOD_DATA.forEach(item => {
                const li = document.createElement('li');
                li.style = `display:flex; justify-content:space-between; color: var(--text-primary); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0.5rem 0;`;
                li.innerHTML = `<span>${item.marker}</span> <div><strong>${item.value}</strong> <span style="color:${item.color}; margin-left: 0.5rem;">[${item.status}]</span></div>`;
                bloodList.appendChild(li);
            });
        }

        // Render Medical Alerts (Doctor Prompts)
        const medicalContainer = document.getElementById('medical-alerts-container');
        if (medicalContainer) {
            medicalContainer.innerHTML = '';
            MEDICAL_ALERTS.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-red); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-red); display: flex; justify-content: space-between;">
                        <span>${item.gene}</span>
                        <span style="font-size: 0.8rem; background: rgba(239, 68, 68, 0.2); padding: 2px 8px; border-radius: 12px; color: #fca5a5;">Clinical Review</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #fca5a5; font-weight: 500; margin-top: 0.25rem;">${item.risk}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem; line-height: 1.5;">
                        <strong>Action for Doctor:</strong> ${item.action}
                    </div>
                `;
                medicalContainer.appendChild(div);
            });
        }

        // Render Genetic Hacks
        const geneticsContainer = document.getElementById('genetic-hacks-container');
        if (geneticsContainer) {
            geneticsContainer.innerHTML = '';
            GENETIC_HACKS.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-purple); display: flex; justify-content: space-between;">
                        <span>${item.gene}</span>
                        <span style="font-size: 0.8rem; background: rgba(192, 132, 252, 0.2); padding: 2px 8px; border-radius: 12px;">${item.trait}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem; line-height: 1.5;">
                        <strong>Hack:</strong> ${item.advice}
                    </div>
                `;
                geneticsContainer.appendChild(div);
            });
        }
    }

    // Initialize View
    // initChart();
    // fetchTasksAndRenderTimeline(); (Now called differently or moved)
    fetchTasksAndRenderTimeline();
    // createListItems(dailyCandidates, 'daily-list');
    // createListItems(weeklyMonthly.weekly, 'weekly-list');
    // createListItems(weeklyMonthly.monthly, 'monthly-list');

    // Create dog tasks
    const dogTrainingTasks = [
        { text: "Meal Time: 'Wait' until told 'Okay'", points: 1 },
        { text: "Doorways: 'Wait' before going through any door", points: 1 },
        { text: "Impulse Control: Practice 'Leave It' during play", points: 1 },
        { text: "Free Time: 30-min Sniffari / Decompression Walk", points: 3 },
        { text: "Mental Stimulation: 10 mins Hide and Seek", points: 2 }
    ];
    createListItems(dogTrainingTasks, 'dog-training-list');

    // Create supplement tasks (now moved exclusively to the Bio tab)
    // We pass extra properties for Supps Vault syncing
    // AM — Empty Stomach (30 min before food)
    const supplementsAM_Empty = [
        { text: "☀️ Solgar NAC 600mg × 2 caps (1200mg) — Empty stomach, 30 min before breakfast", points: 2, suppSync: "NAC", suppDose: 2 }
    ];
    createListItems(supplementsAM_Empty, 'supp-am-empty-body');

    // AM — With Breakfast
    const supplementsAM_Food = [
        { text: "🧬 Doctor's Best Vitamin K2 MK-7 × 2 caps (200mcg) — With food (fat-soluble)", points: 2, suppSync: "Vitamin K2", suppDose: 2 },
        { text: "🐟 Go Healthy Fish Oil + D3 10,000IU × 1 cap — With food", points: 1, suppSync: "Fish Oil", suppDose: 1 },
        { text: "🧠 Natroceutics Activated B-Complex + L-Theanine × 1 cap — With breakfast", points: 1, suppSync: "B-Complex", suppDose: 1 },
        { text: "🔥 Sanderson Turmeric 28,000+ × 2 caps — With food (needs fat)", points: 2, suppSync: "Turmeric", suppDose: 2 },
        { text: "🩸 Even Blood Sugar Babe × 2 caps — With biggest carb meal", points: 2, suppSync: "Blood Sugar Babe", suppDose: 2 },
        { text: "💊 Phloe Bowel & Gut Health × 2 caps — Before breakfast", points: 1, suppSync: "Phloe", suppDose: 2 }
    ];
    createListItems(supplementsAM_Food, 'supp-am-food-body');

    // PM — With Dinner
    const supplementsPM_Dinner = [
        { text: "🐟 Go Healthy Fish Oil + D3 × 2 caps — With dinner (Attia split protocol)", points: 2, suppSync: "Fish Oil", suppDose: 2 }
    ];
    createListItems(supplementsPM_Dinner, 'supp-pm-dinner-body');

    // PM — Before Bed
    const supplementsPM = [
        { text: "🌙 Swisse Magnesium Glycinate × 3 caps (450mg elemental) — 30-60 min before bed", points: 2, suppSync: "Magnesium Glycinate", suppDose: 3 }
    ];
    createListItems(supplementsPM, 'supp-pm-bed-body');

    // Create Reminders (Mental Load)
    const activeReminders = [
        { text: "Make sure outside kids' toys are left upright so they can easily use them", points: 0 },
        { text: "Discard used tooth floss", points: 0 }
    ];
    createListItems(activeReminders, 'reminders-list');

    // --- Procurement (Wants vs Needs) Integration ---
    async function initProcurement() {
        const needsContainer = document.getElementById('needs-container');
        const wantsContainer = document.getElementById('wants-container');
        const advisoryContainer = document.getElementById('athena-advisory-container');
        const addBtn = document.getElementById('add-procurement-btn');

        if (!needsContainer || !wantsContainer || !advisoryContainer) return;

        let procurementData = [];
        const LOCAL_KEY = 'symphony_procurement_local';

        async function fetchData() {
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_procurement?select=*&order=created_at.desc`, {
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (response.ok) {
                    procurementData = await response.json();
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (e) {
                console.warn('Procurement: Supabase fetch failed, using localStorage:', e);
                const local = localStorage.getItem(LOCAL_KEY);
                if (local) procurementData = JSON.parse(local);
            }
        }

        function renderAll() {
            needsContainer.innerHTML = '';
            wantsContainer.innerHTML = '';
            advisoryContainer.innerHTML = '';

            if (procurementData.length === 0) {
                needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No items yet. Add one above!</div>';
                return;
            }

            const needs = procurementData.filter(d => d.category === 'NEED');
            const wants = procurementData.filter(d => d.category === 'WANT');

            function renderCard(item, container, dotColor) {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem; position: relative;`;
                div.innerHTML = `
                    <button class="delete-procurement-btn" data-id="${item.id}" style="position: absolute; top: 0.5rem; right: 0.5rem; background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${dotColor};"></span>
                        ${item.item}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        <strong>Why:</strong> ${item.justification || 'No justification provided.'}
                    </div>
                `;
                container.appendChild(div);
            }

            needs.forEach(item => renderCard(item, needsContainer, 'var(--accent-green)'));
            wants.forEach(item => renderCard(item, wantsContainer, 'var(--accent-yellow)'));

            if (needs.length === 0) needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No essential needs listed.</div>';
            if (wants.length === 0) wantsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No discretionary wants listed.</div>';

            // Render Advisory (for all items)
            procurementData.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem;`;
                const verdictColor = item.athena_verdict === 'APPROVED' ? 'var(--accent-green)' : (item.athena_verdict === 'FLAGGED' ? 'var(--accent-yellow)' : 'var(--text-secondary)');
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-blue); display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Target: ${item.item}</span>
                        <span style="font-size: 0.75rem; color: ${verdictColor}; border: 1px solid ${verdictColor}; padding: 2px 6px; border-radius: 4px;">${item.athena_verdict || 'PENDING'}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        ${item.athena_comment || 'Awaiting Athena assessment...'}
                    </div>
                `;
                advisoryContainer.appendChild(div);
            });

            // Bind delete buttons
            document.querySelectorAll('.delete-procurement-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    procurementData = procurementData.filter(d => d.id !== id);
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                    renderAll();
                    try {
                        await fetch(`${SUPABASE_URL}/rest/v1/symphony_procurement?id=eq.${id}`, {
                            method: 'DELETE',
                            headers: {
                                'apikey': SUPABASE_ANON_KEY,
                                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                            }
                        });
                    } catch (e) { console.warn('Failed to delete procurement item:', e); }
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });
        }

        // Add item handler
        if (addBtn) {
            addBtn.addEventListener('click', async () => {
                const itemEl = document.getElementById('procurement-item-input');
                const justEl = document.getElementById('procurement-justification-input');
                const catEl = document.getElementById('procurement-category-input');

                const item = itemEl.value.trim();
                const justification = justEl.value.trim();
                const category = catEl.value;

                if (!item) {
                    alert('Please enter an item name.');
                    return;
                }

                const newItem = {
                    item,
                    justification: justification || 'No justification provided.',
                    category,
                    athena_verdict: 'PENDING',
                    athena_comment: 'Awaiting Athena assessment...'
                };

                // Optimistic local add
                procurementData.unshift(newItem);
                localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                renderAll();

                itemEl.value = '';
                justEl.value = '';

                // Persist to Supabase
                try {
                    const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_procurement`, {
                        method: 'POST',
                        headers: {
                            'apikey': SUPABASE_ANON_KEY,
                            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=representation'
                        },
                        body: JSON.stringify(newItem)
                    });
                    if (resp.ok) {
                        await fetchData();
                        renderAll();
                    }
                } catch (e) {
                    console.warn('Failed to save procurement item to Supabase:', e);
                }

                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }

        // Init
        needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem;">Syncing from Supabase...</div>';
        await fetchData();
        renderAll();
    }

    // Assign globally to be called by onchange
    window.changeTaskColor = async function (taskId, selectEl) {
        const newColor = selectEl.value;
        const colorMap = {
            'RED': '#ef4444',
            'ORANGE': '#f97316',
            'GREEN': '#10b981'
        };
        const hex = colorMap[newColor];

        // Optimistically update the dropdown visual styling
        selectEl.style.borderColor = hex;
        selectEl.style.color = hex;

        try {
            selectEl.disabled = true;

            await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${taskId}`, {
                method: 'PATCH',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=minimal'
                },
                body: JSON.stringify({ priority_color: newColor })
            });

            selectEl.disabled = false;

            // Intentionally bypassing initTaskConfigurator() here 
            // so the task doesn't vanish from the user's current category view.

            // Refresh the main schedule view behind the scenes just in case
            if (typeof fetchSupabaseData === 'function') {
                fetchSupabaseData();
            }

        } catch (err) {
            console.error("Failed to update task color:", err);
            selectEl.disabled = false;
            alert("Failed to save changes.");
        }
    };

    // --- Supps Vault Implementation ---
    async function initSuppsVault() {
        const grid = document.getElementById('supps-inventory-grid');
        const addBtn = document.getElementById('add-supp-btn');
        if (!grid || !addBtn) return;

        let inventory = [];

        // 1. Fetch from Supabase (safe: won't clobber local data)
        async function fetchSupabaseInventory() {
            try {
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_supp_inventory?order=name.asc`, {
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                    }
                });
                if (resp.ok) {
                    const supabaseData = await resp.json();
                    const localData = localStorage.getItem('symphony_supp_inventory_local');
                    const localItems = localData ? JSON.parse(localData) : [];
                    if (supabaseData.length > 0) {
                        inventory = supabaseData;
                        localStorage.setItem('symphony_supp_inventory_local', JSON.stringify(inventory));
                    } else if (localItems.length > 0) {
                        inventory = localItems;
                        console.info('Supps: Supabase empty, keeping local inventory');
                    } else {
                        inventory = [];
                    }
                }
            } catch (e) {
                console.error("Failed to fetch supps from Supabase, falling back to local:", e);
                const local = localStorage.getItem('symphony_supp_inventory_local');
                if (local) inventory = JSON.parse(local);
            }
        }

        // 2. Add New Supp
        async function addSupp() {
            const nameEl = document.getElementById('supp-name-input');
            const capEl = document.getElementById('supp-capacity-input');
            const doseEl = document.getElementById('supp-dose-input');

            const name = nameEl.value.trim();
            const capacity = parseInt(capEl.value);
            const dailyDose = parseInt(doseEl.value);

            if (!name || isNaN(capacity) || isNaN(dailyDose)) {
                alert("Please fill out all fields correctly.");
                return;
            }

            const newSupp = {
                name,
                total_capacity: capacity,
                current_stock: capacity,
                daily_dose: dailyDose
            };

            // Optimistic Local Add
            inventory.push(newSupp);
            renderGrid();

            nameEl.value = ''; capEl.value = ''; doseEl.value = '';

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_supp_inventory`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify(newSupp)
                });
                // Re-fetch to get actual IDs
                await fetchSupabaseInventory();
                renderGrid();
            } catch (e) {
                console.error("Failed to save new supp to Supabase:", e);
            }
        }

        // 3. Update existing supp (take dose or refill)
        async function updateSuppStock(id, newStock) {
            // Find locally and update
            const supp = inventory.find(s => s.id === id);
            if (supp) {
                supp.current_stock = newStock;
                renderGrid(); // Instant UI update
            }

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_supp_inventory?id=eq.${id}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({
                        current_stock: newStock,
                        updated_at: new Date().toISOString()
                    })
                });
            } catch (e) {
                console.error("Failed to update stock in Supabase:", e);
            }
        }

        // Global Sync Function for Checklists
        window.triggerSuppSync = async function (suppName, amountToDeduct) {
            const supp = inventory.find(s => s.name === suppName);
            if (supp) {
                const newStock = Math.max(0, supp.current_stock - amountToDeduct);
                console.log(`Syncing ${suppName}: Deducting ${amountToDeduct}. New Stock: ${newStock}`);
                await updateSuppStock(supp.id, newStock);
            } else {
                console.warn(`Could not sync ${suppName}: Not found in Vault inventory.`);
            }
        };

        // 4. Render Grid
        function renderGrid() {
            grid.innerHTML = '';
            if (inventory.length === 0) {
                grid.innerHTML = '<div style="color: var(--text-secondary); grid-column: 1/-1;">No supplements tracked yet. Add one above.</div>';
                return;
            }

            inventory.forEach(supp => {
                const { id, name, total_capacity, current_stock, daily_dose } = supp;
                const percentage = Math.max(0, Math.min(100, (current_stock / total_capacity) * 100));

                const isLow = percentage < 50;
                const dangerText = isLow ? '<span style="color: var(--accent-red); font-size: 0.8rem; margin-left: 0.5rem;" class="blinking">⚠️ LOW STOCK</span>' : '';
                const cardBorder = isLow ? 'var(--accent-red)' : 'var(--glass-border)';
                const barColor = isLow ? 'var(--accent-red)' : 'var(--accent-blue)';

                let daysLeft = '0';
                if (daily_dose > 0) {
                    daysLeft = Math.floor(current_stock / daily_dose);
                }

                const div = document.createElement('div');
                div.className = 'glass-panel';
                div.style.cssText = `border-color: ${cardBorder}; position: relative; padding: 1rem;`;

                div.innerHTML = `
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-size: 1.1rem;">
                        ${name} ${dangerText}
                    </h4>
                    
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <span>Dose: ${daily_dose}/day</span>
                        <span style="float: right;">Est. ${daysLeft} days left</span>
                    </div>

                    <div style="width: 100%; height: 8px; background: rgba(0,0,0,0.5); border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="height: 100%; width: ${percentage}%; background: ${barColor}; transition: width 0.3s ease;"></div>
                    </div>
                    
                    <div style="font-size: 0.85rem; color: var(--text-primary); text-align: right; margin-bottom: 1rem;">
                        <strong>${current_stock}</strong> / ${total_capacity} pills
                    </div>

                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <button class="tab-btn take-dose-btn" data-id="${id}" data-dose="${daily_dose}" data-stock="${current_stock}"
                            style="flex: 1; margin: 0; padding: 0.3rem; background: rgba(56,189,248,0.1); border: 1px solid var(--accent-blue); color: var(--accent-blue); font-size: 0.8rem;">
                            Take Dose (-${daily_dose})
                        </button>
                        <button class="tab-btn refill-btn" data-id="${id}" data-cap="${total_capacity}"
                            style="flex: 1; margin: 0; padding: 0.3rem; background: rgba(251,191,36,0.1); border: 1px solid var(--accent-yellow); color: var(--accent-yellow); font-size: 0.8rem;">
                            Refill (Max)
                        </button>
                    </div>
                    <button class="tab-btn adjust-btn" data-id="${id}" data-stock="${current_stock}"
                        style="width: 100%; margin: 0; padding: 0.3rem; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-secondary); font-size: 0.8rem;">
                        ⚙️ Adjust Stock Manually
                    </button>
                `;
                grid.appendChild(div);
            });

            // Bind events
            document.querySelectorAll('.take-dose-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const dose = parseInt(e.target.getAttribute('data-dose'));
                    const stock = parseInt(e.target.getAttribute('data-stock'));
                    const newStock = Math.max(0, stock - dose);
                    updateSuppStock(id, newStock);
                });
            });

            document.querySelectorAll('.refill-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const cap = parseInt(e.target.getAttribute('data-cap'));
                    updateSuppStock(id, cap);
                });
            });

            document.querySelectorAll('.adjust-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const currentStock = e.target.getAttribute('data-stock');
                    const newStockStr = prompt(`Enter the new stock amount (Current: ${currentStock}):`, currentStock);
                    if (newStockStr !== null) {
                        const newStock = parseInt(newStockStr);
                        if (!isNaN(newStock) && newStock >= 0) {
                            updateSuppStock(id, newStock);
                        } else {
                            alert("Invalid number.");
                        }
                    }
                });
            });
        }

        addBtn.addEventListener('click', addSupp);

        // Init
        await fetchSupabaseInventory();
        renderGrid();
    }

    // --- Open Logistics Implementation ---
    async function initLogistics() {
        const container = document.getElementById('logistics-items-container');
        const addBtn = document.getElementById('add-logistics-btn');
        const titleInput = document.getElementById('logistics-title-input');
        if (!container || !addBtn) return;

        let items = []; // { id, title, status, subtasks: [{id, text, completed}] }
        let solvedItems = []; // Solved items log
        const LOCAL_KEY = 'symphony_logistics_local';
        const SOLVED_KEY = 'symphony_logistics_solved';
        const solvedList = document.getElementById('logistics-solved-list');
        const solvedCount = document.getElementById('logistics-solved-count');

        // Try Supabase first, fallback to localStorage (safe: won't clobber local data)
        async function fetchItems() {
            try {
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics?status=eq.open&order=created_at.desc`, {
                    headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
                });
                if (resp.ok) {
                    const data = await resp.json();
                    // Fetch subtasks for all items
                    const stResp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics_subtasks?order=created_at.asc`, {
                        headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
                    });
                    const subtasks = stResp.ok ? await stResp.json() : [];
                    const mergedItems = data.map(item => ({
                        ...item,
                        subtasks: subtasks.filter(st => st.logistics_id === item.id)
                    }));

                    const localData = localStorage.getItem(LOCAL_KEY);
                    const localItems = localData ? JSON.parse(localData) : [];
                    if (mergedItems.length > 0) {
                        items = mergedItems;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                    } else if (localItems.length > 0) {
                        items = localItems;
                        console.info('Logistics: Supabase empty, keeping local data');
                    } else {
                        items = [];
                    }

                    // Also fetch solved items for the log
                    try {
                        const solvedResp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics?status=eq.done&order=updated_at.desc`, {
                            headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
                        });
                        if (solvedResp.ok) {
                            const solvedData = await solvedResp.json();
                            solvedItems = solvedData.map(item => ({
                                ...item,
                                subtasks: subtasks.filter(st => st.logistics_id === item.id)
                            }));
                            localStorage.setItem(SOLVED_KEY, JSON.stringify(solvedItems));
                        }
                    } catch (e) { /* solved fetch optional */ }
                    return;
                }
            } catch (e) {
                console.warn('Logistics: Supabase unavailable, using localStorage', e);
            }
            // Fallback
            const local = localStorage.getItem(LOCAL_KEY);
            items = local ? JSON.parse(local) : [];
            const localSolved = localStorage.getItem(SOLVED_KEY);
            solvedItems = localSolved ? JSON.parse(localSolved) : [];
        }

        function saveLocal() {
            localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
            localStorage.setItem(SOLVED_KEY, JSON.stringify(solvedItems));
        }

        // Add new item
        async function addItem() {
            const title = titleInput.value.trim();
            if (!title) return;

            const newItem = {
                id: crypto.randomUUID(),
                title,
                status: 'open',
                created_at: new Date().toISOString(),
                subtasks: []
            };

            items.unshift(newItem);
            saveLocal();
            renderItems();
            titleInput.value = '';

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ id: newItem.id, title: newItem.title, status: 'open' })
                });
            } catch (e) { console.warn('Failed to save item to Supabase:', e); }
        }

        // Add sub-task
        async function addSubtask(itemId, text) {
            const item = items.find(i => i.id === itemId);
            if (!item || !text.trim()) return;

            const st = { id: crypto.randomUUID(), logistics_id: itemId, text: text.trim(), completed: false };
            item.subtasks.push(st);
            saveLocal();
            renderItems();

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics_subtasks`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify(st)
                });
            } catch (e) { console.warn('Failed to save subtask to Supabase:', e); }
        }

        // Toggle sub-task completion
        async function toggleSubtask(itemId, subtaskId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;
            const st = item.subtasks.find(s => s.id === subtaskId);
            if (!st) return;

            st.completed = !st.completed;
            saveLocal();
            renderItems();

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics_subtasks?id=eq.${subtaskId}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ completed: st.completed })
                });
            } catch (e) { console.warn('Failed to update subtask:', e); }
        }

        // Mark item as done → move to solved log
        async function markDone(itemId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;

            item.status = 'done';
            item.solved_at = new Date().toISOString();
            solvedItems.unshift(item);
            items = items.filter(i => i.id !== itemId);
            saveLocal();
            renderItems();
            renderSolvedLog();

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics?id=eq.${itemId}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ status: 'done', updated_at: new Date().toISOString() })
                });
            } catch (e) { console.warn('Failed to mark done in Supabase:', e); }
        }

        // Re-open a solved item
        async function reopenItem(itemId) {
            const item = solvedItems.find(i => i.id === itemId);
            if (!item) return;

            item.status = 'open';
            delete item.solved_at;
            items.unshift(item);
            solvedItems = solvedItems.filter(i => i.id !== itemId);
            saveLocal();
            renderItems();
            renderSolvedLog();

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics?id=eq.${itemId}`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ status: 'open', updated_at: new Date().toISOString() })
                });
            } catch (e) { console.warn('Failed to reopen in Supabase:', e); }
        }

        // Render Solved Log
        function renderSolvedLog() {
            if (!solvedList || !solvedCount) return;
            solvedCount.textContent = `(${solvedItems.length} item${solvedItems.length !== 1 ? 's' : ''})`;

            if (solvedItems.length === 0) {
                solvedList.innerHTML = '<div style="color: var(--text-secondary); font-size: 0.85rem; padding: 0.5rem;">No solved items yet.</div>';
                return;
            }

            solvedList.innerHTML = solvedItems.map(item => {
                const solvedDate = item.solved_at ? new Date(item.solved_at).toLocaleDateString('en-NZ', { day: 'numeric', month: 'short' }) : '';
                return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.75rem; background: rgba(0,0,0,0.15); border: 1px solid rgba(34,197,94,0.15); border-radius: 6px;">
                    <div style="flex: 1;">
                        <span style="color: var(--text-secondary); text-decoration: line-through; font-size: 0.9rem;">✅ ${item.title}</span>
                        ${solvedDate ? `<span style="font-size: 0.7rem; color: var(--text-secondary); margin-left: 0.5rem; opacity: 0.6;">${solvedDate}</span>` : ''}
                    </div>
                    <button class="logistics-reopen-btn" data-id="${item.id}"
                        style="background: rgba(251,191,36,0.15); border: 1px solid var(--accent-yellow); color: var(--accent-yellow); padding: 0.2rem 0.6rem; border-radius: 4px; font-family: 'VT323', monospace; font-size: 0.8rem; cursor: pointer; white-space: nowrap;"
                        title="Move back to active items">
                        ↩️ Re-open
                    </button>
                </div>`;
            }).join('');

            // Bind reopen buttons
            solvedList.querySelectorAll('.logistics-reopen-btn').forEach(btn => {
                btn.addEventListener('click', () => reopenItem(btn.dataset.id));
            });
        }

        // Delete sub-task
        async function deleteSubtask(itemId, subtaskId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;
            item.subtasks = item.subtasks.filter(s => s.id !== subtaskId);
            saveLocal();
            renderItems();

            try {
                await fetch(`${SUPABASE_URL}/rest/v1/symphony_logistics_subtasks?id=eq.${subtaskId}`, {
                    method: 'DELETE',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Prefer': 'return=minimal'
                    }
                });
            } catch (e) { console.warn('Failed to delete subtask:', e); }
        }

        // Render
        function renderItems() {
            if (items.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                        <div style="font-size: 1.1rem;">Nothing to solve right now!</div>
                        <div style="font-size: 0.85rem; margin-top: 0.5rem;">Add a logistics item above when something comes up.</div>
                    </div>`;
                return;
            }

            container.innerHTML = items.map(item => {
                const completedCount = item.subtasks.filter(s => s.completed).length;
                const totalCount = item.subtasks.length;
                const progressText = totalCount > 0 ? `${completedCount}/${totalCount} steps` : 'No steps yet';
                const progressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
                const barColor = progressPct === 100 ? 'var(--accent-green)' : 'var(--accent-blue)';

                return `
                <div class="glass-panel" style="border-color: var(--accent-blue); padding: 1.25rem; position: relative;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary); font-size: 1.15rem; line-height: 1.3;">
                                🔧 ${item.title}
                            </h4>
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                ${progressText}
                            </div>
                        </div>
                        <button class="logistics-done-btn" data-id="${item.id}"
                            style="background: rgba(34,197,94,0.15); border: 1px solid var(--accent-green); color: var(--accent-green); padding: 0.25rem 0.75rem; border-radius: 4px; font-family: 'VT323', monospace; font-size: 0.85rem; cursor: pointer; white-space: nowrap;">
                            ✅ Solved
                        </button>
                    </div>

                    <!-- Progress bar -->
                    ${totalCount > 0 ? `
                    <div style="width: 100%; height: 4px; background: rgba(0,0,0,0.4); border-radius: 2px; margin-bottom: 1rem; overflow: hidden;">
                        <div style="height: 100%; width: ${progressPct}%; background: ${barColor}; transition: width 0.3s ease;"></div>
                    </div>` : ''}

                    <!-- Sub-tasks list -->
                    <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.75rem;">
                        ${item.subtasks.map(st => `
                        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.5rem; background: rgba(0,0,0,0.2); border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">
                            <input type="checkbox" class="logistics-st-check" data-item="${item.id}" data-st="${st.id}"
                                ${st.completed ? 'checked' : ''}
                                style="cursor: pointer; accent-color: var(--accent-blue); width: 16px; height: 16px;">
                            <span style="flex: 1; font-size: 0.9rem; color: ${st.completed ? 'var(--text-secondary)' : 'var(--text-primary)'}; ${st.completed ? 'text-decoration: line-through;' : ''}">${st.text}</span>
                            <button class="logistics-st-del" data-item="${item.id}" data-st="${st.id}"
                                style="background: none; border: none; color: var(--accent-red); cursor: pointer; font-size: 0.9rem; padding: 0 4px; opacity: 0.6;"
                                title="Remove">×</button>
                        </div>`).join('')}
                    </div>

                    <!-- Add sub-task input -->
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" class="logistics-st-input" data-item="${item.id}"
                            placeholder="Add a step..."
                            style="flex: 1; padding: 0.4rem 0.6rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: 'VT323', monospace; font-size: 0.9rem; border-radius: 4px;">
                        <button class="logistics-st-add" data-item="${item.id}"
                            style="padding: 0.4rem 0.75rem; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); color: var(--accent-blue); font-family: 'VT323', monospace; font-size: 0.85rem; cursor: pointer; border-radius: 4px; white-space: nowrap;">+ Step</button>
                    </div>
                </div>`;
            }).join('');

            // Bind events
            container.querySelectorAll('.logistics-done-btn').forEach(btn => {
                btn.addEventListener('click', () => markDone(btn.dataset.id));
            });

            container.querySelectorAll('.logistics-st-check').forEach(cb => {
                cb.addEventListener('change', () => toggleSubtask(cb.dataset.item, cb.dataset.st));
            });

            container.querySelectorAll('.logistics-st-del').forEach(btn => {
                btn.addEventListener('click', () => deleteSubtask(btn.dataset.item, btn.dataset.st));
            });

            container.querySelectorAll('.logistics-st-add').forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = container.querySelector(`.logistics-st-input[data-item="${btn.dataset.item}"]`);
                    if (input && input.value.trim()) {
                        addSubtask(btn.dataset.item, input.value);
                        input.value = '';
                    }
                });
            });

            // Allow Enter key to add sub-tasks
            container.querySelectorAll('.logistics-st-input').forEach(input => {
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && input.value.trim()) {
                        addSubtask(input.dataset.item, input.value);
                        input.value = '';
                    }
                });
            });
        }

        // Event handlers
        addBtn.addEventListener('click', addItem);
        titleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') addItem();
        });

        // Init
        await fetchItems();
        renderItems();
        renderSolvedLog();
    }

    // populateWorkout();
    initFoodAnalytics();
    initBioTracking();
    initProcurement();
    initLogistics();
    initSuppsVault();

    // --- Calendar Event System ---
    async function initCalendar() {
        let calEvents = [];
        let calViewMonth = new Date().getMonth();
        let calViewYear = new Date().getFullYear();

        const colorMap = {
            'RED': '#ff0000', 'ORANGE': '#ff8c00', 'GREEN': '#008000',
            'BLUE': '#0000ff', 'PURPLE': '#800080'
        };
        const categoryEmoji = {
            'birthday': '🎂', 'appointment': '📋', 'deadline': '⏰',
            'reminder': '🔔', 'other': '📌'
        };
        const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

        // Fetch events from Supabase
        async function fetchEvents() {
            try {
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_events?order=event_date.asc`, {
                    headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
                });
                if (resp.ok) {
                    calEvents = await resp.json();
                    localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                    return;
                }
            } catch (e) {
                console.warn('Calendar: Supabase unavailable, using localStorage', e);
            }
            const local = localStorage.getItem('symphony_events_local');
            calEvents = local ? JSON.parse(local) : [];
        }

        // Check if an event occurs on a given date (considering recurrence)
        function eventOccursOn(event, date) {
            const evDate = new Date(event.event_date + 'T00:00:00');
            const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            if (event.recurrence === 'once') {
                return evDate.getTime() === d.getTime();
            }
            if (event.recurrence === 'yearly') {
                return evDate.getMonth() === d.getMonth() && evDate.getDate() === d.getDate();
            }
            if (event.recurrence === 'monthly') {
                return evDate.getDate() === d.getDate() && d >= evDate;
            }
            if (event.recurrence === 'weekly') {
                return evDate.getDay() === d.getDay() && d >= evDate;
            }
            return false;
        }

        // Get events for a specific date
        function getEventsForDate(date) {
            return calEvents.filter(ev => eventOccursOn(ev, date));
        }

        // Render the week view (Mon-Sun of current week)
        function renderWeekView() {
            const container = document.getElementById('calendar-week-view');
            if (!container) return;

            const today = new Date();
            const dayOfWeek = today.getDay(); // 0=Sun, 1=Mon...
            const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
            const monday = new Date(today);
            monday.setDate(today.getDate() + mondayOffset);

            let html = '';
            for (let i = 0; i < 7; i++) {
                const d = new Date(monday);
                d.setDate(monday.getDate() + i);
                const isToday = d.toDateString() === today.toDateString();
                const eventsOnDay = getEventsForDate(d);

                html += `<div class="week-day-row ${isToday ? 'is-today' : ''}">
                    <div class="week-day-label">
                        ${dayNames[i]}
                        <span class="week-date">${d.getDate()}/${d.getMonth() + 1}</span>
                    </div>
                    <div style="flex: 1;">
                        ${eventsOnDay.length === 0
                        ? '<span style="color: #999; font-size: 0.85rem;">—</span>'
                        : eventsOnDay.map(ev =>
                            `<div class="week-event-item">
                                    <span class="cal-event-dot color-${ev.color}"></span>
                                    <span>${categoryEmoji[ev.category] || '📌'} ${ev.title}</span>
                                    ${ev.time_of_day ? `<span style="color:#666; font-size:0.8rem;">${ev.time_of_day}</span>` : ''}
                                    <span class="recurrence-badge">${ev.recurrence}</span>
                                </div>`
                        ).join('')
                    }
                    </div>
                </div>`;
            }
            container.innerHTML = html;
        }

        // Render the month calendar grid
        function renderMonthGrid() {
            const grid = document.getElementById('calendar-month-grid');
            const title = document.getElementById('calendar-month-title');
            if (!grid) return;

            if (title) title.textContent = `${monthNames[calViewMonth]} ${calViewYear}`;

            const today = new Date();
            const firstDay = new Date(calViewYear, calViewMonth, 1);
            const lastDay = new Date(calViewYear, calViewMonth + 1, 0);

            // Adjust so Monday = 0
            let startDow = firstDay.getDay() - 1;
            if (startDow < 0) startDow = 6;

            let html = '<div class="cal-grid">';
            // Header row
            dayNames.forEach(d => { html += `<div class="cal-header-cell">${d}</div>`; });

            // Previous month padding
            const prevMonthLast = new Date(calViewYear, calViewMonth, 0);
            for (let i = startDow - 1; i >= 0; i--) {
                const dayNum = prevMonthLast.getDate() - i;
                html += `<div class="cal-day other-month"><span class="cal-day-num">${dayNum}</span></div>`;
            }

            // Current month days
            for (let day = 1; day <= lastDay.getDate(); day++) {
                const d = new Date(calViewYear, calViewMonth, day);
                const isToday = d.toDateString() === today.toDateString();
                const eventsOnDay = getEventsForDate(d);

                html += `<div class="cal-day ${isToday ? 'today' : ''}">
                    <span class="cal-day-num">${day}</span>
                    <div>${eventsOnDay.map(ev =>
                    `<span class="cal-event-dot color-${ev.color}" title="${ev.title}"></span>`
                ).join('')}</div>
                </div>`;
            }

            // Next month padding (fill to 42 cells = 6 rows)
            const totalCells = startDow + lastDay.getDate();
            const remaining = (7 - (totalCells % 7)) % 7;
            for (let i = 1; i <= remaining; i++) {
                html += `<div class="cal-day other-month"><span class="cal-day-num">${i}</span></div>`;
            }

            html += '</div>';
            grid.innerHTML = html;
        }

        // Render all events list (editable)
        function renderAllEventsList() {
            const list = document.getElementById('all-events-list');
            if (!list) return;

            if (calEvents.length === 0) {
                list.innerHTML = '<div style="color: #808080; font-style: italic; padding: 0.5rem;">No events yet. Add one above!</div>';
                return;
            }

            list.innerHTML = calEvents.map(ev => {
                const dateStr = new Date(ev.event_date + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
                return `<div class="event-list-item">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span class="cal-event-dot color-${ev.color}" style="width:8px;height:8px;"></span>
                        <span>${categoryEmoji[ev.category] || '📌'} <strong>${ev.title}</strong></span>
                        <span class="recurrence-badge">${ev.recurrence}</span>
                        <span style="color: #666;">${dateStr}</span>
                        ${ev.time_of_day ? `<span style="color: #0000ff;">${ev.time_of_day}</span>` : ''}
                    </div>
                    <button class="event-delete-btn" data-event-id="${ev.id}">×</button>
                </div>`;
            }).join('');

            // Attach delete handlers
            list.querySelectorAll('.event-delete-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.dataset.eventId;
                    calEvents = calEvents.filter(e => e.id !== id);
                    localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                    renderAll();
                    try {
                        await fetch(`${SUPABASE_URL}/rest/v1/symphony_events?id=eq.${id}`, {
                            method: 'DELETE',
                            headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
                        });
                    } catch (e) { console.warn('Failed to delete event from Supabase:', e); }
                });
            });
        }

        // Render "Coming Up This Week" on Today's Schedule
        function renderComingUpThisWeek() {
            const container = document.getElementById('coming-up-this-week');
            if (!container) return;

            const today = new Date();
            const dayOfWeek = today.getDay();
            const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
            const monday = new Date(today);
            monday.setDate(today.getDate() + mondayOffset);
            const sunday = new Date(monday);
            sunday.setDate(monday.getDate() + 6);

            // Collect events for this week
            const weekEvents = [];
            for (let i = 0; i < 7; i++) {
                const d = new Date(monday);
                d.setDate(monday.getDate() + i);
                const evs = getEventsForDate(d);
                evs.forEach(ev => {
                    weekEvents.push({ ...ev, displayDate: new Date(d) });
                });
            }

            if (weekEvents.length === 0) {
                container.innerHTML = '<div style="color: #008000; font-size: 0.95rem;">✅ No events this week — smooth sailing!</div>';
                return;
            }

            container.innerHTML = weekEvents.map(ev => {
                const dName = dayNames[(ev.displayDate.getDay() + 6) % 7]; // Mon=0
                const isPast = ev.displayDate < today && ev.displayDate.toDateString() !== today.toDateString();
                return `<div class="coming-up-event" style="border-left: 4px solid ${colorMap[ev.color] || '#0000ff'}; ${isPast ? 'opacity: 0.5;' : ''}">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-weight: bold; color: #000080; min-width: 30px;">${dName}</span>
                        <span>${categoryEmoji[ev.category] || '📌'} ${ev.title}</span>
                        ${ev.time_of_day ? `<span style="color: #0000ff; font-size: 0.85rem;">${ev.time_of_day}</span>` : ''}
                        <span class="recurrence-badge">${ev.recurrence}</span>
                    </div>
                </div>`;
            }).join('');
        }

        function renderAll() {
            renderWeekView();
            renderMonthGrid();
            renderAllEventsList();
            renderComingUpThisWeek();
        }

        // Add event handler
        const addBtn = document.getElementById('add-event-btn');
        if (addBtn) {
            addBtn.addEventListener('click', async () => {
                const title = document.getElementById('event-title')?.value.trim();
                const eventDate = document.getElementById('event-date')?.value;
                const timeOfDay = document.getElementById('event-time')?.value || null;
                const recurrence = document.getElementById('event-recurrence')?.value || 'once';
                const color = document.getElementById('event-color')?.value || 'BLUE';
                const category = document.getElementById('event-category')?.value || 'other';

                if (!title || !eventDate) {
                    alert('Please enter a title and date.');
                    return;
                }

                addBtn.innerText = '⏳';
                addBtn.style.pointerEvents = 'none';

                const newEvent = {
                    id: crypto.randomUUID(),
                    title, event_date: eventDate, recurrence, color, category,
                    time_of_day: timeOfDay || null
                };

                calEvents.push(newEvent);
                localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                renderAll();

                // Clear form
                document.getElementById('event-title').value = '';
                document.getElementById('event-date').value = '';
                document.getElementById('event-time').value = '';

                try {
                    await fetch(`${SUPABASE_URL}/rest/v1/symphony_events`, {
                        method: 'POST',
                        headers: {
                            'apikey': SUPABASE_ANON_KEY,
                            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                            'Content-Type': 'application/json',
                            'Prefer': 'return=minimal'
                        },
                        body: JSON.stringify({
                            id: newEvent.id, title, event_date: eventDate,
                            recurrence, color, category,
                            time_of_day: timeOfDay || null
                        })
                    });
                } catch (e) { console.warn('Failed to save event to Supabase:', e); }

                addBtn.innerText = 'Add Event';
                addBtn.style.pointerEvents = 'auto';
            });
        }

        // Month navigation
        const prevBtn = document.getElementById('cal-prev-month');
        const nextBtn = document.getElementById('cal-next-month');
        if (prevBtn) prevBtn.addEventListener('click', () => {
            calViewMonth--;
            if (calViewMonth < 0) { calViewMonth = 11; calViewYear--; }
            renderMonthGrid();
        });
        if (nextBtn) nextBtn.addEventListener('click', () => {
            calViewMonth++;
            if (calViewMonth > 11) { calViewMonth = 0; calViewYear++; }
            renderMonthGrid();
        });

        // Initial load
        await fetchEvents();
        renderAll();
    }
    initCalendar();

    async function initExpensesTracker() {
        const listEl = document.getElementById('expenses-list');
        const addBtn = document.getElementById('add-expense-btn');
        if (!listEl || !addBtn) return;

        let expenses = [];
        const LOCAL_KEY = 'symphony_expenses_local';

        // Normalize any frequency to weekly amount
        function toWeekly(amount, frequency) {
            switch (frequency) {
                case 'weekly': return amount;
                case 'fortnightly': return amount / 2;
                case 'monthly': return (amount * 12) / 52;
                case 'yearly': return amount / 52;
                default: return amount;
            }
        }

        function freqLabel(f) {
            return { weekly: '/wk', fortnightly: '/fn', monthly: '/mo', yearly: '/yr' }[f] || '';
        }

        // Fetch from Supabase
        async function fetchExpenses() {
            try {
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_expenses?order=category.asc,name.asc`, {
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                    }
                });
                if (resp.ok) {
                    const supabaseData = await resp.json();
                    const localData = localStorage.getItem(LOCAL_KEY);
                    const localItems = localData ? JSON.parse(localData) : [];

                    if (supabaseData.length > 0) {
                        // Supabase has data — use it as source of truth
                        expenses = supabaseData;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
                    } else if (localItems.length > 0) {
                        // Supabase is empty but localStorage has items — sync UP
                        expenses = localItems;
                        console.info('Expenses: Supabase empty, syncing local items up...');
                        for (const item of localItems) {
                            if (!item.id) {
                                try {
                                    await fetch(`${SUPABASE_URL}/rest/v1/symphony_expenses`, {
                                        method: 'POST',
                                        headers: {
                                            'apikey': SUPABASE_ANON_KEY,
                                            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                                            'Content-Type': 'application/json',
                                            'Prefer': 'return=minimal'
                                        },
                                        body: JSON.stringify({ name: item.name, amount: item.amount, frequency: item.frequency, category: item.category })
                                    });
                                } catch (e) { /* best-effort sync */ }
                            }
                        }
                    } else {
                        expenses = [];
                    }
                } else {
                    throw new Error(`HTTP ${resp.status}`);
                }
            } catch (e) {
                console.warn('Expenses: Supabase fetch failed, using localStorage:', e);
                const local = localStorage.getItem(LOCAL_KEY);
                if (local) expenses = JSON.parse(local);
            }
        }

        function renderExpenses() {
            listEl.innerHTML = '';
            if (expenses.length === 0) {
                listEl.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.85rem; padding: 0.5rem 0;">No expenses added yet. Add your bills above.</div>';
                updateBudgetSummary();
                return;
            }

            // Group by category
            const essential = expenses.filter(e => e.category === 'essential');
            const flexible = expenses.filter(e => e.category === 'flexible');

            const renderGroup = (items, label, color) => {
                if (items.length === 0) return;
                const header = document.createElement('div');
                header.style.cssText = `font-size: 0.75rem; color: ${color}; text-transform: uppercase; font-weight: 700; padding: 0.25rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 0.25rem;`;
                header.textContent = label;
                listEl.appendChild(header);

                items.forEach(exp => {
                    const weeklyAmt = toWeekly(parseFloat(exp.amount), exp.frequency);
                    const row = document.createElement('div');
                    row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.85rem;';
                    row.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: var(--text-primary);">${exp.name}</span>
                            <span style="font-size: 0.7rem; color: var(--text-secondary);">$${parseFloat(exp.amount).toFixed(2)}${freqLabel(exp.frequency)}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: ${color}; font-weight: 600;">$${weeklyAmt.toFixed(2)}/wk</span>
                            <button class="delete-expense-btn" data-id="${exp.id}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                        </div>
                    `;
                    listEl.appendChild(row);
                });
            };

            renderGroup(essential, '🛡️ Essential', '#ef4444');
            renderGroup(flexible, '🎮 Flexible', 'var(--accent-yellow)');

            // Bind delete buttons
            listEl.querySelectorAll('.delete-expense-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    expenses = expenses.filter(e => e.id !== id);
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
                    renderExpenses();
                    // Delete from Supabase
                    try {
                        await fetch(`${SUPABASE_URL}/rest/v1/symphony_expenses?id=eq.${id}`, {
                            method: 'DELETE',
                            headers: {
                                'apikey': SUPABASE_ANON_KEY,
                                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                            }
                        });
                    } catch (e) { console.warn('Failed to delete expense from Supabase:', e); }
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });

            updateBudgetSummary();
        }

        function updateBudgetSummary() {
            const netPay = window.currentNetWeekly || 0;
            const formatCurrency = (num) => '$' + Math.abs(num).toFixed(2);

            let essentialTotal = 0;
            let flexibleTotal = 0;
            expenses.forEach(exp => {
                const weekly = toWeekly(parseFloat(exp.amount), exp.frequency);
                if (exp.category === 'essential') essentialTotal += weekly;
                else flexibleTotal += weekly;
            });

            const totalExpenses = essentialTotal + flexibleTotal;
            const disposable = netPay - totalExpenses;

            const netPayEl = document.getElementById('budget-net-pay');
            const essentialEl = document.getElementById('budget-essential-total');
            const flexibleEl = document.getElementById('budget-flexible-total');
            const totalEl = document.getElementById('budget-expenses-total');
            const disposableEl = document.getElementById('budget-disposable');
            const dailyEl = document.getElementById('budget-disposable-daily');

            if (netPayEl) netPayEl.innerText = formatCurrency(netPay);
            if (essentialEl) essentialEl.innerText = '-' + formatCurrency(essentialTotal);
            if (flexibleEl) flexibleEl.innerText = '-' + formatCurrency(flexibleTotal);
            if (totalEl) totalEl.innerText = '-' + formatCurrency(totalExpenses);

            if (disposableEl) {
                disposableEl.innerText = (disposable >= 0 ? '$' : '-$') + Math.abs(disposable).toFixed(2);
                disposableEl.style.color = disposable >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
            }
            if (dailyEl) {
                const daily = disposable / 7;
                dailyEl.innerText = `(${daily >= 0 ? '$' : '-$'}${Math.abs(daily).toFixed(2)} / day)`;
            }

            // Max Savings Potential (essentials-only baseline)
            const baselineNetWeekly = computeNZNetWeekly(24.00 * 28.5).netWeekly;
            const maxSavingsWeekly = baselineNetWeekly - essentialTotal;
            const maxSavingsYearly = maxSavingsWeekly * 52;

            const maxSavingsEl = document.getElementById('budget-max-savings');
            const maxSavingsWeeklyEl = document.getElementById('budget-max-savings-weekly');
            if (maxSavingsEl) {
                maxSavingsEl.innerText = (maxSavingsYearly >= 0 ? '$' : '-$') + Math.abs(Math.round(maxSavingsYearly)).toLocaleString();
                maxSavingsEl.style.color = maxSavingsYearly >= 0 ? 'var(--accent-blue)' : 'var(--accent-red)';
            }
            if (maxSavingsWeeklyEl) {
                maxSavingsWeeklyEl.innerText = `($${maxSavingsWeekly.toFixed(2)} / week)`;
            }

            const canvas = document.getElementById('budgetPieChart');
            if (canvas && (essentialTotal + flexibleTotal + Math.max(0, disposable)) > 0) {
                const ctx = canvas.getContext('2d');
                if (window.budgetChartInstance) window.budgetChartInstance.destroy();
                window.budgetChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Disposable', 'Essential', 'Flexible'],
                        datasets: [{
                            data: [Math.max(0, disposable), essentialTotal, flexibleTotal],
                            backgroundColor: [
                                'rgba(52, 211, 153, 0.8)',
                                'rgba(239, 68, 68, 0.8)',
                                'rgba(251, 191, 36, 0.8)'
                            ],
                            borderColor: 'rgba(15, 23, 42, 1)',
                            borderWidth: 2,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: { color: '#94a3b8', font: { size: 11 } }
                            }
                        },
                        cutout: '65%'
                    }
                });
            }
        }

        // Expose globally so calculateFinance can trigger it
        window.updateBudgetSummary = updateBudgetSummary;

        // Add expense handler
        addBtn.addEventListener('click', async () => {
            const nameEl = document.getElementById('expense-name-input');
            const amountEl = document.getElementById('expense-amount-input');
            const freqEl = document.getElementById('expense-freq-input');
            const catEl = document.getElementById('expense-cat-input');

            const name = nameEl.value.trim();
            const amount = parseFloat(amountEl.value);
            const frequency = freqEl.value;
            const category = catEl.value;

            if (!name || isNaN(amount) || amount <= 0) {
                alert('Please fill out expense name and a valid amount.');
                return;
            }

            const newExpense = { name, amount, frequency, category };

            // Optimistic local add
            expenses.push(newExpense);
            localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
            renderExpenses();

            nameEl.value = '';
            amountEl.value = '';

            // Persist to Supabase
            try {
                const resp = await fetch(`${SUPABASE_URL}/rest/v1/symphony_expenses`, {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=representation'
                    },
                    body: JSON.stringify(newExpense)
                });
                if (resp.ok) {
                    await fetchExpenses();
                    renderExpenses();
                }
            } catch (e) {
                console.warn('Failed to save expense to Supabase:', e);
            }

            if (typeof playRetroSuccess === 'function') playRetroSuccess();
        });

        // Init
        await fetchExpenses();
        renderExpenses();
    }

    initExpensesTracker();

    // --- Pulse Overview (At-a-Glance Command Center) ---
    function initPulse() {
        const pulseToday = document.getElementById('pulse-today-summary');
        const pulseLogistics = document.getElementById('pulse-logistics');
        const pulseSupps = document.getElementById('pulse-supps');
        const pulseMedical = document.getElementById('pulse-medical');
        const pulseFinance = document.getElementById('pulse-finance');
        if (!pulseToday) return;

        // 1. Today's progress — count checked items in the schedule
        try {
            const allCheckboxes = document.querySelectorAll('#today .task-list .checkbox, .supp-timing-body .checkbox');
            const checked = document.querySelectorAll('#today .task-list .checkbox.checked, .supp-timing-body .checkbox.checked');
            const totalTasks = allCheckboxes.length;
            const completedTasks = checked.length;
            const pct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

            pulseToday.innerHTML = `
                <div style="font-size: 2rem; font-weight: 700; color: var(--accent-green); margin-bottom: 0.25rem;">${pct}%</div>
                <div>${completedTasks} of ${totalTasks} tasks completed today</div>
                <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.4); border-radius: 3px; margin-top: 0.5rem; overflow: hidden;">
                    <div style="height: 100%; width: ${pct}%; background: var(--accent-green); transition: width 0.3s;"></div>
                </div>`;
        } catch (e) {
            pulseToday.innerHTML = '<div>Open Today\'s Schedule to see progress.</div>';
        }

        // 2. Open Logistics
        try {
            const logisticsLocal = localStorage.getItem('symphony_logistics_local');
            const logItems = logisticsLocal ? JSON.parse(logisticsLocal) : [];
            if (logItems.length === 0) {
                pulseLogistics.innerHTML = '<div style="color: var(--accent-green);">✅ Nothing to solve right now!</div>';
            } else {
                pulseLogistics.innerHTML = logItems.map(item => {
                    const stCount = item.subtasks ? item.subtasks.length : 0;
                    const stDone = item.subtasks ? item.subtasks.filter(s => s.completed).length : 0;
                    const badge = stCount > 0 ? ` <span style="color: var(--text-secondary); font-size: 0.75rem;">(${stDone}/${stCount} steps)</span>` : '';
                    return `<div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        🔧 ${item.title}${badge}
                    </div>`;
                }).join('');
            }
        } catch (e) {
            pulseLogistics.innerHTML = '<div>Could not load logistics.</div>';
        }

        // 3. Low Stock Supplements
        try {
            const suppLocal = localStorage.getItem('symphony_supp_inventory_local');
            const supps = suppLocal ? JSON.parse(suppLocal) : [];
            const lowStock = supps.filter(s => s.daily_dose > 0 && (s.current_stock / s.total_capacity) < 0.5);

            if (lowStock.length === 0 && supps.length > 0) {
                pulseSupps.innerHTML = '<div style="color: var(--accent-green);">✅ All supplements well-stocked.</div>';
            } else if (supps.length === 0) {
                pulseSupps.innerHTML = '<div>No supplements tracked yet. Add them in the Supps Vault.</div>';
            } else {
                pulseSupps.innerHTML = lowStock.map(s => {
                    const daysLeft = s.daily_dose > 0 ? Math.floor(s.current_stock / s.daily_dose) : '∞';
                    const pct = Math.round((s.current_stock / s.total_capacity) * 100);
                    const color = pct < 25 ? 'var(--accent-red)' : 'var(--accent-yellow)';
                    return `<div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
                        <span style="color: ${color};">⚠️ ${s.name}</span>
                        <span>${s.current_stock}/${s.total_capacity} (${daysLeft} days left)</span>
                    </div>`;
                }).join('');
            }
        } catch (e) {
            pulseSupps.innerHTML = '<div>Could not load supplement data.</div>';
        }

        // 4. Medical Flags (from static MEDICAL_ALERTS)
        try {
            pulseMedical.innerHTML = MEDICAL_ALERTS.map(alert => `
                <div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span style="color: var(--accent-red); font-weight: 600;">${alert.gene}</span>
                    <span style="color: var(--text-secondary); font-size: 0.8rem;"> — ${alert.risk}</span>
                </div>
            `).join('');
        } catch (e) {
            pulseMedical.innerHTML = '<div>No medical flags loaded.</div>';
        }

        // 5. Financial Snapshot
        try {
            const netPay = document.getElementById('finance-net-pay');
            const gross = document.getElementById('finance-gross');
            const hours = document.getElementById('finance-hours');
            if (netPay && gross && hours) {
                pulseFinance.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span>Est. Weekly Net:</span>
                        <span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-green);">${netPay.innerText}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.25rem;">
                        <span>Gross:</span><span>${gross.innerText}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.25rem;">
                        <span>Hours:</span><span>${hours.innerText}</span>
                    </div>`;
            } else {
                pulseFinance.innerHTML = '<div>Open the Finances tab to calculate.</div>';
            }
        } catch (e) {
            pulseFinance.innerHTML = '<div>Could not load financial data.</div>';
        }
    }

    // Run Pulse after a short delay so other modules populate first
    setTimeout(initPulse, 1500);

    // --- Dynamic Task Config Lock In ---
    const lockInBtn = document.getElementById('lock-in-config-btn');
    if (lockInBtn) {
        lockInBtn.addEventListener('click', async () => {
            lockInBtn.innerHTML = '<span class="icon">⏳</span> Locking...';
            lockInBtn.style.pointerEvents = 'none';

            // Re-render the configurator to move items to their new lists
            await initTaskConfigurator();
            if (typeof fetchSupabaseData === 'function') {
                await fetchSupabaseData();
            }

            lockInBtn.innerHTML = '<span class="icon">🔒</span> Lock In';
            lockInBtn.style.pointerEvents = 'auto';
        });
    }

    // --- Logic shifted to top of file ---

    // Trigger Supabase fetch
    fetchSupabaseData();
});
