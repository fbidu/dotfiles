"""
Installs everything
"""
import sys

from dotfiles.install import (
    cinnamon_setup,
    docker_setup,
    dslr_setup,
    franz_setup,
    git_setup,
    install_fonts,
    keymapper_setup,
    pyenv_setup,
    python_setup,
    vscode_setup,
    zsh_setup,
)
from dotfiles.shell import sys_update, sys_upgrade

if __name__ == "__main__":
    run = input("Would you like to run this now? [y/n]: ")

    if run != "y":
        print("Skipping execution!")
        sys.exit(0)

    for command in [
        sys_update,
        sys_upgrade,
        git_setup,
        install_fonts,
        zsh_setup,
        pyenv_setup,
        docker_setup,
        dslr_setup,
        keymapper_setup,
        vscode_setup,
        python_setup,
        cinnamon_setup,
        franz_setup,
    ]:
        if input(f"Run {command.__name__}? [y/n]: ") == "y":
            command()
