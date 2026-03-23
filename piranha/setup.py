"""Setup script for piranha Python package.

This installs the pure Python wrapper alongside the Rust extension.
"""

from setuptools import find_packages, setup
from piranha import __version__

setup(
    name="piranha",
    version=__version__,
    packages=find_packages(),
    package_data={"piranha": ["py.typed"]},
    python_requires=">=3.10",
)
