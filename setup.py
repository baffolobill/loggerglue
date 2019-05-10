import io
import os
import re
from setuptools import setup, find_packages


PATH_BASE = os.path.dirname(__file__)


def read_file(fpath):
    """Reads a file within package directories."""
    with io.open(os.path.join(PATH_BASE, fpath)) as f:
        return f.read()


def get_version():
    """Returns version number, without module import (which can lead to ImportError
    if some dependencies are unavailable before install."""
    contents = read_file(os.path.join('loggerglue', '__init__.py'))
    version = re.search('VERSION = \(([^)]+)\)', contents)
    version = version.group(1).replace(', ', '.').strip()
    return version


setup(
    name='loggerglue',
    version=get_version(),
    description='Syslog protocol (rfc5424 and rfc5425) utilities',
    long_description=read_file('README.rst') + '\n\n' + read_file('CHANGES.txt'),
    author='Evax Software',
    author_email='contact@evax.fr',
    url='http://www.evax.fr/',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'setuptools',
        'pyparsing',
    ],
    keywords=['syslog', 'rfc5424', 'rfc5425', 'TLS'],
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging",
        "Topic :: Internet :: Log Analysis",
    ],
    test_suite="loggerglue.tests",
)
