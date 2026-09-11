# Lua 5.5 port

The runtime and generator retain their public tolua++ API and package format.
Lua 5.1 remains supported. Lua 5.2–5.4 have compatibility branches but have not
been tested in this change.

Changes:

- Store userdata peer tables in uservalue slot 1 on Lua 5.4+, in the uservalue
  on 5.2/5.3, and in the userdata environment on 5.1. Keep the existing no-peer
  sentinel and object identity cache.
- Use `lua_pushglobaltable` on modern Lua. Do not emulate `LUA_GLOBALSINDEX`.
- Ignore table finalization in the userdata collector: Lua 5.2+ can finalize
  class tables sharing the same metatables as instances.
- Restore the generator's legacy library helpers locally to its own state;
  use explicit vararg tables and `load(..., env)` for package templates.
- Fix invalid Lua string escapes, refresh both embedded generator copies,
  and propagate embedded-script errors. The executable protects generation,
  returns a failing exit code on errors, and closes its Lua state.
- Extend CMake library suffix discovery and Lua 5.5 version detection.

## Reproduce validation

With Python 3 and GCC on PATH, use an unpacked official Lua source distribution:

```text
python src/tests/check_lua_compat.py /path/to/lua-5.5.1/src /path/to/build55
python src/tests/check_lua_compat.py /path/to/lua-5.1.5/src /path/to/build51
```

Tests enable Lua API assertions and cover userdata identity, peer creation and
replacement/reset, inherited lookup, ownership and collection (including state
close), package template expansion with `-E`, compilation and execution of a
generated C binding, and failure reporting. This is a standalone GCC build;
it does not validate every platform's CMake/toolchain integration.

After editing embedded Lua sources, refresh the corresponding chunks:

```text
python src/bin/update_embedded.py compat.lua package.lua
```

The checked-in byte arrays account for most of the textual diff. The script
updates only named chunks and needs no preexisting tolua++ executable.
