import os, sys
import argparse 
import subprocess
import json 
import numpy as np

from ROOT import TH1F, TFile, TCanvas

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
asimov = args.asimov
year = args.year

if asimov != 'asimov':
    asimov = ''

nBin = 24
name = observable+'_'+str(nBin)+'bins_'+year

###################
## Functions
###################

def getValues(line):
    r = line[0]
    x = float(line[2])
    uncertainty = line[3].split('/')
    down = float(uncertainty[0])
    up   = float(uncertainty[1])
    return [r,x,down,up]
    
###################
## Core
###################

print ' >> launch combine'

cmd = ['python', 
       './scripts/launch_multidimfit.py', 
       './inputs/combine_'+name+'_workspace.root' ,
       asimov]
output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
os.system('rm combine_logger.out')
os.system('rm higgsCombineTest.MultiDimFit.mH120.root')

print ' >> plot generation'

r_values = []
output = output.splitlines()
output.sort()
for line in output:
    for i in range(nBin):
        if line.find('r_'+str(i)+' ') != -1:
            r_values.append(getValues(line.split()))

## Diff plots 

h_diff_name = 'diff_'+observable
if asimov != '':
    h_diff_name += '_'+asimov
h_uncor = TH1F(h_diff_name+'_uncorrelated', h_diff_name+'_uncorrelated', nBin, 0, nBin)
for i in range(nBin):
    h_uncor.SetBinContent(i+1, r_values[i][1])
    h_uncor.SetBinError(i+1, r_values[i][3])


## Save plots

output_file = TFile('./results/histograms_24bins_time_'+year+'.root', 'UPDATE')
for l in output_file.GetListOfKeys():
    if l.GetName() == h_diff_name+'_uncorrelated':
        output_file.Delete(h_diff_name+'_uncorrelated'+';1')

h_uncor.Write()
output_file.Close()
