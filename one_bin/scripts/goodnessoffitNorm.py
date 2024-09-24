import os, sys
import argparse 

sys.path.append('./')

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TLine,TGraphAsymmErrors
from ROOT import TStyle, gStyle, TColor, TLatex

import math

from tools.style_manager import *
#from tools.sample_manager import *
import array

import tools.tdrstyle as tdr
tdr.setTDRStyle()

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
#parser.add_argument('wilson', help='display your wilson coefficient')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')
#parser.add_argument('title', help='display your observable title')
#parser.add_argument('timebin', help='display the time bin')
parser.add_argument('algo', help='algorithm (saturated, KS, AD)')
parser.add_argument('muValue', help='set default value of signal strength to generate toys')


args = parser.parse_args()
observable = args.observable
year = args.year
algo = args.algo
muValue = args.muValue

#wilson = args.wilson
#asimov = args.asimov
'''#title = args.title
timebin = int(args.timebin)
stimebin="";
if (timebin==-1):
     stimebin = "_puold";
if (timebin==-2):
     stimebin = "_punew";
if (timebin==-3):
     stimebin = "_puinc";
if (timebin>=0):
     stimebin = "_put"+str(timebin);    
'''

#asi = ''
#sasimov=''
#if asimov == 'asimov':
#    print '################'
#    print '# Asimov test : '
#    print '################'    
#    print ''
#    asi = '--expectSignal 1 -t -1'
#    sasimov = '_asimov'
#else:
#    sasimov = '_data'

#def asimov_param(asimov):
#    if asimov == 'asimov':
#        return '--expectSignal 1 -t -1'
#    else:
#        return ''

#doFit = False
doFit = True

pois = []
pois.append("r_avg")
for i in range(23):
    pois.append('f_'+str(i))
#for i in range(24):
#    pois.append('r_'+str(i))

if muValue=='muSM':
    defaultVal = '1'
if muValue=='muIncData':
    if year=='2016':
	defaultVal = '0.94'
    if year=='2017':
	defaultVal = '0.97'
    if year=='Comb':
	defaultVal = '0.95'

param = ' --setParameters '
for i in range(24):
    param += pois[i]+'='+defaultVal
    if i != 23:
        param += ','

'''
param = ' --floatParameters '
for i in range(24):
    param += pois[i]
    if i != 23:
        param += ','
'''

'''
if len(wilson.split(","))==1:
    param = ' --setParameters '+wilson+'=0'
    param += ' --setParameterRanges '+wilson+'=-30,30 '
else:
    wlist = wilson.split(",")
    param = ' --setParameters '
    for w in wlist:
	param += w+'=0'
	if w!=wlist[-1]:
	    param += ','
    param += ' --setParameterRanges '
    for w in wlist:
	param += w+'=-100,100'
	if w!=wlist[-1]:
            param += ':'
    param += ' '
'''

#ntoys=500
ntoys=300
#ntoys=1

###################
## GoodnessOfFit
###################



print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'
'''
if len(wilson.split(","))==1:
    wilsonserie = wilson
else:
    wilsonserie = ''
    for w in wlist:
        wilsonserie += w
        if w!=wlist[-1]:
            wilsonserie += '_'
'''

#Data fit
cmd1 = 'combine -M GoodnessOfFit inputs/combine_'+observable+'_24bins_'+year+'_workspace_norm.root '
cmd1 += param
cmd1 += ' --algo='+algo+' -n .data_'+observable+'_'+year+'_'+algo+'_'+muValue+'_normfit'

#MC toys
cmd2 = 'combine -M GoodnessOfFit inputs/combine_'+observable+'_24bins_'+year+'_workspace_norm.root '
cmd2 += param
if algo=='saturated':
    cmd2 += ' --algo=saturated --toysFreq -t '+str(ntoys)
else:
    cmd2 += ' --algo='+algo+' -t '+str(ntoys)
cmd2 += ' -n .mctoys_'+observable+'_'+year+'_'+algo+'_'+muValue+'_normfit'

print cmd1
print cmd2

if doFit:
    os.system(cmd1)
    os.system(cmd2)

fData = TFile('higgsCombine.data_'+observable+'_'+year+'_'+algo+'_'+muValue+'_normfit.GoodnessOfFit.mH120.root')
tData = fData.Get('limit')
tData.GetEvent(0)
val_data = tData.GetLeaf('limit').GetValue()
print str(val_data)

fMC = TFile('higgsCombine.mctoys_'+observable+'_'+year+'_'+algo+'_'+muValue+'_normfit.GoodnessOfFit.mH120.123456.root')
tMC = fMC.Get('limit')
val_MC_min=9999999
val_MC_max=0
val_MC = []
for i in range(ntoys):
    tMC.GetEvent(i)
    val_MC.append(tMC.GetLeaf('limit').GetValue())
    if val_MC_max<val_MC[-1]: 
	val_MC_max = val_MC[-1]
    if val_MC_min>val_MC[-1]:
	val_MC_min=val_MC[-1]


windowSpace = 5
if algo=='KS':
    windowSpace = 0.01
if algo=='AD':
    windowSpace = 1.

hMC = TH1F('GoF_MC','GoF_MC',1000,min(val_MC_min,val_data)-windowSpace,max(val_MC_max,val_data)+windowSpace)
for val in val_MC:
   hMC.Fill(val)
hMC.Scale(1./hMC.Integral())

Canvas = TCanvas("GoF","GoF",800,600)
hMC.SetLineColor(4)
hMC.SetYTitle('normalized')
hMC.SetXTitle('GoF value')
hMC.Draw("HIST")

lineData = TLine(val_data,0,val_data,hMC.GetMaximum()*0.9)
lineData.SetLineWidth(2)
lineData.SetLineColor(2)
lineData.Draw("same")

legend = TLegend(0.66,0.75,0.93,0.94, "Differential fit: "+year)
#if len(wilson.split(","))!=1:
#    legend.SetTextSize(0.027)
legend.AddEntry(hMC, 'MC', 'l')
legend.AddEntry(lineData, 'Data', 'l')
legend.Draw("same")

pvalue = hMC.Integral(hMC.FindBin(val_data),hMC.GetNbinsX())
print 'p-value: '+str(pvalue)

latex = TLatex()
latex.SetTextSize(0.75*gStyle.GetPadTopMargin());
latex.SetNDC();
latex.DrawLatex(0.6,0.65,algo+" #mu="+str(defaultVal)+" p-value: "+str(round(pvalue,3)));


if(year=='2016'):
    tdr.cmsPrel(36300., 13.,simOnly=False,thisIsPrelim=True)
elif(year=='2017'):
    tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)
elif (year=='Comb'):
    tdr.cmsPrel(77800., 13.,simOnly=False,thisIsPrelim=True)


Canvas.SaveAs('impacts/'+year+'/goodnessOfFit_differential_'+observable+'_'+year+'_'+algo+'_'+muValue+'_normfit.pdf')

#raw_input()
exit()


