import os, sys
import argparse 

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov

asi = ''
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'    
    print ''
    asi = '--expectSignal 1 -t -1'


###################
## Core
###################

cmd1 = 'combineTool.py -M Impacts -n .impact_'+year+' -d ./inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '+asi+' -m 125 '
cmd2 = cmd1
cmd3 = cmd1

cmd1 += '--doInitialFit --robustFit 1'
cmd2 += '--robustFit 1 --doFits'
cmd3 += '-o '+observable+'_impacts_'+year+'.json '

cmd4 = 'plotImpacts.py -i '+observable+'_impacts_'+year+'.json -o '+observable+'_impacts_'+year

os.system(cmd1)
os.system(cmd2)
os.system(cmd3)
os.system(cmd4)

cmdnew = 'mv '+observable+'_impacts_'+year+'.pdf impacts/'+year+'/'+observable+'_differential_impacts_'+ year+'.pdf'
os.system(cmdnew)
