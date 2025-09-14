from setuptools import setup, find_packages

setup(
    name='cmdz',
    version='2025.09.14.114023',
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
            'gitcp=cmdz.gitcp:main',
        ],
    },
    include_package_data=True,
)
