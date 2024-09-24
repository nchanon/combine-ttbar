import os, sys
sys.path.append('./')

import math
import argparse 
import numpy as np

from tools.style_manager import *

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString, TLatex
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TLine, TGraphErrors, TGraphAsymmErrors, TVirtualFitter
from ROOT import gStyle, TColor, gROOT

import tools.tdrstyle as tdr
tdr.setTDRStyle()

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
#parser.add_argument('workspace', help='display your input workspace')
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='asimov')

args = parser.parse_args()
#workspace = args.workspace
observable = args.observable
year = args.year
asimov = args.asimov

pois = []
pois.append("r_avg")
for i in range(23):
    pois.append('f_'+str(i))

#asi = ''

asi = ' --setParameters '
for i in range(24):
    asi += pois[i]+'=1'
    if i != 23:
        asi += ','


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

#doFit=True
doFit=False

def plot2Dmatrix(hCov, title):
    gStyle.SetPaintTextFormat("2.2f")
    canvas = TCanvas(title,title,1000,800)
    pad = TPad("pad","pad",0,0,1,1)
    pad.SetLeftMargin(0.1)
    pad.SetBottomMargin(0.1)
    pad.SetRightMargin(0.12)
    pad.Draw()
    pad.cd()
    for i in range(24):
        hCov.GetXaxis().SetBinLabel(1+i, pois[i])
        hCov.GetYaxis().SetBinLabel(1+i, pois[i])
    hCov.GetXaxis().LabelsOption("v")
    hCov.GetXaxis().SetLabelSize(0.025)
    hCov.GetYaxis().SetLabelSize(0.025)
    hCov.GetZaxis().SetLabelSize(0.025)
    hCov.SetTitle("Normalized diferential fit: "+title+", "+year)
    palette = hCov.GetListOfFunctions().FindObject("palette")
    hCov.Draw("COLZTEXT")
    #palette.SetX1NDC(0.92)
    #palette.SetX2NDC(0.94)
    #palette.SetY1NDC(0.2)
    #palette.SetY2NDC(0.9)
    #palette.Update()
    #hCov.Draw("COLZTEXT")
    #raw_input()
    canvas.Print("impacts/"+title+"_NormDifferentialFit_"+observable+"_"+year+"_"+asimov+".pdf")

###################
## Core
###################

#optim = ' --robustFit 1'
optim = ' --cminDefaultMinimizerStrategy 0'
#optim = ' --cminDefaultMinimizerStrategy 0 -s 1 --cminDefaultMinimizerTolerance 0.001'
#optim = ' --cminDefaultMinimizerType Minuit --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.5'

if doFit:
    cmd = 'combine -M MultiDimFit '
    cmd += asi
    cmd += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace_norm.root'
    cmd += optim
    #cmd += ' --cminDefaultMinimizerType Minuit'
    #cmd += ' --robustFit 1'
    #cmd += ' --cminDefaultMinimizerStrategy 0'
    #cmd += ' --cminDefaultMinimizerTolerance 0.001'
    #cmd += ' --algo=cross'
    cmd += ' --algo=singles'
    cmd += ' --saveFitResult'
    cmd += ' -n differential_'+observable+'_'+year+'_'+asimov+'_normfit'
    cmd += ' > log_differential_'+observable+'_'+year+'_'+asimov+'_normfit'

    print cmd
    os.system(cmd)

bin_number = []
for i in range(24):
   bin_number.append(i)

rate = []
rate_up = []
rate_down = []

ttbar_yield = []
ttbar_unc_down = []
ttbar_unc_up = []

#higgsCombinedifferential_n_bjets_Comb_asimov_normfit.MultiDimFit.mH120.root
file_res = TFile("./higgsCombinedifferential_"+observable+"_"+year+"_"+asimov+"_normfit.MultiDimFit.mH120.root")
tree = file_res.Get("limit")

file_covar = TFile("./multidimfitdifferential_"+observable+"_"+year+"_"+asimov+"_normfit.root")

hCorrPOI = TH2F("hCorrPOI","hCorrPOI",24,0,24,24,0,24)
hCovPOI_Up = TH2F("hCovPOI_Up","hCovPOI_Up",24,0,24,24,0,24)
hCovPOI_Down = TH2F("hCovPOI_Down","hCovPOI_Down",24,0,24,24,0,24)
hJacobian = TH2F("hJacobian","hJacobian",24,0,24,24,0,24)

fractions_value_central = []
fractions_uncert_up = []
fractions_uncert_down = []
r_avg = 0
r_avg_uncert_down = 0
r_avg_uncert_up = 0

ntimebin=24
tree_map_fractions = []
for i in range(ntimebin):
    tree_map_fractions.append(0)
tree_map_r_avg = 0

ib = 0
for b in tree.GetListOfBranches():
    if b.GetName().find("f_")!=-1:
	num = int(b.GetName()[2:])
	tree_map_fractions[num] = ib
	print b.GetName() + ' ' + str(num) + ' ' + str(ib)
	ib += 1
    elif b.GetName().find("r_avg")!=-1:
	tree_map_r_avg = ib
	ib += 1
print tree_map_fractions
print 'Map r_avg: '+str(tree_map_r_avg)

#exit()

#nuis_syst_b_correlated = []
#nuis_syst_b_correlated_err = []
nuis_syst_elec_id = []
nuis_syst_elec_id_err = []

for j in range(ntimebin):

    fbin = "f_"+str(j)
    fitResult = file_covar.Get("fit_mdf")

    #if j!=23:
	#nuis_syst_b_correlated.append(fitResult.floatParsFinal().find("syst_b_correlated_t"+str(j)).getVal())
	#nuis_syst_b_correlated_err.append(fitResult.floatParsFinal().find("syst_b_correlated_t"+str(j)).getError())
	#nuis_syst_elec_id.append(fitResult.floatParsFinal().find("syst_elec_id_t"+str(j)).getVal())
        #nuis_syst_elec_id_err.append(fitResult.floatParsFinal().find("syst_elec_id_t"+str(j)).getError())

        #print str(fitResult.floatParsFinal().find("syst_b_correlated_t"+str(j)).getVal())

    if j!=23:
        tree.GetEvent(0)
	fractions_value_central.append(tree.GetLeaf(fbin).GetValue())
        tree.GetEvent(1+2*tree_map_fractions[j])
        unc_down = tree.GetLeaf(fbin).GetValue()
        tree.GetEvent(1+2*tree_map_fractions[j]+1)
        unc_up = tree.GetLeaf(fbin).GetValue()
        fractions_uncert_up.append(unc_up-fractions_value_central[-1])
        fractions_uncert_down.append(abs(unc_down-fractions_value_central[-1]))
    elif j==23:
        tree.GetEvent(0)
	r_avg = tree.GetLeaf("r_avg").GetValue()
	tree.GetEvent(1+2*tree_map_r_avg)
        unc_down = tree.GetLeaf("r_avg").GetValue()
        tree.GetEvent(1+2*tree_map_r_avg+1)
        unc_up = tree.GetLeaf("r_avg").GetValue()
	r_avg_uncert_up = unc_up-r_avg
	r_avg_uncert_down = abs(unc_down-r_avg)
	#print 'r_avg = '+str(r_avg)+' +'+str(r_avg_uncert_up)+' -'+str(r_avg_uncert_down)

	f_23 = 24-sum(fractions_value_central)
	fractions_value_central.append(f_23)
	#fitResult = file_covar.Get("fit_mdf")
	for i in range(24):
	    for k in range(24):
		corrval = fitResult.correlation(pois[i], pois[k])
		print 'i='+str(i)+' k='+str(k)+' corrval='+str(corrval)
                hCorrPOI.SetBinContent(i+1,k+1,corrval)
                iunc = i-1
                kunc = k-1
		cov_up = 0
		cov_down = 0
 		if i>0 and k>0:
                    iunc = i-1
                    kunc = k-1
		    cov_up = corrval * fractions_uncert_up[iunc] * fractions_uncert_up[kunc]
                    cov_down = corrval * fractions_uncert_down[iunc] * fractions_uncert_down[kunc]
		if i==0 and k>0:
		    cov_up = corrval * r_avg_uncert_up * fractions_uncert_up[kunc]
                    cov_down = corrval * r_avg_uncert_down * fractions_uncert_down[kunc]
                if i>0 and k==0:
                    cov_up = corrval * r_avg_uncert_up * fractions_uncert_up[iunc]
                    cov_down = corrval * r_avg_uncert_down * fractions_uncert_down[iunc]
		if i==0 and k==0:
		    cov_up = corrval * r_avg_uncert_up * r_avg_uncert_up
		    cov_down = corrval * r_avg_uncert_down * r_avg_uncert_down
		hCovPOI_Up.SetBinContent(i+1,k+1,cov_up)
                hCovPOI_Down.SetBinContent(i+1,k+1,cov_down) 
 
#print 'r_avg = '+str(round(r_avg,3))+' +'+str(round(r_avg_uncert_up,3))+' -'+str(round(r_avg_uncert_down,3))
text = asimov+' '+year+': $\mu_{avg}='+str(round(r_avg,3))+'^{+'+str(round(r_avg_uncert_up,3))+'}_{-'+str(round(r_avg_uncert_down,3))+'}$'
print text
print fractions_value_central
print fractions_uncert_up
print fractions_uncert_down

#exit()

for i in range(24):
    for j in range(24):
	if i==0 and j==0:
	    hJacobian.SetBinContent(1+i,1+j,0)
	elif i==j and i>0:
	    hJacobian.SetBinContent(1+i,1+j,1)
	elif (i==0 and j>0):
            hJacobian.SetBinContent(1+i,1+j,-1) 
	elif (j==0 and i>0):
	    hJacobian.SetBinContent(1+i,1+j,0)
	else:
	    hJacobian.SetBinContent(1+i,1+j,0) #0 or -1?

#plot2Dmatrix(hCorrPOI, "CorrelationMatrix")
#plot2Dmatrix(hCovPOI_Up, "CovarianceMatrixUp")
#plot2Dmatrix(hCovPOI_Down, "CovarianceMatrixDown")
#plot2Dmatrix(hJacobian, "Jacobian")
nbin = 24
matrix_Jacobian = np.zeros((nbin,nbin))
matrix_JacobianTranspose = np.zeros((nbin,nbin))
matrix_CovUp = np.zeros((nbin,nbin))
matrix_CovDown = np.zeros((nbin,nbin))

for i in range(24):
    for j in range(24):
        matrix_Jacobian[i][j] = hJacobian.GetBinContent(1+i, 1+j)
        matrix_JacobianTranspose[i][j] = hJacobian.GetBinContent(1+j, 1+i)
        matrix_CovUp[i][j] = hCovPOI_Up.GetBinContent(1+i, 1+j)
        matrix_CovDown[i][j] = hCovPOI_Down.GetBinContent(1+i, 1+j)

matrix_CovNormUp = matrix_Jacobian.dot(matrix_CovUp).dot(matrix_JacobianTranspose)
matrix_CovNormDown = matrix_Jacobian.dot(matrix_CovDown).dot(matrix_JacobianTranspose)

mu_norm = []
mu_norm_up = []
mu_norm_down = []
for i in range(24):
    mu_norm.append(fractions_value_central[i])
    if i<23:
        mu_norm_up.append(math.sqrt(matrix_CovNormUp[i+1][i+1]))
        mu_norm_down.append(math.sqrt(matrix_CovNormDown[i+1][i+1]))
    if i==23:
        mu_norm_up.append(math.sqrt(matrix_CovNormUp[0][0]))
        mu_norm_down.append(math.sqrt(matrix_CovNormDown[0][0]))

    #print('Normalized differential cross section, bin '+str(i)+' mu_norm='+str(mu_norm[i])+' +'+str(mu_norm_up[i])+' -'+str(mu_norm_down[i]))
    #print('  - value: '+str(mu_norm[i]))
    #print('    errors:')
    #print('    - {asymerror: {minus: '+str(-mu_norm_down[i])+', plus: '+str(mu_norm_up[i])+'}, label: \'total\'}') 


###############################
## Plotting covariance matrices
###############################


doPlotCovariance=False

if doPlotCovariance:
    hCovFractions_Up = TH2F("hCovFractions_Up","hCovFractions_Up", 24,0,24,24,0,24)
    hCovFractions_Down = TH2F("hCovFractions_Down","hCovFractions_Down", 24,0,24,24,0,24)
    for i in range(24):
	for j in range(24):
	    if i<23:
		inew = i+1
	    if i==23:
		inew = 0
	    if j<23:
		jnew = j+1
	    if j==23:
		jnew = 0
	hCovFractions_Up.SetBinContent(1+i,1+j,matrix_CovNormUp[inew][jnew])
	hCovFractions_Down.SetBinContent(1+i,1+j,matrix_CovNormDown[inew][jnew])

def plotCovarianceMatrix(hCovPOI, UpDown):
    gStyle.SetPalette(55)
    gStyle.SetOptStat(0)
    canvas = TCanvas('CovarianceMatrix','CovarianceMatrix',800,700)
    pad = TPad("pad","pad",0,0,1,1)
    #pad.SetLeftMargin(0.16)
    #pad.SetBottomMargin(0.2)
    pad.SetRightMargin(0.1)
    pad.Draw()
    pad.cd()
    for i in range(24):
        hCovPOI.GetXaxis().SetBinLabel(1+i, "f_{"+str(i)+"}")
        hCovPOI.GetYaxis().SetBinLabel(1+i, "f_{"+str(i)+"}")

    hCovPOI.GetXaxis().LabelsOption("v")
    hCovPOI.GetXaxis().SetLabelSize(0.025)
    hCovPOI.GetYaxis().SetLabelSize(0.025)
    hCovPOI.GetZaxis().SetLabelSize(0.025)
	
    hCovPOI.Draw("COLZTEXT")
    pad.Update()

    palette = hCovPOI.GetListOfFunctions().FindObject("palette")
    palette.SetX1NDC(0.92)
    palette.SetX2NDC(0.94)
    palette.SetY1NDC(0.2)
    palette.SetY2NDC(0.9)

    canvas.Print("impacts/CovarianceMatrixFractions_NormFit_"+observable+"_"+year+"_"+UpDown+".pdf")

#plotCovarianceMatrix(hCovFractions_Up, "Up")
#plotCovarianceMatrix(hCovFractions_Down, "Down")

###################
## Plotting
###################

cmunu = 0.01

def textWilson(wilson_):
    if (wilson_=="cLXX"): modwilson = "c_{L,XX}=#minusc_{L,YY}=" + str(cmunu)
    if (wilson_=="cLXY"): modwilson = "c_{L,XY}=c_{L,YX}=" + str(cmunu)
    if (wilson_=="cLXZ"): modwilson = "c_{L,XZ}=c_{L,ZX}=" + str(cmunu)
    if (wilson_=="cLYZ"): modwilson = "c_{L,YZ}=c_{L,ZY}=" + str(cmunu)

    if (wilson_=="cRXX"): modwilson = "c_{R,XX}=#minusc_{R,YY}=" + str(cmunu)
    if (wilson_=="cRXY"): modwilson = "c_{R,XY}=c_{R,YX}=" + str(cmunu)
    if (wilson_=="cRXZ"): modwilson = "c_{R,XZ}=c_{R,ZX}=" + str(cmunu)
    if (wilson_=="cRYZ"): modwilson = "c_{R,YZ}=c_{R,ZY}=" + str(cmunu)

    if (wilson_=="cXX"): modwilson = "c_{XX}=#minusc_{YY}=" + str(cmunu)
    if (wilson_=="cXY"): modwilson = "c_{XY}=c_{YX}=" + str(cmunu)
    if (wilson_=="cXZ"): modwilson = "c_{XZ}=c_{ZX}=" + str(cmunu)
    if (wilson_=="cYZ"): modwilson = "c_{YZ}=c_{ZY}=" + str(cmunu)

    if (wilson_=="dXX"): modwilson = "d_{XX}=#minusd_{YY}=" + str(cmunu)
    if (wilson_=="dXY"): modwilson = "d_{XY}=d_{YX}=" + str(cmunu)
    if (wilson_=="dXZ"): modwilson = "d_{XZ}=d_{ZX}=" + str(cmunu)
    if (wilson_=="dYZ"): modwilson = "d_{YZ}=d_{ZY}=" + str(cmunu)

    return modwilson

doPlotSME = False
doStatOnly = True

wilson = "cLXX"

if doPlotSME:
    print textWilson(wilson)
    fSME = TFile("/gridgroup/cms/nchanon/PPFv2/results/2016/flattree/sme_matrices_alt_puinc.root")
    hSME = fSME.Get("reco_2016_central_"+wilson+'_0').Clone()
    hSME_new = TH1F(hSME.GetName()+"_new",hSME.GetName()+"_new",24,0,24)
    for it in range(24):
	hSME_new.SetBinContent(1+it, 1+cmunu*hSME.GetBinContent(1+it))
    #hSME_new = fSME.Get("reco_2016_central"+wilson).Clone()
    #hSME_new.SetName(hSME.GetName()+"_new")

mu_stat_up = []
mu_stat_down = []

if doStatOnly:
    print 'include stat-only result in the plot'
    fUnc = TFile("impacts/Comb/n_bjets_differential_timeNew_breakdown_Comb_algosingles_normfit_data.root")
    hStatUp = fUnc.Get("statUp")
    hStatDown = fUnc.Get("statDown")
    for iv in range(24):
        mu_stat_up.append(hStatUp.GetBinContent(1+iv)/100)
	mu_stat_down.append(-hStatDown.GetBinContent(1+iv)/100)


min_bin = 0
max_bin = 0

legend_coordinates = [0.65, 0.75, 0.87, 0.87]
TH1.SetDefaultSumw2(1)
canvas = TCanvas('Averaged differential cross section','Averaged differential cross section', 800, 700)
canvas.UseCurrentStyle()

pad1 = TPad("pad1","pad1",0,0,1,1)
#pad1.SetLeftMargin(0.1)
#pad1.SetBottomMargin(0.1)
#pad1.SetRightMargin(0.12)

tm = gStyle.GetPadTopMargin()
print 'TopMargin: '+str(tm)+' -> '+str(1.5*tm)
gStyle.SetPadTopMargin(1.5*tm)
pad1.SetTopMargin(1.5*tm)

pad1.Draw()
pad1.cd()

#histSM = TH1F('histSM','histSM',24,0,24)
#for i in range(24):
#    histSM.Fill(i+1,1)
#histSM.SetLineColor(2)
#histSM.SetLineWidth(2)

y = np.array(mu_norm, dtype='double')
x = np.array([i+0.5 for i in range(24)], dtype='double')

error_left = np.array([0.01 for i in range(24)], dtype='double')
error_right = np.array([0.01 for i in range(24)], dtype='double')

error_up = np.array(mu_norm_up, dtype='double')
error_down = np.array(mu_norm_down, dtype='double')

if doStatOnly:
    error_stat_up = np.array(mu_stat_up, dtype='double')
    error_stat_down = np.array(mu_stat_down, dtype='double')

for i in range(24):
    print('  - value: '+str(mu_norm[i]))
    print('    errors:')
    print('    - {asymerror: {minus: '+str(-mu_norm_down[i])+', plus: '+str(mu_norm_up[i])+'}, label: \'Stat.+syst.\'}')
    print('    - {asymerror: {minus: '+str(-error_stat_down[i])+', plus: '+str(error_stat_up[i])+'}, label: \'Stat.\'}')
   #print('i='+str(i)+' x='+str(x[i])+' y='+str(y[i])+' error_up='+str(error_up[i])+' error_down='+str(error_down[i]))
   #print('i='+str(i)+' x='+str(x[i])+' y='+str(y[i])+' error_stat_up='+str(error_stat_up[i])+' error_stat_down='+str(error_stat_down[i]))


hist  = TGraphAsymmErrors(24, x, y ,
                          error_left, error_right,
                          error_down, error_up)

if doStatOnly:
	histStat = TGraphAsymmErrors(24, x, y ,
                          error_left, error_right,
                          error_stat_down, error_stat_up)
	color = gROOT.GetColor(3)
	color.SetRGB(253/255.,174/255.,97/255.)
	histStat.SetLineColor(3)
	histStat.SetMarkerColor(3)
	histStat.SetLineWidth(2)

#histSM = TH1F('histSM','histSM',24,0,24)
#for i in range(24):
#    histSM.Fill(i+1,1)
#histSM.SetLineColor(3)
#histSM.SetLineWidth(2)
lineSM = TLine(0,1,24,1)
lineSM.SetLineWidth(2)
lineSM.SetLineColor(2)
#lineSM.Draw()

#titleYaxis = 'Averaged t#bar{t} differential cross section'
titleYaxis = '1/(#sigma_{t#bar{t}}/24) d#sigma_{t#bar{t}}/dt (h^{-1})'
hist.GetYaxis().SetTitle(titleYaxis)
legend = TLegend(0.5,0.9,0.9,0.8)
if doStatOnly:
    legend = TLegend(0.55,0.9,0.9,0.77)

legend.SetBorderSize(0)
legend.SetTextSize(0.05)
if (asimov=='asimov'):
    slegendFit = 'Asimov fit '+year
else:
    slegendFit = 'Stat.+syst.'
#legend.SetHeader(slegend, 'C')
legend.AddEntry(hist, slegendFit, 'e')
if doStatOnly:
    legend.AddEntry(histStat, 'Stat.', 'ep')
legend.AddEntry(lineSM, 'SM expectation', 'l')
if doPlotSME:
    hSME_new.SetLineWidth(2)
    hSME_new.SetLineColor(8)
    #legend.AddEntry(hSME_new, "cLXX=0.02", 'l')
    legend.AddEntry(hSME_new, textWilson(wilson), 'l')
#legend.AddEntry(hist, slegendFit, 'ep')
#legend.AddEntry(hist, 'Averaged t#bar{t} differential cross section', 'lep')

#lineSM.Draw()
hist.Draw("ap")
if doStatOnly:
    histStat.Draw("psame")
#histSM.Draw("HISTsame")
lineSM.Draw("SAME")
if doPlotSME:
    hSME_new.Draw("same")
legend.Draw("SAME")


is_center=True

hmin = (min(mu_norm)-max(mu_norm_down))*0.96
hmax = (max(mu_norm)+max(mu_norm_up))*1.04
hist.GetYaxis().SetRangeUser(hmin,hmax)
#hist.GetYaxis().SetRangeUser(0.92,1.08)
#hist.GetYaxis().SetTitle('signal strength #it{#mu}')
hist.GetYaxis().SetRange(0,2)
hist.GetYaxis().SetTitleSize(0.05)
hist.GetYaxis().SetLabelSize(0.05)
hist.GetYaxis().SetTitleOffset(1.5)

hist.GetXaxis().SetRangeUser(0,24)
hist.GetXaxis().SetTitle('Sidereal hour (h)')
hist.GetXaxis().SetRangeUser(0,24)
hist.GetXaxis().SetTitleSize(0.05)
hist.GetXaxis().SetLabelSize(0.05)
hist.GetXaxis().SetTitleOffset(1.2)

if(is_center):
    hist.GetXaxis().CenterTitle()
    hist.GetYaxis().CenterTitle()

style_histo(hist,   1, 2, 4, 3005, 1,20)
hist.SetMarkerColor(1)


if asimov=='asimov':
    sim=True
else:
    sim=False

if(year=='2016'):
    tdr.cmsPrel(36300., 13, simOnly=sim, thisIsPrelim=True)
elif(year=='2017'):
    tdr.cmsPrel(41500., 13., simOnly=sim, thisIsPrelim=True)
elif(year=='Comb'):
    tdr.cmsPrel(77800,13., simOnly=sim, thisIsPrelim=False)

if asimov=='asimov':
    sasimov='asimov'
else:
    sasimov='data'

resultname = './impacts/'+year+'/'+observable+'_normalized_differential_normfit_'+year+'_'+sasimov
canvas.SaveAs(resultname+'.pdf')

#exit()

####################################
## Plotting norm diff XS vs PU, Lumi
####################################

pu_mean_time_2016=[21.6264, 22.2626, 23.3817, 23.912, 24.1626, 23.9724, 23.1957, 22.3314, 22.2815, 21.7199, 21.7161, 21.6868, 23.3312, 23.6596, 24.2805, 23.7329, 24.0503, 23.4109, 23.324, 22.9327, 23.5668, 23.2717, 23.0371, 22.1822]
pu_meanerr_time_2016=[0.0204301, 0.0223933, 0.0237869, 0.0241815, 0.0226658, 0.0221875, 0.0215036, 0.0204143, 0.0217224, 0.0227949, 0.0233063, 0.0235045, 0.026977, 0.0254718, 0.024431, 0.0238533, 0.0242498, 0.0239768, 0.0241916, 0.0238761, 0.0251013, 0.0238977, 0.0230493, 0.0216925]
pu_meanup_time_2016=[22.6212, 23.2867, 24.4572, 25.012, 25.2741, 25.0751, 24.2627, 23.3587, 23.3065, 22.719, 22.715, 22.6844, 24.4045, 24.748, 25.3974, 24.8246, 25.1566, 24.4878, 24.3969, 23.9876, 24.6509, 24.3422, 24.0968, 23.2026]
pu_meandown_time_2016=[20.6316, 21.2385, 22.3061, 22.8121, 23.0511, 22.8697, 22.1287, 21.3042, 21.2566, 20.7208, 20.7171, 20.6892, 22.258, 22.5713, 23.1636, 22.6412, 22.944, 22.334, 22.2511, 21.8778, 22.4828, 22.2012, 21.9774, 21.1618]
lumi_time_2016=[1.44647, 1.48798, 1.61767, 1.7794, 1.92318, 1.87963, 1.84988, 1.6777, 1.5657, 1.37908, 1.41847, 1.27575, 1.32944, 1.26866, 1.36462, 1.35673, 1.44754, 1.33093, 1.31654, 1.34472, 1.49514, 1.51192, 1.45737, 1.46701]
lumi_err_time_2016=[0.0051413, 0.005241, 0.00547008, 0.00575432, 0.0060019, 0.00598975, 0.00596003, 0.00571216, 0.00551915, 0.00517537, 0.0052412, 0.00495628, 0.00501979, 0.0048855, 0.00502409, 0.00500428, 0.00518453, 0.00495972, 0.00486897, 0.00488014, 0.00515956, 0.00520054, 0.00511711, 0.00516829]

pu_mean_time_2017=[31.7385, 31.8198, 32.3273, 32.4375, 32.7786, 33.4619, 32.7123, 33.5479, 34.2367, 33.3084, 32.6375, 31.6112, 31.5979, 32.8485, 32.9402, 33.3106, 32.6652, 31.5084, 30.8107, 32.8567, 34.0875, 32.824, 32.6139, 32.9831]
pu_meanerr_time_2017=[0.0384954, 0.0378822, 0.0370378, 0.0364732, 0.0380747, 0.038831, 0.0410521, 0.039546, 0.037255, 0.0371234, 0.039405, 0.0411367, 0.042237, 0.0402083, 0.0370948, 0.0362293, 0.0384523, 0.0369462, 0.0362201, 0.0385635, 0.0393325, 0.0388335, 0.0395711, 0.042392]
pu_meanup_time_2017=[33.1984, 33.2835, 33.8144, 33.9296, 34.2864, 35.0011, 34.2171, 35.0911, 35.8116, 34.8406, 34.1388, 33.0653, 33.0514, 34.3596, 34.4554, 34.8428, 34.1678, 32.9578, 32.228, 34.3681, 35.6555, 34.3339, 34.1141, 34.5003]
pu_meandown_time_2017=[30.2785, 30.3561, 30.8403, 30.9454, 31.2708, 31.9226, 31.2075, 32.0047, 32.6618, 31.7762, 31.1362, 30.1571, 30.1444, 31.3375, 31.4249, 31.7783, 31.1626, 30.059, 29.3934, 31.3453, 32.5194, 31.3141, 31.1137, 31.4659]
lumi_time_2017=[1.57652, 1.65742, 1.81687, 1.94675, 1.8116, 1.72716, 1.59509, 1.82181, 2.13058, 2.00473, 1.85092, 1.61361, 1.48127, 1.57885, 1.79113, 1.76677, 1.6747, 1.6583, 1.60438, 1.80112, 1.8061, 1.6899, 1.57977, 1.50152]
lumi_err_time_2017=[0.00603861, 0.00612928, 0.00645705, 0.00659428, 0.00641844, 0.00625595, 0.00611893, 0.00661596, 0.007082, 0.00691554, 0.0067004, 0.0063233, 0.00606456, 0.00615804, 0.00645698, 0.00634228, 0.0061069, 0.0060927, 0.0059807, 0.00629895, 0.00629845, 0.00619408, 0.00599071, 0.00590482]

trigSF_time = []
trigSF_err_time = []
file_trig_2016 = TFile("/gridgroup/cms/nchanon/PPFv2/inputs/timed/TriggerSF_2016_noNvtx.root")
file_trig_2017 = TFile("/gridgroup/cms/nchanon/PPFv2/inputs/timed/TriggerSF_2017_noNvtx.root") 
if year=="2016":
    hist_triggerSF_stat = file_trig_2016.Get('h_SF_emu_sidereel_nominal')
if year=="2017":
    hist_triggerSF_stat = file_trig_2017.Get('h_SF_emu_sidereal_nominal')
for i in range(24):
    trigSF_time.append(hist_triggerSF_stat.GetBinContent(1+i))
    trigSF_err_time.append(hist_triggerSF_stat.GetBinError(1+i))

print trigSF_time
print trigSF_err_time


if year=="2016" or year=="2017":
    
    if year=="2016":
	pu_mean_time = pu_mean_time_2016
	pu_meanerr_time = pu_meanerr_time_2016
	pu_meanup_time = pu_meanup_time_2016
	pu_meandown_time = pu_meandown_time_2016
	lumi_time = lumi_time_2016
	lumi_err_time = lumi_err_time_2016
    if year=="2017":
        pu_mean_time = pu_mean_time_2017
        pu_meanerr_time = pu_meanerr_time_2017
        pu_meanup_time = pu_meanup_time_2017
        pu_meandown_time = pu_meandown_time_2017
        lumi_time = lumi_time_2017
        lumi_err_time = lumi_err_time_2017

    pu_mean_errleft_time = []
    pu_mean_errright_time = []
    for i in range(24):
        pu_mean_errleft_time.append(abs(pu_mean_time[i]-pu_meandown_time[i]))
        pu_mean_errright_time.append(abs(pu_mean_time[i]-pu_meanup_time[i]))

    pu = np.array(pu_mean_time, dtype='double')
    #pu_errleft = np.array(pu_mean_errleft_time, dtype='double')
    #pu_errright = np.array(pu_mean_errright_time, dtype='double')
    pu_errleft = np.array(pu_meanerr_time, dtype='double')
    pu_errright = np.array(pu_meanerr_time, dtype='double')

    #lumi = np.array(lumi_time, dtype='double')
    #lumi_errleft = np.array(lumi_err_time, dtype='double')
    #lumi_errright = np.array(lumi_err_time, dtype='double')


def plotNormDiffXSvsVar(x_tmp, y_tmp, x_errleft_tmp, x_errright_tmp, y_errdown_tmp, y_errup_tmp, var, titleXaxis, titleYaxis):

    x = np.array(x_tmp, dtype='double')
    x_errleft = np.array(x_errleft_tmp, dtype='double')
    x_errright = np.array(x_errright_tmp, dtype='double')

    y = np.array(y_tmp, dtype='double')
    y_errdown = np.array(y_errdown_tmp, dtype='double')
    y_errup = np.array(y_errup_tmp, dtype='double')


    histPU  = TGraphAsymmErrors(24, x, y,
                              x_errleft, x_errright,
                              y_errdown, y_errup)

    resPU = histPU.Fit("pol1","S")
    chi2PU = resPU.Chi2()
    probPU = resPU.Prob()
    slopePU = resPU.Parameter(1)
    slopePU_err = resPU.ParError(1)
    #corr_coeff = slopePU / (sum(x_errleft)/len(x_errleft)) / (sum(y_errdown)/len(y_errdown))
    corr_coeff_num = 0
    corr_coeff_denom1 = 0
    corr_coeff_denom2 = 0
    x_avg = sum(x)/len(x)
    y_avg = sum(y)/len(y)
    for i in range(len(x)):
	corr_coeff_num += (x[i]-x_avg) * (y[i]-y_avg)
	corr_coeff_denom1 += (x[i]-x_avg)*(x[i]-x_avg)
	corr_coeff_denom2 += (y[i]-y_avg)*(y[i]-y_avg)
    corr_coeff = corr_coeff_num / math.sqrt(corr_coeff_denom1 * corr_coeff_denom2)
    var_x = corr_coeff_denom1 / sum(x)
    var_y = corr_coeff_denom2 / sum(y)
    
    corr_fromslope = slopePU * math.sqrt(var_x) / math.sqrt(var_y)
    corr_fromslope_err = slopePU_err * math.sqrt(var_x) / math.sqrt(var_y) 

    print var+' Fit to pol1: slope='+str(slopePU)+' slope_err='+str(slopePU_err)+' chi2='+str(chi2PU)+' p-value='+str(probPU)
    print 'Correlation: '+str(corr_coeff)
    print 'Correlation from slope: '+str(corr_fromslope)+' +/- '+str(corr_fromslope_err)

    hxmin = min(x)-1
    hxmax = max(x)+1
    hmin = (min(y)-max(y_errdown))*0.96
    hmax = (max(y)+max(y_errup))*1.04

    fitPU_err = TGraphErrors(100)
    fitPU_err.SetName("fit_err")
    for i in range(100):
	fitPU_err.SetPoint(i, hxmin+i/100.*(hxmax-hxmin), 0)
    TVirtualFitter.GetFitter().GetConfidenceIntervals(fitPU_err)
    fitPU_err.SetLineColor(0)
    fitPU_err.SetFillStyle(3003)

    canvasPU = TCanvas('Averaged differential cross section vs '+var,'Averaged differential cross section vs '+var, 800, 700)
    canvasPU.UseCurrentStyle()

    #titleYaxis = '1/(#sigma_{t#bar{t}}/24) d#sigma_{t#bar{t}}/dt (h^{-1})'
    histPU.GetYaxis().SetTitle(titleYaxis)
    legendPU = TLegend(0.65,0.93,0.95,0.8)
    legendPU.AddEntry(histPU, slegendFit, 'lep')
    legendPU.AddEntry(histPU.GetFunction("pol1"), "Linear fit", 'l')
    legendPU.AddEntry(fitPU_err, "Fit 95% CL", 'f')

    histPU.Draw("ap")
    fitPU_err.Draw("E3 SAME")
    histPU.Draw("pSAME")
    legendPU.Draw("SAME")


    text_slope = TLatex()
    text_slope.SetName("latex_"+var)
    text_slope.SetTextSize(0.03)
    #text_slope.DrawLatex(min(x),hmax*0.98,"slope = "+str(round(slopePU,4))+" #pm "+str(round(slopePU_err,4)))
    text_slope.DrawLatex(min(x),hmax*0.98,"corr = "+str(round(corr_fromslope,3))+" #pm "+str(round(corr_fromslope_err,3)))
    #print 'Latex '+str(hxmin*1.05)+' '+str(hmax*0.98)

    gStyle.SetOptFit(0)

    histPU.GetYaxis().SetRangeUser(hmin,hmax)
    histPU.GetYaxis().SetRange(0,2)
    histPU.GetYaxis().SetTitleSize(0.04)
    histPU.GetYaxis().SetLabelSize(0.04)

    histPU.GetXaxis().SetRangeUser(hxmin,hxmax)
    histPU.GetXaxis().SetTitle(titleXaxis)
    histPU.GetXaxis().SetTitleSize(0.04)
    histPU.GetXaxis().SetLabelSize(0.04)

    if(is_center):
	histPU.GetXaxis().CenterTitle()
	histPU.GetYaxis().CenterTitle()

    style_histo(histPU,   1, 2, 4, 3005, 1,20)
    style_histo(fitPU_err,   1, 2, 4, 3005, 1,20)

    histPU.SetMarkerColor(1)

    if(year=='2016'):
	tdr.cmsPrel(36300., 13, simOnly=sim, thisIsPrelim=True)
    elif(year=='2017'):
	tdr.cmsPrel(41530., 13., simOnly=sim, thisIsPrelim=True)

    resultname = './impacts/'+year+'/'+observable+'_normalized_differential_normfit_vs'+var+'_'+year+'_'+sasimov
    canvasPU.SaveAs(resultname+'.pdf')

if year=="2016" or year=="2017":
    titleYaxis = '1/(#sigma_{t#bar{t}}/24) d#sigma_{t#bar{t}}/dt (h^{-1})'
    plotNormDiffXSvsVar(pu, y, pu_errleft, pu_errright, error_down, error_up, "PU", "number of PU interactions", titleYaxis)
    #plotNormDiffXSvsVar(lumi_time, y, lumi_err_time, lumi_err_time, error_down, error_up, "Lumi", "Integrated Lumi (pb^{-1})", titleYaxis)
    #plotNormDiffXSvsVar(trigSF_time, y, trigSF_err_time, trigSF_err_time, error_down, error_up, "TriggerSF", "Trigger SF", titleYaxis)
    #plotNormDiffXSvsVar(nuis_syst_b_correlated, y, nuis_syst_b_correlated_err, nuis_syst_b_correlated_err, error_down, error_up, "syst_b_correlated", "syst_b_correlated", titleYaxis)
    #plotNormDiffXSvsVar(nuis_syst_elec_id, y, nuis_syst_elec_id_err, nuis_syst_elec_id_err, error_down, error_up, "syst_elec_id", "syst_elec_id", titleYaxis)

    #plotNormDiffXSvsVar(pu, lumi_time, pu_errleft, pu_errright, lumi_err_time, lumi_err_time, "PU-Lumi", "number of PU interactions", "Integrated Lumi (pb^{-1})")
    #plotNormDiffXSvsVar(pu, trigSF_time, pu_errleft, pu_errright, trigSF_err_time, trigSF_err_time, "PU-TriggerSF", "number of PU interactions", "Trigger SF")



#raw_input()
exit()
'''
    #Lumi plot
    lumi = np.array(lumi_time, dtype='double')
    lumi_errleft = np.array(lumi_err_time, dtype='double')
    lumi_errright = np.array(lumi_err_time, dtype='double')

    histLumi = TGraphAsymmErrors(24, lumi, y,
                              lumi_errleft, lumi_errright,
                              error_down, error_up)

    resLumi = histLumi.Fit("pol1","S")
    chi2Lumi = resLumi.Chi2()
    probLumi = resLumi.Prob()
    slopeLumi = resLumi.Parameter(1)
    slopeLumi_err = resLumi.ParError(1)
    print 'Lumi Fit to pol1: slope='+str(slopeLumi)+' slope_err='+str(slopeLumi_err)+' chi2='+str(chi2Lumi)+' p-value='+str(probLumi)

    canvasLumi = TCanvas('Averaged differential cross section vs Lumi','Averaged differential cross section vs Lumi', 800, 700)
    canvasLumi.UseCurrentStyle()

    titleYaxis = '1/(#sigma_{t#bar{t}}/24) d#sigma_{t#bar{t}}/dt (h^{-1})'
    histLumi.GetYaxis().SetTitle(titleYaxis)
    legendLumi = TLegend(0.5,0.93,0.9,0.8)
    legendLumi.AddEntry(histLumi, slegendFit, 'lep')

    histLumi.Draw("ap")
    legendLumi.Draw("SAME")

    hmin = (min(mu_norm)-max(mu_norm_down))*0.96
    hmax = (max(mu_norm)+max(mu_norm_up))*1.04
    histLumi.GetYaxis().SetRangeUser(hmin,hmax)
    histLumi.GetYaxis().SetRange(0,2)
    histLumi.GetYaxis().SetTitleSize(0.04)
    histLumi.GetYaxis().SetLabelSize(0.04)

    histLumi.GetXaxis().SetRangeUser(min(pu)-1,max(pu)+1)
    histLumi.GetXaxis().SetTitle('Integrated Lumi (pb^{-1})')
    histLumi.GetXaxis().SetTitleSize(0.04)
    histLumi.GetXaxis().SetLabelSize(0.04)

    if(is_center):
        histLumi.GetXaxis().CenterTitle()
        histLumi.GetYaxis().CenterTitle()

    style_histo(hist,   1, 2, 4, 3005, 1,20)
    histLumi.SetMarkerColor(1)

    if(year=='2016'):
        tdr.cmsPrel(35900., 13, simOnly=sim, thisIsPrelim=True)
    elif(year=='2017'):
        tdr.cmsPrel(41530., 13., simOnly=sim, thisIsPrelim=True)

    resultname = './impacts/'+year+'/'+observable+'_normalized_differential_normfit_vsLumi_'+year+'_'+sasimov
    canvasLumi.SaveAs(resultname+'.pdf')






raw_input()
exit()

i=0
file = open('log_differential_'+observable+'_'+year+'_'+asimov+'_normfit')
for line in file:
    if TString(line).Contains('68%'):
        #print line
        #for word in line.split():
	#print line.split()[0][2:]
	#print line.split()[2]
	#print line.split()[3]
	bin_number[int(line.split()[0][2:])] = i
	rate.append(float(line.split()[2][1:]))
	rate_down.append(float((line.split()[3]).split('/')[0]))
        rate_up.append(float((line.split()[3]).split('/')[1][1:]))
	#ttbar_yield.update({bin_number[-1]: rate[-1]})
	#ttbar_unc_down.update({bin_number[-1]: rate_down[-1]})
        #ttbar_unc_up.update({bin_number[-1]: rate_up[-1]})
	i = i+1
            #if TString(word).Contains('r_'):
            #    print word[2:]
	    #    bin_number.append(word[2:])	
	    #if TString(word).Contains('-'):
	    #    print word
            #if TString(word).Contains('+'):
	    #    print word	

print bin_number
print rate
print rate_down
print rate_up
#print ttbar_yield
#print ttbar_unc_down
#print ttbar_unc_up

for i in range(24):
    print 'Bin '+str(i)+' rate='+str(rate[bin_number[i]])+ " "+str(rate_down[bin_number[i]])+" +"+str(rate_up[bin_number[i]])
    ttbar_yield.append(rate[bin_number[i]])
    ttbar_unc_down.append(-rate_down[bin_number[i]])
    ttbar_unc_up.append(rate_up[bin_number[i]])
#exit()


#os.system('source scripts/extract_r_in_time.bash '+year)

#file = open('log'+year+'_sorted_final')

#rate = []
#for line in file:
    #print line
    #rate_bin = []
    #for word in line.split():
	#print word
	#if (word[0][:1]!='-'): rate_bin.append(float(word))
	#else: rate_bin.append(-float(word))
    #rate.append(rate_bin)

#print rate

###################
## Plotting
###################

nbin = 0
min_bin = 0
max_bin = 0

legend_coordinates = [0.65, 0.75, 0.87, 0.87]
TH1.SetDefaultSumw2(1)
signal_integral = 0
background_integral_i = []
background_integral = 0
data_integral = 0
syst_up_integral = 0
syst_down_integral = 0
canvas = TCanvas('differential measurment','differential measurment', 800, 700)
canvas.UseCurrentStyle()

def linearized(input, option):
    opt = 0
    if option=='up' :
        opt = 2
    elif option=='down' :
        opt = 1
    else:
        print 'error option'
    foo = []
    for l in input:
        foo.append(l[opt])
    return foo

def squared(list_value):
    somme = 0
    for l in list_value:
        somme += l*l
    return np.sqrt(somme/float(len(list_value)))

################################################################################
## Create Histo 
################################################################################

#x = np.array([1 for i in range(24)], dtype='double')
y = np.array(ttbar_yield, dtype='double')
x = np.array([i+0.5 for i in range(24)], dtype='double')

error_left = np.array([0.01 for i in range(24)], dtype='double')
error_right = np.array([0.01 for i in range(24)], dtype='double')

error_up = np.array(ttbar_unc_up, dtype='double')
error_down = np.array(ttbar_unc_down, dtype='double')


#error_up = np.array(linearized(rate, 'up'), dtype='double')
#error_down = np.array(linearized(rate, 'down'), dtype='double')

for i in range(24):
   print('i='+str(i)+' x='+str(x[i])+' y='+str(y[i])+' error_up='+str(error_up[i])+' error_down='+str(error_down[i]))


print 'error + : '+str(squared(error_up))
print 'error - : '+str(squared(error_down))


s = ''
for i in range(0,11):
    s += '&'+str(i)
print s
s = ''
for i in range(13,23):
    s += '&'+str(i)
print s
s = ''
count =0
for l in error_up:
    s += '&'+str(l)
    count += 1
    if(count==12):
        s += '\n'

print s
print '========'
s = ''
count =0
for l in error_down:
    s += '&'+str(l)
    count += 1
    if(count==12):
        s += '\n'
print s

hist  = TGraphAsymmErrors(24, x, y ,
                          error_left, error_right,
                          error_down, error_up)


################################################################################
## Legend stuff
################################################################################

legend = TLegend(0.5,0.93,0.9,0.8)

if (asimov=='asimov'):
    slegend = 'Asimov fit '+year
else:
    slegend = 'Data fit '+year
legend.SetHeader(slegend, 'C')
legend.AddEntry(hist, 't#bar{t} signal strength', 'lep')

################################################################################
## Draw stuff
################################################################################

hist.Draw("ap")
legend.Draw("SAME")

################################################################################
## Set Style
################################################################################

is_center=True

hmin = (min(ttbar_yield)-max(ttbar_unc_down))*0.94
hmax = (max(ttbar_yield)+max(ttbar_unc_up))*1.06
hist.GetYaxis().SetRangeUser(hmin,hmax)
#hist.GetYaxis().SetRangeUser(0.92,1.08)
hist.GetYaxis().SetTitle('signal strength #it{#mu}')
hist.GetYaxis().SetRange(0,2)
hist.GetYaxis().SetTitleSize(0.04)
hist.GetYaxis().SetLabelSize(0.04)

hist.GetXaxis().SetRangeUser(0,24)
hist.GetXaxis().SetTitle('sidereal time (h)')
hist.GetXaxis().SetRangeUser(0,24)
hist.GetXaxis().SetTitleSize(0.04)
hist.GetXaxis().SetLabelSize(0.04)

if(is_center):
    hist.GetXaxis().CenterTitle()
    hist.GetYaxis().CenterTitle()

style_histo(hist,   1, 2, 4, 3005, 1,20)
hist.SetMarkerColor(1)

if(year=='2016'):
    tdr.cmsPrel(35900., 13.)
elif(year=='2017'):
    tdr.cmsPrel(41530., 13.)
elif(year=='Comb'):
    tdr.cmsPrel(77400,13.)

################################################################################
## Save
################################################################################

if asimov=='asimov':
    sasimov='asimov'
else:
    sasimov='data'

resultname = './impacts/'+year+'/'+observable+'_differential_'+year+'_'+sasimov+'_normfit'

#rootfile_output = TFile(resultname+'.root', "RECREATE")
#canvas.Write()
#canvas.SaveAs(resultname+'.png')
canvas.SaveAs(resultname+'.pdf')
#rootfile_output.Close()

raw_input('exit')

'''
