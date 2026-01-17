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
).setup_venv()
Bootstrapper(name='cmdz').setup_script_shortcut('sleep', args=['cmdz.sleep'])
Bootstrapper(name='cmdz').setup_script_shortcut('shutdown', args=['cmdz.shutdown'])
