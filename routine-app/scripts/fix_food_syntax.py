import re
import sys

file_path = "symphony-app.js"

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(1830, 1920):
    if i < len(lines):
        lines[i] = lines[i].replace(r"\'", "'")

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Syntax fixed")
