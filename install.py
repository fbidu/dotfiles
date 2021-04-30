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
    nerd_fonts_url = "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/"
    fonts = ("Meslo", "FiraCode", "VictorMono", "SourceCodePro")
    subprocess.run("mkdir ~/.local/share/fonts", shell=True)

    for font in fonts:
        url = f"{nerd_fonts_url}{font}.zip"
        logging.info(f"Downloading {font}")
        subprocess.run(["wget", url, "-P", "/tmp"])
        logging.info(f"Extracting {font}")
        subprocess.run(f"unzip -uo /tmp/{font}.zip -d ~/.local/share/fonts", shell=True)
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
            f"git clone --depth=1 {url} ${{ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}}{path}",
            shell=True,
        )


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
zsh_setup()
pyenv_setup()