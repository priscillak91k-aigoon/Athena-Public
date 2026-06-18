const db = require('./database');
const fs = require('fs');
const path = require('path');

async function migrate() {
    console.log("Starting migration from tasks_backup.json to local SQLite...");
    
    try {
        const backupPath = path.join(__dirname, '..', 'tasks_backup.json');
        const rawData = fs.readFileSync(backupPath, 'utf-8');
        const tasks = JSON.parse(rawData);
        console.log(`Read ${tasks.length} tasks from tasks_backup.json.`);
        
        db.serialize(() => {
            const stmt = db.prepare(`INSERT INTO tasks (id, title, description, points, priority_color, time_target, is_active, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`);
            
            let count = 0;
            for (const task of tasks) {
                const tagsStr = task.tags ? JSON.stringify(task.tags) : null;
                const isActive = task.is_active ? 1 : 0;
                
                stmt.run([
                    task.id,
                    task.title,
                    task.description || null,
                    task.points || 0,
                    task.priority_color || 'GREEN',
                    task.time_target || null,
                    isActive,
                    tagsStr
                ], (err) => {
                    if (err) {
                        if (!err.message.includes("UNIQUE constraint failed")) {
                            console.error(`Error inserting task ${task.id}:`, err.message);
                        }
                    } else {
                        count++;
                    }
                });
            }
            
            stmt.finalize(() => {
                console.log(`Migration complete. Inserted ${count} new tasks.`);
                process.exit(0);
            });
        });
        
    } catch (error) {
        console.error("Migration error:", error);
        process.exit(1);
    }
}

// Give the database a moment to initialize tables before migrating
setTimeout(migrate, 1000);
