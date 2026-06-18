import urllib.request
import json
import ssl

SUPABASE_URL = "https://ezvptctdfcddoybownml.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6dnB0Y3RkZmNkZG95Ym93bm1sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NDgzNzAsImV4cCI6MjA4NzMyNDM3MH0.u_t44hY_YCwwtbWCIrQKf7EnUZDrja1q4zUFT0MXNOs"

def make_request(url, method="GET", data=None):
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    if method == "PATCH":
        headers['Prefer'] = 'return=minimal'
        
    req = urllib.request.Request(url, headers=headers, method=method)
    
    if data:
        req.data = json.dumps(data).encode('utf-8')
        
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
        
    try:
        response = urllib.request.urlopen(req, context=context)
        if method == "GET":
            return json.loads(response.read().decode('utf-8'))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return None

def backup_and_clear():
    print("Fetching active tasks from Supabase...")
    url = f"{SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true&select=*"
    tasks = make_request(url)
    
    if tasks is None:
        return
        
    print(f"Found {len(tasks)} active tasks.")
    
    if not tasks:
        print("No active tasks to backup.")
        return
        
    filename = "tasks_backup.json"
    with open(filename, 'w') as f:
        json.dump(tasks, f, indent=2)
    print(f"Successfully backed up {len(tasks)} tasks to {filename}")
    
    print("Deactivating tasks...")
    patch_url = f"{SUPABASE_URL}/rest/v1/symphony_tasks_master?is_active=eq.true"
    result = make_request(patch_url, method="PATCH", data={"is_active": False})
    
    if result:
        print("Tasks successfully deactivated.")

if __name__ == "__main__":
    backup_and_clear()
