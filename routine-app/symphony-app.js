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
        const hourlyRate = 24.00;
        const hoursWorked = 28.5;
        const kiwiSaverRate = 0.03; // 3%

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

    async function handleQuickAdd() {
        const title = quickAddInput.value.trim();
        if (!title) return;

        quickAddBtn.innerText = "⏳";
        quickAddBtn.style.pointerEvents = "none";

        const newTask = {
            title: title,
            points: 2,
            priority_color: 'ORANGE',
            time_target: 'Unscheduled',
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
                if (typeof initTaskConfigurator === 'function') initTaskConfigurator();
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

            // Daily tasks
            if (tt === 'Daily Flexible') return 'pool-today';

            // This week tasks
            if (tt === 'Weekly' || tt === 'Weekly (3x)' || tt === 'Moveable') return 'pool-week';

            // Long-term
            if (tt === 'Monthly') return 'pool-longterm';

            // Everything else (Unscheduled, empty, null, new quick-add tasks)
            return 'pool-future';
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

            el.innerHTML = `
                <div class="task-title" style="font-size: 0.95rem;">${task.title} <span style="font-size:0.8rem; color:var(--accent-blue);">[+${task.points} pts]</span></div>
                ${task.description ? `<div class="task-desc" style="font-size: 0.8rem;">${task.description}</div>` : ''}
                <div style="margin-top: 4px;">
                    ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.65rem; padding: 2px 6px;">${t}</span>`).join('')}
                </div>
            `;

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
    const MOCK_FOOD_DATA = {
        calories: 1850,
        target_calories: 2200,
        protein: 140, // grams
        carbs: 120, // grams
        fats: 65,  // grams
        meals: [
            { time: '08:00 AM', desc: '3x Scrambled Eggs on Toast with Butter' },
            { time: '01:00 PM', desc: 'Chicken Breast Salad with Olive Oil Dressing' },
            { time: '04:00 PM', desc: 'Whey Protein Shake (Water)' },
            { time: '07:30 PM', desc: 'Steak, Kumara Mash, and Broccolini' }
        ]
    };

    function initFoodAnalytics() {
        // 1. Render Calorie Progress
        const calorieDisplay = document.getElementById('food-calorie-display');
        const calorieProgress = document.getElementById('calorie-progress');

        if (calorieDisplay && calorieProgress) {
            calorieDisplay.innerText = `${MOCK_FOOD_DATA.calories} / ${MOCK_FOOD_DATA.target_calories} kcal`;

            let progressPercent = (MOCK_FOOD_DATA.calories / MOCK_FOOD_DATA.target_calories) * 100;
            if (progressPercent > 100) {
                progressPercent = 100;
                calorieProgress.style.background = 'linear-gradient(90deg, #ef4444, #b91c1c)'; // Over target (red)
            }
            calorieProgress.style.width = `${progressPercent}%`;
        }

        // 2. Render Macro Breakdown List
        const pEl = document.getElementById('food-protein');
        const cEl = document.getElementById('food-carbs');
        const fEl = document.getElementById('food-fats');

        if (pEl) pEl.innerText = `${MOCK_FOOD_DATA.protein}g`;
        if (cEl) cEl.innerText = `${MOCK_FOOD_DATA.carbs}g`;
        if (fEl) fEl.innerText = `${MOCK_FOOD_DATA.fats}g`;

        // 3. Render Meal Timeline
        const mealList = document.getElementById('food-timeline-list');
        if (mealList) {
            mealList.innerHTML = '';
            MOCK_FOOD_DATA.meals.forEach(meal => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <div style="color: var(--text-secondary); font-size: 0.85rem; width: 80px; flex-shrink: 0; margin-top: 3px;">${meal.time}</div>
                    <div class="task-content" style="color: var(--text-primary); font-weight: 500;">${meal.desc}</div>
                `;
                mealList.appendChild(li);
            });
        }

        // 4. Initialize Macro Doughnut Chart
        const canvas = document.getElementById('foodMacroChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            if (window.foodChartInstance) {
                window.foodChartInstance.destroy();
            }

            window.foodChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Protein', 'Carbs', 'Fats'],
                    datasets: [{
                        data: [MOCK_FOOD_DATA.protein, MOCK_FOOD_DATA.carbs, MOCK_FOOD_DATA.fats],
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
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    cutout: '65%'
                }
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

    // --- Dynamic Task Configurator (Traffic Light) ---
    async function initTaskConfigurator() {
        const configContent = document.getElementById('config-content');
        if (!configContent) return;

        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?select=*&order=priority_color.desc`, {
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                configContent.innerHTML = '<div style="color:var(--accent-red); font-size: 0.85rem;">[Cloud Database Not Initialized - Run SQL First]</div>';
                return;
            }

            const tasks = await response.json();
            configContent.innerHTML = '';

            // Group tasks by category
            const redTasks = tasks.filter(t => t.priority_color === 'RED');
            const orangeTasks = tasks.filter(t => t.priority_color === 'ORANGE');
            const greenTasks = tasks.filter(t => t.priority_color === 'GREEN');

            const createCategorySection = (title, colorClass, colorHex, taskList) => {
                const section = document.createElement('div');
                section.className = 'sub-panel';
                section.style.borderColor = `rgba(${colorClass}, 0.3)`;

                let html = `<h3 style="color: ${colorHex};"><span class="icon">🚦</span> ${title}</h3>
                <div style="display: flex; flex-direction: column; gap: 0.75rem; margin-top: 1rem;">`;

                taskList.forEach(task => {
                    const selRed = task.priority_color === 'RED' ? 'selected' : '';
                    const selOrg = task.priority_color === 'ORANGE' ? 'selected' : '';
                    const selGrn = task.priority_color === 'GREEN' ? 'selected' : '';

                    html += `
                        <div style="display:flex; justify-content:space-between; align-items:center; background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 0.75rem;">
                            <div>
                                <div style="font-weight: 600; color: var(--text-primary);">${task.title}</div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">${task.time_target || 'Flexible'} • ${task.points} pts</div>
                            </div>
                            <select onchange="changeTaskColor('${task.id}', this)" 
                                style="background: rgba(15, 23, 42, 0.9); border: 1px solid ${colorHex}; color: ${colorHex}; border-radius: var(--radius-sm); padding: 0.25rem 0.5rem; font-weight: bold; cursor: pointer; outline: none; transition: all 0.2s;">
                                <option value="RED" ${selRed}>RED</option>
                                <option value="ORANGE" ${selOrg}>ORANGE</option>
                                <option value="GREEN" ${selGrn}>GREEN</option>
                            </select>
                        </div>
                    `;
                });

                html += `</div>`;
                section.innerHTML = html;
                return section;
            };

            // Needs to match the css variable rgb values or just use hex
            configContent.appendChild(createCategorySection('RED (Strict Timeline)', '239, 68, 68', '#ef4444', redTasks));
            configContent.appendChild(createCategorySection('ORANGE (Daily Flexible)', '249, 115, 22', '#f97316', orangeTasks));
            configContent.appendChild(createCategorySection('GREEN (Moveable/Weekly)', '16, 185, 129', '#10b981', greenTasks));

        } catch (err) {
            console.error("Error fetching tasks configuration:", err);
            configContent.innerHTML = '<div style="color:var(--accent-red); font-size: 0.85rem;">[Network Error - Offline Mode]</div>';
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
    initTaskConfigurator();

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
