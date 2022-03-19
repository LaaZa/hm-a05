import urllib.request
import zipfile
import shutil
import os
from pathlib import Path

print('Starting downloading plugins...')

repo = 'https://github.com/LaaZa/hm-a05-plugins/archive/refs/heads/main.zip'

file = 'plugins.zip'

plugins = set()

try:

    with urllib.request.urlopen(repo) as resp, open(file, 'wb') as f:
        shutil.copyfileobj(resp, f)

    with zipfile.ZipFile(file) as z:
        for zz in z.infolist():
            if zz.filename[-1] == '/':
                continue
            path = Path(zz.filename)
            try:
                directory = path.relative_to('hm-a05-plugins-main/plugins/').parent
                zz.filename = path.name
                z.extract(zz, 'plugins' / directory)
                plugins.add(directory.parts[-1])
            except ValueError:
                pass

except Exception as e:
    print(f'something failed {e}')

os.remove(file)

print('Succesfully downloaded plugins:')
for p in sorted(plugins):
    print(p)
