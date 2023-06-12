import os, sys
sys.path.append('./')

import math
import argparse
import numpy as np

from tools.style_manager import *

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TLine,TGraphAsymmErrors
from ROOT import gStyle

import tools.tdrstyle as tdr
tdr.setTDRStyle()

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
#parser.add_argument('workspace', help='display your input workspace')
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
#workspace = args.workspace
observable = args.observable
year = args.year
asimov = args.asimov

pois = []
for i in range(24):
    pois.append('r_'+str(i))

###############################
## Get differential fit results
###############################


bin_number = []
for i in range(24):
   bin_number.append(i)

rate = []
rate_up = []
rate_down = []

ttbar_yield = []
ttbar_unc_down = []
ttbar_unc_up = []

i=0
file = open('log_differential_'+observable+'_'+year+'_'+asimov)
for line in file:
    if TString(line).Contains('68%'):
        bin_number[int(line.split()[0][2:])] = i
        rate.append(float(line.split()[2][1:]))
        rate_down.append(float((line.split()[3]).split('/')[0]))
        rate_up.append(float((line.split()[3]).split('/')[1][1:]))
        i = i+1

print bin_number
print rate
print rate_down
print rate_up

for i in range(24):
    print 'Bin '+str(i)+' rate='+str(rate[bin_number[i]])+ " "+str(rate_down[bin_number[i]])+" +"+str(rate_up[bin_number[i]])
    ttbar_yield.append(rate[bin_number[i]])
    ttbar_unc_down.append(-rate_down[bin_number[i]])
    ttbar_unc_up.append(rate_up[bin_number[i]])


###############################
## Get POI correlation matrix
###############################

fDiagnostics = TFile('fitDiagnostics.prefit_'+observable+'_'+year+'_'+asimov+'.root',"READ")

hCov = fDiagnostics.Get("covariance_fit_s")
hCovPOI = TH2F("covariance_fit_s_POI","covariance_fit_s_POI",24,0,24,24,0,24)
#for i in range(24):
#    hCovPOI.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
#    hCovPOI.GetYaxis().SetBinLabel(1+i, "r_"+str(i))

for i in range(24):
    for j in range(24):
        corrval = hCov.GetBinContent(hCov.GetXaxis().FindBin("r_"+str(i)), hCov.GetYaxis().FindBin("r_"+str(j)))
        hCovPOI.SetBinContent(i+1,j+1,corrval)

def plot2Dmatrix(hCov, palette, title):
    gStyle.SetPaintTextFormat("2.2f")
    canvas = TCanvas(title,title,1000,800)
    pad = TPad("pad","pad",0,0,1,1)
    pad.SetLeftMargin(0.1)
    pad.SetBottomMargin(0.1)
    pad.SetRightMargin(0.12)
    pad.Draw()
    pad.cd()
    for i in range(24):
        hCov.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
        hCov.GetYaxis().SetBinLabel(1+i, "r_"+str(i))
    hCov.GetXaxis().LabelsOption("v")
    hCov.GetXaxis().SetLabelSize(0.025)
    hCov.GetYaxis().SetLabelSize(0.025)
    hCov.GetZaxis().SetLabelSize(0.025)
    hCov.SetTitle("Signal strengths "+title+", "+year)
    #palette = hCov.GetListOfFunctions().FindObject("palette")
    palette.SetX1NDC(0.92)
    palette.SetX2NDC(0.94)
    palette.SetY1NDC(0.2)
    palette.SetY2NDC(0.9)
    hCov.Draw("COLZTEXT")
    #raw_input()
    canvas.Print("impacts/"+title+"SignalStrength_"+observable+"_"+year+"_"+asimov+".pdf")

plot2Dmatrix(hCovPOI, hCov.GetListOfFunctions().FindObject("palette"), "CorrelationMatrix")


###############################
## Compute Covariance matrices
###############################

hCovUp = TH2F("covariance_matrix_up","covariance_matrix_up",24,0,24,24,0,24)
hCovDown = TH2F("covariance_matrix_down","covariance_matrix_down",24,0,24,24,0,24)
#for i in range(24):
#    hCovUp.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
#    hCovUp.GetYaxis().SetBinLabel(1+i, "r_"+str(i))
#    hCovDown.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
#    hCovDown.GetYaxis().SetBinLabel(1+i, "r_"+str(i))

for i in range(24):
    for j in range(24):
	corrval = hCovPOI.GetBinContent(1+i,1+j)
	covUpVal = corrval * ttbar_unc_up[i] * ttbar_unc_up[j] #multiply by predicted number of events in bins i and j
	covDownVal = corrval * ttbar_unc_down[i] * ttbar_unc_down[j] #multiply by predicted number of events in bins i and j
	print('r_'+str(i)+' r_'+str(j)+' covUpVal='+str(covUpVal)+' covDownVal='+str(covDownVal))
	hCovUp.SetBinContent(1+i, 1+j, covUpVal)
        hCovDown.SetBinContent(1+i, 1+j, covDownVal)

plot2Dmatrix(hCovUp, hCov.GetListOfFunctions().FindObject("palette"), "CovarianceMatrixUp")
plot2Dmatrix(hCovDown, hCov.GetListOfFunctions().FindObject("palette"), "CovarianceMatrixDown")

###############################
## Compute jacobian matrix
###############################

#mu = ttbar_yield
nbin = len(ttbar_yield)
mu_avg = sum(ttbar_yield)/nbin

hJacobian = TH2F("jacobian","jacobian",24,0,24,24,0,24)

for i in range(24):
    for j in range(24):
	jacobian_val = -ttbar_yield[i]/nbin
	if (i==j): 
	    jacobian_val = jacobian_val + mu_avg
	jacobian_val = jacobian_val / (mu_avg*mu_avg)
	hJacobian.SetBinContent(1+i, 1+j, jacobian_val)

plot2Dmatrix(hJacobian, hCov.GetListOfFunctions().FindObject("palette"), "Jacobian")

################################################
## Compute normalized differential cross section
################################################

matrix_Jacobian = np.zeros((nbin,nbin))   
matrix_JacobianTranspose = np.zeros((nbin,nbin))
matrix_CovUp = np.zeros((nbin,nbin))
matrix_CovDown = np.zeros((nbin,nbin))

for i in range(24):
    for j in range(24):
	matrix_Jacobian[i][j] = hJacobian.GetBinContent(1+i, 1+j)
        matrix_JacobianTranspose[i][j] = hJacobian.GetBinContent(1+j, 1+i)
	matrix_CovUp[i][j] = hCovUp.GetBinContent(1+i, 1+j)
	matrix_CovDown[i][j] = hCovDown.GetBinContent(1+i, 1+j)


#matrix_JacobianTranspose = np.linalg.inv(matrix_Jacobian)
matrix_CovNormUp = matrix_Jacobian.dot(matrix_CovUp).dot(matrix_JacobianTranspose)
matrix_CovNormDown = matrix_Jacobian.dot(matrix_CovDown).dot(matrix_JacobianTranspose)


mu_norm = []
mu_norm_up = []
mu_norm_down = []

for i in range(24):
    mu_norm.append(ttbar_yield[i]/mu_avg)
    mu_norm_up.append(math.sqrt(matrix_CovNormUp[i][i]))
    mu_norm_down.append(math.sqrt(matrix_CovNormDown[i][i]))
    print('Normalized differential cross section, bin '+str(i)+' mu_norm='+str(mu_norm[i])+' +'+str(mu_norm_up[i])+' -'+str(mu_norm_down[i]))


###################
## Plotting
###################

min_bin = 0
max_bin = 0

legend_coordinates = [0.65, 0.75, 0.87, 0.87]
TH1.SetDefaultSumw2(1)
canvas = TCanvas('Averaged differential cross section','Averaged differential cross section', 800, 700)
canvas.UseCurrentStyle()

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

for i in range(24):
   print('i='+str(i)+' x='+str(x[i])+' y='+str(y[i])+' error_up='+str(error_up[i])+' error_down='+str(error_down[i]))

hist  = TGraphAsymmErrors(24, x, y ,
                          error_left, error_right,
                          error_down, error_up)

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
legend = TLegend(0.5,0.93,0.9,0.8)

if (asimov=='asimov'):
    slegendFit = 'Asimov fit '+year
else:
    slegendFit = 'Data'
#legend.SetHeader(slegend, 'C')
legend.AddEntry(lineSM, 'SM predictions', 'l')
legend.AddEntry(hist, slegendFit, 'lep')
#legend.AddEntry(hist, 'Averaged t#bar{t} differential cross section', 'lep')

#lineSM.Draw()
hist.Draw("ap")
#histSM.Draw("HISTsame")
lineSM.Draw("SAME")
legend.Draw("SAME")


is_center=True

hmin = (min(mu_norm)-max(mu_norm_down))*0.96
hmax = (max(mu_norm)+max(mu_norm_up))*1.04
hist.GetYaxis().SetRangeUser(hmin,hmax)
#hist.GetYaxis().SetRangeUser(0.92,1.08)
#hist.GetYaxis().SetTitle('signal strength #it{#mu}')
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


if asimov=='asimov':
    sim=True
else:
    sim=False

if(year=='2016'):
    tdr.cmsPrel(35900., 13, simOnly=sim, thisIsPrelim=True)
elif(year=='2017'):
    tdr.cmsPrel(41530., 13., simOnly=sim, thisIsPrelim=True)
elif(year=='Comb'):
    tdr.cmsPrel(77400,13., simOnly=sim, thisIsPrelim=True)

if asimov=='asimov':
    sasimov='asimov'
else:
    sasimov='data'

resultname = './impacts/'+year+'/'+observable+'_normalized_differential_'+year+'_'+sasimov
canvas.SaveAs(resultname+'.pdf')

raw_input('exit')




