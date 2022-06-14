import os, sys
import argparse 

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
#asimov = args.asimov


print '-------------------------'
print ' >>> workspace creation '
print '-------------------------'
    
cmd  = ' text2workspace.py '
cmd += ' inputs/'+year+'/'+observable+'_datacard.txt '
#cmd += ' -P HiggsAnalysis.CombinedLimit.TimePhysicsModel:timeModel '
#cmd += ' --PO '+wilson
cmd += ' -o ./inputs/'+observable+'_inclusive_workspace_'+year+'.root'


#cmd = 'text2workspace.py ./inputs/'+year+'/'+observable+'_datacard.txt '
#cmd += '-o '+observable+'_impacts.root'
os.system(cmd)


#cmd1 = 'combineTool.py -M Impacts -d '+observable+'_impacts.root '+asi+' -m 125 '
#cmd2 = cmd1
#cmd3 = cmd1
#cmd1 += '--doInitialFit --robustFit 1'
#cmd2 += '--robustFit 1 --doFits'
#cmd3 += '-o '+observable+'_impacts.json '

#cmd4 = 'plotImpacts.py -i '+observable+'_impacts.json -o '+observable+'_impacts'
        
#os.system(cmd1)
#os.system(cmd2)
#os.system(cmd3)
#os.system(cmd4)


#if asimov == 'asimov':
#    os.system('mv '+observable+'_impacts* impacts/'+year+'/asimov/')
#    os.system('mv *.png impacts/'+year+'/asimov/')
#    os.system('mv *.root impacts/'+year+'/asimov/')
#    os.system('mv *.out impacts/'+year+'/asimov/')
#else:
#    os.system('mv '+observable+'_impacts* impacts/'+year+'/')
#    os.system('mv *.png impacts/'+year+'/')
#    os.system('mv *.root impacts/'+year+'/')
#    os.system('mv *.out impacts/'+year+'/')
    
    
