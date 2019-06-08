# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
import os
from setuptools import setup, find_packages

description = 'City tours.'

try:
    this_path = os.path.dirname(os.path.abspath(__file__))
    fn_readme = os.path.join(this_path, 'README.md')
    with open(fn_readme) as fh:
        long_description = fh.read()
except (IOError, OSError):
    long_description = description


setup(
    name='citytours',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.4',
    install_requires=[
        'Flask>=1.0',
        'Flask-Assets',
        'webassets>=0.12.1',
        'Flask-Turbolinks',
        'libsass',
        'jsmin',
        'natsort',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    author='Bradley Dice',
    author_email='bdice@bradleydice.com',
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bdice/hack-a2-2019',

    entry_points={
        'console_scripts': [
            'citytours = citytours.__main__:main',
        ],
    },
)
