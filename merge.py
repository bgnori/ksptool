import json
import glob

import sys

parts = json.loads(sys.stdin.read())
for path in glob.iglob("Engine/*.json"):
    with open(path, "r") as g:
        codename = path[7:-5]
        engine = json.loads(g.read())
        parts[codename] = engine

print(json.dumps(parts))
