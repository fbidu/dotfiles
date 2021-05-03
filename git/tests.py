from pathlib import Path
from uuid import uuid4
import uuid
from dotfiles import checkers, shell


def test_git_installed():
    assert checkers.command_available("git")


def test_gitconfig_symlinked():
    assert checkers.symlink(Path("~/.gitconfig"), Path("~/dotfiles/git/gitconfig"))


def test_global_gitignore():
    test_folder = Path("/") / "tmp" / str(uuid4())
    included_file = str(uuid4())
    shell.runsh(
        f"""
        mkdir {test_folder} &&\
        cd {test_folder} \
        git init &&\
        mkdir env &&\
        touch {included_file}
    """
    )

    output = shell.runsh(
        f"cd {test_folder} && git status", capture_output=True, encoding="utf-8"
    )

    assert included_file in output.stdout
    assert not "env" in output.stdout
