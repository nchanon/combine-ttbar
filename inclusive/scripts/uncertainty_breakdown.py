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
#parser.add_argument('year', help='year of samples')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
#asimov = args.asimov
#year = args.year

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

list_asimov = ['asimov','data']
list_years = ['2016','2017','Comb']

for asimov in list_asimov:
    for year in list_years:

        cmd1 = 'combine -M MultiDimFit -n .nominal_'+year+'_'+asimov+' --robustFit 1 '
        cmd1 += ' -d inputs/'+observable+'_inclusive_workspace_'+year+'.root '
        cmd1 += asimov_param(asimov)
        cmd1 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd1 += ' --algo grid --points '+str(npoints)+' '

        cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+'_'+asimov+' --robustFit 1 '
        cmd2 += ' -d inputs/'+observable+'_inclusive_workspace_'+year+'.root '
        cmd2 += asimov_param(asimov)
        cmd2 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd2 += ' --saveWorkspace'

        cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+year+'_'+asimov+'.MultiDimFit.mH120.root -n .freezeall_'+year+'_'+asimov+' '
        cmd3 += asimov_param(asimov)
        cmd3 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1 '
        cmd3 += ' --algo grid --points '+str(npoints*10)+' '
        cmd3 += ' --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

        cmd5 = "python plot1DScan.py higgsCombine.nominal_"+year+'_'+asimov+".MultiDimFit.mH120.root --others 'higgsCombine.freezeall_"+year+'_'+asimov+".MultiDimFit.mH120.root:FreezeAll:2' -o freeze_all_"+year+"_"+asimov+" "
        cmd5  += "--POI "+rbin
        cmd5 += " --main-label "
        if (asimov=='asimov'): cmd5 += 'Asimov'
	else: cmd5 += 'Data'
        cmd5 += " --breakdown Syst,Stat "
	cmd5 += " -o impacts/"+year+"/UncertaintyBreakdown_"+observable+"_"+year+"_"+asimov+"_"+rbin
        cmd5 += " > impacts/"+year+"/uncertainty_breakdown_"+observable+"_"+year+'_'+asimov+'_'+rbin+".log"

        cmd6 = 'cp freeze_all_'+year+'_'+asimov+'.pdf impacts/'+year+'/'
        #if (asimov == 'asimov'): cmd6 += asimov+'/'
        cmd6 += 'UncertaintyBreakdown_'+observable+"_"+year+'_'+asimov+'_'+rbin+'.pdf'

        if (doPlotsOnly==False):
            print cmd1
            os.system(cmd1)
            print cmd2
            os.system(cmd2)
            print cmd3
            os.system(cmd3)
            print cmd5
            os.system(cmd5)
            print cmd6
            os.system(cmd6)


bestval = []
unc_syst_pos = []
unc_syst_neg  = []

rate_total = []
rate_syst = []
rate_stat = []

for asimov in list_asimov:
    for year in list_years:

        file = open('impacts/'+year+'/uncertainty_breakdown_'+observable+"_"+year+'_'+asimov+'_'+rbin+'.log')

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

	fRes = TFile("higgsCombine.nominal_"+year+'_'+asimov+".MultiDimFit.mH120.root","READ")
	tRes = fRes.Get("limit")
	tRes.GetEvent(0)
	mu = tRes.r
	bestval.append(mu)

        rate_total.append([mu,mu-unc_total_neg[-1], unc_total_pos[-1]-mu])
        rate_stat.append([mu,mu-unc_noSyst_neg[-1], unc_noSyst_pos[-1]-mu])

print rate_total
print rate_stat

sys.stdout = open('impacts/'+year+'/Latex_UncertaintyBreakdown_'+observable+'.txt', 'w')

i = 0
for asimov in list_asimov:
    for year in list_years:
	
	text = asimov+' '+year+': $\mu='
	text += str(round(bestval[i], 3))+'^{+' + str(round(unc_total_pos[i]-bestval[i], 3)) + '}_{-' + str(round(bestval[i]-unc_total_neg[i], 3))+ '} '
	syst_up = math.sqrt((unc_total_pos[i]-bestval[i])*(unc_total_pos[i]-bestval[i])-(unc_noSyst_pos[i]-bestval[i])*(unc_noSyst_pos[i]-bestval[i])) 
	syst_down = math.sqrt((unc_total_neg[i]-bestval[i])*(unc_total_neg[i]-bestval[i])-(unc_noSyst_neg[i]-bestval[i])*(unc_noSyst_neg[i]-bestval[i]))
	text += '=  '+ str(round(bestval[i], 3))+'^{+' + str(round(syst_up, 3)) + '}_{-' + str(round(syst_down, 3))+ '}$(syst)'
	text += '$^{+' + str(round(unc_noSyst_pos[i]-bestval[i], 3)) + '}_{-' + str(round(bestval[i]-unc_noSyst_neg[i], 3))+ '}$(stat)'
	print text
	i=i+1

sys.stdout.close()


exit()

#for j in range(ntimebin): 
#    rbin = pois[j]

#    cmd1 = 'combine -M MultiDimFit -n .nominal_'+year+' --robustFit 1 '
#    cmd1 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
#    cmd1 += asi
#    cmd1 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs=1'
#    cmd1 += ' --algo grid --points '+str(npoints)+' '
#
#    cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+' --robustFit 1 '
#    cmd2 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
#    cmd2 += asi
#    cmd2 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs=1'
#    cmd2 += '  --saveWorkspace'
#
#    cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+year+'.MultiDimFit.mH120.root -n .freezeall_'+year+' '
#    cmd3 += asi
#    cmd3 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs=1 '
#    cmd3 += '--algo grid --points '+str(npoints*10)+' '
#    cmd3 += '--freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'
#
#    cmd5 = "python plot1DScan.py higgsCombine.nominal_"+year+".MultiDimFit.mH120.root --others 'higgsCombine.freezeall_"+year+".MultiDimFit.mH120.root:FreezeAll:2' -o freeze_all_"+year+" "
#    cmd5  += "--POI "+rbin
#    cmd5 += " --main-label "
#    if (asimov=='asimov'): cmd5 += 'Asimov'
#    cmd5 += " --breakdown Syst,Stat > impacts/"+year+"/uncertainty_breakdown_"+rbin+".log"
#
#    cmd6 = 'cp freeze_all_'+year+'.pdf impacts/'+year+'/'
#    #if (asimov == 'asimov'): cmd6 += asimov+'/'
#    cmd6 += 'UncertaintyBreakdown_'+year+'_'+rbin+'.pdf'

#    if (doPlotsOnly==False):
#        print cmd1
#        os.system(cmd1)
#        print cmd2
#        os.system(cmd2)
#        print cmd3
#        os.system(cmd3)
#        print cmd5
#        os.system(cmd5)
#        print cmd6
#        os.system(cmd6)
    

unc_syst_pos = []
unc_syst_neg  = []

rate_total = []
rate_syst = []
rate_stat = []
for j in range(ntimebin):
    rbin = pois[j]

    file = open('impacts/'+year+'/uncertainty_breakdown_'+year+'_'+asimov+'_'+rbin+'.log')

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

    #unc_syst_pos.append(math.sqrt(unc_total_pos[j]*unc_total_pos[j]-unc_noSyst_pos[j]*unc_noSyst_pos[j]))
    #unc_syst_neg.append(math.sqrt(unc_total_neg[j]*unc_total_neg[j]-unc_noSyst_neg[j]*unc_noSyst_neg[j]))

    rate_total.append([1,1-unc_total_neg[j], unc_total_pos[j]-1])
    rate_stat.append([1,1-unc_noSyst_neg[j], unc_noSyst_pos[j]-1])

print rate_total
print rate_stat

###################
## Plotting
###################

nbin = 0
min_bin = 0
max_bin = 0

legend_coordinates = [0.65, 0.75, 0.87, 0.87]
TH1.SetDefaultSumw2(1)
signal_integral = 0
background_integral_i = []
background_integral = 0
data_integral = 0
syst_up_integral = 0
syst_down_integral = 0
canvas = TCanvas('differential measurment','differential measurment', 800, 700)
canvas.UseCurrentStyle()

def linearized(input, option):
    opt = 0
    if option=='up' :
        opt = 2
    elif option=='down' :
        opt = 1
    else:
        print 'error option'
    foo = []
    for l in input:
        foo.append(l[opt])
    return foo

def squared(list_value):
    somme = 0
    for l in list_value:
        somme += l*l
    return np.sqrt(somme/float(len(list_value)))


################################################################################
## Create Histo 
################################################################################

x = np.array([1 for i in range(24)], dtype='double')
y = np.array([i+0.5 for i in range(24)], dtype='double')

error_left = np.array([0.5 for i in range(24)], dtype='double')
error_right = np.array([0.5 for i in range(24)], dtype='double')

error_tot_up = np.array(linearized(rate_total, 'up'), dtype='double')
error_tot_down = np.array(linearized(rate_total, 'down'), dtype='double')

error_stat_up = np.array(linearized(rate_stat, 'up'), dtype='double')
error_stat_down = np.array(linearized(rate_stat, 'down'), dtype='double')

hist_tot  = TGraphAsymmErrors(24, y, x ,
                          error_left, error_right,
                          error_tot_down, error_tot_up)
hist_tot.SetName('hist_tot')
hist_tot.SetTitle('hist_tot')

hist_stat  = TGraphAsymmErrors(24, y, x ,
                          error_left, error_right,
                          error_stat_down, error_stat_up)
hist_stat.SetName('hist_stat')
hist_stat.SetTitle('hist_stat')

hist_tot.SetLineColor(1)
hist_stat.SetLineColor(2)
hist_tot.SetMarkerColor(1)
hist_stat.SetMarkerColor(2)

################################################################################
## Set Style
################################################################################

is_center=True

hist_tot.GetYaxis().SetRangeUser(0.92,1.08)
hist_tot.GetYaxis().SetTitle('t#bar{t} signal strength #it{#mu}')
hist_tot.GetYaxis().SetRange(0,2)
hist_tot.GetYaxis().SetTitleSize(0.04)
hist_tot.GetYaxis().SetLabelSize(0.04)

hist_tot.GetXaxis().SetRangeUser(0,24)
hist_tot.GetXaxis().SetTitle('sidereal time (h)')
hist_tot.GetXaxis().SetRangeUser(0,24)
hist_tot.GetXaxis().SetTitleSize(0.04)
hist_tot.GetXaxis().SetLabelSize(0.04)

if(is_center):
    hist_tot.GetXaxis().CenterTitle()
    hist_tot.GetYaxis().CenterTitle()

style_histo(hist_tot,   1, 2, 4, 3005, 1,20)


################################################################################
## Draw stuff
################################################################################

hist_tot.Draw("AP")
hist_stat.Draw("PSAME")

legend = TLegend(0.5,0.93,0.9,0.8)
legend.SetHeader('Asimov test '+year, 'C')
legend.AddEntry(hist_stat.GetName(), 'Stat', 'lep')
legend.AddEntry(hist_tot.GetName(), 'Stat+Syst', 'lep')
legend.Draw("SAME")


if(year=='2016'):
    tdr.cmsPrel(35900., 13.)
elif(year=='2017'):
    tdr.cmsPrel(41530., 13.)
elif(year=='Comb'):
    tdr.cmsPrel(77400,13.)


################################################################################
## Save
################################################################################

resultname = './impacts/'+year+'/differential_time_breakdown_'+year

rootfile_output = TFile(resultname+'.root', "RECREATE")
canvas.Write()
#canvas.SaveAs(resultname+'.png')
canvas.SaveAs(resultname+'.pdf')

