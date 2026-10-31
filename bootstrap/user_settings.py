PURGE_PATHS = [
    '~/tmp/*',
    '~/.local/share/Trash/files/*',
    '~/.local/share/Trash/info/*',
    '~/.cache/pip',
    '~/.cache/uv',
    '~/.cache/BraveSoftware',
    '~/.vscode-server',
    '~/work/**/dist/*.tar',
    '~/work/**/dist/*.tar.gz',
]
# Available: apt, docker, journal, npm, snap.
# docker also removes all unused images and volumes.
ENABLED_CLEANERS = ['journal', 'apt', 'docker', 'snap', 'npm']
# Stopped while zeroing free space, restarted afterwards.
STOP_PROCESSES = ['megasync']
# One directory per filesystem to zero, must be on disk (not tmpfs).
ZERO_DIRS = ['~']
