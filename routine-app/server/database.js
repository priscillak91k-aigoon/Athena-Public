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
