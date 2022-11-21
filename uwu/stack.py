import ctypes
import sys
from collections.abc import Sequence


class Stack(Sequence):
    def __init__(self, frame):
        self.address = id(frame) + ctypes.sizeof(ctypes.c_void_p) * 44
        self.size = frame.f_code.co_stacksize

    def __getitem__(self, key: int) -> object:
        if isinstance(key, int):
            if key < 0:
                key += self.size
            return ctypes.py_object.from_address(
                self.address + key * ctypes.sizeof(ctypes.c_void_p)
            ).value
        if isinstance(key, slice):
            seq = []
            for i in range(*key.indices(self.size)):
                seq.append(
                    ctypes.py_object.from_address(
                        self.address + i * ctypes.sizeof(ctypes.c_void_p)
                    ).value
                )
            return seq
        return NotImplemented

    def __len__(self) -> int:
        return self.size

