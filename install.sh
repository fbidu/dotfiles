#! /usr/bin bash

update() {
    sudo aptitude update
}

upgrade() {
    sudo aptitude full-upgrade -y
}

inst() {
    sudo aptitude install -y $@
}

update_system() {
    update
    upgrade
}


export UBUNTU_CODENAME=$( \
   (grep DISTRIB_CODENAME /etc/upstream-release/lsb-release || \
    grep DISTRIB_CODENAME /etc/lsb-release) 2>/dev/null | \
   cut -d'=' -f2 )

update_system
inst git

# Shell Setup
inst zsh
sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"


# Python Build Deps
inst build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl

# Docker install
inst apt-transport-https ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $UBUNTU_CODENAME stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
update
inst docker-ce docker-ce-cli containerd.io

