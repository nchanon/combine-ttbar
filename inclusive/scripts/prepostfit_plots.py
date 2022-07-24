import os, sys
import argparse 

sys.path.append('./')

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, THStack, TString
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
parser.add_argument('title', help='display your observable title')
parser.add_argument('timebin', help='display the time bin')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov
title = args.title
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


asi = ''
sasimov=''
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'    
    print ''
    asi = '--expectSignal 1 -t -1'
    sasimov = '_asimov'
else:
    sasimov = '_data'

#def asimov_param(asimov):
#    if asimov == 'asimov':
#        return '--expectSignal 1 -t -1'
#    else:
#        return ''

doPrePostFitOnly = True
#doPrePostFitOnly = False


fitkind = 'prefit'
#fitkind = 'fit_s'

#if (fitkind=='prefit'):
#    sfitkind = "Pre-fit"
#else:
#    sfitkind = "Post-fit"

rbin='r'
r_range='0.8,1.2'
npoints=20

###################
## FitDiagnostics
###################



print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'
    
#if (doPrePostFitOnly==False):
#    cmd1 = 'combineTool.py -M Impacts -n .Impact_'+year+' -d inputs/'+observable+'_inclusive_workspace_'+year+'.root '+asi+' -m 125 '
#    cmd2 = cmd1
#    cmd3 = cmd1
#    cmd1 += '--doInitialFit --robustFit 1'
#    cmd2 += '--robustFit 1 --doFits'
#    cmd3 += '-o '+observable+'_inclusive_impacts_'+year+sasimov+'.json '

#    cmd4 = 'plotImpacts.py -i '+observable+'_inclusive_impacts_'+year+sasimov+'.json -o '+observable+'_inclusive_impacts_'+year+sasimov
        
#    os.system(cmd1)
#    os.system(cmd2)
#    os.system(cmd3)
#    os.system(cmd4)

#    if asimov == 'asimov':
#        os.system('mv '+observable+'_inclusive_impacts_'+year+'* impacts/'+year+'/asimov/')
#        os.system('mv *Impact_'+year+'*.root impacts/'+year+'/asimov/')
#    else:
#        os.system('mv '+observable+'_inclusive_impacts_'+year+'* impacts/'+year+'/')
#        os.system('mv *Impact_'+year+'*.root  impacts/'+year+'/')

if (doPrePostFitOnly==True):
    if (fitkind=='prefit'):
	finput = 'inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root'
    else:
        cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+stimebin+'_'+asimov+' --robustFit 1 '
        cmd2 += ' -d inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root '
        cmd2 += asi #asimov_param(asimov)
        cmd2 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd2 += ' --saveWorkspace'
	os.system('echo '+cmd2)
	os.system(cmd2)
	finput = "higgsCombine.snapshot_"+year+stimebin+"_"+asimov+".MultiDimFit.mH120.root --snapshotName MultiDimFit"

    cmd5 = 'combineTool.py -M FitDiagnostics '+finput+' -m 125 --rMin 0 --rMax 10 --cminDefaultMinimizerStrategy 0 --saveShapes --saveWithUncertainties '
    cmd5 += ' --skipBOnlyFit --plots'
    os.system('echo using the root file :inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root ' )
    os.system('echo '+cmd5)
    os.system(cmd5)

#cmd6 = 'python diffNuisances.py fitDiagnostics.Test.root --skipFitB --all -g '+nuisances+'.root'


fDiagnostics = TFile("fitDiagnostics.Test.root","READ")

###################
## Correlation plot
###################

#if (doPrePostFitOnly==True):
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
hCov.GetXaxis().LabelsOption("v")
hCov.GetXaxis().SetLabelSize(0.025)
hCov.GetYaxis().SetLabelSize(0.025)
hCov.GetZaxis().SetLabelSize(0.025)
hCov.SetTitle("Systematics correlation matrix, "+year)
palette = hCov.GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.92)
palette.SetX2NDC(0.94)
palette.SetY1NDC(0.2)
palette.SetY2NDC(0.9)
hCov.Draw("COLZ")
canvas.Print("impacts/CorrelationMatrixParameters_"+observable+"_"+year+stimebin+".pdf")

###################
## Pre-fit plot
###################

if (observable=="m_dilep"):
    nbin = 7
    min_bin = 20
    max_bin = 300
if (observable=="n_bjets"):
    nbin = 4
    min_bin = 1
    max_bin = 5
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

def getUncertaintyBandGraph(hist):
    x = []
    ex_left = []
    ex_right =  []
    y =  []
    ey_up  = []
    ey_down = []
    for i in range(nbin):
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
    for i in range(nbin):
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

	canvas = TCanvas('stack_'+observable+fitkind,'stack_'+observable+fitkind, 800, 800)
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

	hist_data = getGraphWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/data"))
	hist_total = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/total"))
	hist_signal = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/signal"))
	hist_singletop = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/singletop"))
	hist_vjets = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/vjets"))
	hist_ttx = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/ttx"))
	hist_dibosons = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/"+observable+"/dibosons"))
	UncertaintyBand = getUncertaintyBandGraph(hist_total)
	UncertaintyBandRatio = getUncertaintyBandRatioGraph(hist_total)

	legend_args = (0.645, 0.65, 0.85, 0.92, sfitkind, 'NDC')
	legend = TLegend(*legend_args)
	legend.AddEntry(hist_signal, "t#bar{t} SM", "f")
	#legend.AddEntry(hist_background, "non-t#bar{t}", "f")
	legend.AddEntry(hist_singletop, "single top", "f")
	legend.AddEntry(hist_vjets, "W/Z+jets", "f")
	legend.AddEntry(hist_dibosons, "Dibosons", "f")
	legend.AddEntry(hist_ttx, "t#bar{t}+X", "f")
	legend.AddEntry(hist_data, "data")

	stack = THStack()
	stack.Add(hist_ttx)
	stack.Add(hist_dibosons)
	stack.Add(hist_vjets)
	stack.Add(hist_singletop)
	stack.Add(hist_signal)
	if (doLog): stack.SetMinimum(10)

	UncertaintyBand.GetXaxis().SetRangeUser(min_bin,max_bin)
	UncertaintyBand.SetMinimum(0)
	if (doLog): UncertaintyBand.SetMinimum(10)

	stack.Draw()
	UncertaintyBand.Draw("2AP SAME")
	stack.Draw("HIST SAME")
	hist_data.Draw("PSAME")
	legend.Draw("SAME")

	# line_color, line_width, fill_color, fill_style, marker_size, marker_style=1
	style_histo(hist_signal, 2, 1, 2, 3004, 0)
	style_histo(hist_singletop, 4, 1, 4, 3005, 0)
	style_histo(hist_ttx, 8, 1, 8, 3005, 0)
	style_histo(hist_dibosons, 42, 1, 42, 3005, 0)
	style_histo(hist_vjets, 619, 1, 619, 3005, 0)
	#style_histo(hist_background, 4, 1, 4, 3005, 0)
	style_histo(hist_data, 1, 1, 0, 3001, 1, 20)

	style_histo(UncertaintyBand, 1, 1, 1, 3005, 0)
	style_labels_counting(UncertaintyBand, 'Events', title)
	UncertaintyBand.GetXaxis().SetLabelSize(0)
	UncertaintyBand.GetXaxis().SetTitleSize(0)

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
	h_denom = hist_total
	#h_num.Divide(h_denom)
	h_num = hist_total.Clone()
	for i in range(nbin):
	    h_num.SetBinContent(i+1,hist_data.GetY()[i]/hist_total.GetBinContent(i+1))
	    h_num.SetBinError(i+1,hist_data.GetEYhigh()[i]/hist_total.GetBinContent(i+1))
	h_num.GetXaxis().SetTitle("aksjd")
	ratio = THStack()
	ratio.Add(h_num)

	UncertaintyBandRatio.Draw("2A SAME")
	h_num.Draw("E SAME")
	h_one.Draw("SAME")

	style_histo(UncertaintyBandRatio, 1, 1, 1, 3005, 0)
	UncertaintyBandRatio.GetXaxis().SetRangeUser(min_bin,max_bin)
	UncertaintyBandRatio.SetMinimum(1-ratio_coef)
	UncertaintyBandRatio.SetMaximum(1+ratio_coef)

	style_labels_counting(UncertaintyBandRatio, 'Ratio data/mc', title)
	UncertaintyBandRatio.GetYaxis().SetLabelSize(0.1)
	UncertaintyBandRatio.GetYaxis().SetTitleSize(0.1)
	UncertaintyBandRatio.GetYaxis().SetTitleOffset(0.5)
	UncertaintyBandRatio.GetXaxis().SetLabelSize(0.15)
	UncertaintyBandRatio.GetXaxis().SetTitleSize(0.17)
	UncertaintyBandRatio.GetXaxis().SetLabelOffset(0.01)

	resultname = './impacts/'+year+'/'+observable+'_'+year+stimebin+'_'+sfitkind
	canvas.SaveAs(resultname+'.pdf')

displayPrePostFitPlot("prefit")
displayPrePostFitPlot("fit_s")

raw_input('exit')
    
    
