#import cern_sso

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='python-cern-sso',

    # Uses semver
    version='1.2.4',

    description='Cern Single-Single-Sign-On driver',
    long_description=long_description,

    url='https://gitlab.cern.ch/astjerna/cern-sso-python',

    # Author details
    author='Albin Stjerna',
    author_email='albin.stjerna@cern.ch',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='authentication sso cern',

    py_modules=["cern_sso"],

    install_requires=['requests',
                      'lxml',
                      'requests-kerberos',
                      'six'],

    scripts=['bin/cern-get-sso-cookie.py']
)
