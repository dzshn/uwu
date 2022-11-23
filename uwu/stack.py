import ctypes
import types
from collections.abc import Sequence
from typing import Union

svoid_p = ctypes.sizeof(ctypes.c_void_p)


class Stack(Sequence):
    def __init__(self, frame: types.FrameType):
        self.address = id(frame) + svoid_p * 44
        self.size = frame.f_code.co_stacksize

    def __getitem__(self, key: Union[int, slice]) -> object:
        if isinstance(key, int):
            if key < 0:
                key += self.size
            return ctypes.py_object.from_address(self.address + key * svoid_p).value
        if isinstance(key, slice):
            seq = []
            for i in range(*key.indices(self.size)):
                seq.append(
                    ctypes.py_object.from_address(self.address + i * svoid_p).value
                )
            return seq
        return NotImplemented

    def __setitem__(self, key: int, value: object) -> None:
        if not isinstance(key, int):
            return NotImplemented

        ctypes.c_void_p.from_address(self.address + key * svoid_p).value = id(value)

    def __delitem__(self, key: int) -> None:
        if not isinstance(key, int):
            return NotImplemented

        ctypes.c_void_p.from_address(self.address + key * svoid_p).value = 0

    def __len__(self) -> int:
        return self.size

    def __invert__(self):
        i = 0
        while i < self.size:
            if ctypes.c_void_p.from_address(self.address + i * svoid_p).value is None:
                break
            i += 1
        return ctypes.py_object.from_address(self.address + (i - 1) * svoid_p).value
