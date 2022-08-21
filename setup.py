from setuptools import setup, find_packages

setup(
    name='rblx-open-cloud',
    version='0.0.2',
    license='MIT',
    author="TreeBen77",
    package_dir={'': 'src'},
    url='https://github.com/TreeBen77/rblx-open-cloud',
    keywords='roblox, datastores, opencloud',
    install_requires=[
        'python-dateutil',
        'requests'
    ]
)