from pathlib import Path
import subprocess

def command_available(command):
    return subprocess.run(f"command -v {command}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).returncode == 0

def path_exists(path):
    return Path(path).expanduser().exists()

def user_shell_is(shell):
    subprocess.run("getent passwd $USER | awk -F: '{print $NF}'", shell=True).stdout == shell