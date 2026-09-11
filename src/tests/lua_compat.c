#include "tolua++.h"
#include "lualib.h"
#include <stdio.h>
#include <stdlib.h>

static int collected;
static int collect_object(lua_State* L)
{
    ++collected;
    free(tolua_tousertype(L, 1, NULL));
    return 0;
}

int main(void)
{
    lua_State* L = luaL_newstate();
    int object = 42;
    int status;
    luaL_openlibs(L);
    tolua_open(L);
    tolua_usertype(L, "Base");
    tolua_usertype(L, "Derived");
    tolua_beginmodule(L, NULL);
    tolua_cclass(L, "Base", "Base", "", collect_object);
    tolua_cclass(L, "Derived", "Derived", "Base", collect_object);
    tolua_beginmodule(L, "Base");
    tolua_constant(L, "answer", 42);
    tolua_endmodule(L);
    tolua_endmodule(L);
    tolua_pushusertype(L, &object, "Derived");
    lua_setglobal(L, "obj");
    tolua_pushusertype(L, &object, "Derived");
    lua_setglobal(L, "same");
    tolua_pushusertype(L, malloc(sizeof(int)), "Derived");
    lua_setglobal(L, "owned");
    status = luaL_dostring(L,
        "assert(rawequal(obj, same)); assert(obj.answer == 42)\n"
        "assert(tolua.getpeer(obj) == nil)\n"
        "obj.note = 'peer'; assert(same.note == 'peer')\n"
        "tolua.setpeer(obj, {note = 'replacement'})\n"
        "assert(obj.note == 'replacement')\n"
        "tolua.setpeer(obj, nil); assert(obj.note == nil)\n"
        "assert(obj.answer == 42)\n"
        "assert(tolua.takeownership(owned))\n"
        "owned = nil; collectgarbage('collect'); collectgarbage('collect')\n");
    if (status) fprintf(stderr, "%s\n", lua_tostring(L, -1));
    lua_close(L);
    if (status || collected != 1) return 1;
    puts("peer, identity, inheritance and ownership checks passed");
    return 0;
}
