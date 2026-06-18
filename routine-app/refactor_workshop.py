import re

with open('public/workshop.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Purge Supabase Auth & Add API layer
api_layer = """
        const API_BASE = '/api';
        const API_TOKEN = 'local_tailnet_token'; // Sovereign Node Auth

        async function apiFetch(endpoint, options = {}) {
            const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
            const headers = { 
                'Authorization': `Bearer ${API_TOKEN}`,
                ...options.headers 
            };
            if (options.body) headers['Content-Type'] = 'application/json';

            const res = await fetch(url, { ...options, headers });
            if (!res.ok) {
                const detail = await res.text().catch(() => '');
                alert(`Data Sync Error!\\nBackend replied: ${res.status} ${detail}\\n\\nRefreshing data to prevent corruption.`);
                if (typeof loadAll === 'function') loadAll();
                throw new Error(`${options.method || 'GET'} ${endpoint} -> ${res.status} ${detail}`);
            }
            return res.status === 204 ? null : res.json();
        }
"""

# Replace the supabase client block
content = re.sub(
    r"// SUPABASE CLIENT\s*const SUPABASE_ANON_KEY.*?supabase\.createClient\(SUPABASE_URL, SUPABASE_ANON_KEY\);",
    "// SOVEREIGN API CLIENT\n" + api_layer,
    content,
    flags=re.DOTALL
)

# 2. Replace db.from usages
replacements = {
    "const { data, error } = await db.from('workshop_ideas').insert({ text, category }).select().single();\n            if (error) { console.error('[Ideas] Insert failed:', error); return; }":
    "const data = await apiFetch('/workshop_ideas', { method: 'POST', body: JSON.stringify({ text, category }) });",

    "await db.from('workshop_ideas').delete().eq('id', id);":
    "await apiFetch(`/workshop_ideas/${id}`, { method: 'DELETE' });",

    "const { data } = await db.from('workshop_ideas').select('*').order('added_at', { ascending: false });":
    "const data = await apiFetch('/workshop_ideas');",

    "const { data, error } = await db.from('workshop_wishlists').insert({ name, price: price || null, link: link || null, why: why || null }).select().single();\n            if (error) { console.error('[Wishes] Insert failed:', error); return; }":
    "const data = await apiFetch('/workshop_wishlists', { method: 'POST', body: JSON.stringify({ name, price: price || null, link: link || null, why: why || null }) });",

    "await db.from('workshop_wishlists').delete().eq('id', id);":
    "await apiFetch(`/workshop_wishlists/${id}`, { method: 'DELETE' });",

    "const { data } = await db.from('workshop_wishlists').select('*').order('added_at', { ascending: false });":
    "const data = await apiFetch('/workshop_wishlists');",

    "const { data, error } = await db.from('workshop_lists').insert({ list_name: name, icon, items: [] }).select().single();\n            if (error) { console.error('[Lists] Insert failed:', error); return; }":
    "const data = await apiFetch('/workshop_lists', { method: 'POST', body: JSON.stringify({ name: name, icon, items: [] }) });",

    "const { data, error } = await db.from('workshop_lists').update({ items: newItems, updated_at: new Date().toISOString() }).eq('id', listId).select().single();\n            if (error) { console.error('[Lists] Update failed:', error); return; }":
    "await apiFetch(`/workshop_lists/${listId}`, { method: 'PATCH', body: JSON.stringify({ items: newItems }) });\n            const data = { id: listId, items: newItems };",

    "await db.from('workshop_lists').update({ items: list.items, updated_at: new Date().toISOString() }).eq('id', listId);":
    "await apiFetch(`/workshop_lists/${listId}`, { method: 'PATCH', body: JSON.stringify({ items: list.items }) });",

    "await db.from('workshop_lists').delete().eq('id', listId);":
    "await apiFetch(`/workshop_lists/${listId}`, { method: 'DELETE' });",

    "const { data } = await db.from('workshop_lists').select('*').order('updated_at', { ascending: false });":
    "const data = await apiFetch('/workshop_lists');",
}

for old, new_str in replacements.items():
    content = content.replace(old, new_str)

with open('public/workshop.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactored workshop.html successfully.")
