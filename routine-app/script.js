document.addEventListener('DOMContentLoaded', () => {
    // Auth & Lock Screen Logic
    const CORRECT_PASSWORD = "symphony2026";
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

    // Current Data with Point Values
    const scheduleData = [
        { time: '08:50 AM', title: 'Morning Ride Drop-off', desc: 'Sarah and the boys (School/Kindy)', tags: ['Done'], completed: true, points: 2 },
        { time: '09:00 AM - 10:00 AM', title: 'Post-Drop-off Reset', desc: 'Dishes, put stuff away, make boys bed, lux ground floor, empty inside bins, air house out, spray couches.', tags: ['Cleaning'], completed: false, points: 4 },
        { time: '10:00 AM - 11:30 AM', title: 'Wash & Brush', desc: 'Catch up on washing (hang outside) & Quinny 1hr Furminator brush.', tags: ['Chores', 'Pet Care'], completed: false, points: 5 },
        { time: '11:30 AM - 12:30 PM', title: 'Lunch & Wind Down', desc: 'Sort/fold washing, eat lunch, prepare to rest.', tags: ['Break', 'break'], completed: false, points: 1 },
        { time: '12:30 PM - 01:30 PM', title: 'Core Rest Phase (Nap)', desc: 'Crucial for recovery and energy before the afternoon rush. Sleep well!', tags: ['Rest', 'break'], completed: false, points: 1 },
        { time: '01:30 PM - 02:30 PM', title: 'Quinny\'s Walk (Zone 2 Cardio)', desc: '1-Hr brisk walk (conversational but strained) for aerobic base + 10 mins training.', tags: ['Pet Care', 'Health'], completed: false, points: 3 },
        { time: '02:30 PM - 02:45 PM', title: 'Shower & Prep', desc: 'Have a quick shower, tidy up the house, and refill bin liners.', tags: ['Prep', 'Self Care'], completed: false, points: 1 },
        { time: '02:45 PM - 03:30 PM', title: 'Parker Pick Up', desc: 'Leave with Tash at 2:45 PM to pick up Parker for 3:00 PM.', tags: ['Family'], completed: false, points: 2 },
        { time: 'Late Afternoon', title: 'Free Time Block', desc: 'Suggestions: Take Quinny for a second walk, do a Trick session with her, or just relax!', tags: ['Free Time', 'break'], completed: false, points: 0 },
        { time: 'Evening', title: 'Final Sweep', desc: 'Bring in outside bins when convenient.', tags: ['Chores'], completed: false, points: 1 },
    ];

    const dailyCandidates = [
        { text: "Pick up dog (Quinn) poop from the lawn", points: 2 },
        { text: "Morning ride over the hill with Sarah and the boys", points: 3 },
        { text: "Dishes", points: 1 },
        { text: "Put stuff away", points: 1 },
        { text: "Make boys' bed (if needed)", points: 1 },
        { text: "Lux ground floor", points: 2 },
        { text: "Spray couches", points: 1 },
        { text: "Air house out", points: 1 },
        { text: "Make house smell nice", points: 1 },
        { text: "Catch up on washing (hang outside if decent day)", points: 3 },
        { text: "Sort, fold, and pop washing aside for others", points: 2 },
        { text: "Give Quinny a full Furminator brush (takes ~1 hour)", points: 3 },
        { text: "Empty inside bins and refill liners", points: 1 },
        { text: "Bring in outside bins (later in the day)", points: 1 },
        { text: "General clean up of house", points: 2 },
        { text: "Pick up Parker for 3pm (Leave with Tash at 2:45pm)", points: 2 },
        { text: "Clean my shoes", points: 1 }
    ];

    const weeklyMonthly = {
        weekly: [
            "Clean the vacuum (Lux) head",
            "Clean Sarah's car (due to Quinny's fur)",
            "Complete 3-Day Longevity Home Workout Split",
            "Clean the toilet and bathroom"
        ],
        monthly: [
            "Clean the clothes drier and washer",
            "Message sister (Tresha)",
            "Message mum (Rachel)",
            "Message foster mum (Jacinta)",
            "Message foster sister (Shakira)"
        ]
    };

    const workoutPlan = [
        {
            day: "Workout A",
            focus: "Lower Body & Core (Foundation)",
            exercises: [
                "1. Goblet Squats (8kg KB or 10kg DB) - 3x10",
                "2. RDLs (10kg + 8kg) - 3x10",
                "3. Bulgarian Split Squats (Bodyweight/3kg DBs) - 3x8",
                "4. Plank to Bear Hold - 3x 30s/20s"
            ]
        },
        {
            day: "Workout B",
            focus: "Upper Body Pull & Shoulders (Posture)",
            exercises: [
                "1. Single-Arm DB Row (10kg DB on bench) - 3x10",
                "2. Kettlebell Halo (8kg KB) - 3x10",
                "3. Seated Overhead Press (3kg DBs on bench) - 3x15",
                "4. Bench Reverse Flyes (3kg DBs on bench) - 3x15"
            ]
        },
        {
            day: "Workout C",
            focus: "Full Body Functional Stability",
            exercises: [
                "1. Kettlebell Deadbug (8kg KB) - 3x10",
                "2. Incline Bench Push-ups - 3x near failure",
                "3. Goblet Reverse Lunges (8kg KB) - 3x10",
                "4. Farmers Carry (10kg + 8kg) - 3x 45s"
            ]
        }
    ];

    // Supabase Configuration
    const SUPABASE_URL = "YOUR_SUPABASE_URL"; // We will prompt the user to inject these securely or rely on their environment
    const SUPABASE_ANON_KEY = "YOUR_SUPABASE_ANON_KEY";

    async function fetchSupabaseData() {
        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/user_data?id=eq.1&select=*`, {
                method: 'GET',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data && data.length > 0) {
                    const userData = data[0];

                    // Parse Schedule (if it's valid JS/JSON string)
                    if (userData.schedule_payload) {
                        try {
                            // Extract schedule from the payload (assuming it overrides scheduleData)
                            // For security/simplicity, we might use eval or Function, 
                            // but ideally it's an array of objects.
                            console.log("Schedule Payload found, but avoiding unsafe eval for now.");
                        } catch (e) { console.error("Error parsing schedule:", e); }
                    }

                    // Parse History & Memory
                    if (userData.history_payload) {
                        document.getElementById('bio-history-content').innerHTML = marked.parse(userData.history_payload);
                    } else {
                        document.getElementById('bio-history-content').innerHTML = "<p class='text-secondary'>No biological history logged yet.</p>";
                    }

                    if (userData.memory_payload) {
                        document.getElementById('memory-bank-content').innerHTML = marked.parse(userData.memory_payload);
                    } else {
                        document.getElementById('memory-bank-content').innerHTML = "<p class='text-secondary'>No memories logged yet.</p>";
                    }
                }
            } else {
                console.error("Supabase fetch failed:", response.status, response.statusText);
            }
        } catch (error) {
            console.error("Error connecting to Supabase:", error);
            document.getElementById('bio-history-content').innerHTML = `<p class="error-msg">Error loading data: ${error.message}</p>`;
            document.getElementById('memory-bank-content').innerHTML = `<p class="error-msg">Error loading data: ${error.message}</p>`;
        }
    }

    // Load schedule state
    const savedSchedule = JSON.parse(localStorage.getItem('symphony_schedule_state') || 'null');
    if (savedSchedule && savedSchedule.length === scheduleData.length) {
        scheduleData.forEach((item, i) => {
            item.completed = savedSchedule[i];
        });
    }

    // Productivity Point Tracking
    let pointsToday = 0;
    const pointsDisplay = document.getElementById('points-display');

    // Graph Data States (In production, replace dummy history with Supabase historical logs)
    const graphDataWeekly = JSON.parse(localStorage.getItem('symphony_graph_data') || '[12, 19, 15, 8, 22, 18, 0]');

    // Mock historical data to demonstrate the visual scaling
    let graphDataMonthly = Array.from({ length: 29 }, () => Math.floor(Math.random() * 15) + 5);
    graphDataMonthly.push(0); // Today

    let graphDataYearly = [120, 145, 130, 160, 155, 170, 165, 180, 175, 190, 185, 0]; // 11 months + current month empty

    let currentChartView = 'weekly';

    window.setChartView = function (view) {
        currentChartView = view;
        // Update button states
        ['weekly', 'monthly', 'yearly'].forEach(v => {
            document.getElementById(`btn-view-${v}`).classList.remove('active');
        });
        document.getElementById(`btn-view-${view}`).classList.add('active');

        updateChartDisplay();
    };

    function updateChartDisplay() {
        if (!window.productivityChartInstance) return;

        const chart = window.productivityChartInstance;
        const subtitle = document.getElementById('chart-subtitle');

        if (currentChartView === 'weekly') {
            chart.data.labels = ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Today'];
            chart.data.datasets[0].data = graphDataWeekly;
            subtitle.innerText = "Your 7-Day Rolling Gamification Score";
        } else if (currentChartView === 'monthly') {
            const labels = Array.from({ length: 30 }, (_, i) => `${i - 29}d`);
            labels[29] = 'Today';
            chart.data.labels = labels;
            chart.data.datasets[0].data = graphDataMonthly;
            subtitle.innerText = "Your 30-Day Monthly Gamification Score";
        } else if (currentChartView === 'yearly') {
            chart.data.labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            chart.data.datasets[0].data = graphDataYearly;
            subtitle.innerText = "Your Year-to-Date Gamification Score";
        }

        chart.update();
    }

    function updatePoints() {
        pointsToday = 0;

        // Tally from timeline
        scheduleData.forEach(item => {
            if (item.completed && item.points) pointsToday += item.points;
        });

        // Tally from Daily Candidates
        const savedDailyState = JSON.parse(localStorage.getItem('symphony_list_state_daily-list') || '{}');
        dailyCandidates.forEach((cand, index) => {
            if (savedDailyState[index]) pointsToday += cand.points;
        });

        pointsDisplay.innerText = `[${pointsToday} pts]`;

        // Update today's graph value across scales
        graphDataWeekly[6] = pointsToday;
        graphDataMonthly[29] = pointsToday;

        const currentMonth = new Date().getMonth();
        // Just directly setting the current month's accumulated score for demonstration
        graphDataYearly[currentMonth] = 75 + pointsToday;

        localStorage.setItem('symphony_graph_data', JSON.stringify(graphDataWeekly));

        updateChartDisplay();

        // Push current points to Supabase
        syncPointsToCloud(pointsToday);
    }

    // Cloud Sync Logic for Points
    let lastSyncTimeout = null;
    function syncPointsToCloud(points) {
        // Debounce the network request so we don't spam Supabase
        // every time a checkbox is clicked
        if (lastSyncTimeout) clearTimeout(lastSyncTimeout);

        lastSyncTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`${SUPABASE_URL}/rest/v1/user_data?id=eq.1`, {
                    method: 'PATCH',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json',
                        'Prefer': 'return=minimal'
                    },
                    body: JSON.stringify({ dashboard_points: points })
                });

                if (!response.ok) {
                    console.error("Failed to sync points to cloud:", response.statusText);
                } else {
                    console.log(`Synced ${points} points to Supabase.`);
                }
            } catch (err) {
                console.error("Network error syncing points:", err);
            }
        }, 1500); // Wait 1.5 seconds after last click before syncing
    }

    function initChart() {
        const ctx = document.getElementById('productivityChart').getContext('2d');
        window.productivityChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Wed', 'Thu', 'Fri', 'Sat', 'Sun', 'Mon', 'Today'],
                datasets: [{
                    label: 'Productivity Points',
                    data: graphDataWeekly,
                    backgroundColor: 'rgba(56, 189, 248, 0.6)',
                    borderColor: 'rgba(56, 189, 248, 1)',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

        // Initial render update to sync labels
        updateChartDisplay();
    }

    // Render Logic

    // Tab Switching
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Populate Today's Schedule
    const timelineElement = document.getElementById('today-timeline');
    const renderTimeline = () => {
        timelineElement.innerHTML = '';
        let completedCount = 0;

        scheduleData.forEach((item, index) => {
            if (item.completed) completedCount++;

            const el = document.createElement('div');
            el.className = `timeline-item ${item.completed ? 'completed' : ''}`;
            el.innerHTML = `
                <span class="time">${item.time}</span>
                <div class="task-title">${item.title} <span style="font-size:0.8rem; color:var(--accent-blue);">[+${item.points} pts]</span></div>
                <div class="task-desc">${item.desc}</div>
                <div>
                    ${item.tags.map(t => `<span class="tag ${t === 'break' ? 'break' : ''}">${t}</span>`).join('')}
                </div>
            `;

            el.addEventListener('click', () => {
                scheduleData[index].completed = !scheduleData[index].completed;
                localStorage.setItem('symphony_schedule_state', JSON.stringify(scheduleData.map(s => s.completed)));
                renderTimeline();
            });

            timelineElement.appendChild(el);
        });

        const progressPercent = (completedCount / scheduleData.length) * 100;
        document.getElementById('today-progress').style.width = `${progressPercent}%`;

        updatePoints();
    };

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

    // Initialize View
    initChart();
    renderTimeline();
    createListItems(dailyCandidates, 'daily-list');
    createListItems(weeklyMonthly.weekly, 'weekly-list');
    createListItems(weeklyMonthly.monthly, 'monthly-list');

    // Create dog tasks
    const dogTrainingTasks = [
        "Meal Time: 'Wait' until told 'Okay'",
        "Doorways: 'Wait' before going through any door",
        "Impulse Control: Practice 'Leave It' during play",
        "Free Time: 30-min Sniffari / Decompression Walk",
        "Mental Stimulation: 10 mins Hide and Seek"
    ];
    createListItems(dogTrainingTasks, 'dog-training-list');

    // Create supplement tasks
    const supplementTasks = [
        "Vitamin K2 MK-7 (Doctor's Best with MenaQ7)",
        "L-Theanine (Natroceutics B-Complex OR Good Health Rapid Calm)",
        "NAC pure 600mg (Solgar Vegicaps)"
    ];
    createListItems(supplementTasks, 'supplements-list');

    populateWorkout();

    // Trigger Supabase fetch
    fetchSupabaseData();
});
