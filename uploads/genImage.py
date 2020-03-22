'''
genImage.py <sub_directory>
'''
from sys import argv
from glob import glob
from os.path import basename

if len(argv) != 2:
    print(__doc__)
    exit()

files = []

for ext in ('gif', 'png', 'jpg'):
    files.extend(
        glob('{}/*.{}'.format(argv[1], ext), recursive=True)
    )

files = sorted(files)

for i, f in enumerate(files):
    n = basename(f).split('.')[0]
    print('[![{0}][{1}]][{1}]\n'.format(n, i))

print('')

for i, f in enumerate(files):
    print('[{}]: {{{{ site.baseurl }}}}/uploads/{}'.format(i, f))
