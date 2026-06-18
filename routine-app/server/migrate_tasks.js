const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'data', 'lifehub.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database', err.message);
        process.exit(1);
    }
    console.log(`Connected to the SQLite database at ${dbPath}`);
});

db.serialize(() => {
    db.run("PRAGMA foreign_keys = OFF;");
    
    // Create new table with TEXT for task_id
    db.run(`CREATE TABLE IF NOT EXISTS task_completions_new (
        task_id TEXT NOT NULL,
        date TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (task_id, date)
    )`, (err) => {
        if (err) console.error('Error creating new table:', err.message);
    });

    // Copy data
    db.run(`INSERT INTO task_completions_new (task_id, date, created_at)
            SELECT CAST(task_id AS TEXT), date, created_at FROM task_completions`, (err) => {
        if (err) {
            // Ignore if task_completions doesn't exist or is empty
            console.error('Error copying data:', err.message);
        } else {
            console.log('Data copied successfully.');
        }
    });

    // Drop old and rename
    db.run(`DROP TABLE task_completions`);
    db.run(`ALTER TABLE task_completions_new RENAME TO task_completions`, (err) => {
        if (err) console.error('Error renaming table:', err.message);
        else console.log('Migration complete.');
    });
    
    db.run("PRAGMA foreign_keys = ON;");
});

db.close();
