import urllib.request
import urllib.error
import time

mods = [928547,953108,1315440,928445,928424,929690,929737,931750,938621,936551,928502,928621,935639,934572,928574,961601,949521,931085,936457,940989,934376,932145,928925,928708,1246872,929110,929838,928916,945535,933354,929288,929237,929532,929388,929788,928641,928482,928588,928731,928628,930109,932066,933804,933011,1395262,1293541,929146]
bad_mods = []

for mod in mods:
    url = f"https://www.curseforge.com/projects/{mod}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        # Even if it succeeds, sometimes CF redirects to a 404 page, but normally returns 404 status.
        if response.getcode() != 200:
            bad_mods.append(mod)
    except urllib.error.HTTPError as e:
        if e.code == 404 or e.code == 403:
            bad_mods.append(mod)
            print(f"Mod {mod} failed with {e.code}")
    except Exception as e:
        bad_mods.append(mod)
    time.sleep(0.5)

print("Bad Mods:", bad_mods)
