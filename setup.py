from setuptools import setup, find_packages

setup(
    name="PY-spectrogram-Tools",
    version="0.2.1",
    description="A library for recording and plotting spectrograms from audio data.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Sviatoslav",
    author_email="slawekzhukovski@gmail.com",
    packages=find_packages(),
    install_requires=[
        'matplotlib',
        'sounddevice',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
