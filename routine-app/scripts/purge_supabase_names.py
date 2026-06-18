import re

file_path = "c:/Users/prisc/Documents/Athena-Public/routine-app/public/symphony-app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace function names
content = content.replace("fetchSupabaseInventory", "fetchLocalAPIInventory")
content = content.replace("fetchSupabaseData", "fetchLocalAPIData")

# Replace variable names
content = content.replace("supabaseData", "apiData")

# Replace strings inside console warnings/infos
content = re.sub(r'Supabase unavailable', 'Backend unavailable', content, flags=re.IGNORECASE)
content = re.sub(r'Supabase empty', 'Backend empty', content, flags=re.IGNORECASE)
content = re.sub(r'fetch supps from Supabase', 'fetch supps from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'save new supp to Supabase', 'save new supp to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'update stock in Supabase', 'update stock in Backend', content, flags=re.IGNORECASE)
content = re.sub(r'save item to Supabase', 'save item to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'save subtask to Supabase', 'save subtask to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'mark done in Supabase', 'mark done in Backend', content, flags=re.IGNORECASE)
content = re.sub(r'reopen in Supabase', 'reopen in Backend', content, flags=re.IGNORECASE)
content = re.sub(r'delete event from Supabase', 'delete event from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'save event to Supabase', 'save event to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'fetch failed, using localStorage', 'fetch failed, using localStorage', content, flags=re.IGNORECASE)
content = re.sub(r'delete expense from Supabase', 'delete expense from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'save expense to Supabase', 'save expense to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'from Supabase', 'from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'to Supabase', 'to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'Fetch events from Supabase', 'Fetch events from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'Fetch from Supabase', 'Fetch from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'Delete from Supabase', 'Delete from Backend', content, flags=re.IGNORECASE)
content = re.sub(r'Persist to Supabase', 'Persist to Backend', content, flags=re.IGNORECASE)
content = re.sub(r'Supabase has data', 'Backend has data', content, flags=re.IGNORECASE)
content = re.sub(r'Supabase is empty', 'Backend is empty', content, flags=re.IGNORECASE)
content = re.sub(r'Supabase fetch failed', 'Backend fetch failed', content, flags=re.IGNORECASE)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Purge Complete.")
