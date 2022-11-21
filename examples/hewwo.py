import uwu.magic

haiiii <3  # required header

(o @w@o) (0, 0, 0, 0, 0, 0)  # NOP to gaslight python to give a larger stack

(o ^w^o)> 0   # inserts appropriate LOAD_CONST/LOAD_NAME/etc
(o ^w^o)> None
(o//w//o) [ IMPORT_NAME @ctypes ]  # insert any bytecode
ctypes <(o^w^ o)  # (o ^w^o)> but STORE_NAME/etc

(o ^w^o)> ctypes
(o//w//o) [ LOAD_ATTR @cdll ]
(o ^w^o)> "libc.so.6"
(o//w//o) [ BINARY_SUBSCR
          , LOAD_ATTR @syscall ]
(o ^w^o)> 1
(o ^w^o)> 1
(o ^w^o)> ctypes
(o//w//o) [ LOAD_ATTR @c_char_p ]
(o ^w^o)> b"hewwo :3\n"
string <(o^w^ o)
(o ^w^o)> string
(o//w//o) [ CALL_FUNCTION @1 ]
(o ^w^o)> len
(o ^w^o)> string
(o//w//o) [ CALL_FUNCTION @1 ]
(o//w//o) [ CALL_FUNCTION @4 ]
