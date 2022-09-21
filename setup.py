#!/usr/bin/env python
# coding=utf-8
from setuptools import setup

with open("requirements.txt", "r") as file:
    requirements = file.readlines()

setup(
    name="maio_aio_shared_lib",
    version="1.0",
    packages=['maio', 'maio.lib',
              'maio.lib.configs', 'maio.lib.encoders', 'maio.lib.request', 'maio.lib.services',
              'maio.lib.session', 'maio.lib.worker'],
    install_requires=requirements,
    python_requires='>=3.9',
    zip_safe=True,
    author="Maio",
    author_email="konradend@gmail.com",
    description="Maio version of Aiohttp wrapper",
)
