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
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')
#parser.add_argument('title', help='display your observable title')
parser.add_argument('timebin', help='display the time bin')

args = parser.parse_args()
observable = args.observable
year = args.year
#asimov = args.asimov
#title = args.title
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


doFit = False
#doFit = True

rbin='r'
r_range='0.8,1.2'
npoints=20

###################
## FitDiagnostics
###################



print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'

#Data fit
cmd1 = 'combine -M GoodnessOfFit inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root --algo=saturated -n .data_'+observable+'_'+year+stimebin

#MC toys
ntoys=500
cmd2 = 'combine -M GoodnessOfFit inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root --algo=saturated --toysFreq -t '+str(ntoys)+' -n .mctoys_'+observable+'_'+year+stimebin
   
if doFit:
    os.system(cmd1)
    os.system(cmd2)

fData = TFile('higgsCombine.data_'+observable+'_'+year+stimebin+'.GoodnessOfFit.mH120.root')
tData = fData.Get('limit')
tData.GetEvent(0)
val_data = tData.GetLeaf('limit').GetValue()
print str(val_data)

fMC = TFile('higgsCombine.mctoys_'+observable+'_'+year+stimebin+'.GoodnessOfFit.mH120.123456.root')
tMC = fMC.Get('limit')
val_MC_max=0
val_MC = []
for i in range(ntoys):
    tMC.GetEvent(i)
    val_MC.append(tMC.GetLeaf('limit').GetValue())
    if val_MC_max<val_MC[-1]: 
	val_MC_max = val_MC[-1]

hMC = TH1F('GoF_MC','GoF_MC',1000,0,val_MC_max+1)
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

legend = TLegend(0.66,0.75,0.93,0.94, "Time-integrated fit")
#legend.SetTextSize(0.023)
legend.AddEntry(hMC, 'MC', 'l')
legend.AddEntry(lineData, 'Data', 'l')
legend.Draw("same")

pvalue = hMC.Integral(hMC.FindBin(val_data),hMC.GetNbinsX())
print 'p-value: '+str(pvalue)

latex = TLatex()
latex.SetTextSize(0.75*gStyle.GetPadTopMargin());
latex.SetNDC();
latex.DrawLatex(0.7,0.65,"p-value: "+str(round(pvalue,3)));


if(year=='2016'):
    tdr.cmsPrel(36300., 13.,simOnly=False,thisIsPrelim=True)
elif(year=='2017'):
    tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)
elif (year=='Comb'):
    tdr.cmsPrel(77800., 13.,simOnly=False,thisIsPrelim=True)


Canvas.SaveAs('impacts/'+year+'/goodnessOfFit_'+observable+'_'+year+stimebin+'.pdf')

raw_input()
exit()


