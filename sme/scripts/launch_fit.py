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

def asimov_param(w):
    if asimov == 'asimov':
        return ['--setParameters',w+'=0','-t','-1']
    return []

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
    


if asimov == 'asimov':
    print ''
    print '### Asimov test ###'
    print ''

cmd_input = []
for l in wilson_list:
    cmd_input.append('./inputs/'+observable+'_'+l+'_workspace_'+year+'.root')

## Methodes

def getValues(line):
    r = line[0]
    x = float(line[2])
    uncertainty = line[3].split('/')
    down = float(uncertainty[0])
    up   = float(uncertainty[1])
    return [r,x,down,up]


## Fit

fit_values = []

for i in range(len(cmd_input)):

    print '-------------------'
    print ' >>> Fit '+wilson_list[i]
    print '-------------------'

    cmd = ['combine', 
           '-M', 
           'MultiDimFit',
           '--algo=singles', 
           cmd_input[i]]
    for a in asimov_param(wilson_list[i]):
        cmd.append(a)

    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    output = output.splitlines()
    output.sort()
    for line in output:
        if line.find(wilson_list[i]+' :') != -1:
            print line 
            fit_values.append(getValues(line.split()))

## Core
	
text = ''
for l in fit_values:
    for i in l:
        text += str(i) + ' '
    text += '\n'

outname = './results/fit_'+observable+'_'+year
if asimov == 'asimov':
    outname += '_'+asimov

file = open(outname+'.txt','w') 
file.write(text) 
file.close()

