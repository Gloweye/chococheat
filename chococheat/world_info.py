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

# Actually only know this about Windows for certain.
GAME_SAVES_DIR = Path.home() / 'Documents' / 'Square Enix' / 'FINAL FANTASY VIII Steam' / f'user_{config:global.user_id!i}'
CHOCOSAVE = GAME_SAVES_DIR / 'chocorpg.ff8'
CHEATSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.cheat'


def is_chicobo_away(path: Path):
    with path.open('rb') as file:
        file.seek(AWAY_OFFSET)
        return bool(int.from_bytes(file.read(1), 'big'))
