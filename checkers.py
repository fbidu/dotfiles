from pathlib import Path
import subprocess
from shell import runsh


def command_available(command):
    return (
        runsh(
            f"command -v {command}",
            suppress=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        ).returncode
        == 0
    )


def path_exists(path):
    return Path(path).expanduser().exists()


def user_shell_is(shell):
    return runsh("getent passwd $USER | awk -F: '{print $NF}'").stdout == shell


def installed_vscode_extensions():
    output = runsh("code --list-extensions", capture_output=True).stdout
    output = output.decode("utf-8")
    return set(ext.lower() for ext in output.split("\n")[:-1])
