import re
from pathlib import Path

from setuptools import find_packages, setup

README = Path("README.md").read_text(encoding="utf-8")
INIT_TEXT = Path("pyspectools2/__init__.py").read_text(encoding="utf-8")
VERSION_MATCH = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', INIT_TEXT)
if VERSION_MATCH is None:
    raise ValueError("Could not find __version__ in pyspectools2/__init__.py")

setup(
    name="pyspectools2",
    version=VERSION_MATCH.group(1),
    description="A library for recording and plotting spectrograms from audio data.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Sviatoslav Z.",
    author_email="slawekzhukovski@gmail.com",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "numpy",
        "sounddevice",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
