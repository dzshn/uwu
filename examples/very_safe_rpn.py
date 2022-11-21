import uwu.magic

haiiiiiiiii <3

(o @w@o) (0, 0, 0, 0, 0, 0,)

(o ^w^o)/ LOOP  # <--- label
(o//w//o) [ BUILD_LIST ]
stack <(o^w^ o)
(o ^w^o)> input
(o ^w^o)> "% "
(o//w//o) [ CALL_FUNCTION @1
          , LOAD_METHOD @split
          , CALL_METHOD @0
          , GET_ITER ]
(o ^w^o)/ ITER
(o//w//o) [ FOR_ITER @ITER_END
          , DUP_TOP ]
x <(o^w^ o)
(o ^w^o)> "0"
(o//w//o) [ COMPARE_OP @"<"
          , POP_JUMP_IF_FALSE @ADD_SINGLE ]

stack.append(str(eval(stack.pop(-2) + x + stack.pop(-1))))

(o//w//o) [ JUMP_ABSOLUTE @ITER ]
(o ^w^o)/ ADD_SINGLE

stack.append(x)

(o//w//o) [ JUMP_ABSOLUTE @ITER ]
(o ^w^o)/ ITER_END

print(*stack)

(o//w//o) [ JUMP_ABSOLUTE @LOOP ]
