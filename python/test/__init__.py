import pkg_resources  # part of setuptools
version = pkg_resources.require("bbstat")[0].version
__version__ = version
