import os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('wilson', help='display your wilson coefficient')

args = parser.parse_args()
observable = args.observable
year = args.year
wilson = args.wilson

os.system('bash python/cp.sh')

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

if wilson in wilson_list_all:
    cmd  = ' text2workspace.py '
    cmd += ' inputs/'+year+'/'+observable+'_'+wilson+'_datacard.txt '
    cmd += ' -P HiggsAnalysis.CombinedLimit.TimePhysicsModel:timeModel '
    cmd += ' --PO '+wilson
    cmd += ' -o ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root'
else:
    wilson_list = wilson.split(",")
    cmd  = ' text2workspace.py '
    cmd += ' inputs/'+year+'/'+observable+'_sme_all_datacard.txt '
    cmd += ' -P HiggsAnalysis.CombinedLimit.TimePhysicsModelMultiple:timeModel '
    cmd += ' --PO '+wilson
    wilson_string = ''
    for w in wilson_list:
        wilson_string += w
	if w!=wilson_list[-1]:
	    wilson_string += '_'
    cmd += ' -o ./inputs/'+observable+'_'+wilson_string+'_workspace_'+year+'.root'


print cmd
os.system(cmd)
