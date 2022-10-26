import os, sys
sys.path.append('./')

import math
import argparse
import subprocess

import numpy as np

from tools.style_manager import *

from ROOT import TFile, TH1, TCanvas, TH1F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

import tools.tdrstyle as tdr
tdr.setTDRStyle()

doPlotsOnly = False

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('timebin', help='display the time bin')
#parser.add_argument('year', help='year of samples')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
timebin = int(args.timebin)
#asimov = args.asimov
#year = args.year
stimebin="";
if (timebin==-1):
     stimebin = "_puold";
if (timebin==-2):
     stimebin = "_punew";
if (timebin==-3):
     stimebin = "_puinc";
if (timebin>=0):
     stimebin = "_put"+str(timebin);    

#ntimebin = 24

#pois = []
#for i in range(24):
#    pois.append('r_'+str(i))

#asi = ''
#sasimov=''
def asimov_param(asimov):
    if asimov == 'asimov':
        return '--expectSignal 1 -t -1'
    else: 
	return ''
        #print '################'
        #print '# Asimov test : '
        #print '################'
        #print ''
        #sasimov = '_asimov'
    #else:
    #    sasimov = '_data'

#asi = ''
#if asimov == 'asimov':
#   print '################'
#    print '# Asimov test : '
#    print '################'
#    print ''
#    asi = ' --setParameters '
#    for i in range(24):
#        asi += pois[i]+'=1'
#        if i != 23:
#            asi += ','
#    asi += ' -t -1 '

unc_total_pos = []
unc_total_neg = []
#unc_noMCStats_pos = []
#unc_noMCStats_neg = []
unc_noSyst_pos = []
unc_noSyst_neg = []

rbin='r'
r_range='0.8,1.2'
npoints=20


###################
## Core
###################

optim = ' --cminDefaultMinimizerStrategy 0'
#optim = ' --robustFit 1 '

list_asimov = ['asimov','data']
list_years = ['2016','2017','Comb']
#list_years = ['2016']

for asimov in list_asimov:
    for year in list_years:

        cmd1 = 'combine -M MultiDimFit -n .nominal_'+year+stimebin+'_'+asimov+optim
        cmd1 += ' -d inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root '
        cmd1 += asimov_param(asimov)
        cmd1 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd1 += ' --algo grid --points '+str(npoints)+' '

        cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+stimebin+'_'+asimov+optim
        cmd2 += ' -d inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root '
        cmd2 += asimov_param(asimov)
        cmd2 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd2 += ' --saveWorkspace'

        cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+year+stimebin+'_'+asimov+'.MultiDimFit.mH120.root -n .freezeall_'+year+stimebin+'_'+asimov+' '
        cmd3 += asimov_param(asimov)
        cmd3 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1 '
        cmd3 += ' --algo grid --points '+str(npoints*10)+' '
        cmd3 += ' --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

        cmd5 = "python plot1DScan.py higgsCombine.nominal_"+year+stimebin+'_'+asimov+".MultiDimFit.mH120.root --others 'higgsCombine.freezeall_"+year+stimebin+'_'+asimov+".MultiDimFit.mH120.root:FreezeAll:2' -o freeze_all_"+year+"_"+asimov+" "
        cmd5  += "--POI "+rbin
        cmd5 += " --main-label "
        if (asimov=='asimov'): cmd5 += 'Asimov'
	else: cmd5 += 'Data'
        cmd5 += " --breakdown Syst,Stat "
	cmd5 += " -o impacts/"+year+"/UncertaintyBreakdown_"+observable+"_"+year+stimebin+"_"+asimov+"_"+rbin
        cmd5 += " > impacts/"+year+"/uncertainty_breakdown_"+observable+"_"+year+stimebin+'_'+asimov+'_'+rbin+".log"

        #cmd6 = 'cp freeze_all_'+year+stimebin+'_'+asimov+'.pdf impacts/'+year+'/'
        #if (asimov == 'asimov'): cmd6 += asimov+'/'
        #cmd6 += 'UncertaintyBreakdown_'+observable+"_"+year+stimebin+'_'+asimov+'_'+rbin+'.pdf'

        if (doPlotsOnly==False):
            print cmd1
            os.system(cmd1)
            print cmd2
            os.system(cmd2)
            print cmd3
            os.system(cmd3)
            print cmd5
            os.system(cmd5)
            #print cmd6
            #os.system(cmd6)


bestval = []
unc_syst_pos = []
unc_syst_neg  = []

rate_total = []
rate_syst = []
rate_stat = []

for asimov in list_asimov:
    for year in list_years:

        file = open('impacts/'+year+'/uncertainty_breakdown_'+observable+"_"+year+stimebin+'_'+asimov+'_'+rbin+'.log')

        i=0
        for line in file:
            uncert = 0
            for word in line.split():
                print(str(i)+' '+word)
                if (i==4): unc_total_neg.append(float(word[:-1]))
                if (i==6): unc_total_pos.append(float(word[:-1]))
                if (i==20): unc_noSyst_neg.append(float(word[:-1]))
                if (i==22): unc_noSyst_pos.append(float(word[:-1]))
                #if (i==36): unc_noSyst_neg.append(float(word[:-1]))
                #if (i==38): unc_noSyst_pos.append(float(word[:-1]))
                i = i+1

        file.close()

	fRes = TFile("higgsCombine.nominal_"+year+stimebin+'_'+asimov+".MultiDimFit.mH120.root","READ")
	tRes = fRes.Get("limit")
	tRes.GetEvent(0)
	mu = tRes.r
	bestval.append(mu)

        rate_total.append([mu,mu-unc_total_neg[-1], unc_total_pos[-1]-mu])
        rate_stat.append([mu,mu-unc_noSyst_neg[-1], unc_noSyst_pos[-1]-mu])

print rate_total
print rate_stat

print 'Write '+'impacts/'+year+'/Latex_UncertaintyBreakdown_'+observable+stimebin+'.txt'
sys.stdout = open('impacts/'+year+'/Latex_UncertaintyBreakdown_'+observable+stimebin+'.txt', 'w')

i = 0
for asimov in list_asimov:
    for year in list_years:
	
	text = asimov+' '+year+stimebin+': $\mu='
	text += str(round(bestval[i], 3))+'^{+' + str(round(unc_total_pos[i]-bestval[i], 3)) + '}_{-' + str(round(bestval[i]-unc_total_neg[i], 3))+ '} '
	syst_up = math.sqrt((unc_total_pos[i]-bestval[i])*(unc_total_pos[i]-bestval[i])-(unc_noSyst_pos[i]-bestval[i])*(unc_noSyst_pos[i]-bestval[i])) 
	syst_down = math.sqrt((unc_total_neg[i]-bestval[i])*(unc_total_neg[i]-bestval[i])-(unc_noSyst_neg[i]-bestval[i])*(unc_noSyst_neg[i]-bestval[i]))
	text += '=  '+ str(round(bestval[i], 3))+'^{+' + str(round(syst_up, 3)) + '}_{-' + str(round(syst_down, 3))+ '}$(syst)'
	text += '$^{+' + str(round(unc_noSyst_pos[i]-bestval[i], 3)) + '}_{-' + str(round(bestval[i]-unc_noSyst_neg[i], 3))+ '}$(stat)'
	print text
	i=i+1

sys.stdout.close()


exit()

