from pathlib import Path

from setuptools import find_packages, setup

README = Path("README.md").read_text(encoding="utf-8")

setup(
    name="pyspectools2",
    version="1.1.0",
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
