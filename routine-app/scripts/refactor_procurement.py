import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. GET
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_procurement\?select=\*&order=created_at\.desc`, \{[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\'[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/procurement`, {\n                    headers: {\n                        \'Authorization\': `Bearer ${API_TOKEN}`,\n                        \'Content-Type\': \'application/json\'\n                    }\n                });',
    content
)

# 2. DELETE
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_procurement\?id=eq\.\$\{id\}`, \{[\s\n]*method: \'DELETE\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`[\s\n]*\}[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/procurement/${id}`, {\n                            method: \'DELETE\',\n                            headers: {\n                                \'Authorization\': `Bearer ${API_TOKEN}`\n                            }\n                        });',
    content
)

# 3. POST
content = re.sub(
    r'await fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_procurement`, \{[\s\n]*method: \'POST\',[\s\n]*headers: \{[\s\n]*\'apikey\': SUPABASE_ANON_KEY,[\s\n]*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,[\s\n]*\'Content-Type\': \'application/json\',[\s\n]*\'Prefer\': \'return=representation\'[\s\n]*\},[\s\n]*body: JSON\.stringify\(newItem\)[\s\n]*\}\);',
    r'await fetch(`${API_BASE}/procurement`, {\n                        method: \'POST\',\n                        headers: {\n                            \'Authorization\': `Bearer ${API_TOKEN}`,\n                            \'Content-Type\': \'application/json\'\n                        },\n                        body: JSON.stringify(newItem)\n                    });',
    content
)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Procurement API migration complete!")
