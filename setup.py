from setuptools import setup, find_packages

setup(
    name='cmdz',
    version='2025.10.20.081211',
    author='jererc',
    author_email='jererc@gmail.com',
    url='https://github.com/jererc/cmdz',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.10',
    install_requires=[
    ],
    extras_require={
        'dev': ['flake8', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'cleandrive=cmdz.cleandrive:main',
            'cleanfiles=cmdz.cleanfiles:main',
            'findsaves=cmdz.findsaves:main',
            'gitcp=cmdz.gitcp:main',
        ],
    },
    include_package_data=True,
)
