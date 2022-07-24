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

cmd  = ' text2workspace.py '
cmd += ' inputs/'+year+'/'+observable+'_'+wilson+'_datacard.txt '
cmd += ' -P HiggsAnalysis.CombinedLimit.TimePhysicsModel:timeModel '
cmd += ' --PO '+wilson
cmd += ' -o ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root'

print cmd
os.system(cmd)
