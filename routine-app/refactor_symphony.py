import re

with open('public/symphony-app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Inject apiFetch function right after API_BASE definition
api_fetch_code = """
async function apiFetch(endpoint, options = {}) {
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
    const isApi = url.startsWith(API_BASE);
    
    const headers = { ...options.headers };
    if (isApi) {
        headers['Authorization'] = `Bearer ${API_TOKEN}`;
    }
    
    const res = await fetch(url, { ...options, headers });
    
    if (isApi && !res.ok) {
        const detail = await res.text().catch(() => '');
        alert(`Data Sync Error!\\nAction failed: ${options.method || 'GET'} ${endpoint}\\nBackend replied: ${res.status} ${detail}\\n\\nRefreshing data to prevent corruption.`);
        if (typeof loadData === 'function') loadData();
        throw new Error(`${options.method || 'GET'} ${endpoint} -> ${res.status} ${detail}`);
    }
    return res;
}
"""

content = content.replace("const API_BASE = '/api';", "const API_BASE = '/api';\n" + api_fetch_code)

# 2. Replace all fetch calls to API_BASE with apiFetch
# Instead of complex regex for all 41 calls, we can just replace the fetch keyword 
# for everything that hits API_BASE. Since we have a wrapper that returns `res`, 
# the existing `.json()` or `.ok` checks in the code will still work perfectly!
# The only difference is `apiFetch` will throw an error automatically if it fails,
# triggering the catch blocks, which is exactly what we want.

content = content.replace("await fetch(`${API_BASE}", "await apiFetch(`")
content = content.replace("return fetch(`${API_BASE}", "return apiFetch(`")

# 3. Rename Supabase functions
content = content.replace("saveDayToSupabase", "saveDayToBackend")
content = content.replace("fetchHistoryFromSupabase", "fetchHistoryFromBackend")

with open('public/symphony-app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactored symphony-app.js successfully.")
