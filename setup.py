from setuptools import setup, find_packages

setup(
    name='cmdz',
    version='2026.01.17.082839',
    author='jererc',
    author_email='jererc@gmail.com',
    url='https://github.com/jererc/cmdz',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.10',
    install_requires=[
        # 'vbox @ git+https://github.com/jererc/vbox.git@main#egg=vbox',
        'vbox @ https://github.com/jererc/vbox/archive/refs/heads/main.zip',
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
            'stopvms=cmdz.stopvms:main',
            'sleep=cmdz.sleep:main',
            'shutdown=cmdz.shutdown:main',
        ],
    },
    include_package_data=True,
)
