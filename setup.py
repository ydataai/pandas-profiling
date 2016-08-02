import os

__location__ = os.path.dirname(__file__)
print(__location__, __file__)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pandas-profiling',
    version='1.1.0',
    author='Jos Polfliet',
    author_email='jos.polfliet+panpro@gmail.com',
    packages=['pandas_profiling'],
    #package_dir={'pandas_profiling': './pandas_profiling'},
    url='http://github.com/jospolfliet/pandas-profiling',
    license='MIT',
    description='Generate profile report for pandas DataFrame',
    install_requires=[
        "pandas>=0.16",
        "matplotlib>=1.4",
        "seaborn",
        "scikit-learn",
        "six"
    ],
    include_package_data = True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Framework :: IPython',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'

    ],
    keywords='pandas data-science data-analysis python jupyter ipython',

)
