"""Wizard giving access to the scripts."""
import enum
import sys
from argparse import ArgumentParser
from inspect import signature
from pathlib import Path
from time import sleep, time
from logging import getLogger, basicConfig, INFO

from chococheat.world_info import is_chicobo_away, CHEATSAVE, CHOCOSAVE


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
                    logger.info(f'{int(time())} Change detected, altering chocobo save...')
                    copy_from_cheat_file(CHOCOSAVE, CHEATSAVE)
                    current_age = CHOCOSAVE.stat().st_mtime_ns
        except KeyboardInterrupt:
            logger.info('ChocoCheat has exited.')


if __name__ == '__main__':
    basicConfig(format='{levelname: <8}{name: <20}:{lineno: <4}:{msg}', style='{', stream=sys.stdout, level=INFO)
    parser = ArgumentParser(
        'ChocoCheat',
        'python3 -m chococheat',
        'Cheat program to make FF8 really easy from the Chocobo World'
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
                if param.default is not param.empty:
                    kwargs['default'] = param.default
                if issubclass(param.annotation, str) and issubclass(param.annotation, enum.Enum):
                    kwargs['choices'] = param.annotation.__members__.values()
                if param.annotation is bool:
                    kwargs['action'] = 'store_false' if param.default is True else 'store_true'
                else:
                    kwargs['action'] = 'store'
                    kwargs['type'] = param.annotation
                prefix = '--' if param.kind is param.KEYWORD_ONLY or param.annotation is bool else ''
                if prefix and param.annotation is not bool:
                    kwargs['required'] = param.default == param.empty
                if name in param_info:
                    kwargs['help'] = param_info[name]
                command_parser.add_argument(prefix + name, **kwargs)

    args = parser.parse_args()
    command = vars(args).pop('command')
    result = getattr(holder, command)(**vars(args))
    if result and isinstance(result, int) and 0 < result <= 127:  # I remember something about higher being invalid.
        raise SystemExit(result)
