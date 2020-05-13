"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ci.cpp.gen3


_g = globals()
_g.update(build_package_configs(
    project_name='ci_cpp_gen3',
    version=lsst.ci.cpp.gen3.version.__version__))
