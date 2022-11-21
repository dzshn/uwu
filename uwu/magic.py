import abc
import ctypes
import dataclasses
import gc
import re
import sys
import types
from collections.abc import Container
from typing import Any, Literal, Union
from opcode import cmp_op, opmap as om, opname


class Match(abc.ABC):
    @abc.abstractmethod
    def matches(self, code, index) -> bool:
        ...


@dataclasses.dataclass
class Const(Match):
    value: Any

    def matches(self, code, index) -> bool:
        try:
            const = code.co_consts[code.co_code[index]]
            return type(const) is type(self.value) and self.value == const
        except IndexError:
            pass
        return False


@dataclasses.dataclass
class Name(Match):
    value: Union[str, re.Pattern]
    scope: Literal["cellvars", "freevars", "names", "varnames"] = "names"

    def matches(self, code, index) -> bool:
        try:
            name = getattr(code, "co_" + self.scope)[code.co_code[index]]
            if isinstance(self.value, str):
                return self.value == name
            return self.value.fullmatch(name)
        except IndexError:
            pass
        return False


@dataclasses.dataclass
class Op(Match):
    value: Union[str, re.Pattern]

    def matches(self, code, index) -> bool:
        op = opname[code.co_code[index]]
        if isinstance(self.value, str):
            return op == self.value
        return self.value.fullmatch(op)


class Always(Match):
    def matches(self, code, index) -> bool:
        return True


HEADER = [
    # import uwu.magic
    om["LOAD_CONST"],  Const(0),
    om["LOAD_CONST"],  Const(None),
    om["IMPORT_NAME"], Name("uwu.magic"),
    om["STORE_NAME"],  Name("uwu"),

    # haiiiiii <3
    om["LOAD_NAME"],   Name(re.compile(r"haii+")),
    om["LOAD_CONST"],  Const(3),
    om["COMPARE_OP"],  cmp_op.index("<"),
    om["POP_TOP"],     0,
]


def explod(message):
    print(message + ", explod", file=sys.stderr)
    ctypes.c_int.from_address(id(None)).value = 0
    # just in case you survive
    ctypes.c_int.from_address(1).value = 1


def match_code(code, index, query):
    bc = code.co_code
    for i, x in enumerate(query):
        if isinstance(x, int):
            if bc[index + i] != x:
                return None
        else:
            if not x.matches(code, index + i):
                return None
    return bc[index:index+len(query)]


if __name__ == "__main__":
    explod("no")

frame = sys._getframe(1)
while "importlib" in frame.f_code.co_filename:
    frame = frame.f_back

code = frame.f_code
bytecode = code.co_code

if not match_code(code, 0, HEADER):
    explod("ure a meanie")

i = len(HEADER)
new_code = bytearray([om["NOP"], 69] * (i // 2) + [om["POP_TOP"], 0])
while i < len(bytecode):
    if nop := match_code(code, i, [
        om["LOAD_NAME"], Name("o"),
        om["LOAD_NAME"], Name("w"),
        om["BINARY_MATRIX_MULTIPLY"], 0,
        om["LOAD_NAME"], Name("o"),
        om["BINARY_MATRIX_MULTIPLY"], 0,
    ]):
        i += len(nop)
        while not match_code(code, i, [
            om["CALL_FUNCTION"], Always()
        ]):
            i += 2
        i += 4
    elif push := match_code(code, i, [
        om["LOAD_NAME"], Name("o"),
        om["LOAD_NAME"], Name("w"),
        om["BINARY_XOR"], 0,
        om["LOAD_NAME"], Name("o"),
        om["BINARY_XOR"], 0,
        Op(re.compile(r"LOAD_.*")), Always(),
        om["COMPARE_OP"], cmp_op.index(">"),
        om["POP_TOP"], 0,
    ]):
        new_code.append(push[-6])
        new_code.append(push[-5])
        i += len(push)
    elif store := match_code(code, i, [
        Op(re.compile(r"LOAD_.*")), Always(),
        om["LOAD_NAME"], Name("o"),
        om["LOAD_NAME"], Name("w"),
        om["BINARY_XOR"], 0,
        om["LOAD_NAME"], Name("o"),
        om["BINARY_XOR"], 0,
        om["COMPARE_OP"], cmp_op.index("<"),
        om["POP_TOP"], 0,
    ]):
        new_code.append(om[opname[store[0]].replace("LOAD_", "STORE_")])
        new_code.append(store[1])
        i += len(store)
    elif arbitrary := match_code(code, i, [
        om["LOAD_NAME"], Name("o"),
        om["LOAD_NAME"], Name("w"),
        om["BINARY_FLOOR_DIVIDE"], 0,
        om["LOAD_NAME"], Name("o"),
        om["BINARY_FLOOR_DIVIDE"], 0,
    ]):
        i += len(arbitrary)
        j = i
        while not match_code(code, j, [
            om["BINARY_SUBSCR"], 0,
            om["POP_TOP"], 0,
        ]):
            if segment := match_code(code, j, [
                om["LOAD_NAME"], Always(),
                om["LOAD_NAME"], Always(),
                om["BINARY_MATRIX_MULTIPLY"], 0,
            ]):
                new_code.append(om[code.co_names[segment[1]]])
                new_code.append(segment[3])
                j += len(segment)
            elif segment := match_code(code, j, [
                om["LOAD_NAME"], Always(),
                om["LOAD_CONST"], Always(),
                om["BINARY_MATRIX_MULTIPLY"], 0,
            ]):
                op = om[code.co_names[segment[1]]]
                value = code.co_consts[segment[3]]
                if op == om["COMPARE_OP"]:
                    value = cmp_op.index(op)
                new_code.append(op)
                new_code.append(value)
                j += len(segment)
            elif segment := match_code(code, j, [
                om["LOAD_NAME"], Always(),
            ]):
                new_code.append(om[code.co_names[segment[1]]])
                new_code.append(0)
                j += len(segment)
            elif match_code(code, j, [om["BUILD_TUPLE"], Always()]):
                j += 2
            else:
                explod("invalid code")
        i = j + 4
    else:
        new_code.append(bytecode[i])
        new_code.append(bytecode[i+1])
        i += 2

new_code = bytes(new_code)

# we don't overwrite the reference count (immediate explosion otherwise)
start = object.__basicsize__

# overwrite our bytes object with the frame's. yeah, it's that shrimple
arr = ctypes.c_ubyte * (new_code.__sizeof__() - start)
arr.from_address(id(bytecode) + start)[:] = arr.from_address(id(new_code) + start)

