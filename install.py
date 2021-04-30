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
    subprocess.run("mkdir ~/.local/share/fonts", shell=True)

    for font in fonts:
        url = f"{nerd_fonts_url}{font}"
        logging.info(f"Downloading {font.split('/')[0]}")
        subprocess.run(f"wget -nc {url} -P ~/.local/share/fonts", shell=True)
        logging.info(f"Font {font} installed")

    subprocess.run("fc-cache -f -v", shell=True)
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
    install("zsh")
    install("fzf")
    subprocess.run(
        f'sh -c "$(curl -fsSL {zsh_installer})" "" --unattended',
        shell=True,
    )

    for path, url in plugins.items():
        subprocess.run(
            f"git clone --depth=1 {url} ${{ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom/}}{path}",
            shell=True,
        )

    subprocess.run("ln -sfn ~/dotfiles/zshrc ~/.zshrc", shell=True)


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


sys_update()
sys_upgrade()
install("git")
install_fonts()
zsh_setup()
pyenv_setup()