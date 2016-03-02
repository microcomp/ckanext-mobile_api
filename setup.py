from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
    name='ckanext-mobile_api',
    version=version,
    description="Mobile application API",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Janos Farkas',
    author_email='Farkas@microcomp.sk',
    url='',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.mobile_api'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
        mobile_api=ckanext.mobile_api.plugin:MobileApi
    ''',
)
