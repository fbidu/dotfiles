"""Offers a class to handle symbolic links"""
from pathlib import Path

from .checkers import path_exists
from .shell import runsh


# pylint: disable=too-few-public-methods
class SymbolicLinker:
    """
    Handles creation of symbolic link between two folders

    >>> linker = SymbolicLinker("~/dotfiles/vscode/", "~/.config/Code/User/")

    >>> for path in ["snippets", "keybindings.json", "settings.json"]:
    >>>     linker.link(path)

    """

    def __init__(self, source_dir, target_dir) -> None:

        if not path_exists(source_dir):
            raise FileNotFoundError(f"Source directory {source_dir} does not exist")

        if not path_exists(target_dir):
            raise FileNotFoundError(f"Target directory {target_dir} does not exist")

        self.source_dir = Path(source_dir).expanduser()
        self.target_dir = Path(target_dir).expanduser()

    def link(self, name, force=False):
        """
        Creates a symbolic link between the source and target directories
        """
        source = self.source_dir / name

        if not path_exists(source):
            raise FileNotFoundError(f"Source file {source} does not exist")

        target = self.target_dir / name

        command = "ln -s" if not force else "ln -sf"
        runsh(f"{command} {source} {target}")
