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
    function calculateFinance() {
        // User Variables
        const baseHourlyRate = 24.00;
        const kiwiSaverRate = 0.03; // 3%

        const hoursInput = document.getElementById('input-hours');
        const holidayInput = document.getElementById('input-holiday');

        const hoursWorked = hoursInput ? parseFloat(hoursInput.value) || 0 : 28.5;
        const isHoliday = holidayInput ? holidayInput.classList.contains('checked') : false;

        const hourlyRate = isHoliday ? baseHourlyRate * 1.5 : baseHourlyRate;

        // Base Calculations
        const grossWeekly = hourlyRate * hoursWorked; // $684.00
        const annualizedGross = grossWeekly * 52;     // $35,568.00

        // 1. KiwiSaver (Calculated on Gross)
        const weeklyKiwiSaver = grossWeekly * kiwiSaverRate; // $20.52

        // 2. Student Loan (12% over $438/week threshold)
        const slThreshold = 438.00;
        let weeklyStudentLoan = 0;
        if (grossWeekly > slThreshold) {
            weeklyStudentLoan = (grossWeekly - slThreshold) * 0.12; // $29.52
        }

        // 3. PAYE Tax (M Tax Code Approximation for $35,568)
        let annualizedTax = 0;
        if (annualizedGross <= 15600) {
            annualizedTax = annualizedGross * 0.105;
        } else if (annualizedGross <= 53500) {
            annualizedTax = (15600 * 0.105) + ((annualizedGross - 15600) * 0.175);
        }

        const accLevy = annualizedGross * 0.0139;
        const weeklyPayeAndAcc = (annualizedTax + accLevy) / 52;

        // 4. Net Income
        const totalDeductions = weeklyPayeAndAcc + weeklyStudentLoan + weeklyKiwiSaver;
        const netWeekly = grossWeekly - totalDeductions;

        // Update DOM Elements
        const formatCurrency = (num) => '$' + num.toFixed(2);

        document.getElementById('finance-hours').innerText = hoursWorked + ' hrs';
        document.getElementById('finance-gross').innerText = formatCurrency(grossWeekly);
        document.getElementById('finance-tax').innerText = '-' + formatCurrency(weeklyPayeAndAcc);
        document.getElementById('finance-sl').innerText = '-' + formatCurrency(weeklyStudentLoan);
        document.getElementById('finance-ks').innerText = '-' + formatCurrency(weeklyKiwiSaver);
        document.getElementById('finance-net-pay').innerText = formatCurrency(netWeekly);

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
                    data: [netWeekly, weeklyPayeAndAcc, weeklyStudentLoan, weeklyKiwiSaver],
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
        // Clear all drop zones and accordion bodies
        document.querySelectorAll('.drop-zone').forEach(zone => zone.innerHTML = '');

        // Categorization helper: determine which pool a task belongs to
        function getPoolId(task) {
            const tt = (task.time_target || '').trim();

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

        // Adjust task duration by delta minutes, update local state and re-render
        function adjustTaskDuration(taskId, deltaMins) {
            const task = dynamicTasks.find(t => t.id === taskId);
            if (!task) return;
            const timing = parseTaskTiming(task.time_target);
            if (!timing) return;

            let newEndMins = timing.endMins + deltaMins;
            // Minimum duration: 15 minutes
            if (newEndMins - timing.startMins < 15) return;
            // Maximum: don't go past 11:30 PM (23:30 = 1410 mins)
            if (newEndMins > 1410) return;

            const newEndTime = minutesToTime(newEndMins);
            if (newEndMins - timing.startMins <= 30) {
                // Single slot — revert to simple format
                task.time_target = timing.startTime;
            } else {
                task.time_target = `${timing.startTime} - ${newEndTime}`;
            }
            renderDraggableTimeline();
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

            const isOnTimeline = (getPoolId(task) === 'timeline' || getPoolId(task) === 'timeline-span');
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
                    ${isOnTimeline ? `<button class="remove-timeline-btn" style="background: none; border: none; color: red; font-weight: bold; font-size: 1.1rem; cursor: pointer; padding: 0 4px;" title="Remove from schedule">×</button>` : ''}
                </div>
                ${task.description ? `<div class="task-desc" style="font-size: 0.8rem;">${task.description}</div>` : ''}
                <div style="margin-top: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.65rem; padding: 2px 6px;">${t}</span>`).join('')}
                    </div>
                    ${isOnTimeline ? `
                    <div class="duration-controls" style="display: flex; align-items: center; gap: 4px; font-size: 0.75rem;">
                        <button class="dur-minus" style="background: rgba(255,255,255,0.1); border: 1px solid var(--glass-border); color: var(--text-primary); width: 22px; height: 22px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.9rem; line-height: 1;">−</button>
                        <span class="dur-label" style="color: var(--accent-blue); font-weight: 600; min-width: 32px; text-align: center;">${durationLabel}</span>
                        <button class="dur-plus" style="background: rgba(255,255,255,0.1); border: 1px solid var(--glass-border); color: var(--text-primary); width: 22px; height: 22px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 0.9rem; line-height: 1;">+</button>
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

            // Attach remove timeline handler
            const removeBtn = el.querySelector('.remove-timeline-btn');
            if (removeBtn) {
                removeBtn.addEventListener('click', async (e) => {
                    e.stopPropagation(); // Prevent drag initialization
                    removeBtn.innerText = "⏳";
                    try {
                        const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?id=eq.${task.id}`, {
                            method: 'PATCH',
                            headers: {
                                'apikey': SUPABASE_ANON_KEY,
                                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                                'Content-Type': 'application/json',
                                'Prefer': 'return=minimal'
                            },
                            body: JSON.stringify({ time_target: 'Unscheduled' })
                        });

                        if (response.ok) {
                            // Update local task array and re-render without full fetch
                            const tIndex = dynamicTasks.findIndex(t => t.id === task.id);
                            if (tIndex > -1) {
                                dynamicTasks[tIndex].time_target = 'Unscheduled';
                            }
                            renderDraggableTimeline();
                        } else {
                            console.error("Failed to remove task from timeline", response.statusText);
                            alert("Failed to unschedule task");
                            removeBtn.innerText = "×";
                        }
                    } catch (err) {
                        console.error("Network error unscheduling task:", err);
                        alert("Network error. Try again.");
                        removeBtn.innerText = "×";
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

            // Route to the correct container
            const poolId = getPoolId(task);

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

        // Render Weekly/Monthly Tracker immediately after timeline is built
        renderWeeklyMonthlyTracker();

        // Setup drag-and-drop after rendering
        setupDragAndDropZones();
    }

    function setupDragAndDropZones() {
        const dropZones = document.querySelectorAll('.drop-zone');

        dropZones.forEach(zone => {
            // Clone to remove old listeners and prevent stacking
            const freshZone = zone.cloneNode(true);
            zone.parentNode.replaceChild(freshZone, zone);

            freshZone.addEventListener('dragover', e => {
                e.preventDefault();
                freshZone.classList.add('drag-over');
            });

            freshZone.addEventListener('dragleave', () => {
                freshZone.classList.remove('drag-over');
            });

            freshZone.addEventListener('drop', e => {
                e.preventDefault();
                freshZone.classList.remove('drag-over');

                const draggingEl = document.querySelector('.dragging');
                if (draggingEl && draggedTaskObj) {
                    draggedTaskObj.time_target = freshZone.dataset.time;
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
            // Handle both simple strings and objects with points
            const text = typeof itemObj === 'string' ? itemObj : itemObj.text;
            const pointsLabel = (typeof itemObj === 'object' && itemObj.points) ? ` <span style="font-size:0.8rem; color:var(--accent-blue);">[+${itemObj.points} pts]</span>` : '';

            const li = document.createElement('li');
            const isCompleted = savedListState[index];

            if (isCompleted) {
                li.classList.add('completed');
            }

            li.innerHTML = `
                <div class="checkbox ${isCompleted ? 'checked' : ''}"></div>
                <div class="task-content">${text}${pointsLabel}</div>
            `;

            li.querySelector('.checkbox').addEventListener('click', function () {
                this.classList.toggle('checked');
                const parent = this.parentElement;
                parent.classList.toggle('completed');

                // Save state
                savedListState[index] = this.classList.contains('checked');
                localStorage.setItem('symphony_list_state_' + containerId, JSON.stringify(savedListState));

                if (containerId === 'daily-list') updatePoints();
            });

            container.appendChild(li);
        });
    };

    // --- Ideas / Bucket List Setup ---
    function initIdeasPage() {
        const attachListListener = (inputId, btnId, listId, storageKey) => {
            const input = document.getElementById(inputId);
            const btn = document.getElementById(btnId);
            const list = document.getElementById(listId);

            if (!input || !btn || !list) return;

            // Load existing items from localStorage
            const loadItems = () => {
                const storedItems = JSON.parse(localStorage.getItem(storageKey) || '[]');
                list.innerHTML = ''; // Clear default hardcoded or current items
                storedItems.forEach((item, index) => {
                    const li = document.createElement('li');
                    if (item.completed) li.classList.add('completed');

                    li.innerHTML = `
                        <div class="checkbox ${item.completed ? 'checked' : ''}"></div>
                        <div class="task-content" style="flex-grow: 1;">${item.text}</div>
                        <button class="delete-btn" data-index="${index}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.2rem; margin-left: 10px;" title="Delete item">×</button>
                    `;

                    li.querySelector('.checkbox').addEventListener('click', function () {
                        this.classList.toggle('checked');
                        this.parentElement.classList.toggle('completed');
                        saveItems();
                    });

                    li.querySelector('.delete-btn').addEventListener('click', function () {
                        this.parentElement.remove();
                        saveItems();
                    });

                    list.appendChild(li);
                });
            };

            const saveItems = () => {
                const items = [];
                list.querySelectorAll('li').forEach(li => {
                    items.push({
                        text: li.querySelector('.task-content').innerText,
                        completed: li.classList.contains('completed')
                    });
                });
                localStorage.setItem(storageKey, JSON.stringify(items));
            };

            const handleAdd = () => {
                const text = input.value.trim();
                if (!text) return;

                const li = document.createElement('li');
                li.innerHTML = `
                    <div class="checkbox"></div>
                    <div class="task-content" style="flex-grow: 1;">${text}</div>
                    <button class="delete-btn" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.2rem; margin-left: 10px;" title="Delete item">×</button>
                `;

                li.querySelector('.checkbox').addEventListener('click', function () {
                    this.classList.toggle('checked');
                    this.parentElement.classList.toggle('completed');
                    saveItems();
                });

                li.querySelector('.delete-btn').addEventListener('click', function () {
                    this.parentElement.remove();
                    saveItems();
                });

                list.appendChild(li);
                input.value = '';
                saveItems();
            };

            btn.addEventListener('click', handleAdd);
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleAdd();
            });

            // Initialize by loading
            // If it's the first time and the list doesn't have local storage, populate heavily with default so it doesn't look empty
            if (!localStorage.getItem(storageKey) && listId === 'bucket-list') {
                localStorage.setItem(storageKey, JSON.stringify([{ text: "Walk the full Pineapple Track", completed: false }]));
            }

            loadItems();
        };

        attachListListener('quick-add-bucket', 'quick-add-bucket-btn', 'bucket-list', 'symphony_bucket_list');
        attachListListener('quick-add-braindump', 'quick-add-braindump-btn', 'braindump-list', 'symphony_brain_dump');
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

    // --- Food Analytics Integration ---
    // --- Food Metrics Engine ---
    const FOOD_LOG_KEY = `symphony_food_log_${new Date().toISOString().split('T')[0]}`;

    function getDailyFoodLog() {
        const stored = localStorage.getItem(FOOD_LOG_KEY);
        return stored ? JSON.parse(stored) : [];
    }

    function saveFoodLog(logArr) {
        localStorage.setItem(FOOD_LOG_KEY, JSON.stringify(logArr));
    }

    function calculateDailyTotals(logArr) {
        return logArr.reduce((totals, item) => {
            totals.calories += item.calories || 0;
            totals.protein += item.protein || 0;
            totals.carbs += item.carbs || 0;
            totals.fats += item.fats || 0;
            return totals;
        }, { calories: 0, protein: 0, carbs: 0, fats: 0 });
    }

    function renderFoodDashboard() {
        const log = getDailyFoodLog();
        const totals = calculateDailyTotals(log);

        // Update Dash Cards
        document.getElementById('food-dash-calories').innerText = totals.calories;
        document.getElementById('food-dash-protein').innerText = `${totals.protein}g`;
        document.getElementById('food-dash-carbs').innerText = `${totals.carbs}g`;
        document.getElementById('food-dash-fats').innerText = `${totals.fats}g`;

        // Update Macro Details
        const pEl = document.getElementById('food-protein');
        const cEl = document.getElementById('food-carbs');
        const fEl = document.getElementById('food-fats');
        if (pEl) pEl.innerText = `${totals.protein}g`;
        if (cEl) cEl.innerText = `${totals.carbs}g`;
        if (fEl) fEl.innerText = `${totals.fats}g`;

        // Update Chart
        const canvas = document.getElementById('foodMacroChart');
        if (canvas && totals.protein + totals.carbs + totals.fats > 0) {
            const ctx = canvas.getContext('2d');
            if (window.foodChartInstance) {
                window.foodChartInstance.destroy();
            }

            window.foodChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Protein', 'Carbs', 'Fats'],
                    datasets: [{
                        data: [totals.protein, totals.carbs, totals.fats],
                        backgroundColor: [
                            'rgba(56, 189, 248, 0.8)', // Blue (Protein)
                            'rgba(251, 191, 36, 0.8)', // Yellow (Carbs)
                            'rgba(239, 68, 68, 0.8)'   // Red (Fats)
                        ],
                        borderColor: 'rgba(15, 23, 42, 1)',
                        borderWidth: 2,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    cutout: '65%'
                }
            });
        }

        // Render Log List
        const listEl = document.getElementById('food-log-list');
        if (listEl) {
            listEl.innerHTML = '';
            log.forEach((item, index) => {
                const li = document.createElement('li');
                li.style.flexDirection = 'column';
                li.style.alignItems = 'flex-start';

                li.innerHTML = `
                    <div style="display: flex; justify-content: space-between; width: 100%; cursor: pointer;" onclick="document.getElementById('food-details-${index}').style.display = document.getElementById('food-details-${index}').style.display === 'none' ? 'block' : 'none'">
                        <div>
                            <span style="font-size: 0.8rem; color: var(--text-secondary); margin-right: 0.5rem;">${item.timestamp}</span>
                            <strong style="color: var(--text-primary);">${item.name}</strong>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-secondary);">
                            ${item.calories} kcal | ${item.protein}P ${item.carbs}C ${item.fats}F
                        </div>
                    </div>
                    <div id="food-details-${index}" style="display: none; width: 100%; margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px dashed var(--glass-border); font-size: 0.8rem; color: var(--text-secondary);">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                            <span>Sugars: ${item.sugars}g</span>
                            <span>Fiber: ${item.fiber}g</span>
                            <span>Sodium: ${item.sodium}g</span>
                        </div>
                        <div style="margin-top: 0.5rem; font-style: italic;">
                            ${item.ingredients ? item.ingredients.substring(0, 100) + '...' : 'Ingredients not available.'}
                        </div>
                        <button class="delete-food-btn" data-index="${index}" style="margin-top: 0.5rem; background: transparent; border: 1px solid var(--accent-red); color: var(--accent-red); padding: 2px 8px; border-radius: 4px; cursor: pointer;">Remove</button>
                    </div>
                `;
                listEl.appendChild(li);
            });

            // Bind delete buttons
            document.querySelectorAll('.delete-food-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const idx = parseInt(e.target.getAttribute('data-index'));
                    let currentLog = getDailyFoodLog();
                    currentLog.splice(idx, 1);
                    saveFoodLog(currentLog);
                    renderFoodDashboard();
                });
            });
        }
    }

    function initFoodAnalytics() {
        renderFoodDashboard();

        const searchInput = document.getElementById('food-search-input');
        const resultsContainer = document.getElementById('food-autocomplete-results');
        let searchTimeout;

        if (searchInput && resultsContainer) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();

                if (query.length < 3) {
                    resultsContainer.style.display = 'none';
                    return;
                }

                searchTimeout = setTimeout(async () => {
                    resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: #94a3b8; font-size: 0.85rem;">Searching Open Food Facts API...</div>';
                    resultsContainer.style.display = 'block';

                    try {
                        const response = await fetch(`https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=8`);
                        const data = await response.json();

                        resultsContainer.innerHTML = '';
                        if (data.products && data.products.length > 0) {
                            data.products.forEach(product => {
                                // Skip items without caloric info to keep dash clean
                                if (!product.nutriments || !product.nutriments['energy-kcal_100g'] && !product.nutriments['energy-kcal']) return;

                                const n = product.nutriments;
                                const cals = Math.round(n['energy-kcal_100g'] || n['energy-kcal'] || 0);
                                const pro = Math.round(n['proteins_100g'] || n.proteins || 0);
                                const car = Math.round(n['carbohydrates_100g'] || n.carbohydrates || 0);
                                const fat = Math.round(n['fat_100g'] || n.fat || 0);

                                const desc = product.product_name || 'Unknown Product';
                                const brand = product.brands || '';

                                const resDiv = document.createElement('div');
                                resDiv.style.padding = '0.75rem';
                                resDiv.style.borderBottom = '1px solid var(--glass-border)';
                                resDiv.style.cursor = 'pointer';
                                resDiv.className = 'food-result-item';

                                resDiv.innerHTML = `
                                    <div style="font-weight: 600; color: #f1f5f9;">${desc} <span style="font-size: 0.75rem; color: #94a3b8;">${brand}</span></div>
                                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem;">
                                        100g/ml: ${cals} kcal | ${pro}P ${car}C ${fat}F
                                    </div>
                                `;

                                resDiv.addEventListener('click', () => {
                                    // Log the item
                                    const logEntry = {
                                        name: desc,
                                        calories: cals,
                                        protein: pro,
                                        carbs: car,
                                        fats: fat,
                                        sugars: Math.round(n['sugars_100g'] || n.sugars || 0),
                                        fiber: Math.round(n['fiber_100g'] || n.fiber || 0),
                                        sodium: Math.round(n['sodium_100g'] || n.sodium || 0),
                                        ingredients: product.ingredients_text || '',
                                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                    };

                                    const currentLog = getDailyFoodLog();
                                    currentLog.push(logEntry);
                                    saveFoodLog(currentLog);

                                    // Reset UI
                                    searchInput.value = '';
                                    resultsContainer.style.display = 'none';
                                    renderFoodDashboard();
                                });

                                resultsContainer.appendChild(resDiv);
                            });
                        } else {
                            resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: var(--text-secondary); font-size: 0.85rem;">No results found.</div>';
                        }

                    } catch (error) {
                        console.error('Food Search Error:', error);
                        resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: var(--accent-red); font-size: 0.85rem;">Error fetching data.</div>';
                    }
                }, 400); // 400ms debounce
            });

            // Close results if clicked outside
            document.addEventListener('click', (e) => {
                if (e.target !== searchInput && e.target !== resultsContainer) {
                    resultsContainer.style.display = 'none';
                }
            });
        }

        // AI Audit Stub
        const runAuditBtn = document.getElementById('run-food-audit-btn');
        if (runAuditBtn) {
            runAuditBtn.addEventListener('click', () => {
                const resultBox = document.getElementById('food-audit-result');
                runAuditBtn.innerHTML = '<span class="icon">🔍</span> Analyzing...';

                setTimeout(() => {
                    const log = getDailyFoodLog();
                    if (log.length === 0) {
                        resultBox.innerHTML = "No food logged yet today.";
                    } else {
                        resultBox.innerHTML = "[MOCK ATHENA RESPONSE]\nBased on your DAOA/DRD2 profile and MTHFR markers, today's protein intake is optimal for neurotransmitter support, but the sodium levels are slightly elevated. Consider increasing hydration and adding potassium-rich foods to balance. Your caloric intake aligns with the longevity target.";
                    }
                    resultBox.style.display = 'block';
                    runAuditBtn.innerHTML = '<span class="icon">🔍</span> Analyze Today\'s Intake';
                }, 1500);
            });
        }
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
    // AM — Empty Stomach (30 min before food)
    const supplementsAM_Empty = [
        { text: "☀️ Solgar NAC 600mg × 2 caps (1200mg) — Empty stomach, 30 min before breakfast", points: 2 }
    ];
    createListItems(supplementsAM_Empty, 'supp-am-empty-body');

    // AM — With Breakfast
    const supplementsAM_Food = [
        { text: "🧬 Doctor's Best Vitamin K2 MK-7 × 2 caps (200mcg) — With food (fat-soluble)", points: 2 },
        { text: "🐟 Go Healthy Fish Oil + D3 10,000IU × 1 cap — With food", points: 1 },
        { text: "🧠 Natroceutics Activated B-Complex + L-Theanine × 1 cap — With breakfast", points: 1 },
        { text: "🔥 Sanderson Turmeric 28,000+ × 2 caps — With food (needs fat)", points: 2 },
        { text: "🩸 Even Blood Sugar Babe × 2 caps — With biggest carb meal", points: 2 },
        { text: "💊 Phloe Bowel & Gut Health × 2 caps — Before breakfast", points: 1 }
    ];
    createListItems(supplementsAM_Food, 'supp-am-food-body');

    // PM — With Dinner
    const supplementsPM_Dinner = [
        { text: "🐟 Go Healthy Fish Oil + D3 × 2 caps — With dinner (Attia split protocol)", points: 2 }
    ];
    createListItems(supplementsPM_Dinner, 'supp-pm-dinner-body');

    // PM — Before Bed
    const supplementsPM = [
        { text: "🌙 Swisse Magnesium Glycinate × 2-3 caps (400mg elemental) — 30-60 min before bed", points: 2 }
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

        if (!needsContainer || !wantsContainer || !advisoryContainer) return;

        needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem;">Syncing from Supabase...</div>';
        wantsContainer.innerHTML = '';
        advisoryContainer.innerHTML = '';

        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_procurement?select=*`, {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                console.warn("Procurement table might not exist yet or RLS blocked read:", response.status);
                needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem;">[Cloud Database Not Initialized]</div>';
                return;
            }

            const data = await response.json();
            needsContainer.innerHTML = '';

            if (data.length === 0) {
                needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem;">No active procurement items.</div>';
                return;
            }

            // Separate items by category
            const needs = data.filter(d => d.category === 'NEED');
            const wants = data.filter(d => d.category === 'WANT');

            // Render Needs
            needs.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--accent-green);"></span>
                        ${item.item}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        <strong>Why:</strong> ${item.justification}
                    </div>
                `;
                needsContainer.appendChild(div);
            });

            // Render Wants
            wants.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--accent-yellow);"></span>
                        ${item.item}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        <strong>Why:</strong> ${item.justification}
                    </div>
                `;
                wantsContainer.appendChild(div);
            });

            // Render Advisory (for all items)
            data.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem;`;

                const verdictColor = item.athena_verdict === 'APPROVED' ? 'var(--accent-green)' : (item.athena_verdict === 'FLAGGED' ? 'var(--accent-yellow)' : 'var(--text-secondary)');

                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-blue); display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Target: ${item.item}</span>
                        <span style="font-size: 0.75rem; color: ${verdictColor}; border: 1px solid ${verdictColor}; padding: 2px 6px; border-radius: 4px;">${item.athena_verdict}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        ${item.athena_comment || 'Awaiting Athena assessment...'}
                    </div>
                `;
                advisoryContainer.appendChild(div);
            });

        } catch (err) {
            console.error("Network error fetching procurement data:", err);
            needsContainer.innerHTML = '<div style="color:var(--accent-red); font-size: 0.85rem;">[Network Error - Offline Mode]</div>';
        }
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

    // populateWorkout();
    initFoodAnalytics();
    initBioTracking();
    initProcurement();

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
