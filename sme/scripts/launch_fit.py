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
    'cLXY',
    'cLXZ',
    'cLYZ',
    'cRXX',
    'cRXY',
    'cRXZ',
    'cRYZ',
    'cXX',
    'cXY',
    'cXZ',
    'cYZ',
    'dXX',
    'dXY',
    'dXZ',
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
           '--robustFit',
           '1',
           cmd_input[i]]
    for a in asimov_param(wilson_list[i]):
        cmd.append(a)
    #if (asimov=="" and (wilson_list[i].find("XZ")!=-1 or wilson_list[i].find("YZ")!=-1)):
    cmd.append('--setParameterRanges')
    cmd.append(wilson_list[i]+'=-30,30')

    print cmd

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

outname = './impacts/'+year+'/'+asimov+'/fit_'+observable+'_'+year
if asimov == 'asimov':
    outname += '_'+asimov

file = open(outname+'.txt','w') 
file.write(text) 
file.close()

