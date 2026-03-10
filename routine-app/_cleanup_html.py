lines = open('index.html', encoding='utf-8').readlines()
# Find stale old section start (the ghost div.section-header after new planner section closes)
stale_start = None
for i, l in enumerate(lines):
    if i > 640 and '<div class="section-header">' in l and i < 720:
        stale_start = i
        break

# Find dog section
dog_line = None
for i, l in enumerate(lines):
    if 'id="dog"' in l:
        dog_line = i
        break

print(f'Stale at line {stale_start+1}, dog at line {dog_line+1}')
# Remove stale (from stale_start to dog_line)
clean = lines[:stale_start] + ['\n'] + lines[dog_line:]
open('index.html', 'w', encoding='utf-8').writelines(clean)
print('Done. Lines removed:', dog_line - stale_start)
print('Total lines now:', len(clean))
