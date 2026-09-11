/* Private Lua API compatibility. Peer tables belong to userdata, not _ENV. */
#ifndef TOLUA_COMPAT_H
#define TOLUA_COMPAT_H

#if defined(LUA_VERSION_NUM) && LUA_VERSION_NUM >= 504
#define tolua_getpeer_table(L,i) lua_getiuservalue(L,i,1)
#define tolua_setpeer_table(L,i) lua_setiuservalue(L,i,1)
#elif defined(LUA_VERSION_NUM) && LUA_VERSION_NUM >= 502
#define tolua_getpeer_table(L,i) lua_getuservalue(L,i)
#define tolua_setpeer_table(L,i) lua_setuservalue(L,i)
#else
#define tolua_getpeer_table(L,i) lua_getfenv(L,i)
#define tolua_setpeer_table(L,i) lua_setfenv(L,i)
#endif

#if !defined(LUA_VERSION_NUM) || LUA_VERSION_NUM < 502
#define lua_pushglobaltable(L) lua_pushvalue(L,LUA_GLOBALSINDEX)
#endif
#endif
