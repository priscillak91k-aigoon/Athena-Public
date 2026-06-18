import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacement = """                    if (completeBtn.checked) {
                        titleEl.style.opacity = '0.5';
                        titleEl.style.textDecoration = 'line-through';
                        task.completed = true;
                        fetch(`${API_BASE}/tasks/${task.id}/complete`, {
                            method: "POST",
                            headers: { "Authorization": `Bearer ${API_TOKEN}`, "Content-Type": "application/json" },
                            body: JSON.stringify({ completed: true })
                        }).catch(e => console.error(e));
                        
                        let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        lastDoneDates[task.id] = new Date().toISOString();
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        renderWeeklyMonthlyTracker();
                    } else {
                        titleEl.style.opacity = '1';
                        titleEl.style.textDecoration = 'none';
                        task.completed = false;
                        fetch(`${API_BASE}/tasks/${task.id}/complete`, {
                            method: "POST",
                            headers: { "Authorization": `Bearer ${API_TOKEN}`, "Content-Type": "application/json" },
                            body: JSON.stringify({ completed: false })
                        }).catch(e => console.error(e));
                        
                        let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        delete lastDoneDates[task.id];
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        renderWeeklyMonthlyTracker();
                    }"""

content = re.sub(
    r'                    if \(completeBtn\.checked\) \{[\s\n]*titleEl\.style\.opacity = \'0\.5\';[\s\n]*titleEl\.style\.textDecoration = \'line-through\';[\s\n]*let lastDoneDates = JSON\.parse\(localStorage\.getItem\(\'symphony_last_done\'\) \|\| \'\{\}\'\);[\s\n]*lastDoneDates\[task\.id\] = new Date\(\)\.toISOString\(\);[\s\n]*localStorage\.setItem\(\'symphony_last_done\', JSON\.stringify\(lastDoneDates\)\);[\s\n]*// Re-render trackers[\s\n]*renderWeeklyMonthlyTracker\(\);[\s\n]*\} else \{[\s\n]*titleEl\.style\.opacity = \'1\';[\s\n]*titleEl\.style\.textDecoration = \'none\';[\s\n]*// Remove last done date if un-toggled \(optional, but good for correcting mistakes\)[\s\n]*lastDoneDates = JSON\.parse\(localStorage\.getItem\(\'symphony_last_done\'\) \|\| \'\{\}\'\);[\s\n]*delete lastDoneDates\[task\.id\];[\s\n]*localStorage\.setItem\(\'symphony_last_done\', JSON\.stringify\(lastDoneDates\)\);[\s\n]*renderWeeklyMonthlyTracker\(\);[\s\n]*\}',
    replacement,
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Tasks completion API migration complete!")
