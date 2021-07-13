import os, sys
import argparse 

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('workspace', help='display your input workspace')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
workspace = args.workspace
asimov = args.asimov

pois = []
for i in range(24):
    pois.append('r_'+str(i))

asi = ''
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'    
    print ''
    asi = ' --setParameters '
    for i in range(24):
        asi += pois[i]+'=1'
        if i != 23:
            asi += ','
    asi += ' -t -1 '

###################
## Core
###################

cmd = 'combine -M MultiDimFit '
cmd += asi
cmd += ' -d '+workspace
cmd += ' --algo=singles '

print cmd
os.system(cmd)
