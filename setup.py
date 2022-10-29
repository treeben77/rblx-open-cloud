from setuptools import setup
import rblxopencloud

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='rblx-open-cloud',
    description='API wrapper for Roblox Open Cloud',
    version=rblxopencloud.VERSION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    python_requires='>=3.9',
    author="TreeBen77",
    packages=[
        'rblxopencloud'
    ],
    url='https://github.com/TreeBen77/rblx-open-cloud',
    keywords='roblox, open-cloud, data-store, place-publishing, mesageing-service',
    install_requires=[
        'requests'
    ]
)
