
"""
parse and generete a json file from single .cfg in Squad/Parts
"""
import re

AND = "|"

pattern = re.compile(
        r"category = (?P<category>\s+)" + AND +\
        r"cost = (?P<cost>\d+)" + AND +\
        r"mass = (?P<mass>\d+\.\d+)" + AND +\
        r"title = (?P<title>.+)" + AND +\
        r"maxThrust = (?P<maxThrust>\d+)" + AND +\
        r"minThrust = (?P<minThrust>\d+)" + AND +\
        r"(?P<atmosphereCurve>atmosphereCurve)")

keyvalues = re.compile(
        r"key = (?P<key>\d+) (?P<value>(\d+)(\.(\d+))?)"
        )

class Reader:
    def __init__(self):
        self.result = {}
        pass

    def read(self, lines):
        self.lines = lines
        for lno, line in enumerate(self.lines):
            m = pattern.search(line)
            if m:
                self.handle(lno, m)

    def handle(self, lno, m):
        name = m.lastgroup
        if name is not None:
            handler = getattr(self, "handle_"+name, None)
            if handler is not None:
                handler(name, lno, m)

    def do_int(self, name, m):
        self.result[name] = int(m.group(name))

    def do_float(self, name, m):
        self.result[name] = float(m.group(name))

    def do_str(self, name, m):
        self.result[name] = m.group(name)

    def handle_cost(self, name, lno, m):
        self.do_int(name, m)

    def handle_minThrust(self, name, lno, m):
        self.do_int(name, m)

    def handle_maxThrust(self, name, lno, m):
        self.do_int(name, m)

    def handle_mass(self, name, lno, m):
        self.do_float(name, m)

    def handle_title(self, name, lno, m):
        self.do_str(name, m)

    def handle_atmosphereCurve(self, name, lno, m):
        kv = {}
        for line in self.lines[lno+2:]:
            m = keyvalues.search(line)
            if m is None:
                break
            else:
                d = m.groupdict()
                kv[int(d["key"])] = float(d["value"])
        self.result[name] = kv

    

if __name__ == "__main__":
    import sys
    import json
    r = Reader()
    with open(sys.argv[1], encoding='utf-8-sig', mode='r') as f:
        r.read(f.readlines())
    print(json.dumps(r.result))


