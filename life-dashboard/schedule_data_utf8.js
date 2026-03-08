/**
 * Symphony 2.0 - Core Data Structure & Schedule Generation
 * This file dynamically generates the timeline based on day-of-week constraints.
 */

window.SymphonyData = {
    // Current Mode allows the UI to filter what gets shown today.
    activeMode: "Standard Day",

    // We will generate the timeline array dynamically below.
    timeline: [],

    // Custom notes/appointments for this week (editable dynamically)
    weeklyNotes: [
        "Example Note: Dentist appointment on Thursday at 2:00 PM (Adjusted Longevity Protocol to morning)",
        "Example Note: Need to buy more dog food this weekend"
    ],

    // Weekly Bird's Eye View
    weekOverview: [
        { day: "Monday", focus: "Work Shift 12pm-6pm | Evening Walk", type: "work" },
        { day: "Tuesday", focus: "Off Day | Morning Walk | Deep Recovery", type: "off" },
        { day: "Wednesday", focus: "Off Day | Morning Walk | Attia Protocol", type: "off" },
        { day: "Thursday", focus: "Off Day | Morning Walk | House Reset", type: "off" },
        { day: "Friday", focus: "Work Shift 2:45pm-11pm | Morning Walk", type: "work" },
        { day: "Saturday", focus: "Work Shift 2:45pm-11pm | Morning Walk", type: "work" },
        { day: "Sunday", focus: "Work Shift 11am-5pm | Evening Walk | Sleep In (8:30am)", type: "work" }
    ],

    // Habit Pools (Tasks that can be pulled in dynamically)
    pools: {
        daily: [
            { id: "d1", text: "Pick up Quinny poop from lawn", completed: false },
            { id: "d2", text: "Catch up on washing (hang outside)", completed: false },
            { id: "d3", text: "Daily normal brush for Quinny", completed: false },
            { id: "d4", text: "Play outside with Quinny", completed: true }
        ],
        weekly: [
            { id: "w1", text: "Clean Lux vacuum head", completed: false },
            { id: "w2", text: "Clean Sarah's car (Quinny hair)", completed: false },
            { id: "w3", text: "Meal prep protein sources", completed: false },
            { id: "w4", text: "Lawns & Garden maintenance", completed: false },
            { id: "w5", text: "Weekly deep groom / Furminator for Quinny", completed: false }
        ],
        monthly: [
            { id: "m1", text: "Clean clothes drier and washer filters", completed: false },
            { id: "m2", text: "Message sister, mum, foster mum & sister", completed: false },
            { id: "m3", text: "Review Iron Panel & Ferritin levels", completed: false }
        ]
    },

    longevityWorkouts: [
        {
            id: "w_z2_1",
            type: "Cardio",
            day: "Zone 2 Base",
            meta: "45 Mins | ~135 BPM | Metabolic Conditioning",
            exercises: [
                "Strict Zone 2 (Talk Test pacing) via Ruck, Cycle, or Incline Walk",
                "Goal: Mitochondrial biogenesis & insulin sensitivity (T2D protocol)"
            ]
        },
        {
            id: "w_str_1",
            type: "Strength",
            day: "Stability & Neuro-Eccentrics",
            meta: "Achilles Prep + BDNF Stimulation",
            exercises: [
                "Eccentric Calf Drops (slow 4s lower) - 3x10/leg",
                "Kneeling Heel Sit (Foot Rehab) - 60s",
                "Goblet Reverse Lunges (8kg KB) - 3x10/leg (High BDNF yield)",
                "Plank to Bear Hold - 3x40s"
            ]
        },
        {
            id: "w_str_2",
            type: "Strength",
            day: "Centenarian Grip & Pull",
            meta: "Upper Body & Carry",
            exercises: [
                "Heavy Farmer's Carry (Grip Strength proxy) - 3x 60s",
                "Single-Arm DB Row (10kg) - 3x10/arm",
                "Kettlebell Halo (8kg KB) - 3x10/dir",
                "Seated DB Press (3kg DBs) - 3x15"
            ]
        },
        {
            id: "w_z5",
            type: "Cardio",
            day: "VO2 Max Intervals",
            meta: "1x per week ONLY | Cardiac Output",
            exercises: [
                "10 min warm-up",
                "4x 4-minute intervals at MAX sustainable effort (Zone 5)",
                "4-minute active recovery between intervals",
                "10 min cool-down"
            ]
        }
    ],

    bioProtocols: {
        supplements: [
            { id: "s1", text: "Creatine Monohydrate (5-10g) - Brain energy & Alzheimer's defense", completed: false },
            { id: "s2", text: "Omega-3 (EPA/DHA) - Neuro-inflammation reduction", completed: false },
            { id: "s3", text: "Vitamin D3 (5000 IU) - Cognitive support", completed: false },
            { id: "s4", text: "Magnesium Glycinate (Evening) - Deep sleep prep", completed: false },
            { id: "s5", text: "Vitamin K2 MK-7 (Doctor's Best)", completed: false },
            { id: "s6", text: "L-Theanine (Natroceutics / Rapid Calm)", completed: false },
            { id: "s7", text: "NAC pure 600mg (NO SELENIUM)", completed: false },
            { id: "s8", text: "Blood Draw Check: Ferritin < 100 ug/L goal", completed: false }
        ],
        dogTraining: [
            { id: "dt1", text: "Doorways: 'Wait' before crossing threshold", completed: false },
            { id: "dt2", text: "Impulse: 'Leave It' during play", completed: false },
            { id: "dt3", text: "Walks: 30-min Sniffari / Decompression", completed: false }
        ]
    }
};

// ============================================================================
// DYNAMIC DAY-OF-WEEK ROUTER
// ============================================================================

window.generateTodayTimeline = function () {
    const today = new Date().getDay(); // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    let timeline = [];

    // --- WAKE BLOCK ---
    if (today === 0) { // Sunday
        timeline.push({ id: "t_wake", time: "08:30 AM", title: "Wake Up", desc: "Start the day.", expertInsight: "Drink 1L Water with electrolytes immediately. Your Sunday rest day allows for this delayed wake time to prioritize recovery.", tags: ["Health", "Morning"], completed: false });
    } else { // Mon-Sat
        timeline.push({ id: "t_wake", time: "06:30 AM", title: "Wake Up", desc: "Start the day.", expertInsight: "Drink 1L Water with electrolytes immediately. Wait 90 minutes before caffeine (CYP1A2 poor metabolizer) to protect deep sleep later.", tags: ["Health", "Morning"], completed: false });
    }

    // --- MORNING LIGHT / NEURO ---
    let sunTime = today === 0 ? "09:00 AM" : "07:30 AM";
    timeline.push({ id: "t_sun", time: sunTime, title: "Morning Movement Outside", desc: "Get outside for 10-15 minutes.", expertInsight: "Louisa Nicola Protocol: Morning sunlight exposure directly to the eyes regulates your circadian rhythm and supports your CLOCK genes.", tags: ["Bio"], completed: false });

    // --- KIDS MORNING ROUTINE (Mon - Fri) ---
    if (today >= 1 && today <= 5) {
        timeline.push({ id: "t_kids", time: "06:30 AM - 08:15 AM", title: "Kids Morning Prep", desc: "Help with kids routine and breakfast.", expertInsight: "Action-oriented family time. Stay present and avoid digital distraction during this block.", tags: ["Family"], completed: false });
        timeline.push({ id: "t_drop", time: "08:50 AM", title: "Morning Ride Drop-off", desc: "Drop off Sarah and the boys.", tags: ["Family"], completed: false });
    }

    // --- QUINNY WALK (Morning Route: Tue, Wed, Thu, Fri, Sat) ---
    if (today >= 2 && today <= 6) {
        let walkTime = (today === 5 || today === 6) ? "09:30 AM" : "09:30 AM"; // Default morning walk
        timeline.push({ id: "t_walk_am", time: walkTime, title: "Quinny's Morning Walk", desc: "30-45 minute walk.", expertInsight: "Zone 1/2 active recovery. Incorporate 10 minutes of rigid training (impulse control) for mental stimulation.", tags: ["Pet Care"], completed: false });
    }

    // --- LONGEVITY WORKOUT BLOCK ---
    // Off-days (Tue, Wed, Thu) usually have more time for longevity protocols in the morning
    if (today >= 2 && today <= 4) {
        timeline.push({ id: "t_workout", time: "10:30 AM", title: "Daily Training Session", desc: "Execute today's workout block.", expertInsight: "Peter Attia Longevity Protocol: Consistent training volume is the strongest leading indicator of an extended healthspan.", tags: ["Workout", "Attia"], completed: false });
    }

    // --- TCF7L2 GLUCOSE CLEARANCE PROTOCOL ---
    // Injected due to high-glycemic meal log: 5 pieces of Turkish Delight
    // Turkish Delight is extremely high-glycemic (glucose + sucrose base, ~20-25g sugar per 5 pieces)
    // Must be executed within 15-30 minutes of consumption to activate GLUT4 translocation
    const now = new Date();
    let glucoseProtocolHour = now.getHours();
    let glucoseProtocolMin = now.getMinutes() + 20;
    if (glucoseProtocolMin >= 60) {
        glucoseProtocolHour += 1;
        glucoseProtocolMin -= 60;
    }
    if (glucoseProtocolHour >= 24) glucoseProtocolHour = 23;
    const gpPeriod = glucoseProtocolHour >= 12 ? "PM" : "AM";
    const gpHour12 = glucoseProtocolHour % 12 === 0 ? 12 : glucoseProtocolHour % 12;
    const gpMinStr = glucoseProtocolMin < 10 ? "0" + glucoseProtocolMin : "" + glucoseProtocolMin;
    const glucoseProtocolTimeStr = gpHour12 + ":" + gpMinStr + " " + gpPeriod;

    timeline.push({
        id: "t_tcf7l2_squats",
        time: glucoseProtocolTimeStr,
        title: "Glucose Disposal Protocol: 30 Air Squats (GLUT4 Activation)",
        desc: "IMMEDIATE ACTION REQUIRED: Perform 30 continuous air squats NOW. Focus on full depth and controlled tempo (2s down, 1s up). This is a non-negotiable metabolic countermeasure following your Turkish Delight intake.",
        expertInsight: "TCF7L2 Risk Mitigation: You carry a high-risk metabolic genotype (TCF7L2 variant) that impairs insulin secretion timing and glucose uptake efficiency. Turkish Delight is a pure glucose-sucrose bomb (~20-25g of high-GI sugar across 5 pieces), causing a rapid postprandial glucose spike. Skeletal muscle contraction is the only GLUT4-independent pathway to force glucose transporter translocation to the cell membrane — meaning your muscles absorb glucose WITHOUT requiring insulin. 30 air squats engage your largest muscle groups (glutes, quads, hamstrings) and can reduce the postprandial glucose AUC (area under the curve) by up to 30%. Execute this within 20-30 minutes of consumption for maximum glycemic blunting. Do NOT skip this block.",
        tags: ["Bio", "Metabolic"],
        completed: false
    });

    // --- WORK BLOCKS & VACATION OVERRIDE ---
    const todayObj = new Date();
    // Month is 0-indexed (March = 2)
    const isVacation = (todayObj.getMonth() === 2 && todayObj.getDate() >= 27 && todayObj.getDate() <= 30);
    const isMarch9Override = (todayObj.getMonth() === 2 && todayObj.getDate() === 9);

    if (isVacation) {
        timeline.push({ id: "t_work", time: "All Day", title: "Vacation / Time Off", desc: "No work shifts scheduled.", expertInsight: "Focus entirely on parasympathetic recovery, family connection, and deep rest.", tags: ["Rest", "Family"], completed: false });
    } else if (isMarch9Override) {
        timeline.push({ id: "t_work", time: "02:45 PM - 11:00 PM", title: "Work Shift (Override)", desc: "Clock in for the evening shift.", expertInsight: "High dopamine demand. Ensure you take brief 2-minute visual breaks (stare 20ft away) every hour to reduce cognitive fatigue.", tags: ["Work"], completed: false });
    } else {
        if (today === 5 || today === 6) { // Fri, Sat
            timeline.push({ id: "t_work", time: "02:45 PM - 11:00 PM", title: "Work Shift", desc: "Clock in for the evening shift.", expertInsight: "High dopamine demand. Ensure you take brief 2-minute visual breaks (stare 20ft away) every hour to reduce cognitive fatigue.", tags: ["Work"], completed: false });
        } else if (today === 0) { // Sunday
            timeline.push({ id: "t_work", time: "11:00 AM - 05:00 PM", title: "Work Shift", desc: "Clock in for the day shift.", tags: ["Work"], completed: false });
        } else if (today === 1) { // Monday
            timeline.push({ id: "t_work", time: "12:00 PM - 06:00 PM", title: "Work Shift", desc: "Clock in for the day shift.", tags: ["Work"], completed: false });
        }
    }

    // --- KIDS EVENING ROUTINE (Sun, Mon, Tue, Wed, Thu) ---
    // User helps feed, clean, and tuck the kids into bed from 4:15 PM to 7:30 PM on Off Days + Sun/Mon.
    if (today >= 0 && today <= 4) {
        timeline.push({ id: "t_kids_pm", time: "04:15 PM - 07:30 PM", title: "Kids Evening Routine", desc: "Feed, clean, and tuck the kids into bed.", expertInsight: "High physical and emotional engagement. Treat this as an active movement block.", tags: ["Family"], completed: false });
    }

    // --- QUINNY EVENING WALK ---
    // If it's a day with the Kids Evening routine (Sun-Thu) AND we aren't working the evening shift (Fri/Sat), the walk goes AFTER the kids are down.
    if (today >= 0 && today <= 4) {
        timeline.push({ id: "t_walk_pm", time: "07:45 PM", title: "Quinny's Evening Walk", desc: "Decompression walk.", expertInsight: "Post-routine Zone 1 movement clears accumulated lactate and cortisol before bed.", tags: ["Pet Care"], completed: false });
    } else if (today === 1) { // Monday (Fallback, handled by above condition, kept for logic safety if shifting)
        timeline.push({ id: "t_walk_pm", time: "07:45 PM", title: "Quinny's Evening Walk", desc: "Decompression walk.", expertInsight: "Post-work Zone 1 movement clears accumulated lactate and cortisol.", tags: ["Pet Care"], completed: false });
    }

    // --- CHORES / RESET ---
    // If not working the afternoon, add the Parker pickup and house reset
    if (today >= 2 && today <= 4) {
        timeline.push({ id: "t_chores", time: "11:30 AM", title: "House Mid-Day Reset", desc: "Dishes, beds, lux ground floor, spray couches.", tags: ["Chores"], completed: false });
        timeline.push({ id: "t_nap", time: "12:30 PM", title: "Nap / Core Rest", desc: "Take a break to recharge.", expertInsight: "Crucial for physical recovery and cognitive offloading, especially after strength training or poor night sleep.", tags: ["Rest"], completed: false });
        timeline.push({ id: "t_pickup", time: "02:45 PM", title: "Parker Pick Up", desc: "Leave with Tash at 2:45 PM.", tags: ["Family"], completed: false });
    }

    // --- SLEEP PRIMING ---
    // Adjust sleep priming based on work schedule (e.g., late shifts on Fri/Sat means later priming)
    let sleepTime = "08:00 PM";
    if (today === 5 || today === 6) sleepTime = "11:30 PM";
    else if (today === 1) sleepTime = "08:30 PM";

    timeline.push({ id: "t_sleep", time: sleepTime, title: "Wind Down Protocol", desc: "Begin evening routine.", expertInsight: "Louisa Nicola Deep Sleep Priming: Establish a digital sunset (no blue light) and practice box breathing. This triggers the Parasympathetic state and preps the Glymphatic system to clear Alzheimer's-related proteins.", tags: ["Bio", "Neuro"], completed: false });

    // Add brush Quinny reminder
    if (today === 0 || today === 1 || today === 2 || today === 3 || today === 4 || today === 5 || today === 6) {
        timeline.push({ id: "t_quinny_brush", time: "07:00 PM", title: "Brush Quinny's Fur", desc: "Brush Quinny's fur.", tags: ["Pet Care"], completed: false });
    }

    // Sort timeline by time string (basic sorting, works for our PM/AM format if we convert to 24h for sorting)
    timeline.sort((a, b) => {
        const parseTime = (timeStr) => {
            const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/);
            if (!match) return 0;
            let hours = parseInt(match[1]);
            const mins = parseInt(match[2]);
            const period = match[3];
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            return hours * 60 + mins;
        };
        return parseTime(a.time) - parseTime(b.time);
    });

    return timeline;
};
