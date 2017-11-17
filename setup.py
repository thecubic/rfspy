#!/usr/bin/env python3
from setuptools import setup
import os
import sys
import subprocess
import glob
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(name=__name__)
package = 'rfspy'
package_version = 'unknown'
release = False
release_version = '0.1'

# find the top directory, ham-fisted
try:
    revdir = os.path.dirname(os.path.realpath(__file__))
except:
    revdir = os.path.dirname(os.path.realpath(sys.argv[0]))

if release:
    package_version = release_version
else:
    try:
        gitrevcmd = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                   stdout=subprocess.PIPE, cwd=revdir)
        revision = gitrevcmd.stdout.decode('ascii').strip()
    except:
        log.exception("couldn't get git revision")
        revision = 'unknown'
    package_version = f"{release_version}+git.{revision[:7]}"


def id_revision():
    writeit = True
    _data = f'__version__ = "{package_version}"\n'
    # populate version into package
    verfilename = os.path.join(revdir, package, '_version.py')
    if os.path.exists(verfilename):
        with open(verfilename, 'r') as verfile:
            _rdata = verfile.read()
            writeit = _rdata.strip() != _data.strip()
    if writeit:
        with open(verfilename, 'w+') as verfile:
            verfile.write(_data)
    return revision


def get_scripts():
    return [script[len(revdir) + 1:]
            for script in glob.glob(f"{revdir}/bin/*")]


def do_setup():
    id_revision()
    setup(
        name=package,
        version=package_version,
        description='python3 driver for rfspy devices',
        author='Dave Carlson',
        author_email='thecubic@thecubic.net',
        install_requires=['pyusb'],
        packages=[package],
        scripts=get_scripts(),
        license="Apache 2.0",
        url="https://www.github.com/thecubic/rfspy",
    )


if __name__ == '__main__':
    do_setup()
