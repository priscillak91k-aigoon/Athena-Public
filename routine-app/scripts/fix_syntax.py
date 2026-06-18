import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(r"\'", "'")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Syntax fixed")
