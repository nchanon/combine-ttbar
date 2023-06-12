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

#ntoys=100: fit 100 toys + data
#ntoys!=100: fit ntoys (and not data). 
parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('wilson', help='display your wilson coefficient')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')
#parser.add_argument('title', help='display your observable title')
#parser.add_argument('timebin', help='display the time bin')
parser.add_argument('ntoys', help='display your number of toys',default='100')
parser.add_argument('seed', help='display your seed',default='123456')


args = parser.parse_args()
observable = args.observable
year = args.year
wilson = args.wilson
ntoys = int(args.ntoys)
seed = int(args.seed)

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

#ntoys=100

###################
## GoodnessOfFit
###################



print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'

if len(wilson.split(","))==1:
    wilsonserie = wilson
else:
    wilsonserie = ''
    for w in wlist:
        wilsonserie += w
        if w!=wlist[-1]:
            wilsonserie += '_'

#Data fit
cmd1 = 'combine -M GoodnessOfFit inputs/'+observable+'_'+wilsonserie+'_workspace_'+year+'.root '
cmd1 += param
cmd1 += ' --algo=saturated -n .data_'+observable+'_'+year+'_'+wilsonserie

#MC toys
cmd2 = 'combine -M GoodnessOfFit inputs/'+observable+'_'+wilsonserie+'_workspace_'+year+'.root '
cmd2 += param
if ntoys==100:
    cmd2 += ' --algo=saturated --toysFreq -t '+str(ntoys)+' -n .mctoys_'+observable+'_'+year+'_'+wilsonserie
if ntoys!=100:
    cmd2 += ' --algo=saturated --toysFreq -t '+str(ntoys)+' -s '+str(seed)+' -n .mctoys_'+observable+'_'+year+'_'+wilsonserie+'_ntoys'+str(ntoys)#+'_seed'+str(seed)

 
print cmd1
print cmd2

if doFit:
    if ntoys==100 or ntoys==-1:
        os.system(cmd1)
    if ntoys!=-1:
        os.system(cmd2)

if ntoys!=100:
   sys.exit() 

#########################
## Plot the GoodnessOfFit
#########################

if ntoys==100 or doFit==False:

    fData = TFile('higgsCombine.data_'+observable+'_'+year+'_'+wilsonserie+'.GoodnessOfFit.mH120.root')
    tData = fData.Get('limit')
    tData.GetEvent(0)
    val_data = tData.GetLeaf('limit').GetValue()
    print str(val_data)

    fMC = TFile('higgsCombine.mctoys_'+observable+'_'+year+'_'+wilsonserie+'.GoodnessOfFit.mH120.123456.root')
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

    hMC = TH1F('GoF_MC','GoF_MC',1000,min(val_MC_min,val_data)-5,max(val_MC_max,val_data)+5)
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

    legend = TLegend(0.66,0.75,0.93,0.94, "SME fit: "+wilson)
    if len(wilson.split(","))!=1:
	legend.SetTextSize(0.027)
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
	tdr.cmsPrel(35900., 13.,simOnly=False,thisIsPrelim=True)
    elif(year=='2017'):
	tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)
    elif (year=='Comb'):
	tdr.cmsPrel(77400., 13.,simOnly=False,thisIsPrelim=True)


    Canvas.SaveAs('impacts/'+year+'/goodnessOfFit_'+observable+'_'+year+'_'+wilsonserie+'.pdf')

#raw_input()
exit()


