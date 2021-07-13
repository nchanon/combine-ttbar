import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('wilson', help='display your wilson coefficient')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
wilson = args.wilson
asimov = args.asimov

cmd_input = './inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root'

asimov_param = []
if asimov == 'asimov':
    print ''
    print '### Asimov test ###'
    print ''
    asimov_param = ['--setParameters',wilson+'=0','-t','-1']


## Methodes

def getValues(line):
    r = line[0]
    x = float(line[2])
    uncertainty = line[3].split('/')
    down = float(uncertainty[0])
    up   = float(uncertainty[1])
    return [r,x,down,up]


## Fit


print '-------------------'
print ' >>> Fit '+wilson
print '-------------------'
    

cmd = ['combine', 
       '-M', 
       'MultiDimFit',
       '--algo=singles', 
       cmd_input]
for l in asimov_param:
    cmd.append(l)

output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

## Core
	
fit_values = []

output = output.splitlines()
output.sort()
for line in output:
    if line.find(wilson+' :') != -1:
        print line 
        fit_values.append(getValues(line.split()))


