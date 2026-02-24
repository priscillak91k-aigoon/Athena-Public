import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Initialize Supabase client
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

# File paths
schedule_file = "life-dashboard/schedule_data.js"
history_file = "biological_history.md"
memory_file = "memory_bank.md"

def read_file_safe(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""

schedule_content = read_file_safe(schedule_file)
history_content = read_file_safe(history_file)
memory_content = read_file_safe(memory_file)

# Update database
data = {
    "schedule_payload": schedule_content,
    "history_payload": history_content,
    "memory_payload": memory_content
}

response = supabase.table("user_data").update(data).eq("id", 1).execute()
print("Migration complete. Response:", response)
