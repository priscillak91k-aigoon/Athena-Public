# CLAUDE CONTEXT DUMP: CURRENT SOVEREIGN STATE

> Claude, you are reading the CURRENT, mathematical reality of the codebase. Discard any old project files you have read. This is the exact state of the air-gapped system. Do not deviate from the local-only execution model.

## ..\infrastructure\sj_atom\claude_handoff.md
`markdown
# CLAUDE HANDOFF: SOVEREIGN LIFEHUB INFRASTRUCTURE

> **SYSTEM PRIMER FOR CLAUDE**: You are inheriting this architecture from Lobotto. This environment is mathematically hardened, air-gapped, and sovereign. Do not assume cloud deployment. Do not suggest adding external services, analytics, or Vercel/Supabase integrations. The Combat Protocol is active: prioritize resilience, zero-trust routing, and local-only execution. Do not break the air-gap.

## 1. The Core Objective
We successfully decoupled the user's `LifeHub` application from Supabase and deployed it to a local, headless Ubuntu ARM64 workstation (the "Atom"). The application now runs 100% locally, with zero public internet exposure.

## 2. Network Topology & Routing
- **Transport Layer**: All traffic routes through a zero-trust Tailscale network. The Atom's Tailscale IP is `100.103.179.49`.
- **DNS Resolution**: Tailscale MagicDNS was bypassing local TLDs, so we bypassed it. The Windows client (FURY) has a mathematically hardcoded `hosts` file routing `hub.atom.tailnet` directly to the Atom's Tailscale IP.
- **Firewall (UFW)**: The Atom's `ufw` firewall is aggressively configured. It was dropping standard web traffic, so we explicitly whitelisted `80/tcp` and `443/tcp` for the `tailscale0` interface. 

## 3. The Proxy Stack (Caddy)
- **Container**: `caddy:latest` running on the Docker bridge network.
- **Configuration**: The `Caddyfile` uses the `local_certs` directive to generate its own self-signed internal certificates (because Let's Encrypt cannot verify air-gapped domains).
- **Routing**: Caddy intercepts requests for `hub.atom.tailnet` and reverse proxies them to the internal `lifehub` container on port `8086`.
- **Trust Store**: Caddy's generated Root CA (`root.crt`) was extracted and injected directly into FURY's Windows Trusted Root Certification Authorities store to permanently silence browser security warnings.

## 4. The Backend (Node.js & SQLite)
- **Container**: `sj_proxy-lifehub` (Node 20 Alpine).
- **Environment**: Because `.env` files were failing on the sovereign node, environment variables (`PORT=8086`, `API_TOKEN=local_tailnet_token`) are injected directly into the `docker-compose-proxy.yml` file.
- **Database**: Supabase is dead. The backend initializes and connects to a sovereign SQLite database mapped to a physical volume on the Atom (`/home/sj/Athena-Public/routine-app/server/data/lifehub.db`).

## 5. The Backup Pipeline
- **Mechanism**: Data resilience is handled by `restic`, which provides deduplicated, encrypted, and immutable snapshots.
- **Scope**: The script `backup_to_qnap.sh` backs up both the system infrastructure config and the new SQLite database directory.
- **Automation**: The script is bound to an hourly `crontab` on the Atom, pushing the backups to the local QNAP array.

## 6. The Frontend
- The `symphony-app.js` frontend script was aggressively purged using a Python refactoring script. All references to Supabase, cloud endpoints, and remote fetching have been rewritten to reflect the new `LocalAPI` and `Backend` nomenclature.

## Current Status
The stack is stable, operational, and heavily armored. If the user asks you to audit it, check the code for any lingering external API calls or non-relative fetches. If you write new code, ensure it adheres strictly to the offline-first, local-storage, and local-SQLite methodology.

`

## ..\infrastructure\sj_atom\docker-compose-proxy.yml
`yaml
version: "3.8"
name: sj_proxy
services:
  caddy:
    image: caddy:latest
    container_name: caddy-proxy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - ./data/caddy/data:/data
      - ./data/caddy/config:/config
      # Mount the local drop folder to act as a static HTML file server
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Standalone HTTP Server for the Drop Page (Bypasses UFW firewall via Docker bridge)
  drop_page:
    image: python:3-slim
    container_name: drop_page
    restart: unless-stopped
    volumes:
      - ./data/drop:/var/www/drop
    working_dir: /var/www/drop
    command: python -m http.server 8085
    ports:
      - "8085:8085"

  # LifeHub Sovereign Backend
  lifehub:
    build: ../../routine-app
    container_name: lifehub
    restart: unless-stopped
    environment:
      - PORT=8086
      - API_TOKEN=local_tailnet_token
    volumes:
      - ../../routine-app/server/data:/app/server/data
    ports:
      - "127.0.0.1:8086:8086"

`

## ..\infrastructure\sj_atom\Caddyfile
`text
# Global options
{
    # Force Caddy to use internal self-signed certificates for everything
    # This completely stops Let's Encrypt from crashing when MagicDNS fails
    local_certs
    debug
    default_sni 100.73.93.94
}

# Strict IP route for HTTPS only
https://100.73.93.94 {
    tls internal
    reverse_proxy vaultwarden:80
}

vault.atom.tailnet {
    tls internal
    reverse_proxy vaultwarden:80
}

memos.atom.tailnet {
    reverse_proxy 100.73.93.94:5230
}

dna.atom.tailnet {
    reverse_proxy 100.73.93.94:8888
}

wiki.atom.tailnet {
    reverse_proxy 100.73.93.94:8081
}

audio.atom.tailnet {
    reverse_proxy 100.73.93.94:13378
}

ai.atom.tailnet {
    reverse_proxy 100.73.93.94:3000
}

agent.atom.tailnet {
    reverse_proxy 100.73.93.94:5678
}

search.atom.tailnet {
    reverse_proxy 100.73.93.94:8082
}

sync.atom.tailnet {
    reverse_proxy 100.73.93.94:8384
}

tts.atom.tailnet {
    reverse_proxy 100.73.93.94:7860
}

seerr.atom.tailnet {
    reverse_proxy 100.73.93.94:5055
}

media.atom.tailnet {
    reverse_proxy 100.73.93.94:8096
}

hub.atom.tailnet {
    reverse_proxy lifehub:8086
}

sonarr.atom.tailnet {
    reverse_proxy 100.73.93.94:8989
}

radarr.atom.tailnet {
    reverse_proxy 100.73.93.94:7878
}

qbit.atom.tailnet {
    reverse_proxy 100.73.93.94:8088
}

prowlarr.atom.tailnet {
    reverse_proxy 100.73.93.94:9696
}

`

## ..\infrastructure\sj_atom\backup_to_qnap.sh
`bash
#!/bin/bash
# Phase 5: Zero-Trust Automated Backup Script (v2 - True Failsafe)
# Syncs infrastructure state and cognitive air-gap to the QNAP array
# using restic for encrypted, deduplicated, immutable snapshots.
# 
# To install as an hourly cron job:
# run `sudo crontab -e` and add the following line:
# 0 * * * * /home/sj/Athena-Public/infrastructure/sj_atom/backup_to_qnap.sh >> /var/log/qnap_backup.log 2>&1

set -e

# Load environment for Telegram Tokens
if [ -f "/home/sj/Athena-Public/.env" ]; then
    export $(grep -v '^#' /home/sj/Athena-Public/.env | xargs)
fi

notify_failure() {
    echo "[$(date)] 🚨 CRITICAL ERROR: Backup script failed on line $1"
    if [ -n "$TELEGRAM_ARCHITECT_TOKEN" ] && [ -n "$TELEGRAM_ALLOWED_USER_ID" ]; then
        # -s for silent, -o /dev/null to discard response body, preventing token leak in logs
        curl -s -o /dev/null -X POST "https://api.telegram.org/bot${TELEGRAM_ARCHITECT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_ALLOWED_USER_ID}" \
            -d text="🚨 CRITICAL: Restic backup of Sovereign Vault FAILED. Check logs immediately." || true
    fi
}

trap 'notify_failure $LINENO' ERR

# RESTIC_PASSWORD must be set in .env. The previous key was compromised.
if [ -z "$RESTIC_PASSWORD" ]; then
    echo "🚨 ERROR: RESTIC_PASSWORD not found in .env. Halting backup."
    notify_failure $LINENO
    exit 1
fi
REPO_DEST="/mnt/qnap/atom_backups_restic"

INFRA_DIR="/home/sj/Athena-Public/infrastructure/sj_atom/data"
DB_DIR="/home/sj/Athena-Public/routine-app/server/data"
CONTEXT_DIR="/home/sj/context"

echo "[$(date)] Starting Phase 5 Restic Backup..."

# 1. Initialize repo if it doesn't exist
if [ ! -f "$REPO_DEST/config" ]; then
    echo "[$(date)] Initializing restic repository at $REPO_DEST..."
    mkdir -p "$REPO_DEST"
    restic init --repo "$REPO_DEST"
fi

# 2. Perform live, zero-downtime backup
echo "[$(date)] Backing up infrastructure data ($INFRA_DIR)..."
restic -r "$REPO_DEST" backup "$INFRA_DIR"

if [ -d "$DB_DIR" ]; then
    echo "[$(date)] Backing up SQLite database ($DB_DIR)..."
    restic -r "$REPO_DEST" backup "$DB_DIR"
else
    echo "[WARNING] $DB_DIR not found. Skipping database backup."
fi

if [ -d "$CONTEXT_DIR" ]; then
    echo "[$(date)] Backing up cognitive air-gap ($CONTEXT_DIR)..."
    restic -r "$REPO_DEST" backup "$CONTEXT_DIR"
else
    echo "[WARNING] $CONTEXT_DIR not found. Skipping air-gap backup."
fi

# 3. Prune old snapshots (Retention Policy: Keep last 24 hourly, last 7 daily, last 4 weekly, last 12 monthly)
echo "[$(date)] Pruning old snapshots..."
restic -r "$REPO_DEST" forget --keep-hourly 24 --keep-daily 7 --keep-weekly 4 --keep-monthly 12 --prune

echo "[$(date)] Backup complete! No containers were harmed (or stopped) in the making of this snapshot."

# Dead-Man's Switch: Ping Healthchecks.io on absolute success
if [ -n "$HEALTHCHECK_URL" ]; then
    # Timeout 10s, retry up to 3 times, silence output.
    curl -m 10 --retry 3 -s -o /dev/null "$HEALTHCHECK_URL" || echo "[$(date)] WARNING: Healthcheck ping failed to transmit."
fi

`

## Dockerfile
`dockerfile
FROM node:20-alpine

# Install sqlite3 dependencies for node-sqlite3
RUN apk add --no-cache python3 make g++ sqlite

WORKDIR /app

# Copy package files
COPY server/package*.json ./

# Install dependencies (rebuilds sqlite3 for Alpine architecture)
RUN npm install

# Copy application files
# We copy public/ into /app/public and server/ into /app/server
COPY public ./public
COPY server ./server

WORKDIR /app/server

# Expose the API port
EXPOSE 8086

# Start the server
CMD ["node", "server.js"]

`

## server\package.json
`json
{
  "name": "server",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "type": "commonjs",
  "dependencies": {
    "cors": "^2.8.6",
    "dotenv": "^17.4.2",
    "express": "^5.2.1",
    "sqlite3": "^6.0.1"
  }
}

`

## server\server.js
`javascript
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');
const crypto = require('crypto');
const db = require('./database');

dotenv.config();

const app = express();
app.use(express.json({ limit: '1mb' }));

// --- CORS: zero-trust posture ---------------------------------------------
// The frontend is served same-origin (/api), so it does NOT need CORS at all —
// the browser skips CORS checks for same-origin requests. We therefore only emit
// CORS headers for an explicit allowlist (set ALLOWED_ORIGINS in .env, comma-
// separated). Unknown origins get NO headers (so cross-origin JS can't read
// responses) but we never throw — same-origin keeps working. This replaces the
// old wide-open cors() which let any website on the tailnet drive the API.
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || '')
    .split(',').map(s => s.trim()).filter(Boolean);
app.use(cors({
    origin(origin, cb) {
        if (!origin || ALLOWED_ORIGINS.includes(origin)) return cb(null, true);
        return cb(null, false); // no ACAO header; browser blocks the read
    }
}));

// Serve strict allowlist frontend files
app.use(express.static(path.join(__dirname, '..', 'public')));

// --- Authentication Middleware ---
const API_TOKEN = process.env.API_TOKEN;
if (!API_TOKEN) {
    console.error('FATAL: API_TOKEN is not set in .env. Refusing to start.');
    process.exit(1);
}

function requireAuth(req, res, next) {
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({ error: 'Unauthorized: Missing or invalid token format' });
    }
    const token = authHeader.split(' ')[1];
    if (token !== API_TOKEN) {
        return res.status(403).json({ error: 'Forbidden: Invalid token' });
    }
    next();
}

app.use('/api', requireAuth);

// --- Input Validation Middleware ---
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

// --- Endpoints ---

// 1. Get today's shadow balance
app.get('/api/shadow/balance', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    db.get(`SELECT tilt_value FROM shadow_balances WHERE date = ?`, [today], (err, row) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ tilt_value: row ? row.tilt_value : 0 });
    });
});

// 2. Update today's shadow balance
app.post('/api/shadow/balance', (req, res) => {
    const { tilt_value } = req.body;
    if (tilt_value === undefined) return res.status(400).json({ error: 'Missing tilt_value' });

    const today = new Date().toISOString().split('T')[0];

    db.run(`
        INSERT INTO shadow_balances (date, tilt_value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(date) DO UPDATE SET tilt_value = ?, updated_at = CURRENT_TIMESTAMP
    `, [today, tilt_value, tilt_value], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, tilt_value });
    });
});

// 3. Get latest shadow journal (today's draft)
app.get('/api/shadow/journal', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    db.get(`SELECT prompt, entry_text FROM shadow_journals WHERE date = ? ORDER BY id DESC LIMIT 1`, [today], (err, row) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(row || { prompt: '', entry_text: '' });
    });
});

// 4. Save shadow journal entry
app.post('/api/shadow/journal', (req, res) => {
    const { prompt, entry_text } = req.body;
    if (!prompt || entry_text === undefined) return res.status(400).json({ error: 'Missing prompt or entry_text' });

    const today = new Date().toISOString().split('T')[0];
    db.run(`INSERT INTO shadow_journals (date, prompt, entry_text) VALUES (?, ?, ?)`,
    [today, prompt, entry_text], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, id: this.lastID });
    });
});

// 5. Save 3-Chair Exercise
app.post('/api/shadow/chair', (req, res) => {
    const { ego_text, shadow_text, self_text, trigger_context } = req.body;
    const today = new Date().toISOString().split('T')[0];

    db.run(`INSERT INTO chair_exercises (date, trigger_context, ego_text, shadow_text, self_text) VALUES (?, ?, ?, ?, ?)`,
    [today, trigger_context || '', ego_text || '', shadow_text || '', self_text || ''], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, id: this.lastID });
    });
});

// 5b. Get latest 3-Chair Exercise (today's draft)
app.get('/api/shadow/chair', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    db.get(`SELECT trigger_context, ego_text, shadow_text, self_text FROM chair_exercises WHERE date = ? ORDER BY id DESC LIMIT 1`, [today], (err, row) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(row || { trigger_context: '', ego_text: '', shadow_text: '', self_text: '' });
    });
});

// 6. Get all active tasks and today's completions
app.get('/api/tasks', (req, res) => {
    const today = new Date().toISOString().split('T')[0];
    const query = `
        SELECT t.*,
               CASE WHEN c.date IS NOT NULL THEN 1 ELSE 0 END as completed_today
        FROM tasks t
        LEFT JOIN task_completions c ON t.id = c.task_id AND c.date = ?
        WHERE t.is_active = 1
    `;
    db.all(query, [today], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }

        const tasks = rows.map(row => {
            let tags = [];
            if (row.tags) {
                try { tags = JSON.parse(row.tags); }
                catch (e) { console.error('Bad tags JSON for task', row.id, '-', e.message); }
            }
            return { ...row, tags, is_active: !!row.is_active, completed: !!row.completed_today };
        });

        res.json(tasks);
    });
});

// 7. Add a new task
app.post('/api/tasks', (req, res) => {
    const id = req.body.id || crypto.randomUUID();
    const { title, description, points, priority_color, time_target, is_active, tags } = req.body;

    if (!title) return res.status(400).json({ error: 'Missing title' });

    const isActive = is_active !== undefined ? (is_active ? 1 : 0) : 1;
    const tagsStr = tags ? JSON.stringify(tags) : null;

    db.run(
        `INSERT INTO tasks (id, title, description, points, priority_color, time_target, is_active, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [id, title, description || null, points || 0, priority_color || 'GREEN', time_target || null, isActive, tagsStr],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, id: id });
        }
    );
});

// 8. Update a task
app.patch('/api/tasks/:id', (req, res) => {
    const id = req.params.id;
    const updates = [];
    const params = [];

    const allowedFields = ['title', 'description', 'points', 'priority_color', 'time_target', 'is_active', 'tags'];

    allowedFields.forEach(field => {
        if (req.body[field] !== undefined) {
            updates.push(`${field} = ?`);
            let val = req.body[field];
            if (field === 'is_active') val = val ? 1 : 0;
            if (field === 'tags') val = val ? JSON.stringify(val) : null;
            params.push(val);
        }
    });

    if (updates.length === 0) return res.status(400).json({ error: 'No valid fields to update' });

    params.push(id);

    db.run(`UPDATE tasks SET ${updates.join(', ')} WHERE id = ?`, params, function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// 9. Soft Delete task
app.delete('/api/tasks/:id', (req, res) => {
    const id = req.params.id;
    db.run(`UPDATE tasks SET is_active = 0 WHERE id = ?`, [id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// 10. Toggle completion for today
app.post('/api/tasks/:id/complete', (req, res) => {
    const id = req.params.id;
    const { completed } = req.body;
    const today = new Date().toISOString().split('T')[0];

    if (completed === true) {
        db.run(`INSERT OR IGNORE INTO task_completions (task_id, date) VALUES (?, ?)`, [id, today], function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, completed: true });
        });
    } else {
        db.run(`DELETE FROM task_completions WHERE task_id = ? AND date = ?`, [id, today], function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, completed: false });
        });
    }
});

// --- Ideas / Bucket Lists ---

// 11. Get ideas by list_type
app.get('/api/ideas', (req, res) => {
    const listType = req.query.list_type;
    if (!listType) return res.status(400).json({ error: 'Missing list_type query param' });

    db.all(`SELECT * FROM ideas WHERE list_type = ? ORDER BY sort_order ASC, created_at ASC`, [listType], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows.map(r => ({ ...r, completed: !!r.completed })));
    });
});

// 12. Add a new idea
app.post('/api/ideas', (req, res) => {
    const { list_type, text, completed, sort_order } = req.body;
    if (!list_type || !text) return res.status(400).json({ error: 'Missing list_type or text' });

    db.run(`INSERT INTO ideas (list_type, text, completed, sort_order) VALUES (?, ?, ?, ?)`,
        [list_type, text, completed ? 1 : 0, sort_order || 0],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM ideas WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row, completed: !!row.completed }]);
            });
        }
    );
});

// 13. Update an idea
app.patch('/api/ideas/:id', (req, res) => {
    const id = req.params.id;
    const updates = [];
    const params = [];

    if (req.body.completed !== undefined) { updates.push('completed = ?'); params.push(req.body.completed ? 1 : 0); }
    if (req.body.text !== undefined) { updates.push('text = ?'); params.push(req.body.text); }
    if (req.body.sort_order !== undefined) { updates.push('sort_order = ?'); params.push(req.body.sort_order); }
    updates.push('updated_at = CURRENT_TIMESTAMP');

    if (updates.length === 1) return res.status(400).json({ error: 'No valid fields to update' });

    params.push(id);
    db.run(`UPDATE ideas SET ${updates.join(', ')} WHERE id = ?`, params, function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// 14. Delete an idea
app.delete('/api/ideas/:id', (req, res) => {
    db.run(`DELETE FROM ideas WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- Expenses ---

// 15. Get all expenses
app.get('/api/expenses', (req, res) => {
    db.all(`SELECT * FROM expenses ORDER BY category ASC, name ASC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

// 16. Add a new expense
app.post('/api/expenses', (req, res) => {
    const { name, amount, frequency, category } = req.body;
    if (!name || amount === undefined || !frequency || !category) {
        return res.status(400).json({ error: 'Missing required expense fields' });
    }
    if (typeof amount !== 'number' || Number.isNaN(amount)) {
        return res.status(400).json({ error: 'amount must be a number' });
    }

    db.run(`INSERT INTO expenses (name, amount, frequency, category) VALUES (?, ?, ?, ?)`,
        [name, amount, frequency, category],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM expenses WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row }]);
            });
        }
    );
});

// 17. Delete an expense
app.delete('/api/expenses/:id', (req, res) => {
    db.run(`DELETE FROM expenses WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- Food Log & Recipes ---

// 18. Get food log
app.get('/api/food_log', (req, res) => {
    const { date, date_gte } = req.query;
    if (date) {
        db.all(`SELECT * FROM food_log WHERE date = ?`, [date], (err, rows) => {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json(rows.map(r => ({ ...r, items: safeParse(r.items, []), totals: safeParse(r.totals, {}) })));
        });
    } else if (date_gte) {
        db.all(`SELECT date, grade, grade_score, totals FROM food_log WHERE date >= ? ORDER BY date ASC`, [date_gte], (err, rows) => {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json(rows.map(r => ({ ...r, totals: safeParse(r.totals, {}) })));
        });
    } else {
        res.status(400).json({ error: 'Missing date or date_gte param' });
    }
});

// 19. Add (or upsert) food log entry. date is UNIQUE; a second POST for the same
// day used to throw a constraint error and 500. Now it updates in place.
app.post('/api/food_log', (req, res) => {
    const { date, items, totals, grade, grade_score } = req.body;
    if (!date) return res.status(400).json({ error: 'Missing date' });
    db.run(`INSERT INTO food_log (date, items, totals, grade, grade_score)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                items = excluded.items,
                totals = excluded.totals,
                grade = excluded.grade,
                grade_score = excluded.grade_score,
                updated_at = CURRENT_TIMESTAMP`,
        [date, JSON.stringify(items), JSON.stringify(totals), grade, grade_score],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, id: this.lastID });
        }
    );
});

// 20. Update food log entry
app.patch('/api/food_log/:id', (req, res) => {
    const id = req.params.id;
    const { items, totals, grade, grade_score } = req.body;
    db.run(`UPDATE food_log SET items = ?, totals = ?, grade = ?, grade_score = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
        [JSON.stringify(items), JSON.stringify(totals), grade, grade_score, id],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, changes: this.changes });
        }
    );
});

// 21. Add food recipe
app.post('/api/food_recipes', (req, res) => {
    const { name, items } = req.body;
    db.run(`INSERT INTO food_recipes (name, items) VALUES (?, ?)`,
        [name, JSON.stringify(items)],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, id: this.lastID });
        }
    );
});

// --- Procurement ---

// 22. Get all procurement items
app.get('/api/procurement', (req, res) => {
    db.all(`SELECT * FROM procurement ORDER BY created_at DESC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

// 23. Add a new procurement item
app.post('/api/procurement', (req, res) => {
    const { item, justification, category, athena_verdict, athena_comment } = req.body;
    db.run(`INSERT INTO procurement (item, justification, category, athena_verdict, athena_comment) VALUES (?, ?, ?, ?, ?)`,
        [item, justification, category, athena_verdict, athena_comment],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM procurement WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row }]);
            });
        }
    );
});

// 24. Delete a procurement item
app.delete('/api/procurement/:id', (req, res) => {
    db.run(`DELETE FROM procurement WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- Supplement Inventory ---

// 25. Get all supplements
app.get('/api/supp_inventory', (req, res) => {
    db.all(`SELECT * FROM supp_inventory ORDER BY name ASC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

// 26. Add a new supplement
app.post('/api/supp_inventory', (req, res) => {
    const { name, total_capacity, current_stock, daily_dose } = req.body;
    if (!name) return res.status(400).json({ error: 'Missing name' });
    for (const [k, v] of Object.entries({ total_capacity, current_stock, daily_dose })) {
        if (typeof v !== 'number' || Number.isNaN(v)) return res.status(400).json({ error: `${k} must be a number` });
    }
    db.run(`INSERT INTO supp_inventory (name, total_capacity, current_stock, daily_dose) VALUES (?, ?, ?, ?)`,
        [name, total_capacity, current_stock, daily_dose],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM supp_inventory WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row }]);
            });
        }
    );
});

// 27. Update supplement stock
app.patch('/api/supp_inventory/:id', (req, res) => {
    const { current_stock } = req.body;
    db.run(`UPDATE supp_inventory SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
        [current_stock, req.params.id],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true, changes: this.changes });
        }
    );
});

// --- Logistics ---
app.get('/api/logistics', (req, res) => {
    const status = req.query.status;
    let query = `SELECT * FROM logistics`;
    let params = [];
    if (status) {
        query += ` WHERE status = ?`;
        params.push(status);
    }
    query += ` ORDER BY created_at DESC`;
    db.all(query, params, (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

app.post('/api/logistics', (req, res) => {
    const { title, status, urgency, priority } = req.body;
    db.run(`INSERT INTO logistics (title, status, urgency, priority) VALUES (?, ?, ?, ?)`,
        [title, status || 'open', urgency, priority],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM logistics WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row }]);
            });
        }
    );
});

app.patch('/api/logistics/:id', (req, res) => {
    const { title, urgency, priority, status } = req.body;

    if (status !== undefined && title === undefined) {
        db.run(`UPDATE logistics SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
            [status, req.params.id], function(err) {
                if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json({ success: true });
            });
    } else {
        db.run(`UPDATE logistics SET title = ?, urgency = ?, priority = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
            [title, urgency, priority, req.params.id], function(err) {
                if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json({ success: true });
            });
    }
});

// --- Logistics Subtasks ---
app.get('/api/logistics_subtasks', (req, res) => {
    db.all(`SELECT * FROM logistics_subtasks ORDER BY created_at ASC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

app.post('/api/logistics_subtasks', (req, res) => {
    const { logistics_id, title, is_done } = req.body;
    db.run(`INSERT INTO logistics_subtasks (logistics_id, title, is_done) VALUES (?, ?, ?)`,
        [logistics_id, title, is_done ? 1 : 0],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json([{ id: this.lastID, logistics_id, title, is_done }]);
        }
    );
});

app.patch('/api/logistics_subtasks/:id', (req, res) => {
    const { is_done } = req.body;
    db.run(`UPDATE logistics_subtasks SET is_done = ? WHERE id = ?`,
        [is_done ? 1 : 0, req.params.id], function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            res.json({ success: true });
        });
});

app.delete('/api/logistics_subtasks/:id', (req, res) => {
    db.run(`DELETE FROM logistics_subtasks WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true });
    });
});

// --- Events ---
app.get('/api/events', (req, res) => {
    db.all(`SELECT * FROM events ORDER BY event_date ASC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

app.post('/api/events', (req, res) => {
    const { title, event_date, type } = req.body;
    db.run(`INSERT INTO events (title, event_date, type) VALUES (?, ?, ?)`,
        [title, event_date, type],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM events WHERE id = ?`, [this.lastID], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json([{ ...row }]);
            });
        }
    );
});

app.delete('/api/events/:id', (req, res) => {
    db.run(`DELETE FROM events WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true });
    });
});

// --- Workshop: Ideas (sovereign replacement for Supabase workshop_ideas) ---
app.get('/api/workshop_ideas', (req, res) => {
    db.all(`SELECT * FROM workshop_ideas ORDER BY added_at DESC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

app.post('/api/workshop_ideas', (req, res) => {
    const { text, category } = req.body;
    if (!text) return res.status(400).json({ error: 'Missing text' });
    const id = crypto.randomUUID();
    db.run(`INSERT INTO workshop_ideas (id, text, category) VALUES (?, ?, ?)`,
        [id, text, category || 'general'],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM workshop_ideas WHERE id = ?`, [id], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json(row);
            });
        }
    );
});

app.delete('/api/workshop_ideas/:id', (req, res) => {
    db.run(`DELETE FROM workshop_ideas WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- Workshop: Wishlists ---
app.get('/api/workshop_wishlists', (req, res) => {
    db.all(`SELECT * FROM workshop_wishlists ORDER BY added_at DESC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows);
    });
});

app.post('/api/workshop_wishlists', (req, res) => {
    const { name, price, link, why } = req.body;
    if (!name) return res.status(400).json({ error: 'Missing name' });
    const id = crypto.randomUUID();
    db.run(`INSERT INTO workshop_wishlists (id, name, price, link, why) VALUES (?, ?, ?, ?, ?)`,
        [id, name, price || null, link || null, why || null],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM workshop_wishlists WHERE id = ?`, [id], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json(row);
            });
        }
    );
});

app.delete('/api/workshop_wishlists/:id', (req, res) => {
    db.run(`DELETE FROM workshop_wishlists WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- Workshop: Lists (items stored as JSON array) ---
app.get('/api/workshop_lists', (req, res) => {
    db.all(`SELECT * FROM workshop_lists ORDER BY updated_at DESC`, [], (err, rows) => {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json(rows.map(r => ({ ...r, items: safeParse(r.items, []) })));
    });
});

app.post('/api/workshop_lists', (req, res) => {
    const { list_name, icon, items } = req.body;
    if (!list_name) return res.status(400).json({ error: 'Missing list_name' });
    const id = crypto.randomUUID();
    db.run(`INSERT INTO workshop_lists (id, list_name, icon, items) VALUES (?, ?, ?, ?)`,
        [id, list_name, icon || '', JSON.stringify(Array.isArray(items) ? items : [])],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM workshop_lists WHERE id = ?`, [id], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                res.json({ ...row, items: safeParse(row.items, []) });
            });
        }
    );
});

app.patch('/api/workshop_lists/:id', (req, res) => {
    const { items } = req.body;
    if (!Array.isArray(items)) return res.status(400).json({ error: 'items must be an array' });
    db.run(`UPDATE workshop_lists SET items = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?`,
        [JSON.stringify(items), req.params.id],
        function(err) {
            if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
            db.get(`SELECT * FROM workshop_lists WHERE id = ?`, [req.params.id], (err2, row) => {
                if (err2) { console.error('DB Error:', err2.message); return res.status(500).json({ error: 'Internal server error' }); }
                if (!row) return res.status(404).json({ error: 'List not found' });
                res.json({ ...row, items: safeParse(row.items, []) });
            });
        }
    );
});

app.delete('/api/workshop_lists/:id', (req, res) => {
    db.run(`DELETE FROM workshop_lists WHERE id = ?`, [req.params.id], function(err) {
        if (err) { console.error('DB Error:', err.message); return res.status(500).json({ error: 'Internal server error' }); }
        res.json({ success: true, changes: this.changes });
    });
});

// --- helpers ---
function safeParse(str, fallback) {
    if (str === null || str === undefined) return fallback;
    try { return JSON.parse(str); }
    catch (e) { console.error('JSON parse failed:', e.message); return fallback; }
}

const PORT = process.env.PORT || 8086;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Sovereign Backend running on 0.0.0.0:${PORT} (Docker Bridge)`);
});

`

## server\database.js
`javascript
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir);
}

const dbPath = path.join(dataDir, 'lifehub.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        // Fail loudly. A backend with no DB is useless; refuse to limp on.
        console.error('FATAL: Error opening database:', err.message);
        process.exit(1);
    }
    console.log(`Connected to the SQLite database at ${dbPath}`);
    db.run('PRAGMA foreign_keys = ON;');
    // WAL survives power loss better than the default rollback journal and lets
    // reads proceed while a write holds the lock (fewer SQLITE_BUSY errors).
    db.run('PRAGMA journal_mode = WAL;');
    db.run('PRAGMA busy_timeout = 5000;'); // wait up to 5s instead of throwing SQLITE_BUSY
    initializeTables();
});

function initializeTables() {
    db.serialize(() => {
        db.run(`CREATE TABLE IF NOT EXISTS shadow_journals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            prompt TEXT NOT NULL,
            entry_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS shadow_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            tilt_value INTEGER NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS chair_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            trigger_context TEXT,
            ego_text TEXT,
            shadow_text TEXT,
            self_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        // tasks.id is a UUID string
        db.run(`CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            points INTEGER DEFAULT 0,
            priority_color TEXT,
            time_target TEXT,
            is_active INTEGER DEFAULT 1,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        // task_id is TEXT to match tasks.id (a UUID). Previously declared INTEGER,
        // which only worked by accident via SQLite type affinity.
        db.run(`CREATE TABLE IF NOT EXISTS task_completions (
            task_id TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (task_id, date),
            FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_type TEXT NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            frequency TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            items TEXT NOT NULL,
            totals TEXT NOT NULL,
            grade TEXT,
            grade_score INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS food_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            items TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS procurement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            justification TEXT,
            category TEXT NOT NULL,
            athena_verdict TEXT,
            athena_comment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS supp_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_capacity REAL NOT NULL,
            current_stock REAL NOT NULL,
            daily_dose REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS logistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            urgency TEXT,
            priority TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS logistics_subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            logistics_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_done BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(logistics_id) REFERENCES logistics(id) ON DELETE CASCADE
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        // ── Workshop tables (formerly Supabase cloud — now sovereign) ──────────
        // UUID TEXT ids so workshop.html can keep treating ids as opaque strings.
        db.run(`CREATE TABLE IF NOT EXISTS workshop_ideas (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            category TEXT,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS workshop_wishlists (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price TEXT,
            link TEXT,
            why TEXT,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`);

        db.run(`CREATE TABLE IF NOT EXISTS workshop_lists (
            id TEXT PRIMARY KEY,
            list_name TEXT NOT NULL,
            icon TEXT,
            items TEXT NOT NULL DEFAULT '[]',
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )`, (err) => {
            if (err) console.error('DB Error creating workshop_lists:', err.message);
            console.log('Database tables initialized successfully.');
            migrateTaskCompletions();
        });
    });
}

/**
 * One-time, idempotent, transactional migration of task_completions.task_id
 * from INTEGER to TEXT. Runs only if the live table still declares INTEGER.
 * The transaction makes it power-failure safe: a crash mid-migration rolls back
 * to the (still-working) old table rather than leaving a half-built one.
 */
function migrateTaskCompletions() {
    db.all(`PRAGMA table_info(task_completions)`, (err, cols) => {
        if (err) { console.error('Migration check failed:', err.message); return; }
        const col = cols.find(c => c.name === 'task_id');
        if (!col || (col.type || '').toUpperCase() === 'TEXT') return; // nothing to do

        console.log('[migrate] task_completions.task_id is', col.type, '- rebuilding as TEXT...');
        db.serialize(() => {
            db.run('BEGIN IMMEDIATE TRANSACTION;');
            db.run(`CREATE TABLE IF NOT EXISTS task_completions_new (
                task_id TEXT NOT NULL,
                date TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (task_id, date),
                FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )`);
            db.run(`INSERT OR IGNORE INTO task_completions_new (task_id, date, created_at)
                    SELECT CAST(task_id AS TEXT), date, created_at FROM task_completions`);
            db.run('DROP TABLE task_completions;');
            db.run('ALTER TABLE task_completions_new RENAME TO task_completions;');
            db.run('COMMIT;', (commitErr) => {
                if (commitErr) {
                    console.error('[migrate] FAILED, rolling back:', commitErr.message);
                    db.run('ROLLBACK;');
                } else {
                    console.log('[migrate] task_completions.task_id is now TEXT.');
                }
            });
        });
    });
}

module.exports = db;

`

## public\controller-designs.html
`html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xbox Controller Design Lab — Favourites</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0e14;
            color: #e8f0f2;
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            padding: 2rem;
        }

        h1 {
            font-family: ui-monospace, monospace;
            font-size: 2.2rem;
            color: #00c9a0;
            letter-spacing: 2px;
            text-align: center;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            text-align: center;
            color: rgba(232, 240, 242, 0.45);
            font-size: 0.85rem;
            margin-bottom: 2.5rem;
        }

        .designs {
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
            max-width: 1100px;
            margin: 0 auto;
        }

        .card {
            background: rgba(4, 18, 18, 0.7);
            border: 1px solid rgba(64, 224, 208, 0.12);
            border-radius: 8px;
            overflow: hidden;
            transition: border-color 0.2s;
        }

        .card:hover {
            border-color: rgba(64, 224, 208, 0.35);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.25rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .card-name {
            font-family: ui-monospace, monospace;
            font-size: 1.4rem;
            letter-spacing: 1px;
        }

        .badge {
            font-size: 0.72rem;
            padding: 3px 10px;
            border-radius: 3px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-love {
            background: rgba(244, 63, 94, 0.15);
            border: 1px solid rgba(244, 63, 94, 0.3);
            color: #f43f5e;
        }

        .badge-like {
            background: rgba(56, 189, 248, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: #38bdf8;
        }

        .card-body {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
        }

        @media (max-width: 700px) {
            .card-body {
                grid-template-columns: 1fr;
            }
        }

        .card-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            min-height: 280px;
            display: block;
        }

        .parts {
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .parts-title {
            font-size: 0.75rem;
            color: rgba(232, 240, 242, 0.4);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }

        .part-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            padding: 5px 8px;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.03);
        }

        .swatch {
            width: 22px;
            height: 22px;
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            flex-shrink: 0;
        }

        .part-label {
            font-size: 0.8rem;
            color: rgba(232, 240, 242, 0.6);
            flex-shrink: 0;
            min-width: 85px;
        }

        .part-color {
            font-family: ui-monospace, monospace;
            font-size: 0.9rem;
            color: #e8f0f2;
        }

        .part-hex {
            font-size: 0.7rem;
            color: rgba(232, 240, 242, 0.3);
            margin-left: auto;
            font-family: ui-monospace, monospace;
        }

        .design-lab-note {
            margin-top: auto;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.72rem;
            color: rgba(232, 240, 242, 0.3);
            font-style: italic;
        }
    </style>
</head>

<body>
    <h1>🎮 XBOX DESIGN LAB — YOUR PICKS</h1>
    <p class="subtitle">Colour selections mapped to Design Lab parts</p>

    <div class="designs">

        <!-- CYBERPUNK — LOVE -->
        <div class="card">
            <div class="card-header">
                <span class="card-name" style="color:#facc15;">⚡ CYBERPUNK</span>
                <span class="badge badge-love">❤️ LOVE</span>
            </div>
            <div class="card-body">
                <img src="controller_cyberpunk.png" class="card-img" alt="Cyberpunk design">
                <div class="parts">
                    <div class="parts-title">Design Lab Selections</div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Body</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Back</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#facc15;"></div>
                        <span class="part-label">D-pad</span>
                        <span class="part-color">Electric Volt</span>
                        <span class="part-hex">#FACC15</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#facc15;"></div>
                        <span class="part-label">Thumbsticks</span>
                        <span class="part-color">Electric Volt</span>
                        <span class="part-hex">#FACC15</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#dc2626;"></div>
                        <span class="part-label">Bumpers</span>
                        <span class="part-color">Pulse Red</span>
                        <span class="part-hex">#DC2626</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#dc2626;"></div>
                        <span class="part-label">Triggers</span>
                        <span class="part-color">Pulse Red</span>
                        <span class="part-hex">#DC2626</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">ABXY</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch"
                            style="background:rgba(40,40,40,0.6); backdrop-filter:blur(2px); border:1px solid rgba(255,255,255,0.1);">
                        </div>
                        <span class="part-label">Grips</span>
                        <span class="part-color">Dark Smoke Translucent</span>
                        <span class="part-hex">SMOKE</span>
                    </div>
                    <div class="design-lab-note">Closest Design Lab match: Carbon Black body + Pulse Red
                        bumpers/triggers + Lighting Bolt yellow accents</div>
                </div>
            </div>
        </div>

        <!-- SYNTHWAVE — LOVE -->
        <div class="card">
            <div class="card-header">
                <span class="card-name" style="color:#c084fc;">🌌 SYNTHWAVE</span>
                <span class="badge badge-love">❤️ LOVE</span>
            </div>
            <div class="card-body">
                <img src="controller_synthwave.png" class="card-img" alt="Synthwave design">
                <div class="parts">
                    <div class="parts-title">Design Lab Selections</div>
                    <div class="part-row">
                        <div class="swatch" style="background:#4c1d95;"></div>
                        <span class="part-label">Body</span>
                        <span class="part-color">Astral Purple</span>
                        <span class="part-hex">#4C1D95</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#4c1d95;"></div>
                        <span class="part-label">Back</span>
                        <span class="part-color">Astral Purple</span>
                        <span class="part-hex">#4C1D95</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#06b6d4;"></div>
                        <span class="part-label">D-pad</span>
                        <span class="part-color">Dragonfly Blue</span>
                        <span class="part-hex">#06B6D4</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#06b6d4;"></div>
                        <span class="part-label">Thumbsticks</span>
                        <span class="part-color">Dragonfly Blue</span>
                        <span class="part-hex">#06B6D4</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#ec4899;"></div>
                        <span class="part-label">Bumpers</span>
                        <span class="part-color">Deep Pink</span>
                        <span class="part-hex">#EC4899</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#ec4899;"></div>
                        <span class="part-label">Triggers</span>
                        <span class="part-color">Deep Pink</span>
                        <span class="part-hex">#EC4899</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">ABXY</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Grips</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="design-lab-note">Closest: Astral Purple body + Deep Pink bumpers/triggers + Dragonfly
                        Blue D-pad</div>
                </div>
            </div>
        </div>

        <!-- DUAL NEON — LIKE -->
        <div class="card">
            <div class="card-header">
                <span class="card-name"
                    style="background: linear-gradient(90deg, #ec4899, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">🔮
                    DUAL NEON HYBRID</span>
                <span class="badge badge-like">👍 LIKE</span>
            </div>
            <div class="card-body">
                <img src="controller_dualneon.png" class="card-img" alt="Dual Neon design">
                <div class="parts">
                    <div class="parts-title">Design Lab Selections</div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Body</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Back</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#ec4899;"></div>
                        <span class="part-label">D-pad</span>
                        <span class="part-color">Deep Pink</span>
                        <span class="part-hex">#EC4899</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#7c3aed;"></div>
                        <span class="part-label">Thumbsticks</span>
                        <span class="part-color">Astral Purple</span>
                        <span class="part-hex">#7C3AED</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#06b6d4;"></div>
                        <span class="part-label">Bumpers</span>
                        <span class="part-color">Dragonfly Blue</span>
                        <span class="part-hex">#06B6D4</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#06b6d4;"></div>
                        <span class="part-label">Triggers</span>
                        <span class="part-color">Dragonfly Blue</span>
                        <span class="part-hex">#06B6D4</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">ABXY</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:rgba(40,40,40,0.6);"></div>
                        <span class="part-label">Grips</span>
                        <span class="part-color">Dark Smoke Translucent</span>
                        <span class="part-hex">SMOKE</span>
                    </div>
                    <div class="design-lab-note">Closest: Carbon Black body + Deep Pink D-pad + Dragonfly Blue bumpers +
                        Astral Purple sticks</div>
                </div>
            </div>
        </div>

        <!-- NEON NOIR — LIKE -->
        <div class="card">
            <div class="card-header">
                <span class="card-name" style="color:#f472b6;">🖤 NEON NOIR</span>
                <span class="badge badge-like">👍 LIKE</span>
            </div>
            <div class="card-body">
                <img src="controller_neonnoir.png" class="card-img" alt="Neon Noir design">
                <div class="parts">
                    <div class="parts-title">Design Lab Selections</div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Body</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">Back</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#f472b6;"></div>
                        <span class="part-label">D-pad</span>
                        <span class="part-color">Hot Pink</span>
                        <span class="part-hex">#F472B6</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#f472b6;"></div>
                        <span class="part-label">Thumbsticks</span>
                        <span class="part-color">Hot Pink</span>
                        <span class="part-hex">#F472B6</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#7c3aed;"></div>
                        <span class="part-label">Bumpers</span>
                        <span class="part-color">Astral Purple</span>
                        <span class="part-hex">#7C3AED</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#7c3aed;"></div>
                        <span class="part-label">Triggers</span>
                        <span class="part-color">Astral Purple</span>
                        <span class="part-hex">#7C3AED</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:#1a1a1a;"></div>
                        <span class="part-label">ABXY</span>
                        <span class="part-color">Carbon Black</span>
                        <span class="part-hex">#1A1A1A</span>
                    </div>
                    <div class="part-row">
                        <div class="swatch" style="background:rgba(76,29,149,0.4); border-color:rgba(124,58,237,0.3);">
                        </div>
                        <span class="part-label">Grips</span>
                        <span class="part-color">Purple Translucent</span>
                        <span class="part-hex">PURPLE</span>
                    </div>
                    <div class="design-lab-note">Closest: Carbon Black body + Deep Pink D-pad/sticks + Astral Purple
                        bumpers/triggers</div>
                </div>
            </div>
        </div>

    </div>

    <p
        style="text-align:center; color:rgba(232,240,242,0.2); font-size:0.7rem; margin-top:3rem; font-family: ui-monospace, monospace;">
        Xbox Design Lab Reference — Session 57 — xboxdesignlab.xbox.com
    </p>
</body>

</html>
`

## public\index.html
`html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Life Hub | Daily Routine Optimizer</title>
                <link rel="stylesheet" href="styles.css?v=4">
</head>

<body>
    <div class="background-effects">
        <div class="blur-blob blob-1"></div>
        <div class="blur-blob blob-2"></div>
    </div>

    <!-- UI ERROR LOGGER (Injected first) -->
    <div id="sys-error-overlay"
        style="display: none; position: fixed; bottom: 20px; right: 20px; width: 400px; max-width: 90vw; background: #c0c0c0; border: 2px outset #ffffff; border-top: 2px outset #ffffff; border-left: 2px outset #ffffff; border-bottom: 2px inset #808080; border-right: 2px inset #808080; z-index: 99999; font-family: 'MS Sans Serif', 'VT323', monospace; color: #000; padding: 0;">
        <div style="background: #000080; color: #fff; padding: 4px 8px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; cursor: pointer;"
            onclick="document.getElementById('sys-error-overlay').style.display = 'none';">
            <span>⚠️ System Diagnostic Logger</span>
            <span
                style="background: #c0c0c0; color: #000; border: 1px outset #fff; padding: 0 4px; font-size: 10px;">X</span>
        </div>
        <div id="sys-error-content"
            style="padding: 8px; font-size: 0.9rem; max-height: 250px; overflow-y: auto; background: #fff; border: 2px inset #808080; margin: 4px;">
            <i>Waiting for events...</i>
        </div>
        <div style="padding: 4px; display: flex; gap: 4px;">
            <button onclick="clearErrorLog()"
                style="flex: 1; padding: 2px; background: #c0c0c0; border: 2px outset #fff; font-family: ui-monospace, monospace;">Clear</button>
            <button onclick="downloadErrorLog()"
                style="flex: 1; padding: 2px; background: #c0c0c0; border: 2px outset #fff; font-family: ui-monospace, monospace;">Export</button>
        </div>
    </div>

    <!-- MAIN ERROR SCRIPT -->
    <script>
        const ERROR_LOG_KEY = 'sys_error_events';
        window._sysErrors = [];

        function getSavedErrors() {
            try { return JSON.parse(localStorage.getItem(ERROR_LOG_KEY)) || []; }
            catch (e) { return []; }
        }

        function saveError(type, msg, source, line) {
            const errors = getSavedErrors();
            const timestamp = new Date().toISOString();
            const errObj = { timestamp, type, msg, source, line };
            errors.unshift(errObj); // Add to beginning
            if (errors.length > 50) errors.pop(); // Keep last 50
            try { localStorage.setItem(ERROR_LOG_KEY, JSON.stringify(errors)); } catch (e) { }
            updateOverlay(errObj);
        }

        function updateOverlay(errStr) {
            const overlay = document.getElementById('sys-error-overlay');
            const content = document.getElementById('sys-error-content');
            overlay.style.display = 'block';
            let formatted = `[${new Date(errStr.timestamp).toLocaleTimeString()}] <b>${errStr.type}</b>:<br>${errStr.msg}`;
            if (errStr.source) formatted += `<br><small>${errStr.source}:${errStr.line || '?'}</small>`;

            const div = document.createElement('div');
            div.style.borderBottom = "1px solid #ccc";
            div.style.marginBottom = "4px";
            div.style.paddingBottom = "4px";
            div.innerHTML = formatted;

            if (content.innerHTML.includes('Waiting for events')) {
                content.innerHTML = '';
            }
            content.insertBefore(div, content.firstChild);
        }

        function clearErrorLog() {
            localStorage.removeItem(ERROR_LOG_KEY);
            document.getElementById('sys-error-content').innerHTML = '<i>Waiting for events...</i>';
            document.getElementById('sys-error-overlay').style.display = 'none';
        }

        function downloadErrorLog() {
            const errors = getSavedErrors();
            const blob = new Blob([JSON.stringify(errors, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `sys_errors_${new Date().getTime()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }

        // 1. Uncaught Exceptions (e.g. ReferenceError)
        window.onerror = function (msg, url, lineNo, columnNo, error) {
            saveError('UNCAUGHT', msg, url, lineNo);
            return false;
        };

        // 2. Unhandled Promise Rejections (e.g. failed fetch not caught)
        window.addEventListener('unhandledrejection', function (event) {
            saveError('PROMISE', event.reason?.message || event.reason, '', '');
        });

        // 3. Intercept console.error to show in the logger as well
        const originalConsoleError = console.error;
        console.error = function (...args) {
            const msg = args.map(a => typeof a === 'object' ? JSON.stringify(a) : a).join(' ');
            saveError('CONSOLE', msg, 'symphony-app.js', '');
            originalConsoleError.apply(console, args);
        };

        // Load existing errors on boot
        window.addEventListener('DOMContentLoaded', () => {
            const saved = getSavedErrors();
            if (saved.length > 0 && confirm('Previous system errors detected in memory. Show trace logger?')) {
                const overlay = document.getElementById('sys-error-overlay');
                const content = document.getElementById('sys-error-content');
                content.innerHTML = '';
                saved.slice(0, 5).forEach(err => updateOverlay(err)); // Show top 5
                overlay.style.display = 'block';
            }
        });
    </script>

    <!-- Main App Content -->
    <div class="app-container" id="app-content">
        <header class="glass-panel" style="position: relative;">
            <div class="date-display">
                <span id="current-date">Loading...</span>
                <span class="badge">Day Off</span>
            </div>
            <h1>The Life Hub</h1>
            <p class="subtitle">Your dynamic routine tracker & visual schedule.</p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-end; margin-top: 10px;">
                <a href="workshop.html"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #c084fc; color: #c084fc; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #c084fc; text-decoration: none;"
                    title="My Workshop">⚒ Workshop</a>
                <a href="toolbox.html"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #f59e0b; color: #f59e0b; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #f59e0b; text-decoration: none;"
                    title="Toolbox - Ad-Free Utilities">🔧 Toolbox</a>
                <a href="shadow.html"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #818cf8; color: #818cf8; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #818cf8; text-decoration: none;"
                    title="Shadow Protocol">🌑 Shadow Work</a>
                <a href="workout.html"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #00c9a0; color: #00c9a0; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #00c9a0; text-decoration: none;"
                    title="Workout Routine">💪 Workout</a>
                <a href="https://hub.atom.tailnet" target="_blank"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #10B981; color: #10B981; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #10B981; text-decoration: none;"
                    title="SJ's Infrastructure (Secure Node)">🟢 SJ Hub</a>
                <button id="audio-toggle" onclick="toggleRetroAudio()"
                    style="background: rgba(0,0,0,0.6); border: 1px solid #0f0; color: #0f0; font-family: ui-monospace, monospace; font-size: 1rem; padding: 6px 12px; cursor: pointer; border-radius: 4px; text-shadow: 0 0 4px #0f0;"
                    title="Toggle Music">🔊 Music</button>
            </div>
        </header>

        <div class="tabs">
            <button class="tab-btn active" data-tab="pulse"
                style="color: var(--accent-yellow); text-shadow: 0 0 5px var(--accent-yellow); font-weight: 700;">⚡
                Pulse</button>
            <button class="tab-btn" data-tab="today">Today's Schedule</button>
            <button class="tab-btn" data-tab="finances">Finances</button>
            <button class="tab-btn" data-tab="planner">Planner</button>
            <button class="tab-btn" data-tab="dog">Quinny</button>
            <button class="tab-btn" data-tab="workout">Workout</button>
            <button class="tab-btn" data-tab="bio">Bio Tracking</button>
            <button class="tab-btn" data-tab="food">Food Metrics</button>
            <button class="tab-btn" data-tab="logistics"
                style="color: var(--accent-blue); text-shadow: 0 0 5px var(--accent-blue);">🔧 Logistics</button>
            <button class="tab-btn" data-tab="manual"
                style="color: var(--accent-magenta); text-shadow: 0 0 5px var(--accent-magenta);">User Manual</button>
            <button class="tab-btn" data-tab="supps"
                style="color: var(--accent-green); text-shadow: 0 0 5px var(--accent-green);">Supps Vault</button>
            <button class="tab-btn" data-tab="misc"
                style="color: var(--accent-purple); text-shadow: 0 0 5px var(--accent-purple);">✦ Misc</button>
        </div>

        <main class="content-area">
            <!-- Pulse Overview -->
            <section id="pulse" class="tab-content active glass-panel">
                <div class="section-header">
                    <h2><span class="icon">⚡</span> Pulse</h2>
                    <p class="sub-text">Your at-a-glance command center. Alerts, progress, and things that need
                        attention.</p>
                </div>

                <!-- Morning Briefing -->
                <div class="glass-panel"
                    style="padding: 1.25rem; margin-bottom: 1.5rem; border-color: rgba(251,191,36,0.4); background: linear-gradient(135deg, rgba(251,191,36,0.08) 0%, rgba(239,68,68,0.04) 100%);">
                    <h3 style="margin: 0 0 0.5rem 0; color: var(--accent-yellow); font-size: 1.1rem;">
                        🌅 Read First Thing Every Morning
                    </h3>
                    <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Quick
                        reminders, things to ask people, stuff to do first thing. This is the first thing you see.</p>
                    <div id="morning-read-display"
                        style="font-size: 0.9rem; color: var(--text-primary); line-height: 1.7; white-space: pre-wrap; min-height: 2rem; padding: 0.75rem; background: rgba(0,0,0,0.2); border: 1px solid rgba(251,191,36,0.15); border-radius: 3px; cursor: pointer;"
                        title="Click to edit">
                        Click here to write your morning intentions...
                    </div>
                    <textarea id="morning-read-editor"
                        style="display: none; width: 100%; min-height: 120px; padding: 0.75rem; background: rgba(0,0,0,0.3); border: 2px solid var(--accent-yellow); color: #fff; font-family: ui-monospace, monospace; font-size: 1rem; line-height: 1.6; resize: vertical; border-radius: 3px;"
                        placeholder="Write what you need to remember every morning...&#10;&#10;Examples:&#10;• Ask Parker to show me how he rides his bike&#10;• Check if Quinny's worming is due&#10;• Pick up parcel from post office&#10;• Call dentist to reschedule&#10;• Defrost chicken for dinner"></textarea>
                    <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.5rem;">
                        <button id="morning-read-edit-btn"
                            style="padding: 0.3rem 0.8rem; background: rgba(251,191,36,0.15); border: 1px solid rgba(251,191,36,0.3); color: var(--accent-yellow); font-family: ui-monospace, monospace; font-size: 0.85rem; cursor: pointer; border-radius: 3px;">✏️
                            Edit</button>
                        <button id="morning-read-save-btn"
                            style="display: none; padding: 0.3rem 0.8rem; background: rgba(52,211,153,0.2); border: 1px solid var(--accent-green); color: var(--accent-green); font-family: ui-monospace, monospace; font-size: 0.85rem; cursor: pointer; border-radius: 3px;">💾
                            Save</button>
                    </div>
                </div>

                <!-- Pulse Grid -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">

                    <!-- Today's Progress -->
                    <div class="glass-panel" style="padding: 1.25rem; border-color: rgba(52,211,153,0.3);">
                        <h3 style="margin: 0 0 0.75rem 0; color: var(--accent-green); font-size: 1rem;">
                            📊 Today's Progress
                        </h3>
                        <div id="pulse-today-summary"
                            style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                            Loading...
                        </div>
                    </div>

                    <!-- Open Logistics -->
                    <div class="glass-panel" style="padding: 1.25rem; border-color: rgba(56,189,248,0.3);">
                        <h3 style="margin: 0 0 0.75rem 0; color: var(--accent-blue); font-size: 1rem;">
                            🔧 Open Logistics
                        </h3>
                        <div id="pulse-logistics"
                            style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                            Loading...
                        </div>
                    </div>
                </div>

                <!-- Alerts Row -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">

                    <!-- Low Stock Supplements -->
                    <div class="glass-panel" style="padding: 1.25rem; border-color: rgba(239,68,68,0.3);">
                        <h3 style="margin: 0 0 0.75rem 0; color: var(--accent-red); font-size: 1rem;">
                            💊 Supp Alerts
                        </h3>

                        <!-- Daily Protocol Tracker -->
                        <div id="pulse-supps-daily"
                            style="font-size: 0.95rem; font-weight: bold; margin-bottom: 0.5rem; border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom: 0.5rem; color: var(--text-primary);">
                            Loading Daily Status...
                        </div>

                        <div id="pulse-supps"
                            style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                            Loading...
                        </div>
                    </div>

                    <!-- Medical / Genetic Alerts -->
                    <div class="glass-panel" style="padding: 1.25rem; border-color: rgba(239,68,68,0.3);">
                        <h3 style="margin: 0 0 0.75rem 0; color: var(--accent-red); font-size: 1rem;">
                            🚨 Medical Flags
                        </h3>
                        <div id="pulse-medical"
                            style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                            Loading...
                        </div>
                    </div>
                </div>

                <!-- Financial Snapshot -->
                <div class="glass-panel" style="padding: 1.25rem; border-color: rgba(52,211,153,0.3);">
                    <h3 style="margin: 0 0 0.75rem 0; color: var(--accent-green); font-size: 1rem;">
                        💰 Financial Snapshot
                    </h3>
                    <div id="pulse-finance" style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                        Loading...
                    </div>
                </div>

            </section>

            <!-- Today's View (Readonly Week Schedule) -->
            <section id="today" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">📅</span> Weekly Schedule</h2>
                    <p class="sub-text">Read-only view of your planned week. Edit in Planner.</p>
                </div>
                <!-- Colour Legend -->
                <div style="display:flex; gap:1rem; margin-bottom:1rem; font-size:0.82rem; flex-wrap:wrap;">
                    <span><span
                            style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#ef4444;margin-right:4px;"></span><strong>Red</strong>
                        Routine</span>
                    <span><span
                            style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f97316;margin-right:4px;"></span><strong>Orange</strong>
                        Recurring</span>
                    <span><span
                            style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#a855f7;margin-right:4px;"></span><strong>Purple</strong>
                        One-off</span>
                </div>
                <div id="schedule-week-grid" style="overflow-x:auto;"></div>
            </section>


            <!-- Finances View -->
            <section id="finances" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">💰</span> Financial Overview</h2>
                    <p class="sub-text">Weekly Income & Tax Breakdown (NZD)</p>
                </div>

                <div class="grid-2-col">
                    <div class="sub-panel">
                        <h3>Income Summary</h3>
                        <div
                            style="margin-top: 1rem; padding: 1rem; background: rgba(52, 211, 153, 0.1); border: 1px solid var(--accent-green); border-radius: var(--radius-sm); text-align: center;">
                            <span
                                style="font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase;">Estimated
                                Net Weekly Pay</span>
                            <div id="finance-net-pay"
                                style="font-size: 2.5rem; font-weight: 700; color: var(--accent-green); margin: 0.5rem 0;">
                                $0.00</div>
                        </div>

                        <div
                            style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; background: rgba(0, 0, 0, 0.05); padding: 1rem; border: 1px solid var(--glass-border); border-radius: 0;">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <label for="input-hours" style="font-weight: bold; color: var(--text-secondary);">Hours
                                    Worked:</label>
                                <input type="number" id="input-hours" value="28.5" step="0.5" min="0"
                                    style="width: 80px; padding: 0.25rem; font-family: ui-monospace, monospace; font-size: 1.2rem; border: 2px inset var(--win-shadow);">
                            </div>
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <label style="font-weight: bold; color: var(--text-secondary);">Public Holiday (1.5x
                                    pay):</label>
                                <div class="checkbox" id="input-holiday" style="margin-top: 0;"></div>
                            </div>
                        </div>

                        <ul class="workout-list" style="margin-top: 1.5rem;">
                            <li style="display:flex; justify-content:space-between;"><span>Hours Worked</span>
                                <strong id="finance-hours">0 hrs</strong>
                            </li>
                            <li style="display:flex; justify-content:space-between;"><span>Gross Income (@
                                    $24/hr)</span> <strong id="finance-gross">$0.00</strong></li>
                            <li style="display:flex; justify-content:space-between; color: #ef4444;"><span>PAYE Tax
                                    (M
                                    SL)</span> <strong id="finance-tax">-$0.00</strong></li>
                            <li style="display:flex; justify-content:space-between; color: #ef4444;"><span>Student
                                    Loan
                                    (12%)</span> <strong id="finance-sl">-$0.00</strong></li>
                            <li style="display:flex; justify-content:space-between; color: var(--accent-blue);">
                                <span>KiwiSaver (3%)</span> <strong id="finance-ks">-$0.00</strong>
                            </li>
                        </ul>
                    </div>

                    <div class="sub-panel"
                        style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <h3>Distribution Breakdown</h3>
                        <div style="position: relative; height: 200px; width: 100%; margin-top: 1rem;">
                            <canvas id="financePieChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Yearly Income Projection -->
                <div class="sub-panel" style="margin-top: 1.5rem; border-color: rgba(56, 189, 248, 0.3);">
                    <h3 style="color: var(--accent-blue);">📊 Yearly Income Projection</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div
                            style="padding: 1rem; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); text-align: center;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">
                                Baseline (28.5h/wk)</div>
                            <div id="finance-yearly-baseline-gross"
                                style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0.25rem 0;">
                                $0</div>
                            <div style="font-size: 0.7rem; color: var(--text-secondary);">gross / year</div>
                            <div id="finance-yearly-baseline-net"
                                style="font-size: 1.4rem; font-weight: 700; color: var(--accent-blue); margin-top: 0.25rem;">
                                $0</div>
                            <div style="font-size: 0.7rem; color: var(--text-secondary);">take-home / year</div>
                        </div>
                        <div
                            style="padding: 1rem; background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.2); text-align: center;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">At
                                Current Hours</div>
                            <div id="finance-yearly-current-gross"
                                style="font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin: 0.25rem 0;">
                                $0</div>
                            <div style="font-size: 0.7rem; color: var(--text-secondary);">gross / year</div>
                            <div id="finance-yearly-current-net"
                                style="font-size: 1.4rem; font-weight: 700; color: var(--accent-green); margin-top: 0.25rem;">
                                $0</div>
                            <div style="font-size: 0.7rem; color: var(--text-secondary);">take-home / year</div>
                        </div>
                    </div>
                    <div id="finance-yearly-diff"
                        style="text-align: center; margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-secondary);">
                    </div>
                </div>

                <!-- Budget Builder -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem;">

                    <!-- Add Expense Form + Expense List -->
                    <div class="sub-panel" style="border-color: rgba(251, 191, 36, 0.3);">
                        <h3 style="color: var(--accent-yellow);">📋 Budget Builder</h3>
                        <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 1rem;">Add your
                            recurring bills and expenses. They'll auto-calculate into your weekly budget.</p>

                        <!-- Add Form -->
                        <div
                            style="display: flex; flex-direction: column; gap: 0.5rem; padding: 0.75rem; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); margin-bottom: 1rem;">
                            <input type="text" id="expense-name-input" placeholder="Expense name (e.g., Rent)"
                                style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 1rem;">
                            <div style="display: flex; gap: 0.5rem;">
                                <input type="number" id="expense-amount-input" placeholder="$" step="0.01" min="0"
                                    style="flex: 1; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 1rem;">
                                <select id="expense-freq-input"
                                    style="padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace;">
                                    <option value="weekly">Weekly</option>
                                    <option value="fortnightly">Fortnightly</option>
                                    <option value="monthly">Monthly</option>
                                    <option value="yearly">Yearly</option>
                                </select>
                                <select id="expense-cat-input"
                                    style="padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace;">
                                    <option value="essential">🛡️ Essential</option>
                                    <option value="flexible">🎮 Flexible</option>
                                </select>
                            </div>
                            <button id="add-expense-btn" class="tab-btn active"
                                style="margin: 0; padding: 0.4rem; background: rgba(52,211,153,0.2); border: 1px solid var(--accent-green); color: var(--accent-green); font-family: ui-monospace, monospace; font-size: 1rem;">+
                                Add Expense</button>
                        </div>

                        <!-- Expenses List -->
                        <div id="expenses-list" style="display: flex; flex-direction: column; gap: 0.4rem;">
                            <!-- Populated by JS -->
                        </div>
                    </div>

                    <!-- Weekly Budget Summary -->
                    <div class="sub-panel" style="border-color: rgba(52, 211, 153, 0.3);">
                        <h3 style="color: var(--accent-green);">💸 Weekly Budget Summary</h3>

                        <!-- Big disposable number -->
                        <div
                            style="margin-top: 1rem; padding: 1rem; background: rgba(52, 211, 153, 0.08); border: 1px solid rgba(52, 211, 153, 0.2); text-align: center;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">
                                Disposable Income / Week</div>
                            <div id="budget-disposable"
                                style="font-size: 2.2rem; font-weight: 700; color: var(--accent-green); margin: 0.25rem 0;">
                                $0.00</div>
                            <div id="budget-disposable-daily" style="font-size: 0.8rem; color: var(--text-secondary);">
                                ($0.00 / day)</div>
                        </div>

                        <!-- Breakdown -->
                        <ul class="workout-list" style="margin-top: 1rem;">
                            <li style="display:flex; justify-content:space-between;">
                                <span>Net Weekly Pay</span>
                                <strong id="budget-net-pay" style="color: var(--accent-green);">$0.00</strong>
                            </li>
                            <li style="display:flex; justify-content:space-between; color: #ef4444;">
                                <span>🛡️ Essential Expenses</span>
                                <strong id="budget-essential-total">-$0.00</strong>
                            </li>
                            <li style="display:flex; justify-content:space-between; color: var(--accent-yellow);">
                                <span>🎮 Flexible Expenses</span>
                                <strong id="budget-flexible-total">-$0.00</strong>
                            </li>
                            <li
                                style="display:flex; justify-content:space-between; border-top: 2px solid var(--glass-border); padding-top: 0.5rem; margin-top: 0.25rem;">
                                <span style="font-weight: 700;">Total Weekly Expenses</span>
                                <strong id="budget-expenses-total" style="color: #ef4444;">-$0.00</strong>
                            </li>
                        </ul>

                        <!-- Max Savings Potential -->
                        <div
                            style="margin-top: 1rem; padding: 1rem; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.2); text-align: center;">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">🏦
                                Max Savings Potential / Year</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 0.15rem;">(if you
                                only paid essentials)</div>
                            <div id="budget-max-savings"
                                style="font-size: 1.8rem; font-weight: 700; color: var(--accent-blue); margin: 0.25rem 0;">
                                $0</div>
                            <div id="budget-max-savings-weekly"
                                style="font-size: 0.8rem; color: var(--text-secondary);">($0.00 / week)</div>
                        </div>

                        <!-- Expense Breakdown Chart -->
                        <div style="position: relative; height: 180px; width: 100%; margin-top: 1rem;">
                            <canvas id="budgetPieChart"></canvas>
                        </div>
                    </div>

                </div>
            </section>

            <!-- Planner — Template Editor + Yearly Wall -->
            <section id="planner" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">🗓️</span> Planner</h2>
                    <p class="sub-text">Set up your weekly template, manage recurring tasks, and plot yearly events.</p>
                </div>

                <!-- View Toggle -->
                <div id="planner-view-toggle"
                    style="display:flex; gap:0.5rem; margin-bottom:1.25rem; font-family: ui-monospace, monospace;">
                    <button id="planner-view-template"
                        style="padding:0.3rem 1.1rem; background:rgba(0,200,160,0.18); border:1px solid var(--accent-green); color:var(--accent-green); font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px; font-weight:bold;">📋
                        Template</button>
                    <button id="planner-view-yearly"
                        style="padding:0.3rem 1.1rem; background:transparent; border:1px solid var(--glass-border); color:var(--text-secondary); font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px;">📌
                        Yearly</button>
                </div>

                <!-- Two-column layout: sidebar + main -->
                <div class="planner-layout">

                    <!-- Sidebar -->
                    <aside class="planner-sidebar">
                        <!-- Mini Month Calendar -->
                        <div class="planner-sidebar-card">
                            <h4>📅 Calendar</h4>
                            <div id="planner-mini-cal"></div>
                        </div>

                        <!-- Tasks -->
                        <div class="planner-sidebar-card">
                            <h4>✅ Tasks</h4>
                            <input id="planner-task-input" class="sidebar-task-input"
                                placeholder="Add task, press Enter…" type="text">
                            <ul id="planner-task-list" class="sidebar-task-list"></ul>
                        </div>

                        <!-- Notes -->
                        <div class="planner-sidebar-card">
                            <h4>📝 Notes</h4>
                            <textarea id="planner-notes-area" class="sidebar-notes-area"
                                placeholder="Quick notes…"></textarea>
                        </div>
                    </aside>

                    <!-- Main content -->
                    <div class="planner-main">
                        <!-- Section: Weekly Template + Recurring Tasks -->
                        <div id="planner-template-section">
                            <div id="planner-template-grid"></div>
                            <div id="planner-recurring-manager" style="margin-top:2rem;"></div>
                        </div>

                        <!-- Section: Yearly Wall -->
                        <div id="planner-yearly-section" style="display:none;">
                            <div id="planner-yearly-grid"></div>
                        </div>
                    </div>

                </div>
            </section>

            <!-- Block Edit Modal -->
            <div id="block-modal"
                style="display:none; position:fixed; inset:0; z-index:1000; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
                <div
                    style="background:#1a1a2e; border:2px solid var(--accent-green); border-radius:8px; padding:1.5rem; min-width:320px; max-width:420px; font-family: ui-monospace, monospace;">
                    <h3 id="block-modal-title" style="margin:0 0 1rem 0; color:var(--accent-yellow); font-size:1.3rem;">
                        Add Block</h3>
                    <div style="display:flex; flex-direction:column; gap:0.75rem;">
                        <input id="block-label" type="text" placeholder="Block name (e.g. Morning Routine)"
                            style="padding:0.4rem 0.6rem; background:rgba(0,0,0,0.4); border:1px solid var(--glass-border); color:#fff; font-family: ui-monospace, monospace; font-size:1rem; border-radius:3px;">
                        <div style="display:flex; gap:0.5rem;">
                            <div style="flex:1;">
                                <label style="font-size:0.8rem; color:var(--text-secondary);">Start</label>
                                <input id="block-start" type="time"
                                    style="width:100%; padding:0.4rem; background:rgba(0,0,0,0.4); border:1px solid var(--glass-border); color:#fff; font-family: ui-monospace, monospace; font-size:1rem; border-radius:3px;">
                            </div>
                            <div style="flex:1;">
                                <label style="font-size:0.8rem; color:var(--text-secondary);">End</label>
                                <input id="block-end" type="time"
                                    style="width:100%; padding:0.4rem; background:rgba(0,0,0,0.4); border:1px solid var(--glass-border); color:#fff; font-family: ui-monospace, monospace; font-size:1rem; border-radius:3px;">
                            </div>
                        </div>
                        <div>
                            <label style="font-size:0.8rem; color:var(--text-secondary);">Colour</label>
                            <div id="block-colour-picker"
                                style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-top:4px;"></div>
                        </div>
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top:1.25rem; justify-content:flex-end;">
                        <button id="block-modal-delete"
                            style="display:none; padding:0.3rem 0.9rem; background:rgba(239,68,68,0.2); border:1px solid #ef4444; color:#ef4444; font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px;">Delete</button>
                        <button id="block-modal-cancel"
                            style="padding:0.3rem 0.9rem; background:rgba(0,0,0,0.3); border:1px solid var(--glass-border); color:var(--text-secondary); font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px;">Cancel</button>
                        <button id="block-modal-save"
                            style="padding:0.3rem 0.9rem; background:rgba(52,211,153,0.2); border:1px solid var(--accent-green); color:var(--accent-green); font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px; font-weight:bold;">Save</button>
                    </div>
                </div>
            </div>

            <!-- Yearly Event Modal -->
            <div id="event-modal"
                style="display:none; position:fixed; inset:0; z-index:1000; background:rgba(0,0,0,0.7); align-items:center; justify-content:center;">
                <div
                    style="background:#1a1a2e; border:2px solid var(--accent-yellow); border-radius:8px; padding:1.5rem; min-width:320px; max-width:420px; font-family: ui-monospace, monospace;">
                    <h3 id="event-modal-title" style="margin:0 0 1rem 0; color:var(--accent-yellow); font-size:1.3rem;">
                        Add Event</h3>
                    <div style="display:flex; flex-direction:column; gap:0.75rem;">
                        <div style="display:flex; gap:0.5rem; align-items:center;">
                            <select id="event-emoji"
                                style="padding:0.4rem; background:rgba(0,0,0,0.4); border:1px solid var(--glass-border); color:#fff; font-family: ui-monospace, monospace; font-size:1.1rem; border-radius:3px; width:70px;">
                                <option>🎂</option>
                                <option>✈️</option>
                                <option>❤️</option>
                                <option>⭐</option>
                                <option>🎉</option>
                                <option>💼</option>
                                <option>🏥</option>
                                <option>🎓</option>
                                <option>🏖️</option>
                                <option>📅</option>
                            </select>
                            <input id="event-label" type="text" placeholder="Event name"
                                style="flex:1; padding:0.4rem 0.6rem; background:rgba(0,0,0,0.4); border:1px solid var(--glass-border); color:#fff; font-family: ui-monospace, monospace; font-size:1rem; border-radius:3px;">
                        </div>
                        <div>
                            <label style="font-size:0.8rem; color:var(--text-secondary);">Colour</label>
                            <div id="event-colour-picker"
                                style="display:flex; gap:0.4rem; flex-wrap:wrap; margin-top:4px;"></div>
                        </div>
                        <div style="display:flex; gap:1rem; align-items:center;">
                            <label style="font-size:0.9rem; color:var(--text-secondary);">Repeat annually?</label>
                            <input id="event-annual" type="checkbox" style="width:16px; height:16px; cursor:pointer;">
                        </div>
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top:1.25rem; justify-content:flex-end;">
                        <button id="event-modal-delete"
                            style="display:none; padding:0.3rem 0.9rem; background:rgba(239,68,68,0.2); border:1px solid #ef4444; color:#ef4444; font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px;">Delete</button>
                        <button id="event-modal-cancel"
                            style="padding:0.3rem 0.9rem; background:rgba(0,0,0,0.3); border:1px solid var(--glass-border); color:var(--text-secondary); font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px;">Cancel</button>
                        <button id="event-modal-save"
                            style="padding:0.3rem 0.9rem; background:rgba(249,115,22,0.2); border:1px solid #f97316; color:#f97316; font-family: ui-monospace, monospace; font-size:1rem; cursor:pointer; border-radius:3px; font-weight:bold;">Save</button>
                    </div>
                </div>
            </div>

            </section>



            <section id="dog" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">🐶</span> Quinny's Page</h2>
                </div>

                <!-- Profile Hero -->
                <div
                    style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1.5rem; padding: 1rem; background: rgba(251,191,36,0.05); border: 1px solid rgba(251,191,36,0.2); border-radius: 4px;">
                    <div style="position: relative; cursor: pointer; width: 120px; height: 120px; flex-shrink: 0;"
                        id="quinny-photo-wrapper" title="Click to upload a photo of Quinny">
                        <img id="quinny-profile-img" src="quinny_profile.png" alt="Quinny"
                            style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid var(--accent-yellow); box-shadow: 0 0 15px rgba(251,191,36,0.3);">
                        <div
                            style="position: absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.7); border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; border: 1px solid var(--accent-yellow); pointer-events: none;">
                            📷</div>
                        <input type="file" id="quinny-photo-upload" accept="image/*"
                            style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; border-radius: 50%;">
                    </div>
                    <div style="flex: 1;">
                        <div
                            style="font-size: 1.5rem; font-weight: 700; color: var(--accent-yellow); font-family: ui-monospace, monospace;">
                            Quinny</div>
                        <div id="quinny-age"
                            style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            <!-- Calculated by JS -->
                        </div>
                        <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem; align-items: center;">
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">🎂 Birthday:</label>
                            <input type="date" id="quinny-birthday-input"
                                style="padding: 0.3rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 0.9rem;">
                            <button id="quinny-birthday-save"
                                style="margin: 0; padding: 0.3rem 0.6rem; background: rgba(52,211,153,0.2); border: 1px solid var(--accent-green); color: var(--accent-green); font-family: ui-monospace, monospace; font-size: 0.85rem; cursor: pointer;">Save</button>
                        </div>
                    </div>
                </div>

                <div class="grid-2-col">
                    <!-- LEFT COLUMN -->
                    <div>
                        <!-- Vaccination Log -->
                        <div class="sub-panel" style="border-color: rgba(59,130,246,0.3); margin-bottom: 1rem;">
                            <h3 style="color: var(--accent-blue);">💉 Vaccinations</h3>
                            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Track
                                Quinny's vaccination history and upcoming due dates.</p>

                            <div
                                style="display: flex; flex-direction: column; gap: 0.5rem; padding: 0.75rem; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); margin-bottom: 0.75rem;">
                                <input type="text" id="vacc-name-input" placeholder="Vaccine name (e.g., Parvovirus)"
                                    style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 1rem;">
                                <div style="display: flex; gap: 0.5rem;">
                                    <div style="flex: 1;">
                                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Date
                                            Given</label>
                                        <input type="date" id="vacc-date-input"
                                            style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 0.9rem;">
                                    </div>
                                    <div style="flex: 1;">
                                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Next Due</label>
                                        <input type="date" id="vacc-next-input"
                                            style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 0.9rem;">
                                    </div>
                                </div>
                                <button id="vacc-add-btn" class="tab-btn active"
                                    style="margin: 0; padding: 0.4rem; background: rgba(59,130,246,0.2); border: 1px solid var(--accent-blue); color: var(--accent-blue); font-family: ui-monospace, monospace; font-size: 1rem;">+
                                    Add Vaccination</button>
                            </div>
                            <div id="vacc-list" style="display: flex; flex-direction: column; gap: 0.3rem;">
                                <!-- Populated by JS -->
                            </div>
                        </div>
                    </div>

                    <!-- RIGHT COLUMN -->
                    <div>
                        <!-- Worming & Flea Treatment -->
                        <div class="sub-panel" style="border-color: rgba(34,197,94,0.3); margin-bottom: 1rem;">
                            <h3 style="color: var(--accent-green);">🐛 Worming & Flea Treatment</h3>
                            <p style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">Log
                                treatments and track when the next dose is due.</p>

                            <div
                                style="display: flex; flex-direction: column; gap: 0.5rem; padding: 0.75rem; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); margin-bottom: 0.75rem;">
                                <div style="display: flex; gap: 0.5rem;">
                                    <select id="treat-type-input"
                                        style="flex: 1; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace;">
                                        <option value="worming">🐛 Worming</option>
                                        <option value="flea">🪲 Flea/Tick</option>
                                    </select>
                                    <input type="text" id="treat-product-input" placeholder="Product name"
                                        style="flex: 1; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 1rem;">
                                </div>
                                <div style="display: flex; gap: 0.5rem;">
                                    <div style="flex: 1;">
                                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Date
                                            Given</label>
                                        <input type="date" id="treat-date-input"
                                            style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 0.9rem;">
                                    </div>
                                    <div style="flex: 1;">
                                        <label style="font-size: 0.7rem; color: var(--text-secondary);">Next Due</label>
                                        <input type="date" id="treat-next-input"
                                            style="width: 100%; padding: 0.4rem; background: rgba(0,0,0,0.3); border: 2px inset var(--win-shadow); color: #fff; font-family: ui-monospace, monospace; font-size: 0.9rem;">
                                    </div>
                                </div>
                                <button id="treat-add-btn" class="tab-btn active"
                                    style="margin: 0; padding: 0.4rem; background: rgba(34,197,94,0.2); border: 1px solid var(--accent-green); color: var(--accent-green); font-family: ui-monospace, monospace; font-size: 1rem;">+
                                    Add Treatment</button>
                            </div>
                            <div id="treat-list" style="display: flex; flex-direction: column; gap: 0.3rem;">
                                <!-- Populated by JS -->
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Workout Plan View -->
            <section id="workout" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">💪</span> Longevity & Stability Workout</h2>
                    <p class="sub-text">3-Day Split (10kg DB, 3kg DBs, 8kg KB, Bench)</p>
                </div>

                <div class="workout-rules">
                    <strong>⚖️ The "Left Side First" Rule:</strong> Start unilateral moves on the weaker left side.
                    Match reps on the right. <br>
                    <strong>⏱️ Tempo:</strong> 3-1-1 (3 seconds down, 1 second pause, 1 second up).<br>
                    <strong>🦶 Foot Rehab (Post-Walk):</strong> 30s Kneeling Heel Sit, 10x Slow Eccentric
                    Right-to-Left
                    Calf Drops, 2min Frozen Bottle Roll.
                </div>

                <div class="grid-3-col" id="workout-grid">
                    <!-- Populated by JS -->
                </div>
            </section>

            <!-- Bio & Health View -->
            <section id="bio" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">🩸</span> Biological Tracking & Supplements</h2>
                    <p class="sub-text">DNA Analysis, Blood Trends, and Supplement Protocols. Click sections to
                        expand.
                    </p>
                </div>

                <!-- DNA Report Button -->
                <div style="margin-bottom: 1rem; text-align: center;">
                    <button id="dna-report-btn"
                        style="padding: 0.6rem 1.5rem; background: linear-gradient(135deg, rgba(139,92,246,0.3), rgba(59,130,246,0.3)); border: 2px solid rgba(139,92,246,0.5); color: #a78bfa; font-family: ui-monospace, monospace; font-size: 1.1rem; cursor: pointer; border-radius: 4px; transition: all 0.3s; text-shadow: 0 0 8px rgba(139,92,246,0.5);">
                        🧬 View Nuclear DNA Report
                    </button>
                </div>

                <!-- DNA Report Modal -->
                <div id="dna-report-modal"
                    style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.92); z-index: 9999; overflow-y: auto;">
                    <div
                        style="max-width: 900px; margin: 2rem auto; padding: 2rem; background: var(--bg-surface); border: 2px solid rgba(139,92,246,0.4); border-radius: 8px; position: relative;">
                        <button id="dna-report-close"
                            style="position: sticky; top: 0; float: right; background: rgba(239,68,68,0.2); border: 1px solid var(--accent-red); color: var(--accent-red); font-family: ui-monospace, monospace; font-size: 1rem; padding: 0.4rem 1rem; cursor: pointer; border-radius: 4px; z-index: 10;">✕
                            Close</button>
                        <div id="dna-report-content"
                            style="color: var(--text-primary); line-height: 1.8; font-size: 0.95rem;">
                            <div style="text-align: center; color: var(--text-secondary); padding: 2rem;">Loading DNA
                                Report...</div>
                        </div>
                    </div>
                </div>

                <!-- Bio Accordion: Supplements (default OPEN) -->
                <div class="bio-accordion">
                    <div class="bio-accordion-header expanded" data-bio-panel="bio-supplements-body">
                        <span>💊 Supplement Protocol <span
                                style="font-size: 0.75rem; color: var(--accent-blue); font-weight: 400;">(Personalized
                                —
                                DNA + Blood)</span></span>
                        <span class="bio-toggle">▼</span>
                    </div>
                    <div class="bio-accordion-body" id="bio-supplements-body" style="display: block;">
                        <div style="margin-bottom: 1rem; display: flex; justify-content: flex-end;">
                            <a href="reports/supplement_protocol_report.html" target="_blank" class="tab-btn" 
                                style="text-decoration: none; font-size: 0.75rem; background: rgba(0, 229, 255, 0.1); border-color: var(--accent-blue); color: var(--accent-blue); padding: 4px 10px;">
                                📄 View Full Report →
                            </a>
                        </div>
                        <div class="workout-rules" style="font-size: 0.85rem; margin-bottom: 1rem;">
                            <strong>⚠️ Critical:</strong> NAC — no Selenium blends (TSH borderline low).
                            Vit D load = 30,000IU/day — get 25(OH)D test at 8 weeks. ~16-18 total caps/day.
                        </div>

                        <!-- Supplement Date Navigator -->
                        <div
                            style="display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 0.5rem; border: 1px solid var(--glass-border); border-radius: 4px; margin-bottom: 1rem;">
                            <button id="supp-date-prev"
                                style="background: #c0c0c0; border: 2px outset var(--win-highlight); cursor: pointer; padding: 2px 12px; font-family: ui-monospace, monospace; font-weight: bold; color: #000;">◄
                                Prev Day</button>
                            <div id="supp-date-display"
                                style="font-weight: bold; font-size: 1.1rem; color: var(--accent-blue); font-family: ui-monospace, monospace; letter-spacing: 1px;">
                                Today
                            </div>
                            <button id="supp-date-next"
                                style="background: #c0c0c0; border: 2px outset var(--win-highlight); cursor: pointer; padding: 2px 12px; font-family: ui-monospace, monospace; font-weight: bold; color: #000;"
                                disabled>Next Day ►</button>
                        </div>

                        <!-- Supplement Timing Sub-Accordions -->
                        <div class="supp-timing-group">
                            <div class="supp-timing-header expanded" data-supp-body="supp-am-empty-body">
                                <span style="color: var(--accent-yellow);">☀️ AM — Empty Stomach (~6:30 AM)</span>
                                <span class="supp-toggle">▼</span>
                            </div>
                            <ul class="task-list supp-timing-body" id="supp-am-empty-body" style="display: block;">
                                <!-- id referenced by JS -->
                            </ul>
                        </div>

                        <div class="supp-timing-group">
                            <div class="supp-timing-header expanded" data-supp-body="supp-am-food-body">
                                <span style="color: var(--accent-green);">🍳 AM — With Breakfast (~7:00 AM)</span>
                                <span class="supp-toggle">▼</span>
                            </div>
                            <ul class="task-list supp-timing-body" id="supp-am-food-body" style="display: block;">
                                <!-- id referenced by JS -->
                            </ul>
                        </div>

                        <div class="supp-timing-group">
                            <div class="supp-timing-header expanded" data-supp-body="supp-pm-dinner-body">
                                <span style="color: var(--accent-blue);">🍽️ PM — With Dinner (~6:30 PM)</span>
                                <span class="supp-toggle">▼</span>
                            </div>
                            <ul class="task-list supp-timing-body" id="supp-pm-dinner-body" style="display: block;">
                                <!-- id referenced by JS -->
                            </ul>
                        </div>

                        <div class="supp-timing-group">
                            <div class="supp-timing-header expanded" data-supp-body="supp-pm-bed-body">
                                <span style="color: var(--accent-purple);">🌙 PM — Before Bed (~9:00 PM)</span>
                                <span class="supp-toggle">▼</span>
                            </div>
                            <ul class="task-list supp-timing-body" id="supp-pm-bed-body" style="display: block;">
                                <!-- id referenced by JS -->
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Bio Accordion: Blood Markers (default CLOSED) -->
                <div class="bio-accordion">
                    <div class="bio-accordion-header" data-bio-panel="bio-blood-body">
                        <span>🩸 Clinical Blood Markers <span
                                style="font-size: 0.75rem; color: var(--accent-red); font-weight: 400;">[Active
                                Inflammation Detected]</span></span>
                        <span class="bio-toggle">►</span>
                    </div>
                    <div class="bio-accordion-body" id="bio-blood-body" style="display: none;">
                        <div class="workout-rules"
                            style="background: rgba(239, 68, 68, 0.1); border-left-color: var(--accent-red); font-size: 0.85rem;">
                            <strong>Status:</strong> Active systemic inflammatory response detected. Monitoring
                            required.
                        </div>
                        <ul class="workout-list" id="blood-marker-list" style="margin-top: 1rem;">
                            <!-- Populated by JS -->
                        </ul>
                    </div>
                </div>

                <!-- Bio Accordion: Medical Alerts (default CLOSED) -->
                <div class="bio-accordion">
                    <div class="bio-accordion-header" data-bio-panel="bio-medical-body"
                        style="border-color: rgba(239, 68, 68, 0.3);">
                        <span style="color: var(--accent-red);">🚨 Medical Alerts (Doctor Visit) <span
                                style="font-size: 0.75rem; font-weight: 400;">— 4 flagged genes</span></span>
                        <span class="bio-toggle">►</span>
                    </div>
                    <div class="bio-accordion-body" id="bio-medical-body" style="display: none;">
                        <div class="workout-rules"
                            style="font-size: 0.85rem; border-left-color: var(--accent-red); background: rgba(239, 68, 68, 0.05);">
                            <strong>Priority:</strong> Discuss these highest-yield genetic markers at your next GP
                            or
                            specialist visit.
                        </div>
                        <div id="medical-alerts-container"
                            style="display: flex; flex-direction: column; margin-top: 1rem;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>

                <!-- Bio Accordion: Genetic Action Plan (default CLOSED) -->
                <div class="bio-accordion">
                    <div class="bio-accordion-header" data-bio-panel="bio-genetics-body">
                        <span>🧬 Genetic Action Plan <span
                                style="font-size: 0.75rem; color: var(--accent-purple); font-weight: 400;">— 6 DNA
                                hacks</span></span>
                        <span class="bio-toggle">►</span>
                    </div>
                    <div class="bio-accordion-body" id="bio-genetics-body" style="display: none;">
                        <div class="workout-rules"
                            style="font-size: 0.85rem; border-left-color: var(--accent-purple); background: rgba(192, 132, 252, 0.05);">
                            <strong>Protocol:</strong> Daily lifestyle and training hacks tailored to your specific
                            DNA
                            vulnerabilities.
                        </div>
                        <div id="genetic-hacks-container"
                            style="display: flex; flex-direction: column; margin-top: 1rem;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </section>
            <!-- Food Analytics View -->
            <section id="food" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">🍎</span> Food Analytics</h2>
                    <p class="sub-text">DNA-Personalized Nutrition Tracking</p>
                </div>

                <!-- Top Row: Dashboard Tiles + Live Grade -->
                <div
                    style="display: grid; grid-template-columns: 1fr auto; gap: 1rem; margin-bottom: 1.5rem; align-items: start;">
                    <!-- Macro Dashboard -->
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem;">
                        <div class="sub-panel" style="text-align: center; padding: 0.75rem;">
                            <div style="font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase;">
                                Calories</div>
                            <div id="food-dash-calories"
                                style="font-size: 1.6rem; font-weight: 700; color: var(--text-primary);">0</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary);">/ 2100 target</div>
                        </div>
                        <div class="sub-panel"
                            style="text-align: center; padding: 0.75rem; border-color: rgba(56, 189, 248, 0.3);">
                            <div style="font-size: 0.7rem; color: var(--accent-blue); text-transform: uppercase;">
                                Protein</div>
                            <div id="food-dash-protein"
                                style="font-size: 1.6rem; font-weight: 700; color: var(--text-primary);">0g</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary);">/ 120g target</div>
                        </div>
                        <div class="sub-panel"
                            style="text-align: center; padding: 0.75rem; border-color: rgba(251, 191, 36, 0.3);">
                            <div style="font-size: 0.7rem; color: var(--accent-yellow); text-transform: uppercase;">
                                Carbs</div>
                            <div id="food-dash-carbs"
                                style="font-size: 1.6rem; font-weight: 700; color: var(--text-primary);">0g</div>
                            <div style="font-size: 0.65rem; color: var(--text-secondary);">
                                < 150g limit</div>
                            </div>
                            <div class="sub-panel"
                                style="text-align: center; padding: 0.75rem; border-color: rgba(239, 68, 68, 0.3);">
                                <div style="font-size: 0.7rem; color: var(--accent-red); text-transform: uppercase;">
                                    Fats</div>
                                <div id="food-dash-fats"
                                    style="font-size: 1.6rem; font-weight: 700; color: var(--text-primary);">0g</div>
                                <div style="font-size: 0.65rem; color: var(--text-secondary);">
                                    < 80g limit</div>
                                </div>
                            </div>

                            <!-- Live DNA Grade -->
                            <div class="sub-panel" style="text-align: center; padding: 1rem 1.5rem; min-width: 120px;">
                                <div
                                    style="font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 0.25rem;">
                                    DNA Grade</div>
                                <div id="food-grade-badge"
                                    style="font-size: 2.5rem; font-weight: 900; color: #22c55e; text-shadow: 0 0 10px rgba(34,197,94,0.5); font-family: ui-monospace, monospace;">
                                    --</div>
                                <div id="food-grade-score" style="font-size: 0.7rem; color: var(--text-secondary);">Log
                                    food to grade</div>
                            </div>
                        </div>

                        <!-- Main Content Grid -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">

                            <!-- Column 1: Search + Portion Picker + Log -->
                            <div class="sub-panel">
                                <h3>Log Food</h3>
                                <!-- Search -->
                                <div style="position: relative; margin-top: 0.75rem;">
                                    <input type="text" id="food-search-input"
                                        placeholder="Search food (e.g., Chicken Breast)..." autocomplete="off"
                                        style="width: 100%; padding: 0.75rem; background: var(--bg-surface); border: 2px inset var(--win-shadow); color: var(--text-primary); font-family: ui-monospace, monospace; font-size: 1rem;">
                                    <div id="food-autocomplete-results"
                                        style="position: absolute; top: 100%; left: 0; width: 100%; max-height: 250px; overflow-y: auto; background: #1e293b; border: 1px solid var(--glass-border); border-top: none; z-index: 10; display: none; margin-top: 2px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); font-family: 'Segoe UI', Arial, sans-serif; font-size: 0.95rem; color: #f1f5f9;">
                                    </div>
                                </div>

                                <!-- Portion Picker (hidden by default, shown when food is selected) -->
                                <div id="food-portion-picker"
                                    style="display: none; margin-top: 0.75rem; padding: 0.75rem; background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 6px;">
                                    <div
                                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <strong id="portion-food-name"
                                            style="color: var(--text-primary); font-size: 0.9rem;">Food Name</strong>
                                        <button id="portion-cancel-btn"
                                            style="background: none; border: none; color: var(--accent-red); font-size: 1.2rem; cursor: pointer;">×</button>
                                    </div>
                                    <div
                                        style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem;">
                                        <input type="number" id="portion-amount" value="100" min="1" max="5000"
                                            style="width: 80px; padding: 0.4rem; background: var(--bg-surface); border: 2px inset var(--win-shadow); color: var(--text-primary); font-family: ui-monospace, monospace; font-size: 1rem; text-align: center;">
                                        <select id="portion-unit"
                                            style="padding: 0.4rem; background: var(--bg-surface); border: 2px inset var(--win-shadow); color: var(--text-primary); font-family: ui-monospace, monospace;">
                                            <option value="g">grams</option>
                                            <option value="ml">ml</option>
                                        </select>
                                        <button id="portion-serving-btn"
                                            style="padding: 0.4rem 0.6rem; background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.4); color: var(--accent-blue); font-family: ui-monospace, monospace; font-size: 0.85rem; cursor: pointer; border-radius: 4px; white-space: nowrap;"
                                            title="Use product serving size">1 Serving</button>
                                    </div>
                                    <!-- Live macro preview -->
                                    <div id="portion-preview"
                                        style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                                        0 kcal | 0P 0C 0F
                                    </div>
                                    <button id="portion-add-btn"
                                        style="width: 100%; padding: 0.5rem; background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.4); color: var(--accent-green); font-family: ui-monospace, monospace; font-size: 1rem; cursor: pointer; border-radius: 4px;">
                                        + Add to Log
                                    </button>
                                </div>

                                <!-- Saved Recipes -->
                                <div style="margin-top: 1rem;">
                                    <div class="pool-accordion-header" data-pool="food-recipes"
                                        style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                                        <span
                                            style="font-weight: 700; color: var(--text-primary); font-size: 0.9rem;">📋
                                            My Recipes</span>
                                        <span style="font-size: 0.8rem;">▶</span>
                                    </div>
                                    <div id="food-recipes-panel" style="display: none; margin-top: 0.5rem;">
                                        <div id="food-recipes-list" style="margin-bottom: 0.5rem;">
                                            <!-- Populated by JS -->
                                        </div>
                                        <button id="create-recipe-btn"
                                            style="width: 100%; padding: 0.4rem; background: rgba(192, 132, 252, 0.1); border: 1px solid rgba(192, 132, 252, 0.3); color: var(--accent-purple); font-family: ui-monospace, monospace; font-size: 0.85rem; cursor: pointer; border-radius: 4px;">
                                            + New Recipe
                                        </button>
                                    </div>
                                </div>

                                <!-- Recipe Builder (hidden by default) -->
                                <div id="recipe-builder"
                                    style="display: none; margin-top: 0.75rem; padding: 0.75rem; background: rgba(192, 132, 252, 0.05); border: 1px solid rgba(192, 132, 252, 0.2); border-radius: 6px;">
                                    <div
                                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <strong style="color: var(--accent-purple);">New Recipe</strong>
                                        <button id="recipe-builder-close"
                                            style="background: none; border: none; color: var(--accent-red); font-size: 1.2rem; cursor: pointer;">×</button>
                                    </div>
                                    <input type="text" id="recipe-name-input"
                                        placeholder="Recipe name (e.g., Morning Smoothie)"
                                        style="width: 100%; padding: 0.4rem; margin-bottom: 0.5rem; background: var(--bg-surface); border: 2px inset var(--win-shadow); color: var(--text-primary); font-family: ui-monospace, monospace;">
                                    <ul id="recipe-items-list" class="task-list"
                                        style="font-size: 0.8rem; margin-bottom: 0.5rem;">
                                        <li style="color: var(--text-secondary); font-style: italic;">Search and add
                                            foods above, they'll appear here</li>
                                    </ul>
                                    <div id="recipe-totals"
                                        style="font-size: 0.8rem; color: var(--accent-blue); margin-bottom: 0.5rem;">
                                    </div>
                                    <button id="save-recipe-btn"
                                        style="width: 100%; padding: 0.4rem; background: rgba(34, 197, 94, 0.2); border: 1px solid rgba(34, 197, 94, 0.4); color: var(--accent-green); font-family: ui-monospace, monospace; cursor: pointer; border-radius: 4px;">
                                        Save Recipe
                                    </button>
                                </div>

                                <!-- My Foods (History + Favorites) -->
                                <div style="margin-top: 1rem;">
                                    <div class="pool-accordion-header" data-pool="my-foods"
                                        style="cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-weight: 700; color: var(--text-primary); font-size: 0.9rem;">⭐
                                            My Foods</span>
                                        <span style="font-size: 0.8rem;">▶</span>
                                    </div>
                                    <div id="my-foods-panel" style="display: none; margin-top: 0.5rem;">
                                        <!-- Favorites -->
                                        <div style="margin-bottom: 0.75rem;">
                                            <div
                                                style="font-size: 0.75rem; color: #fbbf24; text-transform: uppercase; font-weight: 700; margin-bottom: 0.3rem; letter-spacing: 0.5px;">
                                                ⭐ Favorites
                                            </div>
                                            <div id="my-foods-favorites-list">
                                                <!-- Populated by JS -->
                                            </div>
                                        </div>
                                        <!-- Recent -->
                                        <div>
                                            <div
                                                style="font-size: 0.75rem; color: var(--accent-blue); text-transform: uppercase; font-weight: 700; margin-bottom: 0.3rem; letter-spacing: 0.5px;">
                                                🕐 Recent
                                            </div>
                                            <div id="my-foods-recent-list">
                                                <!-- Populated by JS -->
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Today's Log -->
                                <h3 style="margin-top: 1.5rem;">Today's Log</h3>
                                <ul class="task-list" id="food-log-list" style="margin-top: 0.5rem;">
                                </ul>
                            </div>

                            <!-- Column 2: Grade Breakdown + Audit -->
                            <div style="display: flex; flex-direction: column; gap: 1rem;">
                                <!-- DNA Grade Breakdown -->
                                <div class="sub-panel">
                                    <h3>DNA Grade Breakdown</h3>
                                    <div id="food-grade-breakdown" style="margin-top: 0.5rem; font-size: 0.85rem;">
                                        <!-- Populated by JS with pass/fail per criterion -->
                                        <div style="color: var(--text-secondary); font-style: italic;">Log food to see
                                            your DNA-personalized grade</div>
                                    </div>
                                    <button id="run-food-audit-btn" class="glass-button"
                                        style="margin-top: 0.75rem; width: 100%; padding: 0.6rem;">
                                        <span class="icon">🔍</span> Analyze & Save to History
                                    </button>
                                </div>

                                <!-- Macro Doughnut Chart -->
                                <div class="sub-panel" style="padding: 1rem;">
                                    <h3>Macro Split</h3>
                                    <div style="height: 180px; margin-top: 0.5rem;">
                                        <canvas id="foodMacroChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Historical Charts -->
                        <div style="margin-top: 1.5rem;">
                            <div class="sub-panel" style="padding: 1rem;">
                                <div
                                    style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                                    <h3>Grade History</h3>
                                    <div style="display: flex; gap: 0.25rem;">
                                        <button class="grade-range-btn" data-days="7"
                                            style="padding: 2px 8px; background: rgba(56,189,248,0.2); border: 1px solid rgba(56,189,248,0.4); color: var(--accent-blue); font-family: ui-monospace, monospace; font-size: 0.8rem; cursor: pointer; border-radius: 3px;">7d</button>
                                        <button class="grade-range-btn active" data-days="14"
                                            style="padding: 2px 8px; background: rgba(56,189,248,0.4); border: 1px solid rgba(56,189,248,0.6); color: #fff; font-family: ui-monospace, monospace; font-size: 0.8rem; cursor: pointer; border-radius: 3px;">14d</button>
                                        <button class="grade-range-btn" data-days="30"
                                            style="padding: 2px 8px; background: rgba(56,189,248,0.2); border: 1px solid rgba(56,189,248,0.4); color: var(--accent-blue); font-family: ui-monospace, monospace; font-size: 0.8rem; cursor: pointer; border-radius: 3px;">30d</button>
                                    </div>
                                </div>
                                <div style="height: 200px;">
                                    <canvas id="gradeHistoryChart"></canvas>
                                </div>
                            </div>

                            <!-- Collapsible Detailed Macro History -->
                            <div class="sub-panel" style="padding: 0; margin-top: 0.75rem;">
                                <div id="macro-history-header" class="pool-accordion-header"
                                    style="cursor: pointer; padding: 0.75rem 1rem; display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 700; color: var(--text-primary); font-size: 0.9rem;">📊
                                        Detailed Macro History</span>
                                    <span style="font-size: 0.8rem;">▶</span>
                                </div>
                                <div id="macro-history-body" style="display: none; padding: 1rem;">
                                    <div style="height: 250px;">
                                        <canvas id="macroHistoryChart"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>
            </section>


            <!-- User Manual View -->
            <section id="manual" class="tab-content">
                <div class="glass-panel" style="padding: 1.5rem;">
                    <h2
                        style="color: var(--accent-magenta); display: flex; align-items: center; gap: 0.5rem; text-transform: uppercase;">
                        <span class="icon">📖</span> Operating Manual v1.0
                    </h2>
                    <p class="subtitle" style="margin-bottom: 2rem;">Personalized directives based on DNA Atlas &
                        Biometrics</p>

                    <!-- Core Directives -->
                    <h3
                        style="color: var(--text-primary); margin-bottom: 1rem; border-bottom: 1px dotted rgba(255,255,255,0.2); padding-bottom: 0.5rem;">
                        <span class="icon">⚙️</span> Core Directives (Baseline)
                    </h3>

                    <div
                        style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                        <div class="glass-panel" style="background: rgba(15, 23, 42, 0.4);">
                            <h4 style="color: var(--accent-blue); margin-top: 0;">🍎 The Engine (Diet)</h4>
                            <ul
                                style="font-size: 0.85rem; color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.5;">
                                <li><strong>Carbs:</strong> &lt; 150g strict limit (TCF7L2 fragile pancreas). Naked
                                    carbs are poison.</li>
                                <li><strong>Protein:</strong> &gt; 120g target (ACTN3 hybrid muscle). Fuel the engine.
                                </li>
                                <li><strong>Fats:</strong> &lt; 80g strict limit (9p21 plaque risk). Avoid saturated
                                    fats.</li>
                                <li><strong>Fiber:</strong> &gt; 25g non-negotiable (CRP=9). Feed the gut barrier.</li>
                            </ul>
                        </div>

                        <div class="glass-panel" style="background: rgba(15, 23, 42, 0.4);">
                            <h4 style="color: var(--accent-green); margin-top: 0;">🏋️ The Chassis (Training)</h4>
                            <ul
                                style="font-size: 0.85rem; color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.5;">
                                <li><strong>Power:</strong> Built for heavy lifting/sprints (ADRB2 burns fat via
                                    adrenaline).</li>
                                <li><strong>Endurance:</strong> 50/50 fast/slow twitch (ACTN3). Excels in Crossfit/MMA
                                    style.</li>
                                <li><strong>Danger:</strong> Brittle tendons (COL5A1). <strong>NO</strong> excessive
                                    plyometrics/box jumps.</li>
                            </ul>
                        </div>

                        <div class="glass-panel" style="background: rgba(15, 23, 42, 0.4);">
                            <h4 style="color: var(--accent-yellow); margin-top: 0;">🧠 The Processor (Mind)</h4>
                            <ul
                                style="font-size: 0.85rem; color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.5;">
                                <li><strong>Durability:</strong> Elite in crisis, easily bored in mundane (COMT
                                    Warrior).</li>
                                <li><strong>Drive:</strong> Runs hot on adrenaline (MAOA). Direct into ambition or
                                    lifting.</li>
                                <li><strong>Social:</strong> Oxytocin resistant (OXTR). Independent, immune to
                                    group-think.</li>
                            </ul>
                        </div>

                        <div class="glass-panel" style="background: rgba(15, 23, 42, 0.4);">
                            <h4 style="color: var(--accent-magenta); margin-top: 0;">🔋 The Battery (Sleep)</h4>
                            <ul
                                style="font-size: 0.85rem; color: var(--text-secondary); padding-left: 1.2rem; line-height: 1.5;">
                                <li><strong>Circadian:</strong> Extreme morning lark (CLOCK). Crash at sunset is
                                    natural.</li>
                                <li><strong>Caffeine:</strong> 10:00 AM strict cutoff (CYP1A2 10-hour clearance).</li>
                                <li><strong>Repair:</strong> Mg Glycinate (400mg) mandatory at 9 PM to fix circadian
                                    aging (SIRT1).</li>
                            </ul>
                        </div>
                    </div>

                    <!-- Troubleshooting Protocols -->
                    <h3
                        style="color: var(--text-primary); margin-bottom: 1rem; border-bottom: 1px dotted rgba(255,255,255,0.2); padding-bottom: 0.5rem;">
                        <span class="icon">🚨</span> Troubleshooting Protocols
                    </h3>

                    <div style="display: flex; flex-direction: column; gap: 1rem;">

                        <div class="glass-panel"
                            style="background: rgba(239, 68, 68, 0.05); border-left: 3px solid var(--accent-red);">
                            <h4 style="color: var(--accent-red); margin-top: 0;">Error: "I ate pure junk / massive
                                sugar"</h4>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                <strong>The Threat:</strong> Visceral fat storage (KLF14) and massive inflammatory spike
                                attacking vulnerable arteries (9p21).<br><br>
                                <strong>Mitigation:</strong>
                                <ul style="margin: 0.5rem 0 0 0;">
                                    <li>Immediately take 1200mg NAC (sponges oxidative stress & protects liver).</li>
                                    <li>Do 20 mins of heavy resistance/sprints. Use ADRB2 adrenaline receptors to force
                                        the body to burn the glucose rather than storing it.</li>
                                </ul>
                            </div>
                        </div>

                        <div class="glass-panel"
                            style="background: rgba(249, 115, 22, 0.05); border-left: 3px solid #f97316;">
                            <h4 style="color: #f97316; margin-top: 0;">Error: "I am furiously angry / highly impulsive"
                            </h4>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                <strong>The Threat:</strong> The MAOA "Warrior Gene" isn't clearing out serotonin and
                                adrenaline. The brain is running dangerously "hot".<br><br>
                                <strong>Mitigation:</strong>
                                <ul style="margin: 0.5rem 0 0 0;">
                                    <li>Recognize it is a chemical backlog, not reality.</li>
                                    <li>Direct the volatile energy immediately into a heavy physical task or aggressive
                                        workout. Physical exhaustion manually burns off the neurotransmitters.</li>
                                </ul>
                            </div>
                        </div>

                        <div class="glass-panel"
                            style="background: rgba(56, 189, 248, 0.05); border-left: 3px solid var(--accent-blue);">
                            <h4 style="color: var(--accent-blue); margin-top: 0;">Error: "I drank coffee at 2 PM"</h4>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                <strong>The Threat:</strong> CYP1A2 slow-clearance liver means 50% of the caffeine will
                                still be attached to brain receptors at midnight, preventing deep sleep.<br><br>
                                <strong>Mitigation:</strong>
                                <ul style="margin: 0.5rem 0 0 0;">
                                    <li>Increase physical activity in the afternoon to boost general metabolic
                                        clearance.</li>
                                    <li>Double down on L-Theanine and take 400mg Mg Glycinate at 9:00 PM to manually
                                        force GABA pathways open, overriding the adenosine blockade.</li>
                                </ul>
                            </div>
                        </div>

                        <div class="glass-panel"
                            style="background: rgba(251, 191, 36, 0.05); border-left: 3px solid var(--accent-yellow);">
                            <h4 style="color: var(--accent-yellow); margin-top: 0;">Error: "I was startled/shocked and
                                can't calm down"</h4>
                            <div style="font-size: 0.85rem; color: var(--text-secondary);">
                                <strong>The Threat:</strong> ADCYAP1R1 trait causes an excessive biological startle
                                reflex, flooding the system with adrenaline and risking trauma imprinting.<br><br>
                                <strong>Mitigation:</strong>
                                <ul style="margin: 0.5rem 0 0 0;">
                                    <li>Drop everything and do 5 minutes of Box Breathing (4s in, 4s hold, 4s out, 4s
                                        hold).</li>
                                    <li>This physical action forces the parasympathetic nervous system back online,
                                        halting the adrenaline cascade.</li>
                                </ul>
                            </div>
                        </div>

                    </div>
                </div>
            </section>

            <!-- Open Logistics View -->
            <section id="logistics" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">🔧</span> Open Logistics</h2>
                    <p class="sub-text">Things you need to figure out. Persistent until resolved.</p>
                </div>

                <!-- Add New Logistics Item Form -->
                <div class="glass-panel" style="margin-bottom: 2rem; background: rgba(0,0,0,0.2);">
                    <h3 style="margin-top: 0; margin-bottom: 1rem; color: var(--text-primary);"><span
                            class="icon">➕</span> Add New Item</h3>
                    <div style="display: flex; gap: 1rem; align-items: end;">
                        <div style="flex: 1;">
                            <label
                                style="display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.3rem;">What
                                needs solving?</label>
                            <input type="text" id="logistics-title-input"
                                placeholder="e.g., Hire tracked bike to tow caravan behind new house"
                                style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: ui-monospace, monospace; border-radius: 4px; font-size: 1rem;">
                        </div>
                        <button id="add-logistics-btn" class="tab-btn active"
                            style="margin: 0; height: 36px; padding: 0 1.5rem; background: rgba(56,189,248,0.2); border: 1px solid var(--accent-blue); color: var(--accent-blue); white-space: nowrap;">+
                            Add</button>
                    </div>
                </div>

                <!-- Logistics Items List -->
                <div id="logistics-items-container" style="display: flex; flex-direction: column; gap: 1.5rem;">
                    <!-- Populated by JS -->
                </div>

                <!-- Solved Log (Collapsible) -->
                <div style="margin-top: 2rem;">
                    <div id="logistics-solved-header" class="bio-accordion-header"
                        data-bio-panel="logistics-solved-body"
                        style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); border-radius: 6px;">
                        <span style="font-weight: 700; color: var(--accent-green); font-size: 0.95rem;">✅ Solved Log
                            <span id="logistics-solved-count"
                                style="font-size: 0.75rem; color: var(--text-secondary); font-weight: 400;">(0
                                items)</span></span>
                        <span class="bio-toggle" style="color: var(--accent-green);">►</span>
                    </div>
                    <div class="bio-accordion-body" id="logistics-solved-body"
                        style="display: none; margin-top: 0.75rem;">
                        <div id="logistics-solved-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
                            <!-- Populated by JS -->
                        </div>
                    </div>
                </div>
            </section>

            <!-- Supps Vault View -->
            <section id="supps" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">💊</span> Supps Vault</h2>
                    <p class="sub-text">Inventory and Low-Stock Tracking</p>
                </div>

                <!-- Add New Supplement Form -->
                <div class="glass-panel" style="margin-bottom: 2rem; background: rgba(0,0,0,0.2);">
                    <h3 style="margin-top: 0; margin-bottom: 1rem; color: var(--text-primary);"><span
                            class="icon">➕</span> Add New Bottle</h3>
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 1rem; align-items: end;">
                        <div>
                            <label
                                style="display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.3rem;">Supplement
                                Name</label>
                            <input type="text" id="supp-name-input" placeholder="e.g., Magnesium Glycinate"
                                style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: ui-monospace, monospace; border-radius: 4px;">
                        </div>
                        <div>
                            <label
                                style="display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.3rem;">Total
                                Pills (Capacity)</label>
                            <input type="number" id="supp-capacity-input" placeholder="e.g., 60"
                                style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: ui-monospace, monospace; border-radius: 4px;">
                        </div>
                        <div>
                            <label
                                style="display: block; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.3rem;">Daily
                                Dose</label>
                            <input type="number" id="supp-dose-input" placeholder="e.g., 2"
                                style="width: 100%; padding: 0.5rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: ui-monospace, monospace; border-radius: 4px;">
                        </div>
                        <button id="add-supp-btn" class="tab-btn active"
                            style="margin: 0; height: 36px; padding: 0 1rem; background: rgba(34,197,94,0.2); border: 1px solid var(--accent-green); color: var(--accent-green);">Add
                            to Vault</button>
                    </div>
                </div>

                <!-- Inventory Grid -->
                <h3
                    style="margin-bottom: 1rem; color: var(--text-primary); border-bottom: 1px dotted rgba(255,255,255,0.2); padding-bottom: 0.5rem;">
                    <span class="icon">📦</span> Current Inventory
                </h3>
                <div id="supps-inventory-grid"
                    style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem;">
                    <!-- Tracked supplements populated by JS -->
                </div>
            </section><!-- /supps -->

            <!-- Misc — Life Design Canvas -->
            <section id="misc" class="tab-content glass-panel">
                <div class="section-header">
                    <h2><span class="icon">✦</span> Misc</h2>
                    <p class="sub-text">Life design experiments, challenges, and reference documents.</p>
                </div>

                <!-- Ideal Week Challenge -->
                <div style="margin-bottom: 2rem;">
                    <div style="display:flex; align-items:baseline; gap:0.75rem; margin-bottom:0.5rem;">
                        <h3
                            style="font-family: ui-monospace, monospace; font-size:1.4rem; color:var(--accent-green); letter-spacing:1px; margin:0;">
                            🗓️ THE IDEAL WEEK</h3>
                        <span style="font-size:0.85rem; color:var(--text-secondary);">Target · Asleep by 12:00 AM every
                            night</span>
                    </div>
                    <p style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:1.25rem; line-height:1.6;">
                        Built around your actual roster (Mon 12–6 PM · Fri–Sat 2:45–11 PM · Sun 11–5 PM) and your DNA
                        blueprint: deep work in the morning cortisol peak, exercise mid-morning or afternoon, caffeine
                        cut at 10 AM, wind-down ritual at 9 PM.</p>

                    <!-- Legend -->
                    <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.5rem;">
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #38bdf8; background:rgba(56,189,248,0.08); border-radius:2px; color:var(--text-secondary);">Kids
                            / Family</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #00c9a0; background:rgba(0,200,160,0.08); border-radius:2px; color:var(--text-secondary);">Deep
                            Work</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #c084fc; background:rgba(192,132,252,0.08); border-radius:2px; color:var(--text-secondary);">Nap</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #fbbf24; background:rgba(251,191,36,0.08); border-radius:2px; color:var(--text-secondary);">Work
                            Shift</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #fb923c; background:rgba(251,146,60,0.08); border-radius:2px; color:var(--text-secondary);">Exercise</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #f472b6; background:rgba(244,114,182,0.08); border-radius:2px; color:var(--text-secondary);">Personal
                            / Quinn</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #a78bfa; background:rgba(167,139,250,0.08); border-radius:2px; color:var(--text-secondary);">Wind
                            Down</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid rgba(255,255,255,0.2); background:rgba(255,255,255,0.03); border-radius:2px; color:var(--text-secondary);">Routine</span>
                        <span
                            style="font-size:0.8rem; padding:2px 10px; border-left:3px solid #4ade80; background:rgba(74,222,128,0.08); border-radius:2px; color:var(--text-secondary);">Cannabis</span>
                    </div>

                    <!-- Day Grid — rendered by _misc.js -->
                    <div id="ideal-week-grid"
                        style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:1rem;">
                    </div>

                    <!-- Cannabis Protocol Summary -->
                    <div style="margin-top: 2rem;">
                        <div id="cannabis-protocol-header"
                            style="cursor: pointer; display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; background: rgba(74,222,128,0.06); border: 1px solid rgba(74,222,128,0.2); border-radius: 6px;"
                            onclick="(function(h){var b=document.getElementById('cannabis-protocol-body');var t=h.querySelector('.cp-toggle');if(b.style.display==='none'){b.style.display='block';t.textContent='▼'}else{b.style.display='none';t.textContent='►'}})(this)">
                            <span style="font-weight: 700; color: #4ade80; font-size: 0.95rem;">🌿 Cannabis Protocol
                                <span
                                    style="font-size: 0.75rem; color: var(--text-secondary); font-weight: 400;">DNA-Optimized</span></span>
                            <span class="cp-toggle" style="color: #4ade80;">►</span>
                        </div>
                        <div id="cannabis-protocol-body"
                            style="display: none; margin-top: 0.75rem; padding: 1rem; background: rgba(4,18,18,0.6); border: 1px solid var(--glass-border); border-radius: 4px;">

                            <!-- Gene Interactions -->
                            <h4 style="color: #4ade80; margin: 0 0 0.75rem; font-size: 0.9rem;">Gene Interactions</h4>
                            <div
                                style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.5rem; margin-bottom: 1.25rem;">
                                <div
                                    style="font-size: 0.78rem; color: var(--text-secondary); padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 3px; border-left: 2px solid #4ade80; line-height: 1.5;">
                                    <strong style="color: var(--text-primary);">COMT G/G</strong> — Fast dopamine
                                    clearance. Shorter THC peak, faster recovery. Low anxiety risk.
                                </div>
                                <div
                                    style="font-size: 0.78rem; color: var(--text-secondary); padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 3px; border-left: 2px solid #fbbf24; line-height: 1.5;">
                                    <strong style="color: var(--text-primary);">CYP1A2 A/C</strong> — Slow metabolizer.
                                    Edibles hit harder/longer. Inhaled more predictable.
                                </div>
                                <div
                                    style="font-size: 0.78rem; color: var(--text-secondary); padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 3px; border-left: 2px solid #38bdf8; line-height: 1.5;">
                                    <strong style="color: var(--text-primary);">TNF-α A/G</strong> — High inflammation
                                    baseline. CBD anti-inflammatory benefit above average.
                                </div>
                                <div
                                    style="font-size: 0.78rem; color: var(--text-secondary); padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 3px; border-left: 2px solid #a78bfa; line-height: 1.5;">
                                    <strong style="color: var(--text-primary);">SIRT1 C/C</strong> — THC suppresses REM.
                                    Stacks with disrupted circadian. 2h+ buffer before sleep.
                                </div>
                                <div
                                    style="font-size: 0.78rem; color: var(--text-secondary); padding: 6px 10px; background: rgba(255,255,255,0.03); border-radius: 3px; border-left: 2px solid #f87171; line-height: 1.5;">
                                    <strong style="color: var(--text-primary);">GSTP1 A/G</strong> — Slower phase II
                                    detox. Daily heavy use stresses liver. Moderation required.
                                </div>
                            </div>

                            <!-- Schedule -->
                            <h4 style="color: #4ade80; margin: 0 0 0.5rem; font-size: 0.9rem;">Weekly Schedule</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem;">
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); color: #f87171;">Mon
                                    ✕</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; font-weight: 600;">Tue
                                    ✓</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; font-weight: 600;">Wed
                                    ✓</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); color: #f87171;">Thu
                                    ✕</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); color: #f87171;">Fri
                                    ✕</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.25); color: #f87171;">Sat
                                    ✕</span>
                                <span
                                    style="font-size: 0.75rem; padding: 3px 10px; border-radius: 3px; background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3); color: #4ade80; font-weight: 600;">Sun
                                    ✓</span>
                            </div>

                            <!-- Rules -->
                            <div
                                style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.6; padding: 8px 12px; background: rgba(74,222,128,0.04); border: 1px solid rgba(74,222,128,0.1); border-radius: 4px;">
                                <strong style="color: #4ade80;">Rules:</strong>
                                2–3 nights/week max · Evenings only, after kids' bedtime (~20:30) · 2+ hours before
                                sleep target · Off days preferred (recovery benefit from TNF-α suppression) · No use on
                                work-night closings or early-sleep days
                            </div>

                        </div>
                    </div>

                </div>
            </section><!-- /misc -->

        </main>
    </div>

    <script src="vendor/marked.min.js"></script>
    <script src="vendor/chart.js"></script>
    <script src="retro-audio.js"></script>
    <script src="symphony-app.js?v=5"></script>
    <script src="_planner_v2.js?v=1"></script>
    <script src="_planner_sidebar.js?v=1"></script>
    <script src="_misc.js?v=1"></script>

    <!-- Standalone Quinny handlers (runs independently of main script) -->
    <script>
        (function () {
            'use strict';
            var QUINNY_KEY = 'symphony_quinny_data';
            var PHOTO_KEY = 'symphony_quinny_photo';

            function getQuinnyData() {
                try { return JSON.parse(localStorage.getItem(QUINNY_KEY)) || {}; } catch (e) { return {}; }
            }

            // Photo upload
            var photoInput = document.getElementById('quinny-photo-upload');
            var profileImg = document.getElementById('quinny-profile-img');

            // Restore photo
            try {
                var saved = localStorage.getItem(PHOTO_KEY);
                if (saved && profileImg) profileImg.src = saved;
            } catch (e) { }

            if (photoInput) {
                photoInput.addEventListener('change', function (e) {
                    var file = e.target.files[0];
                    if (!file || !profileImg) return;
                    var reader = new FileReader();
                    reader.onload = function (evt) {
                        var dataUrl = evt.target.result;
                        profileImg.src = dataUrl;
                        try { localStorage.setItem(PHOTO_KEY, dataUrl); } catch (e) {
                            // Too large, resize
                            var img = new Image();
                            img.onload = function () {
                                var c = document.createElement('canvas');
                                var s = Math.min(300 / img.width, 300 / img.height, 1);
                                c.width = img.width * s; c.height = img.height * s;
                                c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
                                var small = c.toDataURL('image/jpeg', 0.6);
                                try { localStorage.setItem(PHOTO_KEY, small); profileImg.src = small; } catch (e2) { alert('Image too large to save.'); }
                            };
                            img.src = dataUrl;
                        }
                    };
                    reader.readAsDataURL(file);
                });
            }

            // Birthday save
            var bdaySave = document.getElementById('quinny-birthday-save');
            var bdayInput = document.getElementById('quinny-birthday-input');
            var ageDisplay = document.getElementById('quinny-age');

            function showAge() {
                var data = getQuinnyData();
                if (!data.birthday) { if (ageDisplay) ageDisplay.innerText = 'Set birthday below \u2193'; return; }
                if (bdayInput) bdayInput.value = data.birthday;
                var bday = new Date(data.birthday + 'T00:00:00');
                var now = new Date();
                var years = now.getFullYear() - bday.getFullYear();
                var months = now.getMonth() - bday.getMonth();
                if (months < 0) { years--; months += 12; }
                if (now.getDate() < bday.getDate()) { months--; if (months < 0) { years--; months += 12; } }
                var dogYears = years <= 2 ? years * 10.5 : 21 + (years - 2) * 4;
                if (ageDisplay) ageDisplay.innerHTML = '\ud83c\udf82 ' + years + ' year' + (years !== 1 ? 's' : '') + ', ' + months + ' month' + (months !== 1 ? 's' : '') + ' old <span style="color:var(--accent-yellow);">(~' + Math.round(dogYears) + ' dog years)</span>';
            }

            if (bdaySave) {
                bdaySave.onclick = function () {
                    var val = bdayInput ? bdayInput.value : '';
                    if (!val) { alert('Please select a date first.'); return; }
                    var data = getQuinnyData();
                    data.birthday = val;
                    if (!data.vaccinations) data.vaccinations = [];
                    if (!data.treatments) data.treatments = [];
                    localStorage.setItem(QUINNY_KEY, JSON.stringify(data));
                    showAge();
                    bdaySave.innerText = '\u2705 Saved!';
                    bdaySave.style.background = 'rgba(52,211,153,0.4)';
                    setTimeout(function () { bdaySave.innerText = 'Save'; bdaySave.style.background = ''; }, 1500);
                };
            }
            showAge();

            // Morning Read (edit/save)
            var MORNING_KEY = 'symphony_morning_read';
            var mrDisplay = document.getElementById('morning-read-display');
            var mrEditor = document.getElementById('morning-read-editor');
            var mrEditBtn = document.getElementById('morning-read-edit-btn');
            var mrSaveBtn = document.getElementById('morning-read-save-btn');

            if (mrDisplay) {
                var savedMR = localStorage.getItem(MORNING_KEY);
                if (savedMR) mrDisplay.innerText = savedMR;

                function openEditor() {
                    if (!mrEditor) return;
                    mrEditor.value = localStorage.getItem(MORNING_KEY) || '';
                    mrDisplay.style.display = 'none';
                    mrEditor.style.display = 'block';
                    if (mrEditBtn) mrEditBtn.style.display = 'none';
                    if (mrSaveBtn) mrSaveBtn.style.display = 'inline-block';
                    mrEditor.focus();
                }
                function closeEditor() {
                    var text = mrEditor ? mrEditor.value.trim() : '';
                    if (text) {
                        localStorage.setItem(MORNING_KEY, text);
                        mrDisplay.innerText = text;
                    } else {
                        localStorage.removeItem(MORNING_KEY);
                        mrDisplay.innerText = 'Click here to write your morning reminders...';
                    }
                    if (mrEditor) mrEditor.style.display = 'none';
                    mrDisplay.style.display = 'block';
                    if (mrSaveBtn) mrSaveBtn.style.display = 'none';
                    if (mrEditBtn) mrEditBtn.style.display = 'inline-block';
                }

                mrDisplay.onclick = openEditor;
                if (mrEditBtn) mrEditBtn.onclick = openEditor;
                if (mrSaveBtn) mrSaveBtn.onclick = closeEditor;
            }

            // DNA Report Modal
            var dnaBtn = document.getElementById('dna-report-btn');
            var dnaModal = document.getElementById('dna-report-modal');
            var dnaClose = document.getElementById('dna-report-close');
            var dnaContent = document.getElementById('dna-report-content');
            var dnaLoaded = false;

            if (dnaBtn && dnaModal) {
                dnaBtn.onclick = function () {
                    dnaModal.style.display = 'block';
                    document.body.style.overflow = 'hidden';
                    if (!dnaLoaded) {
                        // Try fetching from GitHub Pages path
                        var paths = ['../health/DNA_God_Mode_Report.md'];
                        function tryFetch(idx) {
                            if (idx >= paths.length) {
                                dnaContent.innerHTML = '<div style="color:var(--accent-red);padding:2rem;text-align:center;">Could not load DNA report. Please view on the <a href="https://priscillak91k-aigoon.github.io/Athena-Public/routine-app/" style="color:var(--accent-blue);">live site</a>.</div>';
                                return;
                            }
                            fetch(paths[idx]).then(function (r) {
                                if (!r.ok) throw new Error('Not found');
                                return r.text();
                            }).then(function (md) {
                                if (typeof marked !== 'undefined' && marked.parse) {
                                    dnaContent.innerHTML = marked.parse(md);
                                } else {
                                    dnaContent.innerHTML = '<pre style="white-space:pre-wrap;font-family: ui-monospace, monospace;font-size:0.9rem;">' + md + '</pre>';
                                }
                                dnaLoaded = true;
                                // Style the rendered markdown
                                dnaContent.querySelectorAll('h1,h2,h3').forEach(function (h) { h.style.color = '#a78bfa'; });
                                dnaContent.querySelectorAll('strong').forEach(function (s) { s.style.color = 'var(--accent-yellow)'; });
                            }).catch(function () { tryFetch(idx + 1); });
                        }
                        tryFetch(0);
                    }
                };
            }
            if (dnaClose && dnaModal) {
                dnaClose.onclick = function () {
                    dnaModal.style.display = 'none';
                    document.body.style.overflow = '';
                };
                // Also close on clicking backdrop
                dnaModal.onclick = function (e) {
                    if (e.target === dnaModal) {
                        dnaModal.style.display = 'none';
                        document.body.style.overflow = '';
                    }
                };
            }

            // Bio accordion toggle fallback (in case main JS doesn't run)
            document.querySelectorAll('.bio-accordion-header').forEach(function (header) {
                if (!header.onclick) {
                    header.onclick = function () {
                        var panelId = header.getAttribute('data-bio-panel');
                        if (!panelId) return;
                        var body = document.getElementById(panelId);
                        var toggle = header.querySelector('.bio-toggle');
                        if (!body) return;
                        var isOpen = header.classList.contains('expanded');
                        if (isOpen) {
                            body.style.display = 'none';
                            header.classList.remove('expanded');
                            if (toggle) toggle.textContent = '\u25ba';
                        } else {
                            body.style.display = 'block';
                            header.classList.add('expanded');
                            if (toggle) toggle.textContent = '\u25bc';
                        }
                    };
                }
            });
            // Same for supp timing sub-accordions
            document.querySelectorAll('.supp-timing-header').forEach(function (header) {
                if (!header.onclick) {
                    header.onclick = function () {
                        var bodyId = header.getAttribute('data-supp-body');
                        if (!bodyId) return;
                        var body = document.getElementById(bodyId);
                        var toggle = header.querySelector('.supp-toggle');
                        if (!body) return;
                        var isOpen = header.classList.contains('expanded');
                        if (isOpen) {
                            body.style.display = 'none';
                            header.classList.remove('expanded');
                            if (toggle) toggle.textContent = '\u25ba';
                        } else {
                            body.style.display = 'block';
                            header.classList.add('expanded');
                            if (toggle) toggle.textContent = '\u25bc';
                        }
                    };
                }
            });
        })();
    </script>

    <!-- Template Schedule System -->
    <script>
        (function () {
            'use strict';

            // ========== DEFAULT TEMPLATES ==========
            // These are the baseline schedules. Editable via "Edit Template".
            const DEFAULT_TEMPLATES = {
                off: [
                    { time: '06:30 AM', label: '🌅 Wake + NAC (1200mg)', type: 'routine' },
                    { time: '07:00 AM', label: '🍳 Breakfast + Supplements', type: 'routine' },
                    { time: '07:30 AM', label: '🐕 Quinn Walk', type: 'routine' },
                    { time: '08:30 AM', label: '💻 Deep Work / Lobotto', type: 'routine' },
                    { time: '09:00 AM', label: '💻 Deep Work (continued)', type: 'routine' },
                    { time: '09:30 AM', label: '💻 Deep Work (continued)', type: 'routine' },
                    { time: '10:00 AM', label: '☕ Break (no more caffeine after this)', type: 'routine' },
                    { time: '10:30 AM', label: '💻 Projects / Learning', type: 'routine' },
                    { time: '11:00 AM', label: '💻 Projects / Learning', type: 'routine' },
                    { time: '12:00 PM', label: '🍽️ Lunch', type: 'routine' },
                    { time: '01:00 PM', label: '🏋️ Exercise', type: 'routine' },
                    { time: '01:30 PM', label: '🏋️ Exercise (continued)', type: 'routine' },
                    { time: '02:00 PM', label: '🚿 Shower + Recovery', type: 'routine' },
                    { time: '02:30 PM', label: '📱 Free / Errands', type: 'routine' },
                    { time: '03:00 PM', label: '📱 Free / Errands', type: 'routine' },
                    { time: '03:30 PM', label: '🐕 Quinn Afternoon Walk', type: 'routine' },
                    { time: '04:00 PM', label: '🏠 House Tasks', type: 'routine' },
                    { time: '05:00 PM', label: '🏠 House Tasks', type: 'routine' },
                    { time: '06:00 PM', label: '🍽️ Dinner Prep', type: 'routine' },
                    { time: '06:30 PM', label: '🍽️ Dinner + Fish Oil + D3', type: 'routine' },
                    { time: '07:30 PM', label: '📺 Downtime', type: 'routine' },
                    { time: '08:30 PM', label: '📺 Downtime', type: 'routine' },
                    { time: '09:00 PM', label: '💊 Mag Glycinate + Wind Down', type: 'routine' },
                    { time: '09:30 PM', label: '📖 Reading / Bed Prep', type: 'routine' },
                    { time: '10:00 PM', label: '😴 Sleep', type: 'routine' }
                ],
                // Fri/Sat: 2:45 PM - 11:00 PM shift
                work_evening: [
                    { time: '06:30 AM', label: '🌅 Wake + NAC (1200mg)', type: 'routine' },
                    { time: '07:00 AM', label: '🍳 Breakfast + Supplements', type: 'routine' },
                    { time: '07:30 AM', label: '🐕 Quinn Walk', type: 'routine' },
                    { time: '08:30 AM', label: '📱 Free / Errands', type: 'routine' },
                    { time: '09:00 AM', label: '📱 Free / Errands', type: 'routine' },
                    { time: '10:00 AM', label: '🏋️ Exercise', type: 'routine' },
                    { time: '10:30 AM', label: '🏋️ Exercise (continued)', type: 'routine' },
                    { time: '11:00 AM', label: '🚿 Shower', type: 'routine' },
                    { time: '12:00 PM', label: '🍽️ Lunch', type: 'routine' },
                    { time: '01:00 PM', label: '🐕 Quinn Afternoon Walk', type: 'routine' },
                    { time: '01:30 PM', label: '👔 Get Ready for Work', type: 'routine' },
                    { time: '02:00 PM', label: '🛴 Travel to Work', type: 'routine' },
                    { time: '02:30 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '03:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '04:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '05:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '06:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '07:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '08:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '09:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '10:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '11:00 PM', label: '🛴 Travel Home', type: 'routine' },
                    { time: '11:30 PM', label: '💊 Mag Glycinate + Sleep', type: 'routine' }
                ],
                // Sunday: 11:00 AM - 5:00 PM shift
                work_sunday: [
                    { time: '06:30 AM', label: '🌅 Wake + NAC (1200mg)', type: 'routine' },
                    { time: '07:00 AM', label: '🍳 Breakfast + Supplements', type: 'routine' },
                    { time: '07:30 AM', label: '🐕 Quinn Walk', type: 'routine' },
                    { time: '08:30 AM', label: '💻 Lobotto / Projects', type: 'routine' },
                    { time: '09:00 AM', label: '💻 Lobotto / Projects', type: 'routine' },
                    { time: '09:30 AM', label: '🚿 Shower + Get Ready', type: 'routine' },
                    { time: '10:00 AM', label: '👔 Get Ready for Work', type: 'routine' },
                    { time: '10:30 AM', label: '🛴 Travel to Work', type: 'routine' },
                    { time: '11:00 AM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '12:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '01:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '02:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '03:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '04:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '05:00 PM', label: '🛴 Travel Home', type: 'routine' },
                    { time: '05:30 PM', label: '🐕 Quinn Afternoon Walk', type: 'routine' },
                    { time: '06:00 PM', label: '🍽️ Dinner Prep', type: 'routine' },
                    { time: '06:30 PM', label: '🍽️ Dinner + Fish Oil + D3', type: 'routine' },
                    { time: '07:30 PM', label: '📺 Downtime', type: 'routine' },
                    { time: '08:30 PM', label: '📺 Downtime', type: 'routine' },
                    { time: '09:00 PM', label: '💊 Mag Glycinate + Wind Down', type: 'routine' },
                    { time: '09:30 PM', label: '📖 Reading / Bed Prep', type: 'routine' },
                    { time: '10:00 PM', label: '😴 Sleep', type: 'routine' }
                ],
                // Monday: 12:00 PM - 6:00 PM shift
                work_monday: [
                    { time: '06:30 AM', label: '🌅 Wake + NAC (1200mg)', type: 'routine' },
                    { time: '07:00 AM', label: '🍳 Breakfast + Supplements', type: 'routine' },
                    { time: '07:30 AM', label: '🐕 Quinn Walk', type: 'routine' },
                    { time: '08:30 AM', label: '💻 Deep Work / Lobotto', type: 'routine' },
                    { time: '09:00 AM', label: '💻 Deep Work (continued)', type: 'routine' },
                    { time: '09:30 AM', label: '💻 Deep Work (continued)', type: 'routine' },
                    { time: '10:00 AM', label: '☕ Break', type: 'routine' },
                    { time: '10:30 AM', label: '🚿 Shower + Get Ready', type: 'routine' },
                    { time: '11:00 AM', label: '👔 Get Ready for Work', type: 'routine' },
                    { time: '11:30 AM', label: '🛴 Travel to Work', type: 'routine' },
                    { time: '12:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '01:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '02:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '03:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '04:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '05:00 PM', label: '⛽ BP Shift', type: 'routine' },
                    { time: '05:30 PM', label: '⛽ BP Shift (wrap up)', type: 'routine' },
                    { time: '06:00 PM', label: '🛴 Travel Home', type: 'routine' },
                    { time: '06:30 PM', label: '🍽️ Dinner + Fish Oil + D3', type: 'routine' },
                    { time: '07:30 PM', label: '📺 Downtime', type: 'routine' },
                    { time: '08:30 PM', label: '🐕 Quinn Evening Walk', type: 'routine' },
                    { time: '09:00 PM', label: '💊 Mag Glycinate + Wind Down', type: 'routine' },
                    { time: '09:30 PM', label: '📖 Reading / Bed Prep', type: 'routine' },
                    { time: '10:00 PM', label: '😴 Sleep', type: 'routine' }
                ]
            };

            // ========== DAY TYPE DETECTION ==========
            function getDayType() {
                const day = new Date().getDay(); // 0=Sun, 1=Mon, 2=Tue...
                if (day === 5 || day === 6) return 'work_evening';  // Fri, Sat
                if (day === 0) return 'work_sunday';                // Sun
                if (day === 1) return 'work_monday';                // Mon
                return 'off';                                       // Tue, Wed, Thu
            }

            function getDayLabel(dayType) {
                const labels = {
                    off: '🏠 Day Off',
                    work_evening: '⛽ Evening Shift',
                    work_sunday: '⛽ Sunday Shift',
                    work_monday: '⛽ Monday Shift'
                };
                return labels[dayType] || '📅 Today';
            }

            function getDayBadgeColor(dayType) {
                return dayType === 'off'
                    ? 'background: rgba(52,211,153,0.2); color: #22c55e; border: 1px solid rgba(52,211,153,0.4);'
                    : 'background: rgba(251,191,36,0.2); color: #fbbf24; border: 1px solid rgba(251,191,36,0.4);';
            }

            // ========== STORAGE KEYS ==========
            const STORAGE_KEY_TEMPLATE = 'schedule_template_'; // + dayType
            const STORAGE_KEY_TODAY = 'schedule_today_'; // + YYYY-MM-DD
            const STORAGE_KEY_DONE = 'schedule_done_'; // + YYYY-MM-DD

            function todayKey() {
                const d = new Date();
                return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
            }

            // ========== GET TEMPLATE ==========
            function getTemplate(dayType) {
                const saved = localStorage.getItem(STORAGE_KEY_TEMPLATE + dayType);
                if (saved) {
                    try { return JSON.parse(saved); } catch (e) { }
                }
                return DEFAULT_TEMPLATES[dayType] || DEFAULT_TEMPLATES.off;
            }

            function saveTemplate(dayType, items) {
                localStorage.setItem(STORAGE_KEY_TEMPLATE + dayType, JSON.stringify(items));
            }

            // ========== GET TODAY'S SCHEDULE ==========
            function getTodaySchedule() {
                const key = STORAGE_KEY_TODAY + todayKey();
                const saved = localStorage.getItem(key);
                if (saved) {
                    try { return JSON.parse(saved); } catch (e) { }
                }
                // First load today — clone from template
                const dayType = getDayType();
                const template = getTemplate(dayType);
                const schedule = template.map(item => ({ ...item }));
                saveTodaySchedule(schedule);
                return schedule;
            }

            function saveTodaySchedule(items) {
                localStorage.setItem(STORAGE_KEY_TODAY + todayKey(), JSON.stringify(items));
            }

            // ========== DONE TRACKING ==========
            function getDoneSet() {
                const saved = localStorage.getItem(STORAGE_KEY_DONE + todayKey());
                if (saved) {
                    try { return new Set(JSON.parse(saved)); } catch (e) { }
                }
                return new Set();
            }

            function saveDoneSet(doneSet) {
                localStorage.setItem(STORAGE_KEY_DONE + todayKey(), JSON.stringify([...doneSet]));
            }

            // ========== RENDER ==========
            function renderTemplateSchedule() {
                const schedule = getTodaySchedule();
                const doneSet = getDoneSet();
                const dayType = getDayType();

                // Set day badge
                const badge = document.getElementById('template-day-badge');
                if (badge) {
                    badge.textContent = getDayLabel(dayType);
                    badge.style.cssText = getDayBadgeColor(dayType);
                }

                // Clear existing template items from all drop zones
                document.querySelectorAll('.template-item').forEach(el => el.remove());

                // Place template items into their time slots
                schedule.forEach((item, idx) => {
                    const zone = document.querySelector(`.drop-zone[data-time="${item.time}"]`);
                    if (!zone) return;

                    const isDone = doneSet.has(idx + '_' + item.time);
                    const isAdhoc = item.type === 'adhoc';

                    const el = document.createElement('div');
                    el.className = 'template-item';
                    el.dataset.idx = idx;

                    // Colour coding
                    let borderColor = isAdhoc ? '#a855f7' : '#ef4444';
                    let bgColor = isAdhoc ? 'rgba(168,85,247,0.08)' : 'rgba(239,68,68,0.08)';
                    if (isDone) {
                        borderColor = '#22c55e';
                        bgColor = 'rgba(34,197,94,0.08)';
                    }

                    el.style.cssText = `
                    border-left: 3px solid ${borderColor};
                    background: ${bgColor};
                    padding: 0.4rem 0.6rem;
                    margin: 2px 0;
                    border-radius: 3px;
                    font-family: ui-monospace, monospace;
                    font-size: 0.95rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: pointer;
                    transition: all 0.15s ease;
                    ${isDone ? 'opacity: 0.5; text-decoration: line-through;' : ''}
                `;

                    const labelSpan = document.createElement('span');
                    labelSpan.textContent = item.label;
                    labelSpan.style.color = isDone ? '#22c55e' : 'var(--text-primary)';

                    const controls = document.createElement('div');
                    controls.style.cssText = 'display: flex; gap: 4px; align-items: center;';

                    // Done toggle
                    const doneBtn = document.createElement('button');
                    doneBtn.textContent = isDone ? '✅' : '⬜';
                    doneBtn.title = isDone ? 'Mark undone' : 'Mark done';
                    doneBtn.style.cssText = 'background: none; border: none; cursor: pointer; font-size: 1rem; padding: 0 2px;';
                    doneBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const ds = getDoneSet();
                        const key = idx + '_' + item.time;
                        if (ds.has(key)) { ds.delete(key); } else { ds.add(key); }
                        saveDoneSet(ds);
                        renderTemplateSchedule();
                    });

                    // Remove button (only for ad-hoc items)
                    if (isAdhoc) {
                        const removeBtn = document.createElement('button');
                        removeBtn.textContent = '×';
                        removeBtn.title = 'Remove';
                        removeBtn.style.cssText = 'background: none; border: none; cursor: pointer; font-size: 1.1rem; color: #ef4444; font-weight: bold; padding: 0 2px;';
                        removeBtn.addEventListener('click', (e) => {
                            e.stopPropagation();
                            const sched = getTodaySchedule();
                            sched.splice(idx, 1);
                            saveTodaySchedule(sched);
                            renderTemplateSchedule();
                        });
                        controls.appendChild(removeBtn);
                    }

                    controls.appendChild(doneBtn);
                    el.appendChild(labelSpan);
                    el.appendChild(controls);

                    // Prepend template items (before any Supabase-dragged tasks)
                    zone.insertBefore(el, zone.firstChild);
                });
            }

            // ========== AD-HOC ITEM ==========
            function populateTimeSelect() {
                const sel = document.getElementById('adhoc-time-select');
                if (!sel) return;
                const times = [];
                for (let h = 6; h <= 23; h++) {
                    for (let m = 0; m < 60; m += 30) {
                        const period = h >= 12 ? 'PM' : 'AM';
                        let displayH = h > 12 ? h - 12 : h;
                        if (displayH === 0) displayH = 12;
                        times.push(`${String(displayH).padStart(2, '0')}:${String(m).padStart(2, '0')} ${period}`);
                    }
                }
                sel.innerHTML = times.map(t => `<option value="${t}">${t}</option>`).join('');

                // Default to nearest time
                const now = new Date();
                const nowH = now.getHours();
                const nowM = now.getMinutes();
                const nearestM = nowM < 30 ? 0 : 30;
                const period = nowH >= 12 ? 'PM' : 'AM';
                let displayH = nowH > 12 ? nowH - 12 : nowH;
                if (displayH === 0) displayH = 12;
                const nearestTime = `${String(displayH).padStart(2, '0')}:${String(nearestM).padStart(2, '0')} ${period}`;
                sel.value = nearestTime;
            }

            function addAdhocItem() {
                const input = document.getElementById('adhoc-input');
                const sel = document.getElementById('adhoc-time-select');
                if (!input || !sel || !input.value.trim()) return;

                const schedule = getTodaySchedule();
                schedule.push({
                    time: sel.value,
                    label: '🟣 ' + input.value.trim(),
                    type: 'adhoc'
                });
                saveTodaySchedule(schedule);
                input.value = '';
                renderTemplateSchedule();
            }

            // ========== RESET TO TEMPLATE ==========
            function resetToTemplate() {
                if (!confirm('Reset today\'s schedule to the default template? This will remove all ad-hoc items.')) return;
                const dayType = getDayType();
                const template = getTemplate(dayType);
                saveTodaySchedule(template.map(item => ({ ...item })));
                saveDoneSet(new Set());
                renderTemplateSchedule();
            }

            // ========== EDIT TEMPLATE ==========
            let editModalOpen = false;

            function editTemplate() {
                if (editModalOpen) return;
                editModalOpen = true;

                const dayType = getDayType();
                const template = getTemplate(dayType);
                const dayLabel = getDayLabel(dayType);

                // Generate all time slots 6:00 AM to 11:30 PM
                const ALL_SLOTS = [];
                for (let h = 6; h <= 23; h++) {
                    for (let m = 0; m < 60; m += 30) {
                        const period = h >= 12 ? 'PM' : 'AM';
                        let dh = h > 12 ? h - 12 : h;
                        if (dh === 0) dh = 12;
                        ALL_SLOTS.push(`${String(dh).padStart(2, '0')}:${String(m).padStart(2, '0')} ${period}`);
                    }
                }

                // Build slot map: time -> array of task labels
                let slotMap = {};
                ALL_SLOTS.forEach(t => slotMap[t] = []);
                // Parking: tasks not assigned to any slot
                let parkedTasks = [];
                let nextId = 0;

                template.forEach(item => {
                    const task = { label: item.label, _id: 'tpl_' + (nextId++) };
                    if (slotMap[item.time]) {
                        slotMap[item.time].push(task);
                    } else {
                        parkedTasks.push(task);
                    }
                });

                // Create modal
                const overlay = document.createElement('div');
                overlay.id = 'template-edit-modal';
                overlay.style.cssText = `
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    background: rgba(0,0,0,0.7); z-index: 100000;
                    display: flex; align-items: center; justify-content: center;
                    backdrop-filter: blur(4px);
                `;

                const modal = document.createElement('div');
                modal.style.cssText = `
                    background: #1e1e2e; border: 2px solid #a855f7;
                    border-radius: 8px; padding: 1.25rem; width: 900px; max-width: 95vw;
                    height: 85vh; display: flex; flex-direction: column;
                    font-family: ui-monospace, monospace; color: #e2e8f0;
                    box-shadow: 0 0 30px rgba(168,85,247,0.3);
                `;

                modal.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <h3 style="margin: 0; color: #a855f7; font-size: 1.2rem;">
                            ✏️ Edit Template — ${dayLabel}
                        </h3>
                        <span style="font-size: 0.8rem; color: #64748b;">Drag tasks into time slots</span>
                    </div>

                    <!-- Add New Task -->
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem; padding: 0.4rem; background: rgba(168,85,247,0.08); border: 1px solid rgba(168,85,247,0.2); border-radius: 4px;">
                        <input type="text" id="tpl-add-label" placeholder="New task label (e.g. 🏋️ Exercise)" style="flex: 1; padding: 0.3rem 0.5rem; background: #0f0f1a; border: 1px solid #334155; color: #e2e8f0; font-family: ui-monospace, monospace; font-size: 0.95rem;">
                        <button id="tpl-add-btn" style="padding: 0.3rem 0.75rem; background: rgba(168,85,247,0.2); border: 1px solid #a855f7; color: #a855f7; font-family: ui-monospace, monospace; font-size: 0.95rem; cursor: pointer; font-weight: bold;">+ Add to Parking</button>
                    </div>

                    <!-- Two Column Layout -->
                    <div style="display: flex; gap: 0.75rem; flex: 1; min-height: 0; overflow: hidden;">
                        <!-- Timeline Column -->
                        <div style="flex: 2; display: flex; flex-direction: column; min-width: 0;">
                            <div style="font-size: 0.9rem; color: #ef4444; font-weight: bold; margin-bottom: 0.3rem; padding-left: 4px;">
                                📅 Timeline
                            </div>
                            <div id="tpl-timeline" style="flex: 1; overflow-y: auto; padding-right: 4px;"></div>
                        </div>
                        <!-- Parking Column -->
                        <div style="flex: 1; display: flex; flex-direction: column; min-width: 180px;">
                            <div style="font-size: 0.9rem; color: #fbbf24; font-weight: bold; margin-bottom: 0.3rem; padding-left: 4px;">
                                🅿️ Parking <span id="tpl-park-count" style="color: #64748b; font-weight: normal;"></span>
                            </div>
                            <div id="tpl-parking" style="
                                flex: 1; overflow-y: auto; padding: 0.4rem;
                                background: rgba(251,191,36,0.03); border: 2px dashed rgba(251,191,36,0.2);
                                border-radius: 4px; min-height: 100px;
                            "></div>
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.6rem; justify-content: flex-end;">
                        <button id="tpl-cancel" style="padding: 0.4rem 0.8rem; background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: #ef4444; font-family: ui-monospace, monospace; font-size: 1rem; cursor: pointer; border-radius: 4px;">Cancel</button>
                        <button id="tpl-save" style="padding: 0.4rem 0.8rem; background: rgba(168,85,247,0.2); border: 1px solid #a855f7; color: #a855f7; font-family: ui-monospace, monospace; font-size: 1rem; cursor: pointer; border-radius: 4px; font-weight: bold;">💾 Save Template</button>
                    </div>
                `;

                overlay.appendChild(modal);
                document.body.appendChild(overlay);

                // ---- Drag State ----
                let dragTask = null;
                let dragSourceSlot = null; // null = from parking

                function createTaskChip(task, fromSlot) {
                    const chip = document.createElement('div');
                    chip.draggable = true;
                    chip.dataset.id = task._id;
                    chip.style.cssText = `
                        display: inline-flex; align-items: center; gap: 4px;
                        padding: 0.25rem 0.5rem; margin: 2px;
                        background: ${fromSlot ? 'rgba(239,68,68,0.12)' : 'rgba(251,191,36,0.12)'};
                        border: 1px solid ${fromSlot ? 'rgba(239,68,68,0.3)' : 'rgba(251,191,36,0.3)'};
                        border-radius: 3px; cursor: grab; font-size: 0.9rem;
                        transition: all 0.1s; max-width: 100%; white-space: nowrap;
                        overflow: hidden; text-overflow: ellipsis;
                    `;

                    const labelSpan = document.createElement('span');
                    labelSpan.textContent = task.label;
                    labelSpan.style.cssText = 'flex: 1; overflow: hidden; text-overflow: ellipsis; cursor: text;';
                    labelSpan.title = 'Click to edit';
                    labelSpan.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = task.label;
                        input.style.cssText = 'background: #0f0f1a; border: 1px solid #a855f7; color: #e2e8f0; font-family: ui-monospace, monospace; font-size: 0.9rem; padding: 1px 4px; width: 100%;';
                        labelSpan.replaceWith(input);
                        input.focus();
                        input.select();
                        const finishEdit = () => {
                            task.label = input.value.trim() || task.label;
                            renderModal();
                        };
                        input.addEventListener('blur', finishEdit);
                        input.addEventListener('keypress', (ev) => { if (ev.key === 'Enter') finishEdit(); });
                    });

                    const delBtn = document.createElement('span');
                    delBtn.textContent = '×';
                    delBtn.style.cssText = 'color: #ef4444; cursor: pointer; font-weight: bold; font-size: 1rem; flex-shrink: 0; padding: 0 2px;';
                    delBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        // Remove from wherever it is
                        ALL_SLOTS.forEach(t => { slotMap[t] = slotMap[t].filter(x => x._id !== task._id); });
                        parkedTasks = parkedTasks.filter(x => x._id !== task._id);
                        renderModal();
                    });

                    chip.appendChild(labelSpan);
                    chip.appendChild(delBtn);

                    chip.addEventListener('dragstart', (e) => {
                        dragTask = task;
                        dragSourceSlot = fromSlot;
                        chip.style.opacity = '0.4';
                        e.dataTransfer.effectAllowed = 'move';
                    });
                    chip.addEventListener('dragend', () => {
                        chip.style.opacity = '1';
                        dragTask = null;
                        dragSourceSlot = null;
                    });

                    return chip;
                }

                function removeTaskEverywhere(task) {
                    ALL_SLOTS.forEach(t => { slotMap[t] = slotMap[t].filter(x => x._id !== task._id); });
                    parkedTasks = parkedTasks.filter(x => x._id !== task._id);
                }

                function renderModal() {
                    const timeline = document.getElementById('tpl-timeline');
                    const parking = document.getElementById('tpl-parking');
                    timeline.innerHTML = '';
                    parking.innerHTML = '';

                    // Build timeline slots
                    ALL_SLOTS.forEach(time => {
                        const row = document.createElement('div');
                        row.style.cssText = 'display: flex; align-items: stretch; margin-bottom: 1px; min-height: 32px;';

                        const timeLabel = document.createElement('div');
                        timeLabel.textContent = time;
                        timeLabel.style.cssText = 'width: 75px; flex-shrink: 0; font-size: 0.8rem; color: #64748b; padding: 0.3rem 0; text-align: right; padding-right: 8px;';

                        const dropZone = document.createElement('div');
                        dropZone.dataset.slot = time;
                        const hasItems = slotMap[time].length > 0;
                        dropZone.style.cssText = `
                            flex: 1; min-height: 30px; padding: 2px 4px;
                            background: ${hasItems ? 'rgba(239,68,68,0.05)' : 'rgba(255,255,255,0.02)'};
                            border: 1px solid ${hasItems ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.06)'};
                            border-radius: 3px; display: flex; flex-wrap: wrap; align-items: center;
                            gap: 3px; transition: all 0.15s;
                        `;

                        // Add task chips to slot
                        slotMap[time].forEach(task => {
                            dropZone.appendChild(createTaskChip(task, time));
                        });

                        // Drop zone events
                        dropZone.addEventListener('dragover', (e) => {
                            e.preventDefault();
                            dropZone.style.borderColor = '#a855f7';
                            dropZone.style.background = 'rgba(168,85,247,0.1)';
                        });
                        dropZone.addEventListener('dragleave', () => {
                            dropZone.style.borderColor = slotMap[time].length > 0 ? 'rgba(239,68,68,0.15)' : 'rgba(255,255,255,0.06)';
                            dropZone.style.background = slotMap[time].length > 0 ? 'rgba(239,68,68,0.05)' : 'rgba(255,255,255,0.02)';
                        });
                        dropZone.addEventListener('drop', (e) => {
                            e.preventDefault();
                            if (!dragTask) return;
                            removeTaskEverywhere(dragTask);
                            slotMap[time].push(dragTask);
                            renderModal();
                        });

                        row.appendChild(timeLabel);
                        row.appendChild(dropZone);
                        timeline.appendChild(row);
                    });

                    // Build parking
                    if (parkedTasks.length === 0) {
                        parking.innerHTML = '<div style="color: #64748b; font-size: 0.85rem; text-align: center; padding: 1.5rem 0.5rem;">Drag tasks here to unassign them from a time slot</div>';
                    } else {
                        parkedTasks.forEach(task => {
                            parking.appendChild(createTaskChip(task, null));
                        });
                    }

                    // Parking drop zone
                    parking.addEventListener('dragover', (e) => {
                        e.preventDefault();
                        parking.style.borderColor = '#a855f7';
                    });
                    parking.addEventListener('dragleave', () => {
                        parking.style.borderColor = 'rgba(251,191,36,0.2)';
                    });
                    parking.addEventListener('drop', (e) => {
                        e.preventDefault();
                        if (!dragTask) return;
                        removeTaskEverywhere(dragTask);
                        parkedTasks.push(dragTask);
                        renderModal();
                    });

                    document.getElementById('tpl-park-count').textContent = `(${parkedTasks.length})`;
                }

                // Initial render
                renderModal();

                // Add new task to parking
                document.getElementById('tpl-add-btn').addEventListener('click', () => {
                    const label = document.getElementById('tpl-add-label').value.trim();
                    if (!label) return;
                    parkedTasks.push({ label, _id: 'new_' + (nextId++) });
                    document.getElementById('tpl-add-label').value = '';
                    renderModal();
                });
                document.getElementById('tpl-add-label').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') document.getElementById('tpl-add-btn').click();
                });

                // Close
                overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
                document.getElementById('tpl-cancel').addEventListener('click', closeModal);

                // Save
                document.getElementById('tpl-save').addEventListener('click', () => {
                    if (parkedTasks.length > 0) {
                        if (!confirm(`${parkedTasks.length} task(s) still parked (no time assigned). They won't be saved. Continue?`)) return;
                    }

                    const newItems = [];
                    ALL_SLOTS.forEach(time => {
                        slotMap[time].forEach(task => {
                            newItems.push({ time, label: task.label, type: 'routine' });
                        });
                    });

                    if (newItems.length === 0) {
                        alert('No tasks assigned to time slots. Drag tasks into the timeline before saving.');
                        return;
                    }

                    saveTemplate(dayType, newItems);
                    saveTodaySchedule(newItems.map(item => ({ ...item })));
                    saveDoneSet(new Set());
                    renderTemplateSchedule();
                    closeModal();
                });

                function closeModal() {
                    overlay.remove();
                    editModalOpen = false;
                }
            }

            // ========== INIT ==========
            function initTemplateSchedule() {
                populateTimeSelect();
                // Render after a short delay to let Supabase tasks load first
                setTimeout(renderTemplateSchedule, 500);

                // Bind buttons
                const resetBtn = document.getElementById('reset-template-btn');
                if (resetBtn) resetBtn.addEventListener('click', resetToTemplate);

                const editBtn = document.getElementById('edit-template-btn');
                if (editBtn) editBtn.addEventListener('click', editTemplate);

                const addBtn = document.getElementById('adhoc-add-btn');
                if (addBtn) addBtn.addEventListener('click', addAdhocItem);

                const adhocInput = document.getElementById('adhoc-input');
                if (adhocInput) adhocInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') addAdhocItem();
                });

                // Also update the header badge
                const headerBadge = document.querySelector('.badge');
                if (headerBadge) {
                    const dayType = getDayType();
                    headerBadge.textContent = getDayLabel(dayType).replace(/[^\w\s]/g, '').trim();
                }
            }

            // Run immediately if DOM is ready, otherwise wait
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initTemplateSchedule);
            } else {
                initTemplateSchedule();
            }

            // Expose for external use
            window.renderTemplateSchedule = renderTemplateSchedule;
        })();
    </script>
</body>

</html>
`

## public\retro-audio.js
`javascript
// ============================
// 🌿 AMBIENT AUDIO ENGINE v3
// Calming ambient BGM + soft UI sounds
// ============================

let retroAudioCtx = null;
let bgmPlaying = false;
let bgmNodes = [];
let masterGain = null;
let currentTrackIdx = 0;
let loopTimer = null;

// ── Ambient Pad Engine ────────────────────────────────────────
// Uses:  sine-wave sustained chord layers, slow movement,
//        a feedback delay for warmth, and low-pass filter for haze.

const AMBIENT_TRACKS = [
    {
        name: 'Northern Light',
        // D minor pentatonic — slow, airy, wide
        chords: [
            [146.83, 220.00, 293.66],   // Dm
            [164.81, 220.00, 329.63],   // F
            [174.61, 261.63, 349.23],   // G
            [146.83, 220.00, 293.66],   // Dm
        ],
        melody: [587.33, 659.25, 698.46, 587.33, 523.25, 493.88, 523.25, 587.33],
        barLen: 6.0,           // seconds per chord
        melStepLen: 3.0
    },
    {
        name: 'Deep Water',
        // C pentatonic — very low, deep
        chords: [
            [130.81, 196.00, 261.63],
            [146.83, 220.00, 293.66],
            [123.47, 185.00, 246.94],
            [130.81, 196.00, 261.63],
        ],
        melody: [523.25, 587.33, 523.25, 493.88, 440.00, 493.88, 523.25, 587.33],
        barLen: 7.0,
        melStepLen: 3.5
    },
    {
        name: 'Stillness',
        // G major pentatonic — open, airy
        chords: [
            [196.00, 293.66, 392.00],
            [220.00, 329.63, 440.00],
            [246.94, 329.63, 392.00],
            [196.00, 293.66, 392.00],
        ],
        melody: [784.00, 880.00, 784.00, 698.46, 659.25, 698.46, 784.00, 880.00],
        barLen: 8.0,
        melStepLen: 4.0
    }
];

// Build a reverb-like convolver from a noise impulse
function createReverb(ctx, duration = 2.5, decay = 2.0) {
    const sr = ctx.sampleRate;
    const length = sr * duration;
    const impulse = ctx.createBuffer(2, length, sr);
    for (let c = 0; c < 2; c++) {
        const data = impulse.getChannelData(c);
        for (let i = 0; i < length; i++) {
            data[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / length, decay);
        }
    }
    const conv = ctx.createConvolver();
    conv.buffer = impulse;
    return conv;
}

function playAmbientTrack(trackIdx) {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    const track = AMBIENT_TRACKS[trackIdx % AMBIENT_TRACKS.length];

    stopAllNodes();

    // Signal chain: oscBus → filter → reverb(wet) + dry → master
    masterGain = ctx.createGain();
    masterGain.gain.value = 0.09;
    masterGain.connect(ctx.destination);

    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 1800;
    filter.Q.value = 0.6;
    filter.connect(masterGain);

    const reverb = createReverb(ctx, 3.0, 2.5);
    const reverbGain = ctx.createGain();
    reverbGain.gain.value = 0.55;
    reverb.connect(reverbGain);
    reverbGain.connect(masterGain);

    // Bus for wet path
    const wetBus = ctx.createGain();
    wetBus.gain.value = 1;
    wetBus.connect(filter);
    wetBus.connect(reverb);

    let playCount = 0;
    const loopsPerTrack = 2;

    function scheduleLoop() {
        if (!bgmPlaying) return;
        if (playCount >= loopsPerTrack) {
            currentTrackIdx = (currentTrackIdx + 1) % AMBIENT_TRACKS.length;
            updateTrackDisplay();
            playAmbientTrack(currentTrackIdx);
            return;
        }

        const now = ctx.currentTime + 0.1;
        const { chords, melody, barLen, melStepLen } = track;
        const totalLen = chords.length * barLen;

        // Pad chords — slow sustained sine tones with long crossfade
        chords.forEach((chord, ci) => {
            const barStart = now + ci * barLen;
            const barEnd = barStart + barLen + 0.6; // slight overlap for crossfade
            chord.forEach(freq => {
                const osc = ctx.createOscillator();
                const env = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.value = freq;
                // add a tiny detuned twin for warmth
                const osc2 = ctx.createOscillator();
                osc2.type = 'sine';
                osc2.frequency.value = freq * 1.003;
                const attack = Math.min(1.2, barLen * 0.18);
                const release = Math.min(1.5, barLen * 0.25);
                env.gain.setValueAtTime(0, barStart);
                env.gain.linearRampToValueAtTime(0.28, barStart + attack);
                env.gain.setValueAtTime(0.28, barEnd - release);
                env.gain.linearRampToValueAtTime(0, barEnd);
                [osc, osc2].forEach(o => { o.connect(env); o.start(barStart); o.stop(barEnd + 0.1); bgmNodes.push(o); });
                env.connect(wetBus);
            });
        });

        // Slow melody layer (very soft, high octave, every melStepLen seconds)
        melody.forEach((freq, mi) => {
            const noteStart = now + mi * melStepLen;
            if (noteStart >= now + totalLen) return;
            const osc = ctx.createOscillator();
            const env = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            const noteDur = melStepLen * 0.85;
            env.gain.setValueAtTime(0, noteStart);
            env.gain.linearRampToValueAtTime(0.10, noteStart + 0.3);
            env.gain.setValueAtTime(0.10, noteStart + noteDur - 0.5);
            env.gain.linearRampToValueAtTime(0, noteStart + noteDur);
            osc.connect(env);
            env.connect(wetBus);
            osc.start(noteStart);
            osc.stop(noteStart + noteDur + 0.1);
            bgmNodes.push(osc);
        });

        playCount++;
        loopTimer = setTimeout(scheduleLoop, totalLen * 1000);
    }

    bgmPlaying = true;
    scheduleLoop();
}

function stopAllNodes() {
    if (loopTimer) { clearTimeout(loopTimer); loopTimer = null; }
    bgmNodes.forEach(n => { try { n.stop(); } catch (e) { } });
    bgmNodes = [];
}

function updateTrackDisplay() {
    const btn = document.getElementById('audio-toggle');
    if (btn && bgmPlaying) {
        const track = AMBIENT_TRACKS[currentTrackIdx % AMBIENT_TRACKS.length];
        btn.textContent = '🔊 ' + track.name;
        btn.style.color = 'var(--accent-green, #00c9a0)';
    }
}

function toggleRetroAudio() {
    const btn = document.getElementById('audio-toggle');
    if (bgmPlaying) {
        bgmPlaying = false;
        stopAllNodes();
        if (btn) { btn.textContent = '🔇 Music Off'; btn.style.color = '#555'; }
        localStorage.setItem('symphony_music', 'off');
    } else {
        playAmbientTrack(currentTrackIdx);
        updateTrackDisplay();
        localStorage.setItem('symphony_music', 'on');
    }
}

// ── Soft Mechanical Keyboard Thock ───────────────────────────
function playRetroClick() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    const now = ctx.currentTime;

    // 1. Noise burst — the "click" transient
    const bufLen = ctx.sampleRate * 0.04; // 40ms of noise
    const noiseBuf = ctx.createBuffer(1, bufLen, ctx.sampleRate);
    const data = noiseBuf.getChannelData(0);
    for (let i = 0; i < bufLen; i++) data[i] = Math.random() * 2 - 1;

    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuf;

    // Bandpass filter shapes it into a "mid click"
    const bp = ctx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1400;
    bp.Q.value = 1.8;

    const noiseGain = ctx.createGain();
    noiseGain.gain.setValueAtTime(0.18, now);
    noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.035);

    noise.connect(bp);
    bp.connect(noiseGain);
    noiseGain.connect(ctx.destination);
    noise.start(now);
    noise.stop(now + 0.04);

    // 2. Body thud — the low "thock" resonance
    const body = ctx.createOscillator();
    const bodyGain = ctx.createGain();
    body.type = 'sine';
    body.frequency.setValueAtTime(145, now);
    body.frequency.exponentialRampToValueAtTime(60, now + 0.03);
    bodyGain.gain.setValueAtTime(0.12, now);
    bodyGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.05);
    body.connect(bodyGain);
    bodyGain.connect(ctx.destination);
    body.start(now);
    body.stop(now + 0.06);
}

function playRetroSuccess() {
    if (!retroAudioCtx) retroAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = retroAudioCtx;
    // Three soft rising sine tones — gentle success chime
    [523.25, 659.25, 783.99].forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        const t = ctx.currentTime + i * 0.1;
        gain.gain.setValueAtTime(0.06, t);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(t);
        osc.stop(t + 0.3);
    });
}

// ── Wire SFX + Auto-resume ────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('button, .tab-btn, .checkbox');
        if (btn && btn.id !== 'audio-toggle') {
            playRetroClick();
        }
    });

    if (localStorage.getItem('symphony_music') === 'on') {
        const autoStart = () => {
            playAmbientTrack(currentTrackIdx);
            updateTrackDisplay();
            document.removeEventListener('click', autoStart);
        };
        document.addEventListener('click', autoStart, { once: true });
    }
});

`

## public\shadow.html
`html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shadow Protocol | The Life Hub</title>
                <link rel="stylesheet" href="styles.css">
    <style>
        /* Aurora Teal / Indigo Specific Overrides */
        :root {
            --aurora-teal: #0d9488;
            --aurora-teal-glow: rgba(13, 148, 136, 0.4);
            --aurora-indigo: #6366f1;
            --aurora-indigo-glow: rgba(99, 102, 241, 0.4);
            --bg-deep: #0f172a;
        }

        body {
            background: var(--bg-deep);
            color: #e2e8f0;
            overflow-x: hidden;
        }

        /* Ambient background glow */
        .aurora-bg {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: -1;
            overflow: hidden;
            background: radial-gradient(circle at 15% 50%, rgba(13, 148, 136, 0.15), transparent 40%),
                        radial-gradient(circle at 85% 30%, rgba(99, 102, 241, 0.15), transparent 40%);
        }
        
        .blob {
            position: absolute;
            filter: blur(80px);
            opacity: 0.6;
            border-radius: 50%;
            animation: float 20s infinite alternate ease-in-out;
        }
        .blob-teal { width: 40vw; height: 40vw; background: var(--aurora-teal-glow); top: -10%; left: -10%; }
        .blob-indigo { width: 35vw; height: 35vw; background: var(--aurora-indigo-glow); bottom: -10%; right: -10%; animation-delay: -10s; }

        @keyframes float {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(5%, 10%) scale(1.1); }
        }

        .glass-panel-teal {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }

        .glass-panel-teal:hover {
            box-shadow: 0 8px 32px rgba(13, 148, 136, 0.15);
            border-color: rgba(13, 148, 136, 0.3);
        }

        /* Teeter Totter CSS */
        .seesaw-container {
            position: relative;
            height: 100px;
            margin: 2rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .seesaw-board {
            width: 80%;
            height: 8px;
            background: linear-gradient(90deg, #e2e8f0, #475569);
            position: absolute;
            border-radius: 4px;
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            transform-origin: center;
            transform: rotate(0deg);
            z-index: 2;
        }
        .seesaw-fulcrum {
            width: 0;
            height: 0;
            border-left: 20px solid transparent;
            border-right: 20px solid transparent;
            border-bottom: 40px solid var(--aurora-teal);
            position: absolute;
            bottom: 10px;
            z-index: 1;
        }
        .seesaw-weight {
            width: 40px; height: 40px;
            border-radius: 50%;
            position: absolute;
            top: -30px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }
        .weight-left { left: 5%; background: #f8fafc; color: #000; } /* Persona */
        .weight-right { right: 5%; background: #1e293b; border: 2px solid var(--aurora-teal); } /* Shadow */

        /* Trigger Journal */
        .journal-textarea {
            width: 100%;
            min-height: 150px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
            color: #f8fafc;
            font-family: system-ui, -apple-system, sans-serif;
            padding: 1rem;
            border-radius: 8px;
            resize: vertical;
            margin-top: 1rem;
            transition: border-color 0.3s;
        }
        .journal-textarea:focus {
            outline: none;
            border-color: var(--aurora-indigo);
            box-shadow: 0 0 15px var(--aurora-indigo-glow);
        }

        .btn-teal {
            background: rgba(13, 148, 136, 0.2);
            border: 1px solid var(--aurora-teal);
            color: var(--aurora-teal);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-family: ui-monospace, monospace;
            font-size: 1.1rem;
            transition: all 0.2s;
        }
        .btn-teal:hover {
            background: rgba(13, 148, 136, 0.4);
            box-shadow: 0 0 10px var(--aurora-teal-glow);
            color: #fff;
        }

        /* Chair Exercise */
        .chair-tabs { display: flex; gap: 1rem; margin-bottom: 1rem; }
        .chair-tab {
            flex: 1; padding: 1rem; text-align: center;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px; cursor: pointer;
            transition: all 0.3s;
        }
        .chair-tab.active { background: rgba(99, 102, 241, 0.2); border-color: var(--aurora-indigo); }
        .chair-content { display: none; }
        .chair-content.active { display: block; animation: fadeIn 0.4s; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        .genetic-tag {
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
            margin-right: 0.5rem;
            font-family: ui-monospace, monospace;
        }
    </style>
</head>
<body>
    <div class="aurora-bg">
        <div class="blob blob-teal"></div>
        <div class="blob blob-indigo"></div>
    </div>

    <div class="app-container" style="max-width: 900px; margin: 0 auto; padding: 2rem;">
        <header class="glass-panel-teal" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; font-size: 2rem; background: linear-gradient(90deg, #5eead4, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Shadow Protocol</h1>
                <p style="margin: 0.25rem 0 0 0; color: #94a3b8; font-size: 0.9rem;">Robert A. Johnson Framework | Loner Empath Integration</p>
                <div style="margin-top: 0.5rem;">
                    <span class="genetic-tag">OXTR A/A</span>
                    <span class="genetic-tag" style="background: rgba(245, 158, 11, 0.15); border-color: rgba(245, 158, 11, 0.3); color: #fcd34d;">COMT G/G</span>
                    <span class="genetic-tag" style="background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.3); color: #93c5fd;">TNF-Alpha</span>
                </div>
            </div>
            <a href="index.html" class="btn-teal" style="text-decoration: none; border-color: rgba(255,255,255,0.2); color: #e2e8f0;">← Back to Life Hub</a>
        </header>

        <!-- Teeter-Totter -->
        <section class="glass-panel-teal">
            <h2 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.2rem;">⚖️</span> The Law of Compensation</h2>
            <p style="color: #cbd5e1; font-size: 0.9rem;">For every quality pushed into the "light" Persona, an equal weight drops into the Shadow. Log today's balance.</p>
            
            <div class="seesaw-container">
                <div class="seesaw-fulcrum"></div>
                <div class="seesaw-board" id="seesaw-board">
                    <div class="seesaw-weight weight-left" title="Persona (I'm fine, independent)">🎭</div>
                    <div class="seesaw-weight weight-right" title="Shadow (Unacknowledged needs/anger)">🌑</div>
                </div>
            </div>

            <div style="display: flex; justify-content: space-between; margin-top: 1rem;">
                <button class="btn-teal" data-action="seesaw" data-amount="-10" style="border-color: #94a3b8; color: #94a3b8;">+ Performed "I'm Fine"</button>
                <button class="btn-teal" data-action="seesaw" data-amount="10">+ Chose Vulnerability</button>
            </div>
            <div style="text-align: center; margin-top: 0.5rem; font-family: ui-monospace, monospace; color: var(--aurora-teal);" id="seesaw-status">Balance is neutral.</div>
        </section>

        <!-- Daily Trigger Journal -->
        <section class="glass-panel-teal">
            <h2 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.2rem;">📓</span> Daily Trigger Journal</h2>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">What part of yourself are you seeing in others?</p>
                <button class="btn-teal" data-action="rotate-prompt" style="font-size: 0.9rem; padding: 0.3rem 0.6rem;">🔄 Change Prompt</button>
            </div>
            
            <div style="background: rgba(99, 102, 241, 0.1); border-left: 3px solid var(--aurora-indigo); padding: 0.75rem; margin-top: 1rem; border-radius: 0 4px 4px 0; font-style: italic; color: #c7d2fe;" id="journal-prompt">
                "What quality do I hate most in others right now? Do I possess it?"
            </div>

            <textarea class="journal-textarea" id="shadow-journal" placeholder="Write without censoring. The shadow speaks here..."></textarea>
            
            <div style="display: flex; justify-content: flex-end; margin-top: 0.75rem; gap: 0.5rem;">
                <span id="journal-save-msg" style="color: var(--aurora-teal); align-self: center; font-family: ui-monospace, monospace; display: none;">Saved to LocalStorage.</span>
                <button class="btn-teal" data-action="save-journal">💾 Save Entry</button>
                <button class="btn-teal" data-action="clear-journal" style="background: transparent; border-color: #ef4444; color: #ef4444;">🗑️ Clear</button>
            </div>
        </section>

        <!-- 3-Chair Exercise -->
        <section class="glass-panel-teal">
            <h2 style="margin-top: 0; display: flex; align-items: center; gap: 0.5rem;"><span style="font-size: 1.2rem;">🪑</span> The 3-Chair Exercise</h2>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin-bottom: 1.5rem;">Process a specific conflict or trigger by physically or mentally shifting perspectives.</p>

            <div class="chair-tabs">
                <div class="chair-tab active" data-action="chair" data-idx="0">
                    <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">👤</div>
                    <strong>1. Ego</strong>
                </div>
                <div class="chair-tab" data-action="chair" data-idx="1">
                    <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🌑</div>
                    <strong>2. Shadow</strong>
                </div>
                <div class="chair-tab" data-action="chair" data-idx="2">
                    <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">👁️</div>
                    <strong>3. Self</strong>
                </div>
            </div>

            <div class="chair-content active" id="chair-0">
                <h3 style="color: #cbd5e1;">The Everyday Self</h3>
                <p style="font-size: 0.9rem; color: #94a3b8;">State the problem from your Persona's perspective. How were you wronged? Why are you "fine" or justified?</p>
                <textarea class="journal-textarea" id="chair-0-text" style="min-height: 100px;" placeholder="The problem is..."></textarea>
            </div>

            <div class="chair-content" id="chair-1">
                <h3 style="color: #818cf8;">The Disowned Part</h3>
                <p style="font-size: 0.9rem; color: #94a3b8;">Speak as the part you exile. What is its truth? Are you actually angry? Do you secretly need something?</p>
                <textarea class="journal-textarea" id="chair-1-text" style="min-height: 100px; border-color: rgba(99, 102, 241, 0.3);" placeholder="Actually, I am..."></textarea>
            </div>

            <div class="chair-content" id="chair-2">
                <h3 style="color: #5eead4;">The Synthesizer (The Mandorla)</h3>
                <p style="font-size: 0.9rem; color: #94a3b8;">Hold both truths simultaneously. What is the integrated response? (e.g., "I am independent AND I need connection")</p>
                <textarea class="journal-textarea" id="chair-2-text" style="min-height: 100px; border-color: rgba(13, 148, 136, 0.3);" placeholder="Holding both, I choose to..."></textarea>
            </div>
            
            <div style="display: flex; justify-content: flex-end; margin-top: 1rem; gap: 0.5rem;">
                <span id="chair-save-msg" style="color: var(--aurora-teal); align-self: center; font-family: ui-monospace, monospace; display: none;">Saved to Backend.</span>
                <button class="btn-teal" data-action="save-chair">💾 Save Exercise</button>
            </div>
        </section>

    </div>
    <script src="shadow.js"></script>
</body>
</html>

`

## public\shadow.js
`javascript
/**
 * Shadow Protocol — client logic
 *
 * Fixes vs the old inline version:
 *  - API is same-origin ('/api'), so it works when opened over Tailscale from
 *    any device. (The old 'http://localhost:3001' pointed at whatever device
 *    you opened the page on — your phone, not the Spark.)
 *  - No inline event handlers, so it works under a strict Content-Security-Policy.
 */
(function () {
  'use strict';

  const API_BASE = '/api';
  const API_TOKEN = 'local_tailnet_token';

  async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
      method,
      headers: { 
        'Authorization': `Bearer ${API_TOKEN}`,
        'Content-Type': 'application/json' 
      }
    };
    if (body) options.body = JSON.stringify(body);
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, options);
      if (res.status === 401) { window.location.href = '/'; return null; }
      return await res.json();
    } catch (e) {
      console.error('API Error:', e);
      return null;
    }
  }

  // ── Teeter Totter ────────────────────────────────────────
  let tilt = 0;
  function adjustSeesaw(amount) {
    tilt = Math.max(-30, Math.min(30, tilt + amount));
    updateSeesawUI();
    apiCall('/shadow/balance', 'POST', { tilt_value: tilt });
  }
  function updateSeesawUI() {
    const board = document.getElementById('seesaw-board');
    const status = document.getElementById('seesaw-status');
    if (board) board.style.transform = `rotate(${tilt}deg)`;
    if (!status) return;
    if (tilt < -10) {
      status.textContent = '⚠️ Warning: Persona overload. Shadow weight accumulating.';
      status.style.color = '#ef4444';
    } else if (tilt > 10) {
      status.textContent = '⭐ Integration active. Tension is releasing.';
      status.style.color = '#5eead4';
    } else {
      status.textContent = 'Balance is neutral.';
      status.style.color = 'var(--aurora-teal)';
    }
  }

  // ── Journal ──────────────────────────────────────────────
  const prompts = [
    'What quality do I hate most in others right now? Do I possess it?',
    'What am I pretending not to need today?',
    "If I had no 'independent' image to maintain, what would I do differently?",
    'What would I scream right now if no one could hear?',
    "Where did I say 'I'm fine' today when I actually wasn't?"
  ];
  let promptIdx = 0;

  function rotatePrompt() {
    promptIdx = (promptIdx + 1) % prompts.length;
    const el = document.getElementById('journal-prompt');
    if (el) el.textContent = `"${prompts[promptIdx]}"`;
  }

  async function saveJournal() {
    const text = document.getElementById('shadow-journal').value;
    const msg = document.getElementById('journal-save-msg');
    if (msg) { msg.textContent = 'Syncing…'; msg.style.display = 'inline'; }
    await apiCall('/shadow/journal', 'POST', { prompt: prompts[promptIdx], entry_text: text });
    if (msg) { msg.textContent = 'Saved.'; setTimeout(() => { msg.style.display = 'none'; }, 2000); }
  }

  function clearJournal() {
    if (confirm('Clear current entry?')) {
      document.getElementById('shadow-journal').value = '';
    }
  }

  // ── 3-Chair Exercise ─────────────────────────────────────
  function switchChair(idx) {
    const tabs = document.querySelectorAll('.chair-tab');
    const contents = document.querySelectorAll('.chair-content');
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    if (tabs[idx]) tabs[idx].classList.add('active');
    if (contents[idx]) contents[idx].classList.add('active');
  }

  async function saveChairExercise() {
    const msg = document.getElementById('chair-save-msg');
    if (msg) { msg.textContent = 'Syncing…'; msg.style.display = 'inline'; }
    await apiCall('/shadow/chair', 'POST', {
      ego_text: document.getElementById('chair-0-text').value,
      shadow_text: document.getElementById('chair-1-text').value,
      self_text: document.getElementById('chair-2-text').value
    });
    if (msg) { msg.textContent = 'Saved.'; setTimeout(() => { msg.style.display = 'none'; }, 2000); }
  }

  // ── Wire up events (no inline handlers) ──────────────────
  function wire() {
    document.querySelectorAll('[data-action]').forEach(node => {
      const action = node.getAttribute('data-action');
      node.addEventListener('click', () => {
        switch (action) {
          case 'seesaw': adjustSeesaw(Number(node.getAttribute('data-amount')) || 0); break;
          case 'rotate-prompt': rotatePrompt(); break;
          case 'save-journal': saveJournal(); break;
          case 'clear-journal': clearJournal(); break;
          case 'chair': switchChair(Number(node.getAttribute('data-idx')) || 0); break;
          case 'save-chair': saveChairExercise(); break;
        }
      });
    });
  }

  // ── Boot: load saved state ───────────────────────────────
  async function boot() {
    wire();

    const bal = await apiCall('/shadow/balance');
    if (bal && typeof bal.tilt_value === 'number') { tilt = bal.tilt_value; updateSeesawUI(); }

    const journal = await apiCall('/shadow/journal');
    if (journal && journal.entry_text) {
      const ta = document.getElementById('shadow-journal');
      if (ta) ta.value = journal.entry_text;
      if (journal.prompt) {
        const idx = prompts.indexOf(String(journal.prompt).replace(/"/g, ''));
        if (idx !== -1) promptIdx = idx;
        const pe = document.getElementById('journal-prompt');
        if (pe) pe.textContent = `"${prompts[promptIdx]}"`;
      }
    }

    const chair = await apiCall('/shadow/chair');
    if (chair) {
      const map = { 'chair-0-text': chair.ego_text, 'chair-1-text': chair.shadow_text, 'chair-2-text': chair.self_text };
      for (const [id, val] of Object.entries(map)) {
        const el = document.getElementById(id);
        if (el && val) el.value = val;
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

`

## public\styles.css
`css
/* ============================================
   LIFE HUB — AURORA TEAL THEME
   ============================================ */

@import url('https://fonts.googleapis.com/css2?family=VT323&family=Inter:wght@300;400;500;600&display=swap');

:root {
    /* Core palette */
    --bg-primary:       #061414;
    --bg-deep:          #030d0d;
    --glass-bg:         rgba(6, 28, 28, 0.72);
    --glass-bg-light:   rgba(10, 40, 38, 0.55);
    --glass-border:     rgba(0, 200, 160, 0.15);
    --glass-border-hot: rgba(0, 210, 175, 0.35);

    /* Accent colours */
    --accent-green:     #00c9a0;
    --accent-teal:      #0d9488;
    --accent-blue:      #38bdf8;
    --accent-purple:    #a78bfa;
    --accent-yellow:    #fbbf24;
    --accent-red:       #f87171;
    --accent-orange:    #fb923c;
    --accent-magenta:   #f472b6;
    --accent-coral:     #f87171;

    /* Text */
    --text-primary:     rgba(220, 245, 240, 0.92);
    --text-secondary:   rgba(160, 210, 200, 0.6);
    --text-dim:         rgba(100, 160, 150, 0.45);

    /* Win95 compat vars (used by inline JS‐generated styles) */
    --win-highlight:    rgba(0,200,160,0.3);
    --win-shadow:       rgba(0,0,0,0.5);
    --win-dark-shadow:  rgba(0,0,0,0.8);
    --bg-panel:         var(--glass-bg);

    /* Geometry */
    --radius-lg:  6px;
    --radius-md:  4px;
    --radius-sm:  2px;

    --transition-smooth: all 0.2s ease;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* ── Body + Aurora Background ─────────────────── */
body {
    font-family: 'VT323', monospace;
    background-color: var(--bg-primary);
    background-image:
        radial-gradient(ellipse 80% 50% at 60% -5%,  rgba(0, 180, 130, 0.18) 0%, transparent 65%),
        radial-gradient(ellipse 50% 35% at 15% 8%,   rgba(0, 140, 200, 0.10) 0%, transparent 60%),
        radial-gradient(ellipse 120% 80% at 50% 100%, rgba(3, 20, 20, 0.9)   0%, transparent 100%);
    color: var(--text-primary);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    overflow-x: hidden;
    line-height: 1.6;
    font-size: 18px;
}

/* Aurora animated wisps */
.background-effects {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: -1;
    pointer-events: none;
    overflow: hidden;
}

.blur-blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.12;
    animation: drift 18s ease-in-out infinite alternate;
}

.blur-blob:nth-child(1) {
    width: 500px; height: 300px;
    background: radial-gradient(ellipse, #00c9a0, transparent);
    top: -80px; left: 55%;
    animation-duration: 20s;
}
.blur-blob:nth-child(2) {
    width: 350px; height: 200px;
    background: radial-gradient(ellipse, #0891b2, transparent);
    top: -40px; left: 10%;
    animation-duration: 25s;
    animation-delay: -8s;
}
.blur-blob:nth-child(3) {
    width: 250px; height: 180px;
    background: radial-gradient(ellipse, #0d9488, transparent);
    top: 60px; left: 35%;
    animation-duration: 30s;
    animation-delay: -14s;
    opacity: 0.08;
}

@keyframes drift {
    from { transform: translateX(0) translateY(0) scale(1); }
    to   { transform: translateX(40px) translateY(20px) scale(1.1); }
}

/* ── Layout ───────────────────────────────────── */
.app-container {
    width: 100%;
    max-width: 1100px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    position: relative;
    z-index: 1;
}

/* ── Glass Panels ─────────────────────────────── */
.glass-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 1rem;
    box-shadow:
        0 4px 24px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(0,200,160,0.08);
    color: var(--text-primary);
    transition: border-color 0.2s;
}

.glass-panel:hover {
    border-color: var(--glass-border-hot);
}

/* ── Header ───────────────────────────────────── */
header.glass-panel {
    background: linear-gradient(135deg,
        rgba(6, 30, 28, 0.9) 0%,
        rgba(10, 45, 40, 0.85) 100%);
    border-color: rgba(0, 200, 160, 0.25);
    text-align: center;
}

/* Remove Under Construction banner */
header.glass-panel::after {
    display: none;
}

header h1 {
    font-family: 'VT323', monospace;
    font-size: 2.2rem;
    font-weight: 400;
    margin: 0.4rem 0 0.2rem 0;
    color: var(--accent-green);
    text-shadow: 0 0 20px rgba(0, 200, 160, 0.35);
    letter-spacing: 3px;
    background: none;
    -webkit-background-clip: unset;
    background-clip: unset;
    -webkit-text-fill-color: var(--accent-green);
}

.subtitle {
    color: var(--text-secondary);
    font-size: 1rem;
}

.date-display {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 1rem;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
    text-transform: uppercase;
    justify-content: center;
}

.badge {
    background: rgba(0, 200, 160, 0.15);
    color: var(--accent-green);
    padding: 0.2rem 0.75rem;
    border-radius: var(--radius-sm);
    font-size: 0.9rem;
    border: 1px solid rgba(0, 200, 160, 0.3);
    font-weight: bold;
    animation: none;
}

/* ── Tabs ─────────────────────────────────────── */
.tabs {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 2px;
    background: rgba(4, 18, 18, 0.7);
    padding: 4px;
    border-radius: var(--radius-md);
    border: 1px solid var(--glass-border);
    backdrop-filter: blur(10px);
}

.tab-btn {
    flex: 0 1 auto;
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-secondary);
    padding: 0.3rem 0.8rem;
    border-radius: var(--radius-sm);
    font-family: 'VT323', monospace;
    font-size: 1rem;
    font-weight: 400;
    cursor: pointer;
    transition: color 0.15s, background 0.15s, border-color 0.15s;
}

.tab-btn:hover {
    color: var(--text-primary);
    background: rgba(0, 200, 160, 0.08);
    border-color: var(--glass-border);
}

.tab-btn:active {
    background: rgba(0, 200, 160, 0.15);
}

.tab-btn.active {
    background: rgba(0, 200, 160, 0.18);
    color: var(--accent-green);
    border-color: rgba(0, 200, 160, 0.4);
    font-weight: bold;
}

/* ── Content ──────────────────────────────────── */
.tab-content {
    display: none;
    animation: fadeIn 0.2s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to   { opacity: 1; transform: translateY(0); }
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--glass-border);
    padding-bottom: 0.75rem;
}

.section-header h2 {
    font-family: 'VT323', monospace;
    font-weight: 400;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.4rem;
    color: var(--accent-green);
    letter-spacing: 1px;
}

.sub-text {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}

/* ── Progress ─────────────────────────────────── */
.progress-container {
    width: 200px;
    height: 8px;
    background: rgba(0,0,0,0.4);
    border: 1px solid var(--glass-border);
    border-radius: 2px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-teal), var(--accent-green));
    width: 0%;
    transition: width 0.4s ease;
    border-radius: 2px;
}

/* ── Sub-panels ───────────────────────────────── */
.sub-panel {
    background: rgba(4, 20, 20, 0.5);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 1rem;
}

.sub-panel h3 {
    margin-bottom: 0.5rem;
    color: var(--accent-green);
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'VT323', monospace;
    font-weight: 400;
}

/* ── Timeline ─────────────────────────────────── */
.timeline {
    position: relative;
    padding-left: 1.5rem;
}

.timeline::before {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    left: 7px;
    width: 1px;
    background: linear-gradient(180deg,
        var(--accent-green) 0%,
        var(--accent-teal) 50%,
        transparent 100%);
    opacity: 0.4;
}

.timeline-item {
    position: relative;
    margin-bottom: 1.25rem;
    cursor: pointer;
}

.timeline-item:last-child { margin-bottom: 0; }

.timeline-item::before {
    content: '◆';
    position: absolute;
    top: 3px;
    left: -1.7rem;
    color: var(--accent-teal);
    font-size: 10px;
    opacity: 0.7;
}

.timeline-item.completed::before {
    content: '✔';
    color: var(--accent-green);
    opacity: 1;
}

.timeline-item.completed .time,
.timeline-item.completed .task-title {
    opacity: 0.4;
    text-decoration: line-through;
}

.time {
    font-size: 0.9rem;
    color: var(--accent-teal);
    font-weight: 500;
    margin-bottom: 0.2rem;
    display: block;
}

.task-title {
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-primary);
}

.task-desc {
    font-size: 0.9rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}

.tag {
    display: inline-block;
    padding: 0.1rem 0.5rem;
    background: rgba(0, 200, 160, 0.12);
    border: 1px solid rgba(0, 200, 160, 0.25);
    border-radius: var(--radius-sm);
    font-size: 0.8rem;
    margin-top: 0.4rem;
    color: var(--accent-green);
}

.tag.break {
    color: var(--accent-blue);
    background: rgba(56, 189, 248, 0.1);
    border-color: rgba(56, 189, 248, 0.25);
}

/* ── Task Lists ───────────────────────────────── */
.task-list {
    list-style: none;
}

.task-list li {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.6rem 0.8rem;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    margin-bottom: 0.4rem;
    transition: background 0.15s, border-color 0.15s;
}

.task-list li:hover {
    background: rgba(0, 200, 160, 0.06);
    border-color: var(--glass-border-hot);
}

.checkbox {
    width: 18px;
    height: 18px;
    border: 1px solid var(--glass-border-hot);
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    margin-top: 3px;
    background: rgba(0,0,0,0.3);
    flex-shrink: 0;
    transition: background 0.15s;
}

.checkbox.checked {
    background: rgba(0, 200, 160, 0.3);
    border-color: var(--accent-green);
}

.checkbox.checked::after {
    content: '✓';
    color: var(--accent-green);
    font-size: 12px;
}

.task-content {
    flex: 1;
    color: var(--text-primary);
}

.task-list li.completed .task-content {
    opacity: 0.4;
    text-decoration: line-through;
}

/* ── Grids ────────────────────────────────────── */
.grid-2-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.grid-3-col {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.75rem;
}

/* ── Workout ──────────────────────────────────── */
.workout-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid var(--glass-border);
    padding: 1rem;
    border-radius: var(--radius-md);
    transition: border-color 0.15s;
}

.workout-card:hover {
    border-color: var(--glass-border-hot);
}

.workout-focus {
    font-size: 1rem;
    color: var(--accent-teal);
    margin-bottom: 0.75rem;
    font-weight: 500;
}

.workout-list {
    list-style: none;
    font-size: 1rem;
}

.workout-list li {
    margin-bottom: 0.4rem;
    padding-left: 1.2rem;
    position: relative;
    color: var(--text-primary);
}

.workout-list li::before {
    content: "▸";
    color: var(--accent-teal);
    position: absolute;
    left: 0;
    font-size: 0.85em;
}

.workout-rules {
    background: rgba(0, 200, 160, 0.05);
    border-left: 3px solid var(--accent-teal);
    padding: 0.75rem 1rem;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    line-height: 1.7;
    color: var(--text-primary);
}

/* ── Briefing ─────────────────────────────────── */
.briefing-content {
    background: rgba(0,0,0,0.25);
    border: 1px solid var(--glass-border);
    padding: 1rem;
    border-radius: var(--radius-sm);
    font-size: 1rem;
    line-height: 1.6;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    margin-top: 0.75rem;
    color: var(--text-primary);
}

.text-secondary {
    color: var(--text-secondary);
}

/* ── Today Grid ───────────────────────────────── */
.today-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;
    align-items: start;
}

/* ── Lock Screen ──────────────────────────────── */
.lock-container {
    width: 100%;
    max-width: 400px;
    margin: auto;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    z-index: 10;
}

.password-input-group {
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
}

#password-input {
    width: 100%;
    padding: 0.75rem;
    background: rgba(0,0,0,0.4);
    border: 1px solid var(--glass-border-hot);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-size: 1.2rem;
    font-family: 'VT323', monospace;
}

#password-input:focus {
    outline: none;
    border-color: var(--accent-green);
    box-shadow: 0 0 0 2px rgba(0, 200, 160, 0.15);
}

.error-msg {
    color: var(--accent-red);
    font-size: 1rem;
    margin-top: 0.75rem;
    border: 1px solid rgba(248, 113, 113, 0.3);
    background: rgba(248, 113, 113, 0.08);
    padding: 0.5rem;
    border-radius: var(--radius-sm);
}

/* ── Scrollbar ────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb {
    background: rgba(0, 200, 160, 0.25);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 200, 160, 0.4);
}

/* ── Drag and Drop ────────────────────────────── */
.draggable-task {
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    padding: 0.5rem;
    cursor: grab;
    transition: border-color 0.15s, box-shadow 0.15s;
    user-select: none;
    color: var(--text-primary);
}

.draggable-task:active { cursor: grabbing; }

.draggable-task.dragging {
    opacity: 0.6;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    border-color: var(--accent-teal);
    z-index: 100;
}

.drop-zone.drag-over {
    background-color: rgba(0, 200, 160, 0.06) !important;
    border: 1px dashed var(--accent-teal) !important;
}

/* ── Quick Add ────────────────────────────────── */
#quick-add-input {
    background: rgba(0,0,0,0.35) !important;
    border: 1px solid var(--glass-border) !important;
    color: var(--text-primary) !important;
    font-family: 'VT323', monospace !important;
    font-size: 1.1rem !important;
    border-radius: var(--radius-sm) !important;
}

#quick-add-input:focus {
    border-color: var(--accent-teal) !important;
    outline: none !important;
}

#quick-add-btn {
    background: rgba(0, 200, 160, 0.15) !important;
    border: 1px solid rgba(0, 200, 160, 0.3) !important;
    color: var(--accent-green) !important;
    font-family: 'VT323', monospace !important;
    font-size: 1.1rem !important;
    border-radius: var(--radius-sm) !important;
    cursor: pointer;
}

#quick-add-btn:hover {
    background: rgba(0, 200, 160, 0.25) !important;
}

/* ── Lock-In Button ───────────────────────────── */
#lock-in-btn {
    background: rgba(0, 200, 160, 0.15);
    border: 1px solid rgba(0, 200, 160, 0.35);
    color: var(--accent-green);
    font-family: 'VT323', monospace;
    font-size: 1rem;
    padding: 0.3rem 1rem;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: background 0.15s;
}

#lock-in-btn:hover {
    background: rgba(0, 200, 160, 0.25);
}

/* ── Planner Sidebar Layout ────────────────────── */
.planner-layout {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 1.25rem;
    align-items: start;
}

.planner-sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    position: sticky;
    top: 1rem;
}

.planner-sidebar-card {
    background: rgba(4, 20, 20, 0.6);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 0.85rem;
}

.planner-sidebar-card h4 {
    font-family: 'VT323', monospace;
    font-size: 0.85rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--glass-border);
}

/* Mini Calendar */
.mini-cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    font-size: 0.8rem;
}

.mini-cal-day-header {
    text-align: center;
    color: var(--text-dim);
    font-size: 0.7rem;
    padding: 2px 0;
}

.mini-cal-cell {
    text-align: center;
    padding: 3px 1px;
    border-radius: 2px;
    cursor: default;
    color: var(--text-secondary);
    transition: background 0.1s;
}

.mini-cal-cell.today {
    background: rgba(0, 200, 160, 0.25);
    color: var(--accent-green);
    font-weight: bold;
    border-radius: 2px;
}

.mini-cal-cell.other-month {
    opacity: 0.25;
}

.mini-cal-month-label {
    text-align: center;
    font-size: 0.9rem;
    color: var(--accent-green);
    margin-bottom: 0.5rem;
    letter-spacing: 1px;
}

/* Sidebar Tasks */
.sidebar-task-input {
    width: 100%;
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: 'VT323', monospace;
    font-size: 0.95rem;
    padding: 0.3rem 0.5rem;
    margin-bottom: 0.5rem;
    outline: none;
}

.sidebar-task-input:focus {
    border-color: var(--accent-teal);
}

.sidebar-task-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 3px;
    max-height: 160px;
    overflow-y: auto;
}

.sidebar-task-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 3px 4px;
    border-radius: 2px;
    font-size: 0.85rem;
    color: var(--text-primary);
}

.sidebar-task-item input[type="checkbox"] {
    accent-color: var(--accent-green);
    cursor: pointer;
}

.sidebar-task-item span {
    flex: 1;
}

.sidebar-task-item.done span {
    text-decoration: line-through;
    opacity: 0.4;
}

.sidebar-task-item button {
    background: none;
    border: none;
    color: var(--text-dim);
    cursor: pointer;
    font-size: 0.75rem;
    padding: 0 2px;
    opacity: 0;
    transition: opacity 0.1s;
}

.sidebar-task-item:hover button {
    opacity: 1;
}

/* Sidebar Notes */
.sidebar-notes-area {
    width: 100%;
    min-height: 90px;
    background: rgba(0,0,0,0.3);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: 'VT323', monospace;
    font-size: 0.9rem;
    padding: 0.4rem 0.5rem;
    resize: vertical;
    outline: none;
    line-height: 1.5;
}

.sidebar-notes-area:focus {
    border-color: var(--accent-teal);
}

/* ── Bio Tracking Accordion ───────────────────── */
.bio-accordion-header {
    cursor: pointer;
    user-select: none;
}

/* ── General Input / Select overrides ─────────── */
input[type="text"],
input[type="number"],
input[type="password"],
input[type="time"],
input[type="date"],
select,
textarea {
    background: rgba(0,0,0,0.35);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-sm);
    color: var(--text-primary);
    font-family: 'VT323', monospace;
    padding: 0.35rem 0.5rem;
    font-size: 1rem;
}

input[type="text"]:focus,
input[type="number"]:focus,
input[type="time"]:focus,
input[type="date"]:focus,
select:focus,
textarea:focus {
    outline: none;
    border-color: var(--accent-teal);
    box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.15);
}

select {
    cursor: pointer;
}

select option {
    background: #061814;
    color: var(--text-primary);
}

/* ── Responsive ───────────────────────────────── */
@media (max-width: 1024px) {
    .today-grid { grid-template-columns: 1fr; gap: 1rem; }
    .grid-2-col { grid-template-columns: 1fr; }
    .planner-layout { grid-template-columns: 1fr; }
    .planner-sidebar { position: static; }
}

@media (max-width: 768px) {
    .grid-2-col, .grid-3-col { grid-template-columns: 1fr; }
    .section-header { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
    .tabs { flex-direction: column; }
    .today-grid { grid-template-columns: 1fr; gap: 0.75rem; }
    .slot-label { width: 55px !important; font-size: 0.7rem !important; }
    .draggable-task { font-size: 0.85rem; padding: 0.35rem; }
    .section-header h2 { font-size: 1.1rem; }
    .sub-panel h3 { font-size: 0.9rem !important; }
    .app-container, .glass-panel, .sub-panel, .pool-accordion-body {
        max-width: 100vw;
        overflow-x: hidden;
    }
}

@media (max-width: 480px) {
    .slot-label { width: 50px !important; font-size: 0.6rem !important; }
    .draggable-task { font-size: 0.8rem; padding: 0.25rem; }
    .section-header h2 { font-size: 0.95rem; }
    .sub-panel h3 { font-size: 0.75rem !important; }
    .coming-up-event { font-size: 0.85rem; padding: 2px 4px; }
}

html, body {
    overflow-x: hidden;
    max-width: 100vw;
}
`

## public\symphony-app.js
`javascript
document.addEventListener('DOMContentLoaded', () => {
    // --- Dynamic Date Header ---
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const updateDate = () => {
            const now = new Date();
            const dayName = now.toLocaleDateString('en-NZ', { weekday: 'long' });
            const month = now.toLocaleDateString('en-NZ', { month: 'short' });
            const day = now.getDate();
            dateEl.textContent = `${dayName}, ${month} ${day}`;
        };
        updateDate();
        setInterval(updateDate, 60000); // refresh every minute
    }

    // --- Supplement History State ---
    window.bioTrackingDate = new Date();

    function getLocalDateString(dateObj) {
        const year = dateObj.getFullYear();
        const month = String(dateObj.getMonth() + 1).padStart(2, '0');
        const day = String(dateObj.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    // --- Accordion Toggle via Event Delegation ---
    // Placed at the very top of DOMContentLoaded to ensure registration
    // even if subsequent initialization functions fail silently.
    document.body.addEventListener('click', (e) => {
        // Bio Tab Accordion
        const bioHeader = e.target.closest('.bio-accordion-header');
        if (bioHeader) {
            const targetId = bioHeader.getAttribute('data-bio-panel');
            if (!targetId) return;
            const body = document.getElementById(targetId);
            const toggle = bioHeader.querySelector('.bio-toggle');
            if (!body || !toggle) return;

            const isOpen = bioHeader.classList.contains('expanded');
            if (isOpen) {
                body.style.display = 'none';
                bioHeader.classList.remove('expanded');
                toggle.textContent = '►';
            } else {
                body.style.display = 'block';
                bioHeader.classList.add('expanded');
                toggle.textContent = '▼';
            }
            return;
        }

        // Supplement Timing Sub-Accordion
        const suppHeader = e.target.closest('.supp-timing-header');
        if (suppHeader) {
            const targetId = suppHeader.getAttribute('data-supp-body');
            if (!targetId) return;
            const body = document.getElementById(targetId);
            const toggle = suppHeader.querySelector('.supp-toggle');
            if (!body || !toggle) return;

            const isOpen = suppHeader.classList.contains('expanded');
            if (isOpen) {
                body.style.display = 'none';
                suppHeader.classList.remove('expanded');
                toggle.textContent = '►';
            } else {
                body.style.display = 'block';
                suppHeader.classList.add('expanded');
                toggle.textContent = '▼';
            }
            return;
        }
    });

    // --- Local Sovereign Backend Configuration ---
    const API_BASE = "/api"; // same-origin: works over Tailscale from any device
    const API_TOKEN = "local_tailnet_token";

    // Auth & Lock Screen Logic removed - relying on Tailscale

    // --- Financial Calculations (NZ) ---
    // Helper: compute NZ net income for a given weekly gross
    function computeNZNetWeekly(grossWeekly) {
        const kiwiSaverRate = 0.03;
        const annualizedGross = grossWeekly * 52;

        // KiwiSaver
        const weeklyKiwiSaver = grossWeekly * kiwiSaverRate;

        // Student Loan (12% over $438/week threshold)
        const slThreshold = 438.00;
        let weeklyStudentLoan = 0;
        if (grossWeekly > slThreshold) {
            weeklyStudentLoan = (grossWeekly - slThreshold) * 0.12;
        }

        // PAYE Tax (M Tax Code)
        let annualizedTax = 0;
        if (annualizedGross <= 15600) {
            annualizedTax = annualizedGross * 0.105;
        } else if (annualizedGross <= 53500) {
            annualizedTax = (15600 * 0.105) + ((annualizedGross - 15600) * 0.175);
        } else if (annualizedGross <= 78100) {
            annualizedTax = (15600 * 0.105) + ((53500 - 15600) * 0.175) + ((annualizedGross - 53500) * 0.30);
        } else {
            annualizedTax = (15600 * 0.105) + ((53500 - 15600) * 0.175) + ((78100 - 53500) * 0.30) + ((annualizedGross - 78100) * 0.33);
        }

        const accLevy = annualizedGross * 0.0139;
        const weeklyPayeAndAcc = (annualizedTax + accLevy) / 52;

        const totalDeductions = weeklyPayeAndAcc + weeklyStudentLoan + weeklyKiwiSaver;
        const netWeekly = grossWeekly - totalDeductions;

        return { netWeekly, weeklyPayeAndAcc, weeklyStudentLoan, weeklyKiwiSaver, annualizedGross };
    }

    // Global reference so budget builder can use it
    window.currentNetWeekly = 0;

    function calculateFinance() {
        // User Variables
        const baseHourlyRate = 24.00;

        const hoursInput = document.getElementById('input-hours');
        const holidayInput = document.getElementById('input-holiday');

        const hoursWorked = hoursInput ? parseFloat(hoursInput.value) || 0 : 28.5;
        const isHoliday = holidayInput ? holidayInput.classList.contains('checked') : false;

        const hourlyRate = isHoliday ? baseHourlyRate * 1.5 : baseHourlyRate;

        // Base Calculations
        const grossWeekly = hourlyRate * hoursWorked;
        const result = computeNZNetWeekly(grossWeekly);

        const formatCurrency = (num) => '$' + num.toFixed(2);
        const formatCurrencyRound = (num) => '$' + Math.round(num).toLocaleString();

        // Update existing DOM elements
        document.getElementById('finance-hours').innerText = hoursWorked + ' hrs';
        document.getElementById('finance-gross').innerText = formatCurrency(grossWeekly);
        document.getElementById('finance-tax').innerText = '-' + formatCurrency(result.weeklyPayeAndAcc);
        document.getElementById('finance-sl').innerText = '-' + formatCurrency(result.weeklyStudentLoan);
        document.getElementById('finance-ks').innerText = '-' + formatCurrency(result.weeklyKiwiSaver);
        document.getElementById('finance-net-pay').innerText = formatCurrency(result.netWeekly);

        // Store for budget summary
        window.currentNetWeekly = result.netWeekly;

        // --- Yearly Income Projection ---
        // Baseline: 28.5h/wk at $24/hr (non-holiday)
        const baselineGrossWeekly = 24.00 * 28.5;
        const baseline = computeNZNetWeekly(baselineGrossWeekly);
        const baselineAnnualNet = baseline.netWeekly * 52;

        // Current: at whatever hours/rate they entered
        const currentAnnualNet = result.netWeekly * 52;

        const yearlyBaseGrossEl = document.getElementById('finance-yearly-baseline-gross');
        const yearlyBaseNetEl = document.getElementById('finance-yearly-baseline-net');
        const yearlyCurrentGrossEl = document.getElementById('finance-yearly-current-gross');
        const yearlyCurrentNetEl = document.getElementById('finance-yearly-current-net');
        const yearlyDiffEl = document.getElementById('finance-yearly-diff');

        if (yearlyBaseGrossEl) yearlyBaseGrossEl.innerText = formatCurrencyRound(baselineGrossWeekly * 52);
        if (yearlyBaseNetEl) yearlyBaseNetEl.innerText = formatCurrencyRound(baselineAnnualNet);
        if (yearlyCurrentGrossEl) yearlyCurrentGrossEl.innerText = formatCurrencyRound(grossWeekly * 52);
        if (yearlyCurrentNetEl) yearlyCurrentNetEl.innerText = formatCurrencyRound(currentAnnualNet);

        if (yearlyDiffEl) {
            const diff = currentAnnualNet - baselineAnnualNet;
            if (Math.abs(diff) < 1) {
                yearlyDiffEl.innerText = 'At baseline hours';
            } else if (diff > 0) {
                yearlyDiffEl.innerHTML = `<span style="color: var(--accent-green);">+${formatCurrencyRound(diff)}/yr</span> above baseline`;
            } else {
                yearlyDiffEl.innerHTML = `<span style="color: var(--accent-red);">${formatCurrencyRound(diff)}/yr</span> below baseline`;
            }
        }

        // Update budget summary if expenses are loaded
        if (typeof window.updateBudgetSummary === 'function') {
            window.updateBudgetSummary();
        }

        // Refresh Pulse financial snapshot
        if (typeof window.refreshPulse === 'function') {
            window.refreshPulse();
        }

        // Initialize/Update Pie Chart (guarded — Chart.js may not be loaded from file:// protocol)
        try {
            if (typeof Chart !== 'undefined') {
                const ctx = document.getElementById('financePieChart').getContext('2d');
                if (window.financeChartInstance) {
                    window.financeChartInstance.destroy();
                }

                window.financeChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Net Pay', 'PAYE & ACC', 'Student Loan', 'KiwiSaver (3%)'],
                        datasets: [{
                            data: [result.netWeekly, result.weeklyPayeAndAcc, result.weeklyStudentLoan, result.weeklyKiwiSaver],
                            backgroundColor: [
                                'rgba(52, 211, 153, 0.8)', // Green (Net)
                                'rgba(239, 68, 68, 0.8)',  // Red (Tax)
                                'rgba(245, 158, 11, 0.8)', // Orange (SL)
                                'rgba(56, 189, 248, 0.8)'  // Blue (KS)
                            ],
                            borderColor: 'rgba(15, 23, 42, 1)',
                            borderWidth: 2,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: {
                                    color: '#94a3b8',
                                    font: { size: 11 }
                                }
                            }
                        },
                        cutout: '65%'
                    }
                });
            }
        } catch (chartErr) {
            console.warn('Finance chart unavailable:', chartErr.message);
        }
    }

    calculateFinance();

    // Set up finance input listeners
    const hoursInput = document.getElementById('input-hours');
    if (hoursInput) {
        // Load on boot
        const savedHours = localStorage.getItem('symphony_finance_hours');
        if (savedHours) hoursInput.value = savedHours;

        hoursInput.addEventListener('input', () => {
            localStorage.setItem('symphony_finance_hours', hoursInput.value);
            calculateFinance();
        });
    }

    const holidayInput = document.getElementById('input-holiday');
    if (holidayInput) {
        // Load on boot
        const savedHoliday = localStorage.getItem('symphony_finance_holiday') === 'true';
        if (savedHoliday) holidayInput.classList.add('checked');

        holidayInput.addEventListener('click', () => {
            holidayInput.classList.toggle('checked');
            localStorage.setItem('symphony_finance_holiday', holidayInput.classList.contains('checked'));
            calculateFinance();
        });
    }

    // Initial calculation
    calculateFinance();

    // --- Tab Navigation Logic ---
    const tabBtns = document.querySelectorAll('.tab-btn[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');

    function activateTab(tabId) {
        const targetBtn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
        if (!targetBtn) return;

        // Remove active style from all tabs and hide all contents
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => {
            c.classList.remove('active');
            c.style.display = 'none';
        });

        // Add active style to the matched tab
        targetBtn.classList.add('active');

        // Show target content
        const targetContent = document.getElementById(tabId);
        if (targetContent) {
            targetContent.classList.add('active');
            targetContent.style.display = 'block';
        }
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            activateTab(targetId);
            localStorage.setItem('symphony_active_tab', targetId);
        });
    });

    // Persist active tab across refreshes
    const savedTab = localStorage.getItem('symphony_active_tab') || 'today';
    activateTab(savedTab);

    // Explicitly hide non-active tabs on load to be safe
    tabContents.forEach(c => {
        if (!c.classList.contains('active')) {
            c.style.display = 'none';
        }
    });

    // --- Quick Add Logic ---
    const quickAddInput = document.getElementById('quick-add-input');
    const quickAddBtn = document.getElementById('quick-add-btn');
    const quickAddCategory = document.getElementById('quick-add-category');
    const quickAddPriority = document.getElementById('quick-add-priority');

    async function handleQuickAdd() {
        const title = quickAddInput.value.trim();
        if (!title) return;

        const category = quickAddCategory ? quickAddCategory.value : 'Unscheduled';
        const priorityColor = quickAddPriority ? quickAddPriority.value : 'ORANGE';

        quickAddBtn.innerText = "⏳";
        quickAddBtn.style.pointerEvents = "none";

        const newTask = {
            title: title,
            points: 2,
            priority_color: priorityColor,
            time_target: category,
            is_active: true
        };

        try {
            const response = await apiFetch(`/tasks`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify([newTask])
                });

            if (response.ok) {
                quickAddInput.value = '';
                await fetchTasksAndRenderTimeline();
            } else {
                console.error("Failed to add quick task:", response.statusText);
                alert("Failed to add task.");
            }
        } catch (err) {
            console.error("Network error adding task:", err);
        } finally {
            quickAddBtn.innerText = "Add";
            quickAddBtn.style.pointerEvents = "auto";
        }
    }

    if (quickAddBtn) quickAddBtn.addEventListener('click', handleQuickAdd);
    if (quickAddInput) quickAddInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuickAdd();
    });

    // --- Pool Add Item Handlers (Weekly/Monthly/Backlog) ---
    function setupPoolAddButton(inputId, btnId, timeTarget) {
        const input = document.getElementById(inputId);
        const btn = document.getElementById(btnId);
        if (!input || !btn) return;

        async function addPoolItem() {
            const title = input.value.trim();
            if (!title) return;
            btn.innerText = '⏳';
            btn.style.pointerEvents = 'none';
            try {
                const response = await apiFetch(`/tasks`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify([{ title, points: 2, priority_color: 'GREEN', time_target: timeTarget, is_active: true }])
                });
                if (response.ok) {
                    input.value = '';
                    await fetchTasksAndRenderTimeline();
                } else {
                    console.error('Failed to add pool item:', response.statusText);
                }
            } catch (err) {
                console.error('Network error adding pool item:', err);
            } finally {
                btn.innerText = '+';
                btn.style.pointerEvents = 'auto';
            }
        }

        btn.addEventListener('click', addPoolItem);
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') addPoolItem(); });
    }

    setupPoolAddButton('pool-week-input', 'pool-week-add-btn', 'Weekly');
    setupPoolAddButton('pool-longterm-input', 'pool-longterm-add-btn', 'Monthly');
    setupPoolAddButton('pool-future-input', 'pool-future-add-btn', 'Unscheduled');

    // Store our dynamically fetched tasks here
    let dynamicTasks = [];

    // Drag and Drop State
    let draggedTaskObj = null;

    // --- Dynamic Drag and Drop Logic ---
    // --- READONLY TODAY VIEW ---
    async function fetchReadonlyToday() {
        try {
            const response = await apiFetch(`/tasks`, { headers: { "Authorization": `Bearer ${API_TOKEN}` } });
            if (response.ok) {
                const allTasks = await response.json();
                renderReadonlyToday(allTasks);
            }
        } catch (e) {
            console.error("Error fetching readonly timeline:", e);
        }
    }

    function renderReadonlyToday(tasks) {
        const container = document.getElementById('today-schedule-readonly');
        if (!container) return;

        // Filter tasks that belong to the timeline
        let timelineTasks = tasks.filter(t => {
            if (!t.time_target) return false;
            // Match specific time "hh:mm AM" or range "hh:mm AM - hh:mm AM"
            return /^\d{2}:\d{2}\s*(AM|PM)/i.test(t.time_target);
        });

        // Sort by time
        function timeToMinutes(timeStr) {
            const match = timeStr.trim().match(/^(\d{2}):(\d{2})\s*(AM|PM)/i);
            if (!match) return 9999;
            let hours = parseInt(match[1]);
            const minutes = parseInt(match[2]);
            const period = match[3].toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            return hours * 60 + minutes;
        }

        timelineTasks.sort((a, b) => timeToMinutes(a.time_target) - timeToMinutes(b.time_target));

        let html = '<div style="font-family: \\\'VT323\\\', monospace; font-size: 1.1rem; border-left: 2px solid var(--glass-border); padding-left: 1rem; position: relative;">';

        let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');

        if (timelineTasks.length === 0) {
            html += '<div style="color: var(--text-secondary); padding: 1rem;">No tasks locked in for today yet. Use the Planner to schedule your day.</div>';
        } else {
            timelineTasks.forEach(task => {
                const isCompletedToday = lastDoneDates[task.id] && (new Date(lastDoneDates[task.id]).toDateString() === new Date().toDateString());

                let colorBorder = 'var(--glass-border)';
                if (task.priority_color === 'RED') colorBorder = 'var(--accent-red)';
                if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange)';
                if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green)';

                const opacity = isCompletedToday ? '0.5' : '1';
                const decoration = isCompletedToday ? 'line-through' : 'none';
                const checkedState = isCompletedToday ? 'checked' : '';

                html += `
                    <div class="readonly-task" style="position: relative; margin-bottom: 1.5rem; display: flex; gap: 1rem;">
                        <div style="position: absolute; left: -1.45rem; top: 0.25rem; width: 12px; height: 12px; border-radius: 50%; background: ${colorBorder}; box-shadow: 0 0 5px ${colorBorder};"></div>
                        <div style="min-width: 90px; color: var(--accent-magenta); font-weight: bold; margin-top: 0.2rem;">${task.time_target}</div>
                        <div style="flex: 1; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); padding: 0.75rem; border-radius: 4px; border-left: 3px solid ${colorBorder}; opacity: ${opacity};">
                            <div style="display: flex; gap: 0.5rem; align-items: flex-start;">
                                <div class="checkbox completion-toggle readonly-tick" data-id="${task.id}" style="${isCompletedToday ? 'background:var(--accent-green);' : ''}"></div>
                                <div>
                                    <div style="font-weight: bold; text-decoration: ${decoration}; color: var(--text-primary); margin-bottom: 0.25rem;">${escapeHTML(task.title)}</div>
                                    ${task.description ? `<div style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem; text-decoration: ${decoration};">${escapeHTML(task.description)}</div>` : ''}
                                    <div style="display: flex; gap: 4px;">
                                        ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.75rem;">${t}</span>`).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        }

        html += '</div>';
        container.innerHTML = html;

        // Attach listeners for ticks on readonly page
        container.querySelectorAll('.readonly-tick').forEach(tick => {
            tick.addEventListener('click', (e) => {
                e.preventDefault();
                const taskId = tick.getAttribute('data-id');
                const p = tick.parentElement.parentElement;

                let doneDict = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                const isCurrentlyDone = doneDict[taskId] && (new Date(doneDict[taskId]).toDateString() === new Date().toDateString());

                if (isCurrentlyDone) {
                    delete doneDict[taskId];
                    tick.style.background = 'transparent';
                    p.style.opacity = '1';
                    p.querySelector('div[style*="font-weight: bold"]').style.textDecoration = 'none';
                } else {
                    doneDict[taskId] = new Date().toISOString();
                    tick.style.background = 'var(--accent-green)';
                    p.style.opacity = '0.5';
                    p.querySelector('div[style*="font-weight: bold"]').style.textDecoration = 'line-through';
                }
                localStorage.setItem('symphony_last_done', JSON.stringify(doneDict));

                // Refresh both views
                fetchTasksAndRenderTimeline();
            });
        });
    }

    // Call fetchReadonlyToday when "today" tab is active (legacy support - guarded).
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-tab');
            if (targetId === 'today' && document.getElementById('readonly-timeline')) fetchReadonlyToday();
        });
    });

    // Also call on boot if today tab is selected (legacy - guarded)
    if ((localStorage.getItem('symphony_active_tab') === 'today' || !localStorage.getItem('symphony_active_tab')) && document.getElementById('readonly-timeline')) {
        fetchReadonlyToday();
    }

    async function fetchTasksAndRenderTimeline() {
        // Legacy guard: if the old planner DOM no longer exists, do nothing
        if (!document.getElementById('today-timeline') && !document.getElementById('pool-today')) return;
        try {
            // First time UI setup
            setupDragAndDropZones();

            // Fetch ALL active tasks for the universal Task Pool
            const response = await apiFetch(`/tasks`, { headers: { "Authorization": `Bearer ${API_TOKEN}` } });

            if (response.ok) {
                dynamicTasks = await response.json();
                renderDraggableTimeline();
            } else {
                console.error("Failed to fetch tasks list:", response.statusText);
            }
        } catch (error) {
            console.error("Network error fetching tasks:", error);
        }
    }

    function renderDraggableTimeline() {
        // Clear only task cards from drop zones, preserving add-item forms
        document.querySelectorAll('.drop-zone').forEach(zone => {
            zone.querySelectorAll('.draggable-task').forEach(t => t.remove());
        });

        // Categorization helper: determine which pool a task belongs to
        function getPoolId(task) {
            const tt = (task.time_target || '').trim();

            // Legacy fallback: remap "Evening" to a proper time slot
            if (tt === 'Evening') {
                task.time_target = '06:00 PM';
                return 'timeline';
            }

            // If it matches a specific time slot (e.g. "08:00 AM"), it goes on the timeline
            if (/^\d{2}:\d{2}\s*(AM|PM)$/i.test(tt)) return 'timeline';

            // If it matches a time range (e.g. "06:30 AM - 08:30 AM"), it also goes on the timeline
            if (/^\d{2}:\d{2}\s*(AM|PM)\s*-\s*\d{2}:\d{2}\s*(AM|PM)$/i.test(tt)) return 'timeline-span';

            // Daily tasks
            if (tt === 'Daily Flexible') return 'pool-today';

            // This week tasks
            if (tt === 'Weekly' || tt === 'Weekly (3x)' || tt === 'Moveable') return 'pool-week';

            // Long-term
            if (tt === 'Monthly') return 'pool-longterm';

            // Everything else (Unscheduled, empty, null, new quick-add tasks)
            return 'pool-future';
        }

        // Helper: parse "06:30 AM" into minutes since midnight for comparison
        function timeToMinutes(timeStr) {
            const match = timeStr.trim().match(/(\d{2}):(\d{2})\s*(AM|PM)/i);
            if (!match) return -1;
            let hours = parseInt(match[1]);
            const minutes = parseInt(match[2]);
            const period = match[3].toUpperCase();
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            return hours * 60 + minutes;
        }

        // Helper: convert minutes since midnight back to "HH:MM AM/PM" format
        function minutesToTime(totalMins) {
            let h = Math.floor(totalMins / 60);
            const m = totalMins % 60;
            const period = h >= 12 ? 'PM' : 'AM';
            if (h > 12) h -= 12;
            if (h === 0) h = 12;
            return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')} ${period}`;
        }

        // Helper: get the start time and duration of a task from its time_target
        function parseTaskTiming(timeTarget) {
            const tt = (timeTarget || '').trim();
            const rangeMatch = tt.match(/^(\d{2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{2}:\d{2}\s*(?:AM|PM))$/i);
            if (rangeMatch) {
                const startMins = timeToMinutes(rangeMatch[1]);
                const endMins = timeToMinutes(rangeMatch[2]);
                return { startTime: rangeMatch[1].trim(), startMins, endMins, duration: endMins - startMins };
            }
            const singleMatch = tt.match(/^(\d{2}:\d{2}\s*(?:AM|PM))$/i);
            if (singleMatch) {
                const startMins = timeToMinutes(singleMatch[1]);
                return { startTime: singleMatch[1].trim(), startMins, endMins: startMins + 30, duration: 30 };
            }
            return null;
        }

        // Adjust task duration by delta minutes, update local state, persist, and re-render
        async function adjustTaskDuration(taskId, deltaMins) {
            const task = dynamicTasks.find(t => t.id === taskId);
            if (!task) return;
            const timing = parseTaskTiming(task.time_target);
            if (!timing) return;

            let newEndMins = timing.endMins + deltaMins;
            // Minimum duration: 15 minutes
            if (newEndMins - timing.startMins < 15) return;
            // Maximum: don't go past midnight (24:00 = 1440 mins)
            if (newEndMins > 1440) return;

            const newEndTime = minutesToTime(newEndMins);
            if (newEndMins - timing.startMins <= 30) {
                // Single slot — revert to simple format
                task.time_target = timing.startTime;
            } else {
                task.time_target = `${timing.startTime} - ${newEndTime}`;
            }
            renderDraggableTimeline();

            // Persist to Backend
            try {
                await apiFetch(`/tasks/${taskId}`, {
                    method: "PATCH",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ time_target: task.time_target })
                });
            } catch (e) {
                console.warn('Failed to persist duration change:', e);
            }
        }

        // Track counts per section for badge display
        const counts = { 'pool-today': 0, 'pool-week': 0, 'pool-longterm': 0, 'pool-future': 0 };

        dynamicTasks.forEach(task => {
            // Create the draggable card
            const el = document.createElement('div');
            el.className = 'draggable-task';
            el.draggable = true;
            el.dataset.id = task.id;

            // Visual indicator for priority color
            let colorBorder = 'var(--glass-border)';
            if (task.priority_color === 'RED') colorBorder = 'var(--accent-red)';
            if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange)';
            if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green)';

            el.style.borderLeft = `3px solid ${colorBorder}`;

            const poolId = getPoolId(task);
            const isOnTimeline = (poolId === 'timeline' || poolId === 'timeline-span');
            const timing = isOnTimeline ? parseTaskTiming(task.time_target) : null;
            const durationLabel = timing ? `${timing.duration}m` : '';

            el.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="display: flex; align-items: flex-start; gap: 8px;">
                        ${isOnTimeline ? `<div class="checkbox completion-toggle" style="margin-top: 2px;" title="Mark Complete"></div>` : ''}
                         <div class="task-title" style="font-size: 0.95rem; font-weight: bold; transition: all 0.2s;">
                            ${escapeHTML(task.title)}
                        </div>
                    </div>
                    <button class="task-delete-btn" data-task-id="${task.id}" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: red; font-weight: bold; font-size: 0.9rem; cursor: pointer; padding: 0 5px; line-height: 1.2;" title="Delete task">×</button>
                </div>
                ${task.description ? `<div class="task-desc" style="font-size: 0.8rem;">${escapeHTML(task.description)}</div>` : ''}
                <div style="margin-top: 4px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        ${(task.tags || []).map(t => `<span class="tag" style="font-size: 0.65rem; padding: 2px 6px;">${t}</span>`).join('')}
                    </div>
                    ${isOnTimeline ? `
                    <div class="duration-controls" style="display: flex; align-items: center; gap: 4px; font-size: 0.75rem;">
                        <button class="dur-minus" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: #000000; width: 24px; height: 24px; border-radius: 0; cursor: pointer; font-weight: bold; font-size: 1rem; line-height: 1; font-family: 'VT323', monospace;">−</button>
                        <span class="dur-label" style="color: #0000ff; font-weight: 600; min-width: 32px; text-align: center; font-family: 'VT323', monospace;">${durationLabel}</span>
                        <button class="dur-plus" style="background: #c0c0c0; border: 2px outset var(--win-highlight); color: #000000; width: 24px; height: 24px; border-radius: 0; cursor: pointer; font-weight: bold; font-size: 1rem; line-height: 1; font-family: 'VT323', monospace;">+</button>
                    </div>` : ''}
                </div>
            `;

            // Attach duration control listeners
            const durMinus = el.querySelector('.dur-minus');
            const durPlus = el.querySelector('.dur-plus');
            if (durMinus) durMinus.addEventListener('click', (e) => { e.stopPropagation(); adjustTaskDuration(task.id, -15); });
            if (durPlus) durPlus.addEventListener('click', (e) => { e.stopPropagation(); adjustTaskDuration(task.id, 15); });

            // Attach completion toggle
            const completeBtn = el.querySelector('.completion-toggle');
            if (completeBtn) {
                // Determine initial state
                let lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                const lastDoneIso = lastDoneDates[task.id];
                const isCompletedToday = lastDoneIso && (new Date(lastDoneIso).toDateString() === new Date().toDateString());

                if (isCompletedToday) {
                    completeBtn.classList.add('checked');
                    el.querySelector('.task-title').style.opacity = '0.5';
                    el.querySelector('.task-title').style.textDecoration = 'line-through';
                }

                completeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    completeBtn.classList.toggle('checked');
                    const isChecked = completeBtn.classList.contains('checked');

                    const titleEl = el.querySelector('.task-title');
                    if (isChecked) {
                        titleEl.style.opacity = '0.5';
                        titleEl.style.textDecoration = 'line-through';
                        // Save last done date
                        lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        lastDoneDates[task.id] = new Date().toISOString();
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        // Re-render trackers
                        renderWeeklyMonthlyTracker();
                    } else {
                        titleEl.style.opacity = '1';
                        titleEl.style.textDecoration = 'none';
                        // Remove last done date if un-toggled (optional, but good for correcting mistakes)
                        lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');
                        delete lastDoneDates[task.id];
                        localStorage.setItem('symphony_last_done', JSON.stringify(lastDoneDates));
                        renderWeeklyMonthlyTracker();
                    }
                });
            }

            // Attach delete handler
            const deleteBtn = el.querySelector('.task-delete-btn');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (!confirm(`Delete "${escapeHTML(task.title)}"?`)) return;
                    deleteBtn.innerText = "⏳";
                    try {
                        const response = await apiFetch(`/tasks/${task.id}`, {
                            method: "DELETE",
                            headers: { "Authorization": `Bearer ${API_TOKEN}` }
                        });

                        if (response.ok || response.status === 204) {
                            dynamicTasks = dynamicTasks.filter(t => t.id !== task.id);
                            renderDraggableTimeline();
                        } else {
                            console.error("Failed to delete task", response.statusText);
                            alert("Failed to delete task");
                            deleteBtn.innerText = "×";
                        }
                    } catch (err) {
                        console.error("Network error deleting task:", err);
                        alert("Network error. Try again.");
                        deleteBtn.innerText = "×";
                    }
                });
            }

            // Attach drag events
            el.addEventListener('dragstart', (e) => {
                el.classList.add('dragging');
                draggedTaskObj = task;
                e.dataTransfer.setData('text/plain', task.id);
            });

            el.addEventListener('dragend', () => {
                el.classList.remove('dragging');
                draggedTaskObj = null;
            });


            // Route to the correct container (using poolId cached above)

            if (poolId === 'timeline') {
                const targetZone = document.querySelector(`.drop-zone[data-time="${task.time_target}"]`);
                if (targetZone) {
                    targetZone.appendChild(el);
                } else {
                    // Fallback: time slot doesn't exist on the timeline, put in Today
                    const fallback = document.getElementById('pool-today');
                    if (fallback) fallback.appendChild(el);
                    counts['pool-today']++;
                }
            } else if (poolId === 'timeline-span') {
                // Multi-hour task: parse start and end, span across slots
                const parts = task.time_target.split('-').map(s => s.trim());
                const startTime = parts[0];
                const endTime = parts[1];
                const startMinutes = timeToMinutes(startTime);
                const endMinutes = timeToMinutes(endTime);

                const startSlot = document.querySelector(`.time-slot[data-time="${startTime}"]`);
                const timelineContainer = document.getElementById('today-timeline');
                if (startSlot && timelineContainer) {
                    const allSlots = Array.from(document.querySelectorAll('.time-slot'));
                    const startIdx = allSlots.findIndex(s => s.dataset.time === startTime);
                    let endIdx = allSlots.findIndex(s => timeToMinutes(s.dataset.time) >= endMinutes);
                    if (endIdx === -1) endIdx = allSlots.length;

                    for (let i = startIdx; i < endIdx && i < allSlots.length; i++) {
                        const zone = allSlots[i].querySelector('.drop-zone');
                        if (zone) {
                            zone.style.background = 'rgba(56, 189, 248, 0.05)';
                            zone.style.borderColor = 'rgba(56, 189, 248, 0.2)';
                        }
                    }

                    timelineContainer.style.position = 'relative';

                    const rangeBadge = document.createElement('div');
                    rangeBadge.style.cssText = 'font-size: 0.7rem; color: var(--accent-blue); margin-top: 4px;';
                    rangeBadge.textContent = startTime + ' \u2192 ' + endTime;
                    el.appendChild(rangeBadge);

                    timelineContainer.appendChild(el);

                    requestAnimationFrame(() => {
                        const timelineRect = timelineContainer.getBoundingClientRect();
                        const startRect = startSlot.getBoundingClientRect();
                        const lastSlotIdx = Math.min(endIdx - 1, allSlots.length - 1);
                        const endSlotRect = allSlots[lastSlotIdx].getBoundingClientRect();
                        const topOffset = startRect.top - timelineRect.top;
                        const spanHeight = endSlotRect.bottom - startRect.top;
                        el.style.position = 'absolute';
                        el.style.top = topOffset + 'px';
                        el.style.left = '85px';
                        el.style.right = '0';
                        el.style.height = spanHeight + 'px';
                        el.style.zIndex = '5';
                        el.style.background = 'rgba(56, 189, 248, 0.12)';
                        el.style.border = '2px solid rgba(56, 189, 248, 0.4)';
                        el.style.borderRadius = '6px';
                        el.style.padding = '0.5rem';
                        el.style.boxSizing = 'border-box';
                        el.style.backdropFilter = 'blur(4px)';
                    });
                } else {
                    const fallback = document.getElementById('pool-today');
                    if (fallback) fallback.appendChild(el);
                    counts['pool-today']++;
                }
            } else {
                const container = document.getElementById(poolId);
                if (container) container.appendChild(el);
                if (counts[poolId] !== undefined) counts[poolId]++;
            }
        });

        // Update section headers with task counts
        document.querySelectorAll('.pool-accordion-header').forEach(header => {
            const poolId = header.getAttribute('data-pool');
            const count = counts[poolId];
            if (count !== undefined) {
                const label = header.querySelector('span:first-child');
                // Add count badge
                const existingBadge = header.querySelector('.pool-count');
                if (existingBadge) existingBadge.remove();
                const badge = document.createElement('span');
                badge.className = 'pool-count';
                badge.textContent = ` (${count})`;
                label.appendChild(badge);
            }
        });

        // Progress update
        document.getElementById('today-progress').style.width = '0%';

        // Highlight current time slot and auto-scroll to it
        const now = new Date();
        const nowMins = now.getHours() * 60 + now.getMinutes();
        const allTimeSlots = document.querySelectorAll('.time-slot[data-time]');
        let closestSlot = null;
        allTimeSlots.forEach(slot => {
            slot.classList.remove('current-time');
            const slotTime = slot.dataset.time;
            const slotMins = timeToMinutes(slotTime);
            if (slotMins >= 0 && slotMins <= nowMins) {
                closestSlot = slot;
            }
        });
        if (closestSlot) {
            closestSlot.classList.add('current-time');
            // Auto-scroll to current time (only on initial load)
            if (!window._timelineScrolled) {
                window._timelineScrolled = true;
                setTimeout(() => closestSlot.scrollIntoView({ behavior: 'smooth', block: 'center' }), 300);
            }
        }

        // Render Weekly/Monthly Tracker immediately after timeline is built
        renderWeeklyMonthlyTracker();

        // Setup drag-and-drop after rendering
        setupDragAndDropZones();
    }

    function setupDragAndDropZones() {
        const dropZones = document.querySelectorAll('.drop-zone');

        dropZones.forEach(zone => {
            // Skip zones that already have drag handlers (prevents stacking)
            if (zone.dataset.dragReady) return;
            zone.dataset.dragReady = 'true';

            zone.addEventListener('dragover', e => {
                e.preventDefault();
                zone.classList.add('drag-over');
            });

            zone.addEventListener('dragleave', () => {
                zone.classList.remove('drag-over');
            });

            zone.addEventListener('drop', e => {
                e.preventDefault();
                zone.classList.remove('drag-over');

                const draggingEl = document.querySelector('.dragging');
                if (draggingEl && draggedTaskObj) {
                    draggedTaskObj.time_target = zone.dataset.time;
                    // Defer re-render to avoid conflicts during drag event
                    setTimeout(() => renderDraggableTimeline(), 0);
                }
            });
        });

        // Setup the "Lock In Schedule" Button
        const lockBtn = document.getElementById('lock-in-btn');
        if (lockBtn) {
            // Remove old listeners by cloning
            const newBtn = lockBtn.cloneNode(true);
            lockBtn.parentNode.replaceChild(newBtn, lockBtn);
            newBtn.addEventListener('click', lockInSchedule);
        }
    }

    async function lockInSchedule() {
        const lockBtn = document.getElementById('lock-in-btn');
        const originalText = lockBtn.innerText;
        lockBtn.innerText = '\u23f3 Syncing...';
        lockBtn.style.opacity = '0.7';
        lockBtn.style.pointerEvents = 'none';

        try {
            const updates = dynamicTasks.map(t => ({
                id: t.id,
                time_target: t.time_target
            }));

            const patchPromises = updates.map(update => {
                return apiFetch(`/tasks/${update.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ time_target: update.time_target })
                });
            });

            const responses = await Promise.all(patchPromises);
            const allOk = responses.every(r => r.ok);

            if (allOk) {
                lockBtn.innerText = '\u2705 Locked In';
                lockBtn.style.background = 'var(--glass-bg)';
                lockBtn.style.color = 'var(--accent-green)';
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
                // Switch to Today's Schedule and refresh the readonly view
                setTimeout(() => {
                    activateTab('today');
                    localStorage.setItem('symphony_active_tab', 'today');
                    fetchReadonlyToday();
                    lockBtn.innerText = originalText;
                    lockBtn.style.background = 'var(--accent-green)';
                    lockBtn.style.color = '#000';
                    lockBtn.style.opacity = '1';
                    lockBtn.style.pointerEvents = 'auto';
                }, 1500);
            } else {
                console.error('Failed to commit schedule bulk update');
                lockBtn.innerText = '\u274c Sync Failed';
                if (typeof playRetroError === 'function') playRetroError();
            }
        } catch (error) {
            console.error('Network error locking in schedule:', error);
            lockBtn.innerText = '\u274c Network Error';
            if (typeof playRetroError === 'function') playRetroError();
        }
    }

    function renderWeeklyMonthlyTracker() {
        const weeklyList = document.getElementById('weekly-list');
        const monthlyList = document.getElementById('monthly-list');
        if (!weeklyList || !monthlyList) return;

        weeklyList.innerHTML = '';
        monthlyList.innerHTML = '';

        const lastDoneDates = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');

        // Helper to format dates cleanly
        const formatDate = (isoStr) => {
            if (!isoStr) return 'Never';
            const d = new Date(isoStr);
            return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }); // e.g., 25 Mar
        };

        // Filter for tracking tasks
        const trackingTasks = dynamicTasks.filter(t => {
            const tt = (t.time_target || '').trim();
            return ['Weekly', 'Weekly (3x)', 'Monthly'].includes(tt);
        });

        trackingTasks.forEach(task => {
            const tt = (task.time_target || '').trim();
            const lastDone = formatDate(lastDoneDates[task.id]);

            const li = document.createElement('li');
            li.style.display = 'flex';
            li.style.justifyContent = 'space-between';
            li.style.alignItems = 'center';
            li.innerHTML = `
                <div class="task-content">
                    <strong>${escapeHTML(task.title)}</strong>
                    ${task.tags ? `<br><span class="tag" style="font-size:0.65rem;">${task.tags.join(', ')}</span>` : ''}
                </div>
                <div style="background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; border: 1px solid var(--glass-border);">
                    <span style="color: var(--text-secondary);">Last Done:</span> <span style="font-weight:bold; color: var(--accent-green);">${lastDone}</span>
                </div>
            `;

            if (tt === 'Monthly') {
                monthlyList.appendChild(li);
            } else {
                weeklyList.appendChild(li);
            }
        });

        // If nothing was found, put a placeholder
        if (weeklyList.innerHTML === '') weeklyList.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No weekly tasks found.</li>';
        if (monthlyList.innerHTML === '') monthlyList.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No monthly tasks found.</li>';
    }

    // --- Accordion Toggle Logic ---
    document.querySelectorAll('.pool-accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const poolId = header.getAttribute('data-pool');
            const body = document.getElementById(poolId);
            if (!body) return; // guard: element may not exist in this view
            const toggle = header.querySelector('.pool-toggle');

            if (body.style.display === 'none') {
                body.style.display = 'block';
                header.classList.add('expanded');
                if (toggle) toggle.textContent = '▼';
            } else {
                body.style.display = 'none';
                header.classList.remove('expanded');
                if (toggle) toggle.textContent = '►';
            }
        });
    });


    // Populate Lists
    const createListItems = (items, containerId) => {
        const container = document.getElementById(containerId);
        if (!container) return; // Guard: container may not exist in HTML
        container.innerHTML = '';

        // Determine storage key (inject date if it's a supplement list)
        let storageKey = 'symphony_list_state_' + containerId;
        const isSuppList = containerId.startsWith('supp-');
        if (isSuppList) {
            storageKey = `symphony_list_state_${getLocalDateString(window.bioTrackingDate)}_${containerId}`;

            // Migration logic: If today, move old legacy data to the new dated structure to prevent data loss
            const legacyKey = 'symphony_list_state_' + containerId;
            const legacyData = localStorage.getItem(legacyKey);
            if (legacyData && getLocalDateString(window.bioTrackingDate) === getLocalDateString(new Date())) {
                localStorage.setItem(storageKey, legacyData);
                localStorage.removeItem(legacyKey);
                console.log(`Migrated legacy supp data to ${storageKey}`);
            }
        }

        // Load list state
        const savedListState = JSON.parse(localStorage.getItem(storageKey) || '{}');

        items.forEach((itemObj, index) => {
            // Handle both simple strings and objects with points/sync data
            const text = typeof itemObj === 'string' ? itemObj : itemObj.text;


            const suppSyncAttr = (typeof itemObj === 'object' && itemObj.suppSync) ? `data-supp-sync="${itemObj.suppSync}" data-supp-dose="${itemObj.suppDose || 1}"` : '';

            const li = document.createElement('li');
            const isCompleted = savedListState[index];

            if (isCompleted) {
                li.classList.add('completed');
            }

            li.innerHTML = `
                <div class="checkbox ${isCompleted ? 'checked' : ''}" ${suppSyncAttr}></div>
                <div class="task-content">${text}</div>
            `;

            li.querySelector('.checkbox').addEventListener('click', function () {
                const wasChecked = this.classList.contains('checked');
                this.classList.toggle('checked');
                const isNowChecked = this.classList.contains('checked');

                const parent = this.parentElement;
                parent.classList.toggle('completed');

                // Save state
                savedListState[index] = isNowChecked;
                localStorage.setItem(storageKey, JSON.stringify(savedListState));


                // Trigger Supplement Sync if newly checked
                // History note: This deliberately triggers even for past days, enabling retro-logging
                if (!wasChecked && isNowChecked && window.triggerSuppSync) {
                    const syncName = this.getAttribute('data-supp-sync');
                    const syncDose = parseInt(this.getAttribute('data-supp-dose')) || 1;
                    if (syncName) {
                        window.triggerSuppSync(syncName, syncDose);
                    }
                }

                // Refresh Pulse UI if applicable
                if (typeof window.refreshPulse === 'function') {
                    window.refreshPulse();
                }
            });

            container.appendChild(li);
        });
    };

    // --- Ideas / Bucket List Setup (Supabase-backed) ---
    async function initIdeasPage() {
        const attachListListener = (inputId, btnId, listId, listType) => {
            const input = document.getElementById(inputId);
            const btn = document.getElementById(btnId);
            const list = document.getElementById(listId);
            const LOCAL_KEY = `symphony_ideas_${listType}`;

            if (!input || !btn || !list) return;

            let items = []; // [{id, text, completed, sort_order}]

            // Fetch from local backend, fallback to localStorage
            async function fetchItems() {
                try {
                    const resp = await apiFetch(`/ideas?list_type=${listType}`, {
                        headers: {
                            'Authorization': `Bearer ${API_TOKEN}`
                        }
                    });
                    if (resp.ok) {
                        const serverData = await resp.json();
                        if (serverData.length > 0) {
                            items = serverData;
                            localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        } else {
                            const localData = localStorage.getItem(LOCAL_KEY);
                            const localItems = localData ? JSON.parse(localData) : [];
                            if (localItems.length > 0) {
                                items = localItems;
                                console.info(`Ideas (${listType}): Server empty, keeping local data`);
                            } else {
                                items = [];
                            }
                        }
                    } else {
                        throw new Error(`HTTP ${resp.status}`);
                    }
                } catch (e) {
                    console.warn(`Ideas (${listType}): Server fetch failed, using localStorage:`, e);
                    const local = localStorage.getItem(LOCAL_KEY);
                    if (local) items = JSON.parse(local);
                }
            }

            function renderItems() {
                list.innerHTML = '';
                if (items.length === 0) {
                    list.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No items yet — add one above!</li>';
                    return;
                }
                items.forEach((item, index) => {
                    const li = document.createElement('li');
                    if (item.completed) li.classList.add('completed');

                    li.innerHTML = `
                        <div class="checkbox ${item.completed ? 'checked' : ''}"></div>
                        <div class="task-content" style="flex-grow: 1;">${item.text}</div>
                        <button class="delete-btn" data-index="${index}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.2rem; margin-left: 10px;" title="Delete item">×</button>
                    `;

                    li.querySelector('.checkbox').addEventListener('click', async function () {
                        this.classList.toggle('checked');
                        this.parentElement.classList.toggle('completed');
                        items[index].completed = !items[index].completed;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        // Sync to backend
                        if (items[index].id) {
                            try {
                                await apiFetch(`/ideas/${items[index].id}`, {
                                    method: 'PATCH',
                                    headers: {
                                        'Authorization': `Bearer ${API_TOKEN}`,
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ completed: items[index].completed })
                                });
                            } catch (e) { console.warn('Failed to sync checkbox:', e); }
                        }
                    });

                    li.querySelector('.delete-btn').addEventListener('click', async function () {
                        const removedItem = items.splice(index, 1)[0];
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                        renderItems();
                        // Delete from backend
                        if (removedItem && removedItem.id) {
                            try {
                                await apiFetch(`/ideas/${removedItem.id}`, {
                                    method: 'DELETE',
                                    headers: {
                                        'Authorization': `Bearer ${API_TOKEN}`
                                    }
                                });
                            } catch (e) { console.warn('Failed to delete idea:', e); }
                        }
                    });

                    list.appendChild(li);
                });
            }

            async function handleAdd() {
                const text = input.value.trim();
                if (!text) return;

                const newItem = {
                    list_type: listType,
                    text: text,
                    completed: false,
                    sort_order: items.length
                };

                // Optimistic local add
                items.push(newItem);
                localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                renderItems();
                input.value = '';

                // Persist to backend
                try {
                    const resp = await apiFetch(`/ideas`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${API_TOKEN}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(newItem)
                    });
                    if (resp.ok) {
                        // Re-fetch to get the real ID from backend
                        await fetchItems();
                        renderItems();
                    }
                } catch (e) {
                    console.warn('Failed to save idea:', e);
                }

                if (typeof playRetroClick === 'function') playRetroClick();
            }

            btn.addEventListener('click', handleAdd);
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') handleAdd();
            });

            // Initialize: fetch and render
            return fetchItems().then(() => {
                // Seed bucket list default if completely empty (first use)
                if (items.length === 0 && listType === 'bucket') {
                    items = [{ text: "Walk the full Pineapple Track", completed: false, sort_order: 0 }];
                }
                renderItems();
            });
        };

        await Promise.all([
            attachListListener('quick-add-bucket', 'quick-add-bucket-btn', 'bucket-list', 'bucket'),
            attachListListener('quick-add-braindump', 'quick-add-braindump-btn', 'braindump-list', 'braindump')
        ]);
    }

    initIdeasPage();

    // Populate Workout Grid
    const populateWorkout = () => {
        const grid = document.getElementById('workout-grid');
        grid.innerHTML = '';

        workoutPlan.forEach(workout => {
            const card = document.createElement('div');
            card.className = 'sub-panel workout-card';

            let exercisesHtml = workout.exercises.map(ex => `<li>${ex}</li>`).join('');

            card.innerHTML = `
                <h3>${workout.day}</h3>
                <div class="workout-focus">${workout.focus}</div>
                <ul class="workout-list">
                    ${exercisesHtml}
                </ul>
            `;
            grid.appendChild(card);
        });
    };

    // ── Local Time Helper ──
    function getLocalDayDateString(d = new Date()) {
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    const FOOD_LOG_KEY = `symphony_food_log_${getLocalDayDateString()}`;
    const FOOD_RECIPES_KEY = 'symphony_food_recipes';
    const FOOD_HISTORY_KEY = 'symphony_food_history'; // localStorage backup for chart data
    const MY_FOODS_KEY = 'symphony_my_foods'; // persistent food history + favorites

    // ── DNA-Personalized Targets ──
    // Based on: TCF7L2 C/T, KLF14 A/A, 9p21 G/G, ACTN3 C/T, ADRB2 G/G, CRP=9
    const DNA_TARGETS = {
        calories: { min: 1800, max: 2400, label: 'Calories (KLF14 tight margin)' },
        protein: { min: 120, max: 999, label: 'Protein (ACTN3 hybrid muscle)' },
        carbs: { min: 0, max: 150, label: 'Carbs (TCF7L2 pancreas limit)' },
        fats: { min: 0, max: 80, label: 'Fats (9p21 artery risk)' },
        fiber: { min: 25, max: 999, label: 'Fiber (Gut barrier / CRP=9)' },
        sugars: { min: 0, max: 30, label: 'Sugars (TCF7L2 + KLF14)' },
        sodium: { min: 0, max: 2.3, label: 'Sodium (< 2300mg)' }
    };

    // ── LocalStorage helpers ──
    function getDailyFoodLog() {
        const stored = localStorage.getItem(FOOD_LOG_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveFoodLog(logArr) {
        localStorage.setItem(FOOD_LOG_KEY, JSON.stringify(logArr));
    }
    function getRecipes() {
        const stored = localStorage.getItem(FOOD_RECIPES_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveRecipes(arr) {
        localStorage.setItem(FOOD_RECIPES_KEY, JSON.stringify(arr));
    }
    function getFoodHistory() {
        const stored = localStorage.getItem(FOOD_HISTORY_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveFoodHistory(arr) {
        localStorage.setItem(FOOD_HISTORY_KEY, JSON.stringify(arr));
    }
    function getMyFoods() {
        const stored = localStorage.getItem(MY_FOODS_KEY);
        return stored ? JSON.parse(stored) : [];
    }
    function saveMyFoods(arr) {
        localStorage.setItem(MY_FOODS_KEY, JSON.stringify(arr));
    }
    function addToMyFoods(food) {
        // food = selectedFood shape: { name, brand, per100g, servingSize, servingG, qtyLabel, qtyG }
        if (!food || !food.name) return;
        const myFoods = getMyFoods();
        const existing = myFoods.find(f => f.name === food.name && (f.brand || '') === (food.brand || ''));
        if (existing) {
            existing.useCount = (existing.useCount || 1) + 1;
            existing.lastUsed = new Date().toISOString();
        } else {
            myFoods.push({
                name: food.name,
                brand: food.brand || '',
                per100g: food.per100g,
                servingSize: food.servingSize,
                servingG: food.servingG,
                qtyLabel: food.qtyLabel || null,
                qtyG: food.qtyG || null,
                favorite: false,
                lastUsed: new Date().toISOString(),
                useCount: 1
            });
        }
        saveMyFoods(myFoods);
    }
    function toggleMyFoodFavorite(name, brand) {
        const myFoods = getMyFoods();
        const item = myFoods.find(f => f.name === name && (f.brand || '') === (brand || ''));
        if (item) {
            item.favorite = !item.favorite;
            saveMyFoods(myFoods);
        }
    }

    // ── Nutrient scaling ──
    function scaleNutrients(per100g, amountG) {
        const factor = amountG / 100;
        return {
            calories: Math.round((per100g.calories || 0) * factor),
            protein: Math.round((per100g.protein || 0) * factor * 10) / 10,
            carbs: Math.round((per100g.carbs || 0) * factor * 10) / 10,
            fats: Math.round((per100g.fats || 0) * factor * 10) / 10,
            sugars: Math.round((per100g.sugars || 0) * factor * 10) / 10,
            fiber: Math.round((per100g.fiber || 0) * factor * 10) / 10,
            sodium: Math.round((per100g.sodium || 0) * factor * 100) / 100
        };
    }

    function calculateDailyTotals(logArr) {
        return logArr.reduce((totals, item) => {
            totals.calories += item.calories || 0;
            totals.protein += item.protein || 0;
            totals.carbs += item.carbs || 0;
            totals.fats += item.fats || 0;
            totals.sugars += item.sugars || 0;
            totals.fiber += item.fiber || 0;
            totals.sodium += item.sodium || 0;
            return totals;
        }, { calories: 0, protein: 0, carbs: 0, fats: 0, sugars: 0, fiber: 0, sodium: 0 });
    }

    // ── DNA Grading Engine ──
    function gradeDailyIntake(totals) {
        let score = 100;
        const breakdown = [];

        const checks = [
            { key: 'calories', value: Math.round(totals.calories), unit: '' },
            { key: 'protein', value: Math.round(totals.protein * 10) / 10, unit: 'g' },
            { key: 'carbs', value: Math.round(totals.carbs * 10) / 10, unit: 'g' },
            { key: 'fats', value: Math.round(totals.fats * 10) / 10, unit: 'g' },
            { key: 'fiber', value: Math.round(totals.fiber * 10) / 10, unit: 'g' },
            { key: 'sugars', value: Math.round(totals.sugars * 10) / 10, unit: 'g' },
            { key: 'sodium', value: Math.round(totals.sodium * 100) / 100, unit: 'g' }
        ];

        checks.forEach(c => {
            const t = DNA_TARGETS[c.key];
            let status = 'pass';
            let penalty = 0;

            if (c.value < t.min) {
                const deficit = ((t.min - c.value) / t.min) * 100;
                penalty = Math.min(20, Math.round(deficit / 5) * 3);
                status = penalty > 10 ? 'fail' : 'warn';
            } else if (c.value > t.max) {
                const excess = ((c.value - t.max) / t.max) * 100;
                penalty = Math.min(25, Math.round(excess / 5) * 3);
                status = penalty > 10 ? 'fail' : 'warn';
            }

            score -= penalty;
            breakdown.push({
                label: t.label,
                value: `${c.value}${c.unit}`,
                target: c.key === 'protein' || c.key === 'fiber'
                    ? `≥ ${t.min}${c.unit}`
                    : c.key === 'calories'
                        ? `${t.min}-${t.max}`
                        : `≤ ${t.max}${c.unit}`,
                status,
                penalty
            });
        });

        score = Math.max(0, Math.min(100, score));

        let grade;
        if (score >= 95) grade = 'A+';
        else if (score >= 88) grade = 'A';
        else if (score >= 80) grade = 'B+';
        else if (score >= 72) grade = 'B';
        else if (score >= 64) grade = 'C+';
        else if (score >= 55) grade = 'C';
        else if (score >= 45) grade = 'D';
        else grade = 'F';

        return { grade, score, breakdown };
    }

    function gradeToNumber(grade) {
        const map = { 'A+': 5, 'A': 4.5, 'B+': 4, 'B': 3.5, 'C+': 3, 'C': 2.5, 'D': 1.5, 'F': 0.5 };
        return map[grade] || 0;
    }

    function getGradeColor(grade) {
        if (grade.startsWith('A')) return '#22c55e';
        if (grade.startsWith('B')) return '#38bdf8';
        if (grade.startsWith('C')) return '#fbbf24';
        if (grade === 'D') return '#f97316';
        return '#ef4444';
    }

    // ── Render Functions ──
    function renderFoodDashboard() {
        const log = getDailyFoodLog();
        const totals = calculateDailyTotals(log);

        // Dashboard tiles
        document.getElementById('food-dash-calories').innerText = Math.round(totals.calories);
        document.getElementById('food-dash-protein').innerText = `${Math.round(totals.protein)}g`;
        document.getElementById('food-dash-carbs').innerText = `${Math.round(totals.carbs)}g`;
        document.getElementById('food-dash-fats').innerText = `${Math.round(totals.fats)}g`;

        // Live DNA grade
        if (log.length > 0) {
            const result = gradeDailyIntake(totals);
            const badge = document.getElementById('food-grade-badge');
            const scoreEl = document.getElementById('food-grade-score');
            badge.innerText = result.grade;
            badge.style.color = getGradeColor(result.grade);
            badge.style.textShadow = `0 0 12px ${getGradeColor(result.grade)}50`;
            scoreEl.innerText = `${result.score}/100 points`;

            // Grade breakdown
            const breakdownEl = document.getElementById('food-grade-breakdown');
            if (breakdownEl) {
                breakdownEl.innerHTML = result.breakdown.map(b => {
                    const icon = b.status === 'pass' ? '✅' : b.status === 'warn' ? '⚠️' : '❌';
                    const color = b.status === 'pass' ? 'var(--accent-green)' : b.status === 'warn' ? 'var(--accent-yellow)' : 'var(--accent-red)';
                    return `<div style="display: flex; justify-content: space-between; padding: 0.25rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05);">
                        <span>${icon} ${b.label}</span>
                        <span style="color: ${color}; font-weight: 600;">${b.value} <span style="font-weight: 400; color: var(--text-secondary);">(${b.target})</span></span>
                    </div>`;
                }).join('');
            }
        }

        // Doughnut chart
        const canvas = document.getElementById('foodMacroChart');
        if (canvas && typeof Chart !== 'undefined' && totals.protein + totals.carbs + totals.fats > 0) {
            try {
                const ctx = canvas.getContext('2d');
                if (window.foodChartInstance) window.foodChartInstance.destroy();
                window.foodChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Protein', 'Carbs', 'Fats'],
                        datasets: [{
                            data: [Math.round(totals.protein), Math.round(totals.carbs), Math.round(totals.fats)],
                            backgroundColor: ['rgba(56,189,248,0.8)', 'rgba(251,191,36,0.8)', 'rgba(239,68,68,0.8)'],
                            borderColor: 'rgba(15,23,42,1)',
                            borderWidth: 2,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true, maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        cutout: '65%'
                    }
                });
            } catch (e) { console.warn('Food chart unavailable:', e.message); }
        }

        // Food log list
        const listEl = document.getElementById('food-log-list');
        if (listEl) {
            listEl.innerHTML = '';
            if (log.length === 0) {
                listEl.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">No food logged yet today</li>';
            }
            log.forEach((item, index) => {
                const li = document.createElement('li');
                li.style.flexDirection = 'column';
                li.style.alignItems = 'flex-start';
                li.innerHTML = `
                    <div style="display: flex; justify-content: space-between; width: 100%; cursor: pointer;" onclick="document.getElementById('food-details-${index}').style.display = document.getElementById('food-details-${index}').style.display === 'none' ? 'block' : 'none'">
                        <div>
                            <span style="font-size: 0.75rem; color: var(--text-secondary); margin-right: 0.5rem;">${item.timestamp}</span>
                            <strong style="color: var(--text-primary);">${item.name}</strong>
                            <span style="font-size: 0.7rem; color: var(--accent-blue);">${item.amount}${item.unit || 'g'}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);">
                            ${item.calories} kcal | ${Math.round(item.protein)}P ${Math.round(item.carbs)}C ${Math.round(item.fats)}F
                        </div>
                    </div>
                    <div id="food-details-${index}" style="display: none; width: 100%; margin-top: 0.4rem; padding-top: 0.4rem; border-top: 1px dashed var(--glass-border); font-size: 0.75rem; color: var(--text-secondary);">
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.3rem;">
                            <span>Sugars: ${Math.round(item.sugars * 10) / 10}g</span>
                            <span>Fiber: ${Math.round(item.fiber * 10) / 10}g</span>
                            <span>Sodium: ${Math.round(item.sodium * 1000)}mg</span>
                        </div>
                        <button class="delete-food-btn" data-index="${index}" style="margin-top: 0.4rem; background: transparent; border: 1px solid var(--accent-red); color: var(--accent-red); padding: 2px 8px; border-radius: 4px; cursor: pointer; font-family: 'VT323', monospace;">Remove</button>
                    </div>
                `;
                listEl.appendChild(li);
            });

            document.querySelectorAll('.delete-food-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const idx = parseInt(e.target.getAttribute('data-index'));
                    let currentLog = getDailyFoodLog();
                    currentLog.splice(idx, 1);
                    saveFoodLog(currentLog);
                    renderFoodDashboard();
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });
        }
    }

    // ── Recipes rendering ──
    function renderRecipes() {
        const recipes = getRecipes();
        const list = document.getElementById('food-recipes-list');
        if (!list) return;
        list.innerHTML = '';
        if (recipes.length === 0) {
            list.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem; padding: 0.25rem 0;">No recipes saved yet</div>';
            return;
        }
        recipes.forEach((recipe, idx) => {
            const totals = calculateDailyTotals(recipe.items);
            const div = document.createElement('div');
            div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.8rem;';
            div.innerHTML = `
                <div>
                    <strong style="color: var(--text-primary);">${recipe.name}</strong>
                    <span style="color: var(--text-secondary);"> (${recipe.items.length} items, ${Math.round(totals.calories)} kcal)</span>
                </div>
                <div style="display: flex; gap: 0.3rem;">
                    <button class="log-recipe-btn" data-idx="${idx}" style="padding: 2px 6px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: var(--accent-green); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">Log</button>
                    <button class="delete-recipe-btn" data-idx="${idx}" style="padding: 2px 6px; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); color: var(--accent-red); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">×</button>
                </div>
            `;
            list.appendChild(div);
        });

        // Log recipe handlers
        document.querySelectorAll('.log-recipe-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                const recipe = recipes[idx];
                const currentLog = getDailyFoodLog();
                recipe.items.forEach(item => {
                    currentLog.push({
                        ...item,
                        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                        fromRecipe: recipe.name
                    });
                });
                saveFoodLog(currentLog);
                renderFoodDashboard();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        });

        // Delete recipe handlers
        document.querySelectorAll('.delete-recipe-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = parseInt(btn.getAttribute('data-idx'));
                const allRecipes = getRecipes();
                allRecipes.splice(idx, 1);
                saveRecipes(allRecipes);
                renderRecipes();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        });
    }

    // ── Historical Charts ──
    function renderGradeChart(days = 14) {
        const history = getFoodHistory();
        const canvas = document.getElementById('gradeHistoryChart');
        if (!canvas || typeof Chart === 'undefined') return;
        const ctx = canvas.getContext('2d');

        // Get last N days
        const cutoff = new Date();
        cutoff.setDate(cutoff.getDate() - days);
        const filtered = history.filter(h => new Date(h.date) >= cutoff).sort((a, b) => new Date(a.date) - new Date(b.date));

        if (window.gradeChartInstance) window.gradeChartInstance.destroy();

        const labels = filtered.map(h => {
            const d = new Date(h.date);
            return `${d.getDate()}/${d.getMonth() + 1}`;
        });

        const scores = filtered.map(h => gradeToNumber(h.grade));
        const colors = filtered.map(h => getGradeColor(h.grade));

        window.gradeChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Grade',
                    data: scores,
                    borderColor: 'rgba(56,189,248,0.8)',
                    backgroundColor: 'rgba(56,189,248,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0, max: 5.5,
                        ticks: {
                            callback: v => {
                                const map = { 5: 'A+', 4.5: 'A', 4: 'B+', 3.5: 'B', 3: 'C+', 2.5: 'C', 1.5: 'D', 0.5: 'F' };
                                return map[v] || '';
                            },
                            color: '#94a3b8'
                        },
                        grid: { color: 'rgba(255,255,255,0.05)' }
                    },
                    x: {
                        ticks: { color: '#94a3b8', font: { size: 10 } },
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => {
                                const item = filtered[ctx.dataIndex];
                                return item ? `${item.grade} (${item.score}/100)` : '';
                            }
                        }
                    }
                }
            }
        });
    }

    function renderMacroHistoryChart() {
        const history = getFoodHistory();
        const canvas = document.getElementById('macroHistoryChart');
        if (!canvas || typeof Chart === 'undefined') return;
        const ctx = canvas.getContext('2d');

        const sorted = history.sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-30);

        if (window.macroHistChartInstance) window.macroHistChartInstance.destroy();

        const labels = sorted.map(h => {
            const d = new Date(h.date);
            return `${d.getDate()}/${d.getMonth() + 1}`;
        });

        window.macroHistChartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Protein', data: sorted.map(h => Math.round(h.totals?.protein || 0)), backgroundColor: 'rgba(56,189,248,0.7)' },
                    { label: 'Carbs', data: sorted.map(h => Math.round(h.totals?.carbs || 0)), backgroundColor: 'rgba(251,191,36,0.7)' },
                    { label: 'Fats', data: sorted.map(h => Math.round(h.totals?.fats || 0)), backgroundColor: 'rgba(239,68,68,0.7)' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: {
                    x: { stacked: true, ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                    y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } }
            }
        });
    }

    // ── Supabase sync helpers ──
    async function saveDayToBackend(dateStr, items, totals, grade, score) {
        try {
            // First check if an entry exists for this date
            const getResp = await apiFetch(`/food_log?date=${dateStr}`, {
                headers: {
                    'Authorization': `Bearer ${API_TOKEN}`
                }
            });
            const existing = await getResp.json();

            if (existing && existing.length > 0) {
                // Update existing
                const id = existing[0].id;
                const resp = await apiFetch(`/food_log/${id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ items, totals, grade, grade_score: score })
                });
                return resp.ok;
            } else {
                // Insert new
                const resp = await apiFetch(`/food_log`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ date: dateStr, items, totals, grade, grade_score: score })
                });
                return resp.ok;
            }
        } catch (e) {
            console.error('Supabase food log save failed:', e);
            return false;
        }
    }

    async function fetchHistoryFromBackend(days = 30) {
        try {
            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - days);
            const dateStr = getLocalDayDateString(cutoff);

            const resp = await apiFetch(`/food_log?date_gte=${dateStr}`, {
                headers: {
                    'Authorization': `Bearer ${API_TOKEN}`
                }
            });
            if (resp.ok) {
                const data = await resp.json();
                // Sync to localStorage for offline
                const history = data.map(d => ({ date: d.date, grade: d.grade, score: d.grade_score, totals: d.totals }));
                saveFoodHistory(history);
                return history;
            }
        } catch (e) {
            console.error('Supabase history fetch failed, using localStorage:', e);
        }
        return getFoodHistory();
    }

    async function saveRecipeToSupabase(recipe) {
        try {
            const resp = await apiFetch(`/food_recipes`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${API_TOKEN}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(recipe)
            });
            return resp.ok;
        } catch (e) {
            console.error('Supabase recipe save failed:', e);
            return false;
        }
    }

    // ── My Foods panel render ──
    function renderMyFoods() {
        const favList = document.getElementById('my-foods-favorites-list');
        const recentList = document.getElementById('my-foods-recent-list');
        if (!favList || !recentList) return;

        const myFoods = getMyFoods();
        const favorites = myFoods.filter(f => f.favorite).sort((a, b) => (b.useCount || 0) - (a.useCount || 0));
        const recents = [...myFoods].sort((a, b) => new Date(b.lastUsed) - new Date(a.lastUsed)).slice(0, 20);

        function renderList(container, items, emptyMsg) {
            container.innerHTML = '';
            if (items.length === 0) {
                container.innerHTML = `<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem; padding: 0.25rem 0;">${emptyMsg}</div>`;
                return;
            }
            items.forEach(food => {
                const div = document.createElement('div');
                div.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.8rem;';
                const p = food.per100g;
                div.innerHTML = `
                    <div style="flex: 1; min-width: 0;">
                        <strong style="color: var(--text-primary);">${food.name}</strong>
                        ${food.brand ? `<span style="font-size: 0.7rem; color: var(--text-secondary);"> ${food.brand}</span>` : ''}
                        <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 1px;">
                            ${p.calories} kcal/100g · ${Math.round(food.useCount || 1)}× logged
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.3rem; flex-shrink: 0;">
                        <button class="my-foods-fav-btn" data-name="${food.name}" data-brand="${food.brand || ''}" style="padding: 2px 6px; background: none; border: 1px solid rgba(251,191,36,0.3); color: ${food.favorite ? '#fbbf24' : 'var(--text-secondary)'}; font-size: 0.85rem; cursor: pointer; border-radius: 3px;" title="${food.favorite ? 'Remove from favorites' : 'Add to favorites'}">${food.favorite ? '⭐' : '☆'}</button>
                        <button class="my-foods-add-btn" data-name="${food.name}" data-brand="${food.brand || ''}" style="padding: 2px 6px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.3); color: var(--accent-green); font-family: 'VT323', monospace; cursor: pointer; border-radius: 3px; font-size: 0.75rem;">+ Log</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }

        renderList(favList, favorites, 'No favorites yet — tap ☆ on a food to pin it here');
        renderList(recentList, recents, 'No history yet — log food to build your list');

        // Favorite toggle handlers
        document.querySelectorAll('.my-foods-fav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                toggleMyFoodFavorite(btn.getAttribute('data-name'), btn.getAttribute('data-brand'));
                renderMyFoods();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        });

        // Re-log handlers (expose selectedFood setter via window for the render callback)
        document.querySelectorAll('.my-foods-add-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const name = btn.getAttribute('data-name');
                const brand = btn.getAttribute('data-brand');
                const food = myFoods.find(f => f.name === name && (f.brand || '') === (brand || ''));
                if (!food) return;
                // Trigger the portion picker with this food
                if (window._symphonySelectFood) {
                    window._symphonySelectFood(food);
                }
            });
        });
    }

    // ── Main init ──
    function initFoodAnalytics() {
        renderFoodDashboard();
        renderRecipes();
        renderMyFoods();
        renderGradeChart(14);

        // Portion picker state
        let selectedFood = null; // { product, per100g: {cal,pro,carb,fat,...}, servingSize }

        const searchInput = document.getElementById('food-search-input');
        const resultsContainer = document.getElementById('food-autocomplete-results');
        const portionPicker = document.getElementById('food-portion-picker');
        const portionAmount = document.getElementById('portion-amount');
        const portionUnit = document.getElementById('portion-unit');
        const portionPreview = document.getElementById('portion-preview');
        const portionServingBtn = document.getElementById('portion-serving-btn');
        const portionAddBtn = document.getElementById('portion-add-btn');
        const portionCancelBtn = document.getElementById('portion-cancel-btn');
        const portionFoodName = document.getElementById('portion-food-name');

        let searchTimeout;
        let buildingRecipe = false;
        let recipeItems = [];

        // ── Built-in Common Foods Database (per 100g values) ──
        // qtyLabel = natural unit name, qtyG = grams per 1 unit (for quantity-based input)
        const COMMON_FOODS = [
            { name: 'Egg (whole, boiled)', brand: 'Whole Food', cal: 155, pro: 12.6, carb: 1.1, fat: 10.6, sugar: 1.1, fiber: 0, sodium: 0.124, serving: '1 large (50g)', servingG: 50, qtyLabel: 'egg', qtyG: 50 },
            { name: 'Egg (whole, scrambled)', brand: 'Whole Food', cal: 149, pro: 10.0, carb: 1.6, fat: 11.1, sugar: 1.4, fiber: 0, sodium: 0.145, serving: '1 large (61g)', servingG: 61, qtyLabel: 'egg', qtyG: 61 },
            { name: 'Egg (whole, fried)', brand: 'Whole Food', cal: 196, pro: 13.6, carb: 0.8, fat: 15.3, sugar: 0.4, fiber: 0, sodium: 0.207, serving: '1 large (46g)', servingG: 46, qtyLabel: 'egg', qtyG: 46 },
            { name: 'Egg (whole, raw)', brand: 'Whole Food', cal: 143, pro: 12.6, carb: 0.7, fat: 9.5, sugar: 0.4, fiber: 0, sodium: 0.140, serving: '1 large (50g)', servingG: 50, qtyLabel: 'egg', qtyG: 50 },
            { name: 'Egg White (raw)', brand: 'Whole Food', cal: 52, pro: 10.9, carb: 0.7, fat: 0.2, sugar: 0.7, fiber: 0, sodium: 0.166, serving: '1 large (33g)', servingG: 33, qtyLabel: 'egg white', qtyG: 33 },
            { name: 'Chicken Breast (grilled)', brand: 'Whole Food', cal: 165, pro: 31.0, carb: 0, fat: 3.6, sugar: 0, fiber: 0, sodium: 0.074, serving: '1 breast (172g)', servingG: 172, qtyLabel: 'breast', qtyG: 172 },
            { name: 'Chicken Thigh (skin off)', brand: 'Whole Food', cal: 209, pro: 26.0, carb: 0, fat: 10.9, sugar: 0, fiber: 0, sodium: 0.084, serving: '1 thigh (116g)', servingG: 116, qtyLabel: 'thigh', qtyG: 116 },
            { name: 'Salmon (baked)', brand: 'Whole Food', cal: 208, pro: 20.4, carb: 0, fat: 13.4, sugar: 0, fiber: 0, sodium: 0.059, serving: '1 fillet (154g)', servingG: 154, qtyLabel: 'fillet', qtyG: 154 },
            { name: 'Tuna (canned in water)', brand: 'Whole Food', cal: 116, pro: 25.5, carb: 0, fat: 0.8, sugar: 0, fiber: 0, sodium: 0.338, serving: '1 can (165g)', servingG: 165, qtyLabel: 'can', qtyG: 165 },
            { name: 'Beef Mince (lean)', brand: 'Whole Food', cal: 250, pro: 26.1, carb: 0, fat: 15.4, sugar: 0, fiber: 0, sodium: 0.075, serving: '100g', servingG: 100 },
            { name: 'Beef Steak (sirloin)', brand: 'Whole Food', cal: 271, pro: 26.1, carb: 0, fat: 17.3, sugar: 0, fiber: 0, sodium: 0.054, serving: '1 steak (200g)', servingG: 200, qtyLabel: 'steak', qtyG: 200 },
            { name: 'Bacon (cooked)', brand: 'Whole Food', cal: 541, pro: 37.0, carb: 1.4, fat: 42.0, sugar: 0, fiber: 0, sodium: 2.310, serving: '3 slices (34g)', servingG: 34, qtyLabel: 'rasher', qtyG: 11 },
            { name: 'White Rice (cooked)', brand: 'Whole Food', cal: 130, pro: 2.7, carb: 28.2, fat: 0.3, sugar: 0, fiber: 0.4, sodium: 0.001, serving: '1 cup (158g)', servingG: 158, qtyLabel: 'cup', qtyG: 158 },
            { name: 'Brown Rice (cooked)', brand: 'Whole Food', cal: 112, pro: 2.3, carb: 23.5, fat: 0.8, sugar: 0.4, fiber: 1.8, sodium: 0.005, serving: '1 cup (195g)', servingG: 195, qtyLabel: 'cup', qtyG: 195 },
            { name: 'Oats (rolled, dry)', brand: 'Whole Food', cal: 389, pro: 16.9, carb: 66.3, fat: 6.9, sugar: 0, fiber: 10.6, sodium: 0.002, serving: '1/2 cup (40g)', servingG: 40, qtyLabel: 'serve (½ cup)', qtyG: 40 },
            { name: 'White Bread', brand: 'Whole Food', cal: 265, pro: 9.4, carb: 49.2, fat: 3.2, sugar: 5.0, fiber: 2.7, sodium: 0.491, serving: '1 slice (25g)', servingG: 25, qtyLabel: 'slice', qtyG: 25 },
            { name: 'Wholemeal Bread', brand: 'Whole Food', cal: 247, pro: 13.0, carb: 41.3, fat: 3.4, sugar: 5.6, fiber: 6.0, sodium: 0.450, serving: '1 slice (28g)', servingG: 28, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Pasta (cooked)', brand: 'Whole Food', cal: 131, pro: 5.0, carb: 25.0, fat: 1.1, sugar: 0.6, fiber: 1.8, sodium: 0.001, serving: '1 cup (140g)', servingG: 140, qtyLabel: 'cup', qtyG: 140 },
            { name: 'Potato (boiled)', brand: 'Whole Food', cal: 87, pro: 1.9, carb: 20.1, fat: 0.1, sugar: 0.9, fiber: 1.8, sodium: 0.005, serving: '1 medium (150g)', servingG: 150, qtyLabel: 'potato', qtyG: 150 },
            { name: 'Kumara / Sweet Potato (baked)', brand: 'Whole Food', cal: 90, pro: 2.0, carb: 20.1, fat: 0.1, sugar: 6.5, fiber: 3.3, sodium: 0.036, serving: '1 medium (130g)', servingG: 130, qtyLabel: 'kumara', qtyG: 130 },
            { name: 'Banana', brand: 'Whole Food', cal: 89, pro: 1.1, carb: 22.8, fat: 0.3, sugar: 12.2, fiber: 2.6, sodium: 0.001, serving: '1 medium (118g)', servingG: 118, qtyLabel: 'banana', qtyG: 118 },
            { name: 'Apple', brand: 'Whole Food', cal: 52, pro: 0.3, carb: 13.8, fat: 0.2, sugar: 10.4, fiber: 2.4, sodium: 0.001, serving: '1 medium (182g)', servingG: 182, qtyLabel: 'apple', qtyG: 182 },
            { name: 'Orange', brand: 'Whole Food', cal: 47, pro: 0.9, carb: 11.8, fat: 0.1, sugar: 9.4, fiber: 2.4, sodium: 0, serving: '1 medium (131g)', servingG: 131, qtyLabel: 'orange', qtyG: 131 },
            { name: 'Avocado', brand: 'Whole Food', cal: 160, pro: 2.0, carb: 8.5, fat: 14.7, sugar: 0.7, fiber: 6.7, sodium: 0.007, serving: '1/2 avocado (68g)', servingG: 68, qtyLabel: 'half', qtyG: 68 },
            { name: 'Broccoli (steamed)', brand: 'Whole Food', cal: 35, pro: 2.4, carb: 7.2, fat: 0.4, sugar: 1.4, fiber: 3.3, sodium: 0.041, serving: '1 cup (91g)', servingG: 91, qtyLabel: 'cup', qtyG: 91 },
            { name: 'Spinach (raw)', brand: 'Whole Food', cal: 23, pro: 2.9, carb: 3.6, fat: 0.4, sugar: 0.4, fiber: 2.2, sodium: 0.079, serving: '1 cup (30g)', servingG: 30, qtyLabel: 'cup', qtyG: 30 },
            { name: 'Carrot (raw)', brand: 'Whole Food', cal: 41, pro: 0.9, carb: 9.6, fat: 0.2, sugar: 4.7, fiber: 2.8, sodium: 0.069, serving: '1 medium (61g)', servingG: 61, qtyLabel: 'carrot', qtyG: 61 },
            { name: 'Tomato (raw)', brand: 'Whole Food', cal: 18, pro: 0.9, carb: 3.9, fat: 0.2, sugar: 2.6, fiber: 1.2, sodium: 0.005, serving: '1 medium (123g)', servingG: 123, qtyLabel: 'tomato', qtyG: 123 },
            { name: 'Onion (raw)', brand: 'Whole Food', cal: 40, pro: 1.1, carb: 9.3, fat: 0.1, sugar: 4.2, fiber: 1.7, sodium: 0.004, serving: '1 medium (110g)', servingG: 110, qtyLabel: 'onion', qtyG: 110 },
            { name: 'Milk (whole)', brand: 'Whole Food', cal: 61, pro: 3.2, carb: 4.8, fat: 3.3, sugar: 5.1, fiber: 0, sodium: 0.043, serving: '1 cup (244ml)', servingG: 244, qtyLabel: 'cup', qtyG: 244 },
            { name: 'Milk (trim / skim)', brand: 'Whole Food', cal: 34, pro: 3.4, carb: 5.1, fat: 0.1, sugar: 5.1, fiber: 0, sodium: 0.042, serving: '1 cup (244ml)', servingG: 244, qtyLabel: 'cup', qtyG: 244 },
            { name: 'Greek Yoghurt (plain)', brand: 'Whole Food', cal: 97, pro: 9.0, carb: 3.6, fat: 5.0, sugar: 3.2, fiber: 0, sodium: 0.047, serving: '1 pot (170g)', servingG: 170, qtyLabel: 'pot', qtyG: 170 },
            { name: 'Cheese (cheddar)', brand: 'Whole Food', cal: 402, pro: 24.9, carb: 1.3, fat: 33.1, sugar: 0.5, fiber: 0, sodium: 0.621, serving: '1 slice (28g)', servingG: 28, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Butter', brand: 'Whole Food', cal: 717, pro: 0.9, carb: 0.1, fat: 81.1, sugar: 0.1, fiber: 0, sodium: 0.011, serving: '1 tbsp (14g)', servingG: 14, qtyLabel: 'tbsp', qtyG: 14 },
            { name: 'Peanut Butter', brand: 'Whole Food', cal: 588, pro: 25.1, carb: 20.0, fat: 50.4, sugar: 9.2, fiber: 6.0, sodium: 0.459, serving: '2 tbsp (32g)', servingG: 32, qtyLabel: 'tbsp', qtyG: 16 },
            { name: 'Almonds', brand: 'Whole Food', cal: 579, pro: 21.2, carb: 21.6, fat: 49.9, sugar: 4.4, fiber: 12.5, sodium: 0.001, serving: '1/4 cup (35g)', servingG: 35, qtyLabel: 'handful', qtyG: 35 },
            { name: 'Olive Oil', brand: 'Whole Food', cal: 884, pro: 0, carb: 0, fat: 100, sugar: 0, fiber: 0, sodium: 0.002, serving: '1 tbsp (14ml)', servingG: 14, qtyLabel: 'tbsp', qtyG: 14 },
            { name: 'Honey', brand: 'Whole Food', cal: 304, pro: 0.3, carb: 82.4, fat: 0, sugar: 82.1, fiber: 0.2, sodium: 0.004, serving: '1 tbsp (21g)', servingG: 21, qtyLabel: 'tbsp', qtyG: 21 },
            { name: 'Sugar (white)', brand: 'Whole Food', cal: 387, pro: 0, carb: 100, fat: 0, sugar: 100, fiber: 0, sodium: 0.001, serving: '1 tsp (4g)', servingG: 4, qtyLabel: 'tsp', qtyG: 4 },
            { name: 'Protein Powder (whey)', brand: 'Supplement', cal: 120, pro: 24.0, carb: 3.0, fat: 1.5, sugar: 1.5, fiber: 0, sodium: 0.160, serving: '1 scoop (30g)', servingG: 30, qtyLabel: 'scoop', qtyG: 30 },
            { name: 'Baked Beans (canned)', brand: 'Whole Food', cal: 94, pro: 5.2, carb: 14.5, fat: 0.4, sugar: 5.3, fiber: 5.5, sodium: 0.362, serving: '1 cup (254g)', servingG: 254, qtyLabel: 'cup', qtyG: 254 },
            { name: 'Chickpeas (canned)', brand: 'Whole Food', cal: 164, pro: 8.9, carb: 27.4, fat: 2.6, sugar: 4.8, fiber: 7.6, sodium: 0.007, serving: '1 cup (240g)', servingG: 240, qtyLabel: 'cup', qtyG: 240 },
            { name: 'Toast (white, buttered)', brand: 'Whole Food', cal: 313, pro: 8.0, carb: 42.0, fat: 12.0, sugar: 4.5, fiber: 2.0, sodium: 0.500, serving: '1 slice (35g)', servingG: 35, qtyLabel: 'slice', qtyG: 35 },
            { name: 'Sausage (pork)', brand: 'Whole Food', cal: 301, pro: 18.0, carb: 0, fat: 25.0, sugar: 0, fiber: 0, sodium: 0.749, serving: '1 link (75g)', servingG: 75, qtyLabel: 'sausage', qtyG: 75 },
            { name: 'Ham (deli sliced)', brand: 'Whole Food', cal: 145, pro: 21.0, carb: 3.5, fat: 5.5, sugar: 0, fiber: 0, sodium: 1.203, serving: '3 slices (84g)', servingG: 84, qtyLabel: 'slice', qtyG: 28 },
            { name: 'Mushrooms (raw)', brand: 'Whole Food', cal: 22, pro: 3.1, carb: 3.3, fat: 0.3, sugar: 2.0, fiber: 1.0, sodium: 0.005, serving: '1 cup (70g)', servingG: 70, qtyLabel: 'cup', qtyG: 70 },
            { name: 'Capsicum / Bell Pepper', brand: 'Whole Food', cal: 31, pro: 1.0, carb: 6.0, fat: 0.3, sugar: 4.2, fiber: 2.1, sodium: 0.004, serving: '1 medium (119g)', servingG: 119, qtyLabel: 'pepper', qtyG: 119 },
            { name: 'Lettuce (iceberg)', brand: 'Whole Food', cal: 14, pro: 0.9, carb: 3.0, fat: 0.1, sugar: 2.0, fiber: 1.2, sodium: 0.010, serving: '1 cup (72g)', servingG: 72, qtyLabel: 'cup', qtyG: 72 },
            { name: 'Mango', brand: 'Whole Food', cal: 60, pro: 0.8, carb: 15.0, fat: 0.4, sugar: 13.7, fiber: 1.6, sodium: 0.001, serving: '1 cup (165g)', servingG: 165, qtyLabel: 'mango', qtyG: 200 },
            { name: 'Strawberries', brand: 'Whole Food', cal: 32, pro: 0.7, carb: 7.7, fat: 0.3, sugar: 4.9, fiber: 2.0, sodium: 0.001, serving: '1 cup (152g)', servingG: 152, qtyLabel: 'cup', qtyG: 152 },
            { name: 'Blueberries', brand: 'Whole Food', cal: 57, pro: 0.7, carb: 14.5, fat: 0.3, sugar: 10.0, fiber: 2.4, sodium: 0.001, serving: '1 cup (148g)', servingG: 148, qtyLabel: 'cup', qtyG: 148 },
        ];

        // ── Search ──
        if (searchInput && resultsContainer) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value.trim();
                if (query.length < 2) { resultsContainer.style.display = 'none'; return; }

                searchTimeout = setTimeout(async () => {
                    resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: #94a3b8; font-size: 0.85rem;">Searching...</div>';
                    resultsContainer.style.display = 'block';

                    // 1) Search built-in common foods first (instant, always works)
                    const q = query.toLowerCase();
                    const localMatches = COMMON_FOODS.filter(f => f.name.toLowerCase().includes(q));

                    resultsContainer.innerHTML = '';

                    if (localMatches.length > 0) {
                        // Header for local results
                        const header = document.createElement('div');
                        header.style.cssText = 'padding: 0.4rem 0.75rem; font-size: 0.7rem; color: var(--accent-green); text-transform: uppercase; font-weight: 700; border-bottom: 1px solid rgba(52,211,153,0.15);';
                        header.textContent = '🥚 Whole Foods';
                        resultsContainer.appendChild(header);

                        localMatches.forEach(food => {
                            const resDiv = document.createElement('div');
                            resDiv.style.cssText = 'padding: 0.65rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;';
                            resDiv.className = 'food-result-item';
                            resDiv.innerHTML = `
                                <div style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">${food.name} <span style="font-size: 0.7rem; color: var(--accent-green);">${food.brand}</span></div>
                                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                                    per 100g: ${food.cal} kcal | ${food.pro}P ${food.carb}C ${food.fat}F
                                    <span style="color: var(--accent-blue);"> · Serving: ${food.serving}</span>
                                </div>
                            `;
                            resDiv.addEventListener('click', () => {
                                selectedFood = {
                                    name: food.name, brand: food.brand,
                                    per100g: { calories: food.cal, protein: food.pro, carbs: food.carb, fats: food.fat, sugars: food.sugar, fiber: food.fiber, sodium: food.sodium },
                                    servingSize: food.serving, servingG: food.servingG, ingredients: '',
                                    qtyLabel: food.qtyLabel || null, qtyG: food.qtyG || null
                                };
                                portionFoodName.innerText = food.name;
                                // Switch to quantity mode if food has a natural unit
                                if (food.qtyLabel && food.qtyG) {
                                    portionAmount.value = 1;
                                    portionAmount.step = 1;
                                    portionAmount.min = 0.5;
                                    portionUnit.innerHTML = `<option value="qty">× ${food.qtyLabel}${food.qtyLabel.endsWith('s') ? '' : '(s)'} (${food.qtyG}g ea)</option><option value="g">grams</option>`;
                                    portionUnit.value = 'qty';
                                } else {
                                    portionAmount.value = food.servingG || 100;
                                    portionAmount.step = 1;
                                    portionAmount.min = 1;
                                    portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
                                }
                                portionServingBtn.style.display = 'none';
                                updatePortionPreview();
                                portionPicker.style.display = 'block';
                                resultsContainer.style.display = 'none';
                            });
                            resultsContainer.appendChild(resDiv);
                        });
                    }

                    // 2) Also search Open Food Facts for branded/packaged products
                    if (query.length >= 3) {
                        try {
                            const response = await fetch(`https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(query)}&search_simple=1&action=process&json=1&page_size=6`);
                            const data = await response.json();

                            if (data.products && data.products.length > 0) {
                                // Add header for packaged products
                                const offHeader = document.createElement('div');
                                offHeader.style.cssText = 'padding: 0.4rem 0.75rem; font-size: 0.7rem; color: var(--accent-blue); text-transform: uppercase; font-weight: 700; border-bottom: 1px solid rgba(56,189,248,0.15); margin-top: 0.25rem;';
                                offHeader.textContent = '📦 Packaged Products (Open Food Facts)';
                                resultsContainer.appendChild(offHeader);

                                data.products.forEach(product => {
                                    if (!product.nutriments || (!product.nutriments['energy-kcal_100g'] && !product.nutriments['energy-kcal'])) return;

                                    const n = product.nutriments;
                                    const per100g = {
                                        calories: Math.round(n['energy-kcal_100g'] || n['energy-kcal'] || 0),
                                        protein: Math.round((n['proteins_100g'] || n.proteins || 0) * 10) / 10,
                                        carbs: Math.round((n['carbohydrates_100g'] || n.carbohydrates || 0) * 10) / 10,
                                        fats: Math.round((n['fat_100g'] || n.fat || 0) * 10) / 10,
                                        sugars: Math.round((n['sugars_100g'] || n.sugars || 0) * 10) / 10,
                                        fiber: Math.round((n['fiber_100g'] || n.fiber || 0) * 10) / 10,
                                        sodium: Math.round((n['sodium_100g'] || n.sodium || 0) * 100) / 100
                                    };
                                    const servingSize = product.serving_size || null;
                                    const servingG = product.serving_quantity || null;

                                    const desc = product.product_name || 'Unknown Product';
                                    const brand = product.brands || '';

                                    const resDiv = document.createElement('div');
                                    resDiv.style.cssText = 'padding: 0.65rem 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;';
                                    resDiv.className = 'food-result-item';
                                    resDiv.innerHTML = `
                                    <div style="font-weight: 600; color: #f1f5f9; font-size: 0.9rem;">${desc} <span style="font-size: 0.7rem; color: #94a3b8;">${brand}</span></div>
                                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.15rem;">
                                        per 100g: ${per100g.calories} kcal | ${per100g.protein}P ${per100g.carbs}C ${per100g.fats}F
                                        ${servingSize ? `<span style="color: var(--accent-blue);"> · Serving: ${servingSize}</span>` : ''}
                                    </div>
                                `;

                                    resDiv.addEventListener('click', () => {
                                        selectedFood = {
                                            name: desc, brand, per100g, servingSize, servingG,
                                            ingredients: product.ingredients_text || '',
                                            qtyLabel: null, qtyG: null
                                        };
                                        portionFoodName.innerText = `${desc}${brand ? ' (' + brand + ')' : ''}`;
                                        // Reset to grams mode for packaged products
                                        portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
                                        portionAmount.step = 1;
                                        portionAmount.min = 1;
                                        portionAmount.value = 100;
                                        portionServingBtn.style.display = servingSize ? 'inline-block' : 'none';
                                        portionServingBtn.innerText = servingSize ? `1 Serving (${servingSize})` : '1 Serving';
                                        updatePortionPreview();
                                        portionPicker.style.display = 'block';
                                        resultsContainer.style.display = 'none';
                                        searchInput.value = '';
                                        if (typeof playRetroClick === 'function') playRetroClick();
                                    });

                                    resultsContainer.appendChild(resDiv);
                                });
                            }
                        } catch (error) {
                            console.error('Food Search Error:', error);
                        }
                    }

                    // If no results at all from either source
                    if (resultsContainer.children.length === 0) {
                        resultsContainer.innerHTML = '<div style="padding: 0.75rem; color: var(--text-secondary); font-size: 0.85rem;">No results found. Try a different search term.</div>';
                    }
                }, 300);
            });

            document.addEventListener('click', (e) => {
                if (e.target !== searchInput && !resultsContainer.contains(e.target)) {
                    resultsContainer.style.display = 'none';
                }
            });
        }

        // ── Portion controls ──
        function getResolvedGrams() {
            const amt = parseFloat(portionAmount.value) || 0;
            const unit = portionUnit.value;
            if (unit === 'qty' && selectedFood && selectedFood.qtyG) {
                return amt * selectedFood.qtyG;
            }
            return amt;
        }

        function updatePortionPreview() {
            if (!selectedFood) return;
            const grams = getResolvedGrams();
            const scaled = scaleNutrients(selectedFood.per100g, grams);
            const unit = portionUnit.value;
            const suffix = (unit === 'qty' && selectedFood.qtyLabel) ? ` (${Math.round(grams)}g)` : '';
            portionPreview.innerText = `${scaled.calories} kcal | ${scaled.protein}P ${scaled.carbs}C ${scaled.fats}F${suffix}`;
        }

        if (portionAmount) portionAmount.addEventListener('input', updatePortionPreview);
        if (portionUnit) portionUnit.addEventListener('change', () => {
            // When switching between qty and grams, adjust the value
            if (portionUnit.value === 'g' && selectedFood && selectedFood.qtyG) {
                portionAmount.value = getResolvedGrams();
                portionAmount.step = 1;
                portionAmount.min = 1;
            } else if (portionUnit.value === 'qty' && selectedFood && selectedFood.qtyG) {
                portionAmount.value = 1;
                portionAmount.step = 1;
                portionAmount.min = 0.5;
            }
            updatePortionPreview();
        });

        if (portionServingBtn) {
            portionServingBtn.addEventListener('click', () => {
                if (selectedFood && selectedFood.servingG) {
                    portionAmount.value = selectedFood.servingG;
                    updatePortionPreview();
                }
            });
        }

        if (portionCancelBtn) {
            portionCancelBtn.addEventListener('click', () => {
                portionPicker.style.display = 'none';
                selectedFood = null;
            });
        }

        // Expose a function so My Foods panel can open the portion picker
        window._symphonySelectFood = function (food) {
            selectedFood = {
                name: food.name, brand: food.brand || '',
                per100g: food.per100g,
                servingSize: food.servingSize, servingG: food.servingG,
                ingredients: '',
                qtyLabel: food.qtyLabel || null, qtyG: food.qtyG || null
            };
            portionFoodName.innerText = food.name;
            if (food.qtyLabel && food.qtyG) {
                portionAmount.value = 1;
                portionAmount.step = 1;
                portionAmount.min = 0.5;
                portionUnit.innerHTML = `<option value="qty">× ${food.qtyLabel}${food.qtyLabel.endsWith('s') ? '' : '(s)'} (${food.qtyG}g ea)</option><option value="g">grams</option>`;
                portionUnit.value = 'qty';
            } else {
                portionAmount.value = food.servingG || 100;
                portionAmount.step = 1;
                portionAmount.min = 1;
                portionUnit.innerHTML = '<option value="g">grams</option><option value="ml">ml</option>';
            }
            portionServingBtn.style.display = 'none';
            updatePortionPreview();
            portionPicker.style.display = 'block';
        };

        if (portionAddBtn) {
            portionAddBtn.addEventListener('click', () => {
                if (!selectedFood) return;
                const grams = getResolvedGrams();
                const unit = portionUnit.value;
                const displayAmt = parseFloat(portionAmount.value) || 1;
                const displayUnit = (unit === 'qty' && selectedFood.qtyLabel) ? selectedFood.qtyLabel + (displayAmt !== 1 ? 's' : '') : unit;
                const scaled = scaleNutrients(selectedFood.per100g, grams);

                const logEntry = {
                    name: selectedFood.name,
                    amount: displayAmt,
                    unit: displayUnit,
                    grams: Math.round(grams),
                    ...scaled,
                    ingredients: selectedFood.ingredients,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                };

                // Auto-save to My Foods history
                addToMyFoods(selectedFood);

                if (buildingRecipe) {
                    // Add to recipe builder instead
                    recipeItems.push({ ...logEntry, per100g: selectedFood.per100g });
                    renderRecipeBuilder();
                } else {
                    const currentLog = getDailyFoodLog();
                    currentLog.push(logEntry);
                    saveFoodLog(currentLog);
                    renderFoodDashboard();
                }

                portionPicker.style.display = 'none';
                selectedFood = null;
                renderMyFoods();
                if (typeof playRetroClick === 'function') playRetroClick();
            });
        }

        // ── Recipe system ──
        const recipesHeader = document.querySelector('[data-pool="food-recipes"]');
        const recipesPanel = document.getElementById('food-recipes-panel');
        if (recipesHeader && recipesPanel) {
            recipesHeader.addEventListener('click', () => {
                const open = recipesPanel.style.display !== 'none';
                recipesPanel.style.display = open ? 'none' : 'block';
                recipesHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
            });
        }

        // ── My Foods accordion ──
        const myFoodsHeader = document.querySelector('[data-pool="my-foods"]');
        const myFoodsPanel = document.getElementById('my-foods-panel');
        if (myFoodsHeader && myFoodsPanel) {
            myFoodsHeader.addEventListener('click', () => {
                const open = myFoodsPanel.style.display !== 'none';
                myFoodsPanel.style.display = open ? 'none' : 'block';
                myFoodsHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
            });
        }

        const createRecipeBtn = document.getElementById('create-recipe-btn');
        const recipeBuilder = document.getElementById('recipe-builder');
        const recipeCloseBtn = document.getElementById('recipe-builder-close');
        const saveRecipeBtn = document.getElementById('save-recipe-btn');

        if (createRecipeBtn) {
            createRecipeBtn.addEventListener('click', () => {
                buildingRecipe = true;
                recipeItems = [];
                recipeBuilder.style.display = 'block';
                document.getElementById('recipe-name-input').value = '';
                renderRecipeBuilder();
            });
        }

        if (recipeCloseBtn) {
            recipeCloseBtn.addEventListener('click', () => {
                buildingRecipe = false;
                recipeItems = [];
                recipeBuilder.style.display = 'none';
            });
        }

        function renderRecipeBuilder() {
            const list = document.getElementById('recipe-items-list');
            const totalsEl = document.getElementById('recipe-totals');
            if (!list) return;

            if (recipeItems.length === 0) {
                list.innerHTML = '<li style="color: var(--text-secondary); font-style: italic;">Search and add foods above</li>';
                totalsEl.innerText = '';
                return;
            }

            list.innerHTML = recipeItems.map((item, i) =>
                `<li style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                    <span>${item.name} (${item.amount}${item.unit})</span>
                    <span style="color: var(--text-secondary);">${item.calories} kcal</span>
                </li>`
            ).join('');

            const totals = calculateDailyTotals(recipeItems);
            totalsEl.innerText = `Total: ${Math.round(totals.calories)} kcal | ${Math.round(totals.protein)}P ${Math.round(totals.carbs)}C ${Math.round(totals.fats)}F`;
        }

        if (saveRecipeBtn) {
            saveRecipeBtn.addEventListener('click', () => {
                const name = document.getElementById('recipe-name-input').value.trim();
                if (!name || recipeItems.length === 0) return;

                const recipe = { name, items: recipeItems };
                const allRecipes = getRecipes();
                allRecipes.push(recipe);
                saveRecipes(allRecipes);
                saveRecipeToSupabase(recipe); // async background save

                buildingRecipe = false;
                recipeItems = [];
                recipeBuilder.style.display = 'none';
                renderRecipes();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }

        // ── Analyze & Save button ──
        const runAuditBtn = document.getElementById('run-food-audit-btn');
        if (runAuditBtn) {
            runAuditBtn.addEventListener('click', async () => {
                const log = getDailyFoodLog();
                if (log.length === 0) {
                    alert('No food logged yet today.');
                    return;
                }

                runAuditBtn.innerHTML = '<span class="icon">⏳</span> Analyzing...';

                const totals = calculateDailyTotals(log);
                const result = gradeDailyIntake(totals);
                const today = getLocalDayDateString();

                // Save to history (localStorage)
                const history = getFoodHistory();
                const existingIdx = history.findIndex(h => h.date === today);
                const entry = { date: today, grade: result.grade, score: result.score, totals };
                if (existingIdx >= 0) history[existingIdx] = entry;
                else history.push(entry);
                saveFoodHistory(history);

                // Save to Backend
                await saveDayToBackend(today, log, totals, result.grade, result.score);

                // Refresh charts
                renderGradeChart(14);
                renderFoodDashboard();

                runAuditBtn.innerHTML = '<span class="icon">✅</span> Saved!';
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
                setTimeout(() => {
                    runAuditBtn.innerHTML = '<span class="icon">🔍</span> Analyze & Save to History';
                }, 2000);
            });
        }

        // ── Grade range buttons (7d / 14d / 30d) ──
        document.querySelectorAll('.grade-range-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.grade-range-btn').forEach(b => {
                    b.style.background = 'rgba(56,189,248,0.2)';
                    b.style.color = 'var(--accent-blue)';
                });
                btn.style.background = 'rgba(56,189,248,0.4)';
                btn.style.color = '#fff';
                renderGradeChart(parseInt(btn.getAttribute('data-days')));
            });
        });

        // ── Collapsible macro history ──
        const macroHeader = document.getElementById('macro-history-header');
        const macroBody = document.getElementById('macro-history-body');
        let macroLoaded = false;
        if (macroHeader && macroBody) {
            macroHeader.addEventListener('click', () => {
                const open = macroBody.style.display !== 'none';
                macroBody.style.display = open ? 'none' : 'block';
                macroHeader.querySelector('span:last-child').innerText = open ? '▶' : '▼';
                if (!open && !macroLoaded) {
                    renderMacroHistoryChart();
                    macroLoaded = true;
                }
            });
        }

        // Fetch Supabase history in background for charts
        fetchHistoryFromBackend(30).then(() => renderGradeChart(14));
    }

    // Initialize View
    // initChart();
    // renderTimeline();
    // createListItems(dailyCandidates, 'daily-list');
    // createListItems(weeklyMonthly.weekly, 'weekly-list');
    // createListItems(weeklyMonthly.monthly, 'monthly-list');

    // Create dog tasks (Referencing lines 726-734 block instead to avoid duplicate let/const error)

    // --- Bio Tracking Integration ---
    const MOCK_BLOOD_DATA = [
        { marker: 'Platelets', value: '509 x 10e9/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'WBC', value: '12.6 x 10e9/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'Ferritin', value: '205 ug/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'CRP', value: '9 mg/L', status: 'High', color: 'var(--accent-red)' },
        { marker: 'TSH', value: '0.37 mIU/L', status: 'Borderline Low', color: 'var(--accent-yellow)' }
    ];

    const MEDICAL_ALERTS = [
        {
            gene: 'HLA-B27',
            risk: 'Ankylosing Spondylitis / Autoimmune Joint Fusion',
            action: 'ALERT: Massive genetic liability. The moment you experience chronic, unexplainable lower back pain or morning joint stiffness, you must immediately report this HLA-B27 finding to a Rheumatologist to prevent spinal fusion.'
        },
        {
            gene: '9p21 (CDKN2A/B)',
            risk: 'Coronary Artery Disease (Heart Attack Risk)',
            action: 'Your coronary arteries are genetically prone to stiffening and retaining plaque. You must keep your ApoB blood levels <60 mg/dL for life. Aggressive Zone 2 cardio is mandatory.'
        },
        {
            gene: 'CYP3A4 (T/C)',
            risk: 'Rapid Drug Metabolizer (Statins/Testosterone)',
            action: 'Your liver is a hyper-active incinerator. If prescribing a statin for your 9p21 heart gene, warn your doctor that standard starting doses will likely be destroyed before working. You require tailored dosing.'
        },
        {
            gene: 'MTHFR (A/G)',
            risk: 'Homocysteine Vascular Damage',
            action: 'Vitamin conversion runs at ~65% speed. Avoid synthetic Folic Acid; take L-Methylfolate. Request a Homocysteine blood test to ensure levels are < 9 µmol/L to prevent artery scratching.'
        }
    ];

    const GENETIC_HACKS = [
        {
            gene: 'ADRB2 (G/G)',
            trait: 'Power/Sprint Fat Burning',
            advice: 'Stop jogging to lose fat. Your specific beta-2 receptors dictate that heavy, explosive weightlifting or high-intensity sprints will shred body fat drastically faster than steady-state cardio.'
        },
        {
            gene: 'COMT (G/G)',
            trait: 'The Warrior (Fast Dopamine Clearance)',
            advice: 'You violent sweep dopamine away. You require high-stakes environments or intense physical stress to feel "awake". Caffeine and L-Tyrosine are highly effective.'
        },
        {
            gene: 'COL5A1 (C/T)',
            trait: 'Brittle Tendons & Achilles Risk',
            advice: 'Abandon explosive plyometrics (box jumps). Perform Heavy Slow Resistance (HSR) training— specifically 4-5 second eccentric lowering phases—to purposefully thicken your tendons.'
        },
        {
            gene: 'CYP1A2 (A/C)',
            trait: 'Ultra-Slow Caffeine Clearance',
            advice: 'A strict 10:00 AM hard cutoff for ALL caffeine is mandatory. A 2 PM coffee means 50% of the drug is still bound to your receptors at midnight, utterly destroying deep sleep.'
        },
        {
            gene: 'SIRT1 (C/C)',
            trait: 'Disrupted Circadian Aging',
            advice: 'You physically cannot handle shifting sleep schedules. Pulling all-nighters or rotating shift work will shred your telomeres and induce rapid biological aging. Wake up at the exact same hour daily.'
        },
        {
            gene: 'ACTN3 (C/T)',
            trait: 'Hybrid Muscle Fibers',
            advice: 'Perfectly mixed 50/50 muscle fiber. Your body responds incredibly well to hybrid training (Crossfit, Hyrox, MMA) building heavy muscle mass AND deep VO2 max simultaneously.'
        }
    ];

    function initBioTracking() {
        // Render Blood Markers
        const bloodList = document.getElementById('blood-marker-list');
        if (bloodList) {
            bloodList.innerHTML = '';
            MOCK_BLOOD_DATA.forEach(item => {
                const li = document.createElement('li');
                li.style = `display:flex; justify-content:space-between; color: var(--text-primary); border-bottom: 1px solid rgba(255,255,255,0.05); padding: 0.5rem 0;`;
                li.innerHTML = `<span>${item.marker}</span> <div><strong>${item.value}</strong> <span style="color:${item.color}; margin-left: 0.5rem;">[${item.status}]</span></div>`;
                bloodList.appendChild(li);
            });
        }

        // Render Medical Alerts (Doctor Prompts)
        const medicalContainer = document.getElementById('medical-alerts-container');
        if (medicalContainer) {
            medicalContainer.innerHTML = '';
            MEDICAL_ALERTS.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-red); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-red); display: flex; justify-content: space-between;">
                        <span>${item.gene}</span>
                        <span style="font-size: 0.8rem; background: rgba(239, 68, 68, 0.2); padding: 2px 8px; border-radius: 12px; color: #fca5a5;">Clinical Review</span>
                    </div>
                    <div style="font-size: 0.95rem; color: #fca5a5; font-weight: 500; margin-top: 0.25rem;">${item.risk}</div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem; line-height: 1.5;">
                        <strong>Action for Doctor:</strong> ${item.action}
                    </div>
                `;
                medicalContainer.appendChild(div);
            });
        }

        // Render Genetic Hacks
        const geneticsContainer = document.getElementById('genetic-hacks-container');
        if (geneticsContainer) {
            geneticsContainer.innerHTML = '';
            GENETIC_HACKS.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem; margin-bottom: 1rem;`;
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-purple); display: flex; justify-content: space-between;">
                        <span>${item.gene}</span>
                        <span style="font-size: 0.8rem; background: rgba(192, 132, 252, 0.2); padding: 2px 8px; border-radius: 12px;">${item.trait}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.5rem; line-height: 1.5;">
                        <strong>Hack:</strong> ${item.advice}
                    </div>
                `;
                geneticsContainer.appendChild(div);
            });
        }
    }

    // Initialize View
    // initChart();
    // fetchTasksAndRenderTimeline(); (Now called differently or moved)
    // Only run legacy timeline fetch if the old DOM elements exist
    if (document.getElementById('today-timeline') || document.getElementById('pool-today')) {
        fetchTasksAndRenderTimeline();
    }
    // createListItems(dailyCandidates, 'daily-list');
    // createListItems(weeklyMonthly.weekly, 'weekly-list');
    // createListItems(weeklyMonthly.monthly, 'monthly-list');

    // Create dog tasks
    const dogTrainingTasks = [
        { text: "Meal Time: 'Wait' until told 'Okay'", points: 1 },
        { text: "Doorways: 'Wait' before going through any door", points: 1 },
        { text: "Impulse Control: Practice 'Leave It' during play", points: 1 },
        { text: "Free Time: 30-min Sniffari / Decompression Walk", points: 3 },
        { text: "Mental Stimulation: 10 mins Hide and Seek", points: 2 }
    ];
    createListItems(dogTrainingTasks, 'dog-training-list');

    // Create supplement tasks (now moved exclusively to the Bio tab)
    // Wrap in a function to allow re-rendering when the date changes
    function renderSupplements() {
        // Update the date display
        const dateDisplay = document.getElementById('supp-date-display');
        const nextBtn = document.getElementById('supp-date-next');

        if (dateDisplay) {
            const todayStr = getLocalDateString(new Date());
            const activeStr = getLocalDateString(window.bioTrackingDate);

            if (todayStr === activeStr) {
                dateDisplay.textContent = "Today";
                if (nextBtn) nextBtn.disabled = true;
            } else {
                const dayName = window.bioTrackingDate.toLocaleDateString('en-NZ', { weekday: 'short' });
                const monthName = window.bioTrackingDate.toLocaleDateString('en-NZ', { month: 'short' });
                const dayNum = window.bioTrackingDate.getDate();
                dateDisplay.textContent = `${dayName}, ${dayNum} ${monthName}`;
                if (nextBtn) nextBtn.disabled = false;
            }
        }

        // AM — Empty Stomach (30 min before food)
        const supplementsAM_Empty = [
            { text: "☀️ Solgar NAC 600mg × 2 caps (1200mg) — Empty stomach, 30 min before breakfast", points: 2, suppSync: "NAC", suppDose: 2 }
        ];
        createListItems(supplementsAM_Empty, 'supp-am-empty-body');

        // AM — With Breakfast
        const supplementsAM_Food = [
            { text: "🧬 Bioglan Vitamin K2 + D3 × 1 cap (180mcg/1000IU) — With food", points: 1, suppSync: "Vitamin K2", suppDose: 1 },
            { text: "🧠 Clinicians B-Complex Active × 1 cap (Mon/Wed/Fri) — With breakfast", points: 1, suppSync: "B-Complex", suppDose: 1 }
        ];
        createListItems(supplementsAM_Food, 'supp-am-food-body');

        // PM — With Dinner
        const supplementsPM_Dinner = [];
        createListItems(supplementsPM_Dinner, 'supp-pm-dinner-body');

        // PM — Before Bed
        const supplementsPM = [
            { text: "🌙 Doctor's Best Magnesium × 2 caps (400mg elemental) — 30-60 min before bed", points: 2, suppSync: "Magnesium", suppDose: 2 }
        ];
        createListItems(supplementsPM, 'supp-pm-bed-body');

        if (typeof window.refreshPulse === 'function') window.refreshPulse();
    }

    // Attach listeners to navigation buttons
    const prevBtn = document.getElementById('supp-date-prev');
    const nextBtn = document.getElementById('supp-date-next');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            window.bioTrackingDate.setDate(window.bioTrackingDate.getDate() - 1);
            renderSupplements();
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const todayStr = getLocalDateString(new Date());
            const activeStr = getLocalDateString(window.bioTrackingDate);
            if (todayStr !== activeStr) {
                window.bioTrackingDate.setDate(window.bioTrackingDate.getDate() + 1);
                renderSupplements();
            }
        });
    }

    // Initial Render
    renderSupplements();

    // Create Reminders (Mental Load)
    const activeReminders = [
        { text: "Make sure outside kids' toys are left upright so they can easily use them", points: 0 },
        { text: "Discard used tooth floss", points: 0 }
    ];
    createListItems(activeReminders, 'reminders-list');

    // --- Procurement (Wants vs Needs) Integration ---
    async function initProcurement() {
        const needsContainer = document.getElementById('needs-container');
        const wantsContainer = document.getElementById('wants-container');
        const advisoryContainer = document.getElementById('lobotto-advisory-container');
        const addBtn = document.getElementById('add-procurement-btn');

        if (!needsContainer || !wantsContainer || !advisoryContainer) return;

        let procurementData = [];
        const LOCAL_KEY = 'symphony_procurement_local';

        async function fetchData() {
            try {
                const response = await apiFetch(`/procurement`, {
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Content-Type': 'application/json'
                    }
                });
                if (response.ok) {
                    procurementData = await response.json();
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (e) {
                console.warn('Procurement: Backend fetch failed, using localStorage:', e);
                const local = localStorage.getItem(LOCAL_KEY);
                if (local) procurementData = JSON.parse(local);
            }
        }

        function renderAll() {
            needsContainer.innerHTML = '';
            wantsContainer.innerHTML = '';
            advisoryContainer.innerHTML = '';

            if (procurementData.length === 0) {
                needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No items yet. Add one above!</div>';
                return;
            }

            const needs = procurementData.filter(d => d.category === 'NEED');
            const wants = procurementData.filter(d => d.category === 'WANT');

            function renderCard(item, container, dotColor) {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem; position: relative;`;
                div.innerHTML = `
                    <button class="delete-procurement-btn" data-id="${item.id}" style="position: absolute; top: 0.5rem; right: 0.5rem; background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                    <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${dotColor};"></span>
                        ${escapeHTML(item.item)}
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        <strong>Why:</strong> ${item.justification || 'No justification provided.'}
                    </div>
                `;
                container.appendChild(div);
            }

            needs.forEach(item => renderCard(item, needsContainer, 'var(--accent-green)'));
            wants.forEach(item => renderCard(item, wantsContainer, 'var(--accent-yellow)'));

            if (needs.length === 0) needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No essential needs listed.</div>';
            if (wants.length === 0) wantsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem; font-style: italic;">No discretionary wants listed.</div>';

            // Render Advisory (for all items)
            procurementData.forEach(item => {
                const div = document.createElement('div');
                div.style = `background: rgba(15, 23, 42, 0.4); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 1rem;`;
                const verdictColor = item.athena_verdict === 'APPROVED' ? 'var(--accent-green)' : (item.athena_verdict === 'FLAGGED' ? 'var(--accent-yellow)' : 'var(--text-secondary)');
                div.innerHTML = `
                    <div style="font-weight: 600; color: var(--accent-blue); display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Target: ${escapeHTML(item.item)}</span>
                        <span style="font-size: 0.75rem; color: ${verdictColor}; border: 1px solid ${verdictColor}; padding: 2px 6px; border-radius: 4px;">${item.athena_verdict || 'PENDING'}</span>
                    </div>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">
                        ${item.athena_comment || 'Awaiting Lobotto assessment...'}
                    </div>
                `;
                advisoryContainer.appendChild(div);
            });

            // Bind delete buttons
            document.querySelectorAll('.delete-procurement-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    procurementData = procurementData.filter(d => d.id !== id);
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                    renderAll();
                    try {
                        await apiFetch(`/procurement/${id}`, {
                            method: 'DELETE',
                            headers: {
                                'Authorization': `Bearer ${API_TOKEN}`
                            }
                        });
                    } catch (e) { console.warn('Failed to delete procurement item:', e); }
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });
        }

        // Add item handler
        if (addBtn) {
            addBtn.addEventListener('click', async () => {
                const itemEl = document.getElementById('procurement-item-input');
                const justEl = document.getElementById('procurement-justification-input');
                const catEl = document.getElementById('procurement-category-input');

                const item = itemEl.value.trim();
                const justification = justEl.value.trim();
                const category = catEl.value;

                if (!item) {
                    alert('Please enter an item name.');
                    return;
                }

                const newItem = {
                    item,
                    justification: justification || 'No justification provided.',
                    category,
                    athena_verdict: 'PENDING',
                    athena_comment: 'Awaiting Lobotto assessment...'
                };

                // Optimistic local add
                procurementData.unshift(newItem);
                localStorage.setItem(LOCAL_KEY, JSON.stringify(procurementData));
                renderAll();

                itemEl.value = '';
                justEl.value = '';

                // Persist to Backend
                try {
                    const resp = await apiFetch(`/procurement`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${API_TOKEN}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(newItem)
                    });
                    if (resp.ok) {
                        await fetchData();
                        renderAll();
                    }
                } catch (e) {
                    console.warn('Failed to save procurement item to Backend:', e);
                }

                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }

        // Init
        needsContainer.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.85rem;">Syncing from Backend...</div>';
        await fetchData();
        renderAll();
    }

    // Assign globally to be called by onchange
    window.changeTaskColor = async function (taskId, selectEl) {
        const newColor = selectEl.value;
        const colorMap = {
            'RED': '#ef4444',
            'ORANGE': '#f97316',
            'GREEN': '#10b981'
        };
        const hex = colorMap[newColor];

        // Optimistically update the dropdown visual styling
        selectEl.style.borderColor = hex;
        selectEl.style.color = hex;

        try {
            selectEl.disabled = true;

            await apiFetch(`/tasks/${taskId}`, {
                    method: "PATCH",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ priority_color: newColor })
                });

            selectEl.disabled = false;

            // Intentionally bypassing initTaskConfigurator() here 
            // so the task doesn't vanish from the user's current category view.

            // Refresh the main schedule view behind the scenes just in case
            if (typeof fetchLocalAPIData === 'function') {
                fetchLocalAPIData();
            }

        } catch (err) {
            console.error("Failed to update task color:", err);
            selectEl.disabled = false;
            alert("Failed to save changes.");
        }
    };

    // --- Supps Vault Implementation ---
    async function initSuppsVault() {
        const grid = document.getElementById('supps-inventory-grid');
        const addBtn = document.getElementById('add-supp-btn');
        if (!grid || !addBtn) return;

        let inventory = [];

        // 1. Fetch from Backend (safe: won't clobber local data)
        async function fetchLocalAPIInventory() {
            try {
                const resp = await apiFetch(`/supp_inventory`, {
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`
                    }
                });
                if (resp.ok) {
                    const apiData = await resp.json();
                    const localData = localStorage.getItem('symphony_supp_inventory_local');
                    const localItems = localData ? JSON.parse(localData) : [];
                    if (apiData.length > 0) {
                        inventory = apiData;
                        localStorage.setItem('symphony_supp_inventory_local', JSON.stringify(inventory));
                    } else if (localItems.length > 0) {
                        inventory = localItems;
                        console.info('Supps: Backend empty, keeping local inventory');
                    } else {
                        inventory = [];
                    }
                }
            } catch (e) {
                console.error("Failed to fetch supps from Backend, falling back to local:", e);
                const local = localStorage.getItem('symphony_supp_inventory_local');
                if (local) inventory = JSON.parse(local);
            }
        }

        // 2. Add New Supp
        async function addSupp() {
            const nameEl = document.getElementById('supp-name-input');
            const capEl = document.getElementById('supp-capacity-input');
            const doseEl = document.getElementById('supp-dose-input');

            const name = nameEl.value.trim();
            const capacity = parseInt(capEl.value);
            const dailyDose = parseInt(doseEl.value);

            if (!name || isNaN(capacity) || isNaN(dailyDose)) {
                alert("Please fill out all fields correctly.");
                return;
            }

            const newSupp = {
                name,
                total_capacity: capacity,
                current_stock: capacity,
                daily_dose: dailyDose
            };

            // Optimistic Local Add
            inventory.push(newSupp);
            renderGrid();

            nameEl.value = ''; capEl.value = ''; doseEl.value = '';

            try {
                await apiFetch(`/supp_inventory`, {
                    method: 'POST',
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(newSupp)
                });
                // Re-fetch to get actual IDs
                await fetchLocalAPIInventory();
                renderGrid();
            } catch (e) {
                console.error("Failed to save new supp to Backend:", e);
            }
        }

        // 3. Update existing supp (take dose or refill)
        async function updateSuppStock(id, newStock) {
            // Find locally and update
            const supp = inventory.find(s => s.id === id);
            if (supp) {
                supp.current_stock = newStock;
                renderGrid(); // Instant UI update
            }

            try {
                await apiFetch(`/supp_inventory/${id}`, {
                    method: 'PATCH',
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        current_stock: newStock
                    })
                });
            } catch (e) {
                console.error("Failed to update stock in Backend:", e);
            }
        }

        // Global Sync Function for Checklists
        window.triggerSuppSync = async function (suppName, amountToDeduct) {
            const supp = inventory.find(s => s.name === suppName);
            if (supp) {
                const newStock = Math.max(0, supp.current_stock - amountToDeduct);
                console.log(`Syncing ${suppName}: Deducting ${amountToDeduct}. New Stock: ${newStock}`);
                await updateSuppStock(supp.id, newStock);
            } else {
                console.warn(`Could not sync ${suppName}: Not found in Vault inventory.`);
            }
        };

        // 4. Render Grid
        function renderGrid() {
            grid.innerHTML = '';
            if (inventory.length === 0) {
                grid.innerHTML = '<div style="color: var(--text-secondary); grid-column: 1/-1;">No supplements tracked yet. Add one above.</div>';
                return;
            }

            inventory.forEach(supp => {
                const { id, name, total_capacity, current_stock, daily_dose } = supp;
                const percentage = Math.max(0, Math.min(100, (current_stock / total_capacity) * 100));

                const isLow = percentage < 50;
                const dangerText = isLow ? '<span style="color: var(--accent-red); font-size: 0.8rem; margin-left: 0.5rem;" class="blinking">⚠️ LOW STOCK</span>' : '';
                const cardBorder = isLow ? 'var(--accent-red)' : 'var(--glass-border)';
                const barColor = isLow ? 'var(--accent-red)' : 'var(--accent-blue)';

                let daysLeft = '0';
                if (daily_dose > 0) {
                    daysLeft = Math.floor(current_stock / daily_dose);
                }

                const div = document.createElement('div');
                div.className = 'glass-panel';
                div.style.cssText = `border-color: ${cardBorder}; position: relative; padding: 1rem;`;

                div.innerHTML = `
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-size: 1.1rem;">
                        ${name} ${dangerText}
                    </h4>
                    
                    <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <span>Dose: ${daily_dose}/day</span>
                        <span style="float: right;">Est. ${daysLeft} days left</span>
                    </div>

                    <div style="width: 100%; height: 8px; background: rgba(0,0,0,0.5); border-radius: 4px; overflow: hidden; margin-bottom: 0.5rem; border: 1px solid rgba(255,255,255,0.1);">
                        <div style="height: 100%; width: ${percentage}%; background: ${barColor}; transition: width 0.3s ease;"></div>
                    </div>
                    
                    <div style="font-size: 0.85rem; color: var(--text-primary); text-align: right; margin-bottom: 1rem;">
                        <strong>${current_stock}</strong> / ${total_capacity} pills
                    </div>

                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <button class="tab-btn take-dose-btn" data-id="${id}" data-dose="${daily_dose}" data-stock="${current_stock}"
                            style="flex: 1; margin: 0; padding: 0.3rem; background: rgba(56,189,248,0.1); border: 1px solid var(--accent-blue); color: var(--accent-blue); font-size: 0.8rem;">
                            Take Dose (-${daily_dose})
                        </button>
                        <button class="tab-btn refill-btn" data-id="${id}" data-cap="${total_capacity}"
                            style="flex: 1; margin: 0; padding: 0.3rem; background: rgba(251,191,36,0.1); border: 1px solid var(--accent-yellow); color: var(--accent-yellow); font-size: 0.8rem;">
                            Refill (Max)
                        </button>
                    </div>
                    <button class="tab-btn adjust-btn" data-id="${id}" data-stock="${current_stock}"
                        style="width: 100%; margin: 0; padding: 0.3rem; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-secondary); font-size: 0.8rem;">
                        ⚙️ Adjust Stock Manually
                    </button>
                `;
                grid.appendChild(div);
            });

            // Bind events
            document.querySelectorAll('.take-dose-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const dose = parseInt(e.target.getAttribute('data-dose'));
                    const stock = parseInt(e.target.getAttribute('data-stock'));
                    const newStock = Math.max(0, stock - dose);
                    updateSuppStock(id, newStock);
                });
            });

            document.querySelectorAll('.refill-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const cap = parseInt(e.target.getAttribute('data-cap'));
                    updateSuppStock(id, cap);
                });
            });

            document.querySelectorAll('.adjust-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const id = e.target.getAttribute('data-id');
                    const currentStock = e.target.getAttribute('data-stock');
                    const newStockStr = prompt(`Enter the new stock amount (Current: ${currentStock}):`, currentStock);
                    if (newStockStr !== null) {
                        const newStock = parseInt(newStockStr);
                        if (!isNaN(newStock) && newStock >= 0) {
                            updateSuppStock(id, newStock);
                        } else {
                            alert("Invalid number.");
                        }
                    }
                });
            });
        }

        addBtn.addEventListener('click', addSupp);

        // Init
        await fetchLocalAPIInventory();
        renderGrid();
    }

    // --- Open Logistics Implementation ---
    async function initLogistics() {
        const container = document.getElementById('logistics-items-container');
        const addBtn = document.getElementById('add-logistics-btn');
        const titleInput = document.getElementById('logistics-title-input');
        if (!container || !addBtn) return;

        let items = []; // { id, title, status, subtasks: [{id, text, completed}] }
        let solvedItems = []; // Solved items log
        const LOCAL_KEY = 'symphony_logistics_local';
        const SOLVED_KEY = 'symphony_logistics_solved';
        const solvedList = document.getElementById('logistics-solved-list');
        const solvedCount = document.getElementById('logistics-solved-count');

        // Try Supabase first, fallback to localStorage (safe: won't clobber local data)
        async function fetchItems() {
            try {
                const resp = await apiFetch(`/logistics?status=open`, {
                    headers: { "Authorization": `Bearer ${API_TOKEN}` }
                });
                if (resp.ok) {
                    const data = await resp.json();
                    // Fetch subtasks for all items
                    const stResp = await apiFetch(`/logistics_subtasks`, {
                        headers: { "Authorization": `Bearer ${API_TOKEN}` }
                    });
                    const subtasks = stResp.ok ? await stResp.json() : [];
                    const mergedItems = data.map(item => ({
                        ...item,
                        subtasks: subtasks.filter(st => st.logistics_id === item.id)
                    }));

                    const localData = localStorage.getItem(LOCAL_KEY);
                    const localItems = localData ? JSON.parse(localData) : [];
                    if (mergedItems.length > 0) {
                        items = mergedItems;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
                    } else if (localItems.length > 0) {
                        items = localItems;
                        console.info('Logistics: Backend empty, keeping local data');
                    } else {
                        items = [];
                    }

                    // Also fetch solved items for the log
                    try {
                        const solvedResp = await apiFetch(`/logistics?status=done`, {
                            headers: { "Authorization": `Bearer ${API_TOKEN}` }
                        });
                        if (solvedResp.ok) {
                            const solvedData = await solvedResp.json();
                            solvedItems = solvedData.map(item => ({
                                ...item,
                                subtasks: subtasks.filter(st => st.logistics_id === item.id)
                            }));
                            localStorage.setItem(SOLVED_KEY, JSON.stringify(solvedItems));
                        }
                    } catch (e) { /* solved fetch optional */ }
                    return;
                }
            } catch (e) {
                console.warn('Logistics: Backend unavailable, using localStorage', e);
            }
            // Fallback
            const local = localStorage.getItem(LOCAL_KEY);
            items = local ? JSON.parse(local) : [];
            const localSolved = localStorage.getItem(SOLVED_KEY);
            solvedItems = localSolved ? JSON.parse(localSolved) : [];
        }

        function saveLocal() {
            localStorage.setItem(LOCAL_KEY, JSON.stringify(items));
            localStorage.setItem(SOLVED_KEY, JSON.stringify(solvedItems));
        }

        // Add new item
        async function addItem() {
            const title = titleInput.value.trim();
            if (!title) return;

            const newItem = {
                id: crypto.randomUUID(),
                title,
                status: 'open',
                created_at: new Date().toISOString(),
                subtasks: []
            };

            items.unshift(newItem);
            saveLocal();
            renderItems();
            titleInput.value = '';

            try {
                await apiFetch(`/logistics`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ id: newItem.id, title: newItem.title, status: 'open' })
                });
            } catch (e) { console.warn('Failed to save item to Backend:', e); }
        }

        // Add sub-task
        async function addSubtask(itemId, text) {
            const item = items.find(i => i.id === itemId);
            if (!item || !text.trim()) return;

            const st = { id: crypto.randomUUID(), logistics_id: itemId, text: text.trim(), completed: false };
            item.subtasks.push(st);
            saveLocal();
            renderItems();

            try {
                await apiFetch(`/logistics_subtasks`, {
                    method: "POST",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(st)
                });
            } catch (e) { console.warn('Failed to save subtask to Backend:', e); }
        }

        // Toggle sub-task completion
        async function toggleSubtask(itemId, subtaskId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;
            const st = item.subtasks.find(s => s.id === subtaskId);
            if (!st) return;

            st.completed = !st.completed;
            saveLocal();
            renderItems();

            try {
                await apiFetch(`/logistics_subtasks/${subtaskId}`, {
                    method: "PATCH",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ completed: st.completed })
                });
            } catch (e) { console.warn('Failed to update subtask:', e); }
        }

        // Mark item as done → move to solved log
        async function markDone(itemId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;

            item.status = 'done';
            item.solved_at = new Date().toISOString();
            solvedItems.unshift(item);
            items = items.filter(i => i.id !== itemId);
            saveLocal();
            renderItems();
            renderSolvedLog();

            try {
                await apiFetch(`/logistics/${itemId}`, {
                    method: "PATCH",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ status: 'done', updated_at: new Date().toISOString() })
                });
            } catch (e) { console.warn('Failed to mark done in Backend:', e); }
        }

        // Re-open a solved item
        async function reopenItem(itemId) {
            const item = solvedItems.find(i => i.id === itemId);
            if (!item) return;

            item.status = 'open';
            delete item.solved_at;
            items.unshift(item);
            solvedItems = solvedItems.filter(i => i.id !== itemId);
            saveLocal();
            renderItems();
            renderSolvedLog();

            try {
                await apiFetch(`/logistics/${itemId}`, {
                    method: "PATCH",
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ status: 'open', updated_at: new Date().toISOString() })
                });
            } catch (e) { console.warn('Failed to reopen in Backend:', e); }
        }

        // Render Solved Log
        function renderSolvedLog() {
            if (!solvedList || !solvedCount) return;
            solvedCount.textContent = `(${solvedItems.length} item${solvedItems.length !== 1 ? 's' : ''})`;

            if (solvedItems.length === 0) {
                solvedList.innerHTML = '<div style="color: var(--text-secondary); font-size: 0.85rem; padding: 0.5rem;">No solved items yet.</div>';
                return;
            }

            solvedList.innerHTML = solvedItems.map(item => {
                const solvedDate = item.solved_at ? new Date(item.solved_at).toLocaleDateString('en-NZ', { day: 'numeric', month: 'short' }) : '';
                return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.75rem; background: rgba(0,0,0,0.15); border: 1px solid rgba(34,197,94,0.15); border-radius: 6px;">
                    <div style="flex: 1;">
                        <span style="color: var(--text-secondary); text-decoration: line-through; font-size: 0.9rem;">✅ ${escapeHTML(item.title)}</span>
                        ${solvedDate ? `<span style="font-size: 0.7rem; color: var(--text-secondary); margin-left: 0.5rem; opacity: 0.6;">${solvedDate}</span>` : ''}
                    </div>
                    <button class="logistics-reopen-btn" data-id="${item.id}"
                        style="background: rgba(251,191,36,0.15); border: 1px solid var(--accent-yellow); color: var(--accent-yellow); padding: 0.2rem 0.6rem; border-radius: 4px; font-family: 'VT323', monospace; font-size: 0.8rem; cursor: pointer; white-space: nowrap;"
                        title="Move back to active items">
                        ↩️ Re-open
                    </button>
                </div>`;
            }).join('');

            // Bind reopen buttons
            solvedList.querySelectorAll('.logistics-reopen-btn').forEach(btn => {
                btn.addEventListener('click', () => reopenItem(btn.dataset.id));
            });
        }

        // Delete sub-task
        async function deleteSubtask(itemId, subtaskId) {
            const item = items.find(i => i.id === itemId);
            if (!item) return;
            item.subtasks = item.subtasks.filter(s => s.id !== subtaskId);
            saveLocal();
            renderItems();

            try {
                await apiFetch(`/logistics_subtasks/${subtaskId}`, {
                    method: 'DELETE',
                    headers: {
                        "Authorization": `Bearer ${API_TOKEN}`
                    }
                });
            } catch (e) { console.warn('Failed to delete subtask:', e); }
        }

        // Render
        function renderItems() {
            if (items.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 3rem; color: var(--text-secondary);">
                        <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
                        <div style="font-size: 1.1rem;">Nothing to solve right now!</div>
                        <div style="font-size: 0.85rem; margin-top: 0.5rem;">Add a logistics item above when something comes up.</div>
                    </div>`;
                return;
            }

            container.innerHTML = items.map(item => {
                const completedCount = item.subtasks.filter(s => s.completed).length;
                const totalCount = item.subtasks.length;
                const progressText = totalCount > 0 ? `${completedCount}/${totalCount} steps` : 'No steps yet';
                const progressPct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;
                const barColor = progressPct === 100 ? 'var(--accent-green)' : 'var(--accent-blue)';

                return `
                <div class="glass-panel" style="border-color: var(--accent-blue); padding: 1.25rem; position: relative;">
                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary); font-size: 1.15rem; line-height: 1.3;">
                                🔧 ${escapeHTML(item.title)}
                            </h4>
                            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                ${progressText}
                            </div>
                        </div>
                        <button class="logistics-done-btn" data-id="${item.id}"
                            style="background: rgba(34,197,94,0.15); border: 1px solid var(--accent-green); color: var(--accent-green); padding: 0.25rem 0.75rem; border-radius: 4px; font-family: 'VT323', monospace; font-size: 0.85rem; cursor: pointer; white-space: nowrap;">
                            ✅ Solved
                        </button>
                    </div>

                    <!-- Progress bar -->
                    ${totalCount > 0 ? `
                    <div style="width: 100%; height: 4px; background: rgba(0,0,0,0.4); border-radius: 2px; margin-bottom: 1rem; overflow: hidden;">
                        <div style="height: 100%; width: ${progressPct}%; background: ${barColor}; transition: width 0.3s ease;"></div>
                    </div>` : ''}

                    <!-- Sub-tasks list -->
                    <div style="display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.75rem;">
                        ${item.subtasks.map(st => `
                        <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.35rem 0.5rem; background: rgba(0,0,0,0.2); border-radius: 4px; border: 1px solid rgba(255,255,255,0.05);">
                            <input type="checkbox" class="logistics-st-check" data-item="${item.id}" data-st="${st.id}"
                                ${st.completed ? 'checked' : ''}
                                style="cursor: pointer; accent-color: var(--accent-blue); width: 16px; height: 16px;">
                            <span style="flex: 1; font-size: 0.9rem; color: ${st.completed ? 'var(--text-secondary)' : 'var(--text-primary)'}; ${st.completed ? 'text-decoration: line-through;' : ''}">${st.text}</span>
                            <button class="logistics-st-del" data-item="${item.id}" data-st="${st.id}"
                                style="background: none; border: none; color: var(--accent-red); cursor: pointer; font-size: 0.9rem; padding: 0 4px; opacity: 0.6;"
                                title="Remove">×</button>
                        </div>`).join('')}
                    </div>

                    <!-- Add sub-task input -->
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" class="logistics-st-input" data-item="${item.id}"
                            placeholder="Add a step..."
                            style="flex: 1; padding: 0.4rem 0.6rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; font-family: 'VT323', monospace; font-size: 0.9rem; border-radius: 4px;">
                        <button class="logistics-st-add" data-item="${item.id}"
                            style="padding: 0.4rem 0.75rem; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); color: var(--accent-blue); font-family: 'VT323', monospace; font-size: 0.85rem; cursor: pointer; border-radius: 4px; white-space: nowrap;">+ Step</button>
                    </div>
                </div>`;
            }).join('');

            // Bind events
            container.querySelectorAll('.logistics-done-btn').forEach(btn => {
                btn.addEventListener('click', () => markDone(btn.dataset.id));
            });

            container.querySelectorAll('.logistics-st-check').forEach(cb => {
                cb.addEventListener('change', () => toggleSubtask(cb.dataset.item, cb.dataset.st));
            });

            container.querySelectorAll('.logistics-st-del').forEach(btn => {
                btn.addEventListener('click', () => deleteSubtask(btn.dataset.item, btn.dataset.st));
            });

            container.querySelectorAll('.logistics-st-add').forEach(btn => {
                btn.addEventListener('click', () => {
                    const input = container.querySelector(`.logistics-st-input[data-item="${btn.dataset.item}"]`);
                    if (input && input.value.trim()) {
                        addSubtask(btn.dataset.item, input.value);
                        input.value = '';
                    }
                });
            });

            // Allow Enter key to add sub-tasks
            container.querySelectorAll('.logistics-st-input').forEach(input => {
                input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && input.value.trim()) {
                        addSubtask(input.dataset.item, input.value);
                        input.value = '';
                    }
                });
            });
        }

        // Event handlers
        addBtn.addEventListener('click', addItem);
        titleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') addItem();
        });

        // Init
        await fetchItems();
        renderItems();
        renderSolvedLog();
    }

    // populateWorkout();
    initFoodAnalytics();
    initBioTracking();
    initProcurement();
    initLogistics();
    initSuppsVault();

    // --- Quinny's Page (Pet Health Tracking) ---
    function initQuinnyPage() {
        const QUINNY_KEY = 'symphony_quinny_data';
        function getData() {
            const s = localStorage.getItem(QUINNY_KEY);
            return s ? JSON.parse(s) : { birthday: null, vaccinations: [], treatments: [] };
        }
        function saveData(d) { localStorage.setItem(QUINNY_KEY, JSON.stringify(d)); }

        function formatDate(iso) {
            if (!iso) return '—';
            const d = new Date(iso + 'T00:00:00');
            return d.toLocaleDateString('en-NZ', { day: 'numeric', month: 'short', year: 'numeric' });
        }

        function daysUntil(iso) {
            if (!iso) return Infinity;
            const now = new Date(); now.setHours(0, 0, 0, 0);
            return Math.ceil((new Date(iso + 'T00:00:00') - now) / 86400000);
        }

        function dueBadge(iso) {
            const days = daysUntil(iso);
            if (days < 0) return `<span style="color: var(--accent-red); font-weight: 700;">⚠️ OVERDUE by ${Math.abs(days)}d</span>`;
            if (days <= 7) return `<span style="color: var(--accent-yellow);">⏰ Due in ${days}d</span>`;
            if (days <= 30) return `<span style="color: var(--accent-blue);">📅 Due in ${days}d</span>`;
            return `<span style="color: var(--accent-green);">✅ Due ${formatDate(iso)}</span>`;
        }

        // Photo upload
        const photoInput = document.getElementById('quinny-photo-upload');
        const profileImg = document.getElementById('quinny-profile-img');

        // Restore saved photo on load
        try {
            const savedPhoto = localStorage.getItem('symphony_quinny_photo');
            if (savedPhoto && profileImg) profileImg.src = savedPhoto;
        } catch (e) { console.warn('Failed to restore Quinny photo:', e); }

        if (photoInput && profileImg) {
            photoInput.addEventListener('change', function (e) {
                try {
                    const file = e.target.files[0];
                    if (!file) return;
                    console.log('[Quinny] Photo selected:', file.name, file.size, 'bytes');
                    const reader = new FileReader();
                    reader.onload = function (evt) {
                        try {
                            const dataUrl = evt.target.result;
                            profileImg.src = dataUrl;
                            // Check size — localStorage has ~5MB limit
                            if (dataUrl.length > 4000000) {
                                // Too big, resize via canvas
                                const img = new Image();
                                img.onload = function () {
                                    const canvas = document.createElement('canvas');
                                    const MAX = 300;
                                    let w = img.width, h = img.height;
                                    if (w > h) { h = Math.round(h * MAX / w); w = MAX; }
                                    else { w = Math.round(w * MAX / h); h = MAX; }
                                    canvas.width = w; canvas.height = h;
                                    canvas.getContext('2d').drawImage(img, 0, 0, w, h);
                                    const smallUrl = canvas.toDataURL('image/jpeg', 0.7);
                                    localStorage.setItem('symphony_quinny_photo', smallUrl);
                                    profileImg.src = smallUrl;
                                    console.log('[Quinny] Photo saved (resized)');
                                };
                                img.src = dataUrl;
                            } else {
                                localStorage.setItem('symphony_quinny_photo', dataUrl);
                                console.log('[Quinny] Photo saved directly');
                            }
                            if (typeof playRetroSuccess === 'function') playRetroSuccess();
                        } catch (err) {
                            console.error('[Quinny] Photo processing error:', err);
                            alert('Photo save failed: ' + err.message);
                        }
                    };
                    reader.onerror = function () {
                        console.error('[Quinny] FileReader error');
                        alert('Could not read the file. Try a different image.');
                    };
                    reader.readAsDataURL(file);
                } catch (err) {
                    console.error('[Quinny] Photo change handler error:', err);
                }
            });
        }

        // Birthday
        const bdayInput = document.getElementById('quinny-birthday-input');
        const bdaySave = document.getElementById('quinny-birthday-save');
        const ageDisplay = document.getElementById('quinny-age');

        function updateAge() {
            const data = getData();
            if (!data.birthday) {
                if (ageDisplay) ageDisplay.innerText = 'Set birthday below ↓';
                return;
            }
            if (bdayInput) bdayInput.value = data.birthday;
            const bday = new Date(data.birthday + 'T00:00:00');
            const now = new Date();
            let years = now.getFullYear() - bday.getFullYear();
            let months = now.getMonth() - bday.getMonth();
            if (months < 0) { years--; months += 12; }
            if (now.getDate() < bday.getDate()) months--;
            if (months < 0) { years--; months += 12; }
            const dogYears = years <= 2 ? years * 10.5 : 21 + (years - 2) * 4;
            if (ageDisplay) {
                ageDisplay.innerHTML = `🎂 ${years} year${years !== 1 ? 's' : ''}, ${months} month${months !== 1 ? 's' : ''} old <span style="color: var(--accent-yellow);">(~${Math.round(dogYears)} dog years)</span>`;
            }
        }

        if (bdaySave) {
            bdaySave.onclick = function () {
                console.log('[Quinny] Birthday save clicked');
                const val = bdayInput ? bdayInput.value : '';
                console.log('[Quinny] Birthday value:', val);
                if (!val) {
                    alert('Please select a date first.');
                    return;
                }
                const data = getData();
                data.birthday = val;
                saveData(data);
                console.log('[Quinny] Birthday saved:', JSON.stringify(data));
                updateAge();
                // Visual feedback
                bdaySave.innerText = '✅ Saved!';
                bdaySave.style.background = 'rgba(52,211,153,0.4)';
                setTimeout(function () { bdaySave.innerText = 'Save'; bdaySave.style.background = ''; }, 1500);
                if (typeof playRetroClick === 'function') playRetroClick();
            };
        } else {
            console.warn('[Quinny] Birthday save button NOT FOUND');
        }
        updateAge();

        // --- Knowledge Base ---
        const VACC_INFO = {
            'c3': { name: 'C3 (Core)', protects: 'Distemper, Hepatitis (Adenovirus), Parvovirus', schedule: 'Puppy: 6-8, 10-12, 14-16 weeks. Adult booster every 3 years.', note: 'Core vaccine — essential for all dogs in NZ.' },
            'c5': { name: 'C5 (Core + Kennel Cough)', protects: 'Distemper, Hepatitis, Parvovirus + Parainfluenza, Bordetella (Kennel Cough)', schedule: 'Puppy: 6-8, 10-12, 14-16 weeks. Kennel Cough component: annual booster.', note: 'Required for boarding, daycare, and grooming facilities.' },
            'c7': { name: 'C7 (Extended)', protects: 'Everything in C5 + Leptospirosis (2 strains)', schedule: 'Puppy series + annual Leptospirosis booster.', note: 'Recommended if your dog swims in rivers/ponds or lives rurally.' },
            'kennel cough': { name: 'Kennel Cough (Bordetella)', protects: 'Bordetella bronchiseptica + Parainfluenza — causes harsh dry cough', schedule: 'Annual booster (intranasal or injectable).', note: 'Highly contagious. Required before boarding.' },
            'leptospirosis': { name: 'Leptospirosis', protects: 'Bacterial infection from contaminated water/soil — can cause kidney/liver failure', schedule: 'Initial 2 doses 2-4 weeks apart, then annual booster.', note: 'Zoonotic — can spread to humans. Important in rural NZ.' },
            'rabies': { name: 'Rabies', protects: 'Rabies virus — fatal neurological disease', schedule: 'Required for international travel. Not endemic in NZ.', note: 'Only needed if travelling overseas with your dog.' },
            'parvovirus': { name: 'Parvovirus', protects: 'Canine Parvovirus — severe vomiting, bloody diarrhoea, often fatal in puppies', schedule: 'Part of C3/C5/C7. Puppy series critical.', note: 'Survives in soil for years. Unvaccinated puppies at extreme risk.' },
            'distemper': { name: 'Distemper', protects: 'Canine Distemper Virus — respiratory, GI, and neurological disease', schedule: 'Part of C3/C5/C7 core vaccines.', note: 'No cure once infected. Vaccination is the only protection.' },
            'hepatitis': { name: 'Hepatitis (Adenovirus)', protects: 'Infectious Canine Hepatitis — liver inflammation and failure', schedule: 'Part of C3/C5/C7 core vaccines.', note: 'Can cause "blue eye" (corneal edema) in recovered dogs.' }
        };

        const TREAT_INFO = {
            // Worming
            'drontal': { name: 'Drontal', type: 'worming', protects: 'Roundworm, Hookworm, Whipworm, Tapeworm (all major intestinal worms)', schedule: 'Every 3 months for adult dogs. Puppies: every 2 weeks until 12 weeks, then monthly until 6 months.', note: 'Broad-spectrum. Gold standard for intestinal worming.' },
            'milbemax': { name: 'Milbemax', type: 'worming', protects: 'Roundworm, Hookworm, Whipworm, Tapeworm + Heartworm prevention', schedule: 'Monthly for heartworm prevention, or every 3 months for intestinal worms only.', note: 'Also prevents heartworm — good dual-purpose option.' },
            'nexgard spectra': { name: 'NexGard Spectra', type: 'combo', protects: 'Fleas, Ticks, Mites + Roundworm, Hookworm, Whipworm, Heartworm', schedule: 'Monthly chewable tablet.', note: 'All-in-one flea, tick, and worming protection. Very popular in NZ.' },
            'paragard': { name: 'Paragard', type: 'worming', protects: 'Roundworm, Hookworm, Whipworm, Tapeworm', schedule: 'Every 3 months for adults.', note: 'Allwormer tablet — budget-friendly alternative to Drontal.' },
            // Flea/Tick
            'nexgard': { name: 'NexGard', type: 'flea', protects: 'Fleas (kills within 8 hours) + Ticks (including paralysis tick)', schedule: 'Monthly chewable tablet.', note: 'Beef-flavoured chew. Starts killing fleas within 8 hours.' },
            'bravecto': { name: 'Bravecto', type: 'flea', protects: 'Fleas + Ticks for up to 3 months per dose', schedule: 'Every 3 months (chew) or 6 months (spot-on).', note: 'Longest-lasting flea/tick protection available.' },
            'simparica': { name: 'Simparica', type: 'flea', protects: 'Fleas (kills within 3 hours) + Ticks + Mites (sarcoptic & demodectic mange)', schedule: 'Monthly chewable tablet.', note: 'Fastest flea kill speed of any oral product.' },
            'advantage': { name: 'Advantage', type: 'flea', protects: 'Fleas only (spot-on topical treatment)', schedule: 'Monthly spot-on application.', note: 'Topical — good for dogs who won\\\'t take chews. Avoid bathing 48hrs after.' },
            'frontline': { name: 'Frontline Plus', type: 'flea', protects: 'Fleas + Ticks + Lice (spot-on)', schedule: 'Monthly spot-on application.', note: 'Also kills flea eggs and larvae to break the lifecycle.' },
            'seresto': { name: 'Seresto Collar', type: 'flea', protects: 'Fleas + Ticks for up to 8 months', schedule: 'Replace collar every 8 months.', note: 'Continuous slow-release protection. Water-resistant.' },
            'revolution': { name: 'Revolution', type: 'flea', protects: 'Fleas, Heartworm, Ear mites, Sarcoptic mange, some ticks', schedule: 'Monthly spot-on.', note: 'Multi-parasite spot-on. Does NOT cover all tick species.' }
        };

        function matchVaccInfo(name) {
            const lower = name.toLowerCase();
            for (const [key, info] of Object.entries(VACC_INFO)) {
                if (lower.includes(key)) return info;
            }
            return null;
        }

        function matchTreatInfo(product, type) {
            const lower = (product || '').toLowerCase();
            for (const [key, info] of Object.entries(TREAT_INFO)) {
                if (lower.includes(key)) return info;
            }
            return null;
        }

        function infoBoxHtml(info) {
            if (!info) return '';
            return `
            <div style="margin: 0.3rem 0 0.5rem; padding: 0.5rem; background: rgba(59,130,246,0.08); border-left: 3px solid var(--accent-blue); font-size: 0.75rem; line-height: 1.4;">
                <div style="color: var(--accent-blue); font-weight: 700; margin-bottom: 0.2rem;">ℹ️ ${info.name}</div>
                <div><strong style="color: var(--text-secondary);">Protects against:</strong> <span style="color: var(--text-primary);">${info.protects}</span></div>
                <div style="margin-top: 0.15rem;"><strong style="color: var(--text-secondary);">Schedule:</strong> <span style="color: var(--text-primary);">${info.schedule}</span></div>
                ${info.note ? `<div style="margin-top: 0.15rem; color: var(--accent-yellow); font-style: italic;">💡 ${info.note}</div>` : ''}
            </div>`;
        }

        // Vaccinations
        const vaccList = document.getElementById('vacc-list');
        const vaccAddBtn = document.getElementById('vacc-add-btn');

        function renderVaccinations() {
            if (!vaccList) return;
            const data = getData();
            if (data.vaccinations.length === 0) {
                vaccList.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem;">No vaccinations recorded yet.</div>';
                return;
            }
            vaccList.innerHTML = data.vaccinations.map((v, i) => {
                const info = matchVaccInfo(v.name);
                return `
                <div style="padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.85rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: var(--text-primary);">${v.name}</strong>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Given: ${formatDate(v.dateGiven)}</div>
                            <div style="font-size: 0.75rem;">${v.nextDue ? dueBadge(v.nextDue) : '<span style="color: var(--text-secondary);">No follow-up set</span>'}</div>
                        </div>
                        <button class="vacc-del-btn" data-idx="${i}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                    </div>
                    ${infoBoxHtml(info)}
                </div>`;
            }).join('');

            vaccList.querySelectorAll('.vacc-del-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const data = getData();
                    data.vaccinations.splice(parseInt(btn.dataset.idx), 1);
                    saveData(data);
                    renderVaccinations();
                });
            });
        }

        if (vaccAddBtn) {
            vaccAddBtn.addEventListener('click', () => {
                const name = document.getElementById('vacc-name-input').value.trim();
                const dateGiven = document.getElementById('vacc-date-input').value;
                const nextDue = document.getElementById('vacc-next-input').value;
                if (!name) { alert('Please enter a vaccine name.'); return; }
                const data = getData();
                data.vaccinations.push({ name, dateGiven, nextDue });
                saveData(data);
                document.getElementById('vacc-name-input').value = '';
                document.getElementById('vacc-date-input').value = '';
                document.getElementById('vacc-next-input').value = '';
                renderVaccinations();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }
        renderVaccinations();

        // Treatments (Worming / Flea)
        const treatList = document.getElementById('treat-list');
        const treatAddBtn = document.getElementById('treat-add-btn');

        function renderTreatments() {
            if (!treatList) return;
            const data = getData();
            if (data.treatments.length === 0) {
                treatList.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem;">No treatments recorded yet.</div>';
                return;
            }
            treatList.innerHTML = data.treatments.map((t, i) => {
                const icon = t.type === 'worming' ? '🐛' : '🪲';
                const label = t.type === 'worming' ? 'Worming' : 'Flea/Tick';
                const info = matchTreatInfo(t.product, t.type);
                return `
                <div style="padding: 0.4rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.85rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: var(--text-primary);">${icon} ${t.product || label}</strong>
                            <span style="font-size: 0.7rem; color: var(--text-secondary); margin-left: 0.3rem;">${label}</span>
                            <div style="font-size: 0.75rem; color: var(--text-secondary);">Given: ${formatDate(t.dateGiven)}</div>
                            <div style="font-size: 0.75rem;">${t.nextDue ? dueBadge(t.nextDue) : '<span style="color: var(--text-secondary);">No follow-up set</span>'}</div>
                        </div>
                        <button class="treat-del-btn" data-idx="${i}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                    </div>
                    ${infoBoxHtml(info)}
                </div>`;
            }).join('');

            treatList.querySelectorAll('.treat-del-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const data = getData();
                    data.treatments.splice(parseInt(btn.dataset.idx), 1);
                    saveData(data);
                    renderTreatments();
                });
            });
        }

        if (treatAddBtn) {
            treatAddBtn.addEventListener('click', () => {
                const type = document.getElementById('treat-type-input').value;
                const product = document.getElementById('treat-product-input').value.trim();
                const dateGiven = document.getElementById('treat-date-input').value;
                const nextDue = document.getElementById('treat-next-input').value;
                const data = getData();
                data.treatments.push({ type, product, dateGiven, nextDue });
                saveData(data);
                document.getElementById('treat-product-input').value = '';
                document.getElementById('treat-date-input').value = '';
                document.getElementById('treat-next-input').value = '';
                renderTreatments();
                if (typeof playRetroSuccess === 'function') playRetroSuccess();
            });
        }
        renderTreatments();
    }
    initQuinnyPage();

    // --- Calendar Event System ---
    async function initCalendar() {
        let calEvents = [];
        let calViewMonth = new Date().getMonth();
        let calViewYear = new Date().getFullYear();

        const colorMap = {
            'RED': '#ff0000', 'ORANGE': '#ff8c00', 'GREEN': '#008000',
            'BLUE': '#0000ff', 'PURPLE': '#800080'
        };
        const categoryEmoji = {
            'birthday': '🎂', 'appointment': '📋', 'deadline': '⏰',
            'reminder': '🔔', 'other': '📌'
        };
        const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

        // Fetch events from Backend
        async function fetchEvents() {
            try {
                const resp = await apiFetch(`/events`, {
                    headers: { "Authorization": `Bearer ${API_TOKEN}` }
                });
                if (resp.ok) {
                    calEvents = await resp.json();
                    localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                    return;
                }
            } catch (e) {
                console.warn('Calendar: Backend unavailable, using localStorage', e);
            }
            const local = localStorage.getItem('symphony_events_local');
            calEvents = local ? JSON.parse(local) : [];
        }

        // Check if an event occurs on a given date (considering recurrence)
        function eventOccursOn(event, date) {
            const evDate = new Date(event.event_date + 'T00:00:00');
            const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());

            if (event.recurrence === 'once') {
                return evDate.getTime() === d.getTime();
            }
            if (event.recurrence === 'yearly') {
                return evDate.getMonth() === d.getMonth() && evDate.getDate() === d.getDate();
            }
            if (event.recurrence === 'monthly') {
                return evDate.getDate() === d.getDate() && d >= evDate;
            }
            if (event.recurrence === 'weekly') {
                return evDate.getDay() === d.getDay() && d >= evDate;
            }
            return false;
        }

        // Get events for a specific date
        function getEventsForDate(date) {
            return calEvents.filter(ev => eventOccursOn(ev, date));
        }

        // Render the week view (Mon-Sun of current week)
        function renderWeekView() {
            const container = document.getElementById('calendar-week-view');
            if (!container) return;

            const today = new Date();
            const dayOfWeek = today.getDay(); // 0=Sun, 1=Mon...
            const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
            const monday = new Date(today);
            monday.setDate(today.getDate() + mondayOffset);

            let html = '';
            for (let i = 0; i < 7; i++) {
                const d = new Date(monday);
                d.setDate(monday.getDate() + i);
                const isToday = d.toDateString() === today.toDateString();
                const eventsOnDay = getEventsForDate(d);

                html += `<div class="week-day-row ${isToday ? 'is-today' : ''}">
                    <div class="week-day-label">
                        ${dayNames[i]}
                        <span class="week-date">${d.getDate()}/${d.getMonth() + 1}</span>
                    </div>
                    <div style="flex: 1;">
                        ${eventsOnDay.length === 0
                        ? '<span style="color: #999; font-size: 0.85rem;">—</span>'
                        : eventsOnDay.map(ev =>
                            `<div class="week-event-item">
                                    <span class="cal-event-dot color-${ev.color}"></span>
                                    <span>${categoryEmoji[ev.category] || '📌'} ${ev.title}</span>
                                    ${ev.time_of_day ? `<span style="color:#666; font-size:0.8rem;">${ev.time_of_day}</span>` : ''}
                                    <span class="recurrence-badge">${ev.recurrence}</span>
                                </div>`
                        ).join('')
                    }
                    </div>
                </div>`;
            }
            container.innerHTML = html;
        }

        // Render the month calendar grid
        function renderMonthGrid() {
            const grid = document.getElementById('calendar-month-grid');
            const title = document.getElementById('calendar-month-title');
            if (!grid) return;

            if (title) title.textContent = `${monthNames[calViewMonth]} ${calViewYear}`;

            const today = new Date();
            const firstDay = new Date(calViewYear, calViewMonth, 1);
            const lastDay = new Date(calViewYear, calViewMonth + 1, 0);

            // Adjust so Monday = 0
            let startDow = firstDay.getDay() - 1;
            if (startDow < 0) startDow = 6;

            let html = '<div class="cal-grid">';
            // Header row
            dayNames.forEach(d => { html += `<div class="cal-header-cell">${d}</div>`; });

            // Previous month padding
            const prevMonthLast = new Date(calViewYear, calViewMonth, 0);
            for (let i = startDow - 1; i >= 0; i--) {
                const dayNum = prevMonthLast.getDate() - i;
                html += `<div class="cal-day other-month"><span class="cal-day-num">${dayNum}</span></div>`;
            }

            // Current month days
            for (let day = 1; day <= lastDay.getDate(); day++) {
                const d = new Date(calViewYear, calViewMonth, day);
                const isToday = d.toDateString() === today.toDateString();
                const eventsOnDay = getEventsForDate(d);

                html += `<div class="cal-day ${isToday ? 'today' : ''}">
                    <span class="cal-day-num">${day}</span>
                    <div>${eventsOnDay.map(ev =>
                    `<span class="cal-event-dot color-${ev.color}" title="${ev.title}"></span>`
                ).join('')}</div>
                </div>`;
            }

            // Next month padding (fill to 42 cells = 6 rows)
            const totalCells = startDow + lastDay.getDate();
            const remaining = (7 - (totalCells % 7)) % 7;
            for (let i = 1; i <= remaining; i++) {
                html += `<div class="cal-day other-month"><span class="cal-day-num">${i}</span></div>`;
            }

            html += '</div>';
            grid.innerHTML = html;
        }

        // Render all events list (editable)
        function renderAllEventsList() {
            const list = document.getElementById('all-events-list');
            if (!list) return;

            if (calEvents.length === 0) {
                list.innerHTML = '<div style="color: #808080; font-style: italic; padding: 0.5rem;">No events yet. Add one above!</div>';
                return;
            }

            list.innerHTML = calEvents.map(ev => {
                const dateStr = new Date(ev.event_date + 'T00:00:00').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
                return `<div class="event-list-item">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span class="cal-event-dot color-${ev.color}" style="width:8px;height:8px;"></span>
                        <span>${categoryEmoji[ev.category] || '📌'} <strong>${ev.title}</strong></span>
                        <span class="recurrence-badge">${ev.recurrence}</span>
                        <span style="color: #666;">${dateStr}</span>
                        ${ev.time_of_day ? `<span style="color: #0000ff;">${ev.time_of_day}</span>` : ''}
                    </div>
                    <button class="event-delete-btn" data-event-id="${ev.id}">×</button>
                </div>`;
            }).join('');

            // Attach delete handlers
            list.querySelectorAll('.event-delete-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.dataset.eventId;
                    calEvents = calEvents.filter(e => e.id !== id);
                    localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                    renderAll();
                    try {
                        await apiFetch(`/events/${id}`, {
                            method: "DELETE",
                            headers: { "Authorization": `Bearer ${API_TOKEN}` }
                        });
                    } catch (e) { console.warn('Failed to delete event from Backend:', e); }
                });
            });
        }

        // Render "Coming Up This Week" on Today's Schedule
        function renderComingUpThisWeek() {
            const container = document.getElementById('coming-up-this-week');
            if (!container) return;

            const today = new Date();
            const dayOfWeek = today.getDay();
            const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
            const monday = new Date(today);
            monday.setDate(today.getDate() + mondayOffset);
            const sunday = new Date(monday);
            sunday.setDate(monday.getDate() + 6);

            // Collect events for this week
            const weekEvents = [];
            for (let i = 0; i < 7; i++) {
                const d = new Date(monday);
                d.setDate(monday.getDate() + i);
                const evs = getEventsForDate(d);
                evs.forEach(ev => {
                    weekEvents.push({ ...ev, displayDate: new Date(d) });
                });
            }

            if (weekEvents.length === 0) {
                container.innerHTML = '<div style="color: #008000; font-size: 0.95rem;">✅ No events this week — smooth sailing!</div>';
                return;
            }

            container.innerHTML = weekEvents.map(ev => {
                const dName = dayNames[(ev.displayDate.getDay() + 6) % 7]; // Mon=0
                const isPast = ev.displayDate < today && ev.displayDate.toDateString() !== today.toDateString();
                return `<div class="coming-up-event" style="border-left: 4px solid ${colorMap[ev.color] || '#0000ff'}; ${isPast ? 'opacity: 0.5;' : ''}">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span style="font-weight: bold; color: #000080; min-width: 30px;">${dName}</span>
                        <span>${categoryEmoji[ev.category] || '📌'} ${ev.title}</span>
                        ${ev.time_of_day ? `<span style="color: #0000ff; font-size: 0.85rem;">${ev.time_of_day}</span>` : ''}
                        <span class="recurrence-badge">${ev.recurrence}</span>
                    </div>
                </div>`;
            }).join('');
        }

        function renderAll() {
            renderWeekView();
            renderMonthGrid();
            renderAllEventsList();
            renderComingUpThisWeek();
        }

        // Add event handler
        const addBtn = document.getElementById('add-event-btn');
        if (addBtn) {
            addBtn.addEventListener('click', async () => {
                const title = document.getElementById('event-title')?.value.trim();
                const eventDate = document.getElementById('event-date')?.value;
                const timeOfDay = document.getElementById('event-time')?.value || null;
                const recurrence = document.getElementById('event-recurrence')?.value || 'once';
                const color = document.getElementById('event-color')?.value || 'BLUE';
                const category = document.getElementById('event-category')?.value || 'other';

                if (!title || !eventDate) {
                    alert('Please enter a title and date.');
                    return;
                }

                addBtn.innerText = '⏳';
                addBtn.style.pointerEvents = 'none';

                const newEvent = {
                    id: crypto.randomUUID(),
                    title, event_date: eventDate, recurrence, color, category,
                    time_of_day: timeOfDay || null
                };

                calEvents.push(newEvent);
                localStorage.setItem('symphony_events_local', JSON.stringify(calEvents));
                renderAll();

                // Clear form
                document.getElementById('event-title').value = '';
                document.getElementById('event-date').value = '';
                document.getElementById('event-time').value = '';

                try {
                    await apiFetch(`/events`, {
                        method: "POST",
                        headers: {
                            "Authorization": `Bearer ${API_TOKEN}`,
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            id: newEvent.id, title, event_date: eventDate,
                            recurrence, color, category,
                            time_of_day: timeOfDay || null
                        })
                    });
                } catch (e) { console.warn('Failed to save event to Backend:', e); }

                addBtn.innerText = 'Add Event';
                addBtn.style.pointerEvents = 'auto';
            });
        }

        // Month navigation
        const prevBtn = document.getElementById('cal-prev-month');
        const nextBtn = document.getElementById('cal-next-month');
        if (prevBtn) prevBtn.addEventListener('click', () => {
            calViewMonth--;
            if (calViewMonth < 0) { calViewMonth = 11; calViewYear--; }
            renderMonthGrid();
        });
        if (nextBtn) nextBtn.addEventListener('click', () => {
            calViewMonth++;
            if (calViewMonth > 11) { calViewMonth = 0; calViewYear++; }
            renderMonthGrid();
        });

        // Initial load
        await fetchEvents();
        renderAll();
    }
    initCalendar();

    async function initExpensesTracker() {
        const listEl = document.getElementById('expenses-list');
        const addBtn = document.getElementById('add-expense-btn');
        if (!listEl || !addBtn) return;

        let expenses = [];
        const LOCAL_KEY = 'symphony_expenses_local';

        // Normalize any frequency to weekly amount
        function toWeekly(amount, frequency) {
            switch (frequency) {
                case 'weekly': return amount;
                case 'fortnightly': return amount / 2;
                case 'monthly': return (amount * 12) / 52;
                case 'yearly': return amount / 52;
                default: return amount;
            }
        }

        function freqLabel(f) {
            return { weekly: '/wk', fortnightly: '/fn', monthly: '/mo', yearly: '/yr' }[f] || '';
        }

        // Fetch from Backend
        async function fetchExpenses() {
            try {
                const resp = await apiFetch(`/expenses`, {
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`
                    }
                });
                if (resp.ok) {
                    const apiData = await resp.json();
                    const localData = localStorage.getItem(LOCAL_KEY);
                    const localItems = localData ? JSON.parse(localData) : [];

                    if (apiData.length > 0) {
                        // Backend has data — use it as source of truth
                        expenses = apiData;
                        localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
                    } else if (localItems.length > 0) {
                        // Backend is empty but localStorage has items — sync UP
                        expenses = localItems;
                        console.info('Expenses: Backend empty, syncing local items up...');
                        for (const item of localItems) {
                            if (!item.id) {
                                try {
                                    await apiFetch(`/expenses`, {
                                        method: 'POST',
                                        headers: {
                                            'Authorization': `Bearer ${API_TOKEN}`,
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({ name: item.name, amount: item.amount, frequency: item.frequency, category: item.category })
                                    });
                                } catch (e) { /* best-effort sync */ }
                            }
                        }
                    } else {
                        expenses = [];
                    }
                } else {
                    throw new Error(`HTTP ${resp.status}`);
                }
            } catch (e) {
                console.warn('Expenses: Backend fetch failed, using localStorage:', e);
                const local = localStorage.getItem(LOCAL_KEY);
                if (local) expenses = JSON.parse(local);
            }
        }

        function renderExpenses() {
            listEl.innerHTML = '';
            if (expenses.length === 0) {
                listEl.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.85rem; padding: 0.5rem 0;">No expenses added yet. Add your bills above.</div>';
                updateBudgetSummary();
                return;
            }

            // Group by category
            const essential = expenses.filter(e => e.category === 'essential');
            const flexible = expenses.filter(e => e.category === 'flexible');

            const renderGroup = (items, label, color) => {
                if (items.length === 0) return;
                const header = document.createElement('div');
                header.style.cssText = `font-size: 0.75rem; color: ${color}; text-transform: uppercase; font-weight: 700; padding: 0.25rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); margin-bottom: 0.25rem;`;
                header.textContent = label;
                listEl.appendChild(header);

                items.forEach(exp => {
                    const weeklyAmt = toWeekly(parseFloat(exp.amount), exp.frequency);
                    const row = document.createElement('div');
                    row.style.cssText = 'display: flex; justify-content: space-between; align-items: center; padding: 0.3rem 0; border-bottom: 1px dotted rgba(255,255,255,0.05); font-size: 0.85rem;';
                    row.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: var(--text-primary);">${exp.name}</span>
                            <span style="font-size: 0.7rem; color: var(--text-secondary);">$${parseFloat(exp.amount).toFixed(2)}${freqLabel(exp.frequency)}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span style="color: ${color}; font-weight: 600;">$${weeklyAmt.toFixed(2)}/wk</span>
                            <button class="delete-expense-btn" data-id="${exp.id}" style="background: none; border: none; color: #ff0000; cursor: pointer; font-size: 1.1rem;" title="Delete">×</button>
                        </div>
                    `;
                    listEl.appendChild(row);
                });
            };

            renderGroup(essential, '🛡️ Essential', '#ef4444');
            renderGroup(flexible, '🎮 Flexible', 'var(--accent-yellow)');

            // Bind delete buttons
            listEl.querySelectorAll('.delete-expense-btn').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const id = btn.getAttribute('data-id');
                    expenses = expenses.filter(e => e.id !== id);
                    localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
                    renderExpenses();
                    // Delete from Backend
                    try {
                        await apiFetch(`/expenses/${id}`, {
                            method: 'DELETE',
                            headers: {
                                'Authorization': `Bearer ${API_TOKEN}`
                            }
                        });
                    } catch (e) { console.warn('Failed to delete expense from Backend:', e); }
                    if (typeof playRetroClick === 'function') playRetroClick();
                });
            });

            updateBudgetSummary();
        }

        function updateBudgetSummary() {
            const netPay = window.currentNetWeekly || 0;
            const formatCurrency = (num) => '$' + Math.abs(num).toFixed(2);

            let essentialTotal = 0;
            let flexibleTotal = 0;
            expenses.forEach(exp => {
                const weekly = toWeekly(parseFloat(exp.amount), exp.frequency);
                if (exp.category === 'essential') essentialTotal += weekly;
                else flexibleTotal += weekly;
            });

            const totalExpenses = essentialTotal + flexibleTotal;
            const disposable = netPay - totalExpenses;

            const netPayEl = document.getElementById('budget-net-pay');
            const essentialEl = document.getElementById('budget-essential-total');
            const flexibleEl = document.getElementById('budget-flexible-total');
            const totalEl = document.getElementById('budget-expenses-total');
            const disposableEl = document.getElementById('budget-disposable');
            const dailyEl = document.getElementById('budget-disposable-daily');

            if (netPayEl) netPayEl.innerText = formatCurrency(netPay);
            if (essentialEl) essentialEl.innerText = '-' + formatCurrency(essentialTotal);
            if (flexibleEl) flexibleEl.innerText = '-' + formatCurrency(flexibleTotal);
            if (totalEl) totalEl.innerText = '-' + formatCurrency(totalExpenses);

            if (disposableEl) {
                disposableEl.innerText = (disposable >= 0 ? '$' : '-$') + Math.abs(disposable).toFixed(2);
                disposableEl.style.color = disposable >= 0 ? 'var(--accent-green)' : 'var(--accent-red)';
            }
            if (dailyEl) {
                const daily = disposable / 7;
                dailyEl.innerText = `(${daily >= 0 ? '$' : '-$'}${Math.abs(daily).toFixed(2)} / day)`;
            }

            // Max Savings Potential (essentials-only baseline)
            const baselineNetWeekly = computeNZNetWeekly(24.00 * 28.5).netWeekly;
            const maxSavingsWeekly = baselineNetWeekly - essentialTotal;
            const maxSavingsYearly = maxSavingsWeekly * 52;

            const maxSavingsEl = document.getElementById('budget-max-savings');
            const maxSavingsWeeklyEl = document.getElementById('budget-max-savings-weekly');
            if (maxSavingsEl) {
                maxSavingsEl.innerText = (maxSavingsYearly >= 0 ? '$' : '-$') + Math.abs(Math.round(maxSavingsYearly)).toLocaleString();
                maxSavingsEl.style.color = maxSavingsYearly >= 0 ? 'var(--accent-blue)' : 'var(--accent-red)';
            }
            if (maxSavingsWeeklyEl) {
                maxSavingsWeeklyEl.innerText = `($${maxSavingsWeekly.toFixed(2)} / week)`;
            }

            const canvas = document.getElementById('budgetPieChart');
            if (canvas && typeof Chart !== 'undefined' && (essentialTotal + flexibleTotal + Math.max(0, disposable)) > 0) {
                const ctx = canvas.getContext('2d');
                if (window.budgetChartInstance) window.budgetChartInstance.destroy();
                window.budgetChartInstance = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Disposable', 'Essential', 'Flexible'],
                        datasets: [{
                            data: [Math.max(0, disposable), essentialTotal, flexibleTotal],
                            backgroundColor: [
                                'rgba(52, 211, 153, 0.8)',
                                'rgba(239, 68, 68, 0.8)',
                                'rgba(251, 191, 36, 0.8)'
                            ],
                            borderColor: 'rgba(15, 23, 42, 1)',
                            borderWidth: 2,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: { color: '#94a3b8', font: { size: 11 } }
                            }
                        },
                        cutout: '65%'
                    }
                });
            }
        }

        // Expose globally so calculateFinance can trigger it
        window.updateBudgetSummary = updateBudgetSummary;

        // Add expense handler
        addBtn.addEventListener('click', async () => {
            const nameEl = document.getElementById('expense-name-input');
            const amountEl = document.getElementById('expense-amount-input');
            const freqEl = document.getElementById('expense-freq-input');
            const catEl = document.getElementById('expense-cat-input');

            const name = nameEl.value.trim();
            const amount = parseFloat(amountEl.value);
            const frequency = freqEl.value;
            const category = catEl.value;

            if (!name || isNaN(amount) || amount <= 0) {
                alert('Please fill out expense name and a valid amount.');
                return;
            }

            const newExpense = { name, amount, frequency, category };

            // Optimistic local add
            expenses.push(newExpense);
            localStorage.setItem(LOCAL_KEY, JSON.stringify(expenses));
            renderExpenses();

            nameEl.value = '';
            amountEl.value = '';

            // Persist to Backend
            try {
                const resp = await apiFetch(`/expenses`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${API_TOKEN}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(newExpense)
                });
                if (resp.ok) {
                    await fetchExpenses();
                    renderExpenses();
                }
            } catch (e) {
                console.warn('Failed to save expense to Backend:', e);
            }

            if (typeof playRetroSuccess === 'function') playRetroSuccess();
        });

        // Init
        await fetchExpenses();
        renderExpenses();
    }

    initExpensesTracker();

    // --- Pulse Overview (At-a-Glance Command Center) ---
    function initPulse() {
        const pulseToday = document.getElementById('pulse-today-summary');
        const pulseLogistics = document.getElementById('pulse-logistics');
        const pulseSupps = document.getElementById('pulse-supps');
        const pulseMedical = document.getElementById('pulse-medical');
        const pulseFinance = document.getElementById('pulse-finance');
        if (!pulseToday) return;

        // 1. Today's progress — count checked items in the schedule
        try {
            const allCheckboxes = document.querySelectorAll('#today .task-list .checkbox, .supp-timing-body .checkbox');
            const checked = document.querySelectorAll('#today .task-list .checkbox.checked, .supp-timing-body .checkbox.checked');
            const totalTasks = allCheckboxes.length;
            const completedTasks = checked.length;
            const pct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

            pulseToday.innerHTML = `
                <div style="font-size: 2rem; font-weight: 700; color: var(--accent-green); margin-bottom: 0.25rem;">${pct}%</div>
                <div>${completedTasks} of ${totalTasks} tasks completed today</div>
                <div style="width: 100%; height: 6px; background: rgba(0,0,0,0.4); border-radius: 3px; margin-top: 0.5rem; overflow: hidden;">
                    <div style="height: 100%; width: ${pct}%; background: var(--accent-green); transition: width 0.3s;"></div>
                </div>`;
        } catch (e) {
            pulseToday.innerHTML = '<div>Open Today\\\'s Schedule to see progress.</div>';
        }

        // 2. Open Logistics
        try {
            const logisticsLocal = localStorage.getItem('symphony_logistics_local');
            const logItems = logisticsLocal ? JSON.parse(logisticsLocal) : [];
            if (logItems.length === 0) {
                pulseLogistics.innerHTML = '<div style="color: var(--accent-green);">✅ Nothing to solve right now!</div>';
            } else {
                pulseLogistics.innerHTML = logItems.map(item => {
                    const stCount = item.subtasks ? item.subtasks.length : 0;
                    const stDone = item.subtasks ? item.subtasks.filter(s => s.completed).length : 0;
                    const badge = stCount > 0 ? ` <span style="color: var(--text-secondary); font-size: 0.75rem;">(${stDone}/${stCount} steps)</span>` : '';
                    return `<div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        🔧 ${escapeHTML(item.title)}${badge}
                    </div>`;
                }).join('');
            }
        } catch (e) {
            pulseLogistics.innerHTML = '<div>Could not load logistics.</div>';
        }

        // 3. Daily Supplements Progress
        try {
            const dailyPulseSupps = document.getElementById('pulse-supps-daily');
            if (dailyPulseSupps) {
                const todayStr = getLocalDateString(new Date());
                const keys = [
                    `symphony_list_state_${todayStr}_supp-am-empty-body`,
                    `symphony_list_state_${todayStr}_supp-am-food-body`,
                    `symphony_list_state_${todayStr}_supp-pm-dinner-body`,
                    `symphony_list_state_${todayStr}_supp-pm-bed-body`
                ];

                // Hardcoded supplement counts for each bucket based on the arrays in `renderSupplements`
                const expectedCounts = [1, 6, 1, 1];
                let totalSupps = 0;
                let completedSupps = 0;

                keys.forEach((key, index) => {
                    totalSupps += expectedCounts[index];
                    const state = JSON.parse(localStorage.getItem(key) || '{}');
                    // state is an object: { "0": true, "1": false, ... }
                    completedSupps += Object.values(state).filter(val => val === true).length;
                });

                const pct = totalSupps > 0 ? Math.round((completedSupps / totalSupps) * 100) : 0;
                let statusColor = 'var(--accent-red)';
                if (pct === 100) statusColor = 'var(--accent-green)';
                else if (pct >= 50) statusColor = 'var(--accent-yellow)';

                dailyPulseSupps.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span>Protocol Adherence:</span>
                        <span style="color: ${statusColor};">${completedSupps}/${totalSupps} (${pct}%)</span>
                    </div>
                `;
            }
        } catch (e) {
            const dailyPulseSupps = document.getElementById('pulse-supps-daily');
            if (dailyPulseSupps) dailyPulseSupps.innerHTML = '<div>Could not load daily supp status.</div>';
        }

        // 4. Low Stock Supplements
        try {
            const suppLocal = localStorage.getItem('symphony_supp_inventory_local');
            const supps = suppLocal ? JSON.parse(suppLocal) : [];
            const lowStock = supps.filter(s => s.daily_dose > 0 && (s.current_stock / s.total_capacity) < 0.5);

            if (lowStock.length === 0 && supps.length > 0) {
                pulseSupps.innerHTML = '<div style="color: var(--accent-green);">✅ All supplements well-stocked.</div>';
            } else if (supps.length === 0) {
                pulseSupps.innerHTML = '<div>No supplements tracked yet. Add them in the Supps Vault.</div>';
            } else {
                pulseSupps.innerHTML = lowStock.map(s => {
                    const daysLeft = s.daily_dose > 0 ? Math.floor(s.current_stock / s.daily_dose) : '∞';
                    const pct = Math.round((s.current_stock / s.total_capacity) * 100);
                    const color = pct < 25 ? 'var(--accent-red)' : 'var(--accent-yellow)';
                    return `<div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
                        <span style="color: ${color};">⚠️ ${escapeHTML(s.name)}</span>
                        <span>${s.current_stock}/${s.total_capacity} (${daysLeft} days left)</span>
                    </div>`;
                }).join('');
            }
        } catch (e) {
            pulseSupps.innerHTML = '<div>Could not load supplement data.</div>';
        }

        // 4. Medical Flags (from static MEDICAL_ALERTS)
        try {
            pulseMedical.innerHTML = MEDICAL_ALERTS.map(alert => `
                <div style="padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <span style="color: var(--accent-red); font-weight: 600;">${alert.gene}</span>
                    <span style="color: var(--text-secondary); font-size: 0.8rem;"> — ${alert.risk}</span>
                </div>
            `).join('');
        } catch (e) {
            pulseMedical.innerHTML = '<div>No medical flags loaded.</div>';
        }

        // 5. Financial Snapshot — use computed values directly, not DOM text
        try {
            const netWeekly = window.currentNetWeekly || 0;
            const hoursVal = document.getElementById('input-hours');
            const hours = hoursVal ? (parseFloat(hoursVal.value) || 28.5) : 28.5;
            const hourlyRate = 24.00;
            const grossWeekly = hourlyRate * hours;
            const formatCurrency = (num) => '$' + num.toFixed(2);

            if (netWeekly > 0) {
                pulseFinance.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <span>Est. Weekly Net:</span>
                        <span style="font-size: 1.5rem; font-weight: 700; color: var(--accent-green);">${formatCurrency(netWeekly)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.25rem;">
                        <span>Gross:</span><span>${formatCurrency(grossWeekly)}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 0.25rem;">
                        <span>Hours:</span><span>${hours} hrs</span>
                    </div>`;
            } else {
                pulseFinance.innerHTML = '<div>Open the Finances tab to calculate.</div>';
            }
        } catch (e) {
            pulseFinance.innerHTML = '<div>Could not load financial data.</div>';
        }
    }

    // --- Morning Read (Read First Thing Every Morning) ---
    (function initMorningRead() {
        const MORNING_KEY = 'symphony_morning_read';
        const display = document.getElementById('morning-read-display');
        const editor = document.getElementById('morning-read-editor');
        const editBtn = document.getElementById('morning-read-edit-btn');
        const saveBtn = document.getElementById('morning-read-save-btn');
        if (!display || !editor) return;

        // Load saved text
        const saved = localStorage.getItem(MORNING_KEY);
        if (saved) display.innerText = saved;

        function showEditor() {
            editor.value = localStorage.getItem(MORNING_KEY) || '';
            display.style.display = 'none';
            editor.style.display = 'block';
            editBtn.style.display = 'none';
            saveBtn.style.display = 'inline-block';
            editor.focus();
        }

        // Live auto-save to prevent data loss if crash occurs before clicking 'Save'
        editor.addEventListener('input', () => {
            localStorage.setItem(MORNING_KEY, editor.value);
            display.innerText = editor.value || 'Click here to write your morning intentions...';
        });

        function saveAndClose() {
            const text = editor.value.trim();
            if (text) {
                localStorage.setItem(MORNING_KEY, text);
                display.innerText = text;
            } else {
                localStorage.removeItem(MORNING_KEY);
                display.innerText = 'Click here to write your morning intentions...';
            }
            editor.style.display = 'none';
            display.style.display = 'block';
            saveBtn.style.display = 'none';
            editBtn.style.display = 'inline-block';
            if (typeof playRetroSuccess === 'function') playRetroSuccess();
        }

        display.addEventListener('click', showEditor);
        editBtn.addEventListener('click', showEditor);
        saveBtn.addEventListener('click', saveAndClose);
    })();

    // Run Pulse after a reasonable delay so async modules (calendar, logistics, supps) populate first.
    // Also expose initPulse globally so other modules can trigger a refresh.
    window.refreshPulse = initPulse;
    setTimeout(initPulse, 3000);

    // --- Dynamic Task Config Lock In ---
    const lockInBtn = document.getElementById('lock-in-config-btn');
    if (lockInBtn) {
        lockInBtn.addEventListener('click', async () => {
            lockInBtn.innerHTML = '<span class="icon">⏳</span> Locking...';
            lockInBtn.style.pointerEvents = 'none';

            // Re-render the configurator to move items to their new lists
            await initTaskConfigurator();
            if (typeof fetchLocalAPIData === 'function') {
                await fetchLocalAPIData();
            }

            lockInBtn.innerHTML = '<span class="icon">🔒</span> Lock In';
            lockInBtn.style.pointerEvents = 'auto';
        });
    }


});


// ============================================================
// PLANNER ENGINE v2 — Named Blocks + Recurring Tasks + Yearly
// ============================================================
(function initPlannerV2() {
    'use strict';

function escapeHTML(str) {
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


    // ── Constants ──────────────────────────────────────────
    const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const DAYS_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const BLOCK_COLOURS = [
        { name: 'Coral', bg: 'rgba(239,68,68,0.22)', border: '#ef4444', dot: '#ef4444' },
        { name: 'Orange', bg: 'rgba(249,115,22,0.22)', border: '#f97316', dot: '#f97316' },
        { name: 'Amber', bg: 'rgba(245,158,11,0.22)', border: '#f59e0b', dot: '#f59e0b' },
        { name: 'Green', bg: 'rgba(52,211,153,0.22)', border: '#34d399', dot: '#34d399' },
        { name: 'Sky', bg: 'rgba(56,189,248,0.22)', border: '#38bdf8', dot: '#38bdf8' },
        { name: 'Blue', bg: 'rgba(96,165,250,0.22)', border: '#60a5fa', dot: '#60a5fa' },
        { name: 'Violet', bg: 'rgba(167,139,250,0.22)', border: '#a78bfa', dot: '#a78bfa' },
        { name: 'Pink', bg: 'rgba(244,114,182,0.22)', border: '#f472b6', dot: '#f472b6' },
    ];
    const FREE_COLOUR = { bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.12)', dot: 'rgba(255,255,255,0.3)' };
    const EVENT_COLOURS = ['#f472b6', '#60a5fa', '#34d399', '#f97316', '#a78bfa', '#facc15', '#22d3ee', '#ef4444'];
    const DUE_DAYS = DAYS;

    // ── Storage helpers ────────────────────────────────────
    const LS_TEMPLATES = 'symphony_templates_v1';
    const LS_RECURRING = 'symphony_recurring_v1';
    const LS_EVENTS = 'symphony_yearly_events_v1';
    const LS_TODAY_EXTRAS = 'symphony_today_extras_v1';
    function loadTodayExtras() { try { return JSON.parse(localStorage.getItem(LS_TODAY_EXTRAS) || '{}'); } catch { return {}; } }
    function saveTodayExtras(patch) { localStorage.setItem(LS_TODAY_EXTRAS, JSON.stringify({ ...loadTodayExtras(), ...patch })); }

    function loadTemplates() { try { return JSON.parse(localStorage.getItem(LS_TEMPLATES) || '{}'); } catch { return {}; } }
    function saveTemplates(d) { localStorage.setItem(LS_TEMPLATES, JSON.stringify(d)); }
    function loadRecurring() { try { return JSON.parse(localStorage.getItem(LS_RECURRING) || '[]'); } catch { return []; } }
    function saveRecurring(d) { localStorage.setItem(LS_RECURRING, JSON.stringify(d)); }
    function loadEvents() { try { return JSON.parse(localStorage.getItem(LS_EVENTS) || '[]'); } catch { return []; } }
    function saveEvents(d) { localStorage.setItem(LS_EVENTS, JSON.stringify(d)); }

    // ── Date utils ─────────────────────────────────────────
    function localDateStr(dt) {
        return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
    }
    function daysSince(dateStr) {
        if (!dateStr) return null;
        const diff = Date.now() - new Date(dateStr + 'T00:00:00').getTime();
        return Math.floor(diff / 86400000);
    }
    function friendlyDate(dateStr) {
        if (!dateStr) return '—';
        const d = new Date(dateStr + 'T00:00:00');
        return `${DAYS_SHORT[d.getDay() === 0 ? 6 : d.getDay() - 1]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
    }
    function todayDowName() {
        const dow = new Date().getDay();
        return DAYS[dow === 0 ? 6 : dow - 1];
    }

    // ── Planner view state ─────────────────────────────────
    let plannerSection = 'template';
    let yearlyYear = new Date().getFullYear();

    // ── Modal state ────────────────────────────────────────
    let blockModal = { day: null, blockId: null };
    let eventModal = { dateStr: null, eventId: null };
    let selectedBlockColour = 0;
    let selectedEventColour = EVENT_COLOURS[0];

    // ── Colour swatches ────────────────────────────────────
    function renderColourPicker(containerId, colours, selectedIdx, onSelect) {
        const el = document.getElementById(containerId);
        if (!el) return;
        el.innerHTML = '';
        colours.forEach((c, i) => {
            const swatch = document.createElement('div');
            const bg = typeof c === 'string' ? c : c.border;
            swatch.style.cssText = `width:22px;height:22px;border-radius:50%;background:${bg};cursor:pointer;border:2px solid ${i === selectedIdx ? '#fff' : 'transparent'};transition:border 0.15s;`;
            swatch.title = typeof c === 'string' ? c : c.name;
            swatch.addEventListener('click', () => { onSelect(i); renderColourPicker(containerId, colours, i, onSelect); });
            el.appendChild(swatch);
        });
    }

    // ─────────────────────────────────────────────────────
    // TEMPLATE EDITOR
    // ─────────────────────────────────────────────────────
    function renderTemplateEditor() {
        const container = document.getElementById('planner-template-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayDay = todayDowName();

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">📋 WEEKLY TEMPLATE</div>`;

        DAYS.forEach(day => {
            const blocks = (templates[day] || []).slice().sort((a, b) => a.start.localeCompare(b.start));
            const isToday = day === todayDay;

            html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; min-height:42px;">`;
            // Day label
            html += `<div style="width:96px; min-width:96px; font-weight:bold; font-size:0.95rem; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'}; border-left:3px solid ${isToday ? 'var(--accent-green)' : 'rgba(255,255,255,0.15)'}; padding-left:8px;">${day}</div>`;

            // Block strip
            html += `<div style="flex:1; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">`;

            if (blocks.length === 0) {
                html += `<div style="background:${FREE_COLOUR.bg}; border:1px dashed ${FREE_COLOUR.border}; border-radius:16px; padding:6px 14px; font-size:0.82rem; color:rgba(255,255,255,0.35); cursor:pointer; user-select:none;" data-add-block="${day}">🕓 Free all day — click to add block</div>`;
            } else {
                // Render each block as a pill
                blocks.forEach(b => {
                    const ci = typeof b.colour === 'number' ? b.colour : 0;
                    const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                    const duration = calcDuration(b.start, b.end);
                    html += `<div class="template-block" data-day="${day}" data-bid="${b.id}" style="background:${c.bg}; border:1px solid ${c.border}; border-radius:16px; padding:6px 14px; font-size:0.85rem; cursor:pointer; user-select:none; display:flex; align-items:center; gap:6px; transition:opacity 0.15s; white-space:nowrap;">`;
                    html += `<span style="width:8px;height:8px;border-radius:50%;background:${c.dot};display:inline-block;flex-shrink:0;"></span>`;
                    html += `<span style="font-weight:bold;">${b.label}</span>`;
                    html += `<span style="opacity:0.6; font-size:0.78rem;">${b.start}–${b.end}${duration ? ' · ' + duration : ''}</span>`;
                    html += `</div>`;
                });
                // Add block button
                html += `<button data-add-block="${day}" style="background:rgba(52,211,153,0.1); border:1px dashed var(--accent-green); color:var(--accent-green); border-radius:16px; padding:5px 12px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">+ block</button>`;
                // Copy to button + inline picker
                html += `<button class="copy-day-btn" data-day="${day}" style="background:rgba(56,189,248,0.1); border:1px dashed var(--accent-blue,#38bdf8); color:var(--accent-blue,#38bdf8); border-radius:16px; padding:5px 12px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">📋 Copy →</button>`;
                html += `<div class="copy-picker" data-from="${day}" style="display:none; flex-wrap:wrap; gap:4px; align-items:center;">`;
                DAYS.forEach(td => {
                    if (td !== day) html += `<button class="copy-to-btn" data-from="${day}" data-to="${td}" style="background:rgba(56,189,248,0.12); border:1px solid rgba(56,189,248,0.4); color:#38bdf8; border-radius:12px; padding:3px 10px; font-family:'VT323',monospace; font-size:0.78rem; cursor:pointer;">${td.slice(0, 3)}</button>`;
                });
                html += `<button class="copy-to-btn" data-from="${day}" data-to="ALL" style="background:rgba(56,189,248,0.25); border:1px solid #38bdf8; color:#38bdf8; border-radius:12px; padding:3px 10px; font-family:'VT323',monospace; font-size:0.78rem; cursor:pointer; font-weight:bold;">All days</button>`;
                html += `</div>`;
            }

            html += `</div></div>`;

            // Subtle separator
            if (day !== 'Sunday') {
                html += `<div style="height:1px; background:rgba(255,255,255,0.06); margin:0 0 0 104px; margin-bottom:2px;"></div>`;
            }
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire block clicks (edit)
        container.querySelectorAll('.template-block').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.day, el.dataset.bid));
        });
        // Wire add buttons
        container.querySelectorAll('[data-add-block]').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.addBlock, null));
        });
        // Wire copy buttons
        container.querySelectorAll('.copy-day-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                const picker = container.querySelector(`.copy-picker[data-from="${btn.dataset.day}"]`);
                if (picker) picker.style.display = picker.style.display === 'none' ? 'flex' : 'none';
            });
        });
        container.querySelectorAll('.copy-to-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                copyDayTemplate(btn.dataset.from, btn.dataset.to);
            });
        });
    }

    function calcDuration(start, end) {
        if (!start || !end) return '';
        const [sh, sm] = start.split(':').map(Number);
        const [eh, em] = end.split(':').map(Number);
        const mins = (eh * 60 + em) - (sh * 60 + sm);
        if (mins <= 0) return '';
        if (mins < 60) return `${mins}m`;
        const h = Math.floor(mins / 60), m = mins % 60;
        return m ? `${h}h ${m}m` : `${h}h`;
    }

    function copyDayTemplate(fromDay, toDay) {
        const templates = loadTemplates();
        const srcBlocks = (templates[fromDay] || []);
        if (!srcBlocks.length) return;
        if (toDay === 'ALL') {
            DAYS.forEach(d => {
                if (d !== fromDay) {
                    templates[d] = srcBlocks.map(b => ({ ...b, id: String(Date.now() + Math.floor(Math.random() * 9999)) }));
                }
            });
        } else {
            templates[toDay] = srcBlocks.map(b => ({ ...b, id: String(Date.now() + Math.floor(Math.random() * 9999)) }));
        }
        saveTemplates(templates);
        renderTemplateEditor();
    }

    // ── Block Modal ────────────────────────────────────────
    function openBlockModal(day, blockId) {
        blockModal = { day, blockId };
        const modal = document.getElementById('block-modal');
        const titleEl = document.getElementById('block-modal-title');
        const labelEl = document.getElementById('block-label');
        const startEl = document.getElementById('block-start');
        const endEl = document.getElementById('block-end');
        const delBtn = document.getElementById('block-modal-delete');
        if (!modal) return;

        const templates = loadTemplates();
        const blocks = templates[day] || [];
        const block = blockId ? blocks.find(b => b.id === blockId) : null;

        titleEl.textContent = block ? `Edit Block — ${day}` : `Add Block — ${day}`;
        labelEl.value = block ? block.label : '';
        startEl.value = block ? block.start : '07:00';
        endEl.value = block ? block.end : '08:00';
        selectedBlockColour = block ? (block.colour || 0) : 0;
        delBtn.style.display = block ? 'inline-block' : 'none';

        renderColourPicker('block-colour-picker', BLOCK_COLOURS, selectedBlockColour, idx => { selectedBlockColour = idx; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeBlockModal() {
        const modal = document.getElementById('block-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveBlock() {
        const label = document.getElementById('block-label').value.trim();
        const start = document.getElementById('block-start').value;
        const end = document.getElementById('block-end').value;
        if (!label) { alert('Please enter a block name.'); return; }
        const templates = loadTemplates();
        if (!templates[blockModal.day]) templates[blockModal.day] = [];
        const blocks = templates[blockModal.day];
        if (blockModal.blockId) {
            const idx = blocks.findIndex(b => b.id === blockModal.blockId);
            if (idx >= 0) blocks[idx] = { ...blocks[idx], label, start, end, colour: selectedBlockColour };
        } else {
            blocks.push({ id: Date.now().toString(), label, start, end, colour: selectedBlockColour });
        }
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    function deleteBlock() {
        if (!blockModal.blockId) return;
        const templates = loadTemplates();
        const blocks = templates[blockModal.day] || [];
        const idx = blocks.findIndex(b => b.id === blockModal.blockId);
        if (idx >= 0) blocks.splice(idx, 1);
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    // ─────────────────────────────────────────────────────
    // RECURRING TASKS MANAGER
    // ─────────────────────────────────────────────────────
    function renderRecurringManager() {
        const container = document.getElementById('planner-recurring-manager');
        if (!container) return;
        const tasks = loadRecurring();
        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">🔁 RECURRING TASKS</div>`;

        // Add form
        html += `<div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.25rem; align-items:center;">`;
        html += `<input id="rt-title" type="text" placeholder="Task name..." style="flex:2 1 160px; padding:0.35rem 0.6rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<select id="rt-freq" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<option value="weekly">Weekly</option><option value="monthly">Monthly</option></select>`;
        html += `<select id="rt-dueday" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        DAYS.forEach(d => { html += `<option value="${d}">${d}</option>`; });
        html += `</select>`;
        html += `<button id="rt-add-btn" style="padding:0.35rem 1rem; background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.95rem; cursor:pointer; border-radius:3px; font-weight:bold;">+ Add</button>`;
        html += `</div>`;

        // Render two lists
        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            const label = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:1rem;">`;
            html += `<div style="font-size:0.85rem; color:var(--text-secondary); font-weight:bold; margin-bottom:0.4rem; letter-spacing:1px;">${label}</div>`;
            if (list.length === 0) {
                html += `<div style="color:rgba(255,255,255,0.3); font-style:italic; font-size:0.85rem; padding:0.4rem 0;">No ${freq} tasks yet.</div>`;
            } else {
                list.forEach(t => {
                    const ago = daysSince(t.lastDone);
                    const agoText = ago === null ? 'Never done' : ago === 0 ? 'Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                    const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Last done: never';
                    const dueLabel = freq === 'weekly' && t.dueDay ? ` · due by ${t.dueDay}` : '';
                    html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">`;
                    html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.08); border-radius:4px; padding:6px 10px;">`;
                    html += `<div style="font-size:0.9rem; font-weight:bold;">${escapeHTML(t.title)}<span style="opacity:0.45; font-size:0.78rem;">${dueLabel}</span></div>`;
                    html += `<div style="font-size:0.75rem; color:var(--text-secondary); margin-top:1px;">${lastText}</div>`;
                    html += `</div>`;
                    html += `<button class="rt-delete-btn" data-rtid="${t.id}" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.4); color:#ef4444; border-radius:3px; padding:3px 8px; font-family:'VT323',monospace; font-size:0.85rem; cursor:pointer;">✕</button>`;
                    html += `</div>`;
                });
            }
            html += `</div>`;
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire add
        const addBtn = container.querySelector('#rt-add-btn');
        if (addBtn) addBtn.addEventListener('click', () => {
            const title = container.querySelector('#rt-title').value.trim();
            const freq = container.querySelector('#rt-freq').value;
            const dueDay = container.querySelector('#rt-dueday').value;
            if (!title) return;
            const tasks = loadRecurring();
            tasks.push({ id: Date.now().toString(), title, freq, dueDay: freq === 'weekly' ? dueDay : null, lastDone: null, history: [] });
            saveRecurring(tasks);
            renderRecurringManager();
            renderRecurringDisplay();
        });
        // Wire deletes
        container.querySelectorAll('.rt-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring().filter(t => t.id !== btn.dataset.rtid);
                saveRecurring(tasks);
                renderRecurringManager();
                renderRecurringDisplay();
            });
        });
        // Wire freq toggle for dueday visibility
        const freqSel = container.querySelector('#rt-freq');
        const dueSel = container.querySelector('#rt-dueday');
        if (freqSel && dueSel) {
            freqSel.addEventListener('change', () => {
                dueSel.style.display = freqSel.value === 'weekly' ? 'inline-block' : 'none';
            });
        }
    }

    // ─────────────────────────────────────────────────────
    // YEARLY WALL
    // ─────────────────────────────────────────────────────
    function renderYearlyWall() {
        const container = document.getElementById('planner-yearly-grid');
        if (!container) return;

        const events = loadEvents();
        const todayStr = localDateStr(new Date());
        const nowYear = new Date().getFullYear();
        const MCOLS = ['#60a5fa', '#a78bfa', '#f472b6', '#fb923c', '#facc15', '#34d399', '#22d3ee', '#818cf8', '#f87171', '#4ade80', '#fbbf24', '#c084fc'];

        function daysInMonth(mi) { return new Date(yearlyYear, mi + 1, 0).getDate(); }
        function dateStr(mi, d) {
            if (d > daysInMonth(mi)) return null;
            return `${yearlyYear}-${String(mi + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        }
        function getEventsForDate(str) {
            if (!str) return [];
            const [y, m, d] = str.split('-').map(Number);
            return events.filter(ev => {
                if (ev.recurrence === 'annual') return ev.month === m && ev.day === d;
                return ev.date === str;
            });
        }

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Year nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.5rem; margin-bottom:1rem;">`;
        html += `<button id="yearly-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="font-size:1.8rem; font-weight:bold; color:var(--accent-yellow); letter-spacing:2px;">📌 ${yearlyYear}</div>`;
        html += `<button id="yearly-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;
        html += `<div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.75rem;">Click any date to add/edit an event.</div>`;

        html += `<div style="overflow-x:auto;"><table style="border-collapse:collapse; width:100%; table-layout:fixed; min-width:520px; font-family:'VT323',monospace;">`;

        // Month header row
        html += `<thead><tr>`;
        html += `<th style="width:30px; min-width:30px; padding:3px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.08); color:var(--text-secondary); font-size:0.7rem; text-align:center;">#</th>`;
        MONTHS.forEach((name, mi) => {
            const isCur = mi === new Date().getMonth() && yearlyYear === nowYear;
            html += `<th style="padding:4px 2px; background:${isCur ? 'rgba(52,211,153,0.12)' : 'rgba(0,0,0,0.4)'}; border:1px solid ${isCur ? 'rgba(52,211,153,0.4)' : 'rgba(255,255,255,0.08)'}; color:${isCur ? 'var(--accent-green)' : MCOLS[mi]}; font-size:0.82rem; font-weight:bold; text-align:center; letter-spacing:1px;">${name}</th>`;
        });
        html += `</tr></thead><tbody>`;

        // Day rows 1–31
        for (let d = 1; d <= 31; d++) {
            const altRow = d % 2 === 0;
            html += `<tr>`;
            html += `<td style="padding:1px 3px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.06); color:var(--text-secondary); font-size:0.72rem; text-align:center; font-weight:bold;">${d}</td>`;
            MONTHS.forEach((_, mi) => {
                const str = dateStr(mi, d);
                const isToday = str === todayStr;
                const isValid = str !== null;
                const evs = isValid ? getEventsForDate(str) : [];
                let isWeekend = false;
                if (isValid) {
                    const dow = new Date(str + 'T00:00:00').getDay();
                    isWeekend = dow === 0 || dow === 6;
                }
                const bg = isToday ? 'rgba(52,211,153,0.18)'
                    : !isValid ? 'rgba(0,0,0,0.3)'
                        : isWeekend ? 'rgba(255,255,255,0.025)'
                            : altRow ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.1)';
                const bdr = isToday ? '1px solid rgba(52,211,153,0.5)' : '1px solid rgba(255,255,255,0.05)';
                const glow = isToday ? 'box-shadow:inset 0 0 0 1px rgba(52,211,153,0.4);' : '';

                let inner = '';
                if (!isValid) {
                    inner = `<div style="width:100%;height:100%;background:repeating-linear-gradient(45deg,rgba(255,255,255,0.015) 0,rgba(255,255,255,0.015) 1px,transparent 1px,transparent 4px);"></div>`;
                } else if (evs.length > 0) {
                    evs.slice(0, 2).forEach(ev => {
                        inner += `<div style="background:${ev.color}22; border-left:2px solid ${ev.color}; border-radius:1px; padding:0 2px; font-size:0.58rem; line-height:1.4; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${ev.emoji || ''} ${ev.label}</div>`;
                    });
                }

                const cursor = isValid ? 'cursor:pointer;' : 'cursor:default;';
                html += `<td class="yearly-cell" data-date="${str || ''}" data-valid="${isValid ? '1' : '0'}"
                    style="padding:1px; background:${bg}; border:${bdr}; height:24px; vertical-align:top; overflow:hidden; ${cursor} ${glow} transition:background 0.1s;"
                    title="${str || 'n/a'}">
                    ${inner}
                </td>`;
            });
            html += `</tr>`;
        }
        html += `</tbody></table></div></div>`;
        container.innerHTML = html;

        // Year nav
        container.querySelector('#yearly-prev').addEventListener('click', () => { yearlyYear--; renderYearlyWall(); });
        container.querySelector('#yearly-next').addEventListener('click', () => { yearlyYear++; renderYearlyWall(); });

        // Cell clicks
        container.querySelectorAll('.yearly-cell').forEach(cell => {
            if (cell.dataset.valid !== '1') return;
            cell.addEventListener('mouseenter', () => { cell.style.background = 'rgba(52,211,153,0.1)'; });
            cell.addEventListener('mouseleave', () => { cell.style.background = ''; });
            cell.addEventListener('click', () => openEventModal(cell.dataset.date));
        });
    }

    // ── Event Modal ────────────────────────────────────────
    function openEventModal(dateStr_arg) {
        const modal = document.getElementById('event-modal');
        const titleEl = document.getElementById('event-modal-title');
        const labelEl = document.getElementById('event-label');
        const emojiEl = document.getElementById('event-emoji');
        const annualEl = document.getElementById('event-annual');
        const delBtn = document.getElementById('event-modal-delete');
        if (!modal) return;

        const [y, m, d] = dateStr_arg.split('-').map(Number);
        const events = loadEvents();
        // Find existing event on this specific date
        const existing = events.find(ev => ev.recurrence === 'once' ? ev.date === dateStr_arg : (ev.month === m && ev.day === d));

        eventModal = { dateStr: dateStr_arg, eventId: existing ? existing.id : null };
        titleEl.textContent = existing
            ? `Edit Event — ${MONTHS[m - 1]} ${d}`
            : `Add Event — ${MONTHS[m - 1]} ${d}`;
        labelEl.value = existing ? existing.label : '';
        emojiEl.value = existing ? (existing.emoji || '📅') : '📅';
        annualEl.checked = existing ? existing.recurrence === 'annual' : false;
        selectedEventColour = existing ? existing.color : EVENT_COLOURS[0];
        delBtn.style.display = existing ? 'inline-block' : 'none';

        renderColourPicker('event-colour-picker', EVENT_COLOURS, EVENT_COLOURS.indexOf(selectedEventColour) || 0, idx => { selectedEventColour = EVENT_COLOURS[idx]; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeEventModal() {
        const modal = document.getElementById('event-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveEvent() {
        const label = document.getElementById('event-label').value.trim();
        const emoji = document.getElementById('event-emoji').value;
        const annual = document.getElementById('event-annual').checked;
        if (!label) { alert('Please enter an event name.'); return; }
        const [y, m, d] = eventModal.dateStr.split('-').map(Number);
        const events = loadEvents();
        const newEv = { id: eventModal.eventId || Date.now().toString(), label, emoji, color: selectedEventColour, recurrence: annual ? 'annual' : 'once' };
        if (annual) { newEv.month = m; newEv.day = d; }
        else { newEv.date = eventModal.dateStr; }
        const idx = events.findIndex(e => e.id === newEv.id);
        if (idx >= 0) events[idx] = newEv; else events.push(newEv);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    function deleteEvent() {
        if (!eventModal.eventId) return;
        const events = loadEvents().filter(e => e.id !== eventModal.eventId);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    // ─────────────────────────────────────────────────────
    // SCHEDULE PAGE — Day display + Recurring Tasks
    // ─────────────────────────────────────────────────────
    let schedDayOffset = 0;

    function renderScheduleDisplay() {
        renderScheduleDayBlocks();
        renderRecurringDisplay();
    }

    function renderScheduleDayBlocks() {
        const container = document.getElementById('schedule-week-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayStr = localDateStr(new Date());

        const viewDate = new Date();
        viewDate.setDate(viewDate.getDate() + schedDayOffset);
        const viewDow = viewDate.getDay();
        const dayName = DAYS[viewDow === 0 ? 6 : viewDow - 1];
        const isToday = localDateStr(viewDate) === todayStr;

        const blocks = (templates[dayName] || []).slice().sort((a, b) => a.start.localeCompare(b.start));

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.25rem; margin-bottom:1.25rem;">`;
        html += `<button id="sched-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="text-align:center; min-width:200px;">`;
        html += `<div style="font-size:1.6rem; font-weight:bold; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'};">${dayName}${isToday ? ' <span style="font-size:0.7rem;">← TODAY</span>' : ''}</div>`;
        html += `<div style="font-size:0.82rem; color:var(--text-secondary);">${viewDate.getDate()}/${viewDate.getMonth() + 1}/${viewDate.getFullYear()}</div>`;
        if (!isToday) { html += `<button id="sched-today" style="margin-top:3px; background:none; border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.78rem; padding:1px 10px; cursor:pointer; border-radius:2px;">↩ Today</button>`; }
        html += `</div>`;
        html += `<button id="sched-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;

        // Blocks
        const todayExtras = loadTodayExtras();
        const extrasForDay = todayExtras[dayName] || [];

        if (blocks.length === 0) {
            html += `<div class="sched-drop-zone" data-slot="unscheduled" style="background:rgba(52,211,153,0.04); border:1px dashed rgba(52,211,153,0.2); border-radius:6px; padding:2rem; text-align:center; color:var(--text-secondary);">No template set for ${dayName}. Go to Planner → Template to add blocks.</div>`;
        } else {
            html += `<div style="display:flex; flex-direction:column; gap:6px;">`;
            blocks.forEach(b => {
                const ci = typeof b.colour === 'number' ? b.colour : 0;
                const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                const dur = calcDuration(b.start, b.end);
                const slotExtras = extrasForDay.filter(e => e.slot === b.start);
                html += `<div class="sched-block-wrap">`;
                html += `<div class="sched-drop-zone" data-slot="${b.start}" style="background:${c.bg}; border-left:3px solid ${c.border}; border-radius:4px; padding:10px 14px; display:flex; align-items:center; gap:12px; transition: outline 0.15s;">`;
                html += `<div style="text-align:right; min-width:90px; font-size:0.82rem; color:var(--text-secondary);">${b.start} – ${b.end}</div>`;
                html += `<div style="flex:1;"><div style="font-size:1rem; font-weight:bold;">${b.label}</div>${dur ? `<div style="font-size:0.75rem; color:${c.border}; opacity:0.7;">${dur}</div>` : ''}</div>`;
                html += `</div>`;
                if (slotExtras.length > 0) {
                    slotExtras.forEach(ex => {
                        html += `<div class="sched-extra-task" data-extra-id="${ex.id}" data-day="${dayName}" style="margin-left:24px; margin-top:3px; background:rgba(155,89,255,0.08); border-left:3px solid var(--accent-magenta,#c084fc); border-radius:4px; padding:6px 12px; display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">`;
                        html += `<span>⤷ ${ex.label}</span>`;
                        html += `<span class="remove-extra-btn" data-extra-id="${ex.id}" data-day="${dayName}" style="cursor:pointer; color:rgba(255,255,255,0.3); font-size:1rem; line-height:1; padding:0 4px;">×</span>`;
                        html += `</div>`;
                    });
                }
                html += `</div>`;
            });
            html += `</div>`;
        }
        // Unscheduled extras (dropped without a specific slot)
        const unscheduledExtras = extrasForDay.filter(e => e.slot === 'unscheduled');
        if (unscheduledExtras.length > 0) {
            html += `<div style="margin-top:8px; display:flex; flex-direction:column; gap:4px;">`;
            unscheduledExtras.forEach(ex => {
                html += `<div class="sched-extra-task" data-extra-id="${ex.id}" data-day="${dayName}" style="margin-left:24px; background:rgba(155,89,255,0.08); border-left:3px solid var(--accent-magenta,#c084fc); border-radius:4px; padding:6px 12px; display:flex; align-items:center; justify-content:space-between; font-size:0.85rem;">`;
                html += `<span>⤷ ${ex.label}</span>`;
                html += `<span class="remove-extra-btn" data-extra-id="${ex.id}" data-day="${dayName}" style="cursor:pointer; color:rgba(255,255,255,0.3); font-size:1rem; line-height:1; padding:0 4px;">×</span>`;
                html += `</div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
        container.innerHTML = html;

        // Wire nav
        container.querySelector('#sched-prev')?.addEventListener('click', () => { schedDayOffset--; renderScheduleDayBlocks(); });
        container.querySelector('#sched-next')?.addEventListener('click', () => { schedDayOffset++; renderScheduleDayBlocks(); });
        container.querySelector('#sched-today')?.addEventListener('click', () => { schedDayOffset = 0; renderScheduleDayBlocks(); });

        // Wire drop zones
        container.querySelectorAll('.sched-drop-zone').forEach(zone => {
            zone.addEventListener('dragover', e => { e.preventDefault(); zone.style.outline = '2px dashed var(--accent-magenta,#c084fc)'; });
            zone.addEventListener('dragleave', () => { zone.style.outline = ''; });
            zone.addEventListener('drop', e => {
                e.preventDefault();
                zone.style.outline = '';
                const taskId = e.dataTransfer.getData('taskId');
                const taskLabel = e.dataTransfer.getData('taskLabel');
                if (!taskId) return;
                const slot = zone.dataset.slot || 'unscheduled';
                const extras = loadTodayExtras();
                if (!extras[dayName]) extras[dayName] = [];
                // Avoid duplicates
                if (extras[dayName].some(ex => ex.id === taskId && ex.slot === slot)) return;
                extras[dayName].push({ id: taskId, label: taskLabel, slot });
                saveTodayExtras(extras);
                renderScheduleDayBlocks();
            });
        });

        // Wire remove buttons
        container.querySelectorAll('.remove-extra-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const extras = loadTodayExtras();
                const day = btn.dataset.day;
                if (extras[day]) extras[day] = extras[day].filter(e => e.id !== btn.dataset.extraId);
                saveTodayExtras(extras);
                renderScheduleDayBlocks();
            });
        });

        // Render task pool below
        renderTaskPool(container.closest('#today') || container);
    }

    async function renderTaskPool(schedContainer) {
        // Remove any existing pool
        const existing = schedContainer.querySelector('#schedule-task-pool');
        if (existing) existing.remove();

        let tasks = [];
        try {
            const resp = await apiFetch(`/tasks`, { headers: { "Authorization": `Bearer ${API_TOKEN}` } });
            if (resp.ok) tasks = await resp.json();
        } catch (e) { console.warn('Task pool fetch failed', e); return; }

        const lastDone = JSON.parse(localStorage.getItem('symphony_last_done') || '{}');

        // Sort: never-done first, then oldest-done first
        tasks.sort((a, b) => {
            const da = lastDone[a.id] ? new Date(lastDone[a.id]) : new Date(0);
            const db = lastDone[b.id] ? new Date(lastDone[b.id]) : new Date(0);
            return da - db;
        });

        const pool = document.createElement('div');
        pool.id = 'schedule-task-pool';
        pool.style.cssText = 'margin-top:1.75rem; font-family:"VT323",monospace;';

        let html = `<div style="font-size:1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.6rem; letter-spacing:1px;">\\u{1F4CB} TASK POOL <span style="font-size:0.72rem; color:var(--text-secondary); font-weight:normal;">\u2014 drag onto a time block above</span></div>`;
        html += `<div style="display:flex; flex-wrap:wrap; gap:8px;">`;

        tasks.forEach(task => {
            const lastDoneTs = lastDone[task.id] ? new Date(lastDone[task.id]) : null;
            const daysSince = lastDoneTs ? Math.floor((Date.now() - lastDoneTs) / 86400000) : null;
            const lastDoneLabel = daysSince === null ? 'never done' : daysSince === 0 ? 'done today' : `${daysSince}d ago`;
            const isDoneToday = daysSince === 0;

            let colorBorder = 'rgba(255,255,255,0.15)';
            if (task.priority_color === 'RED') colorBorder = 'var(--accent-red,#ef4444)';
            if (task.priority_color === 'ORANGE') colorBorder = 'var(--accent-orange,#f97316)';
            if (task.priority_color === 'GREEN') colorBorder = 'var(--accent-green,#34d399)';

            // Escape label for data attribute
            const safeLabel = task.title.replace(/"/g, '&quot;').replace(/'/g, '&#39;');

            html += `<div class="pool-task-card" draggable="true" data-task-id="${task.id}" data-task-label="${safeLabel}" style="background:rgba(0,0,0,0.3); border:1px solid ${colorBorder}; border-radius:6px; padding:7px 12px; cursor:grab; opacity:${isDoneToday ? '0.4' : '1'}; min-width:120px; max-width:200px; user-select:none;">`;
            html += `<div style="font-size:0.88rem; font-weight:bold; color:var(--text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${escapeHTML(task.title)}</div>`;
            html += `<div style="font-size:0.7rem; color:var(--text-secondary); margin-top:2px;">\u{1F550} ${lastDoneLabel}</div>`;
            html += `</div>`;
        });

        html += `</div>`;
        pool.innerHTML = html;
        schedContainer.appendChild(pool);

        // Wire drag start on pool cards
        pool.querySelectorAll('.pool-task-card').forEach(card => {
            card.addEventListener('dragstart', e => {
                e.dataTransfer.setData('taskId', card.dataset.taskId);
                e.dataTransfer.setData('taskLabel', card.dataset.taskLabel);
                card.style.opacity = '0.3';
            });
            card.addEventListener('dragend', () => {
                card.style.opacity = card.dataset.taskId ? (card.style.opacity === '0.3' ? '1' : card.style.opacity) : '1';
                // Refresh to restore correct done-today opacity
                renderTaskPool(schedContainer);
            });
        });
    }

    function renderRecurringDisplay() {
        // Find or create the recurring display container in schedule section
        let container = document.getElementById('schedule-recurring-display');
        if (!container) {
            const schedGrid = document.getElementById('schedule-week-grid');
            if (!schedGrid) return;
            container = document.createElement('div');
            container.id = 'schedule-recurring-display';
            container.style.marginTop = '1.5rem';
            schedGrid.parentNode.insertBefore(container, schedGrid.nextSibling);
        }

        const tasks = loadRecurring();
        if (tasks.length === 0) { container.innerHTML = ''; return; }

        const todayStr = localDateStr(new Date());
        const todayDow = new Date().getDay(); // 0=Sun
        const todayDayName = DAYS[todayDow === 0 ? 6 : todayDow - 1];
        // Which Monday started this week?
        const monday = new Date();
        const dayOfWeek = monday.getDay();
        const daysToMon = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        monday.setDate(monday.getDate() - daysToMon);
        const weekStartStr = localDateStr(monday);

        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px; border-top:1px solid rgba(255,255,255,0.08); padding-top:1rem;">🔁 RECURRING TASKS</div>`;

        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            if (list.length === 0) return;
            const freqLabel = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:0.75rem;">`;
            html += `<div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.35rem; letter-spacing:1px;">${freqLabel}</div>`;
            list.forEach(t => {
                const ago = daysSince(t.lastDone);
                const agoText = ago === null ? 'Never done' : ago === 0 ? '✓ Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Never done';

                // Overdue logic for weekly tasks
                let overdue = false;
                if (freq === 'weekly' && t.dueDay) {
                    const dueIdx = DAYS.indexOf(t.dueDay);
                    const curIdx = DAYS.indexOf(todayDayName);
                    const doneSinceWeekStart = t.lastDone && t.lastDone >= weekStartStr;
                    overdue = !doneSinceWeekStart && curIdx >= dueIdx;
                }

                const doneToday = t.lastDone === todayStr;
                const dueLabel = freq === 'weekly' && t.dueDay ? ` <span style="opacity:0.5; font-size:0.78rem;">· due by ${t.dueDay}</span>` : '';

                html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">`;
                html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid ${overdue ? 'rgba(239,68,68,0.4)' : 'rgba(255,255,255,0.07)'}; border-radius:4px; padding:7px 10px;">`;
                html += `<div style="font-size:0.92rem; font-weight:bold;">${escapeHTML(t.title)}${dueLabel}${overdue ? ' <span style="color:#ef4444; font-size:0.75rem;">⚠ OVERDUE</span>' : ''}</div>`;
                html += `<div style="font-size:0.75rem; color:${doneToday ? 'var(--accent-green)' : 'var(--text-secondary)'}; margin-top:1px;">${lastText}</div>`;
                html += `</div>`;
                if (!doneToday) {
                    html += `<button class="rt-done-btn" data-rtid="${t.id}" style="background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); border-radius:3px; padding:5px 10px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">✓ Done</button>`;
                } else {
                    html += `<div style="color:var(--accent-green); font-size:0.82rem; padding:5px 8px;">✓</div>`;
                }
                html += `</div>`;
            });
            html += `</div>`;
        });
        html += `</div>`;
        container.innerHTML = html;

        // Wire done buttons
        container.querySelectorAll('.rt-done-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring();
                const t = tasks.find(t => t.id === btn.dataset.rtid);
                if (!t) return;
                t.lastDone = todayStr;
                if (!t.history) t.history = [];
                t.history.push(todayStr);
                saveRecurring(tasks);
                renderRecurringDisplay();
                renderRecurringManager();
            });
        });
    }

    // ─────────────────────────────────────────────────────
    // PLANNER VIEW SWITCHING
    // ─────────────────────────────────────────────────────
    function switchPlannerView(view) {
        plannerSection = view;
        const tmplBtn = document.getElementById('planner-view-template');
        const yearlyBtn = document.getElementById('planner-view-yearly');
        const tmplSec = document.getElementById('planner-template-section');
        const yearlySec = document.getElementById('planner-yearly-section');
        const ACTIVE = { background: 'rgba(52,211,153,0.2)', borderColor: 'var(--accent-green)', color: 'var(--accent-green)', fontWeight: 'bold' };
        const INACTIVE = { background: 'rgba(0,0,0,0.2)', borderColor: 'var(--glass-border)', color: 'var(--text-secondary)', fontWeight: 'normal' };
        const applyStyle = (btn, s) => { if (!btn) return; Object.assign(btn.style, s); };

        if (view === 'yearly') {
            applyStyle(tmplBtn, INACTIVE);
            applyStyle(yearlyBtn, ACTIVE);
            if (tmplSec) tmplSec.style.display = 'none';
            if (yearlySec) yearlySec.style.display = 'block';
            renderYearlyWall();
        } else {
            applyStyle(tmplBtn, ACTIVE);
            applyStyle(yearlyBtn, INACTIVE);
            if (tmplSec) tmplSec.style.display = 'block';
            if (yearlySec) yearlySec.style.display = 'none';
            renderTemplateEditor();
            renderRecurringManager();
        }
    }

    // ─────────────────────────────────────────────────────
    // INIT
    // ─────────────────────────────────────────────────────
    function boot() {
        // Planner view toggles
        document.getElementById('planner-view-template')?.addEventListener('click', () => switchPlannerView('template'));
        document.getElementById('planner-view-yearly')?.addEventListener('click', () => switchPlannerView('yearly'));

        // Block modal buttons
        document.getElementById('block-modal-save')?.addEventListener('click', saveBlock);
        document.getElementById('block-modal-delete')?.addEventListener('click', deleteBlock);
        document.getElementById('block-modal-cancel')?.addEventListener('click', closeBlockModal);
        document.getElementById('block-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeBlockModal(); });

        // Event modal buttons
        document.getElementById('event-modal-save')?.addEventListener('click', saveEvent);
        document.getElementById('event-modal-delete')?.addEventListener('click', deleteEvent);
        document.getElementById('event-modal-cancel')?.addEventListener('click', closeEventModal);
        document.getElementById('event-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeEventModal(); });

        // Hook planner tab
        document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
            btn.addEventListener('click', () => {
                const t = btn.getAttribute('data-tab');
                if (t === 'planner') { switchPlannerView(plannerSection); }
                if (t === 'today') { renderScheduleDisplay(); }
            });
        });

        // Initial render
        switchPlannerView('template');
        renderScheduleDisplay();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
// --- End Planner Engine v2 ---

`

## public\toolbox.html
`html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Toolbox | Ad-Free Utilities</title>
            <link

    <script src="vendor/pdf.min.js"></script>
    <script src="vendor/qrcode.min.js"></script>
    <style>
        :root {
            --bg-forge: #070504;
            --iron-dark: #181008;
            --iron-panel: rgba(24, 16, 8, 0.85);
            --iron-border: rgba(120, 80, 40, 0.35);
            --copper: #b06028;
            --copper-bright: #c87830;
            --forge-amber: #d08030;
            --brass: #c4a040;
            --brass-bright: #d4b050;
            --rust: #905030;
            --rust-dark: #6a3020;
            --patina: #786040;
            --parchment: #ddd0c0;
            --parchment-dim: #a89880;
            --ember: #d47020;
            --flame-orange: #e08020;
            --radius: 3px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--bg-forge);
            color: var(--parchment);
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .forge-bg {
            position: fixed;
            inset: 0;
            z-index: -1;
            overflow: hidden;
        }

        .forge-glow {
            position: absolute;
            width: 600px;
            height: 600px;
            right: -100px;
            top: 20%;
            background: radial-gradient(ellipse, rgba(208, 128, 48, 0.18) 0%, rgba(192, 64, 32, 0.08) 40%, transparent 70%);
            filter: blur(40px);
            animation: forge-pulse 4s ease-in-out infinite alternate;
        }

        .forge-glow-2 {
            position: absolute;
            width: 400px;
            height: 300px;
            left: -50px;
            bottom: -50px;
            background: radial-gradient(ellipse, rgba(196, 112, 32, 0.1) 0%, transparent 70%);
            filter: blur(60px);
            animation: forge-pulse 6s ease-in-out infinite alternate-reverse;
        }

        @keyframes forge-pulse {
            0% {
                opacity: 0.7;
                transform: scale(1);
            }

            100% {
                opacity: 1;
                transform: scale(1.05);
            }
        }

        .app-container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 1.5rem 1.5rem 4rem;
            position: relative;
            z-index: 1;
        }

        .forge-panel {
            background: var(--iron-panel);
            -webkit-backdrop-filter: blur(8px);
            backdrop-filter: blur(8px);
            border: 2px solid var(--iron-border);
            border-top: 2px solid rgba(176, 96, 40, 0.3);
            border-radius: var(--radius);
            position: relative;
        }

        .forge-panel::before {
            content: '';
            position: absolute;
            top: -1px;
            left: 10%;
            right: 10%;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--copper), transparent);
            opacity: 0.4;
        }

        header {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        header h1 {
            font-family: Georgia, serif;
            font-size: 2.4rem;
            font-weight: 700;
            color: var(--copper-bright);
            text-shadow: 0 0 30px rgba(208, 128, 48, 0.3), 0 2px 4px rgba(0, 0, 0, 0.5);
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        header .subtitle {
            color: var(--parchment-dim);
            font-size: 0.82rem;
            margin-top: 0.4rem;
            font-style: italic;
        }

        .back-link {
            position: absolute;
            top: 1rem;
            left: 1.5rem;
            color: var(--copper);
            text-decoration: none;
            font-family: Georgia, serif;
            font-size: 0.85rem;
            opacity: 0.6;
            transition: opacity 0.2s;
            z-index: 2;
        }

        .back-link:hover {
            opacity: 1;
            color: var(--copper-bright);
        }

        /* Tool Grid */
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 1rem;
            padding: 0.5rem 0;
        }

        .tool-card {
            background: rgba(16, 10, 6, 0.7);
            border: 2px solid var(--iron-border);
            border-radius: var(--radius);
            padding: 1.5rem;
            cursor: pointer;
            transition: all 0.25s;
            text-align: center;
        }

        .tool-card:hover {
            border-color: var(--copper);
            box-shadow: 0 0 20px rgba(208, 128, 48, 0.12);
            transform: translateY(-2px);
        }

        .tool-card .icon {
            font-size: 2.5rem;
            margin-bottom: 0.75rem;
            display: block;
        }

        .tool-card h3 {
            font-family: Georgia, serif;
            color: var(--copper-bright);
            font-size: 1rem;
            margin-bottom: 0.4rem;
            letter-spacing: 0.5px;
        }

        .tool-card p {
            font-size: 0.78rem;
            color: var(--parchment-dim);
            line-height: 1.4;
        }

        /* Tool Sections */
        .tool-section {
            display: none;
        }

        .tool-section.active {
            display: block;
        }

        .tool-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding: 1rem;
        }

        .tool-header h2 {
            font-family: Georgia, serif;
            color: var(--copper-bright);
            font-size: 1.4rem;
            letter-spacing: 1px;
        }

        .back-to-tools {
            background: rgba(176, 96, 40, 0.15);
            border: 1px solid var(--copper);
            color: var(--copper-bright);
            font-family: Georgia, serif;
            font-size: 0.8rem;
            padding: 0.4rem 0.8rem;
            cursor: pointer;
            border-radius: var(--radius);
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .back-to-tools:hover {
            background: rgba(176, 96, 40, 0.3);
        }

        /* Shared Components */
        .tb-input,
        .tb-textarea,
        .tb-select {
            width: 100%;
            padding: 0.5rem 0.7rem;
            background: rgba(8, 5, 4, 0.6);
            border: 1px solid rgba(120, 80, 40, 0.25);
            color: var(--parchment);
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 0.9rem;
            border-radius: var(--radius);
            outline: 2px solid transparent;
            outline-offset: 2px;
            transition: border-color 0.2s, outline-color 0.2s;
        }

        .tb-input:focus,
        .tb-textarea:focus,
        .tb-select:focus {
            border-color: var(--copper);
            box-shadow: 0 0 8px rgba(176, 96, 40, 0.15);
            outline-color: var(--copper);
        }

        .tb-input::placeholder,
        .tb-textarea::placeholder {
            color: rgba(168, 152, 128, 0.4);
        }

        .tb-textarea {
            resize: vertical;
            min-height: 120px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
        }

        .tb-select {
            cursor: pointer;
        }

        .tb-btn {
            padding: 0.45rem 1rem;
            background: rgba(176, 96, 40, 0.15);
            border: 1px solid var(--copper);
            color: var(--copper-bright);
            font-family: Georgia, serif;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: var(--radius);
            transition: all 0.2s;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }

        .tb-btn:hover {
            background: rgba(176, 96, 40, 0.3);
            box-shadow: 0 0 10px rgba(208, 128, 48, 0.15);
        }

        .tb-btn.green {
            background: rgba(196, 160, 64, 0.12);
            border-color: var(--brass);
            color: var(--brass-bright);
        }

        .tb-btn.green:hover {
            background: rgba(196, 160, 64, 0.25);
        }

        .sub-panel {
            background: rgba(16, 10, 6, 0.6);
            border: 1px solid var(--iron-border);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .row {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .row>* {
            flex: 1;
            min-width: 120px;
        }

        .drop-zone {
            border: 2px dashed rgba(120, 80, 40, 0.4);
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
            color: var(--parchment-dim);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 1rem;
        }

        .drop-zone:hover,
        .drop-zone.dragover {
            border-color: var(--copper);
            background: rgba(176, 96, 40, 0.08);
            color: var(--copper-bright);
        }

        .result-box {
            background: rgba(8, 5, 4, 0.8);
            border: 1px solid var(--iron-border);
            border-radius: var(--radius);
            padding: 1rem;
            margin-top: 1rem;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            word-break: break-all;
            color: var(--brass-bright);
        }

        .stat {
            display: inline-block;
            padding: 0.3rem 0.7rem;
            background: rgba(176, 96, 40, 0.1);
            border: 1px solid rgba(176, 96, 40, 0.3);
            border-radius: 2px;
            margin: 0.2rem;
            font-size: 0.8rem;
            color: var(--copper-bright);
        }

        .color-swatch {
            width: 100%;
            height: 80px;
            border-radius: var(--radius);
            border: 2px solid var(--iron-border);
            margin-bottom: 0.75rem;
            cursor: pointer;
        }

        .copy-toast {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: var(--copper);
            color: #fff;
            padding: 0.5rem 1.5rem;
            border-radius: var(--radius);
            font-size: 0.85rem;
            opacity: 0;
            transition: opacity 0.3s;
            z-index: 100;
            pointer-events: none;
        }

        .copy-toast.show {
            opacity: 1;
        }

        #pdf-canvas-container {
            overflow: auto;
            max-height: 70vh;
        }

        #pdf-canvas-container canvas {
            display: block;
            margin: 0.5rem auto;
            border: 1px solid var(--iron-border);
            max-width: 100%;
        }

        .pdf-controls {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }

        .pdf-controls span {
            color: var(--parchment-dim);
            font-size: 0.85rem;
        }

        .qr-output {
            text-align: center;
            margin-top: 1rem;
        }

        .qr-output canvas {
            border: 4px solid #fff;
            border-radius: var(--radius);
        }

        @media (prefers-reduced-motion: reduce) {

            .forge-glow,
            .forge-glow-2 {
                animation: none !important;
            }

            .forge-glow {
                opacity: 0.85;
            }
        }

        @media (max-width: 600px) {
            .app-container {
                padding: 0.75rem 0.75rem 3rem;
            }

            header h1 {
                font-size: 1.6rem;
                letter-spacing: 1px;
            }

            .tool-grid {
                grid-template-columns: 1fr 1fr;
            }

            .row {
                flex-direction: column;
            }

            .row>* {
                min-width: 100%;
            }
        }

        @media (max-width: 400px) {
            .tool-grid {
                grid-template-columns: 1fr;
            }
        }

        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(176, 96, 40, 0.2);
            border-radius: 2px;
        }
    </style>
</head>

<body>
    <div class="forge-bg">
        <div class="forge-glow"></div>
        <div class="forge-glow-2"></div>
    </div>
    <div id="copy-toast" class="copy-toast">Copied!</div>

    <div class="app-container">
        <a href="index.html" class="back-link">← Life Hub</a>
        <header class="forge-panel">
            <h1>🔧 Toolbox</h1>
            <p class="subtitle">Your tools. No ads. No uploads. Everything runs locally.</p>
        </header>

        <!-- TOOL GRID -->
        <div id="tool-grid" class="tool-grid">
            <div class="tool-card" onclick="openTool('pdf')"><span class="icon">📄</span>
                <h3>PDF Viewer</h3>
                <p>Open and read PDFs without Adobe or ads</p>
            </div>
            <div class="tool-card" onclick="openTool('image')"><span class="icon">🖼️</span>
                <h3>Image Tools</h3>
                <p>Convert, resize & compress — PNG, JPG, WebP</p>
            </div>
            <div class="tool-card" onclick="openTool('text')"><span class="icon">📝</span>
                <h3>Text Tools</h3>
                <p>Word count, case change, sort, deduplicate</p>
            </div>
            <div class="tool-card" onclick="openTool('units')"><span class="icon">📐</span>
                <h3>Unit Converter</h3>
                <p>Temperature, weight, length, data sizes</p>
            </div>
            <div class="tool-card" onclick="openTool('color')"><span class="icon">🎨</span>
                <h3>Color Picker</h3>
                <p>Pick colors, get hex / rgb / hsl values</p>
            </div>
            <div class="tool-card" onclick="openTool('password')"><span class="icon">🔐</span>
                <h3>Password Generator</h3>
                <p>Crypto-secure passwords, configurable</p>
            </div>
            <div class="tool-card" onclick="openTool('qr')"><span class="icon">📱</span>
                <h3>QR Generator</h3>
                <p>Generate QR codes from text or URLs</p>
            </div>
            <div class="tool-card" onclick="openTool('json')"><span class="icon">{ }</span>
                <h3>JSON Formatter</h3>
                <p>Format, minify & validate JSON</p>
            </div>
            <div class="tool-card" onclick="window.open('../gamma-40hz.html','_blank')"><span class="icon">🧠</span>
                <h3>40 Hz Gamma</h3>
                <p>Neural entrainment — binaural beats for focus & recovery</p>
            </div>
        </div>

        <!-- PDF VIEWER -->
        <div id="tool-pdf" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>📄 PDF Viewer</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="drop-zone" id="pdf-drop" onclick="document.getElementById('pdf-file').click()">
                    Drop a PDF here or click to browse
                    <input type="file" id="pdf-file" accept=".pdf" style="display:none">
                </div>
                <div class="pdf-controls" id="pdf-controls" style="display:none;">
                    <button class="tb-btn" onclick="pdfPrev()">← Prev</button>
                    <span>Page <span id="pdf-page-num">1</span> of <span id="pdf-page-count">0</span></span>
                    <button class="tb-btn" onclick="pdfNext()">Next →</button>
                    <button class="tb-btn" onclick="pdfZoom(-0.25)">−</button>
                    <span id="pdf-zoom-level">100%</span>
                    <button class="tb-btn" onclick="pdfZoom(0.25)">+</button>
                </div>
                <div id="pdf-canvas-container"></div>
            </div>
        </div>

        <!-- IMAGE TOOLS -->
        <div id="tool-image" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>🖼️ Image Tools</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="drop-zone" id="img-drop" onclick="document.getElementById('img-file').click()">
                    Drop an image here or click to browse
                    <input type="file" id="img-file" accept="image/*" style="display:none">
                </div>
                <div id="img-preview-area" style="display:none;">
                    <div class="sub-panel">
                        <div class="row" style="margin-bottom:0.75rem;">
                            <div><strong style="color:var(--copper);">Original:</strong> <span id="img-info"
                                    class="stat"></span></div>
                        </div>
                        <img id="img-preview"
                            style="max-width:100%;max-height:300px;border:1px solid var(--iron-border);border-radius:var(--radius);display:block;margin:0.5rem 0;">
                    </div>
                    <div class="sub-panel">
                        <h3 style="font-family: Georgia, serif;color:var(--copper);margin-bottom:0.75rem;">Convert &
                            Resize</h3>
                        <div class="row" style="margin-bottom:0.75rem;">
                            <div style="flex:0 0 auto;min-width:auto;"><label
                                    style="font-size:0.82rem;color:var(--parchment-dim);">Format:</label></div>
                            <select class="tb-select" id="img-format" style="max-width:140px;">
                                <option value="image/png">PNG</option>
                                <option value="image/jpeg">JPG</option>
                                <option value="image/webp">WebP</option>
                            </select>
                            <div style="flex:0 0 auto;min-width:auto;"><label
                                    style="font-size:0.82rem;color:var(--parchment-dim);">Quality:</label></div>
                            <input type="range" id="img-quality" min="10" max="100" value="85" style="flex:1;">
                            <span id="img-quality-val" style="color:var(--brass);font-size:0.85rem;flex:0;">85%</span>
                        </div>
                        <div class="row" style="margin-bottom:0.75rem;">
                            <div style="flex:0 0 auto;min-width:auto;"><label
                                    style="font-size:0.82rem;color:var(--parchment-dim);">Width:</label></div>
                            <input type="number" class="tb-input" id="img-width" style="max-width:100px;">
                            <div style="flex:0 0 auto;min-width:auto;"><label
                                    style="font-size:0.82rem;color:var(--parchment-dim);">Height:</label></div>
                            <input type="number" class="tb-input" id="img-height" style="max-width:100px;">
                            <label style="font-size:0.78rem;color:var(--parchment-dim);flex:0 0 auto;"><input
                                    type="checkbox" id="img-lock" checked> Lock ratio</label>
                        </div>
                        <button class="tb-btn green" onclick="convertImage()">Convert & Download</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- TEXT TOOLS -->
        <div id="tool-text" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>📝 Text Tools</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <textarea class="tb-textarea" id="text-input" placeholder="Paste or type your text here..."
                    style="min-height:180px;" oninput="updateTextStats()"></textarea>
                <div id="text-stats" style="margin:0.75rem 0;"></div>
                <div class="row" style="flex-wrap:wrap;gap:0.4rem;">
                    <button class="tb-btn" onclick="textTransform('upper')">UPPERCASE</button>
                    <button class="tb-btn" onclick="textTransform('lower')">lowercase</button>
                    <button class="tb-btn" onclick="textTransform('title')">Title Case</button>
                    <button class="tb-btn" onclick="textTransform('sentence')">Sentence case</button>
                    <button class="tb-btn" onclick="textTransform('reverse')">Reverse</button>
                    <button class="tb-btn" onclick="textTransform('sort')">Sort Lines</button>
                    <button class="tb-btn" onclick="textTransform('dedupe')">Deduplicate</button>
                    <button class="tb-btn" onclick="textTransform('trim')">Trim Lines</button>
                    <button class="tb-btn" onclick="textTransform('number')">Number Lines</button>
                    <button class="tb-btn" onclick="textTransform('removeEmpty')">Remove Empty</button>
                    <button class="tb-btn green" onclick="copyResult('text-input')">Copy</button>
                </div>
                <div class="sub-panel" style="margin-top:1rem;">
                    <h3 style="font-family: Georgia, serif;color:var(--copper);margin-bottom:0.5rem;font-size:0.9rem;">
                        Find & Replace</h3>
                    <div class="row" style="gap:0.4rem;">
                        <input class="tb-input" id="text-find" placeholder="Find...">
                        <input class="tb-input" id="text-replace" placeholder="Replace with...">
                        <button class="tb-btn" onclick="textFindReplace()">Replace All</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- UNIT CONVERTER -->
        <div id="tool-units" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>📐 Unit Converter</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="sub-panel">
                    <div class="row" style="margin-bottom:0.75rem;">
                        <select class="tb-select" id="unit-category" onchange="updateUnitOptions()">
                            <option value="temperature">🌡️ Temperature</option>
                            <option value="weight">⚖️ Weight</option>
                            <option value="length">📏 Length</option>
                            <option value="data">💾 Data Size</option>
                            <option value="time">⏱️ Time</option>
                            <option value="volume">🧪 Volume</option>
                        </select>
                    </div>
                    <div class="row" style="align-items:flex-end;gap:0.75rem;">
                        <div style="flex:1;"><label
                                style="font-size:0.78rem;color:var(--parchment-dim);">From:</label><input type="number"
                                class="tb-input" id="unit-from-val" value="1" oninput="convertUnit()"><select
                                class="tb-select" id="unit-from" onchange="convertUnit()"
                                style="margin-top:0.3rem;"></select></div>
                        <div style="flex:0 0 auto;color:var(--copper);font-size:1.5rem;padding-bottom:1rem;">=</div>
                        <div style="flex:1;"><label style="font-size:0.78rem;color:var(--parchment-dim);">To:</label>
                            <div class="result-box" id="unit-result"
                                style="margin-top:0;min-height:2.4rem;display:flex;align-items:center;">—</div><select
                                class="tb-select" id="unit-to" onchange="convertUnit()"
                                style="margin-top:0.3rem;"></select>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- COLOR PICKER -->
        <div id="tool-color" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>🎨 Color Picker</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="sub-panel">
                    <input type="color" id="color-picker" class="color-swatch" value="#c87830"
                        oninput="updateColor(this.value)">
                    <div class="row" style="margin-bottom:0.5rem;">
                        <div><label style="font-size:0.78rem;color:var(--parchment-dim);">HEX:</label>
                            <div class="result-box" id="color-hex" style="cursor:pointer;margin-top:0.2rem;"
                                onclick="copyResult('color-hex')">#c87830</div>
                        </div>
                        <div><label style="font-size:0.78rem;color:var(--parchment-dim);">RGB:</label>
                            <div class="result-box" id="color-rgb" style="cursor:pointer;margin-top:0.2rem;"
                                onclick="copyResult('color-rgb')">rgb(200, 120, 48)</div>
                        </div>
                        <div><label style="font-size:0.78rem;color:var(--parchment-dim);">HSL:</label>
                            <div class="result-box" id="color-hsl" style="cursor:pointer;margin-top:0.2rem;"
                                onclick="copyResult('color-hsl')">hsl(28, 61%, 49%)</div>
                        </div>
                    </div>
                    <div class="row">
                        <div><label style="font-size:0.78rem;color:var(--parchment-dim);">Or paste a hex:</label><input
                                class="tb-input" id="color-hex-input" placeholder="#c87830"
                                oninput="updateColorFromHex(this.value)"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- PASSWORD GENERATOR -->
        <div id="tool-password" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>🔐 Password Generator</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="sub-panel">
                    <div class="result-box" id="pw-output"
                        style="font-size:1.3rem;text-align:center;letter-spacing:2px;cursor:pointer;padding:1.2rem;"
                        onclick="copyResult('pw-output')">Click Generate</div>
                    <div style="margin:1rem 0;">
                        <label style="color:var(--parchment-dim);font-size:0.82rem;">Length: <strong id="pw-len-val"
                                style="color:var(--brass);">20</strong></label>
                        <input type="range" id="pw-length" min="8" max="64" value="20"
                            oninput="document.getElementById('pw-len-val').textContent=this.value" style="width:100%;">
                    </div>
                    <div class="row" style="gap:1rem;margin-bottom:1rem;">
                        <label style="font-size:0.82rem;color:var(--parchment-dim);"><input type="checkbox"
                                id="pw-upper" checked> A-Z</label>
                        <label style="font-size:0.82rem;color:var(--parchment-dim);"><input type="checkbox"
                                id="pw-lower" checked> a-z</label>
                        <label style="font-size:0.82rem;color:var(--parchment-dim);"><input type="checkbox"
                                id="pw-digits" checked> 0-9</label>
                        <label style="font-size:0.82rem;color:var(--parchment-dim);"><input type="checkbox"
                                id="pw-symbols" checked> !@#$</label>
                    </div>
                    <button class="tb-btn green" onclick="generatePassword()"
                        style="width:100%;padding:0.7rem;">Generate Password</button>
                </div>
            </div>
        </div>

        <!-- QR GENERATOR -->
        <div id="tool-qr" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>📱 QR Generator</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <div class="sub-panel">
                    <input class="tb-input" id="qr-input" placeholder="Enter text or URL..." oninput="generateQR()"
                        style="margin-bottom:0.75rem;">
                    <div class="qr-output" id="qr-output">
                        <p style="color:var(--parchment-dim);font-size:0.85rem;">Enter text above to generate a QR code
                        </p>
                    </div>
                    <button class="tb-btn green" onclick="downloadQR()" style="width:100%;margin-top:0.75rem;"
                        id="qr-download" disabled>Download QR</button>
                </div>
            </div>
        </div>

        <!-- JSON FORMATTER -->
        <div id="tool-json" class="tool-section forge-panel">
            <div class="tool-header"><button class="back-to-tools" onclick="closeTool()">← Back</button>
                <h2>{ } JSON Formatter</h2>
            </div>
            <div style="padding:0 1rem 1rem;">
                <textarea class="tb-textarea" id="json-input" placeholder='Paste JSON here...'
                    style="min-height:200px;"></textarea>
                <div class="row" style="margin:0.75rem 0;gap:0.4rem;">
                    <button class="tb-btn green" onclick="jsonFormat()">Format</button>
                    <button class="tb-btn" onclick="jsonMinify()">Minify</button>
                    <button class="tb-btn" onclick="jsonValidate()">Validate</button>
                    <button class="tb-btn" onclick="copyResult('json-input')">Copy</button>
                </div>
                <div id="json-status" style="font-size:0.82rem;margin-top:0.5rem;"></div>
            </div>
        </div>
    </div>

    <script>
        // ═══════════════════════════════════════════════════════════
        // NAVIGATION
        // ═══════════════════════════════════════════════════════════
        function openTool(name) {
            document.getElementById('tool-grid').style.display = 'none';
            document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
            const section = document.getElementById('tool-' + name);
            if (section) section.classList.add('active');
        }
        function closeTool() {
            document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
            document.getElementById('tool-grid').style.display = '';
        }
        function showToast(msg) {
            const t = document.getElementById('copy-toast');
            t.textContent = msg || 'Copied!';
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 1500);
        }
        function copyResult(id) {
            const el = document.getElementById(id);
            const text = el.value !== undefined ? el.value : el.textContent;
            navigator.clipboard.writeText(text).then(() => showToast('Copied!')).catch(() => showToast('Copy failed'));
        }

        // ═══════════════════════════════════════════════════════════
        // PDF VIEWER
        // ═══════════════════════════════════════════════════════════
        let pdfDoc = null, pdfPageNum = 1, pdfScale = 1.0;
        if (window.pdfjsLib) pdfjsLib.GlobalWorkerOptions.workerSrc = 'vendor/pdf.worker.min.js';

        function setupDrop(dropId, fileId, handler) {
            const drop = document.getElementById(dropId);
            const file = document.getElementById(fileId);
            if (!drop || !file) return;
            ['dragenter', 'dragover'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.add('dragover'); }));
            ['dragleave', 'drop'].forEach(e => drop.addEventListener(e, ev => { ev.preventDefault(); drop.classList.remove('dragover'); }));
            drop.addEventListener('drop', ev => { if (ev.dataTransfer.files.length) handler(ev.dataTransfer.files[0]); });
            file.addEventListener('change', ev => { if (ev.target.files.length) handler(ev.target.files[0]); });
        }

        function loadPDF(file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                pdfjsLib.getDocument({ data: new Uint8Array(e.target.result) }).promise.then(doc => {
                    pdfDoc = doc;
                    pdfPageNum = 1;
                    pdfScale = 1.0;
                    document.getElementById('pdf-page-count').textContent = doc.numPages;
                    document.getElementById('pdf-controls').style.display = 'flex';
                    document.getElementById('pdf-zoom-level').textContent = '100%';
                    renderPDFPage();
                }).catch(err => { alert('Failed to load PDF: ' + err.message); });
            };
            reader.readAsArrayBuffer(file);
        }

        function renderPDFPage() {
            if (!pdfDoc) return;
            pdfDoc.getPage(pdfPageNum).then(page => {
                const viewport = page.getViewport({ scale: pdfScale });
                const container = document.getElementById('pdf-canvas-container');
                container.innerHTML = '';
                const canvas = document.createElement('canvas');
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                container.appendChild(canvas);
                page.render({ canvasContext: canvas.getContext('2d'), viewport });
                document.getElementById('pdf-page-num').textContent = pdfPageNum;
            });
        }
        function pdfPrev() { if (pdfPageNum > 1) { pdfPageNum--; renderPDFPage(); } }
        function pdfNext() { if (pdfDoc && pdfPageNum < pdfDoc.numPages) { pdfPageNum++; renderPDFPage(); } }
        function pdfZoom(delta) { pdfScale = Math.max(0.25, Math.min(4, pdfScale + delta)); document.getElementById('pdf-zoom-level').textContent = Math.round(pdfScale * 100) + '%'; renderPDFPage(); }

        setupDrop('pdf-drop', 'pdf-file', loadPDF);

        // ═══════════════════════════════════════════════════════════
        // IMAGE TOOLS
        // ═══════════════════════════════════════════════════════════
        let imgOriginal = null, imgAspect = 1;

        function loadImage(file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = new Image();
                img.onload = function () {
                    imgOriginal = img;
                    imgAspect = img.width / img.height;
                    document.getElementById('img-preview').src = e.target.result;
                    document.getElementById('img-info').textContent = `${img.width}×${img.height} · ${(file.size / 1024).toFixed(1)}KB · ${file.type.split('/')[1].toUpperCase()}`;
                    document.getElementById('img-width').value = img.width;
                    document.getElementById('img-height').value = img.height;
                    document.getElementById('img-preview-area').style.display = 'block';
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }

        document.getElementById('img-width').addEventListener('input', function () {
            if (document.getElementById('img-lock').checked && imgOriginal) {
                document.getElementById('img-height').value = Math.round(this.value / imgAspect);
            }
        });
        document.getElementById('img-height').addEventListener('input', function () {
            if (document.getElementById('img-lock').checked && imgOriginal) {
                document.getElementById('img-width').value = Math.round(this.value * imgAspect);
            }
        });
        document.getElementById('img-quality').addEventListener('input', function () {
            document.getElementById('img-quality-val').textContent = this.value + '%';
        });

        function convertImage() {
            if (!imgOriginal) return;
            const w = parseInt(document.getElementById('img-width').value) || imgOriginal.width;
            const h = parseInt(document.getElementById('img-height').value) || imgOriginal.height;
            const format = document.getElementById('img-format').value;
            const quality = parseInt(document.getElementById('img-quality').value) / 100;
            const canvas = document.createElement('canvas');
            canvas.width = w; canvas.height = h;
            canvas.getContext('2d').drawImage(imgOriginal, 0, 0, w, h);
            canvas.toBlob(blob => {
                const ext = format.split('/')[1];
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = `converted.${ext}`;
                a.click();
                URL.revokeObjectURL(a.href);
                showToast(`Downloaded as ${ext.toUpperCase()} (${(blob.size / 1024).toFixed(1)}KB)`);
            }, format, quality);
        }

        setupDrop('img-drop', 'img-file', loadImage);

        // ═══════════════════════════════════════════════════════════
        // TEXT TOOLS
        // ═══════════════════════════════════════════════════════════
        function updateTextStats() {
            const text = document.getElementById('text-input').value;
            const chars = text.length;
            const words = text.trim() ? text.trim().split(/\s+/).length : 0;
            const lines = text ? text.split('\n').length : 0;
            const sentences = text.trim() ? text.split(/[.!?]+\s*/g).filter(Boolean).length : 0;
            document.getElementById('text-stats').innerHTML =
                `<span class="stat">📊 ${chars} chars</span><span class="stat">📝 ${words} words</span><span class="stat">📄 ${lines} lines</span><span class="stat">💬 ${sentences} sentences</span>`;
        }

        function textTransform(type) {
            const el = document.getElementById('text-input');
            let t = el.value;
            switch (type) {
                case 'upper': t = t.toUpperCase(); break;
                case 'lower': t = t.toLowerCase(); break;
                case 'title': t = t.replace(/\b\w/g, c => c.toUpperCase()); break;
                case 'sentence': t = t.toLowerCase().replace(/(^|[.!?]\s+)\w/g, c => c.toUpperCase()); break;
                case 'reverse': t = t.split('').reverse().join(''); break;
                case 'sort': t = t.split('\n').sort((a, b) => a.localeCompare(b)).join('\n'); break;
                case 'dedupe': t = [...new Set(t.split('\n'))].join('\n'); break;
                case 'trim': t = t.split('\n').map(l => l.trim()).join('\n'); break;
                case 'number': t = t.split('\n').map((l, i) => `${i + 1}. ${l}`).join('\n'); break;
                case 'removeEmpty': t = t.split('\n').filter(l => l.trim()).join('\n'); break;
            }
            el.value = t;
            updateTextStats();
        }

        function textFindReplace() {
            const el = document.getElementById('text-input');
            const find = document.getElementById('text-find').value;
            if (!find) return;
            const replace = document.getElementById('text-replace').value;
            const count = (el.value.match(new RegExp(find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g')) || []).length;
            el.value = el.value.split(find).join(replace);
            showToast(`Replaced ${count} occurrences`);
            updateTextStats();
        }

        // ═══════════════════════════════════════════════════════════
        // UNIT CONVERTER
        // ═══════════════════════════════════════════════════════════
        const UNITS = {
            temperature: {
                units: ['Celsius', 'Fahrenheit', 'Kelvin'], convert: (v, f, t) => {
                    let c = f === 'Celsius' ? v : f === 'Fahrenheit' ? (v - 32) * 5 / 9 : v - 273.15;
                    return t === 'Celsius' ? c : t === 'Fahrenheit' ? c * 9 / 5 + 32 : c + 273.15;
                }
            },
            weight: { units: ['Grams', 'Kilograms', 'Pounds', 'Ounces', 'Stones', 'Milligrams'], base: [1, 1000, 453.592, 28.3495, 6350.29, 0.001] },
            length: { units: ['Meters', 'Kilometers', 'Miles', 'Feet', 'Inches', 'Centimeters', 'Millimeters', 'Yards'], base: [1, 1000, 1609.34, 0.3048, 0.0254, 0.01, 0.001, 0.9144] },
            data: { units: ['Bytes', 'KB', 'MB', 'GB', 'TB'], base: [1, 1024, 1048576, 1073741824, 1099511627776] },
            time: { units: ['Seconds', 'Minutes', 'Hours', 'Days', 'Weeks', 'Months (30d)', 'Years (365d)'], base: [1, 60, 3600, 86400, 604800, 2592000, 31536000] },
            volume: { units: ['Milliliters', 'Liters', 'Gallons (US)', 'Cups', 'Tablespoons', 'Teaspoons', 'Fluid Oz'], base: [1, 1000, 3785.41, 236.588, 14.7868, 4.92892, 29.5735] }
        };

        function updateUnitOptions() {
            const cat = document.getElementById('unit-category').value;
            const units = UNITS[cat].units;
            ['unit-from', 'unit-to'].forEach((id, idx) => {
                const sel = document.getElementById(id);
                sel.innerHTML = units.map((u, i) => `<option value="${i}" ${i === (idx ? 1 : 0) ? 'selected' : ''}>${u}</option>`).join('');
            });
            convertUnit();
        }

        function convertUnit() {
            const cat = document.getElementById('unit-category').value;
            const val = parseFloat(document.getElementById('unit-from-val').value);
            const fi = parseInt(document.getElementById('unit-from').value);
            const ti = parseInt(document.getElementById('unit-to').value);
            if (isNaN(val)) { document.getElementById('unit-result').textContent = '—'; return; }
            let result;
            if (UNITS[cat].convert) {
                result = UNITS[cat].convert(val, UNITS[cat].units[fi], UNITS[cat].units[ti]);
            } else {
                result = val * UNITS[cat].base[fi] / UNITS[cat].base[ti];
            }
            document.getElementById('unit-result').textContent = parseFloat(result.toPrecision(10));
        }
        updateUnitOptions();

        // ═══════════════════════════════════════════════════════════
        // COLOR PICKER
        // ═══════════════════════════════════════════════════════════
        function hexToRgb(hex) {
            const r = parseInt(hex.slice(1, 3), 16), g = parseInt(hex.slice(3, 5), 16), b = parseInt(hex.slice(5, 7), 16);
            return { r, g, b };
        }
        function rgbToHsl(r, g, b) {
            r /= 255; g /= 255; b /= 255;
            const max = Math.max(r, g, b), min = Math.min(r, g, b), l = (max + min) / 2;
            let h = 0, s = 0;
            if (max !== min) { const d = max - min; s = l > 0.5 ? d / (2 - max - min) : d / (max + min); switch (max) { case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break; case g: h = ((b - r) / d + 2) / 6; break; case b: h = ((r - g) / d + 4) / 6; break; } }
            return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
        }
        function updateColor(hex) {
            document.getElementById('color-picker').value = hex;
            const { r, g, b } = hexToRgb(hex);
            const hsl = rgbToHsl(r, g, b);
            document.getElementById('color-hex').textContent = hex;
            document.getElementById('color-rgb').textContent = `rgb(${r}, ${g}, ${b})`;
            document.getElementById('color-hsl').textContent = `hsl(${hsl.h}, ${hsl.s}%, ${hsl.l}%)`;
        }
        function updateColorFromHex(val) {
            if (/^#[0-9a-fA-F]{6}$/.test(val)) updateColor(val);
        }

        // ═══════════════════════════════════════════════════════════
        // PASSWORD GENERATOR
        // ═══════════════════════════════════════════════════════════
        function generatePassword() {
            const len = parseInt(document.getElementById('pw-length').value);
            let chars = '';
            if (document.getElementById('pw-upper').checked) chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
            if (document.getElementById('pw-lower').checked) chars += 'abcdefghijklmnopqrstuvwxyz';
            if (document.getElementById('pw-digits').checked) chars += '0123456789';
            if (document.getElementById('pw-symbols').checked) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
            if (!chars) { alert('Select at least one character set.'); return; }
            const arr = new Uint32Array(len);
            crypto.getRandomValues(arr);
            let pw = '';
            for (let i = 0; i < len; i++) pw += chars[arr[i] % chars.length];
            document.getElementById('pw-output').textContent = pw;
        }

        // ═══════════════════════════════════════════════════════════
        // QR CODE GENERATOR (Canvas-based, no external library)
        // ═══════════════════════════════════════════════════════════
        function generateQR() {
            const text = document.getElementById('qr-input').value.trim();
            const output = document.getElementById('qr-output');
            const dlBtn = document.getElementById('qr-download');
            if (!text) { output.innerHTML = '<p style="color:var(--parchment-dim);font-size:0.85rem;">Enter text above to generate a QR code</p>'; dlBtn.disabled = true; return; }
            
            output.innerHTML = '';
            const container = document.createElement('div');
            container.style.display = 'inline-block';
            output.appendChild(container);

            try {
                new QRCode(container, {
                    text: text,
                    width: 250,
                    height: 250,
                    colorDark: "#000000",
                    colorLight: "#ffffff",
                    correctLevel: QRCode.CorrectLevel.M
                });
                
                setTimeout(() => {
                    const canvas = container.querySelector('canvas');
                    if (canvas) {
                        canvas.id = 'qr-canvas';
                        canvas.style.border = '4px solid #fff';
                        canvas.style.borderRadius = 'var(--radius)';
                        dlBtn.disabled = false;
                    }
                }, 50);
            } catch (err) {
                output.innerHTML = '<p style="color:#c05030;font-size:0.85rem;">Failed to generate QR code locally.</p>';
                dlBtn.disabled = true;
            }
        }

        function downloadQR() {
            const canvas = document.getElementById('qr-canvas');
            if (!canvas) return;
            const a = document.createElement('a');
            a.href = canvas.toDataURL('image/png');
            a.download = 'qrcode.png';
            a.click();
            showToast('QR code downloaded');
        }

        // ═══════════════════════════════════════════════════════════
        // JSON FORMATTER
        // ═══════════════════════════════════════════════════════════
        function jsonFormat() {
            const el = document.getElementById('json-input');
            try {
                el.value = JSON.stringify(JSON.parse(el.value), null, 2);
                document.getElementById('json-status').innerHTML = '<span style="color:var(--brass-bright);">✅ Formatted successfully</span>';
            } catch (e) {
                document.getElementById('json-status').innerHTML = `<span style="color:#c05030;">❌ ${e.message}</span>`;
            }
        }
        function jsonMinify() {
            const el = document.getElementById('json-input');
            try {
                el.value = JSON.stringify(JSON.parse(el.value));
                document.getElementById('json-status').innerHTML = '<span style="color:var(--brass-bright);">✅ Minified</span>';
            } catch (e) {
                document.getElementById('json-status').innerHTML = `<span style="color:#c05030;">❌ ${e.message}</span>`;
            }
        }
        function jsonValidate() {
            try {
                JSON.parse(document.getElementById('json-input').value);
                document.getElementById('json-status').innerHTML = '<span style="color:var(--brass-bright);">✅ Valid JSON</span>';
            } catch (e) {
                document.getElementById('json-status').innerHTML = `<span style="color:#c05030;">❌ Invalid: ${e.message}</span>`;
            }
        }
    </script>
</body>

</html>
`

## public\workout.html
`html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Workout Routine | Life Hub</title>

    <style>
        :root {
            --bg: #050d12;
            --panel: rgba(8, 22, 30, 0.85);
            --border: rgba(0, 200, 160, 0.15);
            --border-hot: rgba(0, 200, 160, 0.4);
            --green: #00c9a0;
            --yellow: #fbbf24;
            --purple: #a78bfa;
            --red: #f87171;
            --blue: #38bdf8;
            --text: #e8f0f2;
            --dim: rgba(232, 240, 242, 0.5);
            --dim2: rgba(232, 240, 242, 0.25);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            padding-bottom: 4rem;
        }

        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse at 20% 30%, rgba(0, 200, 160, 0.06) 0%, transparent 60%), radial-gradient(ellipse at 80% 70%, rgba(167, 139, 250, 0.05) 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
        }

        .app {
            max-width: 900px;
            margin: 0 auto;
            padding: 1.5rem 1rem;
            position: relative;
            z-index: 1;
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: .4rem;
            color: var(--green);
            text-decoration: none;
            font-size: .85rem;
            margin-bottom: 1.25rem;
            opacity: .7;
            transition: opacity .2s;
        }

        .back-link:hover {
            opacity: 1;
        }

        header {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1.5rem;
        }

        .header-img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            object-position: center 30%;
            display: block;
            opacity: .8;
        }

        .header-body {
            padding: 1.25rem 1.5rem 1.5rem;
        }

        header h1 {
            font-size: 1.8rem;
            color: var(--green);
            letter-spacing: 1px;
            margin-bottom: .3rem;
        }

        header p {
            color: var(--dim);
            font-size: .9rem;
        }

        .chips {
            display: flex;
            flex-wrap: wrap;
            gap: .4rem;
            margin-top: .75rem;
        }

        .chip {
            font-size: .72rem;
            padding: .2rem .65rem;
            border-radius: 20px;
            border: 1px solid;
            background: rgba(0, 0, 0, .3);
        }

        .chip.g {
            border-color: rgba(0, 201, 160, .3);
            color: var(--green);
        }

        .chip.y {
            border-color: rgba(251, 191, 36, .3);
            color: var(--yellow);
        }

        .chip.p {
            border-color: rgba(167, 139, 250, .3);
            color: var(--purple);
        }

        /* tabs */
        .tabs {
            display: flex;
            flex-wrap: wrap;
            gap: .4rem;
            margin-bottom: 1.25rem;
        }

        .tab {
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            color: var(--dim);
            padding: .45rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-family: system-ui, -apple-system, sans-serif;
            font-size: .85rem;
            transition: all .2s;
        }

        .tab.active,
        .tab:hover {
            border-color: var(--green);
            color: var(--green);
            background: rgba(0, 201, 160, .08);
        }

        .pane {
            display: none;
        }

        .pane.active {
            display: block;
        }

        /* section */
        .section {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1rem;
        }

        .section h2 {
            font-size: 1rem;
            color: var(--yellow);
            font-family: ui-monospace, monospace;
            letter-spacing: 1px;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }

        .section-note {
            font-size: .82rem;
            color: var(--dim);
            margin-bottom: 1rem;
            padding: .6rem .9rem;
            border-left: 3px solid var(--border);
            background: rgba(0, 0, 0, .2);
            border-radius: 0 4px 4px 0;
        }

        /* exercise cards */
        .ex-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
            gap: .9rem;
        }

        .ex-card {
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            transition: border-color .2s;
        }

        .ex-card:hover {
            border-color: var(--border-hot);
        }

        .ex-fig {
            background: rgba(0, 0, 0, .5);
            height: 130px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3.5rem;
            border-bottom: 1px solid var(--border);
            position: relative;
        }

        .ex-fig svg {
            width: 80px;
            height: 110px;
        }

        .ex-body {
            padding: .85rem;
        }

        .ex-name {
            font-weight: 600;
            font-size: .95rem;
            color: var(--text);
            margin-bottom: .25rem;
        }

        .ex-sets {
            font-size: .78rem;
            color: var(--yellow);
            font-family: ui-monospace, monospace;
            letter-spacing: .5px;
            margin-bottom: .5rem;
        }

        .ex-equip {
            font-size: .72rem;
            color: var(--purple);
            margin-bottom: .5rem;
        }

        .ex-cues {
            list-style: none;
            padding: 0;
        }

        .ex-cues li {
            font-size: .78rem;
            color: var(--dim);
            padding: .2rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, .04);
            padding-left: .9rem;
            position: relative;
        }

        .ex-cues li::before {
            content: '›';
            position: absolute;
            left: 0;
            color: var(--green);
        }

        .ex-cues li:last-child {
            border-bottom: none;
        }

        .injury-flag {
            font-size: .7rem;
            color: #f87171;
            margin-top: .4rem;
            padding: .25rem .5rem;
            background: rgba(248, 113, 113, .08);
            border-radius: 3px;
            border: 1px solid rgba(248, 113, 113, .2);
        }

        /* mob steps */
        .mob-list {
            list-style: none;
        }

        .mob-list li {
            display: flex;
            gap: .75rem;
            align-items: flex-start;
            padding: .65rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, .05);
        }

        .mob-list li:last-child {
            border-bottom: none;
        }

        .mob-icon {
            font-size: 1.4rem;
            flex-shrink: 0;
            margin-top: -.1rem;
        }

        .mob-text strong {
            display: block;
            font-size: .9rem;
            color: var(--text);
        }

        .mob-text span {
            font-size: .78rem;
            color: var(--dim);
        }

        /* table */
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: .83rem;
        }

        th {
            padding: .5rem .75rem;
            background: rgba(0, 0, 0, .4);
            color: var(--dim2);
            text-align: left;
            font-weight: 500;
            border-bottom: 1px solid var(--border);
        }

        td {
            padding: .55rem .75rem;
            border-bottom: 1px solid rgba(255, 255, 255, .04);
            color: var(--text);
            vertical-align: top;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .tag {
            display: inline-block;
            font-size: .68rem;
            padding: .15rem .45rem;
            border-radius: 3px;
            font-weight: 600;
        }

        .tag.rest {
            background: rgba(248, 113, 113, .12);
            color: var(--red);
            border: 1px solid rgba(248, 113, 113, .2);
        }

        .tag.train {
            background: rgba(0, 201, 160, .1);
            color: var(--green);
            border: 1px solid rgba(0, 201, 160, .2);
        }

        .tag.light {
            background: rgba(167, 139, 250, .1);
            color: var(--purple);
            border: 1px solid rgba(167, 139, 250, .2);
        }

        /* phase bars */
        .phase {
            display: flex;
            gap: .75rem;
            align-items: flex-start;
            padding: .8rem;
            background: rgba(0, 0, 0, .3);
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: .6rem;
        }

        .phase-num {
            font-family: ui-monospace, monospace;
            font-size: 1.5rem;
            color: var(--green);
            min-width: 2rem;
            text-align: center;
            line-height: 1;
        }

        .phase-num.p2 {
            color: var(--yellow);
        }

        .phase-num.p3 {
            color: var(--purple);
        }

        .phase-body strong {
            display: block;
            font-size: .9rem;
            color: var(--text);
        }

        .phase-body span {
            font-size: .78rem;
            color: var(--dim);
        }

        @media(max-width:600px) {
            .ex-grid {
                grid-template-columns: 1fr;
            }

            .header-img {
                height: 130px;
            }

            .header-body {
                padding: 1rem;
            }
        }
    </style>
</head>

<body>
    <div class="app">
        <a href="index.html" class="back-link">← Life Hub</a>

        <header>
            <img src="reports/workout-header.png" alt="Workout" class="header-img">
            <div class="header-body">
                <h1>💪 Home Workout Routine</h1>
                <p>Personalised for your equipment, schedule, shift-work recovery, and injury prevention.</p>
                <div class="chips">
                    <span class="chip g">3–4 days/week</span>
                    <span class="chip g">45 min/session</span>
                    <span class="chip y">Post-nap timing</span>
                    <span class="chip y">No gym needed</span>
                    <span class="chip p">Injury prevention</span>
                    <span class="chip p">Starts Monday 17 Mar</span>
                </div>
            </div>
        </header>

        <div class="tabs">
            <button class="tab active" onclick="show('overview',this)">📋 Overview</button>
            <button class="tab" onclick="show('sessionA',this)">🦵 Session A</button>
            <button class="tab" onclick="show('sessionB',this)">💪 Session B</button>
            <button class="tab" onclick="show('sessionC',this)">⚡ Session C</button>
            <button class="tab" onclick="show('mobility',this)">🧘 Mobility</button>
            <button class="tab" onclick="show('schedule',this)">📅 Schedule</button>
        </div>

        <!-- OVERVIEW -->
        <div class="pane active" id="overview">
            <div class="section">
                <h2>🗂 YOUR EQUIPMENT</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Equipment</th>
                            <th>Primary Use</th>
                        </tr>
                    </thead>
                    <tbody id="equip-table"></tbody>
                </table>
            </div>
            <div class="section" style="margin-top:1rem;">
                <h2>⚠ INJURY PREVENTION TARGETS</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Zone</th>
                            <th>Risk</th>
                            <th>Fix</th>
                        </tr>
                    </thead>
                    <tbody id="injury-table"></tbody>
                </table>
            </div>
            <div class="section" style="margin-top:1rem;">
                <h2>📈 PHASES</h2>
                <div id="phases"></div>
            </div>
        </div>

        <!-- SESSION A -->
        <div class="pane" id="sessionA">
            <div class="section">
                <h2>🦵 SESSION A — LOWER BODY</h2>
                <div class="section-note">Best on <strong>Tuesday</strong> post-nap (~3pm). ~45 min. Glute &amp;
                    hamstring focus. Protects your lower back and knees.</div>
                <div class="ex-grid" id="ex-a"></div>
            </div>
        </div>

        <!-- SESSION B -->
        <div class="pane" id="sessionB">
            <div class="section">
                <h2>💪 SESSION B — UPPER BODY</h2>
                <div class="section-note">Best on <strong>Wednesday</strong> post-nap or <strong>Saturday</strong>
                    morning. ~45 min. Counters shoulder rounding from shifts.</div>
                <div class="ex-grid" id="ex-b"></div>
            </div>
        </div>

        <!-- SESSION C -->
        <div class="pane" id="sessionC">
            <div class="section">
                <h2>⚡ SESSION C — FULL BODY POWER</h2>
                <div class="section-note">Best on <strong>Thursday</strong> post-nap (~2:30pm). ~45 min. KB swing is the
                    centrepiece — builds everything.</div>
                <div class="ex-grid" id="ex-c"></div>
            </div>
        </div>

        <!-- MOBILITY -->
        <div class="pane" id="mobility">
            <div class="section">
                <h2>🔥 5-MIN OPENER — EVERY SESSION</h2>
                <div class="section-note">Do this before every strength session, after 5 min on the bike.
                    Non-negotiable.</div>
                <ul class="mob-list" id="mob-opener"></ul>
            </div>
            <div class="section" style="margin-top:1rem;">
                <h2>🌅 DAILY PRE-SHIFT HABIT — 5 MIN</h2>
                <div class="section-note">Before any BP shift. Undoes shift-work damage before it compounds.</div>
                <ul class="mob-list" id="mob-daily"></ul>
            </div>
        </div>

        <!-- SCHEDULE -->
        <div class="pane" id="schedule">
            <div class="section">
                <h2>📅 WEEK 1 SCHEDULE — 17 MARCH</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Date</th>
                            <th>Plan</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="schedule-table"></tbody>
                </table>
            </div>
            <div class="section" style="margin-top:1rem;">
                <h2>⏱ SESSION STRUCTURE</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Block</th>
                            <th>Duration</th>
                            <th>What</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Warm-up</td>
                            <td>5 min</td>
                            <td>Bike — low resistance, get blood moving</td>
                        </tr>
                        <tr>
                            <td>Mobility opener</td>
                            <td>5 min</td>
                            <td>5 movements (see Mobility tab)</td>
                        </tr>
                        <tr>
                            <td>Strength work</td>
                            <td>30–35 min</td>
                            <td>Main exercises from the session</td>
                        </tr>
                        <tr>
                            <td>Cool-down</td>
                            <td>5 min</td>
                            <td>Session-specific stretches</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // ── SVG exercise figure helpers ──────────────────────────────────────
        const svgs = {
            squat: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="12" r="8" fill="#00c9a0"/>
    <line x1="40" y1="20" x2="40" y2="52" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="30" x2="18" y2="42" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="30" x2="62" y2="42" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="52" x2="22" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="52" x2="58" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="72" x2="18" y2="95" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="58" y1="72" x2="62" y2="95" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <rect x="14" y="38" width="8" height="14" rx="3" fill="#fbbf24" opacity=".8"/>
    <rect x="58" y="38" width="8" height="14" rx="3" fill="#fbbf24" opacity=".8"/>
  </svg>`,
            rdl: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="58" cy="14" r="8" fill="#00c9a0"/>
    <line x1="58" y1="22" x2="40" y2="52" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="49" y1="37" x2="28" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="49" y1="37" x2="38" y2="15" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="52" x2="45" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="52" x2="28" y2="55" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="28" y1="55" x2="28" y2="75" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="45" y1="85" x2="50" y2="100" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="20" cy="23" r="5" fill="#fbbf24" opacity=".7"/>
  </svg>`,
            hipthrust: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="70" width="64" height="12" rx="4" fill="#1e3a3a"/>
    <circle cx="40" cy="52" r="8" fill="#00c9a0"/>
    <line x1="40" y1="60" x2="40" y2="72" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="65" x2="18" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="18" y1="72" x2="14" y2="95" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="65" x2="62" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="62" y1="72" x2="66" y2="95" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="33" y1="60" x2="12" y2="65" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="47" y1="60" x2="68" y2="65" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
  </svg>`,
            swing: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="48" cy="12" r="8" fill="#00c9a0"/>
    <line x1="48" y1="20" x2="40" y2="50" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="44" y1="35" x2="22" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="44" y1="35" x2="60" y2="22" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="50" x2="26" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="50" x2="54" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="26" y1="72" x2="20" y2="98" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="54" y1="72" x2="60" y2="98" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <rect x="13" y="22" width="12" height="14" rx="3" fill="#fbbf24" opacity=".8"/>
  </svg>`,
            row: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="55" cy="18" r="8" fill="#00c9a0"/>
    <line x1="55" y1="26" x2="42" y2="52" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="48" y1="39" x2="62" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="62" y1="48" x2="20" y2="42" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="48" y1="39" x2="30" y2="34" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="30" y1="34" x2="18" y2="62" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="42" y1="52" x2="44" y2="80" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="42" y1="52" x2="30" y2="55" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="30" y1="55" x2="28" y2="80" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="18" cy="40" r="5" fill="#fbbf24" opacity=".7"/>
  </svg>`,
            press: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="62" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="38" x2="16" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="16" y1="28" x2="14" y2="12" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="38" x2="64" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="25" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="55" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="25" y1="85" x2="22" y2="102" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="55" y1="85" x2="58" y2="102" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="12" cy="10" r="5" fill="#fbbf24" opacity=".7"/>
  </svg>`,
            splitSq: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="38" cy="12" r="8" fill="#00c9a0"/>
    <line x1="38" y1="20" x2="38" y2="52" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="32" x2="16" y2="38" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="32" x2="58" y2="36" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="52" x2="22" y2="78" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="78" x2="20" y2="100" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="52" x2="56" y2="58" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="56" y1="58" x2="62" y2="80" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <rect x="58" y="78" width="14" height="8" rx="3" fill="#1e3a3a"/>
    <rect x="62" y="80" width="10" height="4" rx="2" fill="#334"/>
  </svg>`,
            pullApart: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="62" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="38" x2="12" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="38" x2="68" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="12" y1="48" x2="68" y2="48" stroke="#a78bfa" stroke-width="2.5" stroke-dasharray="4 2" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="28" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="52" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="28" y1="85" x2="26" y2="100" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="52" y1="85" x2="54" y2="100" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
  </svg>`,
            stepup: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="30" y="75" width="42" height="14" rx="3" fill="#1e3a3a"/>
    <circle cx="38" cy="18" r="8" fill="#00c9a0"/>
    <line x1="38" y1="26" x2="38" y2="58" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="36" x2="16" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="36" x2="60" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="58" x2="44" y2="78" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="58" x2="24" y2="70" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="44" y1="78" x2="46" y2="90" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="16" y1="44" x2="14" y2="60" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
  </svg>`,
            calf: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="28" y="88" width="8" height="16" rx="2" fill="#1e3a3a"/>
    <rect x="44" y="88" width="8" height="16" rx="2" fill="#1e3a3a"/>
    <circle cx="40" cy="18" r="8" fill="#00c9a0"/>
    <line x1="40" y1="26" x2="40" y2="58" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="36" x2="18" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="36" x2="62" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="58" x2="30" y2="78" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="58" x2="50" y2="78" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="30" y1="78" x2="30" y2="90" stroke="#00c9a0" stroke-width="3"/>
    <line x1="50" y1="78" x2="50" y2="90" stroke="#00c9a0" stroke-width="3"/>
    <line x1="28" y1="90" x2="36" y2="80" stroke="#fbbf24" stroke-width="2" stroke-dasharray="3 2"/>
  </svg>`,
            lateral: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="62" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="40" x2="10" y2="30" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="40" x2="70" y2="30" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="8" cy="29" r="4" fill="#fbbf24" opacity=".8"/>
    <circle cx="72" cy="29" r="4" fill="#fbbf24" opacity=".8"/>
    <line x1="40" y1="62" x2="28" y2="88" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="52" y2="88" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="28" y1="88" x2="26" y2="102" stroke="#00c9a0" stroke-width="3"/>
    <line x1="52" y1="88" x2="54" y2="102" stroke="#00c9a0" stroke-width="3"/>
  </svg>`,
            pushup: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="42" r="8" fill="#00c9a0"/>
    <line x1="24" y1="46" x2="50" y2="52" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="22" y1="40" x2="34" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="34" y1="28" x2="38" y2="40" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="50" y1="52" x2="60" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="50" y1="52" x2="64" y2="70" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="60" y1="44" x2="64" y2="70" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
  </svg>`,
            deadlift: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="16" r="8" fill="#00c9a0"/>
    <line x1="40" y1="24" x2="40" y2="55" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="36" x2="14" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="36" x2="66" y2="48" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="14" y1="48" x2="16" y2="68" stroke="#00c9a0" stroke-width="3"/>
    <line x1="66" y1="48" x2="64" y2="68" stroke="#00c9a0" stroke-width="3"/>
    <circle cx="16" cy="70" r="6" fill="#fbbf24" opacity=".8" stroke="#fbbf24"/>
    <circle cx="64" cy="70" r="6" fill="#fbbf24" opacity=".8" stroke="#fbbf24"/>
    <line x1="40" y1="55" x2="26" y2="80" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="55" x2="54" y2="80" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="26" y1="80" x2="24" y2="98" stroke="#00c9a0" stroke-width="3"/>
    <line x1="54" y1="80" x2="56" y2="98" stroke="#00c9a0" stroke-width="3"/>
  </svg>`,
            abduct: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="38" cy="18" r="8" fill="#00c9a0"/>
    <line x1="38" y1="26" x2="38" y2="60" stroke="#00c9a0" stroke-width="3"/>
    <line x1="38" y1="36" x2="16" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="36" x2="60" y2="42" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="60" x2="30" y2="82" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="38" y1="60" x2="55" y2="72" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="30" y1="82" x2="28" y2="100" stroke="#00c9a0" stroke-width="3"/>
    <line x1="55" y1="72" x2="62" y2="90" stroke="#00c9a0" stroke-width="3"/>
    <line x1="28" y1="70" x2="50" y2="78" stroke="#a78bfa" stroke-width="2" stroke-dasharray="3 2"/>
  </svg>`,
            facepull: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="62" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="38" x2="14" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="38" x2="66" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="70" y1="26" x2="78" y2="28" stroke="#a78bfa" stroke-width="2.5" stroke-dasharray="4 2"/>
    <line x1="40" y1="62" x2="28" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="52" y2="85" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="28" y1="85" x2="26" y2="100" stroke="#00c9a0" stroke-width="3"/>
    <line x1="52" y1="85" x2="54" y2="100" stroke="#00c9a0" stroke-width="3"/>
  </svg>`,
            curl: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="62" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="38" x2="18" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="18" y1="44" x2="16" y2="28" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <circle cx="14" cy="25" r="4" fill="#fbbf24" opacity=".9"/>
    <line x1="40" y1="38" x2="62" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="62" y1="44" x2="64" y2="62" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="62" x2="28" y2="85" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="62" x2="52" y2="85" stroke="#00c9a0" stroke-width="3"/>
    <line x1="28" y1="85" x2="26" y2="100" stroke="#00c9a0" stroke-width="3"/>
    <line x1="52" y1="85" x2="54" y2="100" stroke="#00c9a0" stroke-width="3"/>
  </svg>`,
            dips: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="60" width="64" height="8" rx="3" fill="#1e3a3a"/>
    <circle cx="40" cy="20" r="8" fill="#00c9a0"/>
    <line x1="40" y1="28" x2="40" y2="52" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="36" x2="14" y2="58" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="36" x2="66" y2="58" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="52" x2="28" y2="75" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="52" x2="52" y2="75" stroke="#00c9a0" stroke-width="3"/>
    <line x1="28" y1="75" x2="26" y2="95" stroke="#00c9a0" stroke-width="3"/>
    <line x1="52" y1="75" x2="54" y2="95" stroke="#00c9a0" stroke-width="3"/>
  </svg>`,
            generic: `<svg viewBox="0 0 80 110" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="16" r="8" fill="#00c9a0"/>
    <line x1="40" y1="24" x2="40" y2="58" stroke="#00c9a0" stroke-width="3"/>
    <line x1="40" y1="34" x2="16" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="34" x2="64" y2="44" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="58" x2="26" y2="82" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="40" y1="58" x2="54" y2="82" stroke="#00c9a0" stroke-width="3" stroke-linecap="round"/>
    <line x1="26" y1="82" x2="24" y2="100" stroke="#00c9a0" stroke-width="3"/>
    <line x1="54" y1="82" x2="56" y2="100" stroke="#00c9a0" stroke-width="3"/>
  </svg>`
        };

        // ── Data ──────────────────────────────────────────────────────────────
        const EQUIP = [
            ['10kg Dumbbell', 'Main load — squats, rows, shoulder press, RDL'],
            ['8kg Kettlebell', 'Swings, goblet squats, halos, deadlift'],
            ['2× 3kg Dumbbells', 'Shoulder health — lateral raises, rear delt flies'],
            ['2× 5kg Disks', 'Step-up load, hip extension holds'],
            ['Resistance Bands', 'Face pulls, hip abduction, banded squats, rows'],
            ['Workout Bench', 'Hip thrusts, Bulgarian split squats, pressing, dips'],
            ['Staircase', 'Calf raises, step-ups, sprint finishers'],
            ['Exercise Bike', 'Warm-up every session, cardio, active recovery'],
        ];

        const INJURY = [
            ['Lower back', 'Standing shifts + weak posterior chain', 'Hip thrusts + RDL every session. No loaded spinal flexion until Week 8.'],
            ['Knees', 'Glute weakness from prolonged standing', 'Hip abduction + split squats + VMO squats. Knees track over pinky toe.'],
            ['Hip flexors', 'Constant standing/slight forward lean', 'World\'s Greatest Stretch daily + KB swings counteract it.'],
            ['Shoulders', 'Forward rounding from work posture', 'Face pulls + pull-aparts every session. Never skip.'],
            ['Calves/Ankles', '8-hour standing shifts', 'Stair calf raises + band ankle work built into every session.'],
        ];

        const PHASES = [
            { n: '01', cls: '', w: 'Weeks 1–4', focus: 'Foundation', detail: 'Learn the movements. 2–3 reps in reserve every set. 3 sessions/week. Form first, weight second.' },
            { n: '02', cls: 'p2', w: 'Weeks 5–8', focus: 'Build', detail: 'Add Wednesday (4th session). Increase tempo (3-sec lowering). Push to 1–2 RIR. Shorten rest by 10s.' },
            { n: '03', cls: 'p3', w: 'Weeks 9–12', focus: 'Intensity', detail: 'Add 4th set to main lifts. Timed rests: 90s compound, 60s isolation. Heavier band variants.' },
        ];

        const EX_A = [
            { name: 'Goblet Squat', sets: '3 × 12', equip: '8kg Kettlebell', svg: 'squat', cues: ['Hold KB at chest, heels shoulder-width', '3-sec descent — slow is strong', 'Drive through heels, squeeze glutes at top', 'Keep chest up, don\'t round forward'], injury: 'Heels rising? Widen stance or add small heel elevation.' },
            { name: 'Single-Leg Romanian Deadlift', sets: '3 × 8 each', equip: '10kg Dumbbell', svg: 'rdl', cues: ['Hinge at hips — NOT a squat', 'Feel the hamstring stretch behind standing knee', 'Bench nearby for balance in Week 1–2', 'Slow and controlled beats heavy and sloppy'], injury: 'Lower back rounding = hips too high. Think proud chest.' },
            { name: 'Hip Thrust', sets: '3 × 15', equip: 'Bench + Band', svg: 'hipthrust', cues: ['Band across hips (doubles the resistance)', 'Upper back on bench edge, feet flat', 'Drive through heels — hips slam up high', '2-second squeeze at the top. Every rep.'], injury: 'THE most important exercise for protecting your lower back.' },
            { name: 'Step-Ups', sets: '3 × 10 each', equip: 'Bench + 5kg disks', svg: 'stepup', cues: ['Full foot on bench — no heel hanging', 'Drive through front heel, don\'t push off back foot', 'Full lockout at top before stepping down', 'Slow descent = stronger glutes'], injury: 'Feel knee pain? Lower the step height first.' },
            { name: 'Banded Hip Abduction', sets: '3 × 20 each', equip: 'Resistance Band', svg: 'abduct', cues: ['Band just above knees, standing', 'Slow controlled lift — no swinging', 'Feel gluteus medius (outer hip) burning', 'Don\'t let your pelvis tilt side to side'], injury: 'Weak abductors = knee caves on squats. Fix this first.' },
            { name: 'Stair Calf Raises', sets: '3 × 20', equip: 'Staircase', svg: 'calf', cues: ['Toes on step edge, heels hanging off', 'Full range: deep stretch at bottom, high at top', '3-second hold at the top', 'Uni or bilateral — single leg is harder'], injury: 'Essential for shift workers. Standing 8h destroys calves.' },
        ];

        const EX_B = [
            { name: 'Single-Arm DB Row', sets: '3 × 10 each', equip: '10kg Dumbbell + Bench', svg: 'row', cues: ['Knee and hand on bench for support', 'Elbow drives straight back — not up or out', 'Full stretch at bottom, full squeeze at top', 'Keep spine neutral — don\'t rotate to get more range'], injury: 'Most people use too much weight here. Feel it in the back, not the bicep.' },
            { name: 'Single-Arm DB Press', sets: '3 × 10 each', equip: '10kg Dumbbell + Bench', svg: 'press', cues: ['Seated on bench = safer for lower back', 'Control the descent — 3 seconds down', 'Don\'t let elbow flare past 45°', 'Brace core on every rep'], injury: 'Shoulder clicking? Start with neutral grip (thumb up).' },
            { name: 'Band Pull-Aparts', sets: '3 × 20', equip: 'Resistance Band', svg: 'pullApart', cues: ['Band at shoulder height, arms straight', 'Pull band apart to chest level', 'Pinch shoulder blades together at end', 'Slow and controlled — never snap the band'], injury: 'Do this EVERY session. Fixes the forward-shoulder posture from shifts.' },
            { name: 'Lateral Raise', sets: '3 × 15', equip: '2× 3kg Dumbbells', svg: 'lateral', cues: ['Slight forward torso lean (10°)', 'Pinky slightly higher than thumb at top', 'Stop at shoulder height — no higher', 'Pause 1 second at top, slow down'], injury: '3kg will feel light — but proper form means tempo matters more than weight.' },
            { name: 'Rear Delt Fly', sets: '3 × 15', equip: '2× 3kg Dumbbells', svg: 'lateral', cues: ['Hinge forward 45°, chest toward bench', 'Lift arms out to sides like wings', 'Think: stretch across upper back', 'Avoid shrugging — traps should stay down'], injury: 'Counteracts the rounded-forward posture from standing at a counter.' },
            { name: 'Tricep Dips', sets: '3 × 10', equip: 'Bench', svg: 'dips', cues: ['Hands on bench edge, fingers forward', 'Lower until elbows hit 90° — no further', 'Elbows track back, not out to the sides', 'Feet flat and closer = easier. Farther = harder'], injury: 'Sharp shoulder pain? Use a slightly wider hand position.' },
            { name: 'Push-Up', sets: '3 × max (8–15)', equip: 'Bodyweight', svg: 'pushup', cues: ['Incline on bench edge in Week 1–2', 'Hollow body the whole time — no snaking hips', 'Elbows 45° from body — not straight out', 'Touch chest to surface every rep'], injury: 'Incline push-ups are not cheating — they\'re a training tool.' },
        ];

        const EX_C = [
            { name: 'Kettlebell Swing', sets: '4 × 15', equip: '8kg Kettlebell', svg: 'swing', cues: ['Hip hinge — NOT a squat. Hinge back hard.', 'KB swings back between legs (high), then hips SNAP forward', 'Arms stay connected to hips through the backswing', 'Watch a 30-sec tutorial first. The hip snap is everything.'], injury: 'THE most important exercise here. Glutes, hamstrings, posture, calorie burn.' },
            { name: 'Bulgarian Split Squat', sets: '3 × 8 each', equip: '8kg KB + Bench', svg: 'splitSq', cues: ['Back foot elevated on bench, front foot forward', 'Front knee stays over foot — never past toes', 'Slow descent 3 seconds down', 'Week 1: just bodyweight. Add KB Week 3.'], injury: 'Hardest leg exercise in the program. Unilateral = no hiding weak side.' },
            { name: 'KB Deadlift', sets: '3 × 8', equip: 'KB + 10kg DB (one each hand)', svg: 'deadlift', cues: ['Both implements at sides, hinge back', 'Spine neutral, brace core before each rep', 'Drive floor away — don\'t yank it up', 'Feel the hamstrings, not the lower back'], injury: 'Back rounding = ego weight. Drop the load, not the tension.' },
            { name: 'Banded Face Pull', sets: '3 × 20', equip: 'Resistance Band', svg: 'facepull', cues: ['Band at nose height, anchored to door/stairs', 'Pull to ears — elbows HIGH and wide', 'Rotate wrists out at end of pull', 'Every. Single. Session. Non-negotiable.'], injury: 'Protects rotator cuff. Critical for retail workers leaning over counters.' },
            { name: 'Band Bicep Curl', sets: '2 × 15', equip: 'Resistance Band', svg: 'curl', cues: ['Stand on band, symmetrical tension', 'Elbows pinned to sides — don\'t swing', 'Full extension at bottom each rep', 'Squeeze hard at top for 1 second'], injury: 'Supinator motion: rotate wrist outward as you curl.' },
        ];

        const MOB_OPENER = [
            { icon: '🌍', name: "World's Greatest Stretch", detail: '× 3 each side · Hip flexor + T-spine + hip rotation in one move. Lunge forward, elbow to ground, then rotate arm to sky.' },
            { icon: '📖', name: 'Book Opener (Thoracic Rotation)', detail: '× 8 each side · Lie on side, both arms forward, knees on floor. Rotate top arm open toward ceiling. Follow with eyes.' },
            { icon: '🦶', name: 'Banded Ankle Dorsiflexion', detail: '× 10 each foot · Band around ankle, step forward. Drive knee forward over toes, heel stays down. Protects knee mechanics.' },
            { icon: '🌀', name: 'Hip Circles', detail: '× 10 each direction · Hands on hips, full hip circles. Loosens the chronic tightness from standing shifts.' },
            { icon: '⚫', name: 'KB Halo', detail: '× 5 each way · 8kg KB, circle around head, slow and controlled. Shoulder warm-up, rotator cuff activation.' },
        ];

        const MOB_DAILY = [
            { icon: '🧎', name: 'Kneeling Hip Flexor Stretch', detail: '30s each side · Knee on floor, lean forward, squeeze opposite glute. Priority #1 for retail workers.' },
            { icon: '🪑', name: 'Seated Piriformis / Figure-4', detail: '45s each side · Ankle on knee, lean forward. SI joint, outer hip, glute. Reduces back pain from standing.' },
            { icon: '🧱', name: 'Calf + Achilles Wall Stretch', detail: '20s each leg · Hands on wall, heel down. Prevents plantar fasciitis from long shifts.' },
            { icon: '🪑', name: 'Thoracic Extension over Bench', detail: '30s · Upper back on bench edge, let chest drop open. Undoes the forward-rounding from leaning over all day.' },
        ];

        const SCHED = [
            { day: 'Monday 17', status: 'rest', plan: '15-min mobility only (hip flexors, thoracic, calves)', time: 'Anytime' },
            { day: 'Tuesday 18', status: 'train', plan: 'Session A — Lower Body', time: '~3pm post-nap' },
            { day: 'Wednesday 19', status: 'rest', plan: 'Rest — or 20-min bike if feeling good', time: 'Optional' },
            { day: 'Thursday 20', status: 'train', plan: 'Session C — Full Body Power', time: '~2:30pm post-nap' },
            { day: 'Friday 21', status: 'light', plan: 'Pre-shift 5-min mobility habit only', time: 'Before shift' },
            { day: 'Saturday 22', status: 'train', plan: 'Session B — Upper Body', time: '~11:45am (before shift)' },
            { day: 'Sunday 23', status: 'rest', plan: 'Rest', time: '—' },
        ];

        // ── Render functions ───────────────────────────────────────────────────
        function show(id, btn) {
            document.querySelectorAll('.pane').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            btn.classList.add('active');
        }

        function exCard(ex) {
            const svg = svgs[ex.svg] || svgs.generic;
            const cuesHtml = ex.cues.map(c => `<li>${c}</li>`).join('');
            const injHtml = ex.injury ? `<div class="injury-flag">⚠ ${ex.injury}</div>` : '';
            return `<div class="ex-card">
    <div class="ex-fig">${svg}</div>
    <div class="ex-body">
      <div class="ex-name">${ex.name}</div>
      <div class="ex-sets">${ex.sets}</div>
      <div class="ex-equip">🔧 ${ex.equip}</div>
      <ul class="ex-cues">${cuesHtml}</ul>
      ${injHtml}
    </div>
  </div>`;
        }

        function init() {
            // equip table
            document.getElementById('equip-table').innerHTML = EQUIP.map(([e, u]) => `<tr><td><strong>${e}</strong></td><td style="color:var(--dim)">${u}</td></tr>`).join('');
            // injury table
            document.getElementById('injury-table').innerHTML = INJURY.map(([z, r, f]) => `<tr><td><strong>${z}</strong></td><td style="color:var(--red);font-size:.8rem">${r}</td><td style="font-size:.8rem;color:var(--dim)">${f}</td></tr>`).join('');
            // phases
            document.getElementById('phases').innerHTML = PHASES.map(p => `<div class="phase"><div class="phase-num ${p.cls}">${p.n}</div><div class="phase-body"><strong>${p.w} — ${p.focus}</strong><span>${p.detail}</span></div></div>`).join('');
            // exercises
            document.getElementById('ex-a').innerHTML = EX_A.map(exCard).join('');
            document.getElementById('ex-b').innerHTML = EX_B.map(exCard).join('');
            document.getElementById('ex-c').innerHTML = EX_C.map(exCard).join('');
            // mobility
            const mobLi = m => `<li><span class="mob-icon">${m.icon}</span><div class="mob-text"><strong>${m.name}</strong><span>${m.detail}</span></div></li>`;
            document.getElementById('mob-opener').innerHTML = MOB_OPENER.map(mobLi).join('');
            document.getElementById('mob-daily').innerHTML = MOB_DAILY.map(mobLi).join('');
            // schedule
            const tagMap = { rest: '🔴 Rest', train: '✅ Train', light: '🔵 Active rest' };
            document.getElementById('schedule-table').innerHTML = SCHED.map(s => `<tr><td><strong>${s.day}</strong></td><td><span class="tag ${s.status}">${tagMap[s.status]}</span></td><td>${s.plan}</td><td style="color:var(--dim2);font-size:.8rem">${s.time}</td></tr>`).join('');
        }

        init();
    </script>
</body>

</html>
`

## public\workshop.html
`html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Workshop | Personal Organizer</title>
            <link

        <style>
        :root {
            /* ── Forge Palette ── */
            --bg-forge: #070504;
            --iron-dark: #181008;
            --iron-panel: rgba(24, 16, 8, 0.85);
            --iron-border: rgba(120, 80, 40, 0.35);
            --copper: #b06028;
            --copper-bright: #c87830;
            --forge-amber: #d08030;
            --brass: #c4a040;
            --brass-bright: #d4b050;
            --rust: #905030;
            --rust-dark: #6a3020;
            --patina: #786040;
            --parchment: #ddd0c0;
            --parchment-dim: #a89880;
            --ember: #d47020;
            --flame-orange: #e08020;
            --flame-red: #c04020;
            --radius: 3px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: var(--bg-forge);
            color: var(--parchment);
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ═══════════════════════════════════════════════════════════
           FORGE BACKGROUND — Asymmetric firelight + visible flames
           ═══════════════════════════════════════════════════════════ */
        .forge-bg {
            position: fixed;
            inset: 0;
            z-index: -1;
            overflow: hidden;
        }

        /* Asymmetric forge glow — right side */
        .forge-glow {
            position: absolute;
            width: 600px;
            height: 600px;
            right: -100px;
            top: 20%;
            background: radial-gradient(ellipse, rgba(208, 128, 48, 0.18) 0%, rgba(192, 64, 32, 0.08) 40%, transparent 70%);
            filter: blur(40px);
            animation: forge-pulse 4s ease-in-out infinite alternate;
        }

        /* Secondary glow — bottom left */
        .forge-glow-2 {
            position: absolute;
            width: 400px;
            height: 300px;
            left: -50px;
            bottom: -50px;
            background: radial-gradient(ellipse, rgba(196, 112, 32, 0.1) 0%, transparent 70%);
            filter: blur(60px);
            animation: forge-pulse 6s ease-in-out infinite alternate-reverse;
        }

        /* Visible flame tongues */
        .flame {
            position: absolute;
            bottom: 0;
            border-radius: 50% 50% 20% 20%;
            filter: blur(20px);
            opacity: 0;
            animation: flame-flicker 3s ease-in-out infinite;
        }

        .flame-1 {
            right: 80px;
            width: 60px;
            height: 120px;
            background: linear-gradient(to top, rgba(192, 64, 32, 0.4), rgba(224, 128, 32, 0.2), transparent);
            animation-delay: 0s;
            animation-duration: 2.5s;
        }

        .flame-2 {
            right: 160px;
            width: 40px;
            height: 90px;
            background: linear-gradient(to top, rgba(208, 112, 32, 0.3), rgba(212, 160, 48, 0.15), transparent);
            animation-delay: -0.7s;
            animation-duration: 3s;
        }

        .flame-3 {
            right: 40px;
            width: 50px;
            height: 100px;
            background: linear-gradient(to top, rgba(176, 48, 24, 0.35), rgba(208, 96, 32, 0.2), transparent);
            animation-delay: -1.4s;
            animation-duration: 2.8s;
        }

        .flame-4 {
            right: 220px;
            width: 35px;
            height: 70px;
            background: linear-gradient(to top, rgba(196, 80, 28, 0.25), rgba(220, 140, 40, 0.12), transparent);
            animation-delay: -2s;
            animation-duration: 3.2s;
        }

        /* Ember particles */
        .ember-particle {
            position: absolute;
            width: 3px;
            height: 3px;
            background: var(--ember);
            border-radius: 50%;
            box-shadow: 0 0 6px var(--forge-amber);
            animation: ember-rise linear infinite;
        }

        .ember-1 {
            right: 100px;
            bottom: 50px;
            animation-duration: 4s;
            animation-delay: 0s;
        }

        .ember-2 {
            right: 180px;
            bottom: 30px;
            animation-duration: 5s;
            animation-delay: -1s;
            width: 2px;
            height: 2px;
        }

        .ember-3 {
            right: 60px;
            bottom: 80px;
            animation-duration: 3.5s;
            animation-delay: -2s;
        }

        .ember-4 {
            right: 140px;
            bottom: 20px;
            animation-duration: 4.5s;
            animation-delay: -0.5s;
            width: 2px;
            height: 2px;
        }

        .ember-5 {
            right: 200px;
            bottom: 60px;
            animation-duration: 5.5s;
            animation-delay: -3s;
        }

        .ember-6 {
            right: 250px;
            bottom: 40px;
            animation-duration: 4s;
            animation-delay: -1.5s;
            width: 2px;
            height: 2px;
        }

        /* Smoke wisps */
        .smoke {
            position: absolute;
            top: 0;
            width: 200px;
            height: 300px;
            background: linear-gradient(180deg, rgba(24, 16, 8, 0.6) 0%, transparent 100%);
            filter: blur(30px);
            opacity: 0.4;
        }

        .smoke-left {
            left: 0;
        }

        .smoke-right {
            right: 100px;
            animation: smoke-drift 12s ease-in-out infinite alternate;
        }

        /* Canvas grain overlay */
        .grain-overlay {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            opacity: 0.03;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
        }

        @keyframes forge-pulse {
            0% {
                opacity: 0.7;
                transform: scale(1);
            }

            100% {
                opacity: 1;
                transform: scale(1.05);
            }
        }

        @keyframes flame-flicker {
            0% {
                opacity: 0.3;
                transform: scaleY(0.8) scaleX(1);
            }

            25% {
                opacity: 0.6;
                transform: scaleY(1.1) scaleX(0.9);
            }

            50% {
                opacity: 0.4;
                transform: scaleY(0.9) scaleX(1.05);
            }

            75% {
                opacity: 0.7;
                transform: scaleY(1.05) scaleX(0.95);
            }

            100% {
                opacity: 0.3;
                transform: scaleY(0.8) scaleX(1);
            }
        }

        @keyframes ember-rise {
            0% {
                transform: translateY(0) translateX(0);
                opacity: 1;
            }

            50% {
                opacity: 0.8;
            }

            100% {
                transform: translateY(-300px) translateX(-40px);
                opacity: 0;
            }
        }

        @keyframes smoke-drift {
            0% {
                transform: translateX(0);
                opacity: 0.3;
            }

            100% {
                transform: translateX(30px);
                opacity: 0.5;
            }
        }

        /* ═══════════════════════════════════════════════════════════
           FORGE PANELS — Heavy iron with copper patina
           ═══════════════════════════════════════════════════════════ */
        .forge-panel {
            background: var(--iron-panel);
            -webkit-backdrop-filter: blur(8px);
            backdrop-filter: blur(8px);
            border: 2px solid var(--iron-border);
            border-top: 2px solid rgba(176, 96, 40, 0.3);
            border-radius: var(--radius);
            position: relative;
        }

        /* Copper patina highlight on top edge */
        .forge-panel::before {
            content: '';
            position: absolute;
            top: -1px;
            left: 10%;
            right: 10%;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--copper), transparent);
            opacity: 0.4;
        }

        /* ═══════════════════════════════════════════════════════════
           LAYOUT
           ═══════════════════════════════════════════════════════════ */
        .app-container {
            max-width: 1100px;
            margin: 0 auto;
            padding: 1.5rem 1.5rem 4rem;
            position: relative;
            z-index: 1;
        }

        header {
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }

        header h1 {
            font-family: Georgia, serif;
            font-size: 2.4rem;
            font-weight: 700;
            color: var(--copper-bright);
            text-shadow: 0 0 30px rgba(208, 128, 48, 0.3), 0 2px 4px rgba(0, 0, 0, 0.5);
            letter-spacing: 3px;
            text-transform: uppercase;
        }

        header .subtitle {
            color: var(--parchment-dim);
            font-size: 0.82rem;
            margin-top: 0.4rem;
            font-style: italic;
            letter-spacing: 0.5px;
        }

        .back-link {
            position: absolute;
            top: 1rem;
            left: 1.5rem;
            color: var(--copper);
            text-decoration: none;
            font-family: Georgia, serif;
            font-size: 0.85rem;
            opacity: 0.6;
            transition: opacity 0.2s;
            z-index: 2;
        }

        .back-link:hover {
            opacity: 1;
            color: var(--copper-bright);
        }

        /* ── Navigation — Brass plates ── */
        .tabs {
            display: flex;
            gap: 0.3rem;
            padding: 0 0.5rem;
            margin-bottom: 1.5rem;
            overflow-x: auto;
            flex-wrap: wrap;
        }

        .tab-btn {
            padding: 0.55rem 1.2rem;
            background: rgba(24, 16, 8, 0.6);
            border: 1px solid var(--iron-border);
            border-bottom: 2px solid rgba(100, 60, 30, 0.3);
            color: var(--parchment-dim);
            font-family: Georgia, serif;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: var(--radius);
            transition: all 0.25s;
            white-space: nowrap;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .tab-btn:hover {
            border-color: var(--copper);
            color: var(--copper-bright);
            background: rgba(176, 96, 40, 0.1);
        }

        .tab-btn.active {
            background: rgba(176, 96, 40, 0.15);
            border-color: var(--copper);
            border-bottom-color: var(--forge-amber);
            color: var(--copper-bright);
            box-shadow: 0 4px 20px rgba(208, 128, 48, 0.15), inset 0 -1px 0 rgba(208, 128, 48, 0.2);
        }

        /* ── Tab content ── */
        .tab-content {
            display: none;
            padding: 1.5rem;
        }

        .tab-content.active {
            display: block;
        }

        .section-header {
            margin-bottom: 1.5rem;
        }

        .section-header h2 {
            font-family: Georgia, serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--copper-bright);
            text-shadow: 0 0 15px rgba(208, 128, 48, 0.2);
            letter-spacing: 1px;
        }

        .section-header .sub-text {
            font-size: 0.78rem;
            color: var(--parchment-dim);
            margin-top: 0.3rem;
            font-style: italic;
        }

        /* ── Sub panels — Dark iron ── */
        .sub-panel {
            background: rgba(16, 10, 6, 0.6);
            border: 1px solid var(--iron-border);
            border-radius: var(--radius);
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .sub-panel h3 {
            font-family: Georgia, serif;
            font-size: 1rem;
            font-weight: 600;
            margin: 0 0 0.75rem 0;
            color: var(--copper);
            letter-spacing: 0.5px;
        }

        /* ── Inputs — Forged ── */
        .ws-input {
            width: 100%;
            padding: 0.5rem 0.7rem;
            background: rgba(8, 5, 4, 0.6);
            border: 1px solid rgba(120, 80, 40, 0.25);
            color: var(--parchment);
            font-family: system-ui, -apple-system, sans-serif;
            font-size: 0.9rem;
            border-radius: var(--radius);
            outline: 2px solid transparent;
            outline-offset: 2px;
            transition: border-color 0.2s, outline-color 0.2s;
        }

        .ws-input:focus {
            border-color: var(--copper);
            box-shadow: 0 0 8px rgba(176, 96, 40, 0.15);
            outline-color: var(--copper);
        }

        .ws-input::placeholder {
            color: rgba(168, 152, 128, 0.4);
        }

        textarea.ws-input {
            resize: vertical;
            min-height: 60px;
        }

        select.ws-input {
            cursor: pointer;
        }

        /* ── Buttons — Copper & brass ── */
        .ws-btn {
            padding: 0.45rem 1rem;
            background: rgba(176, 96, 40, 0.15);
            border: 1px solid var(--copper);
            color: var(--copper-bright);
            font-family: Georgia, serif;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            border-radius: var(--radius);
            transition: all 0.2s;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }

        .ws-btn:hover {
            background: rgba(176, 96, 40, 0.3);
            box-shadow: 0 0 10px rgba(208, 128, 48, 0.15);
        }

        .ws-btn.green {
            background: rgba(196, 160, 64, 0.12);
            border-color: var(--brass);
            color: var(--brass-bright);
        }

        .ws-btn.green:hover {
            background: rgba(196, 160, 64, 0.25);
        }

        .ws-btn.red {
            background: rgba(144, 48, 32, 0.15);
            border-color: var(--rust);
            color: #c05030;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
        }

        .ws-btn.red:hover {
            background: rgba(144, 48, 32, 0.3);
        }

        /* ── Card grid ── */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1rem;
        }

        .card {
            background: rgba(16, 10, 6, 0.7);
            border: 1px solid var(--iron-border);
            border-left: 3px solid var(--rust-dark);
            border-radius: var(--radius);
            padding: 1rem;
            position: relative;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .card:hover {
            border-color: rgba(176, 96, 40, 0.4);
            box-shadow: 0 0 15px rgba(208, 128, 48, 0.08);
        }

        .card-title {
            font-weight: 600;
            margin-bottom: 0.4rem;
            color: var(--copper-bright);
            font-family: Georgia, serif;
            font-size: 0.95rem;
            overflow-wrap: break-word;
            word-break: break-word;
        }

        .card-meta {
            font-size: 0.75rem;
            color: var(--parchment-dim);
            margin-bottom: 0.5rem;
        }

        .card-body {
            font-size: 0.85rem;
            color: var(--parchment-dim);
            line-height: 1.5;
        }

        .card-actions {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            display: flex;
            gap: 0.3rem;
        }

        .card-tag {
            display: inline-block;
            padding: 0.1rem 0.5rem;
            background: rgba(176, 96, 40, 0.12);
            border: 1px solid rgba(176, 96, 40, 0.3);
            border-radius: 2px;
            font-size: 0.7rem;
            color: var(--copper);
            margin-right: 0.3rem;
            margin-top: 0.3rem;
            font-family: Georgia, serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* ── People cards (gifts) ── */
        .people-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }

        .person-card {
            background: rgba(16, 10, 6, 0.7);
            border: 2px solid var(--iron-border);
            border-radius: var(--radius);
            overflow: hidden;
        }

        .person-header {
            padding: 0.75rem 1rem;
            background: rgba(176, 96, 40, 0.08);
            border-bottom: 1px solid var(--iron-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .person-name {
            font-family: Georgia, serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--brass-bright);
            text-shadow: 0 0 10px rgba(196, 160, 64, 0.15);
        }

        .person-birthday {
            font-size: 0.75rem;
            color: var(--parchment-dim);
        }

        .gift-list {
            padding: 0.75rem 1rem;
            list-style: none;
        }

        .gift-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.4rem 0;
            border-bottom: 1px solid rgba(120, 80, 40, 0.1);
            font-size: 0.85rem;
        }

        .gift-item.given {
            opacity: 0.4;
            text-decoration: line-through;
        }

        .gift-item .price {
            color: var(--brass);
            font-family: Georgia, serif;
            font-size: 0.85rem;
            font-weight: 600;
        }

        /* ── Cooling timer badges — metal tags ── */
        .cool-badge {
            font-size: 0.65rem;
            padding: 0.15rem 0.45rem;
            border-radius: 2px;
            background: rgba(120, 96, 64, 0.2);
            border: 1px solid rgba(120, 96, 64, 0.4);
            color: var(--patina);
            font-family: Georgia, serif;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .cool-badge.warm {
            background: rgba(208, 128, 48, 0.15);
            border-color: rgba(208, 128, 48, 0.4);
            color: var(--forge-amber);
        }

        .cool-badge.hot {
            background: rgba(196, 64, 32, 0.15);
            border-color: rgba(196, 64, 32, 0.4);
            color: #c85030;
        }

        /* ── List items ── */
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(120, 80, 40, 0.1);
        }

        .list-item:last-child {
            border-bottom: none;
        }

        /* ── Add form rows ── */
        .add-row {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }

        .add-row .ws-input {
            flex: 1;
        }

        /* ── Scrollbars — dark iron ── */
        ::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(176, 96, 40, 0.2);
            border-radius: 2px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: rgba(176, 96, 40, 0.4);
        }

        /* ── Empty state ── */
        .empty-state {
            text-align: center;
            padding: 2rem;
            color: var(--parchment-dim);
            font-size: 0.85rem;
            font-style: italic;
        }

        /* ── Accessibility — Reduced motion ── */
        @media (prefers-reduced-motion: reduce) {

            .flame,
            .ember-particle,
            .forge-glow,
            .forge-glow-2,
            .smoke-right {
                animation: none !important;
            }

            .flame {
                opacity: 0.3;
            }

            .ember-particle {
                opacity: 0;
            }

            .forge-glow {
                opacity: 0.85;
            }
        }

        /* ── Mobile responsive ── */
        @media (max-width: 600px) {
            .app-container {
                padding: 0.75rem 0.75rem 3rem;
            }

            header h1 {
                font-size: 1.6rem;
                letter-spacing: 1px;
            }

            .tabs {
                gap: 0.2rem;
            }

            .tab-btn {
                padding: 0.4rem 0.7rem;
                font-size: 0.7rem;
            }

            .card-grid,
            .people-grid {
                grid-template-columns: 1fr;
            }

            .add-row {
                flex-direction: column;
            }

            .add-row .ws-input {
                max-width: 100% !important;
            }

            .section-header h2 {
                font-size: 1.2rem;
            }
        }
    </style>
</head>

<body>
    <!-- ═══ FORGE BACKGROUND ═══ -->
    <div class="forge-bg">
        <div class="forge-glow"></div>
        <div class="forge-glow-2"></div>
        <div class="flame flame-1"></div>
        <div class="flame flame-2"></div>
        <div class="flame flame-3"></div>
        <div class="flame flame-4"></div>
        <div class="ember-particle ember-1"></div>
        <div class="ember-particle ember-2"></div>
        <div class="ember-particle ember-3"></div>
        <div class="ember-particle ember-4"></div>
        <div class="ember-particle ember-5"></div>
        <div class="ember-particle ember-6"></div>
        <div class="smoke smoke-left"></div>
        <div class="smoke smoke-right"></div>
    </div>
    <div class="grain-overlay"></div>

    <!-- ═══ APP ═══ -->
    <div class="app-container">
        <a href="index.html" class="back-link">← Life Hub</a>

        <header class="forge-panel" style="position: relative;">
            <h1>⚒ My Workshop</h1>
            <p class="subtitle">No pressure. No scores. Just organized drawers for your brain's overflow.</p>
            <div style="position:absolute;top:0.75rem;right:1rem;display:flex;gap:0.5rem;align-items:center;">
                <button class="ws-btn" onclick="exportAllData()"
                    style="font-size:0.7rem;padding:0.25rem 0.6rem;opacity:0.5;"
                    title="Export all data as JSON backup">Export</button>
                <button class="ws-btn" onclick="importData()"
                    style="font-size:0.7rem;padding:0.25rem 0.6rem;opacity:0.5;"
                    title="Import data from backup file">Import</button>
                <button id="sync-btn" class="ws-btn green" onclick="syncToLive()"
                    style="font-size:0.78rem;padding:0.3rem 0.8rem;display:none;"
                    title="Sync local changes to live GitHub Pages site">⟳ Sync</button>
            </div>
        </header>

        <div class="tabs">
            <button class="tab-btn active" data-tab="gifts">🎁 Gifts</button>
            <button class="tab-btn" data-tab="ideas">💡 Ideas</button>
            <button class="tab-btn" data-tab="wishlists">🛒 Wishlists</button>
            <button class="tab-btn" data-tab="lists">📝 Lists</button>
            <button class="tab-btn" data-tab="projects">🔨 Projects</button>
            <button class="tab-btn" data-tab="reports">📄 Reports</button>
        </div>

        <main>
            <!-- ═══════════ GIFTS TAB ═══════════ -->
            <section id="gifts" class="tab-content active forge-panel">
                <div class="section-header">
                    <h2>🎁 Gift Tracker</h2>
                    <p class="sub-text">Track gift ideas for people. Spot something perfect? Save it before you forget.
                    </p>
                </div>

                <div class="sub-panel" style="border-color: rgba(196,160,64,0.3); margin-bottom: 1.5rem;">
                    <h3>Add Person</h3>
                    <div class="add-row">
                        <input type="text" class="ws-input" id="gift-person-name"
                            placeholder="Name (e.g., Mum, Parker)">
                        <input type="text" class="ws-input" id="gift-person-bday" placeholder="Birthday (e.g., 15 June)"
                            style="max-width: 160px;" onkeydown="if(event.key==='Enter')addPerson()">
                        <button class="ws-btn green" onclick="addPerson()">+ Add</button>
                    </div>
                </div>

                <div id="gifts-people-grid" class="people-grid"></div>
            </section>

            <!-- ═══════════ IDEAS TAB ═══════════ -->
            <section id="ideas" class="tab-content forge-panel">
                <div class="section-header">
                    <h2>💡 Ideas Board</h2>
                    <p class="sub-text">Quick capture. Dump it, tag it, sort later.</p>
                </div>

                <div class="sub-panel" style="border-color: rgba(208,128,48,0.3); margin-bottom: 1.5rem;">
                    <div class="add-row">
                        <input type="text" class="ws-input" id="idea-text" placeholder="What's the idea?">
                        <select class="ws-input" id="idea-category" style="max-width: 150px;">
                            <option value="general">💭 General</option>
                            <option value="project">🔨 Project</option>
                            <option value="business">💼 Business</option>
                            <option value="make">🎨 To Make</option>
                            <option value="try">🧪 To Try</option>
                        </select>
                        <button class="ws-btn" onclick="addIdea()">+ Add</button>
                    </div>
                </div>

                <div style="display: flex; gap: 0.4rem; margin-bottom: 1rem; flex-wrap: wrap;">
                    <button class="tab-btn active" onclick="filterIdeas('all', this)">All</button>
                    <button class="tab-btn" onclick="filterIdeas('general', this)">💭 General</button>
                    <button class="tab-btn" onclick="filterIdeas('project', this)">🔨 Project</button>
                    <button class="tab-btn" onclick="filterIdeas('business', this)">💼 Business</button>
                    <button class="tab-btn" onclick="filterIdeas('make', this)">🎨 To Make</button>
                    <button class="tab-btn" onclick="filterIdeas('try', this)">🧪 To Try</button>
                </div>

                <div id="ideas-grid" class="card-grid"></div>
            </section>

            <!-- ═══════════ WISHLISTS TAB ═══════════ -->
            <section id="wishlists" class="tab-content forge-panel">
                <div class="section-header">
                    <h2>🛒 Wishlists</h2>
                    <p class="sub-text">Things you want. If it's been here 2+ weeks, it's probably real. Under 2 weeks?
                        Maybe sleep on it.</p>
                </div>

                <div class="sub-panel" style="border-color: rgba(196,160,64,0.3); margin-bottom: 1.5rem;">
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <div class="add-row" style="margin: 0;">
                            <input type="text" class="ws-input" id="wish-name" placeholder="What do you want?">
                            <input type="text" class="ws-input" id="wish-price" placeholder="$" style="max-width: 80px;"
                                onkeydown="if(event.key==='Enter')addWish()">
                        </div>
                        <div class="add-row" style="margin: 0;">
                            <input type="text" class="ws-input" id="wish-link" placeholder="Link (optional)"
                                onkeydown="if(event.key==='Enter')addWish()">
                            <input type="text" class="ws-input" id="wish-why" placeholder="Why?"
                                style="max-width: 200px;" onkeydown="if(event.key==='Enter')addWish()">
                            <button class="ws-btn" onclick="addWish()">+ Add</button>
                        </div>
                    </div>
                </div>

                <div id="wishlists-grid" class="card-grid"></div>
            </section>

            <!-- ═══════════ LISTS TAB ═══════════ -->
            <section id="lists" class="tab-content forge-panel">
                <div class="section-header">
                    <h2>📝 Lists & References</h2>
                    <p class="sub-text">Recipes, shows, music, places — all the things you want to remember.</p>
                </div>

                <div class="sub-panel" style="border-color: rgba(196,160,64,0.3); margin-bottom: 1.5rem;">
                    <h3>Create New List</h3>
                    <div class="add-row">
                        <input type="text" class="ws-input" id="list-name"
                            placeholder="List name (e.g., Movies to Watch, Recipes)">
                        <select class="ws-input" id="list-icon" style="max-width: 70px;">
                            <option>🎬</option>
                            <option>🍳</option>
                            <option>🎵</option>
                            <option>📍</option>
                            <option>📚</option>
                            <option>🎮</option>
                            <option>☕</option>
                            <option>✈️</option>
                        </select>
                        <button class="ws-btn green" onclick="addList()">+ Create</button>
                    </div>
                </div>

                <div id="lists-container"></div>
            </section>

            <!-- ═══════════ PROJECTS TAB ═══════════ -->
            <section id="projects" class="tab-content forge-panel">
                <div class="section-header">
                    <h2>🔨 Projects Workbench</h2>
                    <p class="sub-text">Small personal projects. Track progress without the overhead.</p>
                </div>

                <div class="sub-panel" style="border-color: rgba(176,96,40,0.3); margin-bottom: 1.5rem;">
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <div class="add-row" style="margin: 0;">
                            <input type="text" class="ws-input" id="proj-name" placeholder="Project name">
                            <select class="ws-input" id="proj-status" style="max-width: 140px;">
                                <option value="idea">💭 Idea</option>
                                <option value="active">🔥 Active</option>
                                <option value="paused">⏸️ Paused</option>
                                <option value="done">✅ Done</option>
                            </select>
                        </div>
                        <div class="add-row" style="margin: 0;">
                            <textarea class="ws-input" id="proj-desc" placeholder="What's it about? (optional)"
                                style="min-height: 40px;"></textarea>
                            <button class="ws-btn" onclick="addProject()" style="align-self: flex-end;">+ Add</button>
                        </div>
                    </div>
                </div>

                <div id="projects-grid" class="card-grid"></div>
            </section>

            <!-- ═══════════ REPORTS TAB ═══════════ -->
            <section id="reports" class="tab-content forge-panel">
                <div class="section-header">
                    <h2>📄 Reports Vault</h2>
                    <p class="sub-text">Deep-dive reports generated by Lobotto. Reference library for decisions and
                        hardware analysis.</p>
                </div>

                <div id="reports-grid" class="card-grid"></div>

                <div class="sub-panel" style="border-color: rgba(176,96,40,0.3); margin-top: 1.5rem;">
                    <h3>Add Custom Report Link</h3>
                    <div class="add-row">
                        <input type="text" class="ws-input" id="report-title" placeholder="Report title">
                        <input type="text" class="ws-input" id="report-path"
                            placeholder="Path (e.g. reports/my-report.html)" style="max-width: 280px;">
                    </div>
                    <div class="add-row">
                        <input type="text" class="ws-input" id="report-summary"
                            placeholder="One-line summary (optional)">
                        <button class="ws-btn green" onclick="addCustomReport()">+ Add</button>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <script>
        // ═══════════════════════════════════════════════════════════════════════════
        // SOVEREIGN API CLIENT  (was Supabase cloud — now local /api over Tailscale)
        // ═══════════════════════════════════════════════════════════════════════════
        const API_BASE = '/api';
        const API_TOKEN = 'local_tailnet_token';

        // Single fetch wrapper. Throws loudly on any non-2xx so callers must handle
        // failure rather than silently corrupting the in-memory cache.
        async function api(endpoint, { method = 'GET', body } = {}) {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                method,
                headers: {
                    'Authorization': `Bearer ${API_TOKEN}`,
                    ...(body ? { 'Content-Type': 'application/json' } : {})
                },
                ...(body ? { body: JSON.stringify(body) } : {})
            });
            if (!res.ok) {
                const detail = await res.text().catch(() => '');
                throw new Error(`${method} ${endpoint} -> ${res.status} ${detail}`);
            }
            return res.status === 204 ? null : res.json();
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // SYNC BUTTON (localhost-only)
        // ═══════════════════════════════════════════════════════════════════════════
        const IS_LOCAL = !['priscillak91k-aigoon.github.io'].includes(window.location.hostname);
        if (IS_LOCAL) {
            const syncBtn = document.getElementById('sync-btn');
            if (syncBtn) syncBtn.style.display = 'inline-block';
        }

        async function syncToLive() {
            const btn = document.getElementById('sync-btn');
            btn.textContent = '⟳ Syncing...';
            btn.disabled = true;
            try {
                const res = await fetch('http://localhost:7338/deploy', { signal: AbortSignal.timeout(70000) });
                const json = await res.json();
                if (json.status === 'ok') {
                    btn.textContent = '✅ Synced';
                    btn.style.borderColor = 'var(--brass)';
                    setTimeout(() => { btn.textContent = '⟳ Sync'; btn.style.borderColor = ''; btn.disabled = false; }, 4000);
                } else {
                    btn.textContent = '❌ Failed';
                    btn.disabled = false;
                    console.error('[Sync]', json);
                }
            } catch (e) {
                btn.textContent = '❌ Server offline';
                btn.disabled = false;
                console.error('[Sync] Deploy server not running:', e.message);
            }
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // LOCAL DATA STORE (localStorage) — Gifts, Projects, Reports only
        // ═══════════════════════════════════════════════════════════════════════════
        const KEYS = {
            people: 'workshop_gift_people',
            projects: 'workshop_projects',
            activeTab: 'workshop_active_tab'
        };

        function load(key) {
            try {
                const raw = localStorage.getItem(key);
                if (!raw) return [];
                const data = JSON.parse(raw);
                if (!Array.isArray(data)) {
                    console.warn(`[Workshop] Data for ${key} is not an array, resetting.`);
                    return [];
                }
                return data;
            } catch (e) {
                console.error(`[Workshop] Corrupted data for ${key}:`, e.message);
                // Attempt to preserve corrupted data for recovery
                try {
                    const backup = localStorage.getItem(key);
                    if (backup) localStorage.setItem(key + '_corrupted_backup', backup);
                } catch (_) { /* storage may be full */ }
                return [];
            }
        }

        function save(key, data) {
            try {
                localStorage.setItem(key, JSON.stringify(data));
            } catch (e) {
                if (e.name === 'QuotaExceededError' || e.code === 22) {
                    alert('Storage is full. Your data was NOT saved. Export a backup and clear old items.');
                } else {
                    console.error(`[Workshop] Save failed for ${key}:`, e.message);
                    alert('Failed to save data: ' + e.message);
                }
            }
        }

        function genId() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 6); }

        // ═══════════════════════════════════════════════════════════════════════════
        // EXPORT / IMPORT — data backup
        // ═══════════════════════════════════════════════════════════════════════════
        function exportAllData() {
            try {
                const data = {};
                Object.entries(KEYS).forEach(([name, key]) => {
                    if (name === 'activeTab') return;
                    data[name] = load(key);
                });
                data._exportedAt = new Date().toISOString();
                data._version = 1;
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `workshop-backup-${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (e) {
                alert('Export failed: ' + e.message);
            }
        }

        function importData() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (ev) => {
                    try {
                        const data = JSON.parse(ev.target.result);
                        if (!data._version) {
                            alert('Invalid backup file — not a Workshop export.');
                            return;
                        }
                        if (!confirm('This will REPLACE all current data. Are you sure?')) return;
                        const mapping = { people: KEYS.people, projects: KEYS.projects };
                        Object.entries(mapping).forEach(([name, key]) => {
                            if (Array.isArray(data[name])) save(key, data[name]);
                        });
                        initAll();
                        alert('Data imported successfully.');
                    } catch (err) {
                        alert('Import failed — invalid JSON: ' + err.message);
                    }
                };
                reader.onerror = () => alert('Failed to read file.');
                reader.readAsText(file);
            };
            input.click();
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // TAB NAVIGATION — with persistence
        // ═══════════════════════════════════════════════════════════════════════════
        const VALID_TABS = ['gifts', 'ideas', 'wishlists', 'lists', 'projects', 'reports'];

        function switchTab(tabName) {
            if (!VALID_TABS.includes(tabName)) return;
            document.querySelectorAll('.tab-btn[data-tab]').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            const btn = document.querySelector(`.tab-btn[data-tab="${tabName}"]`);
            const section = document.getElementById(tabName);
            if (btn && section) {
                btn.classList.add('active');
                section.classList.add('active');
                try { localStorage.setItem(KEYS.activeTab, tabName); } catch (_) { }
            }
        }

        document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
            btn.addEventListener('click', () => switchTab(btn.dataset.tab));
        });

        // Restore last active tab
        try {
            const savedTab = localStorage.getItem(KEYS.activeTab);
            if (savedTab && document.getElementById(savedTab)) switchTab(savedTab);
        } catch (_) { }

        // ═══════════════════════════════════════════════════════════════════════════
        // HELPERS — XSS-safe
        // ═══════════════════════════════════════════════════════════════════════════
        function esc(s) {
            return (s || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;')
                .replace(/`/g, '&#96;');
        }

        function safeHref(url) {
            if (!url) return '';
            const trimmed = url.trim().toLowerCase();
            if (trimmed.startsWith('javascript:') || trimmed.startsWith('data:') || trimmed.startsWith('vbscript:')) return '';
            // Ensure it has a protocol
            if (!/^https?:\/\//i.test(url.trim())) return 'https://' + url.trim();
            return url.trim();
        }

        function safeDays(dateStr) {
            try {
                const t = new Date(dateStr).getTime();
                if (isNaN(t)) return 0;
                return Math.max(0, Math.floor((Date.now() - t) / 86400000));
            } catch { return 0; }
        }

        function safeDate(dateStr) {
            try {
                const d = new Date(dateStr);
                if (isNaN(d.getTime())) return '';
                return d.toLocaleDateString('en-NZ', { day: 'numeric', month: 'short' });
            } catch { return ''; }
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // GIFTS
        // ═══════════════════════════════════════════════════════════════════════════
        function addPerson() {
            const nameEl = document.getElementById('gift-person-name');
            const name = nameEl.value.trim();
            if (!name) return;
            const bday = document.getElementById('gift-person-bday').value.trim();
            const people = load(KEYS.people);
            if (people.some(p => p.name.toLowerCase() === name.toLowerCase())) {
                if (!confirm(`"${name}" already exists. Add another entry with this name?`)) return;
            }
            people.push({ id: genId(), name, birthday: bday, gifts: [] });
            save(KEYS.people, people);
            nameEl.value = '';
            document.getElementById('gift-person-bday').value = '';
            renderGifts();
            nameEl.focus();
        }

        function addGiftToPerson(personId) {
            const input = document.getElementById(`gift-input-${personId}`);
            const priceInput = document.getElementById(`gift-price-${personId}`);
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            const people = load(KEYS.people);
            const person = people.find(p => p.id === personId);
            if (!person) return;
            person.gifts.push({
                id: genId(), text,
                price: priceInput ? priceInput.value.trim() : '',
                given: false,
                addedAt: new Date().toISOString()
            });
            save(KEYS.people, people);
            renderGifts();
            // Re-focus the input after render rebuilds the DOM
            const newInput = document.getElementById(`gift-input-${personId}`);
            if (newInput) newInput.focus();
        }

        function toggleGiven(personId, giftId) {
            const people = load(KEYS.people);
            const person = people.find(p => p.id === personId);
            if (!person) return;
            const gift = person.gifts.find(g => g.id === giftId);
            if (gift) {
                gift.given = !gift.given;
                if (gift.given) gift.givenAt = new Date().toISOString();
            }
            save(KEYS.people, people);
            renderGifts();
        }

        function deleteGift(personId, giftId) {
            const people = load(KEYS.people);
            const person = people.find(p => p.id === personId);
            if (!person) return;
            person.gifts = person.gifts.filter(g => g.id !== giftId);
            save(KEYS.people, people);
            renderGifts();
        }

        function deletePerson(personId) {
            const people = load(KEYS.people);
            const person = people.find(p => p.id === personId);
            const name = person ? person.name : 'this person';
            if (!confirm(`Delete ${name} and all their gift ideas?`)) return;
            save(KEYS.people, people.filter(p => p.id !== personId));
            renderGifts();
        }

        function renderGifts() {
            const container = document.getElementById('gifts-people-grid');
            const people = load(KEYS.people).filter(p => p && p.id && p.name);
            if (people.length === 0) {
                container.innerHTML = '<div class="empty-state">No people added yet. Add someone above to start tracking gift ideas.</div>';
                return;
            }
            container.innerHTML = people.map(p => {
                const pid = esc(p.id);
                const giftHtml = (p.gifts || []).map(g => {
                    const gid = esc(g.id);
                    return `
                    <div class="gift-item ${g.given ? 'given' : ''}">
                        <span style="cursor:pointer;" onclick="toggleGiven('${pid}','${gid}')">${g.given ? '✅' : '⬜'} ${esc(g.text)}</span>
                        <div style="display:flex;align-items:center;gap:0.5rem;">
                            ${g.price ? `<span class="price">$${esc(g.price)}</span>` : ''}
                            <button class="ws-btn red" onclick="deleteGift('${pid}','${gid}')">×</button>
                        </div>
                    </div>`;
                }).join('');

                return `
                    <div class="person-card">
                        <div class="person-header">
                            <div>
                                <span class="person-name">${esc(p.name)}</span>
                                ${p.birthday ? `<span class="person-birthday"> · 🎂 ${esc(p.birthday)}</span>` : ''}
                            </div>
                            <button class="ws-btn red" onclick="deletePerson('${pid}')">×</button>
                        </div>
                        <div class="gift-list">
                            ${giftHtml || '<div style="color:var(--parchment-dim);font-size:0.8rem;font-style:italic;padding:0.5rem 0;">No gift ideas yet</div>'}
                            <div style="display:flex;gap:0.4rem;margin-top:0.5rem;">
                                <input type="text" class="ws-input" id="gift-input-${pid}" placeholder="Gift idea..." style="font-size:0.85rem;padding:0.35rem 0.5rem;" onkeydown="if(event.key==='Enter')addGiftToPerson('${pid}')">
                                <input type="text" class="ws-input" id="gift-price-${pid}" placeholder="$" style="max-width:60px;font-size:0.85rem;padding:0.35rem 0.5rem;">
                                <button class="ws-btn green" onclick="addGiftToPerson('${pid}')" style="font-size:0.75rem;padding:0.3rem 0.6rem;">+</button>
                            </div>
                        </div>
                    </div>`;
            }).join('');
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // IDEAS — Sovereign /api
        // ═══════════════════════════════════════════════════════════════════════════
        let currentIdeaFilter = 'all';
        let _ideasCache = [];

        async function addIdea() {
            const textEl = document.getElementById('idea-text');
            const text = textEl.value.trim();
            if (!text) return;
            const category = document.getElementById('idea-category').value;
            let data;
            try { data = await api('/workshop_ideas', { method: 'POST', body: { text, category } }); }
            catch (e) { console.error('[Ideas] Insert failed:', e.message); alert('Could not save idea: ' + e.message); return; }
            _ideasCache.unshift(data);
            textEl.value = '';
            renderIdeas();
            textEl.focus();
        }

        async function deleteIdea(id) {
            if (!confirm('Delete this idea?')) return;
            try { await api('/workshop_ideas/' + id, { method: 'DELETE' }); }
            catch (e) { console.error('[Ideas] Delete failed:', e.message); alert('Could not delete idea: ' + e.message); return; }
            _ideasCache = _ideasCache.filter(i => i.id !== id);
            renderIdeas();
        }

        function filterIdeas(cat, btn) {
            currentIdeaFilter = cat;
            document.querySelectorAll('#ideas .tab-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderIdeas();
        }

        async function loadIdeas() {
            try { _ideasCache = await api('/workshop_ideas') || []; }
            catch (e) { console.error('[Ideas] Load failed:', e.message); _ideasCache = []; }
            renderIdeas();
        }

        const IDEA_ICONS = { general: '💭', project: '🔨', business: '💼', make: '🎨', try: '🧪' };

        function renderIdeas() {
            const container = document.getElementById('ideas-grid');
            let ideas = _ideasCache;
            if (currentIdeaFilter !== 'all') ideas = ideas.filter(i => i.category === currentIdeaFilter);
            if (ideas.length === 0) {
                container.innerHTML = '<div class="empty-state">No ideas yet. Start dumping them above — no pressure to organize.</div>';
                return;
            }
            container.innerHTML = ideas.map(i => {
                const date = safeDate(i.added_at);
                const iid = esc(i.id);
                return `
                    <div class="card">
                        <div class="card-actions"><button class="ws-btn red" onclick="deleteIdea('${iid}')">×</button></div>
                        <div class="card-title">${IDEA_ICONS[i.category] || '💭'} ${esc(i.text)}</div>
                        <div class="card-meta">${date}</div>
                        <span class="card-tag">${esc(i.category)}</span>
                    </div>`;
            }).join('');
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // WISHLISTS — Sovereign /api
        // ═══════════════════════════════════════════════════════════════════════════
        let _wishesCache = [];

        async function addWish() {
            const nameEl = document.getElementById('wish-name');
            const name = nameEl.value.trim();
            if (!name) return;
            const price = document.getElementById('wish-price').value.trim();
            const link = document.getElementById('wish-link').value.trim();
            const why = document.getElementById('wish-why').value.trim();
            let data;
            try { data = await api('/workshop_wishlists', { method: 'POST', body: { name, price: price || null, link: link || null, why: why || null } }); }
            catch (e) { console.error('[Wishes] Insert failed:', e.message); alert('Could not save wish: ' + e.message); return; }
            _wishesCache.unshift(data);
            ['wish-name', 'wish-price', 'wish-link', 'wish-why'].forEach(id => document.getElementById(id).value = '');
            renderWishes();
            nameEl.focus();
        }

        async function deleteWish(id) {
            const wish = _wishesCache.find(w => w.id === id);
            const name = wish ? wish.name : 'this item';
            if (!confirm(`Remove "${name}" from your wishlist?`)) return;
            try { await api('/workshop_wishlists/' + id, { method: 'DELETE' }); }
            catch (e) { console.error('[Wishes] Delete failed:', e.message); alert('Could not delete wish: ' + e.message); return; }
            _wishesCache = _wishesCache.filter(w => w.id !== id);
            renderWishes();
        }

        async function loadWishes() {
            try { _wishesCache = await api('/workshop_wishlists') || []; }
            catch (e) { console.error('[Wishes] Load failed:', e.message); _wishesCache = []; }
            renderWishes();
        }

        function getCoolBadge(addedAt) {
            const days = safeDays(addedAt);
            if (days >= 14) return `<span class="cool-badge hot">🔥 ${days}d — forged</span>`;
            if (days >= 7) return `<span class="cool-badge warm">🌡️ ${days}d — tempering</span>`;
            if (days === 0) return `<span class="cool-badge">❄️ New — cooling</span>`;
            return `<span class="cool-badge">❄️ ${days}d — cooling</span>`;
        }

        function renderWishes() {
            const container = document.getElementById('wishlists-grid');
            if (_wishesCache.length === 0) {
                container.innerHTML = '<div class="empty-state">No wishes yet. Spot something you want? Save it here.</div>';
                return;
            }
            container.innerHTML = _wishesCache.map(w => {
                const wid = esc(w.id);
                const href = safeHref(w.link);
                return `
                <div class="card">
                    <div class="card-actions"><button class="ws-btn red" onclick="deleteWish('${wid}')">×</button></div>
                    <div class="card-title">🛒 ${esc(w.name)}</div>
                    <div class="card-meta">
                        ${w.price ? `<strong style="color:var(--brass);">$${esc(w.price)}</strong> · ` : ''}
                        ${getCoolBadge(w.added_at)}
                    </div>
                    ${w.why ? `<div class="card-body"><strong>Why:</strong> ${esc(w.why)}</div>` : ''}
                    ${href ? `<div style="margin-top:0.4rem;"><a href="${esc(href)}" target="_blank" rel="noopener noreferrer" style="color:var(--forge-amber);font-size:0.8rem;text-decoration:none;">🔗 Link</a></div>` : ''}
                </div>`;
            }).join('');
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // LISTS — Sovereign /api
        // ═══════════════════════════════════════════════════════════════════════════
        let _listsCache = [];

        async function addList() {
            const nameEl = document.getElementById('list-name');
            const name = nameEl.value.trim();
            if (!name) return;
            const icon = document.getElementById('list-icon').value;
            let data;
            try { data = await api('/workshop_lists', { method: 'POST', body: { list_name: name, icon, items: [] } }); }
            catch (e) { console.error('[Lists] Insert failed:', e.message); alert('Could not create list: ' + e.message); return; }
            _listsCache.push(data);
            nameEl.value = '';
            renderLists();
        }

        async function addItemToList(listId) {
            const input = document.getElementById(`list-item-${listId}`);
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            const list = _listsCache.find(l => l.id === listId);
            if (!list) return;
            const newItems = [...(list.items || []), { id: genId(), text, checked: false }];
            let data;
            try { data = await api('/workshop_lists/' + listId, { method: 'PATCH', body: { items: newItems } }); }
            catch (e) { console.error('[Lists] Update failed:', e.message); alert('Could not add item: ' + e.message); return; }
            list.items = data.items;
            renderLists();
            const newInput = document.getElementById(`list-item-${listId}`);
            if (newInput) newInput.focus();
        }

        async function toggleListItem(listId, itemId) {
            const list = _listsCache.find(l => l.id === listId);
            if (!list) return;
            const item = (list.items || []).find(i => i.id === itemId);
            if (item) item.checked = !item.checked;
            try { await api('/workshop_lists/' + listId, { method: 'PATCH', body: { items: list.items } }); }
            catch (e) { console.error('[Lists] Update failed:', e.message); alert('Could not update list: ' + e.message); }
            renderLists();
        }

        async function deleteListItem(listId, itemId) {
            const list = _listsCache.find(l => l.id === listId);
            if (!list) return;
            list.items = (list.items || []).filter(i => i.id !== itemId);
            try { await api('/workshop_lists/' + listId, { method: 'PATCH', body: { items: list.items } }); }
            catch (e) { console.error('[Lists] Update failed:', e.message); alert('Could not update list: ' + e.message); }
            renderLists();
        }

        async function deleteList(listId) {
            if (!confirm('Delete this entire list?')) return;
            try { await api('/workshop_lists/' + listId, { method: 'DELETE' }); }
            catch (e) { console.error('[Lists] Delete failed:', e.message); alert('Could not delete list: ' + e.message); return; }
            _listsCache = _listsCache.filter(l => l.id !== listId);
            renderLists();
        }

        async function loadLists() {
            try { _listsCache = await api('/workshop_lists') || []; }
            catch (e) { console.error('[Lists] Load failed:', e.message); _listsCache = []; }
            renderLists();
        }

        function renderLists() {
            const container = document.getElementById('lists-container');
            if (_listsCache.length === 0) {
                container.innerHTML = '<div class="empty-state">No lists yet. Create one above — recipes, movies, places, anything.</div>';
                return;
            }
            container.innerHTML = _listsCache.map(l => {
                const lid = esc(l.id);
                const sortedItems = [...(l.items || [])].sort((a, b) => (a.checked === b.checked) ? 0 : a.checked ? 1 : -1);
                const itemsHtml = sortedItems.map(i => {
                    const iid = esc(i.id);
                    return `
                    <div class="list-item">
                        <span style="cursor:pointer;${i.checked ? 'opacity:0.4;text-decoration:line-through;' : ''}" onclick="toggleListItem('${lid}','${iid}')">${i.checked ? '✅' : '⬜'} ${esc(i.text)}</span>
                        <button class="ws-btn red" onclick="deleteListItem('${lid}','${iid}')">×</button>
                    </div>`;
                }).join('');

                return `
                    <div class="sub-panel" style="margin-bottom: 1rem;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                            <h3>${esc(l.icon)} ${esc(l.list_name)} <span style="font-size:0.75rem;color:var(--parchment-dim);font-weight:normal;">(${(l.items || []).length})</span></h3>
                            <button class="ws-btn red" onclick="deleteList('${lid}')">Delete</button>
                        </div>
                        ${itemsHtml || '<div style="color:var(--parchment-dim);font-size:0.82rem;font-style:italic;">Empty list</div>'}
                        <div class="add-row" style="margin-top:0.5rem;margin-bottom:0;">
                            <input type="text" class="ws-input" id="list-item-${lid}" placeholder="Add item..." style="font-size:0.85rem;" onkeydown="if(event.key==='Enter')addItemToList('${lid}')">
                            <button class="ws-btn green" onclick="addItemToList('${lid}')" style="font-size:0.75rem;">+</button>
                        </div>
                    </div>`;
            }).join('');
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // PROJECTS
        // ═══════════════════════════════════════════════════════════════════════════
        function addProject() {
            const nameEl = document.getElementById('proj-name');
            const name = nameEl.value.trim();
            if (!name) return;
            const status = document.getElementById('proj-status').value;
            const desc = document.getElementById('proj-desc').value.trim();
            const projects = load(KEYS.projects);
            projects.unshift({ id: genId(), name, status, description: desc, createdAt: new Date().toISOString(), notes: [] });
            save(KEYS.projects, projects);
            nameEl.value = '';
            document.getElementById('proj-desc').value = '';
            renderProjects();
            nameEl.focus();
        }

        function deleteProject(id) {
            if (!confirm('Delete this project?')) return;
            const projects = load(KEYS.projects).filter(p => p.id !== id);
            save(KEYS.projects, projects);
            renderProjects();
        }

        function updateProjectStatus(id, newStatus) {
            const projects = load(KEYS.projects);
            const proj = projects.find(p => p.id === id);
            if (proj) proj.status = newStatus;
            save(KEYS.projects, projects);
            renderProjects();
        }

        function addProjectNote(id) {
            const input = document.getElementById(`proj-note-${id}`);
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            const projects = load(KEYS.projects);
            const proj = projects.find(p => p.id === id);
            if (!proj) return;
            if (!proj.notes) proj.notes = [];
            proj.notes.push({ text, date: new Date().toISOString() });
            save(KEYS.projects, projects);
            renderProjects();
            // Re-focus after render
            const newInput = document.getElementById(`proj-note-${id}`);
            if (newInput) newInput.focus();
        }

        function deleteProjectNote(projId, noteIndex) {
            const projects = load(KEYS.projects);
            const proj = projects.find(p => p.id === projId);
            if (!proj || !proj.notes) return;
            proj.notes.splice(noteIndex, 1);
            save(KEYS.projects, projects);
            renderProjects();
        }

        const STATUS_COLORS = {
            idea: { icon: '💭', color: 'var(--parchment-dim)' },
            active: { icon: '🔥', color: 'var(--forge-amber)' },
            paused: { icon: '⏸️', color: 'var(--brass)' },
            done: { icon: '✅', color: 'var(--copper-bright)' }
        };

        function renderProjects() {
            const container = document.getElementById('projects-grid');
            const projects = load(KEYS.projects);
            if (projects.length === 0) {
                container.innerHTML = '<div class="empty-state">No projects yet. Got a small thing you want to track? Add it above.</div>';
                return;
            }
            container.innerHTML = projects.map(p => {
                const pid = esc(p.id);
                const s = STATUS_COLORS[p.status] || STATUS_COLORS.idea;
                const date = safeDate(p.createdAt);
                const notesHtml = (p.notes || []).map((n, idx) => {
                    const d = safeDate(n.date);
                    return `<div style="font-size:0.8rem;color:var(--parchment-dim);padding:0.2rem 0;border-bottom:1px solid rgba(120,80,40,0.08);display:flex;justify-content:space-between;align-items:center;"><span><span style="color:var(--copper);font-size:0.7rem;">${d}</span> ${esc(n.text)}</span><button class="ws-btn red" onclick="deleteProjectNote('${pid}',${idx})" style="font-size:0.6rem;padding:0.1rem 0.3rem;opacity:0.5;">×</button></div>`;
                }).join('');

                return `
                    <div class="card" style="border-left-color: ${s.color};">
                        <div class="card-actions">
                            <select class="ws-input" onchange="updateProjectStatus('${pid}', this.value)" style="font-size:0.7rem;padding:0.15rem;max-width:100px;">
                                <option value="idea" ${p.status === 'idea' ? 'selected' : ''}>💭 Idea</option>
                                <option value="active" ${p.status === 'active' ? 'selected' : ''}>🔥 Active</option>
                                <option value="paused" ${p.status === 'paused' ? 'selected' : ''}>⏸️ Paused</option>
                                <option value="done" ${p.status === 'done' ? 'selected' : ''}>✅ Done</option>
                            </select>
                            <button class="ws-btn red" onclick="deleteProject('${pid}')">×</button>
                        </div>
                        <div class="card-title" style="color:${s.color};">${s.icon} ${esc(p.name)}</div>
                        <div class="card-meta">Created ${date}</div>
                        ${p.description ? `<div class="card-body">${esc(p.description)}</div>` : ''}
                        ${notesHtml ? `<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid var(--iron-border);">${notesHtml}</div>` : ''}
                        <div class="add-row" style="margin-top:0.5rem;margin-bottom:0;">
                            <input type="text" class="ws-input" id="proj-note-${pid}" placeholder="Add note..." style="font-size:0.8rem;" onkeydown="if(event.key==='Enter')addProjectNote('${pid}')">
                            <button class="ws-btn" onclick="addProjectNote('${pid}')" style="font-size:0.75rem;padding:0.2rem 0.5rem;">+</button>
                        </div>
                    </div>`;
            }).join('');
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // REPORTS
        // ═══════════════════════════════════════════════════════════════════════════
        const BUILTIN_REPORTS = [
            {
                id: 'msi-we75-upgrade',
                title: 'MSI WE75 9TK — Upgrade Report',
                date: '2026-03-14',
                tags: ['hardware', 'laptop', 'ultrathink'],
                summary: 'Full upgrade analysis: SSD, RAM, thermal repaste, battery. eGPU blocked (no Thunderbolt). Prioritised action plan with NZ pricing.',
                path: 'reports/msi-we75-upgrade-report.html',
                confidence: '91%',
                session: 53
            },
            {
                id: 'munro-caravan-move',
                title: 'Munro Caravan Move — Plywood Track Plan (Quad)',
                date: '2026-03-14',
                tags: ['caravan', 'logistics', 'property', 'nz'],
                summary: 'Full logistics plan for moving the 1977 Munro (~800kg) across soft lawn to permanent spot. Quad method: 6 sheets 15mm CD Structural ply (no compromise on quantity). Includes supplier pricing, safety protocols, and permanent storage pads.',
                path: 'reports/munro-caravan-move-report.html',
                confidence: '94%',
                session: 58
            },
            {
                id: 'wood-care-strategy',
                title: '373 York Place Wood Care Strategy',
                date: '2026-03-27',
                tags: ['maintenance', 'property', 'woodworking'],
                summary: "Initial cleaning and ongoing care strategy for dry vs coated woods at the new house. Utilizes existing Gilly's Orange Oil and Cabot's cleaners, with Bunnings upgrade paths for high sheen.",
                path: 'reports/wood-care-report.html',
                confidence: '98%',
                session: 60
            },
            {
                id: 'fireplace-kintsugi',
                title: 'Fireplace Mantle Kintsugi Repair Protocol',
                date: '2026-03-27',
                tags: ['masonry', 'aesthetic', 'repair'],
                summary: "DIY guide to filling the structural cracks in the fireplace surround tiles with clear 5-minute epoxy and gold mica powder based on Heat Triage assessments.",
                path: 'reports/fireplace-kintsugi-repair.html',
                confidence: '95%',
                session: 60
            },
            {
                id: 'shadow-integration',
                title: 'The Loner Empath & The Shadow — A Deep Dive into Jung',
                date: '2026-04-10',
                tags: ['psychology', 'jung', 'shadow-work', 'personal-growth'],
                summary: "Exhaustive analysis of Carl Jung's shadow integration theory for the loner empath archetype. Two paths (integration vs repression), Robert A. Johnson's mandorla framework, genetic markers mapped to Jungian archetypes, and practical shadow work protocol with daily/weekly exercises.",
                path: 'reports/shadow-integration-deep-dive.html',
                confidence: '96%',
                session: 59
            },
            {
                id: 'supplement-protocol-v4',
                title: 'Supplement Protocol v4.0 — Personalized Reference',
                date: '2026-04-14',
                tags: ['health', 'biohacking', 'genetics'],
                summary: 'Comprehensive molecular intervention protocol mapped against COMT, MTHFR, and TCF7L2 genetic variants. Includes targeted dosing for systemic inflammation (CRP 9) and metabolic optimization.',
                path: 'reports/supplement_protocol_report.html',
                confidence: '100%',
                session: 61
            }
        ];

        function renderReports() {
            const custom = JSON.parse(localStorage.getItem('ws_reports') || '[]');
            const all = [...BUILTIN_REPORTS, ...custom];
            const grid = document.getElementById('reports-grid');
            if (!all.length) {
                grid.innerHTML = '<div class="empty-state">No reports yet. Lobotto generates these during deep-dive sessions.</div>';
                return;
            }
            grid.innerHTML = all.map(r => {
                const tagsHtml = (r.tags || []).map(t => `<span class="card-tag">${t}</span>`).join('');
                const isBuiltin = BUILTIN_REPORTS.some(b => b.id === r.id);
                const delBtn = isBuiltin ? '' : `<button class="ws-btn red" onclick="deleteReport('${r.id}')" style="position:absolute;top:0.5rem;right:0.5rem;">×</button>`;
                return `<div class="card" style="border-left-color:var(--copper);">
                    ${delBtn}
                    <div class="card-title">${r.title}</div>
                    <div class="card-meta">${r.date}${r.session ? ' · Session ' + r.session : ''}${r.confidence ? ' · Confidence ' + r.confidence : ''}</div>
                    <div class="card-body" style="margin-bottom:0.6rem;">${r.summary}</div>
                    <div style="margin-bottom:0.5rem;">${tagsHtml}</div>
                    <a href="${r.path}" class="ws-btn" style="display:inline-block;text-decoration:none;font-size:0.75rem;padding:0.3rem 0.7rem;">Open Report →</a>
                </div>`;
            }).join('');
        }

        function addCustomReport() {
            const title = document.getElementById('report-title').value.trim();
            const path = document.getElementById('report-path').value.trim();
            const summary = document.getElementById('report-summary').value.trim();
            if (!title || !path) return;
            const reports = JSON.parse(localStorage.getItem('ws_reports') || '[]');
            reports.unshift({
                id: 'r_' + Date.now(),
                title, path, summary,
                date: new Date().toISOString().slice(0, 10),
                tags: ['custom']
            });
            localStorage.setItem('ws_reports', JSON.stringify(reports));
            document.getElementById('report-title').value = '';
            document.getElementById('report-path').value = '';
            document.getElementById('report-summary').value = '';
            renderReports();
        }

        function deleteReport(id) {
            const reports = JSON.parse(localStorage.getItem('ws_reports') || '[]');
            localStorage.setItem('ws_reports', JSON.stringify(reports.filter(r => r.id !== id)));
            renderReports();
        }

        // ═══════════════════════════════════════════════════════════════════════════
        // INIT
        // ═══════════════════════════════════════════════════════════════════════════
        async function initAll() {
            // Backend tabs (async)
            loadWishes();
            loadIdeas();
            loadLists();
            // localStorage tabs (sync)
            renderGifts();
            renderProjects();
            renderReports();
        }

        initAll();

        document.getElementById('gift-person-name').addEventListener('keydown', e => { if (e.key === 'Enter') addPerson(); });
        document.getElementById('idea-text').addEventListener('keydown', e => { if (e.key === 'Enter') addIdea(); });
        document.getElementById('wish-name').addEventListener('keydown', e => { if (e.key === 'Enter') addWish(); });
        document.getElementById('list-name').addEventListener('keydown', e => { if (e.key === 'Enter') addList(); });
        document.getElementById('proj-name').addEventListener('keydown', e => { if (e.key === 'Enter') addProject(); });
    </script>
</body>

</html>
`

## public\_misc.js
`javascript
// ============================================================
// MISC — Ideal Week Renderer + Editor
// ============================================================
(function initMiscPage() {
    'use strict';

    const STORAGE_KEY = 'idealWeek_v2';

    const C = {
        deepWork: { dot: '#00c9a0', label: 'Deep Work' },
        work: { dot: '#fbbf24', label: 'Work' },
        exercise: { dot: '#fb923c', label: 'Exercise' },
        personal: { dot: '#f472b6', label: 'Personal' },
        windDown: { dot: '#a78bfa', label: 'Wind Down' },
        routine: { dot: 'rgba(255,255,255,0.3)', label: 'Routine' },
        kids: { dot: '#38bdf8', label: 'Kids' },
        nap: { dot: '#c084fc', label: 'Nap' },
        cannabis: { dot: '#4ade80', label: 'Cannabis' },
    };

    const CAT_KEYS = Object.keys(C);

    // ── Default data ──────────────────────────────────────────
    const DEFAULT_WEEK = [
        {
            day: 'Monday', type: 'WORK 12–6 PM',
            note: 'Sleep first. Nap takes the prime morning slot — catch up on 6h night. Light admin after.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast in peace + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk (30 min)', cat: 'personal' },
                { time: '9:20', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '11:20', label: 'Wake · light admin / messages / quick tasks', cat: 'routine' },
                { time: '11:40', label: 'Shower · pack meals · travel prep', cat: 'routine' },
                { time: '12:00', label: '► BP SHIFT', cat: 'work' },
                { time: '18:00', label: 'Shift ends', cat: 'work' },
                { time: '18:15', label: 'Quinn decompression walk', cat: 'personal' },
                { time: '18:45', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: 'Admin · planning · light tasks', cat: 'routine' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '21:30', label: 'Reading — no screens', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early as possible', cat: 'windDown' },
            ]
        },
        {
            day: 'Tuesday', type: 'OFF DAY',
            note: 'Best day. Deep work → nap → gym. Full recovery stack.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast in peace + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — Block 1 (90 min)', cat: 'deepWork' },
                { time: '10:45', label: '10 min break · stretch · water', cat: 'routine' },
                { time: '11:00', label: 'DEEP WORK — Block 2 (60 min)', cat: 'deepWork' },
                { time: '12:00', label: 'Shutdown · lunch', cat: 'routine' },
                { time: '12:30', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:30', label: 'Wake · water · short walk to wake up', cat: 'routine' },
                { time: '15:00', label: 'GYM — heavy lift or sprint session', cat: 'exercise' },
                { time: '16:30', label: 'Shower + protein', cat: 'routine' },
                { time: '17:00', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:30', label: 'Light tasks · admin · messages', cat: 'routine' },
                { time: '18:30', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: '🌿 Cannabis — 2.5h before sleep', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Wednesday', type: 'OFF DAY',
            note: 'Same as Tuesday. Optional: swap gym for Rock Orchestra evening.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — Block 1 (90 min)', cat: 'deepWork' },
                { time: '10:45', label: 'Break · stretch · water', cat: 'routine' },
                { time: '11:00', label: 'DEEP WORK — Block 2 (60 min)', cat: 'deepWork' },
                { time: '12:00', label: 'Shutdown · lunch', cat: 'routine' },
                { time: '12:30', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:30', label: 'Wake · water', cat: 'routine' },
                { time: '15:00', label: 'GYM or active recovery', cat: 'exercise' },
                { time: '16:30', label: 'Shower + protein', cat: 'routine' },
                { time: '17:00', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:30', label: 'Admin / life tasks', cat: 'routine' },
                { time: '18:30', label: 'Dinner + kids', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: '🌿 Cannabis — 2.5h before sleep', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · dim lights', cat: 'windDown' },
                { time: '23:00', label: '💤 SLEEP TARGET', cat: 'windDown' },
            ]
        },
        {
            day: 'Thursday', type: 'OFF DAY',
            note: 'Prep day. Nap → gym → meal prep ready for weekend shifts.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — 2 h block', cat: 'deepWork' },
                { time: '11:15', label: 'Shutdown · review week', cat: 'routine' },
                { time: '11:30', label: 'Lunch', cat: 'routine' },
                { time: '12:00', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '14:00', label: 'Wake · water', cat: 'routine' },
                { time: '14:30', label: 'GYM or outdoor activity', cat: 'exercise' },
                { time: '16:00', label: 'Shower + protein', cat: 'routine' },
                { time: '16:30', label: 'Quinn afternoon walk', cat: 'personal' },
                { time: '17:00', label: 'Errands · life admin', cat: 'routine' },
                { time: '18:00', label: '🍳 MEAL PREP — Fri/Sat/Sun shifts', cat: 'routine' },
                { time: '19:15', label: 'Dinner + kids', cat: 'routine' },
                { time: '20:30', label: 'Kids bedtime', cat: 'kids' },
                { time: '21:00', label: 'Mag Glycinate · early wind-down', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early for weekend', cat: 'windDown' },
            ]
        },
        {
            day: 'Friday', type: 'WORK 2:45–11 PM',
            note: 'Nap replaces gym today — gym on off days covers it. Nap is the priority.',
            blocks: [
                { time: '6:30', label: 'Kids morning — breakfast, school prep, drop-off', cat: 'kids' },
                { time: '8:30', label: 'Quiet breakfast + NAC', cat: 'routine' },
                { time: '8:50', label: 'Quinn morning walk', cat: 'personal' },
                { time: '9:15', label: 'DEEP WORK — 1.5 h block', cat: 'deepWork' },
                { time: '10:45', label: 'Shutdown · wrap deep work', cat: 'routine' },
                { time: '11:00', label: '😴 NAP — 2 hours (blackout, phone off)', cat: 'nap' },
                { time: '13:00', label: 'Wake · shower · pack shift meals', cat: 'routine' },
                { time: '13:45', label: 'Lunch', cat: 'routine' },
                { time: '14:00', label: 'Quinn quick walk · fresh air', cat: 'personal' },
                { time: '14:15', label: 'Travel to BP', cat: 'routine' },
                { time: '14:45', label: '► BP SHIFT', cat: 'work' },
                { time: '23:00', label: 'Shift ends · straight home', cat: 'work' },
                { time: '23:20', label: 'Mag Glycinate · no screens', cat: 'windDown' },
                { time: '23:45', label: '💤 SLEEP — midnight hard cap', cat: 'windDown' },
            ]
        },
        {
            day: 'Saturday', type: 'WORK 2:45–11 PM',
            note: 'Sleep in to 9 AM = full recovery. No nap needed. Morning is yours.',
            blocks: [
                { time: '9:00', label: 'Wake (sleep in) · NAC + water', cat: 'routine' },
                { time: '9:15', label: 'Relaxed breakfast', cat: 'routine' },
                { time: '9:45', label: 'Quinn morning walk', cat: 'personal' },
                { time: '10:15', label: 'DEEP WORK — 90 min block', cat: 'deepWork' },
                { time: '11:45', label: 'GYM — lift or sprint', cat: 'exercise' },
                { time: '13:00', label: 'Shower + protein', cat: 'routine' },
                { time: '13:30', label: 'Lunch · pack shift meals', cat: 'routine' },
                { time: '14:00', label: 'Quinn short walk · prep for shift', cat: 'personal' },
                { time: '14:15', label: 'Travel to BP', cat: 'routine' },
                { time: '14:45', label: '► BP SHIFT', cat: 'work' },
                { time: '23:00', label: 'Shift ends · straight home', cat: 'work' },
                { time: '23:15', label: 'Mag Glycinate · decompress', cat: 'windDown' },
                { time: '23:45', label: '💤 SLEEP — midnight hard cap', cat: 'windDown' },
            ]
        },
        {
            day: 'Sunday', type: 'WORK 11 AM–5 PM',
            note: 'Sleep in to 9 AM. Shortest shift. Earliest sleep target — reset for Monday.',
            blocks: [
                { time: '9:00', label: 'Wake (sleep in) · NAC + water', cat: 'routine' },
                { time: '9:15', label: 'Relaxed Sunday breakfast', cat: 'routine' },
                { time: '9:45', label: 'Quinn morning walk', cat: 'personal' },
                { time: '10:15', label: 'Shower · get ready · pack bag', cat: 'routine' },
                { time: '10:30', label: 'Travel to BP', cat: 'routine' },
                { time: '11:00', label: '► BP SHIFT', cat: 'work' },
                { time: '17:00', label: 'Shift ends', cat: 'work' },
                { time: '17:20', label: 'Quinn evening walk — decompress', cat: 'personal' },
                { time: '18:00', label: 'Dinner + kids evening', cat: 'routine' },
                { time: '20:00', label: 'Kids bedtime', cat: 'kids' },
                { time: '20:30', label: '🌿 Cannabis + week review', cat: 'cannabis' },
                { time: '21:00', label: 'Mag Glycinate · pure rest', cat: 'windDown' },
                { time: '21:30', label: 'Reading — no screens', cat: 'windDown' },
                { time: '22:30', label: '💤 SLEEP — early reset for Monday', cat: 'windDown' },
            ]
        }
    ];

    // ── Data persistence ──────────────────────────────────────
    function loadWeek() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) return JSON.parse(stored);
        } catch (e) { /* fall through */ }
        return JSON.parse(JSON.stringify(DEFAULT_WEEK));
    }

    function saveWeek(week) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(week));
    }

    let WEEK = loadWeek();
    let editingDay = -1; // index of day being edited, -1 = none

    // ── Dirty-state guard ─────────────────────────────────────
    function setDirtyGuard(isDirty) {
        window.onbeforeunload = isDirty
            ? () => 'You have unsaved changes to your Ideal Week. Leave anyway?'
            : null;
    }

    // ── Category dropdown HTML ────────────────────────────────
    function catOptions(selected) {
        return CAT_KEYS.map(k =>
            `<option value="${k}" ${k === selected ? 'selected' : ''}>${C[k].label}</option>`
        ).join('');
    }

    // ── Renderer ──────────────────────────────────────────────
    function renderIdealWeek() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        grid.innerHTML = WEEK.map((dayData, dayIdx) => {
            const { day, type, note, blocks } = dayData;
            const isOff = type === 'OFF DAY';
            const isEditing = editingDay === dayIdx;

            // --- Edit mode ---
            if (isEditing) {
                const blockRows = blocks.map((b, bIdx) => {
                    const dot = C[b.cat]?.dot || 'rgba(255,255,255,0.3)';
                    return `
                    <div class="iw-edit-row" data-bidx="${bIdx}" style="display:flex; gap:6px; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                        <input type="text" value="${b.time}" class="iw-input iw-time" style="width:52px; font-size:0.75rem; font-family:'VT323',monospace;" placeholder="HH:MM">
                        <select class="iw-input iw-cat" style="width:90px; font-size:0.72rem;">
                            ${catOptions(b.cat)}
                        </select>
                        <input type="text" value="${b.label.replace(/"/g, '&quot;')}" class="iw-input iw-label" style="flex:1; font-size:0.78rem;" placeholder="Activity label">
                        <button class="iw-btn-icon iw-del-block" title="Remove" data-bidx="${bIdx}" style="color:#f87171; background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.15);">✕</button>
                    </div>`;
                }).join('');

                const typeBg = isOff ? 'rgba(0,200,160,0.08)' : 'rgba(251,191,36,0.08)';
                const typeBorder = isOff ? 'rgba(0,200,160,0.2)' : 'rgba(251,191,36,0.25)';
                const typeColor = isOff ? 'var(--accent-green)' : '#fbbf24';

                return `
                <div class="iw-card-editing" data-day="${dayIdx}" style="background:rgba(4,18,18,0.75); border:1px solid var(--accent-green); border-radius:4px; padding:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                        <div style="display:flex; gap:6px; align-items:center;">
                            <input type="text" value="${type}" class="iw-input iw-type-input" style="width:120px; font-size:0.7rem; text-align:center;">
                        </div>
                    </div>
                    <div style="margin-bottom:8px;">
                        <input type="text" value="${(note || '').replace(/"/g, '&quot;')}" class="iw-input iw-note-input" style="width:100%; font-size:0.75rem; font-style:italic;" placeholder="Day note (optional)">
                    </div>
                    <div class="iw-edit-blocks">${blockRows}</div>
                    <div style="display:flex; gap:8px; margin-top:10px; justify-content:space-between; flex-wrap:wrap;">
                        <button class="iw-btn iw-add-block" data-day="${dayIdx}" style="font-size:0.75rem;">+ Add Block</button>
                        <div style="display:flex; gap:6px;">
                            <button class="iw-btn iw-save-day" data-day="${dayIdx}" style="background:rgba(0,200,160,0.15); border-color:rgba(0,200,160,0.3); color:#00c9a0;">✓ Save</button>
                            <button class="iw-btn iw-cancel-day" data-day="${dayIdx}" style="background:rgba(248,113,113,0.08); border-color:rgba(248,113,113,0.15); color:#f87171;">Cancel</button>
                        </div>
                    </div>
                </div>`;
            }

            // --- View mode ---
            const rows = blocks.map(b => {
                const dot = C[b.cat]?.dot || 'rgba(255,255,255,0.3)';
                const isSleep = b.label.includes('💤');
                const isNap = b.cat === 'nap' && b.label.includes('NAP');
                const isKids = b.cat === 'kids';
                const isDeep = b.cat === 'deepWork';
                const textColor = isSleep ? '#a78bfa'
                    : isNap ? '#c084fc'
                        : isKids ? '#38bdf8'
                            : isDeep ? '#00c9a0'
                                : 'var(--text-secondary)';
                const bold = (isSleep || isNap || isKids) ? 'font-weight:600;' : '';
                return `
                <div style="display:flex; gap:0.5rem; align-items:flex-start; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="font-size:0.71rem; color:var(--text-dim); min-width:42px; font-family:'VT323',monospace; flex-shrink:0; padding-top:2px;">${b.time}</span>
                    <span style="width:3px; height:3px; border-radius:50%; background:${dot}; flex-shrink:0; margin-top:7px;"></span>
                    <span style="font-size:0.81rem; color:${textColor}; line-height:1.4; ${bold}">${b.label}</span>
                </div>`;
            }).join('');

            const noteHtml = note
                ? `<p style="font-size:0.75rem; color:var(--text-dim); font-style:italic; margin:0 0 0.6rem; padding:3px 8px; border-left:2px solid var(--glass-border); line-height:1.5;">${note}</p>`
                : '';

            const typeBg = isOff ? 'rgba(0,200,160,0.08)' : 'rgba(251,191,36,0.08)';
            const typeBorder = isOff ? 'rgba(0,200,160,0.2)' : 'rgba(251,191,36,0.25)';
            const typeColor = isOff ? 'var(--accent-green)' : '#fbbf24';

            return `
            <div style="background:rgba(4,18,18,0.6); border:1px solid var(--glass-border); border-radius:4px; padding:1rem; transition:border-color 0.15s; position:relative;"
                 onmouseover="this.style.borderColor='var(--glass-border-hot)'"
                 onmouseout="this.style.borderColor='var(--glass-border)'">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                    <span style="font-family:'VT323',monospace; font-size:1.2rem; color:var(--text-primary); letter-spacing:1px;">${day}</span>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span style="font-size:0.7rem; padding:2px 8px; background:${typeBg}; border:1px solid ${typeBorder}; color:${typeColor}; border-radius:2px;">${type}</span>
                        <button class="iw-btn-icon iw-edit-day" data-day="${dayIdx}" title="Edit ${day}" style="color:var(--accent-green); background:rgba(0,200,160,0.08); border:1px solid rgba(0,200,160,0.15);">✎</button>
                    </div>
                </div>
                ${noteHtml}
                <div>${rows}</div>
            </div>`;
        }).join('');

        // -- Attach event listeners --
        attachListeners();
    }

    // ── Event delegation ──────────────────────────────────────
    function attachListeners() {
        const grid = document.getElementById('ideal-week-grid');
        if (!grid) return;

        // Remove old listener to avoid stacking
        grid.removeEventListener('click', handleGridClick);
        grid.addEventListener('click', handleGridClick);
    }

    function handleGridClick(e) {
        const target = e.target;

        // Edit day
        if (target.classList.contains('iw-edit-day')) {
            editingDay = parseInt(target.dataset.day);
            setDirtyGuard(true);
            renderIdealWeek();
            return;
        }

        // Cancel edit
        if (target.classList.contains('iw-cancel-day')) {
            editingDay = -1;
            setDirtyGuard(false);
            WEEK = loadWeek(); // revert unsaved changes
            renderIdealWeek();
            return;
        }

        // Save day
        if (target.classList.contains('iw-save-day')) {
            saveDayFromDOM(parseInt(target.dataset.day));
            return;
        }

        // Add block
        if (target.classList.contains('iw-add-block')) {
            const dayIdx = parseInt(target.dataset.day);
            const card = target.closest('.iw-card-editing');
            const blocksContainer = card.querySelector('.iw-edit-blocks');
            const newIdx = blocksContainer.querySelectorAll('.iw-edit-row').length;
            const newRow = document.createElement('div');
            newRow.className = 'iw-edit-row';
            newRow.dataset.bidx = newIdx;
            newRow.style.cssText = 'display:flex; gap:6px; align-items:center; padding:5px 0; border-bottom:1px solid rgba(255,255,255,0.04);';
            newRow.innerHTML = `
                <input type="text" value="" class="iw-input iw-time" style="width:52px; font-size:0.75rem; font-family:'VT323',monospace;" placeholder="HH:MM">
                <select class="iw-input iw-cat" style="width:90px; font-size:0.72rem;">
                    ${catOptions('routine')}
                </select>
                <input type="text" value="" class="iw-input iw-label" style="flex:1; font-size:0.78rem;" placeholder="Activity label">
                <button class="iw-btn-icon iw-del-block" title="Remove" style="color:#f87171; background:rgba(248,113,113,0.08); border:1px solid rgba(248,113,113,0.15);">✕</button>
            `;
            blocksContainer.appendChild(newRow);
            newRow.querySelector('.iw-time').focus();
            return;
        }

        // Delete block
        if (target.classList.contains('iw-del-block')) {
            target.closest('.iw-edit-row').remove();
            return;
        }
    }

    // ── Save from DOM ─────────────────────────────────────────
    function saveDayFromDOM(dayIdx) {
        const card = document.querySelector(`.iw-card-editing[data-day="${dayIdx}"]`);
        if (!card) return;

        const typeInput = card.querySelector('.iw-type-input');
        const noteInput = card.querySelector('.iw-note-input');
        const rows = card.querySelectorAll('.iw-edit-row');

        const blocks = [];
        rows.forEach(row => {
            const time = row.querySelector('.iw-time')?.value.trim();
            const cat = row.querySelector('.iw-cat')?.value;
            const label = row.querySelector('.iw-label')?.value.trim();
            if (time && label) {
                blocks.push({ time, label, cat: cat || 'routine' });
            }
        });

        // Sort by time
        blocks.sort((a, b) => {
            const ta = a.time.replace(':', '').padStart(4, '0');
            const tb = b.time.replace(':', '').padStart(4, '0');
            return ta.localeCompare(tb);
        });

        WEEK[dayIdx].type = typeInput?.value.trim() || WEEK[dayIdx].type;

        const newNote = noteInput?.value.trim() || '';
        if (!newNote && WEEK[dayIdx].note) {
            if (!confirm('Clear the day note? This cannot be undone.')) return;
        }
        WEEK[dayIdx].note = newNote;
        WEEK[dayIdx].blocks = blocks;

        saveWeek(WEEK);
        setDirtyGuard(false);
        editingDay = -1;
        renderIdealWeek();
    }

    // ── Reset to defaults ─────────────────────────────────────
    window._resetIdealWeek = function () {
        if (confirm('Reset all days to the original Ideal Week? Your edits will be lost.')) {
            localStorage.removeItem(STORAGE_KEY);
            WEEK = JSON.parse(JSON.stringify(DEFAULT_WEEK));
            editingDay = -1;
            renderIdealWeek();
        }
    };

    // ── Inject editor styles ──────────────────────────────────
    function injectStyles() {
        if (document.getElementById('iw-edit-styles')) return;
        const style = document.createElement('style');
        style.id = 'iw-edit-styles';
        style.textContent = `
            .iw-input {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 3px;
                color: var(--text-primary, #e8f0f2);
                padding: 4px 6px;
                font-family: 'Inter', sans-serif;
                outline: none;
                transition: border-color 0.15s;
            }
            .iw-input:focus {
                border-color: rgba(0,200,160,0.4);
            }
            .iw-input::placeholder {
                color: rgba(255,255,255,0.2);
            }
            select.iw-input {
                cursor: pointer;
            }
            select.iw-input option {
                background: #0d1520;
                color: #e8f0f2;
            }
            .iw-btn {
                background: rgba(64,224,208,0.08);
                border: 1px solid rgba(64,224,208,0.15);
                border-radius: 3px;
                color: var(--text-secondary, rgba(232,240,242,0.55));
                padding: 5px 12px;
                font-size: 0.75rem;
                font-family: 'Inter', sans-serif;
                cursor: pointer;
                transition: all 0.15s;
            }
            .iw-btn:hover {
                border-color: rgba(64,224,208,0.35);
                color: var(--text-primary, #e8f0f2);
            }
            .iw-btn-icon {
                width: 24px; height: 24px;
                display: flex; align-items: center; justify-content: center;
                border-radius: 3px;
                font-size: 0.8rem;
                cursor: pointer;
                transition: all 0.15s;
                padding: 0;
                line-height: 1;
                flex-shrink: 0;
            }
            .iw-btn-icon:hover {
                filter: brightness(1.3);
            }
        `;
        document.head.appendChild(style);
    }

    // ── Boot ──────────────────────────────────────────────────
    function boot() {
        injectStyles();
        renderIdealWeek();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

`

## public\_planner_sidebar.js
`javascript
// ============================================================
// PLANNER SIDEBAR — Mini Cal + Tasks + Notes
// ============================================================
(function initPlannerSidebar() {
    'use strict';

    const LS_TASKS = 'symphony_planner_tasks';
    const LS_NOTES = 'symphony_planner_notes';

    // ── Mini Calendar ─────────────────────────────────
    function renderMiniCal() {
        const el = document.getElementById('planner-mini-cal');
        if (!el) return;

        const now = new Date();
        const y = now.getFullYear();
        const m = now.getMonth();
        const today = now.getDate();

        const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'];
        const DAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

        const firstDow = new Date(y, m, 1).getDay(); // 0=Sun
        const daysInMonth = new Date(y, m + 1, 0).getDate();

        let html = `<div class="mini-cal-month-label">${MONTHS[m]} ${y}</div>`;
        html += `<div class="mini-cal-grid">`;

        // Day headers
        DAYS.forEach(d => {
            html += `<div class="mini-cal-day-header">${d}</div>`;
        });

        // Empty leading cells
        for (let i = 0; i < firstDow; i++) {
            html += `<div class="mini-cal-cell other-month"></div>`;
        }

        // Day cells
        for (let d = 1; d <= daysInMonth; d++) {
            const isToday = d === today;
            html += `<div class="mini-cal-cell${isToday ? ' today' : ''}">${d}</div>`;
        }

        html += `</div>`;
        el.innerHTML = html;
    }

    // ── Tasks ─────────────────────────────────────────
    function loadTasks() {
        try { return JSON.parse(localStorage.getItem(LS_TASKS) || '[]'); } catch { return []; }
    }
    function saveTasks(tasks) { localStorage.setItem(LS_TASKS, JSON.stringify(tasks)); }

    function renderTasks() {
        const list = document.getElementById('planner-task-list');
        if (!list) return;
        const tasks = loadTasks();
        list.innerHTML = tasks.map((t, i) => `
            <li class="sidebar-task-item${t.done ? ' done' : ''}" data-idx="${i}">
                <input type="checkbox" ${t.done ? 'checked' : ''}>
                <span>${escHtml(t.text)}</span>
                <button title="Remove">✕</button>
            </li>
        `).join('');

        list.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', () => {
                const idx = +cb.closest('li').dataset.idx;
                const tasks = loadTasks();
                tasks[idx].done = cb.checked;
                saveTasks(tasks);
                renderTasks();
            });
        });

        list.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => {
                const idx = +btn.closest('li').dataset.idx;
                const tasks = loadTasks();
                tasks.splice(idx, 1);
                saveTasks(tasks);
                renderTasks();
            });
        });
    }

    function wireTaskInput() {
        const input = document.getElementById('planner-task-input');
        if (!input) return;
        input.addEventListener('keydown', e => {
            if (e.key !== 'Enter') return;
            const text = input.value.trim();
            if (!text) return;
            const tasks = loadTasks();
            tasks.push({ text, done: false });
            saveTasks(tasks);
            input.value = '';
            renderTasks();
        });
    }

    // ── Notes ─────────────────────────────────────────
    function initNotes() {
        const area = document.getElementById('planner-notes-area');
        if (!area) return;
        area.value = localStorage.getItem(LS_NOTES) || '';
        area.addEventListener('input', () => {
            localStorage.setItem(LS_NOTES, area.value);
        });
    }

    // ── Helpers ───────────────────────────────────────
    function escHtml(s) {
        return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    // ── Boot ──────────────────────────────────────────
    function boot() {
        renderMiniCal();
        renderTasks();
        wireTaskInput();
        initNotes();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }
})();

`

## public\_planner_v2.js
`javascript

// ============================================================
// PLANNER ENGINE v2 — Named Blocks + Recurring Tasks + Yearly
// ============================================================
(function initPlannerV2() {
    'use strict';

    // ── Constants ──────────────────────────────────────────
    const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const DAYS_SHORT = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const BLOCK_COLOURS = [
        { name: 'Coral', bg: 'rgba(239,68,68,0.22)', border: '#ef4444', dot: '#ef4444' },
        { name: 'Orange', bg: 'rgba(249,115,22,0.22)', border: '#f97316', dot: '#f97316' },
        { name: 'Amber', bg: 'rgba(245,158,11,0.22)', border: '#f59e0b', dot: '#f59e0b' },
        { name: 'Green', bg: 'rgba(52,211,153,0.22)', border: '#34d399', dot: '#34d399' },
        { name: 'Sky', bg: 'rgba(56,189,248,0.22)', border: '#38bdf8', dot: '#38bdf8' },
        { name: 'Blue', bg: 'rgba(96,165,250,0.22)', border: '#60a5fa', dot: '#60a5fa' },
        { name: 'Violet', bg: 'rgba(167,139,250,0.22)', border: '#a78bfa', dot: '#a78bfa' },
        { name: 'Pink', bg: 'rgba(244,114,182,0.22)', border: '#f472b6', dot: '#f472b6' },
    ];
    const FREE_COLOUR = { bg: 'rgba(255,255,255,0.04)', border: 'rgba(255,255,255,0.12)', dot: 'rgba(255,255,255,0.3)' };
    const EVENT_COLOURS = ['#f472b6', '#60a5fa', '#34d399', '#f97316', '#a78bfa', '#facc15', '#22d3ee', '#ef4444'];
    const DUE_DAYS = DAYS;

    // ── Storage helpers ────────────────────────────────────
    const LS_TEMPLATES = 'symphony_templates_v1';
    const LS_RECURRING = 'symphony_recurring_v1';
    const LS_EVENTS = 'symphony_yearly_events_v1';

    function loadTemplates() { try { return JSON.parse(localStorage.getItem(LS_TEMPLATES) || '{}'); } catch { return {}; } }
    function saveTemplates(d) { localStorage.setItem(LS_TEMPLATES, JSON.stringify(d)); }
    function loadRecurring() { try { return JSON.parse(localStorage.getItem(LS_RECURRING) || '[]'); } catch { return []; } }
    function saveRecurring(d) { localStorage.setItem(LS_RECURRING, JSON.stringify(d)); }
    function loadEvents() { try { return JSON.parse(localStorage.getItem(LS_EVENTS) || '[]'); } catch { return []; } }
    function saveEvents(d) { localStorage.setItem(LS_EVENTS, JSON.stringify(d)); }

    // ── Date utils ─────────────────────────────────────────
    function localDateStr(dt) {
        return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
    }
    function daysSince(dateStr) {
        if (!dateStr) return null;
        const diff = Date.now() - new Date(dateStr + 'T00:00:00').getTime();
        return Math.floor(diff / 86400000);
    }
    function friendlyDate(dateStr) {
        if (!dateStr) return '—';
        const d = new Date(dateStr + 'T00:00:00');
        return `${DAYS_SHORT[d.getDay() === 0 ? 6 : d.getDay() - 1]} ${d.getDate()} ${MONTHS[d.getMonth()]}`;
    }
    function todayDowName() {
        const dow = new Date().getDay();
        return DAYS[dow === 0 ? 6 : dow - 1];
    }

    // ── Planner view state ─────────────────────────────────
    let plannerSection = 'template';
    let yearlyYear = new Date().getFullYear();

    // ── Modal state ────────────────────────────────────────
    let blockModal = { day: null, blockId: null };
    let eventModal = { dateStr: null, eventId: null };
    let selectedBlockColour = 0;
    let selectedEventColour = EVENT_COLOURS[0];

    // ── Colour swatches ────────────────────────────────────
    function renderColourPicker(containerId, colours, selectedIdx, onSelect) {
        const el = document.getElementById(containerId);
        if (!el) return;
        el.innerHTML = '';
        colours.forEach((c, i) => {
            const swatch = document.createElement('div');
            const bg = typeof c === 'string' ? c : c.border;
            swatch.style.cssText = `width:22px;height:22px;border-radius:50%;background:${bg};cursor:pointer;border:2px solid ${i === selectedIdx ? '#fff' : 'transparent'};transition:border 0.15s;`;
            swatch.title = typeof c === 'string' ? c : c.name;
            swatch.addEventListener('click', () => { onSelect(i); renderColourPicker(containerId, colours, i, onSelect); });
            el.appendChild(swatch);
        });
    }

    // ─────────────────────────────────────────────────────
    // TEMPLATE EDITOR
    // ─────────────────────────────────────────────────────
    function renderTemplateEditor() {
        const container = document.getElementById('planner-template-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayDay = todayDowName();

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">📋 WEEKLY TEMPLATE</div>`;

        DAYS.forEach(day => {
            const blocks = (templates[day] || []).slice().sort((a, b) => a.start.localeCompare(b.start));
            const isToday = day === todayDay;

            html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem; min-height:42px;">`;
            // Day label
            html += `<div style="width:96px; min-width:96px; font-weight:bold; font-size:0.95rem; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'}; border-left:3px solid ${isToday ? 'var(--accent-green)' : 'rgba(255,255,255,0.15)'}; padding-left:8px;">${day}</div>`;

            // Block strip
            html += `<div style="flex:1; display:flex; flex-wrap:wrap; gap:6px; align-items:center;">`;

            if (blocks.length === 0) {
                html += `<div style="background:${FREE_COLOUR.bg}; border:1px dashed ${FREE_COLOUR.border}; border-radius:16px; padding:6px 14px; font-size:0.82rem; color:rgba(255,255,255,0.35); cursor:pointer; user-select:none;" data-add-block="${day}">🕓 Free all day — click to add block</div>`;
            } else {
                // Render each block as a pill
                blocks.forEach(b => {
                    const ci = typeof b.colour === 'number' ? b.colour : 0;
                    const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                    const duration = calcDuration(b.start, b.end);
                    html += `<div class="template-block" data-day="${day}" data-bid="${b.id}" style="background:${c.bg}; border:1px solid ${c.border}; border-radius:16px; padding:6px 14px; font-size:0.85rem; cursor:pointer; user-select:none; display:flex; align-items:center; gap:6px; transition:opacity 0.15s; white-space:nowrap;">`;
                    html += `<span style="width:8px;height:8px;border-radius:50%;background:${c.dot};display:inline-block;flex-shrink:0;"></span>`;
                    html += `<span style="font-weight:bold;">${b.label}</span>`;
                    html += `<span style="opacity:0.6; font-size:0.78rem;">${b.start}–${b.end}${duration ? ' · ' + duration : ''}</span>`;
                    html += `</div>`;
                });
                // Add button at end of strip
                html += `<button data-add-block="${day}" style="background:rgba(52,211,153,0.1); border:1px dashed var(--accent-green); color:var(--accent-green); border-radius:16px; padding:5px 12px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">+ block</button>`;
            }

            html += `</div></div>`;

            // Subtle separator
            if (day !== 'Sunday') {
                html += `<div style="height:1px; background:rgba(255,255,255,0.06); margin:0 0 0 104px; margin-bottom:2px;"></div>`;
            }
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire block clicks (edit)
        container.querySelectorAll('.template-block').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.day, el.dataset.bid));
        });
        // Wire add buttons
        container.querySelectorAll('[data-add-block]').forEach(el => {
            el.addEventListener('click', () => openBlockModal(el.dataset.addBlock, null));
        });
    }

    function calcDuration(start, end) {
        if (!start || !end) return '';
        const [sh, sm] = start.split(':').map(Number);
        const [eh, em] = end.split(':').map(Number);
        const mins = (eh * 60 + em) - (sh * 60 + sm);
        if (mins <= 0) return '';
        if (mins < 60) return `${mins}m`;
        const h = Math.floor(mins / 60), m = mins % 60;
        return m ? `${h}h ${m}m` : `${h}h`;
    }

    // ── Block Modal ────────────────────────────────────────
    function openBlockModal(day, blockId) {
        blockModal = { day, blockId };
        const modal = document.getElementById('block-modal');
        const titleEl = document.getElementById('block-modal-title');
        const labelEl = document.getElementById('block-label');
        const startEl = document.getElementById('block-start');
        const endEl = document.getElementById('block-end');
        const delBtn = document.getElementById('block-modal-delete');
        if (!modal) return;

        const templates = loadTemplates();
        const blocks = templates[day] || [];
        const block = blockId ? blocks.find(b => b.id === blockId) : null;

        titleEl.textContent = block ? `Edit Block — ${day}` : `Add Block — ${day}`;
        labelEl.value = block ? block.label : '';
        startEl.value = block ? block.start : '07:00';
        endEl.value = block ? block.end : '08:00';
        selectedBlockColour = block ? (block.colour || 0) : 0;
        delBtn.style.display = block ? 'inline-block' : 'none';

        renderColourPicker('block-colour-picker', BLOCK_COLOURS, selectedBlockColour, idx => { selectedBlockColour = idx; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeBlockModal() {
        const modal = document.getElementById('block-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveBlock() {
        const label = document.getElementById('block-label').value.trim();
        const start = document.getElementById('block-start').value;
        const end = document.getElementById('block-end').value;
        if (!label) { alert('Please enter a block name.'); return; }
        const templates = loadTemplates();
        if (!templates[blockModal.day]) templates[blockModal.day] = [];
        const blocks = templates[blockModal.day];
        if (blockModal.blockId) {
            const idx = blocks.findIndex(b => b.id === blockModal.blockId);
            if (idx >= 0) blocks[idx] = { ...blocks[idx], label, start, end, colour: selectedBlockColour };
        } else {
            blocks.push({ id: Date.now().toString(), label, start, end, colour: selectedBlockColour });
        }
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    function deleteBlock() {
        if (!blockModal.blockId) return;
        const templates = loadTemplates();
        const blocks = templates[blockModal.day] || [];
        const idx = blocks.findIndex(b => b.id === blockModal.blockId);
        if (idx >= 0) blocks.splice(idx, 1);
        saveTemplates(templates);
        closeBlockModal();
        renderTemplateEditor();
    }

    // ─────────────────────────────────────────────────────
    // RECURRING TASKS MANAGER
    // ─────────────────────────────────────────────────────
    function renderRecurringManager() {
        const container = document.getElementById('planner-recurring-manager');
        if (!container) return;
        const tasks = loadRecurring();
        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1.1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px;">🔁 RECURRING TASKS</div>`;

        // Add form
        html += `<div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1.25rem; align-items:center;">`;
        html += `<input id="rt-title" type="text" placeholder="Task name..." style="flex:2 1 160px; padding:0.35rem 0.6rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<select id="rt-freq" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        html += `<option value="weekly">Weekly</option><option value="monthly">Monthly</option></select>`;
        html += `<select id="rt-dueday" style="padding:0.35rem; background:rgba(0,0,0,0.35); border:1px solid var(--glass-border); color:#fff; font-family:'VT323',monospace; font-size:0.95rem; border-radius:3px;">`;
        DAYS.forEach(d => { html += `<option value="${d}">${d}</option>`; });
        html += `</select>`;
        html += `<button id="rt-add-btn" style="padding:0.35rem 1rem; background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.95rem; cursor:pointer; border-radius:3px; font-weight:bold;">+ Add</button>`;
        html += `</div>`;

        // Render two lists
        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            const label = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:1rem;">`;
            html += `<div style="font-size:0.85rem; color:var(--text-secondary); font-weight:bold; margin-bottom:0.4rem; letter-spacing:1px;">${label}</div>`;
            if (list.length === 0) {
                html += `<div style="color:rgba(255,255,255,0.3); font-style:italic; font-size:0.85rem; padding:0.4rem 0;">No ${freq} tasks yet.</div>`;
            } else {
                list.forEach(t => {
                    const ago = daysSince(t.lastDone);
                    const agoText = ago === null ? 'Never done' : ago === 0 ? 'Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                    const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Last done: never';
                    const dueLabel = freq === 'weekly' && t.dueDay ? ` · due by ${t.dueDay}` : '';
                    html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.35rem;">`;
                    html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid rgba(255,255,255,0.08); border-radius:4px; padding:6px 10px;">`;
                    html += `<div style="font-size:0.9rem; font-weight:bold;">${t.title}<span style="opacity:0.45; font-size:0.78rem;">${dueLabel}</span></div>`;
                    html += `<div style="font-size:0.75rem; color:var(--text-secondary); margin-top:1px;">${lastText}</div>`;
                    html += `</div>`;
                    html += `<button class="rt-delete-btn" data-rtid="${t.id}" style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.4); color:#ef4444; border-radius:3px; padding:3px 8px; font-family:'VT323',monospace; font-size:0.85rem; cursor:pointer;">✕</button>`;
                    html += `</div>`;
                });
            }
            html += `</div>`;
        });

        html += `</div>`;
        container.innerHTML = html;

        // Wire add
        const addBtn = container.querySelector('#rt-add-btn');
        if (addBtn) addBtn.addEventListener('click', () => {
            const title = container.querySelector('#rt-title').value.trim();
            const freq = container.querySelector('#rt-freq').value;
            const dueDay = container.querySelector('#rt-dueday').value;
            if (!title) return;
            const tasks = loadRecurring();
            tasks.push({ id: Date.now().toString(), title, freq, dueDay: freq === 'weekly' ? dueDay : null, lastDone: null, history: [] });
            saveRecurring(tasks);
            renderRecurringManager();
            renderRecurringDisplay();
        });
        // Wire deletes
        container.querySelectorAll('.rt-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring().filter(t => t.id !== btn.dataset.rtid);
                saveRecurring(tasks);
                renderRecurringManager();
                renderRecurringDisplay();
            });
        });
        // Wire freq toggle for dueday visibility
        const freqSel = container.querySelector('#rt-freq');
        const dueSel = container.querySelector('#rt-dueday');
        if (freqSel && dueSel) {
            freqSel.addEventListener('change', () => {
                dueSel.style.display = freqSel.value === 'weekly' ? 'inline-block' : 'none';
            });
        }
    }

    // ─────────────────────────────────────────────────────
    // YEARLY WALL
    // ─────────────────────────────────────────────────────
    function renderYearlyWall() {
        const container = document.getElementById('planner-yearly-grid');
        if (!container) return;

        const events = loadEvents();
        const todayStr = localDateStr(new Date());
        const nowYear = new Date().getFullYear();
        const MCOLS = ['#60a5fa', '#a78bfa', '#f472b6', '#fb923c', '#facc15', '#34d399', '#22d3ee', '#818cf8', '#f87171', '#4ade80', '#fbbf24', '#c084fc'];

        function daysInMonth(mi) { return new Date(yearlyYear, mi + 1, 0).getDate(); }
        function dateStr(mi, d) {
            if (d > daysInMonth(mi)) return null;
            return `${yearlyYear}-${String(mi + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
        }
        function getEventsForDate(str) {
            if (!str) return [];
            const [y, m, d] = str.split('-').map(Number);
            return events.filter(ev => {
                if (ev.recurrence === 'annual') return ev.month === m && ev.day === d;
                return ev.date === str;
            });
        }

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Year nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.5rem; margin-bottom:1rem;">`;
        html += `<button id="yearly-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="font-size:1.8rem; font-weight:bold; color:var(--accent-yellow); letter-spacing:2px;">📌 ${yearlyYear}</div>`;
        html += `<button id="yearly-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 16px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;
        html += `<div style="font-size:0.78rem; color:var(--text-secondary); margin-bottom:0.75rem;">Click any date to add/edit an event.</div>`;

        html += `<div style="overflow-x:auto;"><table style="border-collapse:collapse; width:100%; table-layout:fixed; min-width:520px; font-family:'VT323',monospace;">`;

        // Month header row
        html += `<thead><tr>`;
        html += `<th style="width:30px; min-width:30px; padding:3px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.08); color:var(--text-secondary); font-size:0.7rem; text-align:center;">#</th>`;
        MONTHS.forEach((name, mi) => {
            const isCur = mi === new Date().getMonth() && yearlyYear === nowYear;
            html += `<th style="padding:4px 2px; background:${isCur ? 'rgba(52,211,153,0.12)' : 'rgba(0,0,0,0.4)'}; border:1px solid ${isCur ? 'rgba(52,211,153,0.4)' : 'rgba(255,255,255,0.08)'}; color:${isCur ? 'var(--accent-green)' : MCOLS[mi]}; font-size:0.82rem; font-weight:bold; text-align:center; letter-spacing:1px;">${name}</th>`;
        });
        html += `</tr></thead><tbody>`;

        // Day rows 1–31
        for (let d = 1; d <= 31; d++) {
            const altRow = d % 2 === 0;
            html += `<tr>`;
            html += `<td style="padding:1px 3px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.06); color:var(--text-secondary); font-size:0.72rem; text-align:center; font-weight:bold;">${d}</td>`;
            MONTHS.forEach((_, mi) => {
                const str = dateStr(mi, d);
                const isToday = str === todayStr;
                const isValid = str !== null;
                const evs = isValid ? getEventsForDate(str) : [];
                let isWeekend = false;
                if (isValid) {
                    const dow = new Date(str + 'T00:00:00').getDay();
                    isWeekend = dow === 0 || dow === 6;
                }
                const bg = isToday ? 'rgba(52,211,153,0.18)'
                    : !isValid ? 'rgba(0,0,0,0.3)'
                        : isWeekend ? 'rgba(255,255,255,0.025)'
                            : altRow ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.1)';
                const bdr = isToday ? '1px solid rgba(52,211,153,0.5)' : '1px solid rgba(255,255,255,0.05)';
                const glow = isToday ? 'box-shadow:inset 0 0 0 1px rgba(52,211,153,0.4);' : '';

                let inner = '';
                if (!isValid) {
                    inner = `<div style="width:100%;height:100%;background:repeating-linear-gradient(45deg,rgba(255,255,255,0.015) 0,rgba(255,255,255,0.015) 1px,transparent 1px,transparent 4px);"></div>`;
                } else if (evs.length > 0) {
                    evs.slice(0, 2).forEach(ev => {
                        inner += `<div style="background:${ev.color}22; border-left:2px solid ${ev.color}; border-radius:1px; padding:0 2px; font-size:0.58rem; line-height:1.4; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${ev.emoji || ''} ${ev.label}</div>`;
                    });
                }

                const cursor = isValid ? 'cursor:pointer;' : 'cursor:default;';
                html += `<td class="yearly-cell" data-date="${str || ''}" data-valid="${isValid ? '1' : '0'}"
                    style="padding:1px; background:${bg}; border:${bdr}; height:24px; vertical-align:top; overflow:hidden; ${cursor} ${glow} transition:background 0.1s;"
                    title="${str || 'n/a'}">
                    ${inner}
                </td>`;
            });
            html += `</tr>`;
        }
        html += `</tbody></table></div></div>`;
        container.innerHTML = html;

        // Year nav
        container.querySelector('#yearly-prev').addEventListener('click', () => { yearlyYear--; renderYearlyWall(); });
        container.querySelector('#yearly-next').addEventListener('click', () => { yearlyYear++; renderYearlyWall(); });

        // Cell clicks
        container.querySelectorAll('.yearly-cell').forEach(cell => {
            if (cell.dataset.valid !== '1') return;
            cell.addEventListener('mouseenter', () => { cell.style.background = 'rgba(52,211,153,0.1)'; });
            cell.addEventListener('mouseleave', () => { cell.style.background = ''; });
            cell.addEventListener('click', () => openEventModal(cell.dataset.date));
        });
    }

    // ── Event Modal ────────────────────────────────────────
    function openEventModal(dateStr_arg) {
        const modal = document.getElementById('event-modal');
        const titleEl = document.getElementById('event-modal-title');
        const labelEl = document.getElementById('event-label');
        const emojiEl = document.getElementById('event-emoji');
        const annualEl = document.getElementById('event-annual');
        const delBtn = document.getElementById('event-modal-delete');
        if (!modal) return;

        const [y, m, d] = dateStr_arg.split('-').map(Number);
        const events = loadEvents();
        // Find existing event on this specific date
        const existing = events.find(ev => ev.recurrence === 'once' ? ev.date === dateStr_arg : (ev.month === m && ev.day === d));

        eventModal = { dateStr: dateStr_arg, eventId: existing ? existing.id : null };
        titleEl.textContent = existing
            ? `Edit Event — ${MONTHS[m - 1]} ${d}`
            : `Add Event — ${MONTHS[m - 1]} ${d}`;
        labelEl.value = existing ? existing.label : '';
        emojiEl.value = existing ? (existing.emoji || '📅') : '📅';
        annualEl.checked = existing ? existing.recurrence === 'annual' : false;
        selectedEventColour = existing ? existing.color : EVENT_COLOURS[0];
        delBtn.style.display = existing ? 'inline-block' : 'none';

        renderColourPicker('event-colour-picker', EVENT_COLOURS, EVENT_COLOURS.indexOf(selectedEventColour) || 0, idx => { selectedEventColour = EVENT_COLOURS[idx]; });
        modal.style.display = 'flex';
        labelEl.focus();
    }

    function closeEventModal() {
        const modal = document.getElementById('event-modal');
        if (modal) modal.style.display = 'none';
    }

    function saveEvent() {
        const label = document.getElementById('event-label').value.trim();
        const emoji = document.getElementById('event-emoji').value;
        const annual = document.getElementById('event-annual').checked;
        if (!label) { alert('Please enter an event name.'); return; }
        const [y, m, d] = eventModal.dateStr.split('-').map(Number);
        const events = loadEvents();
        const newEv = { id: eventModal.eventId || Date.now().toString(), label, emoji, color: selectedEventColour, recurrence: annual ? 'annual' : 'once' };
        if (annual) { newEv.month = m; newEv.day = d; }
        else { newEv.date = eventModal.dateStr; }
        const idx = events.findIndex(e => e.id === newEv.id);
        if (idx >= 0) events[idx] = newEv; else events.push(newEv);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    function deleteEvent() {
        if (!eventModal.eventId) return;
        const events = loadEvents().filter(e => e.id !== eventModal.eventId);
        saveEvents(events);
        closeEventModal();
        renderYearlyWall();
    }

    // ─────────────────────────────────────────────────────
    // SCHEDULE PAGE — Day display + Recurring Tasks
    // ─────────────────────────────────────────────────────
    let schedDayOffset = 0;

    function renderScheduleDisplay() {
        renderScheduleDayBlocks();
        renderRecurringDisplay();
    }

    function renderScheduleDayBlocks() {
        const container = document.getElementById('schedule-week-grid');
        if (!container) return;
        const templates = loadTemplates();
        const todayStr = localDateStr(new Date());

        const viewDate = new Date();
        viewDate.setDate(viewDate.getDate() + schedDayOffset);
        const viewDow = viewDate.getDay();
        const dayName = DAYS[viewDow === 0 ? 6 : viewDow - 1];
        const isToday = localDateStr(viewDate) === todayStr;

        const blocks = (templates[dayName] || []).slice().sort((a, b) => a.start.localeCompare(b.start));

        let html = `<div style="font-family:'VT323',monospace;">`;
        // Nav
        html += `<div style="display:flex; align-items:center; justify-content:center; gap:1.25rem; margin-bottom:1.25rem;">`;
        html += `<button id="sched-prev" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">◄</button>`;
        html += `<div style="text-align:center; min-width:200px;">`;
        html += `<div style="font-size:1.6rem; font-weight:bold; color:${isToday ? 'var(--accent-green)' : 'var(--text-primary)'};">${dayName}${isToday ? ' <span style="font-size:0.7rem;">← TODAY</span>' : ''}</div>`;
        html += `<div style="font-size:0.82rem; color:var(--text-secondary);">${viewDate.getDate()}/${viewDate.getMonth() + 1}/${viewDate.getFullYear()}</div>`;
        if (!isToday) { html += `<button id="sched-today" style="margin-top:3px; background:none; border:1px solid var(--accent-green); color:var(--accent-green); font-family:'VT323',monospace; font-size:0.78rem; padding:1px 10px; cursor:pointer; border-radius:2px;">↩ Today</button>`; }
        html += `</div>`;
        html += `<button id="sched-next" style="background:#c0c0c0; border:2px outset #fff; color:#000; font-family:'VT323',monospace; font-size:1.3rem; padding:2px 14px; cursor:pointer; line-height:1;">►</button>`;
        html += `</div>`;

        // Blocks
        if (blocks.length === 0) {
            html += `<div style="background:rgba(52,211,153,0.04); border:1px solid rgba(52,211,153,0.15); border-radius:6px; padding:2rem; text-align:center; color:var(--text-secondary);">No template set for ${dayName}. Go to Planner → Template to add blocks.</div>`;
        } else {
            html += `<div style="display:flex; flex-direction:column; gap:6px;">`;
            blocks.forEach(b => {
                const ci = typeof b.colour === 'number' ? b.colour : 0;
                const c = BLOCK_COLOURS[ci] || BLOCK_COLOURS[0];
                const dur = calcDuration(b.start, b.end);
                html += `<div style="background:${c.bg}; border-left:3px solid ${c.border}; border-radius:4px; padding:10px 14px; display:flex; align-items:center; gap:12px;">`;
                html += `<div style="text-align:right; min-width:90px; font-size:0.82rem; color:var(--text-secondary);">${b.start} – ${b.end}</div>`;
                html += `<div style="flex:1;"><div style="font-size:1rem; font-weight:bold;">${b.label}</div>${dur ? `<div style="font-size:0.75rem; color:${c.border}; opacity:0.7;">${dur}</div>` : ''}</div>`;
                html += `</div>`;
            });
            html += `</div>`;
        }
        html += `</div>`;
        container.innerHTML = html;

        // Wire nav
        container.querySelector('#sched-prev')?.addEventListener('click', () => { schedDayOffset--; renderScheduleDayBlocks(); });
        container.querySelector('#sched-next')?.addEventListener('click', () => { schedDayOffset++; renderScheduleDayBlocks(); });
        container.querySelector('#sched-today')?.addEventListener('click', () => { schedDayOffset = 0; renderScheduleDayBlocks(); });
    }

    function renderRecurringDisplay() {
        // Find or create the recurring display container in schedule section
        let container = document.getElementById('schedule-recurring-display');
        if (!container) {
            const schedGrid = document.getElementById('schedule-week-grid');
            if (!schedGrid) return;
            container = document.createElement('div');
            container.id = 'schedule-recurring-display';
            container.style.marginTop = '1.5rem';
            schedGrid.parentNode.insertBefore(container, schedGrid.nextSibling);
        }

        const tasks = loadRecurring();
        if (tasks.length === 0) { container.innerHTML = ''; return; }

        const todayStr = localDateStr(new Date());
        const todayDow = new Date().getDay(); // 0=Sun
        const todayDayName = DAYS[todayDow === 0 ? 6 : todayDow - 1];
        // Which Monday started this week?
        const monday = new Date();
        const dayOfWeek = monday.getDay();
        const daysToMon = dayOfWeek === 0 ? 6 : dayOfWeek - 1;
        monday.setDate(monday.getDate() - daysToMon);
        const weekStartStr = localDateStr(monday);

        const weekly = tasks.filter(t => t.freq === 'weekly');
        const monthly = tasks.filter(t => t.freq === 'monthly');

        let html = `<div style="font-family:'VT323',monospace;">`;
        html += `<div style="font-size:1rem; color:var(--accent-yellow); font-weight:bold; margin-bottom:0.75rem; letter-spacing:1px; border-top:1px solid rgba(255,255,255,0.08); padding-top:1rem;">🔁 RECURRING TASKS</div>`;

        ['weekly', 'monthly'].forEach(freq => {
            const list = freq === 'weekly' ? weekly : monthly;
            if (list.length === 0) return;
            const freqLabel = freq === 'weekly' ? '📅 Weekly' : '📆 Monthly';
            html += `<div style="margin-bottom:0.75rem;">`;
            html += `<div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.35rem; letter-spacing:1px;">${freqLabel}</div>`;
            list.forEach(t => {
                const ago = daysSince(t.lastDone);
                const agoText = ago === null ? 'Never done' : ago === 0 ? '✓ Done today' : `${ago} day${ago === 1 ? '' : 's'} ago`;
                const lastText = t.lastDone ? `Last done: ${friendlyDate(t.lastDone)} — ${agoText}` : 'Never done';

                // Overdue logic for weekly tasks
                let overdue = false;
                if (freq === 'weekly' && t.dueDay) {
                    const dueIdx = DAYS.indexOf(t.dueDay);
                    const curIdx = DAYS.indexOf(todayDayName);
                    const doneSinceWeekStart = t.lastDone && t.lastDone >= weekStartStr;
                    overdue = !doneSinceWeekStart && curIdx >= dueIdx;
                }

                const doneToday = t.lastDone === todayStr;
                const dueLabel = freq === 'weekly' && t.dueDay ? ` <span style="opacity:0.5; font-size:0.78rem;">· due by ${t.dueDay}</span>` : '';

                html += `<div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">`;
                html += `<div style="flex:1; background:rgba(0,0,0,0.2); border:1px solid ${overdue ? 'rgba(239,68,68,0.4)' : 'rgba(255,255,255,0.07)'}; border-radius:4px; padding:7px 10px;">`;
                html += `<div style="font-size:0.92rem; font-weight:bold;">${t.title}${dueLabel}${overdue ? ' <span style="color:#ef4444; font-size:0.75rem;">⚠ OVERDUE</span>' : ''}</div>`;
                html += `<div style="font-size:0.75rem; color:${doneToday ? 'var(--accent-green)' : 'var(--text-secondary)'}; margin-top:1px;">${lastText}</div>`;
                html += `</div>`;
                if (!doneToday) {
                    html += `<button class="rt-done-btn" data-rtid="${t.id}" style="background:rgba(52,211,153,0.15); border:1px solid var(--accent-green); color:var(--accent-green); border-radius:3px; padding:5px 10px; font-family:'VT323',monospace; font-size:0.82rem; cursor:pointer; white-space:nowrap;">✓ Done</button>`;
                } else {
                    html += `<div style="color:var(--accent-green); font-size:0.82rem; padding:5px 8px;">✓</div>`;
                }
                html += `</div>`;
            });
            html += `</div>`;
        });
        html += `</div>`;
        container.innerHTML = html;

        // Wire done buttons
        container.querySelectorAll('.rt-done-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const tasks = loadRecurring();
                const t = tasks.find(t => t.id === btn.dataset.rtid);
                if (!t) return;
                t.lastDone = todayStr;
                if (!t.history) t.history = [];
                t.history.push(todayStr);
                saveRecurring(tasks);
                renderRecurringDisplay();
                renderRecurringManager();
            });
        });
    }

    // ─────────────────────────────────────────────────────
    // PLANNER VIEW SWITCHING
    // ─────────────────────────────────────────────────────
    function switchPlannerView(view) {
        plannerSection = view;
        const tmplBtn = document.getElementById('planner-view-template');
        const yearlyBtn = document.getElementById('planner-view-yearly');
        const tmplSec = document.getElementById('planner-template-section');
        const yearlySec = document.getElementById('planner-yearly-section');
        const ACTIVE = { background: 'rgba(52,211,153,0.2)', borderColor: 'var(--accent-green)', color: 'var(--accent-green)', fontWeight: 'bold' };
        const INACTIVE = { background: 'rgba(0,0,0,0.2)', borderColor: 'var(--glass-border)', color: 'var(--text-secondary)', fontWeight: 'normal' };
        const applyStyle = (btn, s) => { if (!btn) return; Object.assign(btn.style, s); };

        if (view === 'yearly') {
            applyStyle(tmplBtn, INACTIVE);
            applyStyle(yearlyBtn, ACTIVE);
            if (tmplSec) tmplSec.style.display = 'none';
            if (yearlySec) yearlySec.style.display = 'block';
            renderYearlyWall();
        } else {
            applyStyle(tmplBtn, ACTIVE);
            applyStyle(yearlyBtn, INACTIVE);
            if (tmplSec) tmplSec.style.display = 'block';
            if (yearlySec) yearlySec.style.display = 'none';
            renderTemplateEditor();
            renderRecurringManager();
        }
    }

    // ─────────────────────────────────────────────────────
    // INIT
    // ─────────────────────────────────────────────────────
    function boot() {
        // Planner view toggles
        document.getElementById('planner-view-template')?.addEventListener('click', () => switchPlannerView('template'));
        document.getElementById('planner-view-yearly')?.addEventListener('click', () => switchPlannerView('yearly'));

        // Block modal buttons
        document.getElementById('block-modal-save')?.addEventListener('click', saveBlock);
        document.getElementById('block-modal-delete')?.addEventListener('click', deleteBlock);
        document.getElementById('block-modal-cancel')?.addEventListener('click', closeBlockModal);
        document.getElementById('block-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeBlockModal(); });

        // Event modal buttons
        document.getElementById('event-modal-save')?.addEventListener('click', saveEvent);
        document.getElementById('event-modal-delete')?.addEventListener('click', deleteEvent);
        document.getElementById('event-modal-cancel')?.addEventListener('click', closeEventModal);
        document.getElementById('event-modal')?.addEventListener('click', e => { if (e.target === e.currentTarget) closeEventModal(); });

        // Hook planner tab
        document.querySelectorAll('.tab-btn[data-tab]').forEach(btn => {
            btn.addEventListener('click', () => {
                const t = btn.getAttribute('data-tab');
                if (t === 'planner') { switchPlannerView(plannerSection); }
                if (t === 'today') { renderScheduleDisplay(); }
            });
        });

        // Initial render
        switchPlannerView('template');
        renderScheduleDisplay();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

})();
// --- End Planner Engine v2 ---

`

