"""Wizard giving access to the scripts."""
from enum import Enum
import sys
from argparse import ArgumentParser
from inspect import signature
from pathlib import Path
from time import sleep, time
from logging import getLogger, basicConfig, INFO

from chococheat.world_info import (is_chicobo_away, CHEATSAVE, CHOCOSAVE, OFFSET_ITEMS_A, OFFSET_ITEMS_B, LEVEL_OFFSET,
                                   OFFSET_ITEMS_C, OFFSET_ITEMS_D, RANK_OFFSET, CURRENT_HP_OFFSET, MAX_HP_OFFSET)


logger = getLogger(__name__)


def copy_from_cheat_file(path: Path, cheat_path: Path):
    path.write_bytes(cheat_path.read_bytes())


def cli_endpoint(func=None, /, **kwargs):
    """Decorator for CLI Endpoints"""
    if func:
        func.endpoint_info = {}
        return func
    else:
        def deco(func):
            func.endpoint_info = kwargs
            return func
        return deco


class SaveType(str, Enum):
    primary = 'primary'
    cheat = 'cheat'
    backup = 'backup'


class CLITool:
    """Manages CLI endpoints. Quick and Dirty kind."""

    @cli_endpoint
    def run(self):
        """Using the saved settings, keep swapping out the Chocobo World file for the cheating one."""
        if CHEATSAVE.read_bytes() != CHOCOSAVE.read_bytes():
            logger.info('Files different during init, copying...')
            copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)

        current_age = CHOCOSAVE.stat().st_mtime_ns
        logger.info('Running ChocoCheat auto-refresh.')
        logger.info('You can now repeatedly bring your Chicobo home and send him away in the menu.')
        logger.info('Press Ctrl+C to exit.')
        try:
            while True:
                sleep(0.2)
                if current_age != CHOCOSAVE.stat().st_mtime_ns and is_chicobo_away(CHOCOSAVE):
                    logger.info(f'Change detected, replacing chocobo save...')
                    copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)
                    current_age = CHOCOSAVE.stat().st_mtime_ns
        except KeyboardInterrupt:
            logger.info('ChocoCheat has exited.')

    @cli_endpoint(
        main='Which save to print the status of; defaults to the cheatsave.'
    )
    def status(self, *, main: SaveType = SaveType.cheat):
        """
        Print the status of a chocoworld save.
        """
        subject = {
            SaveType.cheat: CHEATSAVE,
            SaveType.primary: CHOCOSAVE,
            SaveType.backup: CHOCOSAVE,  # @TODO: Actual backup management.
        }[main]
        if not subject.exists():
            logger.info(f'Could not find the {main} file.')
            return

        filedata = subject.read_bytes()

        if is_chicobo_away(subject):
            logger.info('Chicobo is currently exploring. That means we can cheat.')
        else:
            logger.info('Chicobo is currently home. That means we can\'t meaningfully edit the save file.')

        logger.info(f'Chicobo\'s (hidden) rank is {filedata[RANK_OFFSET].to_bytes(1, "big").hex()}.')
        level = int(filedata[LEVEL_OFFSET].to_bytes(1, "big").hex()) or 100
        logger.info(f'Chicobo\'s level is {level}.')
        min_hp = filedata[CURRENT_HP_OFFSET].to_bytes(1, 'big').hex()
        max_hp = filedata[MAX_HP_OFFSET].to_bytes(1, 'big').hex()
        logger.info(f'Chicobo\'s HP is {min_hp}/{max_hp}')

        if filedata[OFFSET_ITEMS_A].to_bytes(1, 'big').hex():
            # Consider it valid item data
            for key, value in {
                'A': filedata[OFFSET_ITEMS_A].to_bytes(1, 'big').hex(),
                'B': filedata[OFFSET_ITEMS_B].to_bytes(1, 'big').hex(),
                'C': filedata[OFFSET_ITEMS_C].to_bytes(1, 'big').hex(),
                'D': filedata[OFFSET_ITEMS_D].to_bytes(1, 'big').hex(),
            }.items():
                if value:
                    logger.info(f'Cactuar has found {int(value)} {key}-class items.')

    @cli_endpoint(
        item_a='Number of items of category A to give, range 0-99 inclusive.',
        item_b='Number of items of category B to give, range 0-99 inclusive.',
        item_c='Number of items of category C to give, range 0-99 inclusive.',
        item_d='Number of items of category D to give, range 0-99 inclusive.',
    )
    def items(self, *, item_a: int = None, item_b: int = None, item_c: int = None, item_d: int = None):
        """Changes the item numbers set in the cheatsave."""
        data = bytearray(CHEATSAVE.read_bytes())
        if not data[OFFSET_ITEMS_A].to_bytes(1, 'big').hex():
            logger.critical('Cheat Save is not in a state that we know how to modify number of items.')
            logger.info('Please play the chocobo game until you have at least 2 kinds of items.')
            return 1
        table = {
            'A': (item_a, OFFSET_ITEMS_A),
            'B': (item_b, OFFSET_ITEMS_B),
            'C': (item_c, OFFSET_ITEMS_C),
            'D': (item_d, OFFSET_ITEMS_D),
        }
        for symbol, (item, offset) in table.items():
            if item is not None:
                if 0 <= item < 100:
                    data[offset] = int.from_bytes(bytes.fromhex(f'{item:0<2}'), 'big')
                    logger.info(f'There are now {item} {symbol}-class items.')
                else:
                    logger.info(f'Number of items provided for {symbol} out of range 0-99 inclusive.')

        CHEATSAVE.write_bytes(data)


if __name__ == '__main__':
    fmt = '{levelname: <8}{name: <20}:{lineno: <4}:{msg}' if '--verbose' in sys.argv else '{msg}'
    basicConfig(format=fmt, style='{', stream=sys.stdout, level=INFO)
    parser = ArgumentParser(
        'ChocoCheat',
        'python -m chococheat',
        'Cheat program to make FF8 really easy by messing with the Chocobo World save file.'
    )
    subs = parser.add_subparsers(title='command', dest='command')
    holder = CLITool()
    for key, value in vars(CLITool).items():
        if hasattr(value, 'endpoint_info'):
            param_info = value.endpoint_info
            command_parser = subs.add_parser(key, help=value.__doc__)
            for name, param in signature(value, follow_wrapped=True).parameters.items():
                if name == 'self':
                    continue

                kwargs = {}
                prefix = ''
                if param.default is not param.empty:
                    kwargs['default'] = param.default
                    kwargs['required'] = False
                    if param.kind is param.KEYWORD_ONLY:
                        prefix = '--'
                elif param.annotation is not bool and param.kind is param.KEYWORD_ONLY:
                    kwargs['required'] = True
                    prefix = '--'

                if issubclass(param.annotation, str) and issubclass(param.annotation, Enum):
                    kwargs['choices'] = tuple(mem for mem in param.annotation.__members__)
                if param.annotation is bool:
                    kwargs['action'] = 'store_false' if param.default is True else 'store_true'
                else:
                    kwargs['action'] = 'store'
                    kwargs['type'] = param.annotation
                if name in param_info:
                    kwargs['help'] = param_info[name]
                if '_' in name:
                    kwargs['dest'] = name
                    name = name.replace('_', '-')

                command_parser.add_argument(prefix + name, **kwargs)

    args = parser.parse_args()
    command = vars(args).pop('command')
    if command is None:
        parser.print_help()
        raise SystemExit(0)
    result = getattr(holder, command)(**vars(args))
    if result and isinstance(result, int) and 0 < result <= 127:  # I remember something about higher being invalid.
        raise SystemExit(result)
