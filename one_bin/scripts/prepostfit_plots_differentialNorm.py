import os, sys
import argparse 
import numpy as np

sys.path.append('./')

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors
from ROOT import TStyle, gStyle, TColor, TLatex, TGaxis, TLine

import math

from tools.style_manager import *
#from tools.sample_manager import *
import array

import tools.tdrstylePaper as tdr
tdr.setTDRStyle()

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test')
parser.add_argument('fitkind',nargs='?', help='prefit or postfit')
parser.add_argument('title', help='display your observable title')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov
fitkind_ = args.fitkind
title = args.title

pois = []
pois.append("r_avg")
for i in range(23):
    pois.append('f_'+str(i))
#for i in range(24):
#    pois.append('r_'+str(i))

initial_param = ' --redefineSignalPOIs '
for i in range(24):
    initial_param += pois[i]
    if i != 23:
        initial_param += ','
initial_param += ' --setParameters '
for i in range(24):
    initial_param += pois[i]+'=1'
    if i != 23:
        initial_param += ','

asi = initial_param
sasimov=''
#    asi = '--expectSignal 1 -t -1'
if asimov == 'asimov':
    print '################'
    print '# Asimov test : '
    print '################'
    print ''
#    asi = ' --redefineSignalPOIs '
#    for i in range(24):
#        asi += pois[i]
#        if i != 23:
#            asi += ','
#    asi += ' --setParameters '
#    for i in range(24):
#        asi += pois[i]+'=1'
#        if i != 23:
#            asi += ','
    asi += ' -t -1 '
    sasimov = '_asimov'
else:
    print '################'
    print '# Data test : '
    print '################'
    print ''
    sasimov = '_data'

#def asimov_param(asimov):
#    if asimov == 'asimov':
#        return '--expectSignal 1 -t -1'
#    else:
#        return ''

doPrePostFitOnly = True
#doPrePostFitOnly = False


#fitkind = 'prefit'
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

optim = ' --cminDefaultMinimizerStrategy 0 '
#optim = ' --robustFit 1 '

if (doPrePostFitOnly==False):
    #if (fitkind_.find('prefit')!=-1):
    if (asimov=='asimov'):
	finput = 'inputs/combine_'+observable+'_24bins_'+year+'_workspace_norm.root'
    else:
        cmd2 = 'combine -M MultiDimFit -n .snapshot_'+year+'_'+asimov+'_normfit'+ optim #' --robustFit 1 '
        cmd2 += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace_norm.root '
        cmd2 += asi #asimov_param(asimov)
        #cmd2 += ' --algo=singles'
        #cmd2 += ' --parameters '+rbin+' --setParameterRanges '+rbin+'='+r_range #+' --floatOtherPOIs=1'
        cmd2 += ' --saveWorkspace '
	print cmd2
	os.system(cmd2)
	finput = "higgsCombine.snapshot_"+year+"_"+asimov+"_normfit.MultiDimFit.mH120.root --snapshotName MultiDimFit"

	#exit()

    cmd5 = 'combineTool.py -M FitDiagnostics '+finput+' -m 125 '
    if fitkind_=='prefit_asimov':
	cmd5 += asi #Removed on Apr 1st (wasn't there for inclusive fit)
    else:
	cmd5 += initial_param
    #cmd5 +=  ' --cminDefaultMinimizerType Minuit --cminDefaultMinimizerStrategy 0'
    cmd5 += ' --cminDefaultMinimizerStrategy 0'
    cmd5 += ' --saveShapes --saveWithUncertainties --plots --saveOverallShapes'
    cmd5 += ' -n .prefit_'+observable+'_'+year+'_'+fitkind_+'_normfit'
    print cmd5
    #cmd5 += ' --skipBOnlyFit --plots'
    os.system(cmd5)

#cmd6 = 'python diffNuisances.py fitDiagnostics.Test.root --skipFitB --all -g '+nuisances+'.root'

#exit()

fDiagnostics = TFile('fitDiagnostics.prefit_'+observable+'_'+year+'_'+fitkind_+'_normfit.root',"READ")
#fDiagnostics = TFile("fitDiagnostics.Test.root","READ")


###################
## Nuisances checks
###################

doPull=False

if doPull==True:
    tolerance = 0.05
    #poi = 'r_0'
    #poi = 'r_1'
    #poi = 'r_18'
    #poi = 'r_23'
    poi = 'f_0'

    cmd6 = 'python diffNuisances.py '+fDiagnostics.GetName()+' -p '
    cmd6 += poi
    #for i in range(24):
    #    cmd6 += pois[i]
    #    if (i!=23): 
    #        cmd6 += ','
    cmd6 += ' --skipFitB'
    #cmd6 += ' --all '
    cmd6 += ' --vtol '+str(tolerance)
    cmd6 += ' -g Nuisances.prefit_'+observable+'_'+year+'_'+asimov+'_normfit.root -f text > diffNuisances_'+'prefit_'+observable+'_'+year+'_'+poi+'_'+asimov+'_normfit.log'
    print cmd6
    os.system(cmd6)



    syst_list = []
    syst_pull = []
    syst_uncert = []

    file = open('diffNuisances_'+'prefit_'+observable+'_'+year+'_'+poi+'_'+asimov+'_normfit.log')
    iline=0
    for line in file:
	j = 0
	isHighlightedFirst = False
	isHighlightedSecond = False
	for word in line.split():
	    print(str(iline)+' j='+str(j)+' '+word)
	    if iline>3:
		if j==0:
		    syst_list.append(word)
		if j==1 and word=='!':
		    isHighlightedFirst = True
		if j==3 and word=='!':
		    isHighlightedSecond = True
		if j==3 and isHighlightedFirst==False and isHighlightedSecond==False:
		    syst_pull.append(float(word[:-1]))
		if j==4 and isHighlightedFirst==False and isHighlightedSecond==False:
		    syst_uncert.append(float(word))
		if j==4 and isHighlightedSecond==True:
		    syst_pull.append(float(word[:-1]))
		if j==5 and isHighlightedSecond==True:
		    syst_uncert.append(float(word[:-1]))
		if j==5 and isHighlightedFirst==True:
		    syst_pull.append(float(word[:-1]))
		if j==6 and isHighlightedFirst==True:
		    syst_uncert.append(float(word[:-1]))

	    j += 1
	iline += 1

    print str(len(syst_list))+ ' ' + str(len(syst_uncert))

    print syst_list
    print syst_uncert

    syst_uncert_new = []
    syst_list_new = []
    syst_pull_new = []

    if asimov=='asimov' or asimov=='data':
	for i in range(len(syst_uncert)):
	    if syst_uncert[i]<0.95:
		syst_uncert_new.append(syst_uncert[i])
		syst_list_new.append(syst_list[i])
		syst_pull_new.append(syst_pull[i])
	#syst_list.clear()
	#syst_list = syst_list_new
	#syst_uncert.clear()
	#syst_uncer = syst_uncert_new
	print str(len(syst_list))+ ' ' + str(len(syst_uncert))
    else:
	syst_list_new = syst_list
	syst_uncert_new = syst_uncert
	syst_pull_new = syst_pull
	print str(len(syst_list))+ ' ' + str(len(syst_uncert))

    syst_triple_list = []
    for isyst in range(len(syst_list_new)):
	syst_triple_list.append([syst_list_new[isyst],syst_pull_new[isyst],syst_uncert_new[isyst]])

    syst_triple_list.sort(key=lambda row: row[0])

    nSystMax = 100
    nPlots = 1 + len(syst_triple_list) / nSystMax
    print "nSyst="+str(len(syst_triple_list))+" nPlots="+str(nPlots)
    #nSystPerPlot = len(syst_triple_list)/nPlots
    nSystPerPlot = []
    for j in range(nPlots):
	if j!=nPlots-1 or (j==nPlots-1 and len(syst_triple_list) % nPlots == 0):
	    nSystPerPlot.append(len(syst_triple_list)/nPlots)
	elif j==nPlots-1 and len(syst_triple_list) % nPlots == 1:
	    nSystPerPlot.append(len(syst_triple_list)/nPlots+1)

    knuis=0
    syst_triple_list_splitted = []
    for j in range(nPlots):
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
        pad.SetRightMargin(0.1)
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

	if asimov=='asimov':
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
	if asimov!='asimov':
	    hist_nuis_down.Draw("SAME")
	hist_nuis_pulled.Draw("ESAME")

	latex = TLatex()
	latex.SetTextSize(1.2*gStyle.GetPadTopMargin())
	latex.SetNDC()
	latex.DrawLatex(0.25,0.9,year+' '+poi+'  '+asimov)

	#canvas.SaveAs('nuis_pulled_'+'prefit_'+observable+'_'+year+'_'+poi+'_'+asimov+'_normfit_'+str(j)+'.pdf')
	canvas.SaveAs('nuis_pulled_'+'prefit_'+observable+'_'+year+'_'+poi+'_'+fitkind_+'_normfit_'+str(j)+'.pdf')

#raw_input()
#sys.exit()


###################
## Correlation plot
###################

doCorrPOI=False

if doCorrPOI==True:
    #if (doPrePostFitOnly==True):
    gStyle.SetPalette(55)
    gStyle.SetOptStat(0)

    hCov = fDiagnostics.Get("covariance_fit_s")

    canvas = TCanvas('CorrelationMatrix','CorrelationMatrix',1000,800)
    pad = TPad("pad","pad",0,0,1,1)
    pad.SetLeftMargin(0.16)
    pad.SetBottomMargin(0.2)
    pad.SetRightMargin(0.1)
    pad.Draw()
    pad.cd()

    hCovPOI = TH2F("covariance_fit_s_POI","covariance_fit_s_POI",24,0,24,24,0,24)
    for i in range(24):
	#hCovPOI.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
	#hCovPOI.GetYaxis().SetBinLabel(1+i, "r_"+str(i))
	hCovPOI.GetXaxis().SetBinLabel(1+i, pois[i])
	hCovPOI.GetYaxis().SetBinLabel(1+i, pois[i])

    for i in range(24):
	for j in range(24):
	    corrval = hCov.GetBinContent(hCov.GetXaxis().FindBin(pois[i]), hCov.GetYaxis().FindBin(pois[j]))
	    #corrval = hCov.GetBinContent(hCov.GetXaxis().FindBin("r_"+str(i)), hCov.GetYaxis().FindBin("r_"+str(j)))
	    hCovPOI.SetBinContent(i+1,j+1,corrval)
	    
    hCovPOI.GetXaxis().LabelsOption("v")
    hCovPOI.GetXaxis().SetLabelSize(0.025)
    hCovPOI.GetYaxis().SetLabelSize(0.025)
    hCovPOI.GetZaxis().SetLabelSize(0.025)
    #hCov.SetTitle("Systematics correlation matrix, "+year)
    hCovPOI.SetTitle("Signal strengths correlation matrix, "+year)

    palette = hCov.GetListOfFunctions().FindObject("palette")
    palette.SetX1NDC(0.92)
    palette.SetX2NDC(0.94)
    palette.SetY1NDC(0.2)
    palette.SetY2NDC(0.9)
    hCovPOI.Draw("COLZ")
    #canvas.Print("impacts/CorrelationMatrixParameters_"+observable+"_"+year+".pdf")
    canvas.Print("impacts/CorrelationMatrixNormFit_"+observable+"_"+year+"_"+fitkind_+".pdf")

#raw_input()
#sys.exit()


###################
## Pre-fit plot
###################

leftmargin = 0.2

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

r = 0.4
epsilon = 0.1

#displayPrePostFitPlot("prefit")
#displayPrePostFitPlot("fit_s")

#pad1 = TPad("pad1", "pad1", 0, r-epsilon, 1, 1)
#pad1.SetBottomMargin(epsilon)
#canvas.cd()
#if (doLog): pad1.SetLogy()
#pad1.Draw()
#pad1.cd()

nObsBins = 24
if (year=="Comb"): 
    nObsBins = 48

def getHistWithXaxis(hist):
    nbin_new = hist.GetNbinsX()
    min_bin_new = hist.GetXaxis().GetXmin()
    max_bin_new = hist.GetXaxis().GetXmax()
    hist_new = TH1F(hist.GetName()+"_new", hist.GetName()+"_new", nbin_new, min_bin_new, max_bin_new)
    for i in range(nbin_new):
        hist_new.SetBinContent(i+1,hist.GetBinContent(i+1))
        hist_new.SetBinError(i+1,hist.GetBinError(i+1))
    return hist_new

def getHist2DWithXaxis(hist):
    nbin_new = hist.GetNbinsX()
    min_bin_new = hist.GetXaxis().GetXmin()
    max_bin_new = hist.GetXaxis().GetXmax()
    hist_new = TH2F(hist.GetName()+"_new", hist.GetName()+"_new", nbin_new, min_bin_new, max_bin_new, nbin_new, min_bin_new, max_bin_new)
    for i in range(nbin_new):
	for j in range(nbin_new):
	    hist_new.SetBinContent(i+1,j+1,hist.GetBinContent(i+1,j+1))
    return hist_new

def mergeHisto(hist_list):
    print hist_list[0].GetName()
    hist_allbins = TH1F(hist_list[0].GetName()+"_allbins", hist_list[0].GetName()+"_allbins", nbin*nObsBins, 0, nbin*nObsBins)
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
    for i in range(graph.GetN()):
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

def getChi2(hist_data, hist_total, hist_total_covar, nkinbin):

    doNormalize = False

    #nkinbin = hist_total.GetNbinsX()
    print 'nkinbin='+str(nkinbin) 

    doNoCovMatrix = False
    if doNoCovMatrix==True:
	chi2noCov = 0
	for i in range(nkinbin):
	    chi2noCov += (hist_data.GetY()[i] - hist_total.GetBinContent(1+i))*(hist_data.GetY()[i] - hist_total.GetBinContent(1+i)) / (hist_total.GetBinError(1+i)*hist_total.GetBinError(1+i))
	print  'chi2noCov='+str(chi2noCov)
	return chi2noCov 

    matrix_Cov = np.zeros((nkinbin,nkinbin))
    for i in range(nkinbin):
	#print 'Check: nbjet bin '+str(i)+' errror on Nev ='+str(hist_total.GetBinError(1+i))+' from covar '+str(math.sqrt(hist_total_covar.GetBinContent(1+i,1+i)))
	for j in range(nkinbin):
	    matrix_Cov[i][j] = hist_total_covar.GetBinContent(1+i,1+j)
	    if doNormalize==True:
		matrix_Cov[i][j] /= hist_total.GetBinError(1+i)*hist_total.GetBinError(1+j)
    #print matrix_Cov
    matrix_Cov_Inv = np.linalg.inv(matrix_Cov)
    #print 'Check identity:'
    identity = np.matmul(matrix_Cov_Inv,matrix_Cov)
    #print identity

    #vect_Datafit = np.matrix([0,0,0,0])
    #vect_Datafit_T = np.matrix([0,0,0,0])
    vect_Datafit = np.matrix(np.zeros(nkinbin))
    vect_Datafit_T = np.matrix(np.zeros(nkinbin))
    #vect_Datafit = np.zeros(nkinbin)
    #vect_Datafit_T = np.zeros(nkinbin)

    #vect_Datafit = np.zeros((1,nkinbin))
    #vect_Datafit_T = np.zeros((nkinbin,1))
    for i in range(nkinbin):
	#vect_Datafit[i] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
	#vect_Datafit_T[i] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
	vect_Datafit[0,i] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
        vect_Datafit_T[0,i] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
	#print str(vect_Datafit[0,i])+' '+str(vect_Datafit_T[0,i])
	#print str(hist_total.GetBinContent(1+i))
	#if doNormalize==True:
	    #vect_Datafit[0,i] = (hist_data.GetY()[i] - hist_total.GetBinContent(1+i))/hist_total.GetBinContent(1+i)
	    #vect_Datafit_T[0,i] = (hist_data.GetY()[i] - hist_total.GetBinContent(1+i))/hist_total.GetBinContent(1+i)
	    #print str(vect_Datafit[0,i])+' '+str(vect_Datafit_T[0,i])
	#vect_Datafit[0][i] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
	#vect_Datafit_T[i][0] = hist_data.GetY()[i] - hist_total.GetBinContent(1+i)
    #vect_Datafit_T = vect_Datafit_T.transpose()
    vect_Datafit = vect_Datafit.transpose()

    #print vect_Datafit
    #print vect_Datafit_T
    #print matrix_Cov_Inv
    #chi2 = (np.matmul(np.matmul(vect_Datafit_T,matrix_Cov_Inv),vect_Datafit)) #/nkinbin
    chi2 = np.matmul(vect_Datafit_T,np.matmul(matrix_Cov_Inv,vect_Datafit))    

    print 'chi2='+str(chi2)
    return chi2[0,0]
    #return chi2

def getPlotIntegratedOverObs(fitkind, hist_data, hist_total, hist_signal, hist_singletop, hist_vjets, hist_ttx, hist_dibosons, hist_total_covar):
 
    #Integrating over obs and filling histos/graphs
    hist_total_int = TH1F("hist_total_int", "hist_total_int", nObsBins, 0, nObsBins)
    hist_signal_int = TH1F("hist_signal_int", "hist_signal_int", nObsBins, 0, nObsBins)
    hist_singletop_int = TH1F("hist_singletop_int", "hist_singletop_int", nObsBins, 0, nObsBins)
    hist_vjets_int = TH1F("hist_vjets_int", "hist_vjets_int", nObsBins, 0, nObsBins)
    hist_ttx_int = TH1F("hist_ttx_int", "hist_ttx_int", nObsBins, 0, nObsBins)
    hist_dibosons_int = TH1F("hist_dibosons_int", "hist_dibosons_int", nObsBins, 0, nObsBins)

    data_int = []
    for i in range(len(hist_total)):
	nkinbin = hist_total[i].GetNbinsX()
	data = 0
	total = 0
	signal = 0
	singletop = 0
	vjets = 0
	ttx = 0
	dibosons = 0
	error = 0
	for j in range(nkinbin):
	    data += hist_data[i].GetY()[j]
	    total += hist_total[i].GetBinContent(j)
	    signal += hist_signal[i].GetBinContent(j)
	    singletop += hist_singletop[i].GetBinContent(j)
	    vjets += hist_vjets[i].GetBinContent(j)
	    ttx += hist_ttx[i].GetBinContent(j)
	    dibosons += hist_dibosons[i].GetBinContent(j)
	    for k in range(nkinbin):
		error += hist_total_covar[i].GetBinContent(1+j,1+k)
	error = math.sqrt(error)
	hist_total_int.SetBinContent(1+i, total)
	hist_total_int.SetBinError(1+i,error)
	hist_signal_int.SetBinContent(1+i, signal)
	hist_singletop_int.SetBinContent(1+i, singletop)
	hist_vjets_int.SetBinContent(1+i, vjets)
	hist_ttx_int.SetBinContent(1+i, ttx)
	hist_dibosons_int.SetBinContent(1+i, dibosons)
        data_int.append(data)

    x = []
    ex_left = []
    ex_right =  []
    y = []
    ey_up  = []
    ey_down = []
    for i in range(len(hist_total)):
        x.append(min_bin+width_bin/2.+width_bin*i)
        ex_left.append(width_bin/2.)
        ex_right.append(width_bin/2.)
        y.append(data_int[i])
        ey_up.append(math.sqrt(data_int[i]))
        ey_down.append(math.sqrt(data_int[i]))
    hist_data_int = TGraphAsymmErrors(len(x),array.array('d', x),array.array('d', y),array.array('d', ex_left),array.array('d', ex_right),array.array('d', ey_down),array.array('d', ey_up))
    hist_data_int.SetName("graph_data_int")
    hist_data_int.SetTitle("graph_data_int")

    #Plotting
    canvas = TCanvas('stack_'+observable+fitkind+'_int','stack_'+observable+fitkind+'_int', 2400, 800)
    canvas.UseCurrentStyle()

    if (fitkind=='prefit'):
	sfitkind = "Pre-fit"
    else:
	sfitkind = "Post-fit"

    epsilon_int = epsilon
    pad1 = TPad("pad1_int", "pad1_int", 0, r-epsilon_int, 1, 1)
    pad1.SetLeftMargin(leftmargin)
    pad1.SetRightMargin(0.01)
    pad1.SetBottomMargin(epsilon_int)
    #pad1.SetTopMargin(2*gStyle.GetPadTopMargin()) #Was 1.5

    canvas.cd()
    if (doLog): pad1.SetLogy()
    pad1.Draw()
    pad1.cd()

    UncertaintyBand = getUncertaintyBandGraph(hist_total_int)
    UncertaintyBand.SetName("hist_total_int_band")
    UncertaintyBand.SetTitle("hist_total_int_band")
    UncertaintyBandRatio = getUncertaintyBandRatioGraph(hist_total_int)
    UncertaintyBandRatio.SetName("hist_total_int_bandratio")
    UncertaintyBandRatio.SetTitle("hist_total_int_bandratio")

    if sfitkind=="Pre-fit":
        sfitkind_corrected = "Prefit"
    elif sfitkind == "Post-fit":
	sfitkind_corrected = "Postfit"
    else:
	sfitkind_corrected = sfitkind
    legend_args = (0.005, 0.60, 0.1, 0.90, sfitkind_corrected, 'NDC')
    #legend_args = (0.005, 0.68, 0.105, 0.95, sfitkind_corrected, 'NDC')
    legend = TLegend(*legend_args)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.05)
    legend.AddEntry(hist_signal_int, "t#bar{t} SM", "f")
    legend.AddEntry(hist_singletop_int, "Single top", "f")
    legend.AddEntry(hist_vjets_int, "W/Z+jets", "f")
    legend.AddEntry(hist_dibosons_int, "Diboson", "f")
    legend.AddEntry(hist_ttx_int, "t#bar{t}+X", "f")
    if (fitkind_!='prefit_asimov'):
	legend.AddEntry(hist_data_int, "Data","ep")
    else:
	legend.AddEntry(hist_data_int, "Asimov","ep")

    stack = THStack("THStack_int","THStack_int")
    stack.Add(hist_ttx_int)
    stack.Add(hist_dibosons_int)
    stack.Add(hist_vjets_int)
    stack.Add(hist_singletop_int)
    stack.Add(hist_signal_int)
    if (doLog): stack.SetMinimum(10)

    UncertaintyBand.GetXaxis().SetRangeUser(0,nObsBins)
    UncertaintyBand.SetMinimum(0)
    if (doLog): UncertaintyBand.SetMinimum(10)

    stack.Draw()
    UncertaintyBand.Draw("2AP SAME")
    stack.Draw("HIST SAME")
    hist_data_int.Draw("PSAME")
    legend.Draw("SAME")

    # line_color, line_width, fill_color, fill_style, marker_size, marker_style=1
    style_histo(hist_signal_int, 2, 1, 2, 3004, 0) #3004
    style_histo(hist_singletop_int, 4, 1, 4, 3005, 0) #3005
    style_histo(hist_ttx_int, 8, 1, 8, 3005, 0) #3005
    style_histo(hist_dibosons_int, 42, 1, 42, 3005, 0) #3005
    style_histo(hist_vjets_int, 619, 1, 619, 3005, 0) #3005
    style_histo(hist_data_int, 1, 1, 0, 3001, 1, 20)

    style_histo(UncertaintyBand, 1, 1, 1, 3002, 0)
    style_labels_counting(UncertaintyBand, 'Events', title)
    UncertaintyBand.GetXaxis().SetLabelSize(0)
    UncertaintyBand.GetXaxis().SetTitleSize(0)
    UncertaintyBand.GetYaxis().SetTitleOffset(0.85)

    if year=='Comb':
	line_year = TLine(24,0,24,stack.GetMaximum()*1.05)
	line_year.SetLineStyle(9)
	line_year.SetLineWidth(2)
	line_year.SetLineColor(15)
	line_year.Draw("SAME")
	text_2016 = TLatex()
	text_2016.SetTextSize(0.04)
	text_2016.DrawLatex(12,stack.GetMaximum(),"2016")
	text_2017 = TLatex()
	text_2017.SetTextSize(0.04)
	text_2017.DrawLatex(36,stack.GetMaximum(),"2017")

    if(year=='2016'):
	tdr.cmsPrel(35900., 13.,simOnly=False,thisIsPrelim=True)
    elif(year=='2017'):
       tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)
    elif (year=='Comb'):
       tdr.cmsPrel(77400., 13.,simOnly=False,thisIsPrelim=True)


    pad2 = TPad("pad2_int", "pad2_int", 0, 0, 1, r*(1-epsilon_int))
    pad2.SetTopMargin(0)
    pad2.SetBottomMargin(0.4)
    pad2.SetLeftMargin(leftmargin)
    pad2.SetRightMargin(0.01)
    pad2.SetFillStyle(0)
    canvas.cd()
    pad2.Draw()
    pad2.cd()

    ratio_coef = 0.3

    h_one = TH1F("one_int", "one_int", nObsBins, 0, nObsBins)
    for i in range(nObsBins):
	h_one.SetBinContent(1+i, 1)
    h_one.SetLineWidth(1)
    h_one.SetLineColor(1)
    h_num = hist_total_int.Clone()
    ratio_coef_max = -99
    ratio_coef_min = 99
    for i in range(nObsBins):
	h_num.SetBinContent(i+1,hist_data_int.GetY()[i]/hist_total_int.GetBinContent(i+1))
	h_num.SetBinError(i+1,hist_data_int.GetEYhigh()[i]/hist_total_int.GetBinContent(i+1))
	if ratio_coef_min>(hist_data_int.GetY()[i]-hist_data_int.GetEYhigh()[i])/hist_total_int.GetBinContent(i+1):
	    ratio_coef_min = (hist_data_int.GetY()[i]-hist_data_int.GetEYhigh()[i])/hist_total_int.GetBinContent(i+1)
	if ratio_coef_max< (hist_data_int.GetY()[i]+hist_data_int.GetEYhigh()[i])/hist_total_int.GetBinContent(i+1):
	    ratio_coef_max = (hist_data_int.GetY()[i]+hist_data_int.GetEYhigh()[i])/hist_total_int.GetBinContent(i+1)
    h_num.GetXaxis().SetTitle("aksjd_int")
    print  'ratio_coef_min='+str(ratio_coef_min)+' ratio_coef_max='+str(ratio_coef_max)

    ratioplot_min = 0.7#ratio_coef_min-0.005
    #ratioplot_max = #ratio_coef_max+0.005

    #h_one.Draw("SAME")
    UncertaintyBandRatio.Draw("2A SAME")
    h_num.Draw("E SAME")

    style_histo(UncertaintyBandRatio, 1, 1, 1, 3002, 0)
    UncertaintyBandRatio.GetXaxis().SetRangeUser(0,nObsBins)
    UncertaintyBandRatio.SetMinimum(1-ratio_coef)
    UncertaintyBandRatio.SetMaximum(1+ratio_coef-0.01)
    #UncertaintyBandRatio.SetMinimum(ratio_coef_min-0.005)
    #UncertaintyBandRatio.SetMaximum(ratio_coef_max+0.005)

    UncertaintyBandRatio.GetYaxis().SetTitle("Data/MC")
    UncertaintyBandRatio.GetYaxis().SetMaxDigits(4)
    UncertaintyBandRatio.GetYaxis().CenterTitle()
    UncertaintyBandRatio.GetYaxis().SetLabelSize(0.1)
    #UncertaintyBandRatio.GetYaxis().SetTitleSize(0.1)
    #UncertaintyBandRatio.GetYaxis().SetTitleOffset(0.3)
    UncertaintyBandRatio.GetYaxis().SetTitleSize(0.12)
    UncertaintyBandRatio.GetYaxis().SetTitleOffset(0.39)

    UncertaintyBandRatio.GetXaxis().SetTitle("Sidereal time (h)")
    UncertaintyBandRatio.GetXaxis().SetMaxDigits(0)
    UncertaintyBandRatio.GetXaxis().CenterTitle()
    UncertaintyBandRatio.GetXaxis().SetLabelSize(0)#0.15)
    UncertaintyBandRatio.GetXaxis().SetTitleSize(0.17)
    UncertaintyBandRatio.GetXaxis().SetLabelOffset(0.01)
    UncertaintyBandRatio.GetXaxis().SetTitleSize(0.12)
    UncertaintyBandRatio.GetXaxis().SetTitleOffset(1.2)

    UncertaintyBandRatio.GetXaxis().SetNdivisions(nObsBins,False)
    UncertaintyBandRatio.GetXaxis().SetTickLength(0)#0.05)
    line_axis = []
    text_axis = []
    for i in range(0,nObsBins):
        if i>=24:
            inew=i-24
        else:
            inew=i
	#inew = i
	#if i>=24:
	#    inew=i-24
	#else:
	#    inew=i
	print str(i)
        line_axis.append(TLine(i,ratioplot_min,i,ratioplot_min-0.05))
	#line_axis.append(TLine(i,0.75,i,0.65))
	line_axis[-1].Draw("SAME")
	text_axis.append(TLatex())
	#text_axis[-1].SetTextSize(0.08)
	#text_axis[-1].DrawLatex(i-0.5,0.55,str(inew))
        text_axis[-1].SetTextSize(0.07)
	if inew<10:
            text_axis[-1].DrawLatex(i-0.2,ratioplot_min-0.12,str(inew))
	if inew>=10:
	    text_axis[-1].DrawLatex(i-0.4,ratioplot_min-0.12,str(inew))

        if year=='Comb':
	    line_year2 = TLine(24,1-ratio_coef,24,1+ratio_coef-0.01)
            #line_year2 = TLine(24,ratio_coef_min,24,ratio_coef_max-0.05)
            line_year2.SetLineStyle(9)
            line_year2.SetLineWidth(2)
            line_year2.SetLineColor(15)
            line_year2.Draw("SAME")


    #resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind+sasimov+'_integrated_normfit'
    resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+fitkind_+'_integrated_normfit'
    canvas.SaveAs(resultname+'.pdf')

def displayPrePostFitPlot(fitkind):

	canvas = TCanvas('stack_'+observable+fitkind,'stack_'+observable+fitkind, 2400, 800)
	canvas.UseCurrentStyle()

	if (fitkind=='prefit'):
	    sfitkind = "Pre-fit"
	else:
	    sfitkind = "Post-fit"

	pad1 = TPad("pad1", "pad1", 0, r-epsilon, 1, 1)
	pad1.SetBottomMargin(epsilon)
        pad1.SetLeftMargin(leftmargin)
        pad1.SetRightMargin(0.01)
	
        tm = gStyle.GetPadTopMargin()
        print 'TopMargin: '+str(tm)+' -> '+str(1.5*tm)
        gStyle.SetPadTopMargin(2*tm) #Was 1.5
        pad1.SetTopMargin(2*tm) #Was 1.5

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
	hist_total_covar = []
	chi2_timebin = []
	for i in range(nObsBins):
		print 'Time bin ',str(i)
		hist_data.append(getGraphWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/data")))
		hist_total.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/total")))
		hist_signal.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/signal")))
		hist_singletop.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/singletop")))
		hist_vjets.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/vjets")))
		hist_ttx.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/ttx")))
		hist_dibosons.append(getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/dibosons")))
		hist_total_covar.append(getHist2DWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/ch"+str(i+1)+"/total_covar")))
		chi2_timebin.append(getChi2(hist_data[-1], hist_total[-1], hist_total_covar[-1], 4))
	
	hist_data_allbins = mergeGraph(hist_data)	
	hist_total_allbins = mergeHisto(hist_total)
	hist_signal_allbins = mergeHisto(hist_signal)
	hist_singletop_allbins = mergeHisto(hist_singletop)
	hist_vjets_allbins = mergeHisto(hist_vjets)
	hist_ttx_allbins = mergeHisto(hist_ttx)
	hist_dibosons_allbins = mergeHisto(hist_dibosons)
	
	UncertaintyBand = getUncertaintyBandGraph(hist_total_allbins)
	UncertaintyBandRatio = getUncertaintyBandRatioGraph(hist_total_allbins)

	hist_data_overall = getGraphWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/total_data"))
	hist_total_overall = getHistWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/total_overall"))
	hist_total_covar_overall = getHist2DWithXaxis(fDiagnostics.Get("shapes_"+fitkind+"/overall_total_covar"))
	print 'nbins_overall='+str(hist_total_overall.GetNbinsX())
	sumchi2_correl_Comb = getChi2(hist_data_overall, hist_total_overall, hist_total_covar_overall, nObsBins*4)
	sumchi2_correl_Comb /= (nObsBins*4-24)
        print 'sumchi2_correl_Comb='+str(sumchi2_correl_Comb)


	if sfitkind=="Pre-fit":
	    sfitkind_corrected = "Prefit"
        elif sfitkind == "Post-fit":
            sfitkind_corrected = "Postfit"
        else:
            sfitkind_corrected = sfitkind
	legend_args = (0.005, 0.60, 0.1, 0.90, sfitkind_corrected, 'NDC')
	legend = TLegend(*legend_args)
	legend.SetBorderSize(0)
	legend.SetTextSize(0.05)
	legend.AddEntry(hist_signal_allbins, "t#bar{t} SM", "f")
	#legend.AddEntry(hist_background_allbins, "non-t#bar{t}", "f")
	legend.AddEntry(hist_singletop_allbins, "Single top", "f")
	legend.AddEntry(hist_vjets_allbins, "W/Z+jets", "f")
	legend.AddEntry(hist_dibosons_allbins, "Diboson", "f")
	legend.AddEntry(hist_ttx_allbins, "t#bar{t}+X", "f")
	if (fitkind_!='prefit_asimov'):
	    legend.AddEntry(hist_data_allbins, "Data", "ep")
	else:
	    legend.AddEntry(hist_data_allbins, "Asimov", "ep")

	stack = THStack()
	stack.Add(hist_ttx_allbins)
	stack.Add(hist_dibosons_allbins)
	stack.Add(hist_vjets_allbins)
	stack.Add(hist_singletop_allbins)
	stack.Add(hist_signal_allbins)
	if (doLog): stack.SetMinimum(10)

	UncertaintyBand.GetXaxis().SetRangeUser(min_bin,max_bin*nObsBins)
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
	UncertaintyBand.GetYaxis().SetTitleOffset(0.85)

        if year=='Comb':
            line_year = TLine(24*nbin,0,24*nbin,stack.GetMaximum()*1.1)
            line_year.SetLineStyle(9)
            line_year.SetLineWidth(2)
            line_year.SetLineColor(15)
            line_year.Draw("SAME")
	    text_2016 = TLatex()
	    text_2016.SetTextSize(0.04)
	    text_2016.DrawLatex(12*nbin,stack.GetMaximum(),"2016")
            text_2017 = TLatex()
	    text_2017.SetTextSize(0.04)
            text_2017.DrawLatex(36*nbin,stack.GetMaximum(),"2017")

	if(year=='2016'):
	    tdr.cmsPrel(35900., 13.,simOnly=False,thisIsPrelim=True)
	elif(year=='2017'):
	   tdr.cmsPrel(41500., 13.,simOnly=False,thisIsPrelim=True)
	elif (year=='Comb'):
           tdr.cmsPrel(77400., 13.,simOnly=False,thisIsPrelim=False)


	pad2 = TPad("pad2", "pad2", 0, 0, 1, r*(1-epsilon))
	pad2.SetTopMargin(0)
	pad2.SetBottomMargin(0.4)
        pad2.SetLeftMargin(leftmargin)
        pad2.SetRightMargin(0.01)
	pad2.SetFillStyle(0)
	canvas.cd()
	pad2.Draw()
	pad2.cd()

	ratio_coef = 0.3

	h_one = TH1F("one", "one", max_bin*nObsBins, min_bin, max_bin*nObsBins)
	for i in range(max_bin*nObsBins):
	    h_one.SetBinContent(1+i, 1)
	h_one.SetLineWidth(1)
	h_one.SetLineColor(1)
	#h_num = hist_data.Clone()
	#h_denom = hist_total_allbins
	#h_num.Divide(h_denom)
	h_num = hist_total_allbins.Clone()
	ratio_coef_min = 99
	ratio_coef_max = -99
	for i in range(nbin*nObsBins):
	    h_num.SetBinContent(i+1,hist_data_allbins.GetY()[i]/hist_total_allbins.GetBinContent(i+1))
	    h_num.SetBinError(i+1,hist_data_allbins.GetEYhigh()[i]/hist_total_allbins.GetBinContent(i+1))
            if ratio_coef_min>(hist_data_allbins.GetY()[i]-hist_data_allbins.GetEYhigh()[i])/hist_total_allbins.GetBinContent(i+1):
                ratio_coef_min = (hist_data_allbins.GetY()[i]-hist_data_allbins.GetEYhigh()[i])/hist_total_allbins.GetBinContent(i+1)
            if ratio_coef_max< (hist_data_allbins.GetY()[i]+hist_data_allbins.GetEYhigh()[i])/hist_total_allbins.GetBinContent(i+1):
                ratio_coef_max = (hist_data_allbins.GetY()[i]+hist_data_allbins.GetEYhigh()[i])/hist_total_allbins.GetBinContent(i+1)
        print  'ratio_coef_min='+str(ratio_coef_min)+' ratio_coef_max='+str(ratio_coef_max)

	h_num.GetXaxis().SetTitle("aksjd")
	#ratio = THStack()
	#ratio.Add(h_num)

	#h_one.Draw("SAME")
	UncertaintyBandRatio.Draw("2A SAME")
	h_num.Draw("E SAME")
	#h_one.Draw("SAME")

	style_histo(UncertaintyBandRatio, 1, 1, 1, 3002, 0)
	UncertaintyBandRatio.GetXaxis().SetRangeUser(min_bin,max_bin*nObsBins)
	#UncertaintyBandRatio.GetXaxis().SetRangeUser(0,nObsBins)
	#if sfitkind!="Pre-fit":
	#    UncertaintyBandRatio.SetMinimum(1-ratio_coef)
	#    UncertaintyBandRatio.SetMaximum(1+ratio_coef-0.01)
	#    ratioplot_min = ratio_coef
	#else:
	UncertaintyBandRatio.SetMinimum(ratio_coef_min-0.005)
        UncertaintyBandRatio.SetMaximum(ratio_coef_max+0.005)
	ratioplot_min = ratio_coef_min-0.005
	ratioplot_max = ratio_coef_max+0.005

	#style_labels_counting(h_one, 'Ratio data/mc', title)
	#style_labels_counting(UncertaintyBandRatio, 'Ratio data/mc', title)
	UncertaintyBandRatio.GetYaxis().SetTitle("Data/MC")
        UncertaintyBandRatio.GetYaxis().SetMaxDigits(4)
	UncertaintyBandRatio.GetYaxis().CenterTitle()
	UncertaintyBandRatio.GetYaxis().SetLabelSize(0.1)
	UncertaintyBandRatio.GetYaxis().SetTitleSize(0.12)
	UncertaintyBandRatio.GetYaxis().SetTitleOffset(0.39)

        UncertaintyBandRatio.GetXaxis().SetTitle(title)
        UncertaintyBandRatio.GetXaxis().SetMaxDigits(0)
        UncertaintyBandRatio.GetXaxis().CenterTitle()
	UncertaintyBandRatio.GetXaxis().SetLabelSize(0)#0.15)
	UncertaintyBandRatio.GetXaxis().SetTitleSize(0.12)
        UncertaintyBandRatio.GetXaxis().SetTitleOffset(1.2)
	UncertaintyBandRatio.GetXaxis().SetLabelOffset(0.01)

        #UncertaintyBandRatio.GetXaxis().SetNdivisions(nObsBins,True)
        #UncertaintyBandRatio.GetXaxis().SetTickLength(0.05)
	#h_one.GetXaxis().SetRangeUser(min_bin,max_bin*nObsBins)
	UncertaintyBandRatio.GetXaxis().SetNdivisions(nObsBins,False)
	#UncertaintyBandRatio.GetXaxis().SetNdivisions(nObsBins,nbin-1,False)
	UncertaintyBandRatio.GetXaxis().SetTickLength(0)#0.05)
        #h_one.GetXaxis().SetLabelSize(0.15)
	line_axis = []
	text_axis = []
	#text_axis.append(TLatex())
	#text_axis[-1].SetTextSize(0.02)
        for i in range(0,nObsBins):
	    if i>=24:
		inew=i-24
	    else:
		inew=i
	    print str(i)
	    line_axis.append(TLine(i*nbin,ratioplot_min,i*nbin,ratioplot_min-0.1))
            #line_axis[i].SetLineStyle(9)
            #line_axis[-1].SetLineWidth(2)
            #line_axis[i].SetLineColor(11)
            line_axis[-1].Draw("SAME")
            text_axis.append(TLatex())
            text_axis[-1].SetTextSize(0.07)
	    if inew<10:
	        text_axis[-1].DrawLatex(i*nbin-0.55,ratioplot_min-0.25,str(inew))
	    if inew>=10:
		 text_axis[-1].DrawLatex(i*nbin-1.55,ratioplot_min-0.25,str(inew))
	#line_axis_last = TLine(23*nbin,0.7,23*nbin,0.65)
	#line_axis_last.Draw("SAME")

        if year=='Comb':
            line_year2 = TLine(24*nbin,ratio_coef_min,24*nbin,ratio_coef_max-0.05)
            line_year2.SetLineStyle(9)
            line_year2.SetLineWidth(2)
            line_year2.SetLineColor(15)
            line_year2.Draw("SAME")

        #resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind+sasimov+'_normfit'
	resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+fitkind_+'_normfit'
        canvas.SaveAs(resultname+'.pdf')

        #   UncertaintyBandRatio.GetXaxis().SetBinLabel(1+i*nbin,str(i))
        #UncertaintyBandRatio.GetXaxis().LabelsOption("h")
	#h_one.Draw("SAME")

	#print str(UncertaintyBandRatio.GetXaxis().GetNbins())+' '+str(UncertaintyBandRatio.GetXaxis().GetXmin())+' '+str(UncertaintyBandRatio.GetXaxis().GetXmax())
	#for i in range(24):
	#   h_one.GetXaxis().SetBinLabel(1+i,str(i))
        #h_one.GetXaxis().LabelsOption("h")
	#h_one.GetXaxis().SetLabelSize(0.15)

        #if (fitkind!='prefit'):
	#    resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind
	#else:
	#    resultname = './impacts/'+year+'/'+observable+'_'+year+'_'+sfitkind+'_asimov'

	#CHI2 PLOTS
	sumchi2_2016 = 0
	sumchi2_2017 = 0
	sumchi2_Comb = 0
	print chi2_timebin 
	for i in range(nObsBins):
	    sumchi2_Comb += chi2_timebin[i]
	    if i<nObsBins/2:
		sumchi2_2016 += chi2_timebin[i]
	    else:
		sumchi2_2017 += chi2_timebin[i]
	sumchi2_2016 /= (nObsBins/2*4-24)
	sumchi2_2017 /= (nObsBins/2*4-24)
	sumchi2_Comb /= (nObsBins*4-24)
	print 'sumchi2_2016='+str(sumchi2_2016)
        print 'sumchi2_2017='+str(sumchi2_2017)
	print 'sumchi2_Comb='+str(sumchi2_Comb)

	doChi2plot = False
	if doChi2plot==True:
	    canvasChi2 = TCanvas('Chi2 in time bins','Chi2 in time bins',800,600)
	    hist_chi2_2016 = TH1F("hist_chi2_2016","hist_chi2_2016",10,0,200)
	    hist_chi2_2017 = TH1F("hist_chi2_2017","hist_chi2_2017",10,0,200)
	    for i in range(nObsBins):
		if i<nObsBins/2:
		    hist_chi2_2016.Fill(chi2_timebin[i]/nbin)
		else:
		    hist_chi2_2017.Fill(chi2_timebin[i]/nbin)
	    hist_chi2_2016.SetLineColor(2)
	    hist_chi2_2017.SetLineColor(8)
	    hist_chi2_2016.Draw("HIST")
	    hist_chi2_2017.Draw("HISTsame")	
	    #canvasChi2.SaveAs('./impacts/'+year+'/chi2_'+observable+'_'+year+'_'+sfitkind+sasimov+'_normfit.pdf')
	    canvasChi2.SaveAs('./impacts/'+year+'/chi2_'+observable+'_'+year+'_'+fitkind_+'_normfit.pdf')

	doIntegratedPlot = True
	if doIntegratedPlot:
	    getPlotIntegratedOverObs(fitkind, hist_data, hist_total, hist_signal, hist_singletop, hist_vjets, hist_ttx, hist_dibosons, hist_total_covar)

if asimov=="asimov":
    displayPrePostFitPlot("prefit")
if asimov=="data":
    displayPrePostFitPlot("fit_s")

raw_input('exit')
    
    
