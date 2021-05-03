from dataclasses import dataclass
from enum import Enum

from .shell import install

PackageTypes = Enum("PackageType", "APT PIP GH_RELEASE GH_REPO PYENV-RELEASE WGET")


@dataclass
class Package:
    name: str
    pkg_type: PackageTypes
    url: str = ""

    def install(self):
        if self.pkg_type == PackageTypes.APT:
            install(self.name)
