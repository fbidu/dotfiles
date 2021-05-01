from datetime import datetime, time
from functools import partial
import logging
import platform
import subprocess

import checkers

PKG_MANAGER = "aptitude"
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


def runsh(*args, suppress=False, **kwargs):
    response = subprocess.run(*args, **kwargs, shell=True)
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
