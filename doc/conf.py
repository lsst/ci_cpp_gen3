"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
"""

from documenteer.conf.pipelinespkg import *  # noqa: F403, import *

project = "ci_cpp_gen3"
html_theme_options["logotext"] = project     # noqa: F405, unknown name
html_title = project
html_short_title = project
doxylink = {}
