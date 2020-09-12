from setuptools import setup, find_packages


setup(
    name="ytmusic-deleter",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "ytmusicapi", "enlighten"],
    extras_require={
        "dev": ["pre-commit", "flake8", "yapf", "coverage"]
    },
    entry_points="""
        [console_scripts]
        ytmusic-deleter=ytmusic_deleter.cli:cli
    """,
)
