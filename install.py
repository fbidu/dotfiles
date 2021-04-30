from functools import partial
import logging
import platform
import subprocess

logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s", level=logging.DEBUG
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

sys_update = lambda: subprocess.run(["sudo", PKG_MANAGER, "update"])
sys_upgrade = lambda: subprocess.run(["sudo", PKG_MANAGER, "full-upgrade", "-y"])
runsh = partial(subprocess.run, shell=True)


def install(*args):
    logging.info(f"Installing {', '.join(args)}")
    subprocess.run(["sudo", PKG_MANAGER, "install", *args, "-y"])


def install_fonts():
    fonts = (
        "FiraCode/Regular/complete/Fira%20Code%20Regular%20Nerd%20Font%20Complete.ttf",
        "Meslo/L/Regular/complete/Meslo%20LG%20L%20Regular%20Nerd%20Font%20Complete.ttf",
        "SourceCodePro/Regular/complete/Sauce%20Code%20Pro%20Nerd%20Font%20Complete.ttf",
    )
    nerd_fonts_url = "https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/"
    runsh("mkdir ~/.local/share/fonts")

    for font in fonts:
        url = f"{nerd_fonts_url}{font}"
        logging.info(f"Downloading {font.split('/')[0]}")
        runsh(f"wget -nc {url} -P ~/.local/share/fonts")
        logging.info(f"Font {font} installed")

    runsh("fc-cache -f -v")
    logging.info("All fonts installed")


def zsh_setup():
    zsh_installer = (
        "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
    )

    plugins = {
        "themes/powerlevel10k": "https://github.com/romkatv/powerlevel10k.git",
        "plugins/zsh-autosuggestions": "https://github.com/zsh-users/zsh-autosuggestions",
        "plugins/zsh-syntax-highlighting": "https://github.com/zsh-users/zsh-syntax-highlighting.git",
    }

    gterminal_profile = (
        "/org/gnome/terminal/legacy/profiles:/:b1dcc9dd-5262-4d8d-a863-c897e6d979b9"
    )
    default_font = "SauceCodePro Nerd Font 15"
    install("zsh")
    install("fzf")
    runsh(f'sh -c "$(curl -fsSL {zsh_installer})" "" --unattended')

    for path, url in plugins.items():
        runsh(
            f"git clone --depth=1 {url} ${{ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom/}}{path}"
        )

    runsh("ln -sfn ~/dotfiles/zshrc ~/.zshrc")
    runsh(f"dconf write {gterminal_profile}/font \"'{default_font}'\"")
    runsh(f"dconf write {gterminal_profile}/use-system-font false")
    runsh("chsh -s $(which zsh)")


def pyenv_setup():
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
    install(*docker_deps)
    runsh(f"curl -fsSL {docker_key} | sudo gpg --dearmor -o {docker_keyring}")
    runsh(
        f"""echo "deb [arch=amd64 signed-by={docker_keyring}] https://download.docker.com/linux/ubuntu \
        {UBUNTU_CODENAME} stable" | sudo tee {docker_repo_list}  > /dev/null"""
    )
    sys_update()
    install("docker-ce", "docker-ce-cli", "containerd.io")


sys_update()
sys_upgrade()
install("git")
install_fonts()
zsh_setup()
pyenv_setup()
docker_setup()