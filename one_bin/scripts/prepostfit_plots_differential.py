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

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov
title = args.title

pois = []
for i in range(24):
    pois.append('r_'+str(i))

asi = ''
sasimov=''
#    asi = '--expectSignal 1 -t -1'
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
#combine_n_bjets_24bins_Comb_workspace.root

if (doPrePostFitOnly==False):
    if (fitkind=='prefit'):
	finput = 'inputs/combine_'+observable+'_24bins_'+year+'_workspace.root'
    else:
        cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+'_'+asimov+' --robustFit 1 '
        cmd2 += ' -d inputs/'+observable+'_inclusive_workspace_'+year+'.root '
        cmd2 += asi #asimov_param(asimov)
        cmd2 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd2 += ' --saveWorkspace'
	os.system(cmd2)
	finput = "higgsCombine.snapshot_"+year+"_"+asimov+".MultiDimFit.mH120.root --snapshotName MultiDimFit"

    cmd5 = 'combineTool.py -M FitDiagnostics '+finput+' -m 125 '+asi+' --cminDefaultMinimizerStrategy 0 --saveShapes --saveWithUncertainties '
    cmd5 += ' --skipBOnlyFit --plots'
    os.system(cmd5)

#cmd6 = 'python diffNuisances.py fitDiagnostics.Test.root --skipFitB --all -g '+nuisances+'.root'

#exit()

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
canvas.Print("impacts/CorrelationMatrixParameters_"+observable+"_"+year+".pdf")

#exit()

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
	if (doPrePostFitOnly==False):
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
    
    
