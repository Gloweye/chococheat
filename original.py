from platform import system
from pathlib import Path
from configparser import ConfigParser

if system() == 'Windows':
    CONFIGFILE = Path.home() / 'AppData' / 'Local' / 'chococheat.ini'
else:  # Assume Linux-y
    CONFIGFILE = Path.home() / '.config' / 'chococheat.ini'

config = ConfigParser()
config.read(CONFIGFILE)
MAX_COUNT = b'\x99'  # Actually 2 4-bit integers. But still semantically one number, to represent 0-100.
OFFSET_ITEMS_A = 0x1c
OFFSET_ITEMS_B = 0x1d
OFFSET_ITEMS_C = 0x1e
OFFSET_ITEMS_D = 0x1f
AWAY_OFFSET = 0x15
USER_ID = config.getint('global', 'user_id', fallback=None)
GAME_SAVES_DIR = Path.home() / 'Documents' / 'Square Enix' / 'FINAL FANTASY VIII Steam' / f'user_{USER_ID}'
CHOCOSAVE = GAME_SAVES_DIR / 'chocorpg.ff8'
CHEATSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.cheat'


def copy_from_cheat_file(path: Path, cheat_path: Path):
    path.write_bytes(cheat_path.read_bytes())


def is_chicobo_away(path: Path):
    with path.open('rb') as file:
        file.seek(AWAY_OFFSET)
        return bool(int.from_bytes(file.read(1), 'big'))


def keep_items_at_max_forever():
    if CHEATSAVE.read_bytes() != CHOCOSAVE.read_bytes():
        print('Files different during init, copying...')
        copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)

    current_age = CHOCOSAVE.stat().st_mtime_ns
    while True:
        time.sleep(0.2)
        if current_age != CHOCOSAVE.stat().st_mtime_ns and is_chicobo_away(CHOCOSAVE):
            print(f'{int(time.time())} Change detected, altering chocobo save...')
            copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)
            current_age = CHOCOSAVE.stat().st_mtime_ns
            # write(CHOCOSAVE, {
            #     OFFSET_ITEMS_A: MAX_COUNT,
            #     OFFSET_ITEMS_B: MAX_COUNT,
            #     OFFSET_ITEMS_C: MAX_COUNT,
            #     OFFSET_ITEMS_D: MAX_COUNT,
            # })


if __name__ == '__main__':
    keep_items_at_max_forever()
