from setuptools import setup, find_packages

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name='rblx-open-cloud',
    version='0.0.7',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author="TreeBen77",
    packages=[
        'rblxopencloud'
    ],
    url='https://github.com/TreeBen77/rblx-open-cloud',
    keywords='roblox, datastores, opencloud',
    install_requires=[
        'python-dateutil',
        'requests'
    ]
)