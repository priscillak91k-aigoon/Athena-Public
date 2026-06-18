import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. GET food_log?date=eq
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_food_log\?date=eq\.\$\{dateStr\}&select=id`, \{[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/food_log?date=${dateStr}`, {\n                headers: {\n                    \'Authorization\': `Bearer ${API_TOKEN}`\n                }\n            });',
    content
)

# 2. PATCH food_log
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_food_log\?id=eq\.\$\{id\}`, \{[\s\n]*method: \'PATCH\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=minimal\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(\{ items, totals, grade, grade_score: score \}\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/food_log/${id}`, {\n                    method: \'PATCH\',\n                    headers: {\n                        \'Authorization\': `Bearer ${API_TOKEN}`,\n                        \'Content-Type\': \'application/json\'\n                    },\n                    body: JSON.stringify({ items, totals, grade, grade_score: score })\n                });',
    content
)

# 3. POST food_log
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_food_log`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=minimal\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(\{ date: dateStr, items, totals, grade, grade_score: score \}\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/food_log`, {\n                    method: \'POST\',\n                    headers: {\n                        \'Authorization\': `Bearer ${API_TOKEN}`,\n                        \'Content-Type\': \'application/json\'\n                    },\n                    body: JSON.stringify({ date: dateStr, items, totals, grade, grade_score: score })\n                });',
    content
)

# 4. GET food_log?date=gte
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_food_log\?date=gte\.\$\{dateStr\}&select=date,grade,grade_score,totals&order=date\.asc`, \{[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/food_log?date_gte=${dateStr}`, {\n                headers: {\n                    \'Authorization\': `Bearer ${API_TOKEN}`\n                }\n            });',
    content
)

# 5. POST food_recipes
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_food_recipes`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=minimal\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(recipe\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/food_recipes`, {\n                method: \'POST\',\n                headers: {\n                    \'Authorization\': `Bearer ${API_TOKEN}`,\n                    \'Content-Type\': \'application/json\'\n                },\n                body: JSON.stringify(recipe)\n            });',
    content
)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Food API migration complete!")
