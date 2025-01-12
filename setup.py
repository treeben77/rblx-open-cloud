import re

from setuptools import setup

with open("rblxopencloud/__init__.py", "r") as file:
    version = re.search(
        r"VERSION: str = \"(\d+\.\d+\.\d+)\"", file.read()
    ).group(1)

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="rblx-open-cloud",
    description="API wrapper for Roblox Open Cloud",
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.9.0",
    author="treeben77",
    packages=["rblxopencloud", "rblxopencloudasync"],
    url="https://github.com/treeben77/rblx-open-cloud",
    keywords="roblox, open-cloud, data-store, place-publishing, mesageing-service",
    install_requires=[
        "requests",
        "aiohttp",
        "cryptography",
        "pyjwt",
        "python-dateutil",
        "PyNaCl",
    ],
)
