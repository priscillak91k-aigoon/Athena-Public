const fs = require('fs');

const SUPABASE_URL = "https://ezvptctdfcddoybownml.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6dnB0Y3RkZmNkZG95Ym93bm1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NDgzNzAsImV4cCI6MjA4NzMyNDM3MH0.u_t44hY_YCwwtbWCIrQKf7EnUZDrja1q4zUFT0MXNOs";

async function backupAndClear() {
    try {
        console.log("Fetching active tasks from Supabase...");
        const getRes = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true&select=*`, {
            method: 'GET',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                'Content-Type': 'application/json'
            }
        });

        if (!getRes.ok) throw new Error("Failed to fetch tasks: " + getRes.statusText);

        const tasks = await getRes.json();
        console.log(`Found ${tasks.length} active tasks.`);

        if (tasks.length === 0) {
            console.log("No active tasks to backup.");
            return;
        }

        // Save backup
        const backupFile = 'tasks_backup.json';
        fs.writeFileSync(backupFile, JSON.stringify(tasks, null, 2));
        console.log(`Successfully backed up ${tasks.length} tasks to ${backupFile}`);

        // Deactivate tasks
        console.log("Deactivating tasks...");
        const patchRes = await fetch(`${SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true`, {
            method: 'PATCH',
            headers: {
                'apikey': SUPABASE_ANON_KEY,
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            },
            body: JSON.stringify({ is_active: false })
        });

        if (!patchRes.ok) throw new Error("Failed to deactivate tasks: " + patchRes.statusText);

        console.log("Tasks successfully deactivated.");
    } catch (error) {
        console.error("Error:", error.message);
    }
}

backupAndClear();
