# Setup.py for cssaudit
# (c) 2011, Kyle Wanamaker
# Licensed under the GNU GPL v3

from setuptools import setup

setup(
      name='CssAudit',
      packages=['cssaudit',],
      version='0.01a',
      description='A rather basic tool to see if you have excess styles in your CSS stylesheets.',
      author='Kyle Wanamaker (KyleWpppd)',
      author_email='k.dev@klowell.com',
      url='http://github.com/KyleWpppd/css-audit',
      install_requires=['cssutils>=0.9.8a3', ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)'
          'Operating System :: OS Independent'
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Utilities'
          ],

      )
