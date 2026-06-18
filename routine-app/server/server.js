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
