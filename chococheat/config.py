"""Configfile Management"""
from platform import system
from pathlib import Path
from configparser import ConfigParser, _UNSET


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
config.read(CONFIGFILE)
