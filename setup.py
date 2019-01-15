from setuptools import setup
import sys

if (sys.version_info[0] != 3):
    print("Please run this setup.py with python3")
    exit(1)

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    the_license = f.read()

setup(
    name='ansiterm',
    version='0.0.2',
    description='Python module to drive ANSI terminals.',
    long_description=readme,
    author='Peter Kraak<pkraak@dynamiccontrols.com>',
    license=the_license,
    packages=['ansiterm'],
    entry_points={}
)
