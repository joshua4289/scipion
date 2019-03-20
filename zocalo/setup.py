#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

requirements = ["workflows", "zocalo"]
setup_requirements = []

setup(
    author="Joshua Lobo",
    author_email="scientificsoftware@diamond.ac.uk",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
    ],
    description="Zocalo runners for Scipion",
    entry_points={
        "workflows.services": [
            "ScipionRunner = scipilo.consumers.scipion_consumer:ScipionRunner",
            "MotionCor2Runner = scipilo.consumers.zoc_mc2_consumer:MotionCor2Runner",
            "GctfRunner = scipilo.consumers.zoc_gctf_consumer:GctfRunner",
            "Relion2DRunner = scipilo.consumers.zoc_relion_refine_consumer:Relion2DRunner",
            "GautomatchRunner = scipilo.consumers.zoc_gautomatch_consumer:GautomatchRunner",
        ],
    },
    install_requires=requirements,
    license="BSD license",
    include_package_data=True,
    name="scipilo",
    packages=find_packages(),
    setup_requires=setup_requirements,
    version="0.5",
    zip_safe=False,
)

