import setuptools


setuptools.setup(
    name='consumers',
    version='0.1.0',
    description='A simple, flexible way to parallelize processing in Python.',
    long_description=open('README.rst').read(),
    author='Andrew Rabert',
    author_email='arabert@nullsum.net',
    url='https://github.com/nvllsvm/consumers',
    license='Apache 2.0',
    py_modules=['consumers'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ),
    zip_safe=True
)
