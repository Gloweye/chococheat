"""Info about Chocoboworld, constants and functions"""
from pathlib import Path

from chococheat.config import config

MAX_COUNT = b'\x99'  # Actually 2 4-bit integers. But still semantically one number, to represent 0-100.

# Only valid if 0x1c != 0xea
OFFSET_ITEMS_A = 0x1c
OFFSET_ITEMS_B = 0x1d
OFFSET_ITEMS_C = 0x1e
OFFSET_ITEMS_D = 0x1f
AWAY_OFFSET = 0x15  # To determine whether the Chicobo is "away", and therefore editable.
LEVEL_OFFSET = 0x08
CURRENT_HP_OFFSET = 0x09
MAX_HP_OFFSET = 0x0a
RANK_OFFSET = 0x0e
LOWER_ID_OFFSET = 0x13
HIGHER_ID_OFFSET = 0x14

# Actually only know this about Windows for certain.
GAME_SAVES_DIR = Path.home() / 'Documents' / 'Square Enix' / 'FINAL FANTASY VIII Steam' / f'user_{config:global.user_id!i}'
CHOCOSAVE = GAME_SAVES_DIR / 'chocorpg.ff8'
BACKUPSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.bak'
CHEATSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.cheat'


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


def is_chicobo_away(path: Path):
    with path.open('rb') as file:
        file.seek(AWAY_OFFSET)
        return bool(int.from_bytes(file.read(1), 'big'))
