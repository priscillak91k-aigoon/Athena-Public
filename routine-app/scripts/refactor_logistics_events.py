import re
import os

file_path = "c:/Users/prisc/Documents/Athena-Public/routine-app/symphony-app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Logistics GETs
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics\?status=eq\.open&order=created_at\.desc`, \{\s*headers: \{ \'apikey\': SUPABASE_ANON_KEY, \'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}` \}\s*\}\)',
    r'fetch(`${API_BASE}/logistics?status=open`, {\n                    headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                })',
    content
)

content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics_subtasks\?order=created_at\.asc`, \{\s*headers: \{ \'apikey\': SUPABASE_ANON_KEY, \'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}` \}\s*\}\)',
    r'fetch(`${API_BASE}/logistics_subtasks`, {\n                        headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                    })',
    content
)

content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics\?status=eq\.done&order=updated_at\.desc`, \{\s*headers: \{ \'apikey\': SUPABASE_ANON_KEY, \'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}` \}\s*\}\)',
    r'fetch(`${API_BASE}/logistics?status=done`, {\n                            headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                        })',
    content
)

# Logistics POSTs
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics`, \{\s*method: \'POST\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,\s*\'Content-Type\': \'application/json\',\s*\'Prefer\': \'return=minimal\'\s*\},',
    r'fetch(`${API_BASE}/logistics`, {\n                    method: "POST",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },',
    content
)

content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics_subtasks`, \{\s*method: \'POST\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,\s*\'Content-Type\': \'application/json\',\s*\'Prefer\': \'return=minimal\'\s*\},',
    r'fetch(`${API_BASE}/logistics_subtasks`, {\n                    method: "POST",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },',
    content
)

# Logistics PATCHes
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics_subtasks\?id=eq\.\$\{subtaskId\}`, \{\s*method: \'PATCH\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,\s*\'Content-Type\': \'application/json\',\s*\'Prefer\': \'return=minimal\'\s*\},',
    r'fetch(`${API_BASE}/logistics_subtasks/${subtaskId}`, {\n                    method: "PATCH",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },',
    content
)

content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics\?id=eq\.\$\{itemId\}`, \{\s*method: \'PATCH\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,\s*\'Content-Type\': \'application/json\',\s*\'Prefer\': \'return=minimal\'\s*\},',
    r'fetch(`${API_BASE}/logistics/${itemId}`, {\n                    method: "PATCH",\n                    headers: {\n                        "Authorization": `Bearer ${API_TOKEN}`,\n                        "Content-Type": "application/json"\n                    },',
    content
)

# Logistics DELETE
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_logistics_subtasks\?id=eq\.\$\{subtaskId\}`, \{\s*method: \'DELETE\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`\s*\}\s*\}\)',
    r'fetch(`${API_BASE}/logistics_subtasks/${subtaskId}`, {\n                    method: "DELETE",\n                    headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                })',
    content
)

# Events GET
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_events\?order=event_date\.asc`, \{\s*headers: \{ \'apikey\': SUPABASE_ANON_KEY, \'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}` \}\s*\}\)',
    r'fetch(`${API_BASE}/events`, {\n                    headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                })',
    content
)

# Events DELETE
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_events\?id=eq\.\$\{id\}`, \{\s*method: \'DELETE\',\s*headers: \{ \'apikey\': SUPABASE_ANON_KEY, \'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}` \}\s*\}\)',
    r'fetch(`${API_BASE}/events/${id}`, {\n                            method: "DELETE",\n                            headers: { "Authorization": `Bearer ${API_TOKEN}` }\n                        })',
    content
)

# Events POST
content = re.sub(
    r'fetch\(`\$\{SUPABASE_URL\}/rest/v1/symphony_events`, \{\s*method: \'POST\',\s*headers: \{\s*\'apikey\': SUPABASE_ANON_KEY,\s*\'Authorization\': `Bearer \$\{SUPABASE_ANON_KEY\}`,\s*\'Content-Type\': \'application/json\',\s*\'Prefer\': \'return=minimal\'\s*\},',
    r'fetch(`${API_BASE}/events`, {\n                        method: "POST",\n                        headers: {\n                            "Authorization": `Bearer ${API_TOKEN}`,\n                            "Content-Type": "application/json"\n                        },',
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Refactored logistics and events fetches in symphony-app.js")
