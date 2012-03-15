#! /usr/bin/env python

# Copyright (c) 2011 PediaPress GmbH
# See README.txt for additional licensing information.

from setuptools import setup

def get_version():
    d = {}
    execfile("batchrender/__init__.py", d, d)
    return d["__version__"]


install_requires=['mwlib', 'py', 'argparse']


def main():
    setup(
        name="mwlib.batchrender",
        version=get_version(),
        entry_points = {
            'console_scripts': ['batchrender = batchrender.batchrender:main'],
        },
        install_requires=install_requires,
        packages=["batchrender",],
        zip_safe=False,
        include_package_data=True,
        url = "http://code.pediapress.com/",
        description="batch render list of collections",
        long_description = open("README.txt", "r").read(),
        license="BSD License",
        maintainer="pediapress.com",
        maintainer_email="info@pediapress.com")

if __name__ == '__main__':
    main()
