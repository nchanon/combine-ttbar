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

doPlotsOnly = True
#doPlotsOnly = False

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('nuisancegroup', help='nuisance group', default='')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')


args = parser.parse_args()
observable = args.observable
asimov = args.asimov
year = args.year
nuisancegroup = args.nuisancegroup

ntimebin = 24

pois = []
for i in range(24):
    pois.append('r_'+str(i))

asi = ''
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'
    print ''
    asi = ' --setParameters '
    for i in range(24):
        asi += pois[i]+'=1'
        if i != 23:
            asi += ','
    asi += ' -t -1 '

r_range='0.9,1.1'
npoints=10


NuisanceGroup = ""
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


###################
## Nuisances to be evaluated
###################

list_nuisgroups=[]
list_nuisnames=[]

#Grouping by kind of nuisances
nuis_lumi_time_uncorr = 'rgx{lumi_flat_uncor_.*},lumi_flat_cor'
nuis_lumi_time_corr = 'rgx{lumi_stability_.*},rgx{lumi_linearity_.*}'
nuis_lumi = nuis_lumi_time_uncorr+','+nuis_lumi_time_corr

nuis_bkgdnorm = 'rttx,rsingletop,rdibosons,rvjets'

nuis_theory = 'syst_pt_top,syst_ps_isr_signal,syst_ps_isr_singletop,syst_ps_fsr,syst_qcdscale_signal,syst_qcdscale_singletop,syst_qcdscale_ttx,syst_qcdscale_vjets,syst_pdfas,hdamp,CP5,erdOn,GluonMove,QCDinspired,mtop'

nuis_theory_pttop = 'syst_pt_top'
nuis_theory_mtop = 'mtop'
nuis_theory_ps = 'syst_ps_isr_signal,syst_ps_isr_singletop,syst_ps_fsr'
nuis_theory_qcdscale = 'rgx{syst_qcdscale_.*}'
nuis_theory_pdfas = 'syst_pdfas'
nuis_theory_hdamp = 'hdamp'
nuis_theory_uetune = 'CP5'
nuis_theory_colorreco = 'erdOn,GluonMove,QCDinspired'


nuis_exp_time_corr = 'rgx{.*trig.*}'
nuis_exp_time_uncorr = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*},rgx{syst_muon_iso.*},rgx{syst_muon_id.*},rgx{syst_pu.*},rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*},rgx{syst_prefiring.*},rgx{.*jec.*}'
nuis_exp = nuis_exp_time_corr+','+nuis_exp_time_uncorr

nuis_exp_elec = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*}'
nuis_exp_muon = 'rgx{syst_elec_id.*},rgx{syst_muon_iso.*}'
nuis_exp_pu = 'rgx{syst_pu.*}'
nuis_exp_btag = 'rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*}'
nuis_exp_jec = 'rgx{.*jec.*}'
nuis_exp_prefiring = 'rgx{syst_prefiring.*}'
nuis_exp_trigger = 'rgx{.*trig.*}'
#nuis_exp_trigger = 'rgx{emu_trig_.*}'
#nuis_exp_trigger  = 'rgx{syst_em_trig.*}'

nuis_mcstat = 'autoMCStats'

nuis_time_flat = nuis_lumi_time_uncorr+','+nuis_bkgdnorm+','+nuis_theory
nuis_time_corr = nuis_lumi_time_corr+','+nuis_exp_time_corr

if NuisanceGroup=="time_flat_uncorr_corr_mcstat":
    list_nuisgroups.append(nuis_time_flat)
    list_nuisgroups.append(nuis_time_corr)
    list_nuisgroups.append(nuis_exp_time_uncorr)
    list_nuisgroups.append(nuis_mcstat)
    list_nuisnames.append('time_flat')
    list_nuisnames.append('time_correlated')
    list_nuisnames.append('time_uncorrelated')
    list_nuisnames.append('mc_stat')

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

if NuisanceGroup=="pu_trigger":
    list_nuisgroups.append(nuis_exp_pu)
    list_nuisgroups.append(nuis_exp_trigger)
    list_nuisnames.append('pu_flat')
    #list_nuisnames.append('pu_time')
    list_nuisnames.append('trig_full')
    #list_nuisnames.append('trig_noNvtx')
    #list_nuisnames.append('trig_flat')



#if NuisanceGroup=="lumi_bkgdnorm_theory_exp":
#    list_nuisgroups.append(nuis_lumi)
#    list_nuisgroups.append(nuis_bkgdnorm)
#    list_nuisgroups.append(nuis_theory)
#    list_nuisgroups.append(nuis_exp)
#    list_nuisnames.append('lumi')
#    list_nuisnames.append('bkgd_norm')
#    list_nuisnames.append('theory')
#    list_nuisnames.append('exp')

nuisnames_remain = "Others"
#nuisnames_remain = "MCstat"

print("Checking "+str(len(list_nuisgroups))+" groups of nuisances")
print list_nuisnames 

###################
## Core
###################

doFloatPOI = '1'
#doFloatPOI = '0'

#for j in range(1):
for j in range(ntimebin): 
    rbin = pois[j]

    #Nominal fit
    cmd1 = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+NuisanceGroup+' --robustFit 1 '
    cmd1 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
    cmd1 += asi
    cmd1 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
    cmd1 += ' --algo grid --points '+str(npoints)+' '

    #Snaphsot
    cmd2 = 'combine -M MultiDimFit -n .snapshot_'+observable+'_'+year+'_'+NuisanceGroup+' --robustFit 1 '
    cmd2 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
    cmd2 += asi
    cmd2 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
    cmd2 += '  --saveWorkspace'

    #Stat. uncertainty only
    cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root -n .freezeall_'+observable+'_'+year+'_'+NuisanceGroup+' '
    cmd3 += asi
    cmd3 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
    cmd3 += ' --algo grid --points '+str(npoints*5)+' '
    cmd3 += '--freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

    #Fit removing group uncertainties
    cmd4 = []
    for k in range(len(list_nuisgroups)):
	cmd_k = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root -n .freeze'+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+' '
	cmd_k += asi
	cmd_k += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
	cmd_k += ' --algo grid --points '+str(npoints*3)+' '
	if (list_nuisgroups[k]=='autoMCStats'): 
	    cmd_k += '--freezeNuisanceGroups '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
	else:
	    cmd_k += '--freezeParameters '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
	cmd4.append(cmd_k)

    #Plotting likelihood scan
    cmd5 = "python plot1DScan.py higgsCombine.nominal_"+observable+"_"+year+"_"+NuisanceGroup+".MultiDimFit.mH120.root --others "
    for k in range(len(list_nuisgroups)):
	cmd5 += " 'higgsCombine.freeze"+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+".MultiDimFit.mH120.root:Freeze_"+list_nuisnames[k]+":"+str(k+2)+"' "
    cmd5 += " 'higgsCombine.freezeall_"+observable+'_'+year+'_'+NuisanceGroup+".MultiDimFit.mH120.root:FreezeAll:1' "
    #cmd5 += "-o freeze_all_"+year+" "
    cmd5 += "-o impacts/"+year+"/"+ observable + "_UncertaintyBreakdown_detailed_"+year+"_"+rbin+"_"+NuisanceGroup+" "
    cmd5 += "--POI "+rbin
    cmd5 += " --main-label "
    if (asimov=='asimov'): cmd5 += 'Asimov'
    cmd5 += " --breakdown "
    for k in range(len(list_nuisgroups)):
	cmd5 += list_nuisnames[k] + ","
    cmd5 += "Others,Stat > impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+rbin+"_"+NuisanceGroup+".log"

    #cmd6 = 'cp freeze_all_'+year+'.pdf impacts/'+year+'/'
    #if (asimov == 'asimov'): cmd6 += asimov+'/'
    #cmd6 += observable + '_UncertaintyBreakdown_detailed_'+year+'_'+rbin+'_'+NuisanceGroup+'.pdf'

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
        #print cmd6
        #os.system(cmd6)
    

#exit()

###################
## Getting uncertainties
###################

unc_syst_pos = []
unc_syst_neg  = []

unc_total_pos = []
unc_total_neg = []
#unc_noMCStats_pos = []
#unc_noMCStats_neg = []
unc_noSyst_pos = []
unc_noSyst_neg = []

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

rate_total = []
rate_syst = []
rate_stat = []

#for j in range(1):
for j in range(ntimebin):
    rbin = pois[j]

    file = open('impacts/'+year+'/'+observable+'_uncertainty_breakdown_detailed_'+rbin+'_'+NuisanceGroup+'.log')

    individual_uncert_up = []
    individual_uncert_down = []
    individual_uncert_avg = []

    i=0
    for line in file:
        uncert = 0
        for word in line.split():
            #print(str(i)+' '+word)
	    for k in range(len(wordnum_down)):
		if i==wordnum_down[k]:
		    print("Freeze "+list_nuisnames[k]+" down="+str(float(word[:-1])))
		    individual_uncert_down.append(float(word[:-1])-1)
		if i==wordnum_up[k]:
		    print("Freeze "+list_nuisnames[k]+" up="+str(float(word[:-1])))
		    individual_uncert_up.append(float(word[:-1])-1)

            #if (i==4): unc_total_neg.append(float(word[:-1]))
            #if (i==6): unc_total_pos.append(float(word[:-1]))
            #if (i==20): unc_noSyst_neg.append(float(word[:-1]))
            #if (i==22): unc_noSyst_pos.append(float(word[:-1]))
            #if (i==36): unc_noSyst_neg.append(float(word[:-1]))
            #if (i==38): unc_noSyst_pos.append(float(word[:-1]))
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

    for k in range(len(individual_uncert_up)):
	if k!=0 and k!=len(individual_uncert_up)-1:
	    individual_uncert_avg.append((individual_uncert_up[k]+individual_uncert_down[k])/2.)
	else:
	    individual_uncert_avg.append((individual_uncert_up[k]-individual_uncert_down[k])/2.)

    individual_uncert_down_allbins.append(individual_uncert_down)
    individual_uncert_up_allbins.append(individual_uncert_up)
    individual_uncert_avg_allbins.append(individual_uncert_avg)

    file.close()

print 'individual_uncert_down_allbins', individual_uncert_down_allbins
print 'individual_uncert_up_allbins', individual_uncert_up_allbins
print 'individual_uncert_avg_allbins', individual_uncert_avg_allbins


    #unc_syst_pos.append(math.sqrt(unc_total_pos[j]*unc_total_pos[j]-unc_noSyst_pos[j]*unc_noSyst_pos[j]))
    #unc_syst_neg.append(math.sqrt(unc_total_neg[j]*unc_total_neg[j]-unc_noSyst_neg[j]*unc_noSyst_neg[j]))

    #rate_total.append([1,1-unc_total_neg[j], unc_total_pos[j]-1])
    #rate_stat.append([1,1-unc_noSyst_neg[j], unc_noSyst_pos[j]-1])

#print rate_total
#print rate_stat

#exit()

###################
## Plotting
###################

nbin = 0
min_bin = 0
max_bin = 0

#legend_coordinates = [0.7, 0.8, 0.87, 0.87]
#TH1.SetDefaultSumw2(1)
signal_integral = 0
background_integral_i = []
background_integral = 0
data_integral = 0
syst_up_integral = 0
syst_down_integral = 0
canvas = TCanvas('differential measurment','differential measurment', 1000, 800)
canvas.UseCurrentStyle()

pad = TPad("pad","pad",0,0,1,1)
pad.SetLeftMargin(0.14)
#pad.SetBottomMargin(0.2)
pad.SetRightMargin(0.245)
pad.Draw()
pad.cd()

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

h_uncert = []
h_uncertUp = []
h_uncertDown = []

uncert_bin = []
uncert_binUp = []
uncert_binDown = []

for k in range(len(list_nuisnames)):
    h = TH1F(list_nuisnames[k], list_nuisnames[k], 24, 0, 24)
    hUp = TH1F(list_nuisnames[k]+'Up', list_nuisnames[k]+'Up', 24, 0, 24)
    hDown = TH1F(list_nuisnames[k]+'Down', list_nuisnames[k]+'Down', 24, 0, 24)
    #for j in range(1):
    for j in range(ntimebin):
        uncert_bin = individual_uncert_avg_allbins[j]
	uncert_binUp = individual_uncert_up_allbins[j]
	uncert_binDown = individual_uncert_down_allbins[j]
	h.Fill(j+0.5, 100*uncert_bin[k])
	hUp.Fill(j+0.5, 100*uncert_binUp[k])
        if k!=0 and k!=len(individual_uncert_up)-1: 
	    hDown.Fill(j+0.5, -100*uncert_binDown[k])
	else:
	    hDown.Fill(j+0.5, 100*uncert_binDown[k])
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

plotYmin=-5.0
plotYmax=5.0

if nuisancegroup=="exp_breakdown":
    plotYmin=-2.0
    plotYmax=2.0
if nuisancegroup=="theory_breakdown":
    plotYmin=-1.0
    plotYmax=1.0

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
            h_uncertUp[k].SetYTitle("Uncertainty (%)")
            h_uncertUp[k].SetXTitle("sidereal time (h)");
            h_uncertUp[k].GetYaxis().SetTitleOffset(1.1)
	    h_uncertUp[k].Draw("HIST")
            h_uncertDown[k].Draw("HISTsame")
	    #h_uncert[k].SetMinimum(0.)
	    #h_uncert[k].SetMaximum(0.06)
	    #h_uncert[k].SetYTitle("Uncertainty (%)")
	    #h_uncert[k].SetXTitle("sidereal time (h)");
	    #h_uncert[k].Draw("HIST")
	else: 
	    #h_uncert[k].Draw("HISTsame")
	    h_uncertUp[k].Draw("HISTsame")
	    h_uncertDown[k].Draw("HISTsame")

legend = TLegend(0.76,0.94,0.998,0.94-len(list_nuisnames)*0.035)
#legend.SetHeader('Asimov '+' '+year, 'C')
legend.SetTextSize(0.03)
for k in range(len(list_nuisnames)):
    legend.AddEntry(h_uncertUp[k].GetName(), list_nuisnames[k], 'l')
legend.Draw()
legend.Draw("SAME")

resultname = './impacts/'+year+'/'+observable+'_differential_'+nuisancegroup+'_'+year

canvas.SaveAs(resultname+'.pdf')

#raw_input()
#exit()
