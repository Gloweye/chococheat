"""Wizard giving access to the scripts."""
from enum import Enum
import sys
from argparse import ArgumentParser
from inspect import signature
from pathlib import Path
from time import sleep
from logging import getLogger, basicConfig, INFO

from chococheat.config import config
from chococheat.world_info import World, CHEATSAVE, CHOCOSAVE, BACKUPSAVE, MogStatus

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
                if current_age != CHOCOSAVE.stat().st_mtime_ns and World(CHOCOSAVE).away:
                    logger.info(f'Change detected, replacing chocobo save...')
                    copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)
                    current_age = CHOCOSAVE.stat().st_mtime_ns
        except KeyboardInterrupt:
            logger.info('ChocoCheat has exited.')

    @cli_endpoint(
        world_='Which save to print the status of; defaults to the cheatsave.'
    )
    def status(self, *, world_: SaveType = SaveType.cheat):
        """
        Print the status of a chocoworld save.
        """
        subject = {
            SaveType.cheat: CHEATSAVE,
            SaveType.primary: CHOCOSAVE,
            SaveType.backup: BACKUPSAVE,
        }[world_]
        if not subject.exists():
            logger.info(f'Could not find the {world_} file.')
            return

        world = World(subject)

        if world.away:
            logger.info('Chicobo is currently exploring. That means we can cheat.')
        else:
            logger.info('Chicobo is currently home. That means we can\'t meaningfully edit the save file.')

        logger.info(f'Chicobo\'s (hidden) rank is {int(world.rank)}.')
        logger.info(f'Chicobo\'s level is {int(world.level) or 100}.')
        logger.info(f'Chicobo\'s weapon is {world.weapon}.')
        logger.info(f'Chicobo\'s HP is {int(world.current_hp)}/{int(world.maximum_hp)}')
        if world.items_visible:
            for item_class, number in world.items.items():
                logger.info(f'Cactuar has found {int(number)} {item_class}-class items.')
        else:
            logger.info('Cannot read the items at this time.')

    @cli_endpoint(
        auto='Automagically initialize the cheat tool as recommended.',
        ff8_only='Ignored without --auto. When initializing, optimizes only for purposes of playing FF8.'
    )
    def init(self, auto: bool, ff8_only: bool):
        """
        Setup the cheat tool. Backups, Chicobo power boosts, items, etc. You can either
        """
        if not CHOCOSAVE.exists():
            logger.info('There is currently no Chocobo World save file. This means there\'s also no way to import '
                        'cheated stuff. To get started, go into FF8, catch your first Chocobo (or pay the Chocoboy '
                        'to do it for you), and then go into the "Save" menu to send your Chicobo on it\'s way. '
                        'To edit data, it needs to be on "World", not "Home".')
            return

        world = World(CHEATSAVE if CHEATSAVE.exists() else CHOCOSAVE)
        if not world.away:
            logger.info('Your Chicobo is currently in it\'s "Home" state. To edit the file, you need to send it off'
                        'into the world first.')
            return

        if auto:
            if not BACKUPSAVE.exists():
                world.write_to_file(BACKUPSAVE)
            if not world.items_visible:
                world = World.from_dummy()
            if not ff8_only:
                world.weapon = 9999
                world.rank = 0
                world.level = 0  # This is actually level 100
                world.mog_status = MogStatus.ALL
            world.item_a = world.item_b = world.item_c = world.item_d = 99
            world.mog_status = world.mog_status | MogStatus.MOG_AVAILABLE
            world.write_to_file(CHEATSAVE)
            return

        logger.info('Wizard has not been implemented yet.')

    @cli_endpoint(
        item_a='Number of items of category A to give, range 0-99 inclusive.',
        item_b='Number of items of category B to give, range 0-99 inclusive.',
        item_c='Number of items of category C to give, range 0-99 inclusive.',
        item_d='Number of items of category D to give, range 0-99 inclusive.',
    )
    def items(self, *, item_a: int = None, item_b: int = None, item_c: int = None, item_d: int = None):
        """Changes the item numbers set in the cheatsave."""
        world = World(CHEATSAVE, for_writing=True)
        if not world.items_visible:
            logger.critical('Cheat Save is not in a state that we know how to modify number of items.')
            logger.info('Please play the chocobo game until you have at least 2 kinds of items.')
            return 1
        table = {
            'A': item_a,
            'B': item_b,
            'C': item_c,
            'D': item_d,
        }
        for item_class, num_desired in table.items():
            if num_desired is not None:
                if 0 <= num_desired < 100:
                    world.items[item_class] = str(num_desired)
                    logger.info(f'There are now {num_desired} {item_class}-class items.')
                else:
                    logger.info(f'Number of items provided for {item_class} out of range 0-99 inclusive.')

        world.write_to_file(CHEATSAVE)


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
                if param.annotation is not bool:

                    if param.default is not param.empty:
                        kwargs['default'] = param.default
                        kwargs['required'] = False

                    if param.kind is param.KEYWORD_ONLY:
                        kwargs['required'] = True
                        prefix = '--'

                if issubclass(param.annotation, str) and issubclass(param.annotation, Enum):
                    kwargs['choices'] = tuple(mem for mem in param.annotation.__members__)
                if param.annotation is bool:
                    kwargs['action'] = 'store_false' if param.default is True else 'store_true'
                    prefix = '--'
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
