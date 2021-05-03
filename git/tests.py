from pathlib import Path
from dotfiles import checkers


def test_git_installed():
    assert checkers.command_available("git")


def test_gitconfig_symlinked():
    assert checkers.symlink(
        Path("~/.gitconfig"), Path("/home/fbidu/dotfiles/git/gitconfig")
    )
