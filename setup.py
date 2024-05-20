#!/usr/bin/env python
import os
import sys

from setuptools import find_packages, setup

from immunity_firmware_upgrader import get_version

if sys.argv[-1] == 'publish':
    # delete any *.pyc, *.pyo and __pycache__
    os.system('find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf')
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload -s dist/*")
    os.system("rm -rf dist build")
    args = {'version': get_version()}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


setup(
    name='immunity-firmware-upgrader',
    version=get_version(),
    license='GPL3',
    author='Federico Capoano',
    author_email='support@immunity.io',
    description='Firmware upgrader module of Immunity',
    long_description=open('README.rst').read(),
    url='http://immunity.org',
    download_url='https://github.com/edge-servers/immunity-firmware-upgrader/releases',
    platforms=['Platform Independent'],
    keywords=['django', 'netjson', 'networking', 'immunity', 'firmware'],
    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'immunity-controller @ https://github.com/edge-servers/immunity-controller/tarball/master',
        'django-private-storage~=3.1.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
