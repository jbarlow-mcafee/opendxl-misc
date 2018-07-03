# pylint: disable=no-member, no-name-in-module, import-error

from __future__ import absolute_import
import glob
import distutils.command.sdist
import distutils.log
import subprocess
from setuptools import Command, setup
import setuptools.command.sdist

# Patch setuptools' sdist behaviour with distutils' sdist behaviour
setuptools.command.sdist.sdist.run = distutils.command.sdist.sdist.run

class LintCommand(Command):
    """
    Custom setuptools command for running lint
    """
    description = 'run lint against project source files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce("Running pylint", level=distutils.log.INFO)
        subprocess.check_call(["pylint"] + glob.glob("*.py"))

setup(
    # Package name:
    name="dxlmisc",

    # Version number:
    version="0.0.1",

    # Requirements
    install_requires=[
        "pylint"
    ],

    description="Misc OpenDXL Tools",

    python_requires='>=2.7.9,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',

    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],

    cmdclass={
        "lint": LintCommand
    }
)
