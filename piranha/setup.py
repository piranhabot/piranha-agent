"""Setup script for piranha Python package.

This installs the pure Python wrapper alongside the Rust extension.
"""

from setuptools import find_packages, setup

setup(
    name="piranha",
    version="0.4.0",
    packages=find_packages(),
    package_data={"piranha": ["py.typed"]},
    python_requires=">=3.10",
)
