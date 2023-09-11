from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path


class _Args(Namespace):
    path: Path


def _valid_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_file():
        raise ValueError(f'"{path_str}" is not a file')
    return path


def parse_argv() -> _Args:
    """"""
    parser = ArgumentParser()

    parser.add_argument("path", type=_valid_path, help="Picture path", required=True)

    return parser.parse_args(namespace=_Args())
