import os, sys
import math
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('nuisancegroup', help='nuisance group', default='')
#parser.add_argument('wilson', help='display your wilson coefficient')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
#wilson = args.wilson
asimov = args.asimov
year = args.year
nuisancegroup = args.nuisancegroup


if nuisancegroup=='time_breakdown':
    NuisanceGroup = "time_flat_uncorr_corr_mcstat"
if nuisancegroup=='kind_breakdown':
    NuisanceGroup = "exp_theory_bkgdnorm_lumi_mcstat"
if nuisancegroup=='exp_breakdown':
    NuisanceGroup = "exp_elec_muon_pu_btag_jec_trigger_prefiring"
if nuisancegroup=='theory_breakdown':
    NuisanceGroup = "theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco"



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


nuis_exp_time_corr = 'rgx{emu_trig_.*}'
nuis_exp_time_uncorr = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*},rgx{syst_muon_iso.*},rgx{syst_muon_id.*},rgx{syst_pu.*},rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*},rgx{syst_prefiring.*},rgx{.*jec.*}'
nuis_exp = nuis_exp_time_corr+','+nuis_exp_time_uncorr

nuis_exp_elec = 'rgx{syst_elec_reco.*},rgx{syst_elec_id.*}'
nuis_exp_muon = 'rgx{syst_elec_id.*},rgx{syst_muon_iso.*}'
nuis_exp_pu = 'rgx{syst_pu.*}'
nuis_exp_btag = 'rgx{syst_b_correlated.*},rgx{syst_b_uncorrelated.*},rgx{syst_l_correlated.*},rgx{syst_l_uncorrelated.*}'
nuis_exp_jec = 'rgx{.*jec.*}'
nuis_exp_prefiring = 'rgx{syst_prefiring.*}'
nuis_exp_trigger = 'rgx{emu_trig_.*}'

nuis_mcstat = 'autoMCStats'

nuis_sme_singletop = 'sme_decay'

nuis_time_flat = nuis_lumi_time_uncorr+','+nuis_bkgdnorm+','+nuis_theory
nuis_time_corr = nuis_lumi_time_corr+','+nuis_exp_time_corr+','+nuis_sme_singletop

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


nuisnames_remain = "Others"
#nuisnames_remain = "MCstat"

print("Checking "+str(len(list_nuisgroups))+" groups of nuisances")
print list_nuisnames



###################
## Loop  over wilson coefficients
###################


def asimov_param(w):
    if asimov == 'asimov':
        return '--setParameters '+w+'=0 -t -1'

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

unc_total_pos = []
unc_total_neg = []
unc_noMCStats_pos = []
unc_noMCStats_neg = []
unc_noSyst_pos = []
unc_noSyst_neg = []

npoints=10

wilson_list_all = ['cLXX'] #for testing

for wilson in wilson_list_all:

    #Nominal fit
    cmd1 = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+NuisanceGroup+' --robustFit 1 '
    cmd1 +=' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root '
    cmd1 += asimov_param(wilson) + ' --algo grid --points '+str(npoints)

    #Snaphsot
    cmd2 = 'combine -M MultiDimFit -n .snapshot_'+observable+'_'+year+'_'+NuisanceGroup+' --algo=singles --robustFit 1 '
    cmd2 +=' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root ' 
    cmd2 += asimov_param(wilson) +' --saveWorkspace'

    #MC stat
    #cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH120.root -n .freezeMCStats '+asimov_param(wilson)+' --algo grid --points 30 --freezeNuisanceGroups autoMCStats --snapshotName MultiDimFit'

    #Stat. uncertainty only
    cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot_'+observable+'_'+year+'_'+NuisanceGroup+'.MultiDimFit.mH120.root '
    cmd3 += '-n .freezeall_'+observable+'_'+year+'_'+NuisanceGroup +' '
    cmd3 += asimov_param(wilson)+' --algo grid --points '+str(npoints*5)+' '
    cmd3 += '--freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

    #Fit removing group uncertainties
    cmd4 = []
    for k in range(len(list_nuisgroups)):


    #Plotting likelihood scan
    cmd5 = "python plot1DScan.py higgsCombine.nominal.MultiDimFit.mH120.root --others 'higgsCombine.freezeMCStats.MultiDimFit.mH120.root:FreezeMCStats:2' 'higgsCombine.freezeall.MultiDimFit.mH120.root:FreezeAll:4' -o freeze_MCStats_all --POI "+wilson+" --main-label "
    if (asimov=='asimov'): cmd5 += 'Asimov'
    cmd5 += " --breakdown MCStats,Syst,Stat > uncertainty_breakdown_"+wilson+".log"

    os.system(cmd1)
    os.system(cmd2)
    #os.system(cmd3)
    os.system(cmd4)
    os.system(cmd5)

    cmd6 = 'cp freeze_MCStats_all.pdf impacts/'+year+'/'
    if (asimov == 'asimov'): cmd6 += asimov+'/'
    cmd6 += 'UncertaintyBreakdown_'+year+'_'+wilson+'.pdf'
    os.system(cmd6)


    file = open('uncertainty_breakdown_'+wilson+'.log')
  
    i=0 
    for line in file:
        uncert = 0
        for word in line.split():
            #print(str(i)+' '+word)
	    if (i==4): unc_total_neg.append(float(word[:-1]))
	    if (i==6): unc_total_pos.append(float(word[:-1]))
	    if (i==20): unc_noMCStats_neg.append(float(word[:-1]))
            if (i==22): unc_noMCStats_pos.append(float(word[:-1]))
            if (i==36): unc_noSyst_neg.append(float(word[:-1]))
            if (i==38): unc_noSyst_pos.append(float(word[:-1]))
            i = i+1

    file.close()


sys.stdout = open('impacts/'+year+'/'+asimov+'/Table_UncertaintyBreakdown.txt', 'w')

print '\\begin{table}[h!]'
print '\\begin{center}'
print '\\begin{tabular}{|c|c|c|c|c|}'
print '\\hline '
print 'Wilson coefficient & Total ($\\times 10^{-3}$) & MCStats ($\\times 10^{-3}$) & Syst ($\\times 10^{-3}$) & Stat ($\\times 10^{-3}$) \\\\'
print '\\hline '

for i in range(len(wilson_list_all)):
    #print i
    if (i==0 or i==4 or i==8 or i==12): print '\\hline '
    text = '$'+getwilsontext(wilson_list_all[i]) + '$ & $0 ^{+' + str(round(unc_total_pos[i], 3)) + '}_{' + str(round(unc_total_neg[i], 3))+ '}$ ' 
    #print unc_total_pos[i]
    #print unc_total_neg[i]
    #print unc_noMCStats_pos[i] 
    #print unc_noMCStats_neg[i]
    MCStats_pos = math.sqrt(unc_total_pos[i]*unc_total_pos[i]-unc_noMCStats_pos[i]*unc_noMCStats_pos[i])
    MCStats_neg = math.sqrt(unc_total_neg[i]*unc_total_neg[i]-unc_noMCStats_neg[i]*unc_noMCStats_neg[i])
    if (round(MCStats_pos,3)!=round(MCStats_neg,3)): text += '& $^{+' + str(round(MCStats_pos,3))+ '}_{-' + str(round(MCStats_neg,3))+ '}$ '
    else: text += '& $ \pm ' + str(round(MCStats_pos,3))+ '$ '
    Syst_pos = math.sqrt(unc_noMCStats_pos[i]*unc_noMCStats_pos[i]-unc_noSyst_pos[i]*unc_noSyst_pos[i])
    Syst_neg = math.sqrt(unc_noMCStats_neg[i]*unc_noMCStats_neg[i]-unc_noSyst_neg[i]*unc_noSyst_neg[i])
    if (round(Syst_pos,3)!=round(Syst_neg,3)): text += '& $^{+' + str(round(Syst_pos,3))+ '}_{-' + str(round(Syst_neg,3))+ '}$ '
    else: text += '& $ \pm ' + str(round(Syst_pos,3))+ '$ '
    Stat_pos = math.sqrt(unc_total_pos[i]*unc_total_pos[i]-MCStats_pos*MCStats_pos-Syst_pos*Syst_pos)
    Stat_neg = math.sqrt(unc_total_neg[i]*unc_total_neg[i]-MCStats_neg*MCStats_neg-Syst_neg*Syst_neg)
    if (round(Stat_pos,3)!=round(Stat_neg,3)): text += '& $^{+' + str(round(Stat_pos,3))+ '}_{-' + str(round(Stat_neg,3))+ '}$ \\\\'
    else: text += '& $ \pm ' + str(round(Stat_pos,3))+ '$ \\\\'
    print text

print '\\hline '
print '\\end{tabular}'
print '\\caption{\\label{SMEfit_Comb_Breakdown}Uncertainty breakdown on the measurement of the SME coefficients, combining 2016 and 2017 analyses (assuming Asimov dataset).}'
print '\\end{center}'
print '\\end{table}'

sys.stdout.close()


