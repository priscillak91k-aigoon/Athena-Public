import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Fetch Expenses (GET)
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_expenses\?order=category\.asc,name\.asc`, \{[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/expenses`, {\n                    headers: {\n                        \'Authorization\': `Bearer ${API_TOKEN}`\n                    }\n                });',
    content
)

# 2. Sync missing IDs (POST)
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_expenses`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=minimal\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(\{ name: item\.name, amount: item\.amount, frequency: item\.frequency, category: item\.category \}\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/expenses`, {\n                                        method: \'POST\',\n                                        headers: {\n                                            \'Authorization\': `Bearer ${API_TOKEN}`,\n                                            \'Content-Type\': \'application/json\'\n                                        },\n                                        body: JSON.stringify({ name: item.name, amount: item.amount, frequency: item.frequency, category: item.category })\n                                    });',
    content
)

# 3. Delete Expense (DELETE)
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_expenses\?id=eq\.\$\{id\}`, \{[\s\n]*method: \'DELETE\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/expenses/${id}`, {\n                            method: \'DELETE\',\n                            headers: {\n                                \'Authorization\': `Bearer ${API_TOKEN}`\n                            }\n                        });',
    content
)

# 4. Add New Expense (POST)
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_expenses`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=representation\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(newExpense\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/expenses`, {\n                    method: \'POST\',\n                    headers: {\n                        \'Authorization\': `Bearer ${API_TOKEN}`,\n                        \'Content-Type\': \'application/json\'\n                    },\n                    body: JSON.stringify(newExpense)\n                });',
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Expenses API migration complete!")
