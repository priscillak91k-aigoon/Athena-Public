import re
import os

file_path = "c:/Users/prisc/Documents/Athena-Public/routine-app/public/symphony-app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

escape_func = """function escapeHTML(str) {
    if (typeof str !== 'string') return str;
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}
"""

if "function escapeHTML" not in content:
    content = content.replace("'use strict';", "'use strict';\n\n" + escape_func)

# We want to replace common variables inside template literals ${...} that go into innerHTML
# Known variables: task.title, task.description, s.name, item.title, event.title, etc.
# We will do simple re.sub for these exact patterns.

safe_vars = [
    'task.title', 'task.description', 't.title', 't.description',
    'idea.text', 'expense.name', 's.name', 's.justification', 's.athena_comment',
    'item.item', 'item.title', 'event.title', 'sub.title', 'newSupp.name', 'newExpense.name'
]

for var in safe_vars:
    # Replace ${var} with ${escapeHTML(var)}
    # But only if it's not already escaped
    pattern = r'\$\{' + var.replace('.', r'\.') + r'\}'
    replacement = f'${{escapeHTML({var})}}'
    content = re.sub(pattern, replacement, content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Sanitization Script Complete.")
