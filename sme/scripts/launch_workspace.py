import os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')


args = parser.parse_args()
observable = args.observable
year = args.year


## Methodes

def getValues(line):
    r = line[0]
    x = float(line[2])
    uncertainty = line[3].split('/')
    down = float(uncertainty[0])
    up   = float(uncertainty[1])
    return [r,x,down,up]


wilson_list_XX = [
    'cLXX',
    'cRXX',
    'cXX',
    'dXX'
]
wilson_list_XY = [
    'cLXY',
    'cRXY',
    'cXY',
    'dXY'
]
wilson_list_XZ = [
    'cLXZ',
    'cRXZ',
    'cXZ',
    'dXZ'
]
wilson_list_YZ = [
    'cLYZ',
    'cRYZ',
    'cYZ',
    'dYZ'
]

wilson_list_all = [
    'cLXX',
    'cRXX',
    'cXX',
    'dXX',
    'cLXY',
    'cRXY',
    'cXY',
    'dXY',
    'cLXZ',
    'cRXZ',
    'cXZ',
    'dXZ',
    'cLYZ',
    'cRYZ',
    'cYZ',
    'dYZ'
]

wilson = raw_input('choose wilson benshmark (XX, XY, XZ, YZ, all) : ')
if wilson == 'XX':
    wilson_list = wilson_list_XX
elif wilson == 'XY':
    wilson_list = wilson_list_XY
elif wilson == 'XZ':
    wilson_list = wilson_list_XZ
elif wilson == 'YZ':
    wilson_list = wilson_list_YZ
elif wilson == 'all':
    wilson_list = wilson_list_all
else:
    print 'wrong benchmark !'
    exit()

for l in wilson_list:
    os.system('python scripts/workspace_creator.py '+observable+' '+year+' '+l)
