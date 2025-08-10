#!/usr/bin/env python

from setuptools import setup

setup(
    name='termcap',
    version='1.1.0',
    license='BSD 3-clause license',
    author='rexwzh',
    author_email='1073853456@qq.com',
    description='Terminal capture tool - Record terminal sessions as SVG animations',
    long_description='A Linux terminal recorder written in Python '
                     'which renders your command line sessions as '
                     'standalone SVG animations.',
    url='https://github.com/rexwzh/termcap',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Shells',
        'Topic :: Terminals'
    ],
    python_requires='>=3.5',
    packages=[
        'termcap',
        'termcap.tests'
    ],
    scripts=['scripts/termcap'],
    include_package_data=True,
    install_requires=[
        'lxml',
        'pyte',
        'wcwidth',
    ],
    extras_require={
        'dev': [
            'coverage',
            'pylint',
            'twine',
            'wheel',
        ]
    }
)
