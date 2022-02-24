# Pyflow an open-source tool for modular visual programing in python
# Copyright (C) 2021-2022 Bycelium <https://www.gnu.org/licenses/>

"""Setup for the python package build."""

import pathlib
from setuptools import setup, find_packages


def get_version():
    """Load version from file."""
    version_file = open("VERSION")
    return version_file.read().strip()


def get_requirements():
    """Load requirements from file."""
    requirements_file = open("requirements.txt")
    return requirements_file.readlines()


HERE = pathlib.Path(__file__).parent  # The directory containing this file
README = (HERE / "pypi-readme.md").read_text()
VERSION = get_version()
REQUIREMENTS = get_requirements()

setup(
    name="byc-pyflow",
    version=VERSION,
    author="Bycelium",
    author_email="mathis.federico@bycelium.com",
    description="An open-source tool for modular visual programing in python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Bycelium/PyFlow",
    packages=find_packages(exclude=["*test*", "*docs*"]),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license="GPLv3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
