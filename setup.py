# Copyright (C) 2019 New York University.
#
# This file is part of REANA Templates. REANA Templates is free software; you
# can redistribute it and/or modify it under the terms of the MIT License; see
# LICENSE file for more details.

from setuptools import setup


install_requires=[
    'jsonschema',
    'pyyaml>=5.1',
    'future',
    'gitpython'
]


tests_require = [
    'coverage>=4.0',
    'coveralls',
    'nose'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
}


setup(
    name='reana-template-core',
    version='0.1.0',
    description='Templates for REANA workflows',
    license='MIT',
    packages=['reanatempl'],
    test_suite='nose.collector',
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires
)
