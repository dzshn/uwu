# uwu

forbidden python bytecode magic :3

```py
import uwu.magic

haiiiiiiiii <3

(o ^w^o)> 0
(o ^w^o)/ LOOP

print(STACK[0])

(o ^w^o)> 1
(o//w//o) [ INPLACE_ADD ]

(o//w//o) [ DUP_TOP ]
(o ^w^o)> 10
(o//w//o) [ COMPARE_OP @"<"
          , POP_JUMP_IF_TRUE @LOOP ]
```

## Usage

Install the project: (only dependency is python 3.9~3.10)

```
$ pip install git+https://github.com/dzshn/uwu
# or `py -m pip` etc
```

The [examples](examples/) folder contains a few scripts showing off all features

## COOL STUFFz

-   push any variable or constant with `(o ^w^o)> thing`
-   store to any variable with `thing <(^w^ o)`
-   insert arbitrary bytecode with `(o//w//o) [ OPERATOR @ARGUMENT ]`
-   mark labels for jumping with `(o ^w^o)/ LABEL`
-   delete a variable with `thing <(o -w-o)` (or the top-of-stack (or the entire stack))
-   manually access the stack without popping a value with `STACK[x]`
    - insert `DUP_TOP` anywhere with `~STACK`
-   mix in as much normal code as you want! (subject to inexplicable segfaulting)
-   seriously, even using `if` or `while` or `for`

## TODO

- [ ] also patch functions
- [ ] more instructions for common opcodes
- [ ] maybe mnemonics for opcodes in `(o//w//o)`?
- [ ] also inject silly raw memory manipulation functions
- [x] fix jump targets
- [ ] use `EXTENDED_ARG` when necessary
- [ ] also detect `*_SUBSCR`

## wait, what

good question!

## how

instructions like `(o ^w^o)>` were deliberately picked in such a way that they
are valid syntax and easy to spot in the compiled bytecode. since everything is
perfectly valid syntax, all the magic can be done when `uwu.magic` is imported:
after finding the correct frame (i.e. the interpreter's state object), the
*compiled bytecode* is scanned, and new bytecode is generated according to
the specification, leaving "usual" code is left as-is. then, using `ctypes`,
the `bytes` object at the frame's memory is overwritten by our own and, when
execution is resumed (`uwu.magic` is finished), the interpreter will be running
the new bytecode, completely clueless about our changes
