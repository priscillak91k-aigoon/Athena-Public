import re
import os

file_path = "c:/Users/prisc/Documents/Athena-Public/routine-app/server/server.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

validation_middleware = r'''// --- Input Validation Middleware ---
function validateBody(req, res, next) {
    if (req.body) {
        if (req.body.points !== undefined && typeof req.body.points !== 'number') return res.status(400).json({ error: 'points must be a number' });
        if (req.body.tilt_value !== undefined && typeof req.body.tilt_value !== 'number') return res.status(400).json({ error: 'tilt_value must be a number' });
        if (req.body.is_active !== undefined && typeof req.body.is_active !== 'boolean' && typeof req.body.is_active !== 'number') return res.status(400).json({ error: 'is_active must be boolean' });
        if (req.body.priority_color !== undefined && !['RED','YELLOW','GREEN','BLUE','PURPLE'].includes(req.body.priority_color)) return res.status(400).json({ error: 'invalid priority_color' });
    }
    next();
}

app.use('/api', validateBody);

// --- Endpoints ---'''

old_endpoints_marker = r'// --- Endpoints ---'

if "validateBody" not in content:
    content = content.replace(old_endpoints_marker, validation_middleware)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Validation Script Complete.")
