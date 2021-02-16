# -*- coding: utf-8 -*-
"""This module contains setup instructions for armadyl."""
import os
from setuptools import setup

curr_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(curr_dir, 'README.md')) as f:
    long_description = f.read()

with open(os.path.join(curr_dir, 'armadyl', 'version.py')) as f:
    exec(f.read())

setup(
    name='armadyl',
    version=__version__,  # noqa: F821
    author='Taylor Fox Dahlin',
    packages=['armadyl'],
    package_data={'': ['LICENSE'], },
    url='https://github.com/tfdahlin/armadyl',
    license='MIT',
    entry_points={

    },
    install_requires=['pycnic'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    description=('A lightweight Python 3 web framework.'),
    include_package_data=True,
    long_description_content_type='text/markdown',
    long_description=long_description,
    zip_safe=True,
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/tfdahlin/armadyl'
    },
    keywords=['API', 'Framework']
)
