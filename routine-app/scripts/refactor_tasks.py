import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Task Pool Fetch
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master\?is_active=eq\.true&select=id,title,priority_color,time_target`, \{[\s\S]*?\}\);',
    r'await fetch(`${API_BASE}/tasks`, { headers: { "Authorization": `Bearer ${API_TOKEN}` } });',
    content
)

# Replace Timeline Fetch
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master\?is_active=eq\.true&select=\*`, \{[\s\S]*?\}\);',
    r'await fetch(`${API_BASE}/tasks`, { headers: { "Authorization": `Bearer ${API_TOKEN}` } });',
    content
)

# Replace Patch Task
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master\?id=eq\.\$\{taskId\}`, \{[\s\n]*method: \'PATCH\',[\s\n]*headers: \{[\s\S]*?\},[\s\n]*body: (.*?)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/tasks/${taskId}`, {\n                    method: "PATCH",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },\n                    body: \1\n                });',
    content
)

# Replace Delete Task
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master\?id=eq\.\$\{task\.id\}`, \{[\s\n]*method: \'DELETE\',[\s\n]*headers: \{[\s\S]*?\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/tasks/${task.id}`, {\n                            method: "DELETE",\n                            headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                        });',
    content
)

# Replace Multi-Patch Tasks (Drag and drop reordering)
# Wait, my regex might fail if it's too complex. Let's write it carefully.
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master\?id=eq\.\$\{update\.id\}`, \{[\s\n]*method: \'PATCH\',[\s\n]*headers: \{[\s\S]*?\},[\s\n]*body: JSON\.stringify\(\{ time_target: update\.time_target \}\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/tasks/${update.id}`, {\n                    method: "PATCH",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },\n                    body: JSON.stringify({ time_target: update.time_target })\n                });',
    content
)

# Replace Add Task
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_tasks_master`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\S]*?\},[\s\n]*body: (.*?)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/tasks`, {\n                    method: "POST",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },\n                    body: \1\n                });',
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Tasks API migration complete!")
