"""
Info about Chocoboworld, constants and functions.
Much detailed info originates from https://gamefaqs.gamespot.com/boards/197343-final-fantasy-viii/68239394 ,
Though the actual byte locations are shifted in the PC version.
"""
from enum import IntFlag
from logging import getLogger
from pathlib import Path
from typing import Union, Type

from chococheat.config import config

# Actually only know this about Windows for certain.
GAME_SAVES_DIR = Path.home() / 'Documents' / 'Square Enix' / 'FINAL FANTASY VIII Steam' \
                 / f'user_{config:global.user_id!d}'
CHOCOSAVE = GAME_SAVES_DIR / 'chocorpg.ff8'
BACKUPSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.bak'
CHEATSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.cheat'
logger = getLogger()


# Fully valid file. With max items, best weapon, best rank, and no powerups.
# Unlike pocket-station, it seems cross-save compatible, though cross-player hasn't been tested.
DEMO_FILE = b'\xb3\x00\x00\x00\xff\xff\x08\x83\x02\x16\x16\x99\x99\xf7\x00\x05' \
            b'\x0b\xeb\xf0b\x05\x01\x02\xff\x14/\x08\x04\x99\x99\x99\x99' \
            b'\xff\x02\x08\x01\x05\x11\x06\x01\x0b\xff\x01\t\x00\x03\x10\x03' \
            b'\x03\x01\xdf\xb4#\x8b\x00\xc8\x04\x00\x06\x01\xbb\x00\x00 ' \
            b'\x00\x05""\xf4\xf0\x02\x87\x02\x03\xd8\xdc\xffB\x0fT' \
            b'\x0f\xe5\xf6$\xffsA\x005\x00!\x00\x03\xf7\x02\x00' \
            b'\x03l\x05E\x00]\x00\xef\x0f\x02\x03\x0fl\x05K\x00' \
            b'`\xdf\x00\x10\x01\x03\x10l\x05\x00\x00\x05\x17\x04\x00\x07' \
            b'k\x06\xa4\x0f\xb6\x0f\xc8\x0f\xda\x03\x00\xef\x0f\x01\x1f\x13' \
            b'\x1f%\x1f7\x1fI\x1f[\x1fm\x1f\xc0\x7f\x1f\x91\x1f' \
            b'\xa3\x1f\xb5\x1f\xc7\x1f\xe8\xf3b\x05\xf7\x99\x99\x06\xe9\xf2' \
            b'0\x02\x00\x00\x03\xc5\x07'


class MogStatus(IntFlag):
    UNUSED = 1  # Always set
    OUT = 2
    FOUND = 4
    MOG_AVAILABLE = 8
    MOG_ACTIVE = 16
    DEMON_KING_DEAD = 32  # Only use when level == 100
    CURRENT_EVENT_HAPPENED = 64
    EVENT_WAIT_OFF = 128

    INITIAL = UNUSED + OUT
    ALL = 255 - 64


class Variable:

    def __init__(self, offset: int, end: int = None):
        if end is None:
            end = offset
        self.offset = offset
        self.size = end - offset + 1

    def __get__(self, instance, owner) -> str:
        if isinstance(instance, type):
            raise TypeError('Variables are only valid on instances, not types.')
        # The [::-1] looks really weird, but that's a file structure issue.
        return instance.buffer[self.offset:self.offset + self.size][::-1].hex()

    def __set__(self, instance, value: str):
        if not isinstance(instance.buffer, bytearray):
            raise RuntimeError('Cannot assign to instance when it\'s not writable.')
        instance.buffer[self.offset:self.offset + self.size] = bytes.fromhex(f'{value:0<{self.size}}')[::-1]


class FlagsVariable:
    def __init__(self, offset: int, flags: Type[IntFlag]):
        self.offset = offset
        self.flags = flags

    def __get__(self, instance, owner) -> IntFlag:
        if isinstance(instance, type):
            raise TypeError('Variables are only valid on instances, not types.')
        return self.flags(instance.buffer[self.offset])

    def __set__(self, instance, value: IntFlag):
        if not isinstance(instance.buffer, bytearray):
            raise RuntimeError('Cannot assign to instance when it\'s not writable.')
        instance.buffer[self.offset] = value


class DictVariable:

    def __init__(self, **kwargs: Variable):
        self.variables = kwargs

    def __get__(self, instance, owner):
        return BoundDict(instance, self.variables)


class BoundDict:

    def __init__(self, owner, mapping):
        self.owner: World = owner
        self.mapping: dict[str, Variable] = mapping

    def __getitem__(self, item: str):
        return self.mapping[item].__get__(self.owner, self.owner)

    def __setitem__(self, key, value):
        return self.mapping[key].__set__(self.owner, value)

    def get(self, item: str, default=None):
        return self.mapping.get(item, default).__get__(self.owner, self.owner)

    def _as_normal_dict(self):
        return {key: value.__get__(self.owner, self.owner) for key, value in self.mapping.items()}

    def items(self):
        return self._as_normal_dict().items()


class World:
    """
    Describes a world and how to edit it. Note that most data is absent here.
    Most numeric data is in a very odd format, leading to the odd parsing in the Variable class.
    """
    away = Variable(0x15)  # Valid are 00, 01, and reading can show a few others. Also tracked in FF8, must match.
    level = Variable(0x08)  # 01-99, and 00 means level 100 and is the max.
    current_hp = Variable(0x09)
    maximum_hp = Variable(0x0a)  # Gets to like 40-ish assuming Rank 0 and Level 100. But up to 99 works fine.
    rank = Variable(0x0e)  # 00 to 06 are valid. Lower gives higher class items and about 10 more (max) HP on lvl-up.
    world_id = Variable(0x13, 0x14)  # Ignorable. Affects rank on creation, but not during a game.
    weapon = Variable(0x0b, 0x0c)  # 0000 to 9999 valid as integers, with each digit being separate. 8999 beats 9000.
    item_a = Variable(0x1c)  # If reading this doesn't give an int of 00-99, then I don't know how to read/write items.
    item_b = Variable(0x1d)
    item_c = Variable(0x1e)
    item_d = Variable(0x1f)
    items = DictVariable(A=item_a, B=item_b, C=item_c, D=item_d)
    mog_status = FlagsVariable(0x07, MogStatus)
    # Haven't yet managed to find the byte location of the powerup counter.

    def __init__(self, arg: Union[Path, bytes], for_writing=False):
        if isinstance(arg, Path):
            self.buffer = arg.read_bytes()
        else:
            self.buffer = arg
        if for_writing and self.away:
            self.buffer = bytearray(self.buffer)

    @classmethod
    def from_dummy(cls):
        return cls(DEMO_FILE)

    def write_to_file(self, path: Path):
        path.write_bytes(self.buffer)

    @property
    def items_visible(self) -> bool:
        try:
            int(self.item_a)
            return True
        except ValueError:
            return False
