#!/usr/bin/env python3

import os
import pip
from setuptools import setup, find_packages

req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")

# Parse requirements:
requires = list(pip.req.parse_requirements(req_path, session=pip.download.PipSession()))

setup(
    name='kisschat',
    version='0.1.0',
    description='Simple web chat',
    install_requires=[str(r.req) for r in requires if r.req],
    dependency_links=[str(r.link) for r in requires if r.link],
    packages=find_packages(),
    scripts=['bin/kisschat', 'bin/kissauth']
)
