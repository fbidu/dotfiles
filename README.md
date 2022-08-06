# Dotfiles and Stuff

**Pretty Alpha stuff here. Not suitable for general usage yet**

Select your closes APT mirror first and then run

```bash
wget https://github.com/fbidu/dotfiles/archive/refs/heads/main.zip && unzip main.zip && mv dotfiles-main dotfiles
```

## Design Constraints

In short: **You must be able to pick a freshly installed Ubuntu system and run this.**

This code is made to be executed with any off-the-shelf Linux Mint setup. That is
the code does _not_ rely on anything outside of Python's standard library. It
does not even rely on `git` being already installed - hence the `wget` of
an archive of the repo.
## Whishlist

* [x] Update the whole system with aptitude
* [x] Install git
* [x] Install python build tools
* [x] Setup shell as ZSH
* [x] Install oh-my-zsh
* [x] Install powerline patched fonts
* [x] Install omzsh plugins
* [x] Setup pyenv
  * [x] Python 3.9
  * [x] Python 2.x
* [x] Install docker
  * [x] Add user to `docker` group
* [x] Install docker-compose
* [x] Install aliases
* [x] Install DLSR as webcam drivers
* [x] Setup git
* [x] Install key-mapper and my settings

## References

Heavily inspired on https://github.com/holman/dotfiles
