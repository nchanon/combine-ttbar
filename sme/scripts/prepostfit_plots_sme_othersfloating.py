import os, sys
import argparse 

sys.path.append('./')

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors
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
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')
parser.add_argument('wilson', help='display your wilson coefficient')
parser.add_argument('title', help='display your observable title')

args = parser.parse_args()
observable = args.observable
year = args.year
wilson = args.wilson #should be something like cLXX_cLXY_cLXZ_cLYZ
asimov = args.asimov
title = args.title


#should check if wilson belongs for instance to cLXX_cLXY_cLXZ_cLYZ
wilson_list_all = [
    'cLXX_cLXY_cLXZ_cLYZ',
    'cRXX_cRXY_cRXZ_cRYZ',
    'cXX_cXY_cXZ_cYZ',
    'dXX_dXY_dXZ_dYZ'
]
for w4 in wilson_list_all:
    if w4.find(wilson)!=-1:
	wilsonserie = w4


#pois = []
#for i in range(24):
#    pois.append('r_'+str(i))


#asi = ' --setParameterRanges '+wilson+'=-30,30 ' #range OK for single fits

def asimov_param(wlist):
    asi = ' --setParameters '
    for w in wlist:
	if asimov=='injectiontest' and w==wilson:
	    asi += w+'=1'
	else:
            asi += w+'=0'
        if w!=wlist[-1]:
            asi += ','
    asi += ' --setParameterRanges '
    for w in wlist:
        if w[-2:]=='XX' or w[-2:]=='XY':
            wrange='30'
        if w[-2:]=='XZ' or w[-2:]=='YZ':
            wrange='100'
        asi += w+'=-'+wrange+','+wrange
        #asi += w+'=-100,100'
        if w!=wlist[-1]:
            asi += ':'
    if asimov == 'asimov' or asimov=='injectiontest':
        asi += ' -t -1'
    return asi

wilson_list_all = [
    'cLXX_cLXY_cLXZ_cLYZ',
    'cRXX_cRXY_cRXZ_cRYZ',
    'cXX_cXY_cXZ_cYZ',
    'dXX_dXY_dXZ_dYZ'
]

wilson_list = wilson_list_all

sasimov=''
if asimov == 'asimov':
    #asi += '--expectSignal 0  -t -1 '
    #asi  += '--setParameters '+wilson+'=0 -t -1 '
    sasimov = '_asimov'
elif asimov == 'injectiontest':
    #asi  += '--setParameters '+wilson+'=1 -t -1 '
    sasimov = '_injectiontest'
else:
    sasimov = '_data'

doFit = True
#doFit = False

###################
## FitDiagnostics
###################

print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'

optim = ' --cminDefaultMinimizerStrategy 0 '
#optim = ' --robustFit 1 '

if (doFit==True):

    if (asimov=='asimov' or asimov=='injectiontest'):
        finput = './inputs/'+observable+'_'+wilsonserie+'_workspace_'+year+'.root'
    else:
	cmd2 = 'combine -M MultiDimFit --algo=singles -n .othersfloating_snapshot_'+year+'_'+wilsonserie+'_'+asimov
        #cmd2 = 'combine -M MultiDimFit --algo=cross --cl=0.68 -n .cross_snapshot_'+year+'_'+wilson+'_'+asimov
	cmd2 += optim
        cmd2 += ' -d inputs/'+observable+'_'+wilsonserie+'_workspace_'+year+'.root '
        cmd2 += asimov_param(wilsonserie.split("_")) #asimov_param(asimov)
        cmd2 += ' --saveWorkspace'
    	os.system(cmd2)
    	finput = "higgsCombine.othersfloating_snapshot_"+year+"_"+wilsonserie+"_"+asimov+".MultiDimFit.mH120.root --snapshotName MultiDimFit"

    cmd5 = 'combineTool.py -M FitDiagnostics '+finput+' -m 125 ' + asimov_param(wilsonserie.split("_")) + optim
    cmd5 += ' --saveShapes --saveWithUncertainties --plots '
    cmd5 += '-n .othersfloating_prefit_'+observable+'_'+year+'_'+wilsonserie+'_'+asimov
    #cmd5 += ' --skipBOnlyFit --plots'
    print cmd5
    os.system(cmd5)

#cmd6 = 'python diffNuisances.py fitDiagnostics.Test.root --skipFitB --all -g '+nuisances+'.root'

fDiagnostics = TFile('fitDiagnostics.othersfloating_prefit_'+observable+'_'+year+'_'+wilsonserie+'_'+asimov+'.root',"READ")

###################
## Nuisances checks
###################

def makeNuisancePulls(wilson_choice):
    #wilson_choice = wilson
    #wilson_choice = wilson.split("_")[0]
    tolerance = 0.05
    #tolerance = -0.5

    cmd6 = 'python diffNuisances.py '+fDiagnostics.GetName()+' -p '+wilson_choice
    if tolerance!=0:
      cmd6 +=' --vtol '+str(tolerance)
    cmd6 +=' -g Nuisances.prefit_'+observable+'_'+year+'_'+wilsonserie+'_'+asimov+'.root -f text > diffNuisances_'+'prefit_'+observable+'_'+year+'_'+wilson_choice+'_'+asimov+'_othersfloating.log'
    print cmd6
    os.system(cmd6)

    syst_list = []
    syst_pull = []
    syst_uncert = []

    file = open('diffNuisances_prefit_'+observable+'_'+year+'_'+wilson_choice+'_'+asimov+'_othersfloating.log')

    iline=0
    for line in file:
	j = 0
	isHighlightedFirst = False
	isHighlightedSecond = False
	isHighlightedBoth = False
	for word in line.split():
	    print(str(iline)+' j='+str(j)+' '+word)
	    if iline>3:
		if j==0:
		    syst_list.append(word)
		if j==1 and word=='!':
		    isHighlightedFirst = True
		if j==3 and word=='!' and isHighlightedFirst==False:
		    isHighlightedSecond = True
		if j==4 and word=='!' and isHighlightedFirst==True:
		    isHighlightedSecond = True

		if (isHighlightedFirst==False and isHighlightedSecond==False):
		    if j==3: syst_pull.append(float(word[:-1]))
		    if j==4: syst_uncert.append(float(word))

		if (isHighlightedFirst==True and isHighlightedSecond==False):
		    if j==4: syst_pull.append(float(word[:-1]))
		    if j==5: syst_uncert.append(float(word))

		if (isHighlightedFirst==False and isHighlightedSecond==True):
		    if j==4: syst_pull.append(float(word[:-1]))
		    if j==5: syst_uncert.append(float(word[:-1]))
	       
		if (isHighlightedFirst==True and isHighlightedSecond==True):
		    if j==5: syst_pull.append(float(word[:-1]))
		    if j==6: syst_uncert.append(float(word[:-1]))

	    j += 1
	iline += 1

    print str(len(syst_list))+ ' ' + str(len(syst_uncert))

    print syst_list
    print syst_uncert

    syst_uncert_new = []
    syst_list_new = []
    syst_pull_new = []

    if asimov=='asimov' or asimov=='injectiontest' or asimov=='data':

	for i in range(len(syst_uncert)):
	    if tolerance==0 or (tolerance!=0 and syst_uncert[i]<1-tolerance):
		syst_uncert_new.append(syst_uncert[i])
		syst_list_new.append(syst_list[i])
		syst_pull_new.append(syst_pull[i])

	print str(len(syst_list_new))+ ' ' + str(len(syst_uncert_new))
    else:
	syst_list_new = syst_list
	syst_uncert_new = syst_uncert
	syst_pull_new = syst_pull
	print str(len(syst_list_new))+ ' ' +str(len(syst_uncert_new))


    syst_triple_list = []
    for isyst in range(len(syst_list_new)):
	syst_triple_list.append([syst_list_new[isyst],syst_pull_new[isyst],syst_uncert_new[isyst]])

    syst_triple_list.sort(key=lambda row: row[0])

    nSystMax = 100
    nPlots = 1 + len(syst_triple_list) / nSystMax
    print "nSyst="+str(len(syst_triple_list))+" nPlots="+str(nPlots)
    nSystPerPlot = []
    for j in range(nPlots):
	if j!=nPlots-1 or (j==nPlots-1 and len(syst_triple_list) % nPlots == 0):
	    nSystPerPlot.append(len(syst_triple_list)/nPlots)
	elif j==nPlots-1 and len(syst_triple_list) % nPlots == 1:
	    nSystPerPlot.append(len(syst_triple_list)/nPlots+1)
	else:
	    nSystPerPlot.append(len(syst_triple_list)/nPlots+(len(syst_triple_list) % nPlots))
	    print str(len(syst_triple_list) % nPlots)
	    print 'Plot with undefined number of syst'

    knuis=0
    syst_triple_list_splitted = []
    for j in range(nPlots):
	print 'New plot '+str(j)+' nSystPerPlot='+str(nSystPerPlot[j])
	syst_triple_list_splitted_tmp = []
	for k in range(nSystPerPlot[j]):
	    #for k in range(len(syst_triple_list)):
	    syst_triple_list_splitted_tmp.append(syst_triple_list[knuis])
	    print str(j)+" k="+str(k)+" "+syst_triple_list[knuis][0]
	    knuis = knuis + 1
	syst_triple_list_splitted.append(syst_triple_list_splitted_tmp)

    for j in range(nPlots):

	canvas = TCanvas('Nuisance pulls','Nuisance pulls',1400,400)
	pad = TPad("pad","pad",0,0,1,1)
	pad.SetLeftMargin(0.06)
	pad.SetBottomMargin(0.45)
	pad.Draw()
	pad.cd()

	#nNuis = len(syst_list_new)
	nNuis = nSystPerPlot[j]
	hist_nuis_up = TH1F("hist_nuis_up","hist_nuis_up",nNuis,0,nNuis)
	hist_nuis_down = TH1F("hist_nuis_down","hist_nuis_down",nNuis,0,nNuis)
	hist_nuis_pulled = TH1F("hist_nuis_pulled","hist_nuis_pulled",nNuis,0,nNuis)

	minhist=-1.2
	maxhist=1.2
	for i in range(nNuis):
	    hist_nuis_up.SetBinContent(1+i,1)
	    hist_nuis_up.GetXaxis().SetBinLabel(1+i,syst_triple_list_splitted[j][i][0])
	    hist_nuis_down.SetBinContent(1+i,-1)
	    if (syst_triple_list_splitted[j][i][1]-syst_triple_list_splitted[j][i][2]<minhist):
		minhist = syst_triple_list_splitted[j][i][1]-syst_triple_list_splitted[j][i][2]
	    if (syst_triple_list_splitted[j][i][1]+syst_triple_list_splitted[j][i][2]>maxhist):
		maxhist = syst_triple_list_splitted[j][i][1]+syst_triple_list_splitted[j][i][2]
	    hist_nuis_pulled.SetBinContent(1+i,syst_triple_list_splitted[j][i][1])
	    hist_nuis_pulled.SetBinError(1+i,syst_triple_list_splitted[j][i][2])
	    #hist_nuis.GetXaxis().SetBinLabel(1+i,syst_list_new[i])
	    #hist_nuis_pulled.SetBinError(1+i,syst_uncert_new[i])
	    #hist_nuis_pulled.SetBinContent(1+i,syst_uncert[i])

	if asimov=='asimov': #or asimov=='injectiontest':
	    hist_nuis_up.SetMinimum(0)
	    hist_nuis_up.SetMaximum(1.2)
	else:
	    hist_nuis_up.SetMinimum(minhist-0.05)
	    hist_nuis_up.SetMaximum(maxhist+0.05)
	    hist_nuis_down.SetLineStyle(2)
	#hist_nuis.SetMaximum(1.2)
	hist_nuis_up.GetYaxis().SetTitleOffset(0.4)
	hist_nuis_up.SetYTitle("Pull")
	hist_nuis_up.SetLineStyle(2)
	hist_nuis_up.GetXaxis().LabelsOption("v")
	hist_nuis_up.GetXaxis().SetLabelSize(0.05)
	hist_nuis_up.Draw()
	if asimov!='asimov':# and asimov!='injectiontest':
	    hist_nuis_down.Draw("SAME")
	hist_nuis_pulled.Draw("ESAME")

	latex = TLatex()
	latex.SetTextSize(1.2*gStyle.GetPadTopMargin())
	latex.SetNDC()
	if asimov!='injectiontest':
	    latex.DrawLatex(0.25,0.9,year+' '+wilson_choice+'  '+asimov)
	else:
	    latex.DrawLatex(0.25,0.9,year+' '+wilson_choice+'  '+asimov+' '+wilson+'=0.001')

	canvas.SaveAs('nuis_pulled_'+'prefit_'+observable+'_'+year+'_'+wilson_choice+'_'+asimov+'_'+str(j)+'_othersfloating.pdf')


for wilson_choice_ in wilsonserie.split("_"):
    makeNuisancePulls(wilson_choice_)

#raw_input()
sys.exit()

###################
## Correlation plot
###################

gStyle.SetPalette(55)
gStyle.SetOptStat(0)

canvas = TCanvas('CorrelationMatrix','CorrelationMatrix',1000,800)
pad = TPad("pad","pad",0,0,1,1)
pad.SetLeftMargin(0.16)
pad.SetBottomMargin(0.2)
pad.SetRightMargin(0.1)
pad.Draw()
pad.cd()

hCov = fDiagnostics.Get("covariance_fit_s")
hCovPOI = TH2F("covariance_fit_s_POI","covariance_fit_s_POI",4,0,4,4,0,4)
for i in range(4):
    hCovPOI.GetXaxis().SetBinLabel(1+i, wilson.split("_")[i])
    hCovPOI.GetYaxis().SetBinLabel(1+i, wilson.split("_")[i])
for i in range(4):
    for j in range(4):
        corrval = hCov.GetBinContent(hCov.GetXaxis().FindBin(wilson.split("_")[i]), hCov.GetYaxis().FindBin(wilson.split("_")[j]))
        hCovPOI.SetBinContent(i+1,j+1,corrval)


hCovPOI.GetXaxis().LabelsOption("v")
hCovPOI.GetXaxis().SetLabelSize(0.025)
hCovPOI.GetYaxis().SetLabelSize(0.025)
hCovPOI.GetZaxis().SetLabelSize(0.025)
hCovPOI.SetTitle("SME coefficients correlation matrix, "+year)
palette = hCov.GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.92)
palette.SetX2NDC(0.94)
palette.SetY1NDC(0.2)
palette.SetY2NDC(0.9)
hCovPOI.Draw("COLZTEXT")
canvas.Print("impacts/CorrelationMatrixSMEcoefficients_othersfloating_"+observable+"_"+year+"_"+wilson+sasimov+".pdf")

#raw_input()
exit()

###################
## Pre-fit plot
###################

if (observable=="m_dilep"):
    nbin = 7
    min_bin = 20
    max_bin = 300
if (observable=="n_bjets"):
    nbin = 4
    min_bin = 0 #1
    max_bin = 4 #5
if (observable=="pt_emu"):
    nbin = 7
    min_bin = 0
    max_bin = 245

width_bin = (max_bin-min_bin)/nbin

TH1.SetDefaultSumw2(1)
#canvas = TCanvas('stack_'+observable,'stack_'+observable, 800, 800)
#canvas.UseCurrentStyle()

doLog = False

r = 0.3
epsilon = 0.1

#displayPrePostFitPlot("prefit")
#displayPrePostFitPlot("fit_s")

#pad1 = TPad("pad1", "pad1", 0, r-epsilon, 1, 1)
#pad1.SetBottomMargin(epsilon)
#canvas.cd()
#if (doLog): pad1.SetLogy()
#pad1.Draw()
#pad1.cd()

def getHistWithXaxis(hist):
    hist_new = TH1F(hist.GetName()+"_new", hist.GetName()+"_new", nbin, min_bin, max_bin)
    for i in range(nbin):
        hist_new.SetBinContent(i+1,hist.GetBinContent(i+1))
        hist_new.SetBinError(i+1,hist.GetBinError(i+1))
    return hist_new

def mergeHisto(hist_list):
    print hist_list[0].GetName()
    hist_allbins = TH1F(hist_list[0].GetName()+"_allbins", hist_list[0].GetName()+"_allbins", nbin*24, 0, nbin*24)
    for i in range(len(hist_list)):
        for j in range(nbin):
	    hist_allbins.SetBinContent(j+1+i*nbin, hist_list[i].GetBinContent(j+1))
	    hist_allbins.SetBinError(j+1+i*nbin, hist_list[i].GetBinError(j+1))
    return hist_allbins

def getGraphWithXaxis(graph):
    x = []
    ex_left = []
    ex_right =  []
    y = []
    ey_up  = []
    ey_down = []
    for i in range(nbin):
        x.append(min_bin+width_bin/2.+width_bin*i)
        ex_left.append(width_bin/2.)
        ex_right.append(width_bin/2.)
        y.append(graph.GetY()[i])
        ey_up.append(graph.GetEYhigh()[i])
        ey_down.append(graph.GetEYlow()[i])
    graph_new = TGraphAsymmErrors(len(x),array.array('d', x),array.array('d', y),array.array('d', ex_left),array.array('d', ex_right),array.array('d', ey_down),array.array('d', ey_up))
    graph_new.SetName(graph.GetName()+"_new")
    graph_new.SetTitle(graph.GetName()+"_new")
    return graph_new

def mergeGraph(graph_list):
    x = []
    ex_left = []
    ex_right =  []
    y = []
    ey_up  = []
    ey_down = []
    for i in range(len(graph_list)):
	for j in range(nbin):
	    x.append(min_bin+width_bin/2.+width_bin*(j+i*nbin))
	    ex_left.append(width_bin/2.)
	    ex_right.append(width_bin/2.)
	    y.append(graph_list[i].GetY()[j])
            ey_up.append(graph_list[i].GetEYhigh()[j])
            ey_down.append(graph_list[i].GetEYlow()[j])
    graph_allbins = TGraphAsymmErrors(len(x),array.array('d', x),array.array('d', y),array.array('d', ex_left),array.array('d', ex_right),array.array('d', ey_down),array.array('d', ey_up))
    graph_allbins.SetName(graph_list[0].GetName()+"_allbins")
    graph_allbins.SetTitle(graph_list[0].GetName()+"_allbins")
    return graph_allbins

def getUncertaintyBandGraph(hist):
    x = []
    ex_left = []
    ex_right =  []
    y =  []
    ey_up  = []
    ey_down = []
    for i in range(hist.GetNbinsX()):
    #for i in range(nbin):
        x.append(min_bin+width_bin/2.+width_bin*i)
        ex_left.append(width_bin/2.)
        ex_right.append(width_bin/2.)
	y.append(hist.GetBinContent(i+1))
	ey_up.append(hist.GetBinErrorUp(i+1))
	ey_down.append(hist.GetBinErrorLow(i+1))
    graph_new = TGraphAsymmErrors(len(x),array.array('d', x),array.array('d', y),array.array('d', ex_left),array.array('d', ex_right),array.array('d', ey_down),array.array('d', ey_up))
    graph_new.SetName("uncertainty_band_"+hist.GetName())
    graph_new.SetTitle("uncertainty_band_"+hist.GetName())
    return graph_new

def getUncertaintyBandRatioGraph(hist):
    x = []
    ex_left = []
    ex_right =  []
    y =  []
    ey_up  = []
    ey_down = []
    for i in range(hist.GetNbinsX()):
    #for i in range(nbin):
        x.append(min_bin+width_bin/2.+width_bin*i)
        ex_left.append(width_bin/2.)
        ex_right.append(width_bin/2.)
        y.append(1)
        ey_up.append(hist.GetBinErrorUp(i+1)/hist.GetBinContent(i+1))
        ey_down.append(hist.GetBinErrorLow(i+1)/hist.GetBinContent(i+1))
    graph_new = TGraphAsymmErrors(len(x),array.array('d', x),array.array('d', y),array.array('d', ex_left),array.array('d', ex_right),array.array('d', ey_down),array.array('d', ey_up))
    graph_new.SetName("uncertainty_band_ratio_"+hist.GetName())
    graph_new.SetTitle("uncertainty_band_ratio_"+hist.GetName())
    return graph_new

#def getHistFromGraph(graph):
#    hist_new = TH1F(hist.GetName()+"_new", hist.GetName()+"_new", nbin, min_bin, max_bin)
#    for i in range(nbin):
#        hist_new.SetBinContent(i+1,graph.GetY()[i])
#        hist_new.SetBinError(i+1,hist.GetBinError(i+1))
#    return hist_new

def displayPrePostFitPlot(fitkind):

	canvas = TCanvas('stack_'+observable+fitkind,'stack_'+observable+fitkind, 2400, 800)
	canvas.UseCurrentStyle()

	if (fitkind=='prefit'):
	    sfitkind = "Pre-fit"
	else:
	    sfitkind = "Post-fit"

	pad1 = TPad("pad1", "pad1", 0, r-epsilon, 1, 1)
	pad1.SetBottomMargin(epsilon)
	canvas.cd()
	if (doLog): pad1.SetLogy()
	pad1.Draw()
	pad1.cd()

	hist_data = []
	hist_total = []
	hist_signal = []
	hist_singletop = []
	hist_vjets = []
	hist_ttx = []
	hist_dibosons = []
	for i in range(24):
		print 'Time bin ',str(i)
		hist_data.append(getGraphWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/data")))
		hist_total.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/total")))
		hist_signal.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/signal")))
		hist_singletop.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/singletop")))
		hist_vjets.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/vjets")))
		hist_ttx.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/ttx")))
		hist_dibosons.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/dibosons")))
	
	hist_data_allbins = mergeGraph(hist_data)	
	hist_total_allbins = mergeHisto(hist_total)
	hist_signal_allbins = mergeHisto(hist_signal)
	hist_singletop_allbins = mergeHisto(hist_singletop)
	hist_vjets_allbins = mergeHisto(hist_vjets)
	hist_ttx_allbins = mergeHisto(hist_ttx)
	hist_dibosons_allbins = mergeHisto(hist_dibosons)
	
	UncertaintyBand = getUncertaintyBandGraph(hist_total_allbins)
	UncertaintyBandRatio = getUncertaintyBandRatioGraph(hist_total_allbins)

	legend_args = (0.005, 0.68, 0.105, 0.95, sfitkind, 'NDC')
	legend = TLegend(*legend_args)
	legend.AddEntry(hist_signal_allbins, "t#bar{t} SM", "f")
	#legend.AddEntry(hist_background_allbins, "non-t#bar{t}", "f")
	legend.AddEntry(hist_singletop_allbins, "single top", "f")
	legend.AddEntry(hist_vjets_allbins, "W/Z+jets", "f")
	legend.AddEntry(hist_dibosons_allbins, "Dibosons", "f")
	legend.AddEntry(hist_ttx_allbins, "t#bar{t}+X", "f")
	if (asimov=='data'):
	    legend.AddEntry(hist_data_allbins, "data")
	else:
	    legend.AddEntry(hist_data_allbins, "asimov")

	stack = THStack()
	stack.Add(hist_ttx_allbins)
	stack.Add(hist_dibosons_allbins)
	stack.Add(hist_vjets_allbins)
	stack.Add(hist_singletop_allbins)
	stack.Add(hist_signal_allbins)
	if (doLog): stack.SetMinimum(10)

	UncertaintyBand.GetXaxis().SetRangeUser(min_bin,max_bin*24)
	UncertaintyBand.SetMinimum(0)
	if (doLog): UncertaintyBand.SetMinimum(10)

	#UncertaintyBand.SetMaximum(stack.GetMaximum()*1.5)
	#stack.SetMaximum(stack.GetMaximum()*1.5)
	#hist_data_allbins.SetMaximum(stack.GetMaximum()*1.5)
	#hist_data_allbins.GetYaxis().SetRangeUser(0,stack.GetMaximum()*1.5)
        #UncertaintyBandRatio.GetYaxis().SetRangeUser(0,stack.GetMaximum()*1.5)
	

	stack.Draw()
	UncertaintyBand.Draw("2AP SAME")
	stack.Draw("HIST SAME")
	hist_data_allbins.Draw("PSAME")
	legend.Draw("SAME")

	# line_color, line_width, fill_color, fill_style, marker_size, marker_style=1
	style_histo(hist_signal_allbins, 2, 1, 2, 3004, 0)
	style_histo(hist_singletop_allbins, 4, 1, 4, 3005, 0)
	style_histo(hist_ttx_allbins, 8, 1, 8, 3005, 0)
	style_histo(hist_dibosons_allbins, 42, 1, 42, 3005, 0)
	style_histo(hist_vjets_allbins, 619, 1, 619, 3005, 0)
	#style_histo(hist_background_allbins, 4, 1, 4, 3005, 0)
	style_histo(hist_data_allbins, 1, 1, 0, 3001, 1, 20)

	style_histo(UncertaintyBand, 1, 1, 1, 3002, 0)
	style_labels_counting(UncertaintyBand, 'Events', title)
	UncertaintyBand.GetXaxis().SetLabelSize(0)
	UncertaintyBand.GetXaxis().SetTitleSize(0)
	#UncertaintyBand.SetTitleOffset(0.1)

	if(year=='2016'):
	    tdr.cmsPrel(35900., 13.,simOnly=False,thisIsPrelim=True)
	elif(year=='2017'):
	   tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)

	pad2 = TPad("pad2", "pad2", 0, 0, 1, r*(1-epsilon))
	pad2.SetTopMargin(0)
	pad2.SetBottomMargin(0.4)
	pad2.SetFillStyle(0)
	canvas.cd()
	pad2.Draw()
	pad2.cd()

	ratio_coef = 0.3

	h_one = TH1F("one", "one", 1, min_bin, max_bin)
	h_one.SetBinContent(1, 1)
	h_one.SetLineWidth(1)
	h_one.SetLineColor(15)
	#h_num = hist_data.Clone()
	h_denom = hist_total_allbins
	#h_num.Divide(h_denom)
	h_num = hist_total_allbins.Clone()
	for i in range(nbin*24):
	    h_num.SetBinContent(i+1,hist_data_allbins.GetY()[i]/hist_total_allbins.GetBinContent(i+1))
	    h_num.SetBinError(i+1,hist_data_allbins.GetEYhigh()[i]/hist_total_allbins.GetBinContent(i+1))
	h_num.GetXaxis().SetTitle("aksjd")
	ratio = THStack()
	ratio.Add(h_num)

	UncertaintyBandRatio.Draw("2A SAME")
	h_num.Draw("E SAME")
	h_one.Draw("SAME")

	style_histo(UncertaintyBandRatio, 1, 1, 1, 3002, 0)
	UncertaintyBandRatio.GetXaxis().SetRangeUser(min_bin,max_bin*24)
	UncertaintyBandRatio.SetMinimum(1-ratio_coef)
	UncertaintyBandRatio.SetMaximum(1+ratio_coef)

	style_labels_counting(UncertaintyBandRatio, 'Ratio data/mc', title)
	UncertaintyBandRatio.GetYaxis().SetLabelSize(0.1)
	UncertaintyBandRatio.GetYaxis().SetTitleSize(0.1)
	UncertaintyBandRatio.GetYaxis().SetTitleOffset(0.3)
	UncertaintyBandRatio.GetXaxis().SetLabelSize(0.15)
	UncertaintyBandRatio.GetXaxis().SetTitleSize(0.17)
	UncertaintyBandRatio.GetXaxis().SetLabelOffset(0.01)

        if (fitkind!='prefit'):
	    resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind
	else:
	    resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind+'_asimov'
	canvas.SaveAs(resultname+'.pdf')

displayPrePostFitPlot("prefit")
#displayPrePostFitPlot("fit_s")

raw_input('exit')
    
    
