import os
import urllib.request

url = 'https://raw.githubusercontent.com/jererc/svcutils/refs/heads/main/svcutils/bootstrap.py'
exec(urllib.request.urlopen(url).read().decode('utf-8'))
Bootstrapper(
    name='cmdz',
    install_requires=[
        # 'git+https://github.com/jererc/cmdz.git',
        'cmdz @ https://github.com/jererc/cmdz/archive/refs/heads/main.zip',
    ],
    force_reinstall=True,
    shortcuts=[
        {'name': 'sleep', 'args': ['cmdz.sleep'], 'headless': False},
        {'name': 'shutdown', 'args': ['cmdz.shutdown'], 'headless': False},
    ],
)
