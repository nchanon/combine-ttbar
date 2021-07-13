import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov


if asimov == 'asimov':
    print ''
    print '### Asimov test ###'
    print ''
else:
    asimov = ''


wilson_list_XX = [
    'fXX_L',
    'fXX_R',
    'fXX_C',
    'fXX_D'
]
wilson_list_XY = [
    'fXY_L',
    'fXY_R',
    'fXY_C',
    'fXY_D'
]
wilson_list_XZ = [
    'fXZ_L',
    'fXZ_R',
    'fXZ_C',
    'fXZ_D'
]
wilson_list_YZ = [
    'fYZ_L',
    'fYZ_R',
    'fYZ_C',
    'fYZ_D'
]

wilson_list_all = [
    'fXX_L',
    'fXY_L',
    'fXZ_L',
    'fYZ_L',
    'fXX_R',
    'fXY_R',
    'fXZ_R',
    'fYZ_R',
    'fXX_C',
    'fXY_C',
    'fXZ_C',
    'fYZ_C',
    'fXX_D',
    'fXY_D',
    'fXZ_D',
    'fYZ_D'
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
    cmd = 'python ./scripts/impacts.py '+observable+' '+year+' '+l+' '+asimov
    os.system(cmd)
    

