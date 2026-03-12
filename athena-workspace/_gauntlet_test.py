import requests, json

BASE = 'http://127.0.0.1:7337'
KEY = 'athena-local-dev'
HDR = {'X-API-Key': KEY, 'Content-Type': 'application/json'}
RESULTS = []

def check(name, condition, detail=''):
    status = 'PASS' if condition else 'FAIL'
    RESULTS.append((status, name, detail))
    print(f'[{status}] {name}' + (f' -- {detail}' if detail else ''))

# 1. Health (no auth needed)
try:
    r = requests.get(f'{BASE}/health', timeout=5)
    h = r.json()
    check('Health endpoint', r.status_code == 200)
    check('Health status ok', h.get('status') == 'ok')
    check('Uptime > 0', h.get('uptime_seconds', 0) > 0, str(h.get('uptime_seconds')) + 's')
    check('Workspace root', 'Athena-Public' in h.get('workspace_root', ''))
except Exception as e:
    check('Health endpoint', False, str(e))

# 2. File tree
try:
    r = requests.get(f'{BASE}/api/tree', headers=HDR, timeout=5)
    check('File tree loads', r.status_code == 200)
    children = r.json().get('tree', {}).get('children', [])
    check('Tree has children', len(children) > 0, f'{len(children)} items')
except Exception as e:
    check('File tree', False, str(e))

# 3. Read existing file
try:
    r = requests.get(f'{BASE}/api/file/.context/last_thread.md', headers=HDR, timeout=5)
    check('Read file', r.status_code == 200)
    content = r.json().get('content', '')
    check('File has content', len(content) > 10, f'{len(content)} chars')
except Exception as e:
    check('Read file', False, str(e))

# 4. Write test file
TEST_PATH = 'athena-workspace/_test_gauntlet.md'
TEST_CONTENT = '# Gauntlet Test\nWritten by automated test suite.'
try:
    r = requests.post(f'{BASE}/api/file/{TEST_PATH}', headers=HDR,
                      data=json.dumps({'content': TEST_CONTENT}), timeout=5)
    check('Write file', r.status_code == 200)
except Exception as e:
    check('Write file', False, str(e))

# 5. Read back
try:
    r = requests.get(f'{BASE}/api/file/{TEST_PATH}', headers=HDR, timeout=5)
    check('Read-back written file', r.status_code == 200)
    check('Content matches', r.json().get('content') == TEST_CONTENT)
except Exception as e:
    check('Read-back', False, str(e))

# 6. Execute command
try:
    r = requests.post(f'{BASE}/api/exec', headers=HDR,
                      data=json.dumps({'command': 'echo gauntlet_ok'}), timeout=10)
    check('Exec command', r.status_code == 200)
    res = r.json()
    check('Exec stdout', 'gauntlet_ok' in res.get('stdout', ''), res.get('stdout','').strip())
    check('Exec exit 0', res.get('returncode') == 0)
except Exception as e:
    check('Exec', False, str(e))

# 7. Task queue
try:
    r = requests.post(f'{BASE}/api/task', headers=HDR,
                      data=json.dumps({'task': 'gauntlet test task', 'author': 'gauntlet'}), timeout=5)
    check('Task submit', r.status_code == 200)
    r2 = requests.get(f'{BASE}/api/tasks', headers=HDR, timeout=5)
    tasks = r2.json().get('tasks', [])
    check('Task in queue', any(t['task'] == 'gauntlet test task' for t in tasks), f'{len(tasks)} total')
except Exception as e:
    check('Task queue', False, str(e))

# 8. Wrong API key = 403
try:
    r = requests.get(f'{BASE}/api/tree', headers={'X-API-Key': 'wrongkey'}, timeout=5)
    check('Auth blocks wrong key', r.status_code == 403)
except Exception as e:
    check('Auth wrong key', False, str(e))

# 9. Path traversal = blocked
try:
    r = requests.get(f'{BASE}/api/file/../../etc/passwd', headers=HDR, timeout=5)
    check('Path traversal blocked', r.status_code in (403, 404))
except Exception as e:
    check('Path traversal blocked', False, str(e))

# 10. Delete test file
try:
    r = requests.delete(f'{BASE}/api/file/{TEST_PATH}', headers=HDR, timeout=5)
    check('Delete file', r.status_code == 200)
    r2 = requests.get(f'{BASE}/api/file/{TEST_PATH}', headers=HDR, timeout=5)
    check('File gone after delete', r2.status_code == 404)
except Exception as e:
    check('Delete', False, str(e))

# Summary
passed = sum(1 for s,_,_ in RESULTS if s == 'PASS')
failed = sum(1 for s,_,_ in RESULTS if s == 'FAIL')
print(f'\n=== GAUNTLET: {passed} PASS / {failed} FAIL / {len(RESULTS)} total ===')
