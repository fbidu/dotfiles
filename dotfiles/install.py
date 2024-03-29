"""
This module includes functions to install softwares and files necessary for my setup.
"""
import logging
import platform
import subprocess
from pathlib import Path

from . import checkers
from .shell import install, runsh, set_dconf_key, sys_update
from .symbolic_linker import SymbolicLinker

logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)

# Are we on Linux Mint?
ON_MINT = (
    subprocess.check_output(["lsb_release", "-is"], encoding="utf-8")[:-1]
    == "Linuxmint"
)

if not ON_MINT:
    logging.warning("Not on Linux Mint! Some functions may not work")

# Linux Mint's Ubuntu Upstream
UBUNTU_CODENAME = (
    subprocess.check_output(
        """(grep DISTRIB_CODENAME /etc/upstream-release/lsb-release || \
    grep DISTRIB_CODENAME /etc/lsb-release) 2>/dev/null | \
   cut -d'=' -f2""",
        shell=True,
        encoding="utf-8",
    )[:-1]
    if ON_MINT
    else ""
)

if platform.system() != "Linux" or platform.machine() != "x86_64":
    raise RuntimeError("This code is for x86_64 Linux systems only")


def install_fonts():
    """
    Install Nerd Fonts I like. See https://github.com/ryanoasis/nerd-fonts.
    This function will also set Source Code Pro 15 as Gnome Terminal's font.

    Currently it install FiraCode, Mesl L and Source Code Pro.
    """
    fonts = (
        "FiraCode/Regular/complete/Fira%20Code%20Regular%20Nerd%20Font%20Complete.ttf",
        "Meslo/L/Regular/complete/Meslo%20LG%20L%20Regular%20Nerd%20Font%20Complete.ttf",
        "SourceCodePro/Regular/complete/Sauce%20Code%20Pro%20Nerd%20Font%20Complete.ttf",
    )
    nerd_fonts_url = "https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/"
    gterminal_profile = (
        "/org/gnome/terminal/legacy/profiles:/:b1dcc9dd-5262-4d8d-a863-c897e6d979b9"
    )
    default_font = "SauceCodePro Nerd Font 15"

    # Init local font dir
    runsh("mkdir ~/.local/share/fonts")

    for font in fonts:
        url = f"{nerd_fonts_url}{font}"
        logging.info(f"Downloading {font.split('/', maxsplit=1)[0]}")
        runsh(f"wget -nc {url} -P ~/.local/share/fonts")
        logging.info(f"Font {font} installed")

    # Update system font cache
    runsh("fc-cache -f -v > /dev/null")
    logging.info("All fonts installed")
    set_dconf_key(f"{gterminal_profile}/font", f"\"'{default_font}'\"")

    set_dconf_key(f"{gterminal_profile}/use-system-font", "false")


def zsh_setup():
    """
    Setups my shell. In details this function:
        * Installs zsh and oh-my-zsh
        * Install my current fav theme, powerlevel10k
        * Installs the ausuggestions and syntax highlighting plugins
        * Installs fzf, needed for the fuzzy finder built in plugin
        * Symlink zshrc to ~/.zshrc
        * Change the user's default shell to zsh
    """
    ohmyzsh_installer = (
        "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
    )

    plugins = {
        "themes/powerlevel10k": "https://github.com/romkatv/powerlevel10k.git",
        "plugins/zsh-autosuggestions": "https://github.com/zsh-users/zsh-autosuggestions",
        "plugins/zsh-syntax-highlighting": "https://github.com/zsh-users/zsh-syntax-highlighting.git",  # noqa pylint: disable=line-too-long
    }
    deps = []

    if not checkers.command_available("zsh"):
        deps.append("zsh")
    if not checkers.command_available("fzf"):
        deps.append("fzf")

    install(*deps)
    if not checkers.path_exists("~/.oh-my-zsh"):
        logging.info("Installing oh-my-zsh")
        runsh(f'sh -c "$(curl -fsSL {ohmyzsh_installer})" "" --unattended')
    else:
        logging.info("oh-my-zsh already exists. Skipping")

    for path, url in plugins.items():
        logging.info(f"Installing {path}")
        runsh(
            f"git clone --depth=1 {url} ${{ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom/}}{path}"
        )

    runsh("ln -sfn ~/dotfiles/zshrc ~/.zshrc")
    if not checkers.user_shell_is("/usr/bin/zsh"):
        runsh("chsh -s $(which zsh)")
    logging.info("zsh installed")
    runsh("source ~/.zshrc")


def pyenv_setup():
    """
    Install pyenv, Python 3.9.1 and Python 2.7.18 as global versions.
    """
    python_build_deps = (
        "build-essential",
        "curl",
        "libbz2-dev",
        "libffi-dev",
        "liblzma-dev",
        "libncurses5-dev",
        "libncursesw5-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "libssl-dev",
        "llvm",
        "python3-openssl",
        "tk-dev",
        "wget",
        "xz-utils",
        "zlib1g-dev",
    )
    install(*python_build_deps)
    runsh("git clone https://github.com/pyenv/pyenv.git ~/.pyenv")
    runsh("cd ~/.pyenv && src/configure && make -C src")
    runsh("source ~/.zshrc")
    runsh("pyenv install 3.10.5 -s")
    runsh("pyenv install 2.7.18 -s")
    runsh("pyenv global 3.10.5 2.7.18")


def docker_setup():
    """
    Install docker, docker-compose and add
    the current user to the `docker` group
    """
    docker_deps = (
        "apt-transport-https",
        "ca-certificates",
        "curl",
        "gnupg",
        "lsb-release",
    )
    docker_key = "https://download.docker.com/linux/ubuntu/gpg"
    docker_keyring = "/usr/share/keyrings/docker-archive-keyring.gpg"
    docker_repo_list = "/etc/apt/sources.list.d/docker.list"
    docker_compose_url = "https://github.com/docker/compose/releases/download/v2.9.0/docker-compose-linux-x86_64"  # noqa #pylint: disable=line-too-long
    install(*docker_deps)
    runsh(f"curl -fsSL {docker_key} | sudo gpg --dearmor -o {docker_keyring}")
    runsh(
        f"""echo "deb [arch=amd64 signed-by={docker_keyring}] https://download.docker.com/linux/ubuntu \
        {UBUNTU_CODENAME} stable" | sudo tee {docker_repo_list}  > /dev/null"""  # noqa pylint: disable=line-too-long
    )
    sys_update()
    install("docker-ce", "docker-ce-cli", "containerd.io")
    runsh("sudo usermod -aG docker $USER")
    runsh(f"sudo curl -L {docker_compose_url} -o /usr/local/bin/docker-compose")
    runsh("sudo chmod +x /usr/local/bin/docker-compose")


def dslr_setup():
    """
    Install gphoto2, v4l2loopback-utils and ffmpeg, needed for the `cam` alias to work.
    This is needed in order to use a DSLR cam on linux.

    See:
    https://medium.com/nerdery/dslr-webcam-setup-for-linux-9b6d1b79ae22
    https://askubuntu.com/questions/856460/using-a-digital-camera-canon-as-webcam
    """
    install("gphoto2", "ffmpeg", "v4l2loopback-utils")


def git_setup():
    """Sets up the global gitconfig and gitignore files"""
    install("git")
    runsh("ln -sfn ~/dotfiles/git/gitconfig ~/.gitconfig")
    runsh("ln -sfn ~/dotfiles/git/global.gitignore ~/.gitignore")
    if not checkers.path_exists("~/.gitconfig.local"):
        name = input("Full name for git: ")
        email = input("Email for git: ")

        with open(
            Path("~/.gitconfig.local").expanduser(), "w", encoding="utf-8"
        ) as gitconfig:
            gitconfig.write(f"[user]\n\tname = {name}\n\temail = {email}\n")


def input_remapper_setup():
    """
    Installs Input Remapper and setups its configuration

    https://github.com/sezanzeb/input-remapper
    """
    url = "https://github.com/sezanzeb/input-remapper/releases/download/1.5.0/input-remapper-1.5.0.deb"  # noqa pylint: disable=line-too-long
    runsh(f"wget -nc {url} -P /tmp")
    runsh("sudo gdebi /tmp/input-remapper-1.5.0.deb -n")
    runsh("ln -sfn ~/dotfiles/input-remapper ~/.config/input-remapper")


def vscode_setup():
    """
    Installs vscode, my favorite extensions, and sets up the configuration.
    """
    url = r"https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64"
    extensions = {
        "asciidoctor.asciidoctor-vscode",
        "batisteo.vscode-django",
        "bierner.emojisense",
        "dbaeumer.vscode-eslint",
        "eamodio.gitlens",
        "esbenp.prettier-vscode",
        "foxundermoon.shell-format",
        "ms-azuretools.vscode-docker",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter",
        "ms-vscode-remote.remote-containers",
        "ms-vscode-remote.remote-ssh-edit",
        "ms-vscode-remote.remote-ssh",
        "ms-vscode-remote.vscode-remote-extensionpack",
        "ms-vsliveshare.vsliveshare-audio",
        "ms-vsliveshare.vsliveshare-pack",
        "ms-vsliveshare.vsliveshare",
        "njpwerner.autodocstring",
        "pkief.material-icon-theme",
        "redhat.vscode-yaml",
        "richie5um2.vscode-sort-json",
        "tamasfe.even-better-toml",
        "techer.open-in-browser",
        "vscode-icons-team.vscode-icons",
        "wakatime.vscode-wakatime",
        "yummygum.city-lights-theme",
    }
    to_install = extensions - checkers.installed_vscode_extensions()

    if not checkers.command_available("code"):
        runsh(f"wget -nc --trust-server-names {url} -P /tmp")
        runsh("sudo gdebi /tmp/code_*_amd64.deb -n")

    for extension in to_install:
        logging.info(f"Installing vscode extension {extension}")
        runsh(f"code --install-extension {extension}")

    runsh("mv ~/.config/Code/User/ ~/.config/Code/User_backup")
    runsh("mkdir -p ~/.config/Code/User")

    linker = SymbolicLinker("~/dotfiles/vscode/", "~/.config/Code/User/")

    for path in ["snippets", "keybindings.json", "settings.json"]:
        linker.link(path)


def python_setup():
    """Installs my favorite python tools"""
    poetry_url = (
        "https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py"
    )
    to_install = {
        "black",
        "cookiecutter",
        "ipython",
        "jupyterlab",
        "notebook",
        "numpy",
        "pandas",
        "pre-commit",
        "pytest",
    }

    for package in to_install:
        if checkers.command_available(package):
            logging.info(f"Skipping {package} installation")
        runsh(f"pip install --user {package}")

    if not checkers.command_available("poetry"):
        logging.info("Installing Poetry")
        runsh(f"curl -sSL {poetry_url} | python -")
    else:
        logging.info("Skipping Poetry install")

    install("httpie")


def cinnamon_setup():
    """
    Sets up cinnamon to:
    - have 'sloppy' mouse focus
    - do not make that terrible sound while switching workspaces
    """
    set_dconf_key("/org/cinnamon/desktop/wm/preferences/focus-mode", "\"'sloppy'\"")
    set_dconf_key("/org/cinnamon/sounds/switch-enabled", "false")


def franz_setup():
    """
    Installs Franz
    """
    url = "https://github.com/meetfranz/franz/releases/download/v5.9.2/franz_5.9.2_amd64.deb"
    if not checkers.command_available("franz"):
        runsh(f"wget -nc {url} -P /tmp")
        runsh("sudo gdebi /tmp/franz_*_amd64.deb -n")
