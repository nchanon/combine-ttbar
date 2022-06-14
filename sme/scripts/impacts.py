import os, sys
import argparse 

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('wilson', help='wilson coef')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
wilson = args.wilson
asimov = args.asimov

asi = ''
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'    
    print ''
    asi = '--setParameters '+wilson+'=0 -t -1'

test = False

###################
## Core
###################

print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'
    

#cmd = 'text2workspace.py ./inputs/'+year+'/'+observable+'_unrolled_datacard.txt '
#cmd += '-o '+observable+'_impacts.root'


cmd1 = 'combineTool.py -M Impacts -n .Impact_'+year+'_'+wilson +' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root '+asi+' -m 125 '
cmd2 = cmd1
cmd3 = cmd1
cmd1 += '--doInitialFit --robustFit 1'
cmd2 += '--robustFit 1 --doFits'
cmd3 += '-o '+observable+'_'+wilson+'_impacts_'+year+'.json '

cmd4 = 'plotImpacts.py -i '+observable+'_'+wilson+'_impacts_'+year+'.json -o '+observable+'_'+wilson+'_impacts_'+year+' --POI '+wilson
        

os.system(cmd1)
os.system(cmd2)
os.system(cmd3)
os.system(cmd4)


if asimov == 'asimov':
    os.system('mv '+observable+'_'+wilson+'_impacts_'+year+'* impacts/'+year+'/asimov/')
    #os.system('mv *.png impacts/'+year+'/asimov/')
    os.system('mv *.Impact_'+year+'_'+wilson+'*.root impacts/'+year+'/asimov/')
    #os.system('mv *.out impacts/'+year+'/asimov/')
    #os.system('mv impacts/'+year+'/asimov/'+observable+'_'+wilson+'_impacts.pdf impacts/'+year+'/asimov/'+observable+'_'+wilson+'_impacts_'+year+'.pdf')
else:
    os.system('mv '+observable+'_'+wilson+'_impacts_'+year+'* impacts/'+year+'/')
    #os.system('mv *.png impacts/'+year+'/')
    os.system('mv *.Impacts_'+year+'_'+wilson+'*.root impacts/'+year+'/')
    #os.system('mv *.root impacts/'+year+'/')
    #os.system('mv *.out impacts/'+year+'/')
    
