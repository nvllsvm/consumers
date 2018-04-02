import sys

import setuptools

if 'test' in sys.argv:
    setup_requires = ['pytest-runner']
elif 'build_sphinx' in sys.argv:
    setup_requires = ['sphinx', 'sphinx_rtd_theme']
else:
    setup_requires = []

setuptools.setup(
    name='consumers',
    version='0.6.1',
    description='A simple, flexible way to parallelize processing in Python.',
    long_description=open('README.rst').read(),
    author='Andrew Rabert',
    author_email='arabert@nullsum.net',
    url='https://github.com/nvllsvm/consumers',
    license='Apache 2.0',
    packages=['consumers'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only'
    ),
    setup_requires=setup_requires,
    tests_require=['pytest', 'pytest-cov'],
    zip_safe=True
)
