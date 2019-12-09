from os import path
from setuptools import setup, find_packages

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as readme:
    long_description = readme.read()

setup(
    name='fry',
    version='0.2.0',

    description="Library for maintaining tracked requests sessions",
    long_description=long_description,
    long_description_content_type='text/markdown',

    author="Paul Henke",
    author_email="paul.henke@hulu.com",

    license="Apache 2.0",

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'License :: OSI Approved :: Apache Software License',
    ],

    keywords='requests stats',

    packages=find_packages(),

    install_requires=[
        'requests>=2.12.0',
    ],
)
