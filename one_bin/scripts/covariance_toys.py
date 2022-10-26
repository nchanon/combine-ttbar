import os, sys
sys.path.append('./')

import math
import argparse
import subprocess

import numpy as np

from tools.style_manager import *
from tools.norm_xs_utils import *

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

#import print_options
#print_options.set_float_precision(4)

import tools.tdrstyle as tdr
tdr.setTDRStyle()

fCovar = []
fCovarPrefix = "./multidimfit"
observable = "n_bjets"
year="Comb"

#nuisname = "hdamp"
#NuisanceGroup="theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco"

#nuisname = "theory"
nuisname = "bkgd_norm"
NuisanceGroup="exp_theory_bkgdnorm_lumi_mcstat"

hCorrPOI_mean = TH2F("hCorrPOI_mean","hCorrPOI_mean",24,0,24,24,0,24)
hCovUp_mean = TH2F("hCovUp_mean","hCovUp_mean",24,0,24,24,0,24)
hCovDown_mean = TH2F("hCovDown_mean","hCovDown_mean",24,0,24,24,0,24)
hCovAvg_mean = TH2F("hCovAvg_mean","hCovAvg_mean",24,0,24,24,0,24)
hCov_sample = TH2F("hCov_sample","hCov_sample",24,0,24,24,0,24)


ntimebin = 24


####################################
# Get average covariance matrices
####################################

print 'Get covariance matrices AVERAGED OVER SAMPLES'

#corrval = np.zeros((ntimebin,ntimebin)) 
corrval_sum = np.zeros((ntimebin,ntimebin))
covUp_sum = np.zeros((ntimebin,ntimebin))
covDown_sum = np.zeros((ntimebin,ntimebin))
covAvg_sum = np.zeros((ntimebin,ntimebin))

for k in range(0, 200):
    print str(k)

    fCovar.append(TFile(fCovarPrefix+".freeze"+nuisname+"_"+observable+"_"+year+"_"+NuisanceGroup+"_toy_"+str(k)+".root"))
    fitResult = fCovar[k].Get("fit_mdf")
    parameters = fitResult.floatParsFinal()

    for i in range(ntimebin):
	uncert_i = parameters.find("r_"+str(i)).getError()
        uncert_up_i = parameters.find("r_"+str(i)).getErrorHi()
        uncert_down_i = parameters.find("r_"+str(i)).getErrorLo()
        for j in range(ntimebin):
            corrval = fitResult.correlation("r_"+str(i), "r_"+str(j))
            #uncert_up_i = parameters.find("r_"+str(i)).getErrorHi()
	    uncert_j = parameters.find("r_"+str(j)).getError()
            uncert_up_j = parameters.find("r_"+str(j)).getErrorHi()
	    #uncert_down_i = parameters.find("r_"+str(i)).getErrorLo()
            uncert_down_j = parameters.find("r_"+str(j)).getErrorLo()
	    covUp_sum[i][j] += corrval * uncert_up_i * uncert_up_j
	    covDown_sum[i][j] += corrval * uncert_down_i * uncert_down_j
	    covAvg_sum[i][j] += corrval * uncert_i * uncert_j
	    #corrval_sum[i][j] += corrval[i][j]
            #print str(k)+" "+str(i)+" "+str(j)+" "+str(corrval)

for i in range(ntimebin):
    for j in range(ntimebin):
	#hCorrPOI_mean.SetBinContent(1+i,1+j,corrval_sum[i][j]/200.)
	hCovUp_mean.SetBinContent(1+i,1+j,covUp_sum[i][j]/200.)
        hCovDown_mean.SetBinContent(1+i,1+j,covDown_sum[i][j]/200.)
	hCovAvg_mean.SetBinContent(1+i,1+j,covAvg_sum[i][j]/200.)

####################################
# Get sample covariance matrix
####################################

print 'Get SAMPLE covariance matrix'

central_val = np.zeros((200,ntimebin))
central_val_samplemean = []

print 'Get signal strengths'
for i in range(0, 200):
    print str(i)
    fitResult = fCovar[i].Get("fit_mdf")
    parameters = fitResult.floatParsFinal()

    for j in range(ntimebin):
	val_j = parameters.find("r_"+str(j)).getValV()
	central_val[i][j] = val_j

print 'Compute mean of signal strengths over samples'
for j in range(ntimebin):
    val_sum = 0  
    for i in range(0, 200):
	val_sum += central_val[i][j] 
    central_val_samplemean.append(val_sum/200.)

print 'Estimate sample covariance matrix'
cov_sample = np.zeros((ntimebin,ntimebin))
for j in range(ntimebin):
    for k in range(ntimebin):
	print str(j)+' '+str(k)
	for i in range(0, 200):
	    cov_sample[j][k] += (central_val[i][j]-central_val_samplemean[j])*(central_val[i][k]-central_val_samplemean[k])
	cov_sample[j][k] /= (200.-1.)
	hCov_sample.SetBinContent(1+j,1+k,cov_sample[j][k])


fOut = TFile("covariance_fromToys_"+observable+"_"+year+"_"+NuisanceGroup+"_freeze"+nuisname+".root","RECREATE")
fOut.cd()
hCovAvg_mean.Write()
hCovUp_mean.Write()
hCovDown_mean.Write()
hCov_sample.Write()
fOut.Close()

#raw_input()

