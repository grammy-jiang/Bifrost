"""
setup.py for packaging
"""
from setuptools import find_packages, setup

import versioneer

setup(
    name="Bifrost",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A Great FireWall Crossing Framework",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=False,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "cachetools",
        "grpcio",
        "grpcio-tools",
        "orjson",
        "orm",
        "sanic",
        "sanic-graphql",
        "uvloop",
        "websockets",
    ],
)
