document.addEventListener('DOMContentLoaded', () => {
    // Current Data
    const scheduleData = [
        { time: '08:50 AM', title: 'Morning Ride Drop-off', desc: 'Sarah and the boys (School/Kindy)', tags: ['Done'], completed: true },
        { time: '09:00 AM - 10:00 AM', title: 'Post-Drop-off Reset', desc: 'Dishes, put stuff away, make boys bed, lux ground floor, empty inside bins, air house out, spray couches.', tags: ['Cleaning'], completed: false },
        { time: '10:00 AM - 11:30 AM', title: 'Wash & Brush', desc: 'Catch up on washing (hang outside) & Quinny 1hr Furminator brush.', tags: ['Chores', 'Pet Care'], completed: false },
        { time: '11:30 AM - 12:30 PM', title: 'Lunch & Wind Down', desc: 'Sort/fold washing, eat lunch, prepare to rest.', tags: ['Break', 'break'], completed: false },
        { time: '12:30 PM - 01:30 PM', title: 'Core Rest Phase (Nap)', desc: 'Crucial for recovery and energy before the afternoon rush. Sleep well!', tags: ['Rest', 'break'], completed: false },
        { time: '01:30 PM - 02:30 PM', title: 'Quinny\'s Walk (Zone 2 Cardio)', desc: '1-Hr brisk walk (conversational but strained) for aerobic base + 10 mins training.', tags: ['Pet Care', 'Health'], completed: false },
        { time: '02:30 PM - 02:45 PM', title: 'Shower & Prep', desc: 'Have a quick shower, tidy up the house, and refill bin liners.', tags: ['Prep', 'Self Care'], completed: false },
        { time: '02:45 PM - 03:30 PM', title: 'Parker Pick Up', desc: 'Leave with Tash at 2:45 PM to pick up Parker for 3:00 PM.', tags: ['Family'], completed: false },
        { time: 'Late Afternoon', title: 'Free Time Block', desc: 'Suggestions: Take Quinny for a second walk, do a Trick session with her, or just relax!', tags: ['Free Time', 'break'], completed: false },
        { time: 'Evening', title: 'Final Sweep', desc: 'Bring in outside bins when convenient.', tags: ['Chores'], completed: false },
    ];

    const dailyCandidates = [
        "Pick up dog (Quinn) poop from the lawn",
        "Morning ride over the hill with Sarah and the boys",
        "Dishes",
        "Put stuff away",
        "Make boys' bed (if needed)",
        "Lux ground floor",
        "Spray couches",
        "Air house out",
        "Make house smell nice",
        "Catch up on washing (hang outside if decent day)",
        "Sort, fold, and pop washing aside for others",
        "Give Quinny a full Furminator brush (takes ~1 hour)",
        "Empty inside bins and refill liners",
        "Bring in outside bins (later in the day)",
        "General clean up of house",
        "Pick up Parker for 3pm (Leave with Tash at 2:45pm)"
    ];

    const weeklyMonthly = {
        weekly: [
            "Clean the vacuum (Lux) head",
            "Clean Sarah's car (due to Quinny's fur)",
            "Complete 3-Day Longevity Home Workout Split"
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
                <div class="task-title">${item.title}</div>
                <div class="task-desc">${item.desc}</div>
                <div>
                    ${item.tags.map(t => `<span class="tag ${t === 'break' ? 'break' : ''}">${t}</span>`).join('')}
                </div>
            `;

            el.addEventListener('click', () => {
                scheduleData[index].completed = !scheduleData[index].completed;
                renderTimeline();
            });

            timelineElement.appendChild(el);
        });

        const progressPercent = (completedCount / scheduleData.length) * 100;
        document.getElementById('today-progress').style.width = `${progressPercent}%`;
    };

    // Populate Lists
    const createListItems = (items, containerId) => {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        items.forEach((itemText) => {
            const li = document.createElement('li');
            li.innerHTML = `
                <div class="checkbox"></div>
                <div class="task-content">${itemText}</div>
            `;

            li.querySelector('.checkbox').addEventListener('click', function () {
                this.classList.toggle('checked');
                this.parentElement.classList.toggle('completed');
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
});
