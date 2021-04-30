from datetime import datetime, time
from functools import partial
import logging
import platform
import subprocess

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO
)

PKG_MANAGER = "aptitude"

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

timestamp = lambda: datetime.now().strftime("%Y_%m_%d_%Hh%Mmin%S.%f")


def package_cmd(command, *args):
    """
    Runs an `PKG_MANAGER` with an arbitrary `command` and any number of
    `args`, redirecting STDOUT and STDER to `logs/{timestamp}-{command}.log`
    and logs an error in case the command exists with failure
    """
    logfile = f"logs/{timestamp()}-{command}.log"

    log_args = ", ".join(args) if args else ""

    logging.info(f"Running {PKG_MANAGER} {command} {log_args}")

    response = subprocess.run(
        ["sudo", PKG_MANAGER, command, *args, "-y"],
        stdout=open(logfile, "w"),
        stderr=subprocess.STDOUT,
    )

    if response.returncode != 0:
        logging.error(
            f"Package management command '{command}' failed. See logs/{logfile} for details."
        )


install = lambda *args: package_cmd("install", *args)
sys_update = lambda: package_cmd("update")
sys_upgrade = lambda: package_cmd("dist-upgrade")


def runsh(*args, **kwargs):
    response = subprocess.run(*args, **kwargs, shell=True)
    if response.returncode != 0:
        logging.error(f"Shell command errored. Args: {', '.join(args)}")


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
        logging.info(f"Downloading {font.split('/')[0]}")
        runsh(f"wget -nc {url} -P ~/.local/share/fonts")
        logging.info(f"Font {font} installed")

    # Update system font cache
    runsh("fc-cache -f -v")
    logging.info("All fonts installed")
    runsh(f"dconf write {gterminal_profile}/font \"'{default_font}'\"")
    runsh(f"dconf write {gterminal_profile}/use-system-font false")


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
        "plugins/zsh-syntax-highlighting": "https://github.com/zsh-users/zsh-syntax-highlighting.git",
    }

    install("zsh", "fzf")
    logging.info("Installing oh-my-zsh")
    runsh(f'sh -c "$(curl -fsSL {ohmyzsh_installer})" "" --unattended')

    for path, url in plugins.items():
        logging.info(f"Installing {path}")
        runsh(
            f"git clone --depth=1 {url} ${{ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom/}}{path}"
        )

    runsh("ln -sfn ~/dotfiles/zshrc ~/.zshrc")
    runsh("chsh -s $(which zsh)")
    logging.info("zsh installed")


def pyenv_setup():
    """
    Install pyenv, Python 3.9.1 and Python 2.7.18 as global versions.
    """
    python_build_deps = (
        "build-essential",
        "libssl-dev",
        "zlib1g-dev",
        "libbz2-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "wget",
        "curl",
        "llvm",
        "libncurses5-dev",
        "libncursesw5-dev",
        "xz-utils",
        "tk-dev",
        "libffi-dev",
        "liblzma-dev",
        "python-openssl",
    )
    install(*python_build_deps)
    runsh("git clone https://github.com/pyenv/pyenv.git ~/.pyenv")
    runsh("cd ~/.pyenv && src/configure && make -C src")
    runsh("pyenv install 3.9.1 -s")
    runsh("pyenv install 2.7.18 -s")
    runsh("pyenv global 3.9.1 2.7.18")


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
    docker_compose_url = "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-Linux-x86_64"
    install(*docker_deps)
    runsh(f"curl -fsSL {docker_key} | sudo gpg --dearmor -o {docker_keyring}")
    runsh(
        f"""echo "deb [arch=amd64 signed-by={docker_keyring}] https://download.docker.com/linux/ubuntu \
        {UBUNTU_CODENAME} stable" | sudo tee {docker_repo_list}  > /dev/null"""
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
    runsh("ln -sfn ~/dotfiles/git/gitconfig ~/.gitconfig")
    name = input("Full name for git: ")
    email = input("Email for git: ")
    runsh(f"git config --global user.name {name}")
    runsh(f"git config --global user.email {email}")
    


def keymapper_setup():
    url = "https://github.com/sezanzeb/key-mapper/releases/download/0.8.1/key-mapper-0.8.1.deb"
    runsh(f"wget -nc {url} -P /tmp")
    runsh("sudo gdebi /tmp/key-mapper-0.8.1.deb -n")
    runsh("ln -sfn ~/dotfiles/key-mapper ~/.config/key-mapper")


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
