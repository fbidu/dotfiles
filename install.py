from dotfiles.install import *

if __name__ == "__main__":
    sys_update()
    sys_upgrade()
    install("git")
    install_fonts()
    zsh_setup()
    pyenv_setup()
    docker_setup()
    dslr_setup()
    git_setup()
    keymapper_setup()
    vscode_setup()
    python_setup()
    cinnamon_setup()
    franz_setup()
