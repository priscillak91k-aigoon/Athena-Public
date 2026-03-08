import sys

with open('symphony-app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update tab logic
content = content.replace("const savedTab = localStorage.getItem('symphony_active_tab') || 'today';", "const savedTab = localStorage.getItem('symphony_active_tab') || 'today';")

# Replace 'pool-week', 'timeline', 'timeline-span' drop zone scopes if necessary.
# Target zone queries: .drop-zone[data-time="${task.time_target}"]
# The JS doesn't strictly depend on #today, it queries globally for `.drop-zone` or `#pool-today`.
# Our python script moved these IDs along with the markup to #planner.
# We need to make sure `renderDraggableTimeline` still finds `#pool-today` (maybe rename it to pool-unscheduled?). No, pool-today is fine mechanically.

# 2. Need to change "Lock In" button behavior
# Currently, drop actions send PATCH immediately:
# `body: JSON.stringify({ time_target: task.time_target })` (in adjustTaskDuration)
# Drop event logic is further down. Let's find "drop".

# We'll use a simpler approach:
# We just need to implement the Read-Only logic for #today, and implement Lock-In button.

# Let's write the Read-Only render function.
readonly_render = """
    // --- READONLY TODAY VIEW ---
    async function fetchReadonlyToday() {
        try {
            const response = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true&select=*`, {
                method: 'GET',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': 'application/json'
                }
            });
            if (response.ok) {
                const allTasks = await response.json();
                renderReadonlyToday(allTasks);
            }
        } catch (e) {
            console.error("Error fetching readonly timeline:", e);
        }
    }

    function renderReadonlyToday(tasks) {
        const container = document.getElementById('today-schedule-readonly');
        if (!container) return;
        
        // Filter tasks that belong to the timeline
        let timelineTasks = tasks.filter(t => {
            if (!t.time_target) return false;
            // Match specific time "hh:mm AM" or range "hh:mm AM - hh:mm AM"
            return /^\\d{2}:\\d{2}\\s*(AM|PM)/i.test(t.time_target);
        });

        // Sort by time
        function timeToMinutes(timeStr) {
            const match = timeStr.trim().match(/^(\\d{2}):(\\d{2})\\s*(AM|PM)/i);
            if (!match) return 9999;
            let hours = parseInt(match[1]);
            const minutes = parseInt(match[2]);
            const period = match[3].toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            return hours * 60 + minutes;
        }

        timelineTasks.sort((a, b) => timeToMinutes(a.time_target) - timeToMinutes(b.time_target));

        let html = '<div style="font-family: \\'VT323\\', monospace; font-size: 1.1rem; border-left: 2px solid var(--glass-border); padding-left: 1rem; position: relative;">';
        
        let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
        
        if (timelineTasks.length === 0) {
            html += '<div style="color: var(--text-secondary); padding: 1rem;">No tasks locked in for today yet. Use the Planner to schedule your day.</div>';
        } else {
            timelineTasks.forEach(task => {
                const isCompletedToday = lastDoneDates[task.id] && (new Date(lastDoneDates[task.id]).toDateString() === new Date().toDateString());
                
                let colorBorder = 'var(--glass-border)';
                if (task.priority_color === 'RED') colorBorder = 'var(--accent-red)';
                if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange)';
                if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green)';

                const opacity = isCompletedToday ? '0.5' : '1';
                const decoration = isCompletedToday ? 'line-through' : 'none';
                const checkedState = isCompletedToday ? 'checked' : '';

                html += `
                    <div class="readonly-task" style="position: relative; margin-bottom: 1.5rem; display: flex; gap: 1rem;">
                        <div style="position: absolute; left: -1.45rem; top: 0.25rem; width: 12px; height: 12px; border-radius: 50%; background: ${colorBorder}; box-shadow: 0 0 5px ${colorBorder};"></div>
                        <div style="min-width: 90px; color: var(--accent-magenta); font-weight: bold; margin-top: 0.2rem;">${task.time_target}</div>
                        <div style="flex: 1; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); padding: 0.75rem; border-radius: 4px; border-left: 3px solid ${colorBorder}; opacity: ${opacity};">
                            <div style="display: flex; gap: 0.5rem; align-items: flex-start;">
                                <div class="checkbox completion-toggle readonly-tick" data-id="${task.id}" style="${isCompletedToday ? 'background:var(--accent-green);' : ''}"></div>
                                <div>
                                    <div style="font-weight: bold; text-decoration: ${decoration}; color: var(--text-primary); margin-bottom: 0.25rem;">${task.title} <span style="font-size: 0.8rem; color: var(--accent-blue); font-weight: normal;">[+${task.points} pts]</span></div>
                                    ${task.description ? `<div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem; text-decoration: ${decoration};">${task.description}</div>` : ''}
                                    <div style="display: flex; gap: 4px;">
                                        ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.75rem;">${t}</span>`).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        html += '</div>';
        container.innerHTML = html;

        // Attach listeners for ticks on readonly page
        container.querySelectorAll('.readonly-tick').forEach(tick => {
            tick.addEventListener('click', (e) => {
                e.preventDefault();
                const taskId = tick.getAttribute('data-id');
                const p = tick.parentElement.parentElement;
                
                let doneDict = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                const isCurrentlyDone = doneDict[taskId] && (new Date(doneDict[taskId]).toDateString() === new Date().toDateString());
                
                if (isCurrentlyDone) {
                    delete doneDict[taskId];
                    tick.style.background = 'transparent';
                    p.style.opacity = '1';
                    p.querySelector('div[style*="font-weight: bold"]').style.textDecoration = 'none';
                } else {
                    doneDict[taskId] = new Date().toISOString();
                    tick.style.background = 'var(--accent-green)';
                    p.style.opacity = '0.5';
                    p.querySelector('div[style*="font-weight: bold"]').style.textDecoration = 'line-through';
                }
                localStorage.setItem('symphony_last_done', JSON.stringify(doneDict));
                
                // Refresh both views
                fetchTasksAndRenderTimeline();
            });
        });
    }

    // Call fetchReadonlyToday when "today" tab is active.
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            if (targetId === 'today') fetchReadonlyToday();
        });
    });
    
    // Also call on boot if today tab is selected
    if (localStorage.getItem('symphony_active_tab') === 'today' || !localStorage.getItem('symphony_active_tab')) {
        fetchReadonlyToday();
    }
"""

insertion_point = content.find("function fetchTasksAndRenderTimeline() {")
content = content[:insertion_point] + readonly_render + "\n" + content[insertion_point:]

# 3. Modify Lock In button behavior
# Currently, it has id "lock-in-btn". We need to add an event listener to it.
lock_in_logic = """
    const lockInBtn = document.getElementById('lock-in-btn');
    if (lockInBtn) {
        lockInBtn.addEventListener('click', async () => {
            lockInBtn.innerText = "🔒 Locking...";
            lockInBtn.style.pointerEvents = 'none';
            // Actually, in the current app version, drops auto-save via PATCH.
            // We just sync data visually and show a flash message.
            alert("Schedule locked in! Switching to Today view.");
            activateTab('today');
            localStorage.setItem('symphony_active_tab', 'today');
            fetchReadonlyToday();
            
            lockInBtn.innerText = "🔒 Lock In";
            lockInBtn.style.pointerEvents = 'auto';
        });
    }
"""

end_of_file = content.rfind("});")
content = content[:end_of_file] + lock_in_logic + "\n" + content[end_of_file:]

# 4. In `fetchTasksAndRenderTimeline` success block, call `renderReadonlyToday(dynamicTasks)`
success_block = content.find("dynamicTasks = await response.json();\\n                renderDraggableTimeline();")
if success_block != -1:
    content = content.replace("dynamicTasks = await response.json();\\n                renderDraggableTimeline();", 
                              "dynamicTasks = await response.json();\\n                renderDraggableTimeline();\\n                renderReadonlyToday(dynamicTasks);")


with open('symphony-app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("symphony-app.js refactored successfully.")
