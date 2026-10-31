from setuptools import setup, find_packages

setup(
    name='cmdz',
    version='2026.09.05.055948',
    author='jererc',
    author_email='jererc@gmail.com',
    url='https://github.com/jererc/cmdz',
    packages=find_packages(exclude=['tests*']),
    python_requires='>=3.10',
    install_requires=[
        # 'svcutils @ git+https://github.com/jererc/svcutils.git@main#egg=svcutils',
        'svcutils @ https://github.com/jererc/svcutils/archive/refs/heads/main.zip',
        # 'vbox @ git+https://github.com/jererc/vbox.git@main#egg=vbox',
        'vbox @ https://github.com/jererc/vbox/archive/refs/heads/main.zip',
    ],
    extras_require={
        'dev': ['flake8', 'pytest'],
    },
    entry_points={
        'console_scripts': [
            'cleanfilenames=cmdz.cleanfilenames:main',
            'findsaves=cmdz.findsaves:main',
            'pause=cmdz.pause:main',
            'purgevm=cmdz.purgevm:main',
        ],
    },
    include_package_data=True,
)
