"""
Utilitary functions to check for pre-conditions like 'is this command available?'
or 'is this path available?'
"""
import subprocess
from pathlib import Path

from .shell import runsh


def command_available(command: str) -> bool:
    """
    Checks if a given command is available in the current shell.
    """
    return (
        runsh(
            f"command -v {command}",
            suppress=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ).returncode
        == 0
    )


def path_exists(path: str) -> bool:
    """
    Checks if a given path exists.
    """
    return Path(path).expanduser().exists()


def user_shell_is(shell: str) -> bool:
    """
    Checks if the current user's shell is the given shell.

    Shell must be passed as full path string, such as `/usr/bin/zsh`.
    """
    return runsh("getent passwd $USER | awk -F: '{print $NF}'").stdout == shell


def installed_vscode_extensions():
    """
    Lists the currently installed vscode extensions.
    """
    output = runsh("code --list-extensions", capture_output=True).stdout
    output = output.decode("utf-8")
    return set(ext.lower() for ext in output.split("\n")[:-1])


def symlink(path, target_path):
    """
    Checks if a symlink points to the given target path.
    """
    link = Path(path).expanduser().readlink()
    target = Path(target_path).expanduser()

    try:
        return link == target
    except Exception:
        return False
