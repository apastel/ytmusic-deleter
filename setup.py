from setuptools import setup


setup(
    name="ytmusic-deleter",
    version="0.1",
    py_modules=["deleter"],
    include_package_data=True,
    install_requires=["click", "ytmusicapi", "enlighten"],
    extras_require={
        "dev": ["pre-commit", "flake8", "yapf", "coverage"]
    },
    entry_points="""
        [console_scripts]
        deleter=deleter:cli
    """,
)
