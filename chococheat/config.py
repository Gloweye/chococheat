"""Configfile Management"""
from configparser import ConfigParser, _UNSET
from logging import getLogger
from platform import system
from pathlib import Path


logger = getLogger(__name__)


class Config(ConfigParser):

    def __format__(self, format_spec):
        format_spec, type_ = format_spec.split('!')
        section, key, *fb = format_spec.split('.')
        fallback = _UNSET if not fb else fb[0]
        return str({
            'd': self.getint,
            'i': self.getint,
            'b': self.getboolean,
            'f': self.getfloat,
        }.get(type_, self.get)(section, key, fallback=fallback))


if system() == 'Windows':
    CONFIGFILE = Path.home() / 'AppData' / 'Local' / 'chococheat.ini'
else:  # Assume Linux-y
    CONFIGFILE = Path.home() / '.config' / 'chococheat.ini'

config = Config()
if CONFIGFILE.exists():
    config.read(CONFIGFILE)
else:
    CONFIGFILE.touch()

FF8_DIR = Path.home() / 'Documents' / 'Square Enix' / 'FINAL FANTASY VIII Steam'


def _init_user_id(directory):
    if not directory.exists():
        logger.critical('Could not find FF8 Game directory.')
        return
    candidates = []
    for path in directory.iterdir():
        if path.is_dir() and path.name.startswith('user_'):
            candidates.append(path)

    if candidates:
        user_id = candidates[0].stem[5:]
        logger.info(f'Found multiple candiate user id\'s. Using {user_id}')
    else:
        logger.critical('Could not find your user id from the user saves directory.')
        return

    config.set('global', 'user_id', user_id)
    with CONFIGFILE.open('w') as file:
        config.write(file)


if config.get('global', 'user_id', fallback=None) is None:
    _init_user_id(FF8_DIR)

GAME_SAVES_DIR = FF8_DIR / f'user_{config:global.user_id.not_found!d}'
CHOCOSAVE = GAME_SAVES_DIR / 'chocorpg.ff8'
BACKUPSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.bak'
CHEATSAVE = GAME_SAVES_DIR / 'chocorpg.ff8.cheat'
