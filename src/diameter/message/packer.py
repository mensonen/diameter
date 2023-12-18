"""
Copied and updated from python 3.12 stdlib's xdrlib.

As xdrlib will be removed in Python 3.13, this module preserves the Packer and
Unpacker functionality from it, while making slight upgrades.
"""
from __future__ import annotations

import struct

from io import BytesIO
from functools import wraps
from typing import Any, Callable, TypeVar


class Error(Exception):
    pass


class ConversionError(Error):
    pass


_CT = TypeVar("_CT")


def raise_conversion_error(function: Callable[..., _CT]) -> Callable[..., _CT]:
    """Wrap any raised `struct.errors` in a ConversionError."""
    @wraps(function)
    def result(self: Packer | Unpacker, *args: Any, **kwargs: Any):
        try:
            return function(self, *args, **kwargs)
        except (EOFError, TypeError, ValueError, struct.error) as e:
            raise ConversionError(e.args[0]) from None
    return result


class Packer:
    """Pack various data representations into a buffer."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.__buf = BytesIO()

    def get_buffer(self) -> bytes:
        return self.__buf.getvalue()

    @raise_conversion_error
    def pack_uint(self, x: int):
        self.__buf.write(struct.pack('>L', x))

    @raise_conversion_error
    def pack_int(self, x: int):
        self.__buf.write(struct.pack('>l', x))

    pack_enum = pack_int

    def pack_bool(self, x: bool):
        if x:
            self.__buf.write(b'\0\0\0\1')
        else:
            self.__buf.write(b'\0\0\0\0')

    def pack_uhyper(self, x: int):
        try:
            self.pack_uint(x >> 32 & 0xffffffff)
        except (TypeError, struct.error) as e:
            raise ConversionError(e.args[0]) from None
        try:
            self.pack_uint(x & 0xffffffff)
        except (TypeError, struct.error) as e:
            raise ConversionError(e.args[0]) from None

    pack_hyper = pack_uhyper

    @raise_conversion_error
    def pack_float(self, x: float):
        self.__buf.write(struct.pack('>f', x))

    @raise_conversion_error
    def pack_double(self, x: float):
        self.__buf.write(struct.pack('>d', x))

    @raise_conversion_error
    def pack_fstring(self, n: int, s: bytes):
        if n < 0:
            raise ValueError("fstring size must be nonnegative")
        data = s[:n]
        n = ((n+3)//4)*4
        data = data + (n - len(data)) * b'\0'
        self.__buf.write(data)

    pack_fopaque = pack_fstring

    def pack_string(self, s: bytes):
        n = len(s)
        self.pack_uint(n)
        self.pack_fstring(n, s)

    pack_opaque = pack_string
    pack_bytes = pack_string

    def pack_list(self, item_list, pack_item):
        for item in item_list:
            self.pack_uint(1)
            pack_item(item)
        self.pack_uint(0)

    @raise_conversion_error
    def pack_farray(self, n, item_list, pack_item):
        if len(item_list) != n:
            raise ValueError("wrong array size")
        for item in item_list:
            pack_item(item)

    def pack_array(self, item_list, pack_item):
        n = len(item_list)
        self.pack_uint(n)
        self.pack_farray(n, item_list, pack_item)


class Unpacker:
    """Unpacks various data representations from the given buffer."""
    def __init__(self, data: bytes):
        self.reset(data)

    def reset(self, data: bytes):
        self.__buf: bytes = data
        self.__pos: int = 0

    def get_position(self) -> int:
        return self.__pos

    def set_position(self, position: int):
        self.__pos = position

    def get_buffer(self) -> bytes:
        return self.__buf

    def done(self):
        if self.__pos < len(self.__buf):
            raise Error("unextracted data remains")

    def is_done(self):
        return self.__pos >= len(self.__buf)

    @raise_conversion_error
    def unpack_char(self) -> int:
        i = self.__pos
        self.__pos = j = i+1
        data = self.__buf[i:j]
        if len(data) < 1:
            raise EOFError("Not enough bytes left to unpack")
        return struct.unpack(">B", data)[0]

    @raise_conversion_error
    def unpack_uint(self) -> int:
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError("Not enough bytes left to unpack")
        return struct.unpack(">L", data)[0]

    @raise_conversion_error
    def unpack_int(self) -> int:
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError("Not enough bytes left to unpack")
        return struct.unpack('>l', data)[0]

    unpack_enum = unpack_int

    def unpack_bool(self) -> bool:
        return bool(self.unpack_int())

    def unpack_uhyper(self) -> int:
        hi = self.unpack_uint()
        lo = self.unpack_uint()
        return int(hi) << 32 | lo

    def unpack_hyper(self) -> int:
        x = self.unpack_uhyper()
        if x >= 0x8000000000000000:
            x = x - 0x10000000000000000
        return x

    @raise_conversion_error
    def unpack_float(self) -> float:
        i = self.__pos
        self.__pos = j = i+4
        data = self.__buf[i:j]
        if len(data) < 4:
            raise EOFError("Not enough bytes left to unpack")
        return struct.unpack(">f", data)[0]

    @raise_conversion_error
    def unpack_double(self) -> float:
        i = self.__pos
        self.__pos = j = i+8
        data = self.__buf[i:j]
        if len(data) < 8:
            raise EOFError("Not enough bytes left to unpack")
        return struct.unpack(">d", data)[0]

    @raise_conversion_error
    def unpack_fstring(self, n: int) -> bytes:
        if n < 0:
            raise ValueError("fstring size must be a positive value")
        i = self.__pos
        j = i + (n+3)//4*4
        if j > len(self.__buf):
            raise EOFError("Not enough bytes left to unpack")
        self.__pos = j
        return self.__buf[i:i+n]

    unpack_fopaque = unpack_fstring

    def unpack_string(self) -> bytes:
        n = self.unpack_uint()
        return self.unpack_fstring(n)

    unpack_opaque = unpack_string
    unpack_bytes = unpack_string

    def unpack_list(self, unpack_item) -> list:
        item_list = []
        while (x := self.unpack_uint()) != 0:
            if x != 1:
                raise ConversionError(f"0 or 1 expected, got {x!r}")
            item_list.append(unpack_item())
        return item_list

    def unpack_farray(self, n: int, unpack_item) -> list:
        return [unpack_item() for _ in range(n)]

    def unpack_array(self, unpack_item) -> list:
        n = self.unpack_uint()
        return self.unpack_farray(n, unpack_item)