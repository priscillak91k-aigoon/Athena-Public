import re
import os

file_path = "c:/Users/prisc/Documents/Athena-Public/routine-app/server/server.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update static file serving and remove denylist shield
old_static_block = r'''// Security Shield: Prevent static file server from exposing backend code or databases
app\.use\(\(req, res, next\) => \{
    if \(req\.path\.startsWith\('/server'\) \|\| req\.path\.endsWith\('\.db'\) \|\| req\.path\.endsWith\('\.py'\) \|\| req\.path\.endsWith\('\.env'\)\) \{
        return res\.status\(403\)\.send\('Forbidden: Access to backend infrastructure is denied\.'\);
    \}
    next\(\);
\}\);

// Serve static frontend files \(must be before /api auth middleware\)
app\.use\(express\.static\(path\.join\(__dirname, '\.\.'\)\)\);'''

new_static_block = r'''// Serve strict allowlist frontend files
app.use(express.static(path.join(__dirname, '..', 'public')));'''

content = re.sub(old_static_block, new_static_block, content, flags=re.MULTILINE)

# 2. Fix API_TOKEN
old_token_block = r'''// --- Authentication Middleware ---
const API_TOKEN = process\.env\.API_TOKEN \|\| 'local_tailnet_token';'''

new_token_block = r'''// --- Authentication Middleware ---
const API_TOKEN = process.env.API_TOKEN;
if (!API_TOKEN) {
    console.error('FATAL: API_TOKEN is not set in .env. Refusing to start.');
    process.exit(1);
}'''

content = re.sub(old_token_block, new_token_block, content)

# 3. Fix 500 error leaking
# Current: if (err) return res.status(500).json({ error: err.message });
# Replace: if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
content = re.sub(
    r'if\s*\(err\)\s*return\s*res\.status\(500\)\.json\(\{\s*error:\s*err\.message\s*\}\);',
    r"if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }",
    content
)

# And similarly for err2
content = re.sub(
    r'if\s*\(err2\)\s*return\s*res\.status\(500\)\.json\(\{\s*error:\s*err2\.message\s*\}\);',
    r"if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }",
    content
)

# 4. Bind address and remove console.log(API_TOKEN)
old_listen_block = r'''app\.listen\(PORT, \(\) => \{
    console\.log\(`Sovereign Backend running on port \$\{PORT\}`\);
    console\.log\(`API Token in use: \$\{API_TOKEN\}`\);
\}\);'''

new_listen_block = r'''app.listen(PORT, '127.0.0.1', () => {
    console.log(`Sovereign Backend running on 127.0.0.1:${PORT}`);
});'''

content = re.sub(old_listen_block, new_listen_block, content)

# 5. Add body limit
content = content.replace("app.use(express.json());", "app.use(express.json({ limit: '1mb' }));")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Harden Server Script Complete.")
