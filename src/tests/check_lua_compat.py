"""Build and test with GCC and an unpacked Lua source tree (5.1 or 5.5).

Usage: python check_lua_compat.py LUA_SRC OUTPUT_DIR
Run the resulting toluapp executable on application packages separately.
"""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
lua = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
out.mkdir(parents=True, exist_ok=True)
sources = [str(p) for p in lua.glob('*.c') if p.name not in ('lua.c', 'luac.c', 'print.c')]
sources += [str(p) for p in (root / 'src/lib').glob('*.c')]
base = ['gcc', '-O0', '-g', '-DLUA_USE_APICHECK', '-I' + str(lua),
        '-I' + str(root / 'include'), '-I' + str(root / 'src/lib')]
for name, files in [('toluapp', ['src/bin/tolua.c', 'src/bin/toluabind.c']),
                    ('lua_compat', ['src/tests/lua_compat.c'])]:
    subprocess.run(base + sources + [str(root / f) for f in files]
                   + ['-lm', '-o', str(out / (name + '.exe'))], check=True)
subprocess.run([str(out / 'lua_compat.exe')], check=True)

# Exercise template expansion (-E), then compile and run the generated binding.
(out / 'fixture.pkg').write_text('int $(NAME)(int a, int b);\n')
(out / 'fixture.h').write_text('int add(int a, int b);\n')
subprocess.run([str(out / 'toluapp.exe'), '-E', 'NAME=add', '-n', 'fixture',
                '-o', str(out / 'fixture.c'), str(out / 'fixture.pkg')], check=True)
assert 'tolua_function' in (out / 'fixture.c').read_text()
(out / 'run_fixture.c').write_text('''
#include "tolua++.h"
#include "lualib.h"
#include <stdio.h>
int add(int a, int b) { return a + b; }
int tolua_fixture_open(lua_State* L);
int main(void) {
    lua_State* L = luaL_newstate();
    int result;
    luaL_openlibs(L);
    tolua_fixture_open(L);
    result = luaL_dostring(L, "assert(add(19,23) == 42)");
    if (result) fprintf(stderr, "%s\\n", lua_tostring(L, -1));
    lua_close(L);
    return result != 0;
}
''')
subprocess.run(base + sources + ['-include', str(out / 'fixture.h'),
                str(out / 'fixture.c'), str(out / 'run_fixture.c'), '-lm',
                '-o', str(out / 'fixture.exe')], check=True)
subprocess.run([str(out / 'fixture.exe')], check=True)
print('template expansion, generated binding compilation and execution passed')
failure = subprocess.run([str(out / 'toluapp.exe'), '-n', 'missing',
                          str(out / 'does-not-exist.pkg')], capture_output=True)
assert failure.returncode != 0, 'generator must report input errors to the build'
