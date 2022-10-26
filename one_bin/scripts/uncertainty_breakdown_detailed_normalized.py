import os, sys
sys.path.append('./')

import math
import argparse
import subprocess

import numpy as np

from tools.style_manager import *
from tools.norm_xs_utils import *

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

#import print_options
#print_options.set_float_precision(4)

import tools.tdrstyle as tdr
tdr.setTDRStyle()

#doPlotsOnly = True
doPlotsOnly = False

#doNormBreakDown = False
#doNormBreakDown = True

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

r_range='0.5,2.0'

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
    asi += ' --setParameterRanges '
    for i in range(24):
        asi += pois[i]+'='+r_range
        if i != 23:
            asi += ':'
    asi += ' -t -1 '


#optim = ''
#optim = ' --robustFit 1'
#optim = ' --cminDefaultMinimizerStrategy 0 '
optim = ' --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01 '
#optim = ' --cminDefaultMinimizerStrategy 2 '
#optim = ' --cminDefaultMinimizerType Minuit --cminDefaultMinimizerStrategy 0'

NuisanceGroup = ""
if nuisancegroup=='test':
   NuisanceGroup="Test"
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
nuis_lumi_time_flat = 'rgx{lumi_flat_uncor_.*},lumi_flat_cor'
nuis_lumi_time_corr = 'rgx{lumi_stability_.*},rgx{lumi_linearity_.*}'
nuis_lumi = nuis_lumi_time_flat+','+nuis_lumi_time_corr

nuis_bkgdnorm = 'rttx,rsingletop,rdibosons,rvjets'

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
nuis_exp_time_flat = 'FlavorPureGluon_jec,FlavorPureBottom_jec'
nuis_exp_time_corr = 'rgx{.*trig_syst.*},rgx{.*syst_pu}'
nuis_exp_time_uncorr = 'rgx{.*trig_stat.*},rgx{syst_elec_reco.*},rgx{syst_elec_id.*},rgx{.*muon_iso.*},rgx{.*muon_id.*},rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*},rgx{syst_prefiring.*},'+nuis_jec_uncorr  #rgx{.*jec.*}'
nuis_exp = nuis_exp_time_flat+','+nuis_exp_time_corr+','+nuis_exp_time_uncorr

nuis_exp_elec = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*}'
nuis_exp_muon = 'rgx{.*muon_id.*},rgx{.*muon_iso.*}'
nuis_exp_pu = 'rgx{syst_pu.*}'
nuis_exp_btag = 'rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*}'
nuis_exp_jec = 'rgx{.*jec.*}'
nuis_exp_prefiring = 'rgx{syst_prefiring.*}'
nuis_exp_trigger = 'rgx{.*trig.*}'
#nuis_exp_trigger = 'rgx{emu_trig_.*}'
#nuis_exp_trigger  = 'rgx{syst_em_trig.*}'

#nuis_mcstat = 'autoMCStats'
nuis_mcstat = 'rgx{MCstat.*}'

nuis_time_flat = nuis_lumi_time_flat+','+nuis_bkgdnorm+','+nuis_theory+','+nuis_exp_time_flat
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
#for j in range(ntimebin): 
#    rbin = pois[j]

#Nominal fit
#cmd1 = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+NuisanceGroup+' --robustFit 1 '
#cmd1 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
#cmd1 += asi
#cmd1 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
#cmd1 += ' --algo grid --points '+str(npoints)+' '

#Nominal fit + snaphsot
cmd2 = 'combine -M MultiDimFit -n .snapshot_'+observable+'_'+year+'_'+NuisanceGroup #+' --robustFit 1 '
cmd2 += optim
cmd2 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root '
cmd2 += asi
#cmd2 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
cmd2 += ' --algo=singles  --saveWorkspace --saveFitResult'

cmd2_fd = 'combineTool.py -M FitDiagnostics ./higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root '
cmd2_fd += optim
cmd2_fd += asi
cmd2_fd += ' --plots '
cmd2_fd += ' -n .snapshot_'+observable+'_'+year+'_'+NuisanceGroup

#Stat. uncertainty only + snaphsot
cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root -n .freezeall_'+observable+'_'+year+'_'+NuisanceGroup+' '
cmd3 += optim
cmd3 += asi
#cmd3 += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
#cmd3 += ' --algo grid --points '+str(npoints*5)+' '
cmd3 += '--freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'
cmd3 += ' --algo=singles  --saveWorkspace --saveFitResult'

cmd3_fd = 'combineTool.py -M FitDiagnostics ./higgsCombine.freezeall_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root '
cmd3_fd += optim
cmd3_fd += asi
cmd3_fd += ' --plots '
cmd3_fd += ' -n .freezeall_'+observable+'_'+year+'_'+NuisanceGroup

#Fit removing group uncertainties + snapshots
cmd4 = []
for k in range(len(list_nuisgroups)):
    cmd_k = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root -n .freeze'+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+' '
    cmd_k += optim
    cmd_k += asi
    #cmd_k += '--parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range+' --floatOtherPOIs='+doFloatPOI
    #cmd_k += ' --algo grid --points '+str(npoints*3)+' '
    if (list_nuisgroups[k]=='autoMCStats'): 
	cmd_k += '--freezeNuisanceGroups '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
    else:
	cmd_k += '--freezeParameters '+list_nuisgroups[k]+' --snapshotName MultiDimFit'
    cmd_k += ' --algo=singles  --saveWorkspace --saveFitResult'
    cmd4.append(cmd_k)

cmd4_fd = []
for k in range(len(list_nuisgroups)):
    cmd_fd_k = 'combineTool.py -M FitDiagnostics ./higgsCombine.freeze'+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root '
    cmd_fd_k += optim
    cmd_fd_k += asi
    cmd_fd_k += ' --plots '
    cmd_fd_k += ' -n .freeze'+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+' '   
    cmd4_fd.append(cmd_fd_k)

#Plotting likelihood scan
#cmd5 = "python plot1DScan.py higgsCombine.nominal_"+observable+"_"+year+"_"+NuisanceGroup+".MultiDimFit.mH120.root --others "
#for k in range(len(list_nuisgroups)):
#	cmd5 += " 'higgsCombine.freeze"+list_nuisnames[k]+'_'+observable+'_'+year+'_'+NuisanceGroup+".MultiDimFit.mH120.root:Freeze_"+list_nuisnames[k]+":"+str(k+2)+"' "
#cmd5 += " 'higgsCombine.freezeall_"+observable+'_'+year+'_'+NuisanceGroup+".MultiDimFit.mH120.root:FreezeAll:1' "
#cmd5 += "-o freeze_all_"+year+" "
#cmd5 += "-o impacts/"+year+"/"+ observable + "_UncertaintyBreakdown_detailed_"+year+"_"+rbin+"_"+NuisanceGroup+" "
#cmd5 += "--POI "+rbin
#cmd5 += " --main-label "
#if (asimov=='asimov'): cmd5 += 'Asimov'
#cmd5 += " --breakdown "
#for k in range(len(list_nuisgroups)):
#	cmd5 += list_nuisnames[k] + ","
#cmd5 += "Others,Stat > impacts/"+year+"/" + observable + "_uncertainty_breakdown_detailed_"+rbin+"_"+NuisanceGroup+".log"

#cmd6 = 'cp freeze_all_'+year+'.pdf impacts/'+year+'/'
#if (asimov == 'asimov'): cmd6 += asimov+'/'
#cmd6 += observable + '_UncertaintyBreakdown_detailed_'+year+'_'+rbin+'_'+NuisanceGroup+'.pdf'

if (doPlotsOnly==True):
    print cmd2
    print cmd3
    for k in range(len(list_nuisgroups)):
        print cmd4[k]


if (doPlotsOnly==False):
    print cmd2
    os.system(cmd2)
    #print cmd2_fd
    #os.system(cmd2_fd)
    print cmd3
    os.system(cmd3)
    #print cmd3_fd
    #os.system(cmd3_fd)
    for k in range(len(list_nuisgroups)):
        print cmd4[k]
        os.system(cmd4[k])
    #for k in range(len(list_nuisgroups)):
	#print cmd4_fd[k]
	#os.system(cmd4_fd[k])

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

total_uncert_up_allbins = []
total_uncert_down_allbins = []
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

tree_map = []
for i in range(ntimebin):
    tree_map.append(0)

#for j in range(1):
for j in range(ntimebin):
    rbin = pois[j]

    #file = open('impacts/'+year+'/'+observable+'_uncertainty_breakdown_detailed_'+rbin+'_'+NuisanceGroup+'.log')

    value_central = []
    total_uncert_up = []
    total_uncert_down = []
    individual_uncert_up = []
    individual_uncert_down = []
    individual_uncert_avg = []

    #for k in range(1):
    for k in range(len(list_nuisnames)):

	if k==0:
	    filein = TFile("./higgsCombine.snapshot_"+observable+"_"+year+"_"+NuisanceGroup+".MultiDimFit.mH120.root")
	if k>0 and k<len(list_nuisnames)-1:
	    filein = TFile("./higgsCombine.freeze"+list_nuisnames[k]+"_"+observable+"_"+year+"_"+NuisanceGroup+".MultiDimFit.mH120.root")
	if k==len(list_nuisnames)-1:
	    filein = TFile("./higgsCombine.freezeall_"+observable+"_"+year+"_"+NuisanceGroup+".MultiDimFit.mH120.root")

        tree = filein.Get("limit")

	if j==0 and k==0:
	    ib=0
	    for b in tree.GetListOfBranches():
		if b.GetName().find("r_")!=-1:
		    num = int(b.GetName()[2:])
		    tree_map[num] = ib
		    print b.GetName() + ' ' + str(num)
		    ib += 1

	tree.GetEvent(0)
	value_central.append(tree.GetLeaf(rbin).GetValue())

	#for l in range(ntimebin): 
	tree.GetEvent(1+2*tree_map[j])
	unc_down = tree.GetLeaf(rbin).GetValue()
        tree.GetEvent(1+2*tree_map[j]+1)
	unc_up = tree.GetLeaf(rbin).GetValue()
	    #val = tree.GetLeaf(rbin).GetValue()
	    #if (val<1):
	        #unc_down = val
	    #if (val>1):
		#unc_up = val
	#val = 1
	total_uncert_up.append(unc_up-1)
	total_uncert_down.append(abs(unc_down-1))
	#individual_uncert_up.append(unc_up-1)
        #individual_uncert_down.append(unc_down-1)

	#print 'j='+str(j)+' '+rbin+' mu='+str(val)+' mu_up='+str(unc_up)+' mu_down='+str(unc_down) 
	filein.Close()

    total_uncert_up_allbins.append(total_uncert_up)
    total_uncert_down_allbins.append(total_uncert_down)

    for k in range(len(list_nuisnames)):
	if k==0 or k==len(list_nuisnames)-1:
	    individual_uncert_down.append(total_uncert_down[k])
	    individual_uncert_up.append(total_uncert_up[k])
	if k!=0 and k!=len(list_nuisnames)-1:
	    if (total_uncert_down[0]*total_uncert_down[0]-total_uncert_down[k]*total_uncert_down[k]>0):
		individual_uncert_down.append(math.sqrt(total_uncert_down[0]*total_uncert_down[0]-total_uncert_down[k]*total_uncert_down[k]))
	    else:
		individual_uncert_down.append(0)
            if (total_uncert_up[0]*total_uncert_up[0]-total_uncert_up[k]*total_uncert_up[k]>0):
		individual_uncert_up.append(math.sqrt(total_uncert_up[0]*total_uncert_up[0]-total_uncert_up[k]*total_uncert_up[k]))
	    else:
		individual_uncert_up.append(0)

    for k in range(len(list_nuisnames)):
	#if k!=0 and k!=len(list_nuisnames)-1:
	individual_uncert_avg.append((individual_uncert_up[k]+individual_uncert_down[k])/2.)
	#else:
	 #   individual_uncert_avg.append((individual_uncert_up[k]-individual_uncert_down[k])/2.)

    individual_uncert_down_allbins.append(individual_uncert_down)
    individual_uncert_up_allbins.append(individual_uncert_up)
    individual_uncert_avg_allbins.append(individual_uncert_avg)


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


#######################################
## Get covariance matrices and jacobian
#######################################

hCorr = []
hCorrPOI = []
fCovar = []

#fCovarPrefix = "./fitDiagnostics"
fCovarPrefix = "./multidimfit"

doSubtractCovar=True
#doSubtractCovar=False

#Get the correlation matrices for POI 
for k in range(len(list_nuisnames)):

    hCorrPOI.append(TH2F("correlation_fit_s_POI"+list_nuisnames[k],"correlation_fit_s_POI"+list_nuisnames[k],24,0,24,24,0,24))
    #print hCorrPOI[-1].GetName()
    #print str(k)+" "+fCovar[k].GetName()

    if k==0:
	fCovar.append(TFile(fCovarPrefix+".snapshot_"+observable+"_"+year+"_"+NuisanceGroup+".root"))
    if k>0 and k<len(list_nuisnames)-1:
	#if list_nuisnames[k]!="hdamp":
	fCovar.append(TFile(fCovarPrefix+".freeze"+list_nuisnames[k]+"_"+observable+"_"+year+"_"+NuisanceGroup+".root"))
	#else:
	#fCovar.append(TFile(fCovarPrefix+".freeze"+list_nuisnames[k]+"_"+observable+"_"+year+"_"+NuisanceGroup+"_testToys.root"))
    if k==len(list_nuisnames)-1:
	fCovar.append(TFile(fCovarPrefix+".freezeall_"+observable+"_"+year+"_"+NuisanceGroup+".root"))

    if fCovarPrefix == "./fitDiagnostics":
	hCorr.append(fCovar[k].Get("covariance_fit_s").Clone())
	for i in range(24):
	    for j in range(24):
		corrval = hCorr[k].GetBinContent(hCorr[k].GetXaxis().FindBin("r_"+str(i)), hCorr[k].GetYaxis().FindBin("r_"+str(j)))
		#print str(k)+" "+str(i)+" "+str(j)+" "+str(corrval)
		hCorrPOI[k].SetBinContent(i+1,j+1,corrval)

    elif fCovarPrefix == "./multidimfit":
	fitResult = fCovar[k].Get("fit_mdf")
	print list_nuisnames[k]+" Minuit Covariance quality: "+str(fitResult.covQual())
        for i in range(24):
            for j in range(24):
                corrval = fitResult.correlation("r_"+str(i), "r_"+str(j))
                #print str(k)+" "+str(i)+" "+str(j)+" "+str(corrval)
		hCorrPOI[k].SetBinContent(i+1,j+1,corrval)


#Compute up/down covariance matrices
doToysCovariance=False
hCovUp = []
hCovDown = []
for k in range(len(list_nuisnames)):
    if (list_nuisnames[k]=="hdamp" or list_nuisnames[k]=="bkgd_norm") and year=="Comb" and doToysCovariance==True:
	print "Open "+"covariance_fromToys_"+observable+"_"+year+"_"+NuisanceGroup+"_freeze"+list_nuisnames[k]+".root"
    	externalFile = TFile("covariance_fromToys_"+observable+"_"+year+"_"+NuisanceGroup+"_freeze"+list_nuisnames[k]+".root")
	#hCovUp.append(externalFile.Get("hCov_sample").Clone())
	#hCovDown.append(externalFile.Get("hCov_sample").Clone())
    	hCovUp.append(externalFile.Get("hCovUp_mean").Clone())
        hCovDown.append(externalFile.Get("hCovDown_mean").Clone())
        for i in range(24):
            for j in range(24):
        	print(list_nuisnames[k]+' r_'+str(i)+' r_'+str(j)+' covUpVal='+str(hCovUp[-1].GetBinContent(1+i,1+j))+' covDownVal='+str(hCovDown[-1].GetBinContent(1+i,1+j)))
    else:
	hCovUp.append(TH2F("correlation_matrix_up"+list_nuisnames[k],"correlation_matrix_up"+list_nuisnames[k],24,0,24,24,0,24))
	hCovDown.append(TH2F("correlation_matrix_down"+list_nuisnames[k],"correlation_matrix_down"+list_nuisnames[k],24,0,24,24,0,24))
	for i in range(24):
	    for j in range(24):
		corrval = hCorrPOI[k].GetBinContent(1+i,1+j)
		covUpVal = corrval * total_uncert_up_allbins[i][k] * total_uncert_up_allbins[j][k] #multiply by predicted number of events in bins i and j
		covDownVal = corrval * total_uncert_down_allbins[i][k] * total_uncert_down_allbins[j][k] #multiply by predicted number of events in bins i and j
		print(list_nuisnames[k]+' r_'+str(i)+' r_'+str(j)+' corrVal='+str(corrval)+' covUpVal='+str(covUpVal)+' covDownVal='+str(covDownVal))
		hCovUp[k].SetBinContent(1+i, 1+j, covUpVal)
		hCovDown[k].SetBinContent(1+i, 1+j, covDownVal)


#Substract covariance matrices to total covariance matrix
hCovSubtractedUp = [] 
hCovSubtractedDown = []
for k in range(len(list_nuisnames)):
    print str(list_nuisnames[k])
    if k==0 or k==len(list_nuisnames)-1:
	hCovSubtractedUp.append(hCovUp[k].Clone())
        hCovSubtractedDown.append(hCovDown[k].Clone()) 
    else:
        hCovSubtractedUp.append(TH2F("covariance_fit_s_substracted_up"+list_nuisnames[k],"covariance_fit_s_substracted_up"+list_nuisnames[k],24,0,24,24,0,24))
        hCovSubtractedDown.append(TH2F("covariance_fit_s_substracted_down"+list_nuisnames[k],"covariance_fit_s_substracted_down"+list_nuisnames[k],24,0,24,24,0,24))
    for i in range(24):
	for j in range (24):
	    if k!=0 and k!=len(list_nuisnames)-1:
		rho = 0
		#if list_nuisnames[k]=="hdamp" or list_nuisnames[k]=="bkgd_norm" or list_nuisnames[k]=="theory":
		#rho = 0.01
	        hCovSubtractedUp[k].SetBinContent(1+i,1+j,hCovUp[0].GetBinContent(1+i,1+j)-hCovUp[k].GetBinContent(1+i,1+j)-rho*math.sqrt(hCovUp[0].GetBinContent(1+i,1+j)*hCovUp[k].GetBinContent(1+i,1+j)))
                hCovSubtractedDown[k].SetBinContent(1+i,1+j,hCovDown[0].GetBinContent(1+i,1+j)-hCovDown[k].GetBinContent(1+i,1+j)-rho*math.sqrt(hCovDown[0].GetBinContent(1+i,1+j)*hCovDown[k].GetBinContent(1+i,1+j)))

    #plot2Dmatrix(hCovSubtracted[k], observable+"_CorrelationMatrix_"+list_nuisnames[k]+"_"+year, False)

#Compute Jacobian
#ntimebin = 24
ttbar_yield = []
for i in range(24):  #To be revisited for data (where it will be needed to do it for each of the nuisance group since mu can change)
    ttbar_yield.append(1.)
    print ttbar_yield[-1]
mu_avg = sum(ttbar_yield)/ntimebin
print 'mu_avg='+str(mu_avg)

hJacobian = TH2F("jacobian","jacobian",24,0,24,24,0,24)

jacobian_val  = 0.
for i in range(24):
    for j in range(24):
        jacobian_val = -ttbar_yield[i]/ntimebin
	#print str(ttbar_yield[i])+" "+str(ntimebin)+" "+str(jacobian_val)
        if (i==j):
            jacobian_val = jacobian_val + mu_avg
        jacobian_val = jacobian_val / (mu_avg*mu_avg)
        hJacobian.SetBinContent(1+i, 1+j, jacobian_val)
	#print "i="+str(i)+" j="+str(j)+" jacobian="+str(hJacobian.GetBinContent(1+i, 1+j))

#Compute normalized differential cross section
individual_uncert_up_allbins_norm = []
individual_uncert_down_allbins_norm = []
individual_uncert_avg_allbins_norm = []

mu_norm_eachNuis = []
mu_norm_up_eachNuis = []
mu_norm_down_eachNuis = []

for k in range(len(list_nuisnames)):
    matrix_Jacobian = np.zeros((ntimebin,ntimebin))
    matrix_JacobianTranspose = np.zeros((ntimebin,ntimebin))
    matrix_CovUp = np.zeros((ntimebin,ntimebin))
    matrix_CovDown = np.zeros((ntimebin,ntimebin))
    for i in range(24):
        for j in range(24):
            matrix_Jacobian[i][j] = hJacobian.GetBinContent(1+i, 1+j)
            matrix_JacobianTranspose[i][j] = hJacobian.GetBinContent(1+j, 1+i)
	    if doSubtractCovar==True:
                matrix_CovUp[i][j] = hCovSubtractedUp[k].GetBinContent(1+i, 1+j)
                matrix_CovDown[i][j] = hCovSubtractedDown[k].GetBinContent(1+i, 1+j)
	    elif doSubtractCovar==False:
		matrix_CovUp[i][j] = hCovUp[k].GetBinContent(1+i, 1+j)
		matrix_CovDown[i][j] = hCovDown[k].GetBinContent(1+i, 1+j)
    matrix_CovNormUp = matrix_Jacobian.dot(matrix_CovUp).dot(matrix_JacobianTranspose)
    matrix_CovNormDown = matrix_Jacobian.dot(matrix_CovDown).dot(matrix_JacobianTranspose)

    mu_norm = []
    mu_norm_up = []
    mu_norm_down = []
    for i in range(24):
        mu_norm.append(ttbar_yield[i]/mu_avg)
	if doSubtractCovar==True:
	    if (matrix_CovNormUp[i][i]>0): 
		mu_norm_up.append(math.sqrt(matrix_CovNormUp[i][i]))
	    else:
		mu_norm_up.append(0.)
	    if (matrix_CovNormDown[i][i]>0):
		mu_norm_down.append(math.sqrt(matrix_CovNormDown[i][i]))
	    else:
		mu_norm_down.append(0.)
	elif doSubtractCovar==False:
	    if k==0 or k==len(individual_uncert_up)-1:
		if (matrix_CovNormUp[i][i]>0):
		    mu_norm_up.append(math.sqrt(matrix_CovNormUp[i][i]))
		else:
		    mu_norm_up.append(0.)
		if (matrix_CovNormDown[i][i]>0):
		    mu_norm_down.append(math.sqrt(matrix_CovNormDown[i][i]))
		else:
		    mu_norm_down.append(0.)
	    else:
		if (mu_norm_up_eachNuis[0][i]*mu_norm_up_eachNuis[0][i]-matrix_CovNormUp[i][i]>0):
		    mu_norm_up.append(math.sqrt(mu_norm_up_eachNuis[0][i]*mu_norm_up_eachNuis[0][i]-matrix_CovNormDown[i][i]))
		else:
		    mu_norm_up.append(0.)
		if (mu_norm_down_eachNuis[0][i]*mu_norm_down_eachNuis[0][i]-matrix_CovNormUp[i][i]>0):
		    mu_norm_down.append(math.sqrt(mu_norm_down_eachNuis[0][i]*mu_norm_down_eachNuis[0][i]-matrix_CovNormDown[i][i]))
		else:
		    mu_norm_down.append(0.)
        print('Normalized differential cross section, bin '+str(i)+' mu_norm='+str(mu_norm[i])+' +'+str(mu_norm_up[i])+' -'+str(mu_norm_down[i]))
    mu_norm_eachNuis.append(mu_norm)
    mu_norm_up_eachNuis.append(mu_norm_up)
    mu_norm_down_eachNuis.append(mu_norm_down)   

#Transpose individual_uncert_up_allbins_norm, etc, to make it same format as the un-normalized uncertainties.
for i in range(24):
    mu_norm_eachBin = []
    mu_norm_up_eachBin = []
    mu_norm_down_eachBin = []
    for k in range(len(list_nuisnames)):
        mu_norm_eachBin.append(mu_norm_eachNuis[k][i])
        mu_norm_up_eachBin.append(mu_norm_up_eachNuis[k][i])
	#if k==0 or k==len(individual_uncert_up)-1:
        #    mu_norm_down_eachBin.append(-mu_norm_down_eachNuis[k][i])
        #if k!=0 and k!=len(individual_uncert_up)-1:
	mu_norm_down_eachBin.append(mu_norm_down_eachNuis[k][i])
    individual_uncert_up_allbins_norm.append(mu_norm_up_eachBin)
    individual_uncert_down_allbins_norm.append(mu_norm_down_eachBin)

###################
## Plotting
###################

def plotUncerainties(doNormBreakDown):
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
	    #uncert_bin = individual_uncert_avg_allbins[j]
	    if doNormBreakDown==False:
		uncert_binUp = individual_uncert_up_allbins[j]
		uncert_binDown = individual_uncert_down_allbins[j]
	    if doNormBreakDown==True:
		uncert_binUp = individual_uncert_up_allbins_norm[j]
		uncert_binDown = individual_uncert_down_allbins_norm[j]
	    #h.Fill(j+0.5, 100*uncert_bin[k])
	    hUp.Fill(j+0.5, 100*uncert_binUp[k])
	    #if k!=0 and k!=len(individual_uncert_up)-1: 
	    hDown.Fill(j+0.5, -100*uncert_binDown[k])
	    #else:
	#	hDown.Fill(j+0.5, 100*uncert_binDown[k])
	#h_uncert.append(h)
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
	    #h_uncert[k].SetLineColor(getcolor(k+1))
	    #h_uncert[k].SetLineWidth(2)
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

    resultname = './impacts/'+year+'/'+observable+'_differential_'+nuisancegroup+'_'+year+'_algosingles'
    if doNormBreakDown==True:
	resultname += '_norm'
    canvas.SaveAs(resultname+'.pdf')
 
    #raw_input()

plotUncerainties(False)
plotUncerainties(True)


#raw_input()
#exit()
