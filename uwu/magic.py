import abc
import ctypes
import dataclasses
import re
import opcode
import sys
import types
from typing import Any, Literal, Union

from uwu.stack import Stack


class Match(abc.ABC):
    @abc.abstractmethod
    def matches(self, code: types.CodeType, index: int) -> bool:
        ...


@dataclasses.dataclass
class Const(Match):
    value: Any

    def matches(self, code: types.CodeType, index: int) -> bool:
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

    def matches(self, code: types.CodeType, index: int) -> bool:
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

    def __post_init__(self):
        self._re = re.compile(re.escape(self.value).replace("\\*", ".*"))

    def matches(self, code: types.CodeType, index: int) -> bool:
        op = opcode.opname[code.co_code[index]]
        return self._re.fullmatch(op)


class Always(Match):
    def matches(self, code: types.CodeType, index: int) -> bool:
        return True


def overwrite(victim: object, value: object):
    # don't overwrite the reference count (immediate explosion otherwise)
    start = ctypes.sizeof(ctypes.c_int)
    arr = ctypes.c_ubyte * (value.__sizeof__() - start)
    arr.from_address(id(victim) + start)[:] = arr.from_address(id(value) + start)


def explod(message: str):
    print(message + ", explod", file=sys.stderr)
    ctypes.c_int.from_address(id(None)).value = 0
    # just in case you survive
    ctypes.c_int.from_address(1).value = 1


def match_code(code: types.CodeType, index: int, query: list[Match]):
    bc = code.co_code
    for i, x in enumerate(query):
        if isinstance(x, int):
            if bc[index + i] != x:
                return None
        else:
            if not x.matches(code, index + i):
                return None
    return bc[index:index+len(query)]


def insanity(code: types.CodeType) -> bytes:
    bytecode = code.co_code
    i = 0
    new_code = bytearray()
    labels = {}
    jumps = {}
    broken_targets = {}
    while i < len(bytecode):
        if nop := match_code(code, i, [
            LOAD_NAME, Name("o"),
            LOAD_NAME, Name("w"),
            BINARY_MATRIX_MULTIPLY, 0,
            LOAD_NAME, Name("o"),
            BINARY_MATRIX_MULTIPLY, 0,
        ]):
            i += len(nop)
            while not match_code(code, i, [
                CALL_FUNCTION, Always()
            ]):
                i += 2
            i += 4
        elif haiii := match_code(code, i, [
            LOAD_NAME, Name(re.compile("haii+")),
            LOAD_CONST, Const(3),
            COMPARE_OP, opcode.cmp_op.index("<"),
            POP_TOP, 0,
        ]):
            i += len(haiii)
        elif push := match_code(code, i, [
            LOAD_NAME, Name("o"),
            LOAD_NAME, Name("w"),
            BINARY_XOR, 0,
            LOAD_NAME, Name("o"),
            BINARY_XOR, 0,
            Op("LOAD_*"), Always(),
            COMPARE_OP, opcode.cmp_op.index(">"),
            POP_TOP, 0,
        ]):
            new_code.append(push[-6])
            new_code.append(push[-5])
            i += len(push)
        elif store := match_code(code, i, [
            Op("LOAD_*"), Always(),
            LOAD_NAME, Name("o"),
            LOAD_NAME, Name("w"),
            BINARY_XOR, 0,
            LOAD_NAME, Name("o"),
            BINARY_XOR, 0,
            COMPARE_OP, opcode.cmp_op.index("<"),
            POP_TOP, 0,
        ]):
            new_code.append(opcode.opmap[opcode.opname[store[0]].replace("LOAD_", "STORE_")])
            new_code.append(store[1])
            i += len(store)
        elif arbitrary := match_code(code, i, [
            LOAD_NAME, Name("o"),
            LOAD_NAME, Name("w"),
            BINARY_FLOOR_DIVIDE, 0,
            LOAD_NAME, Name("o"),
            BINARY_FLOOR_DIVIDE, 0,
        ]):
            i += len(arbitrary)
            j = i
            while not match_code(code, j, [
                BINARY_SUBSCR, 0,
                POP_TOP, 0,
            ]):
                if segment := match_code(code, j, [
                    LOAD_NAME, Always(),
                    LOAD_NAME, Always(),
                    BINARY_MATRIX_MULTIPLY, 0,
                ]):
                    op = opcode.opmap[code.co_names[segment[1]]]
                    value = segment[3]
                    if op in opcode.hasjabs or op in opcode.hasjrel:
                        label = code.co_names[value]
                        if (value := labels.get(label)) is None:
                            value = 0
                            jumps.setdefault(label, set())
                            jumps[label].add(len(new_code))
                    new_code.append(op)
                    new_code.append(value)
                    j += len(segment)
                elif segment := match_code(code, j, [
                    LOAD_NAME, Always(),
                    LOAD_CONST, Always(),
                    BINARY_MATRIX_MULTIPLY, 0,
                ]):
                    op = opcode.opmap[code.co_names[segment[1]]]
                    value = code.co_consts[segment[3]]
                    if op == COMPARE_OP:
                        value = opcode.cmp_op.index(value)
                    new_code.append(op)
                    new_code.append(value)
                    j += len(segment)
                elif segment := match_code(code, j, [
                    LOAD_NAME, Always(),
                ]):
                    new_code.append(opcode.opmap[code.co_names[segment[1]]])
                    new_code.append(0)
                    j += len(segment)
                elif match_code(code, j, [BUILD_TUPLE, Always()]):
                    j += 2
                else:
                    explod("invalid code")
            i = j + 4
        elif label := match_code(code, i, [
            LOAD_NAME, Name("o"),
            LOAD_NAME, Name("w"),
            BINARY_XOR, 0,
            LOAD_NAME, Name("o"),
            BINARY_XOR, 0,
            LOAD_NAME, Always(),
            BINARY_TRUE_DIVIDE, 0,
            POP_TOP, 0,
        ]):
            target = len(new_code) // 2
            labels[code.co_names[label[-5]]] = target
            for x in jumps.get(code.co_names[label[-5]], set()):
                if new_code[x] in opcode.hasjrel:
                    new_code[x + 1] = target - x // 2 - 1
                else:
                    new_code[x + 1] = target
            i += len(label)
        else:
            op = bytecode[i]
            arg = bytecode[i+1]
            for x in broken_targets.get(i, set()):
                if new_code[x] in opcode.hasjrel:
                    new_code[x] = len(new_code) - x
                else:
                    new_code[x + 1] -= (i - len(new_code)) // 2
            if op in opcode.hasjabs or op in opcode.hasjrel:
                target = arg * 2
                if op in opcode.hasjrel:
                    target += i + 2
                broken_targets.setdefault(target, set())
                broken_targets[target].add(len(new_code))
            new_code.append(op)
            new_code.append(arg)
            i += 2

    return bytes(new_code)


if __name__ == "__main__":
    explod("no")

locals().update(opcode.opmap)  # 🚎

frame = sys._getframe(1)
while "importlib" in frame.f_code.co_filename:
    frame = frame.f_back

if not match_code(frame.f_code, 0, [
    LOAD_CONST, Const(0),
    LOAD_CONST, Const(None),
    IMPORT_NAME, Name("uwu.magic"),
    STORE_NAME, Name("uwu"),
    LOAD_NAME, Name(re.compile(r"haii+")),
    LOAD_CONST, Const(3),
    COMPARE_OP, opcode.cmp_op.index("<"),
    POP_TOP, 0,
]):
    explod("ure a meanie")

# nomz *eats ur header*
new_code = bytes([NOP, 69] * 3 + [POP_TOP, 0]) + insanity(frame.f_code)[8:]

overwrite(frame.f_code.co_code, new_code)
overwrite(frame.f_code.co_linetable, bytes())

frame.f_locals["STACK"] = Stack(frame)
