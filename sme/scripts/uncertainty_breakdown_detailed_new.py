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

#doPlotsOnly = True
doPlotsOnly = False

###################
## Initialisation
###################


parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('nuisancegroup', help='nuisance group', default='')
parser.add_argument('wilson', help='display your wilson coefficient', default='sme_all')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='asimov')

args = parser.parse_args()
observable = args.observable
wilson_ = args.wilson
asimov = args.asimov
year = args.year
nuisancegroup = args.nuisancegroup


NuisanceGroup = ""
if nuisancegroup=='timeNew_breakdown':
    NuisanceGroup = "time_flat_uncorr_corr"
if nuisancegroup=='time_breakdown':
    NuisanceGroup = "time_flat_uncorr_corr_mcstat"
if nuisancegroup=='kind_breakdown':
    NuisanceGroup = "exp_theory_bkgdnorm_lumi_mcstat"
if nuisancegroup=='exp_breakdown':
    NuisanceGroup = "exp_elec_muon_pu_btag_jec_trigger_prefiring"
if nuisancegroup=='theory_breakdown':
    NuisanceGroup = "theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco"
if nuisancegroup=='putrig_breakdown':
    NuisanceGroup = "pu_trigger"
if nuisancegroup=='putrigsmedecay_breakdown':
    NuisanceGroup = "pu_trigger_smedecay"
if nuisancegroup=='smedecay_breakdown':
    NuisanceGroup = "smedecay"


###################
## Nuisances to be evaluated
###################

list_nuisgroups=[]
list_nuisnames=[]
list_legendnames=[]

#Grouping by kind of nuisances
nuis_lumi_time_flat = 'rgx{lumi_flat_uncor_.*},lumi_flat_cor'
nuis_lumi_time_corr = 'rgx{lumi_stability_.*},rgx{lumi_linearity_.*}'
nuis_lumi = nuis_lumi_time_flat+','+nuis_lumi_time_corr

nuis_bkgdnorm = 'rsignal,rttx,rsingletop,rdibosons,rvjets'

nuis_theory = 'syst_pt_top,rgx{syst_ps_isr.*},rgx{syst_ps_fsr.*},rgx{syst_qcdscale.*},syst_pdfas,hdamp,CP5,erdOn,GluonMove,QCDinspired,mtop'

nuis_theory_pttop = 'syst_pt_top'
nuis_theory_mtop = 'mtop'
nuis_theory_ps = 'rgx{syst_ps_isr.*},rgx{syst_ps_fsr.*}'
nuis_theory_qcdscale = 'rgx{syst_qcdscale_.*}'
nuis_theory_pdfas = 'syst_pdfas'
nuis_theory_hdamp = 'hdamp'
nuis_theory_uetune = 'CP5'
nuis_theory_colorreco = 'erdOn,GluonMove,QCDinspired'

nuis_jec_uncorr = 'rgx{Absolute.*},rgx{BBEC1.*},rgx{RelativeBal.*},rgx{RelativeSample.*}'
nuis_exp_time_flat = 'FlavorPureGluon_jec,FlavorPureBottom_jec,rgx{.*SF_phasespace}' #added phase-space here on 17/01/2023
nuis_exp_time_corr = 'rgx{.*trig_syst.*},rgx{.*syst_pu}'
nuis_exp_time_uncorr = 'rgx{.*trig_stat.*},rgx{syst_elec_reco.*},rgx{syst_elec_id.*},rgx{.*muon_iso.*},rgx{.*muon_id.*},rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*},rgx{syst_prefiring.*},'+nuis_jec_uncorr  #rgx{.*jec.*}''
nuis_exp = nuis_exp_time_flat+','+nuis_exp_time_corr+','+nuis_exp_time_uncorr

nuis_exp_elec = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*}'
nuis_exp_muon = 'rgx{.*muon_id.*},rgx{.*muon_iso.*}'
nuis_exp_pu = 'rgx{syst_pu.*}'
nuis_exp_btag = 'rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*}'
nuis_exp_jec = 'rgx{.*jec.*}'
nuis_exp_prefiring = 'rgx{syst_prefiring.*}'
nuis_exp_trigger = 'rgx{.*trig.*}'

#nuis_mcstat = 'autoMCStats'
nuis_mcstat = 'rgx{MCstat.*}'

nuis_sme_singletop_XX = 'sme_decay_XX'
nuis_sme_singletop_XY = 'sme_decay_XY'
nuis_sme_singletop_XZ = 'sme_decay_XZ'
nuis_sme_singletop_YZ = 'sme_decay_YZ'
nuis_sme_singletop = 'rgx{sme_decay.*}'

nuis_time_flat = nuis_lumi_time_flat+','+nuis_bkgdnorm+','+nuis_theory+','+nuis_exp_time_flat
nuis_time_corr = nuis_lumi_time_corr+','+nuis_exp_time_corr+','+nuis_sme_singletop
nuis_time_corr_withMCstat = nuis_lumi_time_corr+','+nuis_exp_time_corr+','+nuis_sme_singletop+','+nuis_mcstat

if NuisanceGroup=="time_flat_uncorr_corr":
    list_nuisgroups.append(nuis_time_flat)
    list_nuisgroups.append(nuis_time_corr_withMCstat)
    list_nuisgroups.append(nuis_exp_time_uncorr)
    list_nuisnames.append('time_flat')
    list_nuisnames.append('time_correlated')
    list_nuisnames.append('time_uncorrelated')
    list_legendnames.append('Time uniform')
    list_legendnames.append('Time correlated')
    list_legendnames.append('Time uncorrelated')

if NuisanceGroup=="time_flat_uncorr_corr_mcstat":
    list_nuisgroups.append(nuis_time_flat)
    list_nuisgroups.append(nuis_time_corr)
    list_nuisgroups.append(nuis_exp_time_uncorr)
    list_nuisgroups.append(nuis_mcstat)
    list_nuisnames.append('time_flat')
    list_nuisnames.append('time_correlated')
    list_nuisnames.append('time_uncorrelated')
    list_nuisnames.append('mc_stat')
    list_legendnames.append('Time uniform')
    list_legendnames.append('Time correlated')
    list_legendnames.append('Time uncorrelated')
    list_legendnames.append('MC Stat.')

if NuisanceGroup=="exp_theory_bkgdnorm_lumi_mcstat":
    list_nuisgroups.append(nuis_exp)
    list_nuisgroups.append(nuis_theory)
    list_nuisgroups.append(nuis_bkgdnorm)
    list_nuisgroups.append(nuis_lumi)
    list_nuisgroups.append(nuis_mcstat)
    list_nuisnames.append('exp')
    list_nuisnames.append('theory')
    list_nuisnames.append('bkgd_norm')
    list_nuisnames.append('lumi')
    list_nuisnames.append('mc_stat')
    list_legendnames.append('Experimental')
    list_legendnames.append('Theory')
    list_legendnames.append('Background norm')
    list_legendnames.append('Luminosity')
    list_legendnames.append('MC Stat.')

if NuisanceGroup=="exp_elec_muon_pu_btag_jec_trigger_prefiring":
    list_nuisgroups.append(nuis_exp_elec)
    list_nuisgroups.append(nuis_exp_muon)
    list_nuisgroups.append(nuis_exp_pu)
    list_nuisgroups.append(nuis_exp_btag)
    list_nuisgroups.append(nuis_exp_jec)
    list_nuisgroups.append(nuis_exp_prefiring)
    list_nuisgroups.append(nuis_exp_trigger)
    list_nuisnames.append('electron')
    list_nuisnames.append('muon')
    list_nuisnames.append('pileup')
    list_nuisnames.append('btag')
    list_nuisnames.append('jec')
    list_nuisnames.append('prefiring')
    list_nuisnames.append('trigger')
    list_legendnames.append('Electron')
    list_legendnames.append('Muon')
    list_legendnames.append('Pileup')
    list_legendnames.append('B tagging')
    list_legendnames.append('Jet energy scale')
    list_legendnames.append('ECAL prefiring')
    list_legendnames.append('Trigger')

if NuisanceGroup=="theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco":
    list_nuisgroups.append(nuis_theory_pttop)
    list_nuisgroups.append(nuis_theory_mtop)
    list_nuisgroups.append(nuis_theory_ps)
    list_nuisgroups.append(nuis_theory_qcdscale)
    list_nuisgroups.append(nuis_theory_pdfas)
    list_nuisgroups.append(nuis_theory_hdamp)
    list_nuisgroups.append(nuis_theory_uetune)
    list_nuisgroups.append(nuis_theory_colorreco)
    list_nuisnames.append('pt_top')
    list_nuisnames.append('mtop')
    list_nuisnames.append('parton_shower')
    list_nuisnames.append('qcd_scale')
    list_nuisnames.append('pdf_as')
    list_nuisnames.append('hdamp')
    list_nuisnames.append('ue_tune')
    list_nuisnames.append('color_reco')
    list_legendnames.append('Top p_{T}')
    list_legendnames.append('Top mass')
    list_legendnames.append('Parton shower')
    list_legendnames.append('QCD scale')
    list_legendnames.append('Pdf + #alpha_{s}')
    list_legendnames.append('ME-PS matching')
    list_legendnames.append('UE tune')
    list_legendnames.append('Color reconnection')

if NuisanceGroup=="pu_trigger":
    list_nuisgroups.append(nuis_exp_pu)
    list_nuisgroups.append(nuis_exp_trigger)
    #list_nuisnames.append('pu_flat')
    list_nuisnames.append('pu_time')
    #list_nuisnames.append('trig_full')
    list_nuisnames.append('trig_noNvtx')
    #list_nuisnames.append('trig_flat')

if NuisanceGroup=="pu_trigger_smedecay":
    list_nuisgroups.append(nuis_exp_pu)
    list_nuisgroups.append(nuis_exp_trigger)
    list_nuisgroups.append(nuis_sme_singletop)
    list_nuisnames.append('pu_time')
    list_nuisnames.append('trig_noNvtx')
    list_nuisnames.append('sme_decay')
    list_legendnames.append('Pileup uniform')
    list_legendnames.append('Trigger full')
    list_legendnames.append('SME single top')

if NuisanceGroup=="smedecay":
    list_nuisgroups.append(nuis_sme_singletop_XX)
    list_nuisgroups.append(nuis_sme_singletop_XY)
    list_nuisgroups.append(nuis_sme_singletop_XZ)
    list_nuisgroups.append(nuis_sme_singletop_YZ)
    list_nuisnames.append('sme_decay_XX')
    list_nuisnames.append('sme_decay_XY')
    list_nuisnames.append('sme_decay_XZ')
    list_nuisnames.append('sme_decay_YZ')
    list_legendnames.append('SME single top XX')
    list_legendnames.append('SME single top XY')
    list_legendnames.append('SME single top XZ')
    list_legendnames.append('SME single top YZ')



nuisnames_remain = "Others"
#nuisnames_remain = "MCstat"

print("Checking "+str(len(list_nuisgroups))+" groups of nuisances")
print list_nuisnames



###################
## Loop  over wilson coefficients
###################


def asimov_param(w):
    sasimov=''
    wrange=''
    if w[-2:]=='XX' or w[-2:]=='XY':
	wrange='5'
    if w[-2:]=='XZ' or w[-2:]=='YZ':
	wrange='15'
    if asimov == 'asimov':
        sasimov += '--setParameters '+w+'=0 -t -1'
    elif asimov == 'injectiontest':
        sasimov += '--setParameters '+w+'=1 -t -1 '
    sasimov += '  --setParameterRanges '+w+'=-'+wrange+','+wrange
    return sasimov

def getwilsontext(wilson):
    if (wilson=="cLXX"): modwilson = "c_{L,XX}=-c_{L,YY}"
    if (wilson=="cLXY"): modwilson = "c_{L,XY}=c_{L,YX}"
    if (wilson=="cLXZ"): modwilson = "c_{L,XZ}=c_{L,ZX}"
    if (wilson=="cLYZ"): modwilson = "c_{L,YZ}=c_{L,ZY}"
    if (wilson=="cRXX"): modwilson = "c_{R,XX}=-c_{R,YY}"
    if (wilson=="cRXY"): modwilson = "c_{R,XY}=c_{R,YX}"
    if (wilson=="cRXZ"): modwilson = "c_{R,XZ}=c_{R,ZX}"
    if (wilson=="cRYZ"): modwilson = "c_{R,YZ}=c_{R,ZY}"
    if (wilson=="cXX"): modwilson = "c_{XX}=-c_{YY}"
    if (wilson=="cXY"): modwilson = "c_{XY}=c_{YX}"
    if (wilson=="cXZ"): modwilson = "c_{XZ}=c_{ZX}"
    if (wilson=="cYZ"): modwilson = "c_{YZ}=c_{ZY}"
    if (wilson=="dXX"): modwilson = "d_{XX}=-d_{YY}"
    if (wilson=="dXY"): modwilson = "d_{XY}=d_{YX}"
    if (wilson=="dXZ"): modwilson = "d_{XZ}=d_{ZX}"
    if (wilson=="dYZ"): modwilson = "d_{YZ}=d_{ZY}"
    return modwilson


###################
## Core
###################

optim = ' --cminDefaultMinimizerStrategy 0 '
npoints=10

if wilson_=='sme_all':
    wilson_list_all = ['cLXX','cLXY','cLXZ','cLYZ','cRXX','cRXY','cRXZ','cRYZ','cXX','cXY','cXZ','cYZ','dXX','dXY','dXZ','dYZ']
    #wilson_list_all = ['cLXX','cLXY','cLXZ','cLYZ','cRXX','cRXY','cRXZ','cRYZ']
else:
    wilson_list_all = [wilson_] #for testing

print 'Uncertainty breakdown '+NuisanceGroup+', wilson: '
print wilson_list_all

for wilson in wilson_list_all:

    #Nominal fit
    cmd1 = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov + optim #' --robustFit 1 '
    cmd1 +=' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root '
    cmd1 += asimov_param(wilson) + ' --algo grid --points '+str(npoints)

    #Snaphsot
    cmd2 = 'combine -M MultiDimFit -n .snapshot_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov+' --algo=singles '+optim#--robustFit 1 '
    cmd2 +=' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root ' 
    cmd2 += asimov_param(wilson) +' --saveWorkspace'

    #MC stat
    #cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH120.root -n .freezeMCStats '+asimov_param(wilson)+' --algo grid --points 30 --freezeNuisanceGroups autoMCStats --snapshotName MultiDimFit'

    #Stat. uncertainty only
    cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov+'.MultiDimFit.mH120.root '+optim
    cmd3 += '-n .freezeall_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov +' '
    cmd3 += asimov_param(wilson)+' --algo grid --points '+str(npoints*5)+' '
    cmd3 += '--freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

    #Fit removing group uncertainties
    cmd4 = []
    for k in range(len(list_nuisgroups)):
        cmd_k = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov+'.MultiDimFit.mH120.root '+optim
	cmd_k += '-n .freeze_'+list_nuisnames[k]+'_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov +' '
	cmd_k += asimov_param(wilson)+' --algo grid --points '+str(npoints*3)+' '
        if (list_nuisgroups[k]=='autoMCStats'):
            cmd_k += '--freezeNuisanceGroups '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
	else:
	    cmd_k += '--freezeParameters '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
        cmd4.append(cmd_k)

    #Plotting likelihood scan
    #cmd5 = "python plot1DScan.py higgsCombine.nominal.MultiDimFit.mH120.root --others 'higgsCombine.freezeMCStats.MultiDimFit.mH120.root:FreezeMCStats:2' 'higgsCombine.freezeall.MultiDimFit.mH120.root:FreezeAll:4' -o freeze_MCStats_all --POI "+wilson+" --main-label "
    #if (asimov=='asimov'): cmd5 += 'Asimov'
    #cmd5 += " --breakdown MCStats,Syst,Stat > uncertainty_breakdown_"+wilson+".log"

    cmd5 = "python plot1DScan.py higgsCombine.nominal_"+observable+"_"+year+"_"+wilson+"_"+NuisanceGroup+'_'+asimov+".MultiDimFit.mH120.root --others "
    for k in range(len(list_nuisgroups)):
        cmd5 += " 'higgsCombine.freeze_"+list_nuisnames[k]+'_'+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov+".MultiDimFit.mH120.root:Freeze_"+list_nuisnames[k]+":"+str(k+2)+"' "
    cmd5 += " 'higgsCombine.freezeall_"+observable+'_'+year+'_'+wilson+'_'+NuisanceGroup+'_'+asimov+".MultiDimFit.mH120.root:FreezeAll:1' "
    cmd5 += "-o impacts/"+year+"/"+ observable + "_UncertaintyBreakdown_detailed_"+year+"_"+wilson+"_"+NuisanceGroup+"_"+asimov+" "
    cmd5 += "--POI "+wilson
    cmd5 += " --main-label "
    if (asimov=='asimov'): cmd5 += 'Asimov'
    if (asimov=='injectiontest'): cmd5 += 'InjectionTest'
    if (asimov=='data'): cmd5 += 'Data'
    cmd5 += " --breakdown "
    for k in range(len(list_nuisgroups)):
        cmd5 += list_nuisnames[k] + ","
    cmd5 += "Others,Stat > impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+wilson+"_"+NuisanceGroup+"_"+asimov+".log"

    if (doPlotsOnly==False):
        print cmd1
        os.system(cmd1)
        print cmd2
        os.system(cmd2)
        print cmd3
        os.system(cmd3)
        for k in range(len(list_nuisgroups)):
            print cmd4[k]
            os.system(cmd4[k])
        print cmd5
        os.system(cmd5)

###################
## Getting uncertainties
###################


unc_syst_pos = []
unc_syst_neg  = []

unc_total_pos = []
unc_total_neg = []
unc_noSyst_pos = []
unc_noSyst_neg = []

individual_bestfit_allbins = []
individual_uncert_up_allbins = []
individual_uncert_down_allbins = []
individual_uncert_avg_allbins = []

wordnum_down = []
wordnum_up = []
for k in range(2+len(list_nuisgroups)):
    wordnum_down.append(4+16*k)
    wordnum_up.append(6+16*k)

list_nuisnames.insert(0, 'stat+syst')
list_nuisnames.append('stat')
list_legendnames.insert(0, 'Stat.+Syst.')
list_legendnames.append('Stat.')

rate_total = []
rate_syst = []
rate_stat = []


for wilson in wilson_list_all:

    try:
        file = open("./impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+wilson+"_"+NuisanceGroup+"_"+asimov+".log")
	rootfile = TFile("higgsCombine.nominal_"+observable+"_"+year+"_"+wilson+"_"+NuisanceGroup+"_"+asimov+".MultiDimFit.mH120.root","READ")
    except:
        print "Problem with file: "+"./impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+wilson+"_"+NuisanceGroup+"_"+asimov+".log"
    print "Opened: "+"./impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+wilson+"_"+NuisanceGroup+"_"+asimov+".log"

    individual_uncert_up = []
    individual_uncert_down = []
    individual_uncert_avg = []

    tree = rootfile.Get("limit")
    tree.GetEvent(0)
    individual_bestfit_allbins.append(tree.GetLeaf(wilson).GetValue())

    i=0
    for line in file:
        uncert = 0
        for word in line.split():
            #print(str(i)+' '+word)
            for k in range(len(wordnum_down)):
                if i==wordnum_down[k]:
                    #print("Freeze "+list_nuisnames[k]+" down="+str(float(word[:-1])))
                    individual_uncert_down.append(float(word[:-1])-individual_bestfit_allbins[-1])
                if i==wordnum_up[k]:
                    #print("Freeze "+list_nuisnames[k]+" up="+str(float(word[:-1])))
                    individual_uncert_up.append(float(word[:-1])-individual_bestfit_allbins[-1])
            i = i+1

    for k in range(len(individual_uncert_up)):
        if k!=0 and k!=len(individual_uncert_up)-1:
            if (individual_uncert_down[0]*individual_uncert_down[0]-individual_uncert_down[k]*individual_uncert_down[k]>0):
                individual_uncert_down[k] = math.sqrt(individual_uncert_down[0]*individual_uncert_down[0]-individual_uncert_down[k]*individual_uncert_down[k])
            else:
                individual_uncert_down[k] = 0
            if (individual_uncert_up[0]*individual_uncert_up[0]-individual_uncert_up[k]*individual_uncert_up[k]>0):
                individual_uncert_up[k] = math.sqrt(individual_uncert_up[0]*individual_uncert_up[0]-individual_uncert_up[k]*individual_uncert_up[k])
            else:
                individual_uncert_up[k] = 0

    #print str(len(individual_uncert_down))+' '+ str(len(individual_uncert_up))

    for k in range(len(individual_uncert_up)):
        if k!=0 and k!=len(individual_uncert_up)-1:
	    individual_uncert_down[k]=-individual_uncert_down[k]
            #individual_uncert_avg.append((individual_uncert_up[k]+individual_uncert_down[k])/2.)
        #else:
        individual_uncert_avg.append((individual_uncert_up[k]-individual_uncert_down[k])/2.)

    print str(len(individual_uncert_down))+' '+ str(len(individual_uncert_up))+' '+str(len(individual_uncert_avg))

    individual_uncert_down_allbins.append(individual_uncert_down)
    individual_uncert_up_allbins.append(individual_uncert_up)
    individual_uncert_avg_allbins.append(individual_uncert_avg)

    file.close()

print 'individual_uncert_down_allbins', individual_uncert_down_allbins
print 'individual_uncert_up_allbins', individual_uncert_up_allbins
print 'individual_uncert_avg_allbins', individual_uncert_avg_allbins

print str(len(individual_uncert_down_allbins))+' '+str(len(individual_uncert_up_allbins))
for j in range(len(individual_uncert_down_allbins)):
    print str(len(individual_uncert_down_allbins[j]))+' '+str(len(individual_uncert_up_allbins[j]))

###################
## Plotting
###################

canvas = TCanvas('SME fit uncertainties','SME fit uncertainties', 1000, 800)
canvas.UseCurrentStyle()

pad = TPad("pad","pad",0,0,1,1)
pad.SetLeftMargin(0.14)
#pad.SetBottomMargin(0.2)
pad.SetRightMargin(0.245)
pad.Draw()
pad.cd()

h_uncert = []
h_uncertUp = []
h_uncertDown = []

#uncert_bin = []
#uncert_binUp = []
#uncert_binDown = []

for k in range(len(list_nuisnames)):
    print str(k)
    h = TH1F(list_nuisnames[k], list_nuisnames[k], 16, 0, 16)
    hUp = TH1F(list_nuisnames[k]+'Up', list_nuisnames[k]+'Up', 16, 0, 16)
    hDown = TH1F(list_nuisnames[k]+'Down', list_nuisnames[k]+'Down', 16, 0, 16)
    uncert_bin = []
    uncert_binUp = []
    uncert_binDown = []
    for j in range(len(wilson_list_all)):
	uncert_bin = individual_uncert_avg_allbins[j]
        uncert_binUp = individual_uncert_up_allbins[j]
        uncert_binDown = individual_uncert_down_allbins[j]
	print str(len(uncert_bin))+' '+str(len(uncert_binUp))+' '+str(len(uncert_binDown))
        h.Fill(j+0.5, uncert_bin[k])
        hUp.Fill(j+0.5, uncert_binUp[k])
        hDown.Fill(j+0.5, uncert_binDown[k])
    h_uncert.append(h)
    h_uncertUp.append(hUp)
    h_uncertDown.append(hDown)

def getcolor(c):
   d = c
   if c==3:
        d = 820
   if c==5:
        d = 800
   if c==8:
        d = 807
   if c==9:
        d = 823
   if c==10:
        d = 880
   return d

plotYmin=-15
plotYmax=15

for k in range(len(list_nuisnames)):
        h_uncert[k].SetLineColor(getcolor(k+1))
        h_uncert[k].SetLineWidth(2)
        h_uncertUp[k].SetLineColor(getcolor(k+1))
        h_uncertUp[k].SetLineWidth(2)
        h_uncertDown[k].SetLineColor(getcolor(k+1))
        h_uncertDown[k].SetLineWidth(2)
        if k==0:
            h_uncertUp[k].SetMinimum(plotYmin)
            h_uncertUp[k].SetMaximum(plotYmax)
            h_uncertUp[k].SetYTitle("Uncertainty on Wilson coefficient")
            #h_uncertUp[k].SetXTitle("Wilson")
	    h_uncertUp[k].GetXaxis().SetLabelSize(0.04)
	    for j in range(len(wilson_list_all)):
	        h_uncertUp[k].GetXaxis().SetBinLabel(1+j,getwilsontext(wilson_list_all[j]))
		#h_uncertUp[k].GetXaxis().ChangeLabel(1+j,15,-1,0)
	    h_uncertUp[k].GetXaxis().LabelsOption("v")
            h_uncertUp[k].GetYaxis().SetTitleOffset(1.)
            h_uncertUp[k].Draw("HIST")
            h_uncertDown[k].Draw("HISTsame")
        else:
            h_uncertUp[k].Draw("HISTsame")
            h_uncertDown[k].Draw("HISTsame")

legend = TLegend(0.76,0.94,0.998,0.94-len(list_nuisnames)*0.035)
legend.SetTextSize(0.03)
for k in range(len(list_nuisnames)):
    legend.AddEntry(h_uncertUp[k].GetName(), list_legendnames[k], 'l')
legend.Draw()
legend.Draw("SAME")

if asimov=='asimov':
    sim=True
else:
    sim=False
if(year=='2016'):
    tdr.cmsPrel(36300., 13, simOnly=sim, thisIsPrelim=True)
elif(year=='2017'):
    tdr.cmsPrel(41530., 13., simOnly=sim, thisIsPrelim=True)
elif(year=='Comb'):
    tdr.cmsPrel(77800,13., simOnly=sim, thisIsPrelim=True)

resultname = './impacts/'+year+'/'+asimov+'/'+observable+'_smefit_'+nuisancegroup+'_'+year
#if (asimov=='injectiontest'):
resultname += '_'+asimov

if len(wilson_list_all)>=8:
    canvas.SaveAs(resultname+'.pdf')



