import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update tabs
content = content.replace('<button class="tab-btn" data-tab="weekly">Weekly/Monthly</button>', '<button class="tab-btn" data-tab="planner">Planner</button>')

# 2. Rename #weekly section to #planner
content = content.replace('<section id="weekly" class="tab-content glass-panel">', '<section id="planner" class="tab-content glass-panel">')
content = content.replace('<h2><span class="icon">📅</span> Weekly & Monthly Planner</h2>', '<h2><span class="icon">📅</span> Planner</h2>')

# 3. Extract today-grid
start_marker = '<div class="today-grid">'
end_marker = '<!-- Productivity & Gamification View -->'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

# Need to find the end of the today section, which is just before <section id="productivity"...
# Let's find the `</section>\n\n            <!-- Productivity & Gamification View -->`
section_end_idx = content.rfind('</section>', start_idx, end_idx)

today_grid_content = content[start_idx:section_end_idx]

# Remove it from #today
content = content[:start_idx] + '''
                <div id="today-schedule-readonly" style="display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; max-width: 800px; margin-left: auto; margin-right: auto; padding-bottom: 2rem;">
                    <div id="readonly-timeline">
                        <div style="color: var(--text-secondary); font-style: italic; text-align: center; padding: 2rem;">Loading today's schedule...</div>
                    </div>
                </div>
            ''' + content[section_end_idx:]

# 4. Insert today_grid_content into #planner
planner_end_idx = content.find('</section>', content.find('<section id="planner"'))
content = content[:planner_end_idx] + '\n                <!-- Drag and Drop Daily Planner -->\n                <hr style="border: 0; height: 1px; background: var(--glass-border); margin: 2rem 0;">\n                <h3 style="margin-bottom: 1rem; color: var(--accent-magenta);">Daily Schedule Planner</h3>\n                ' + today_grid_content + '\n            ' + content[planner_end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("index.html refactored successfully.")
