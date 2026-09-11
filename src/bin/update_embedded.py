"""Refresh selected embedded generator chunks without bootstrapping tolua++."""
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[2]
names = set(sys.argv[1:])
if not names:
    raise SystemExit('usage: update_embedded.py compat.lua package.lua ...')
for filename in ('toluabind.c', 'toluabind_default.c'):
    path = root / 'src/bin' / filename
    source = path.read_bytes().decode()
    def update(match):
        name = match['name']
        if name not in names:
            return match[0]
        script = (root / 'src/bin/lua' / name).read_bytes().decode()
        data = script.encode()
        array = '\r\n'.join('    ' + ','.join(str(b) for b in data[i:i+20]) + ','
                            for i in range(0, len(data), 20))
        return match['head'] + '\r\n' + array + '\r\n   ' + match['tail']
    source, count = re.subn(
        r'(?P<head>static unsigned char B\[\] = \{).*?(?P<tail>\};\s*tolua_dobuffer\(.*?"tolua embedded: (?:lua/tolua\+\+/)?src/bin/lua/(?P<name>[^"/]+)"\);)',
        update, source, flags=re.S)
    if not count:
        raise SystemExit(f'No embedded scripts in {path}')
    path.write_bytes(source.encode())
