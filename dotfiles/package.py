"""Supplies a general package definition"""
from dataclasses import dataclass
from enum import Enum

from .shell import install

PackageTypes = Enum("PackageType", "APT PIP GH_RELEASE GH_REPO PYENV-RELEASE WGET")


@dataclass
class Package:
    """
    A package is any installable thing.
    """

    name: str
    pkg_type: PackageTypes
    url: str = ""

    def install(self):
        """
        Installs the package.
        """
        if self.pkg_type == PackageTypes.APT:
            install(self.name)
