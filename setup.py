from setuptools import setup, find_packages
import os
import sys

# Place the directory containing _version_git on the path
for path, _, filenames in os.walk(os.path.dirname(os.path.abspath(__file__))):
    if "_version_git.py" in filenames:
        sys.path.append(path)
        break

from _version_git import __version__, get_cmdclass  # noqa

module_name = "ytmusic-deleter"

install_reqs = [
    "click",
    "ytmusicapi >= 0.19.3",
    "enlighten"
]

develop_reqs = [
    "pre-commit",
    "flake8",
    "yapf",
    "coverage",
    "rope",
    "pytest"
]

with open("README.md", "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name=module_name,
    version=__version__,
    description="Delete your YouTube Music library and/or uploads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="apastel",
    author_email="alex.r.pastel@gmail.com",
    url="https://github.com/apastel/ytmusic-deleter",
    cmdclass=get_cmdclass(),
    packages=find_packages(),
    install_requires=install_reqs,
    python_requires=">=3.5",
    extras_require={"dev": develop_reqs},
    entry_points="""
        [console_scripts]
        ytmusic-deleter=ytmusic_deleter.cli:cli
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
