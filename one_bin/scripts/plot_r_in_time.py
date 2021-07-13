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

def get_value(data, value):
    if(value == 'value'):
        return data[1]
    elif(value == 'up'):
        return data[1]-data[0]
    elif(value == 'down'):
        return data[2]-data[1]
    else:
        print 'argument need to be "value", "up" or "down"'

def get_global(input_json, value):
    tmp  = json.dumps(input_json[0])
    data = json.loads(tmp)
    return get_value(data['fit'], value)

bin_content    = []
bin_error_up   = []
bin_error_down = []

syst_name       = [] 
syst_content    = []
syst_error_up   = []
syst_error_down = []

for i in range(nBin):
    directory = './impacts/'+year+'/'+str(i)+'/'+asimov+'/'+observable+'_impacts'+str(i)+'.json'
    with open(directory) as json_file:
        data = json.load(json_file)
        bin_content.append(get_global(data['POIs'], 'value'))
        bin_error_up.append(get_global(data['POIs'], 'up'))
        bin_error_down.append(get_global(data['POIs'], 'down'))


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


h_name = observable
if asimov != '':
    h_name += '_'+asimov
h = TH1F(h_name, h_name, nBin, 0, nBin)
for i in range(nBin):
    h.SetBinContent(i+1, r_values[i][1])
    h.SetBinError(i+1, r_values[i][3])
    print 'r'+str(i)+' = '+str(r_values[i][1])+' -'+str(r_values[i][2])+' +'+str(r_values[i][3])

print ' >> save rootfile'

## Diff plots 

h_diff_name = 'diff_'+observable
if asimov != '':
    h_diff_name += '_'+asimov
h_diff = TH1F(h_diff_name, h_diff_name, nBin, 0, nBin)
h_uncor = TH1F(h_diff_name+'_uncorrelated', h_diff_name+'_uncorrelated', nBin, 0, nBin)
h_cor = TH1F(h_diff_name+'_correlated', h_diff_name+'_correlated', nBin, 0, nBin)
for i in range(nBin):
    content_value = r_values[i][1] - bin_content[i]
    error_value   = np.sqrt(r_values[i][3]*r_values[i][3] + bin_error_up[i]*bin_error_up[i]) 
    h_uncor.SetBinContent(i+1, r_values[i][1])
    h_uncor.SetBinError(i+1, r_values[i][3])
    h_cor.SetBinContent(i+1, bin_content[i])
    h_cor.SetBinError(i+1, bin_error_up[i])
    h_diff.SetBinContent(i+1, content_value)
    h_diff.SetBinError(i+1, error_value)


## Save plots

output_file = TFile('./results/histograms_24bins_time_'+year+'.root', 'UPDATE')
for l in output_file.GetListOfKeys():
    if l.GetName() == h_name:
        output_file.Delete(h_name+';1')
    elif l.GetName() == h_diff_name:
        output_file.Delete(h_diff_name+';1')
    elif l.GetName() == h_diff_name+'_uncorrelated':
        output_file.Delete(h_diff_name+'_uncorrelated'+';1')
    elif l.GetName() == h_diff_name+'_correlated':
        output_file.Delete(h_diff_name+'_correlated'+';1')
h.Write()
h_diff.Write()
h_uncor.Write()
h_cor.Write()
output_file.Close()
'''
c = TCanvas()
h_uncor.SetMinimum(0)
h_uncor.Draw()
h_cor.SetLineColor(1)
h_cor.Draw("SAME")
c.SaveAs("delta_r.png")
'''
    
