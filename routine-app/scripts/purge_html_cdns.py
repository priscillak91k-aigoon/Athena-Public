import os
import glob
import re

public_dir = "c:/Users/prisc/Documents/Athena-Public/routine-app/public"
html_files = glob.glob(os.path.join(public_dir, "*.html"))

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove Google Fonts links
    content = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com".*?>\n?', '', content)
    content = re.sub(r'<link rel="preconnect" href="https://fonts\.gstatic\.com".*?>\n?', '', content)
    content = re.sub(r'<link href="https://fonts\.googleapis\.com/css2.*?>\n?', '', content)
    
    # Replace any specific font-families in CSS with system fonts
    content = re.sub(r"font-family:\s*['\"]?Outfit['\"]?[^;]*;", "font-family: system-ui, -apple-system, sans-serif;", content)
    content = re.sub(r"font-family:\s*['\"]?Inter['\"]?[^;]*;", "font-family: system-ui, -apple-system, sans-serif;", content)
    content = re.sub(r"font-family:\s*['\"]?VT323['\"]?[^;]*;", "font-family: ui-monospace, monospace;", content)
    content = re.sub(r"font-family:\s*['\"]?Cinzel['\"]?[^;]*;", "font-family: Georgia, serif;", content)

    # 2. Update JS libraries to point to local vendor/
    content = content.replace("https://cdn.jsdelivr.net/npm/marked/marked.min.js", "vendor/marked.min.js")
    content = content.replace("https://cdn.jsdelivr.net/npm/chart.js", "vendor/chart.js")
    content = content.replace("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js", "vendor/pdf.min.js")
    content = content.replace("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js", "vendor/pdf.worker.min.js")

    # 3. Purge Supabase from workshop.html
    if "workshop.html" in file_path:
        content = re.sub(r'<script src="https://cdn\.jsdelivr\.net/npm/@supabase/supabase-js@2"></script>\n?', '', content)
        content = re.sub(r"const SUPABASE_URL = 'https://ezvptctdfcddoybownml\.supabase\.co';\n?", '', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("HTML Air-Gap Purge Complete.")
