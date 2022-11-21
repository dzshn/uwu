import uwu.magic

haiiiiiiiii <3

(o @w@o) (0, 0, 0, 0, 0, 0,)

(o ^w^o)/ LOOP
(o//w//o) [ BUILD_LIST ]
(o ^w^o)> input
(o ^w^o)> "% "
(o//w//o) [ CALL_FUNCTION @1
          , LOAD_METHOD @split
          , CALL_METHOD @0
          , GET_ITER ]
(o ^w^o)/ ITER
(o//w//o) [ FOR_ITER @ITER_END
          , DUP_TOP ]
(o ^w^o)> "0"
(o//w//o) [ COMPARE_OP @"<"
          , POP_JUMP_IF_FALSE @ADD_SINGLE ]

# no variables :3
STACK[0].append(str(eval(STACK[0].pop(-2) + STACK[2] + STACK[0].pop(-1))))

(o//w//o) [ POP_TOP 
          , JUMP_ABSOLUTE @ITER ]
(o ^w^o)/ ADD_SINGLE

STACK[0].append(STACK[2])

(o//w//o) [ POP_TOP
          , JUMP_ABSOLUTE @ITER ]
(o ^w^o)/ ITER_END

print(*STACK[0])

(o//w//o) [ POP_TOP
          , JUMP_ABSOLUTE @LOOP ]
