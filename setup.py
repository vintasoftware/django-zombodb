#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from django_zombodb/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("django_zombodb", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('CHANGELOG.rst').read().replace('.. :changelog:', '')

setup(
    name='django-zombodb',
    version=version,
    description="""Easy Django integration with Elasticsearch through ZomboDB Postgres Extension""",
    long_description=readme + '\n\n' + history,
    author='Flávio Juvenal',
    author_email='flavio@vinta.com.br',
    url='https://github.com/vintasoftware/django-zombodb',
    packages=[
        'django_zombodb',
    ],
    include_package_data=True,
    install_requires=[
        'elasticsearch-dsl>=6.3.1',
        'elasticsearch>=6.3.1',
        'psycopg2>=2.7.7',
    ],
    zip_safe=False,
    keywords='django-zombodb',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
