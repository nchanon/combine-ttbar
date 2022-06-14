import os, sys
import math
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
#parser.add_argument('wilson', help='display your wilson coefficient')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
#wilson = args.wilson
asimov = args.asimov
year = args.year



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

#wilson_list_all = ['cLXX']

for wilson in wilson_list_all:

    cmd1 = 'combine -M MultiDimFit -n .nominal --robustFit 1 ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root '+asimov_param(wilson)+ ' --algo grid --points 30'

    cmd2 = 'combine -M MultiDimFit -n .snapshot --algo=singles --robustFit 1 ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root ' + asimov_param(wilson) +' --saveWorkspace'

    cmd3 = 'combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH120.root -n .freezeMCStats '+asimov_param(wilson)+' --algo grid --points 30 --freezeNuisanceGroups autoMCStats --snapshotName MultiDimFit'

    cmd4 = 'combine -M MultiDimFit higgsCombine.snapshot.MultiDimFit.mH120.root -n .freezeall '+asimov_param(wilson)+' --algo grid --points 30 --freezeParameters allConstrainedNuisances --snapshotName MultiDimFit'

    cmd5 = "python plot1DScan.py higgsCombine.nominal.MultiDimFit.mH120.root --others 'higgsCombine.freezeMCStats.MultiDimFit.mH120.root:FreezeMCStats:2' 'higgsCombine.freezeall.MultiDimFit.mH120.root:FreezeAll:4' -o freeze_MCStats_all --POI "+wilson+" --main-label "
    if (asimov=='asimov'): cmd5 += 'Asimov'
    cmd5 += " --breakdown MCStats,Syst,Stat > uncertainty_breakdown_"+wilson+".log"

    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)
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


sys.stdout = open('impacts/'+year+'/'+asimov+'/Table_UncertaintyBreakdown_'+observable+'.txt', 'w')

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


