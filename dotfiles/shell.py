"""Utility functions to run shell commands"""
import logging
import subprocess
from datetime import datetime

PKG_MANAGER = "apt-get"


def timestamp():
    """Returns the current date time in the format YYYY_MM_DD_HHhMMminSS"""
    datetime.now().strftime("%Y_%m_%d_%Hh%Mmin%S.%f")


def package_cmd(command, *args):
    """
    Runs an `PKG_MANAGER` with an arbitrary `command` and any number of
    `args`, redirecting STDOUT and STDER to `logs/{timestamp}-{command}.log`
    and logs an error in case the command exists with failure
    """
    logfile = f"logs/{timestamp()}-{command}.log"

    log_args = ", ".join(args) if args else ""

    logging.info(f"Running {PKG_MANAGER} {command} {log_args}")

    with open(logfile, "w", encoding="utf-8") as logfile_handle:
        response = subprocess.run(
            ["sudo", PKG_MANAGER, command, *args, "-y"],
            stdout=logfile_handle,
            stderr=subprocess.STDOUT,
            check=True,
        )

    if response.returncode != 0:
        logging.error(
            f"Package management command '{command}' failed. See logs/{logfile} for details."
        )


def install(*args):
    """Install packages using the configured package manager"""
    package_cmd("install", *args)


def sys_update():
    """Updates the package manager's package lists"""
    package_cmd("update")


def sys_upgrade():
    """Upgrades the system"""
    package_cmd("full-upgrade")


def runsh(*args, suppress=False, **kwargs):
    """
    Runs a shell command and returns the response

    If `suppress` is True and the command errors out, no logs are written.
    """
    response = subprocess.run(*args, **kwargs, shell=True, check=False)
    if response.returncode != 0 and not suppress:
        logging.error(f"Shell command errored. Args: {', '.join(args)}")
    return response


def set_dconf_key(key, value):
    """
    Writes a key to dconf storage

    :param key: key to be written
    :type key: str
    :param value: value to be written - keep in mind of "GVariant" format
    :type value: str
    """
    runsh(f"dconf write {key} {value}")
