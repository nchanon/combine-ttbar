import os, sys
sys.path.append('./')

import argparse
import subprocess
import numpy as np

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame, TColor, TLine, TGraph
from ROOT import gPad, gStyle, TGraphAsymmErrors

import tools.tdrstyleNew as tdr
tdr.setTDRStyle()

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test')
#parser.add_argument('multiple',help='set if multiple fit', default='single')

args = parser.parse_args()
observable = args.observable
asimov = args.asimov
year = args.year
#multiple = args.multiple

if asimov=='asimov':
    sasimov='_asimov'
else:
    sasimov='_data'

#doSingle = True
doSingle = False
doOthersFloating = True
doMultiple = False
#doMultiple = True
do2sigma = True

results_single = open('impacts/'+year+'/'+asimov+'/fit_'+observable+'_'+year+sasimov+'.txt')
results_multiple = open('impacts/'+year+'/'+asimov+'/fit_multiple_'+observable+'_'+year+sasimov+'.txt')
if do2sigma==False:
    results_othersfloating = open('impacts/'+year+'/'+asimov+'/fit_othersfloating_'+observable+'_'+year+sasimov+'.txt')
else:
    results_othersfloating = open('impacts/'+year+'/'+asimov+'/fit_othersfloating_'+observable+'_'+year+sasimov+'_2sigma.txt')

#cmunu = 0.001
cmunu = 1e-3

wilson = []

bestfit_single = []
bestfit_multiple = []
bestfit_othersfloating = []
uncert_single = []
uncert_multiple = []
uncert_othersfloating = []
uncert_single_up = []
uncert_multiple_up = []
uncert_othersfloating_up = []
uncert_single_down = []
uncert_multiple_down = []
uncert_othersfloating_down = []
uncert_othersfloating_2sigma_up = []
uncert_othersfloating_2sigma_down = []


for line in results_single:
    i=0
    uncert = 0
    for word in line.split():
	#print(word)
	if (i==0): wilson.append(word)
	if (i==1): bestfit_single.append(float(word))
	if (i==2):
	    uncert_single_down.append(float(word)) 
	    uncert = -float(word)
	if (i==3): 
	    uncert_single_up.append(float(word))
	    uncert = uncert + float(word)
	    uncert_single.append(uncert/2.)
	i = i+1

for line in results_multiple:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
	if (i==1): bestfit_multiple.append(float(word))
        if (i==2):
	    uncert_multiple_down.append(float(word)) 
	    uncert = -float(word)
        if (i==3):
	    uncert_multiple_up.append(float(word))
            uncert = uncert + float(word)
            uncert_multiple.append(uncert/2.)
        i = i+1

for line in results_othersfloating:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
        if (i==1): bestfit_othersfloating.append(float(word))
        if (i==2):
            uncert_othersfloating_down.append(float(word))
            uncert = -float(word)
        if (i==3):
            uncert_othersfloating_up.append(float(word))
            uncert = uncert + float(word)
            uncert_othersfloating.append(uncert/2.)
	if (i==4):
            uncert_othersfloating_2sigma_down.append(float(word))
	if (i==5):
	    uncert_othersfloating_2sigma_up.append(float(word))
        i = i+1


def getwilsontext(wilson):
    if (wilson=="cLXX"): modwilson = "c_{L,XX}=#minusc_{L,YY}"
    if (wilson=="cLXY"): modwilson = "c_{L,XY}=c_{L,YX}"
    if (wilson=="cLXZ"): modwilson = "c_{L,XZ}=c_{L,ZX}"
    if (wilson=="cLYZ"): modwilson = "c_{L,YZ}=c_{L,ZY}"
    if (wilson=="cRXX"): modwilson = "c_{R,XX}=#minusc_{R,YY}"
    if (wilson=="cRXY"): modwilson = "c_{R,XY}=c_{R,YX}"
    if (wilson=="cRXZ"): modwilson = "c_{R,XZ}=c_{R,ZX}"
    if (wilson=="cRYZ"): modwilson = "c_{R,YZ}=c_{R,ZY}"
    if (wilson=="cXX"): modwilson = "c_{XX}=#minusc_{YY}"
    if (wilson=="cXY"): modwilson = "c_{XY}=c_{YX}"
    if (wilson=="cXZ"): modwilson = "c_{XZ}=c_{ZX}"
    if (wilson=="cYZ"): modwilson = "c_{YZ}=c_{ZY}"
    if (wilson=="dXX"): modwilson = "d_{XX}=#minusd_{YY}"
    if (wilson=="dXY"): modwilson = "d_{XY}=d_{YX}"
    if (wilson=="dXZ"): modwilson = "d_{XZ}=d_{ZX}"
    if (wilson=="dYZ"): modwilson = "d_{YZ}=d_{ZY}"
    return modwilson

#def addLineWilsonSingle(num):
#    line_wilson = TLine(uncert_single_down[num],16-num-0.3,uncert_single_up[num],16-num-0.3)
#    line_wilson.Draw()

#def addLineWilsonMultiple(num):
#    line_wilson = TLine(uncert_multiple_down[num],16-num-0.6,uncert_multiple_up[num],16-num-0.6)
#    line_wilson.Draw()

#if asimov=='asimov':
#    xmin = -0.024
#    xmax = 0.024
#else:
#xmin = -0.0305


xmin = -0.04
if doMultiple:
    xmin = -0.04
    xmax = 0.0305
elif doSingle==False and doOthersFloating==True and doMultiple==False:
    xmin = -0.02
    xmax = 0.02
    if do2sigma:
        xmin = -0.025
	xmax = 0.025
else:
    xmin = -0.035
    xmax = 0.02

canvas = TCanvas('Compare single/multiple SME fits', 'Compare single/multiple SME fits', 800, 600)
pad1 = TPad("pad", "pad", 0, 0, 1, 1)

tm = gStyle.GetPadTopMargin()
print 'TopMargin: '+str(tm)+' -> '+str(1.5*tm)
gStyle.SetPadTopMargin(1.5*tm)
pad1.SetTopMargin(1.5*tm)

canvas.cd()
pad1.Draw()
pad1.cd()

grid = TH2F('grid','grid',300,xmin,xmax,16,0,16)
for i in range(16):
   grid.GetYaxis().SetBinLabel(16-i,getwilsontext(wilson[i]))
grid.GetYaxis().SetLabelSize(0.06) #0.045
grid.SetXTitle("SME coefficient value")
grid.GetXaxis().SetTitleSize(0.045)#0.04
grid.GetXaxis().SetLabelSize(0.045)#0.04
gPad.SetGridx(1)

grid.GetXaxis().SetNdivisions(505)
grid.Draw()

line_block1 = TLine(xmin,12,xmax,12)
line_block2 = TLine(xmin,8,xmax,8)
line_block3 = TLine(xmin,4,xmax,4)
line_block1.Draw()
line_block2.Draw()
line_block3.Draw()

#Plot results
#line_wilson = TLine(uncert_single_down[0],15.5,uncert_single_up[0],15.5)
#line_wilson.Draw()
line_wilson_single = []
line_wilson_othersfloating = []
line_wilson_othersfloating_2sigma = []
line_wilson_multiple = []
wilson_height_single = []
wilson_height_othersfloating = []
wilson_height_multiple = []


if doSingle==True and ((doOthersFloating==False and doMultiple==True) or (doOthersFloating==True and doMultiple==False)):
    spacing = 0.3
if doSingle==True and doOthersFloating==True and doMultiple==True:
    spacing = 0.2
if doSingle==False and doOthersFloating==True and doMultiple==False:
    spacing = 0.5

print 'Preparing lines '

for num in range(16):
    #print str(num)
    if doSingle==True and ((doOthersFloating==False and doMultiple==True) or (doOthersFloating==True and doMultiple==False) or (doOthersFloating==True and doMultiple==True)):
        wilson_height_single.append(16-num-spacing)
        line_wilson_single.append(TLine(cmunu*(bestfit_single[num]+uncert_single_down[num]),16-num-spacing,cmunu*(bestfit_single[num]+uncert_single_up[num]),16-num-spacing))
        line_wilson_single[-1].SetLineWidth(2)
    if doSingle==True and doOthersFloating==False and doMultiple==True:
        wilson_height_multiple.append(16-num-2*spacing)
        line_wilson_multiple.append(TLine(cmunu*(bestfit_multiple[num]+uncert_multiple_down[num]),16-num-2*spacing,cmunu*(bestfit_multiple[num]+uncert_multiple_up[num]),16-num-2*spacing))
        line_wilson_multiple[-1].SetLineWidth(2)
        line_wilson_multiple[-1].SetLineColor(2)
    if doSingle==True and doOthersFloating==True and doMultiple==False:
        wilson_height_othersfloating.append(16-num-2*spacing)
        line_wilson_othersfloating.append(TLine(cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_down[num]),16-num-2*spacing,cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_up[num]),16-num-2*spacing))
        line_wilson_othersfloating[-1].SetLineWidth(2)
        line_wilson_othersfloating[-1].SetLineColor(8)
	print 'added'
    if doSingle==True and doOthersFloating==True and doMultiple==True:
        wilson_height_multiple.append(16-num-3*spacing)
        line_wilson_multiple.append(TLine(cmunu*(bestfit_multiple[num]+uncert_multiple_down[num]),16-num-3*spacing,cmunu*(bestfit_multiple[num]+uncert_multiple_up[num]),16-num-3*spacing))
        line_wilson_multiple[-1].SetLineWidth(2)
        line_wilson_multiple[-1].SetLineColor(2)
        wilson_height_othersfloating.append(16-num-2*spacing)
        line_wilson_othersfloating.append(TLine(cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_down[num]),16-num-2*spacing,cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_up[num]),16-num-2*spacing))
        line_wilson_othersfloating[-1].SetLineWidth(2)
        line_wilson_othersfloating[-1].SetLineColor(8)
    if doSingle==False and doOthersFloating==True and doMultiple==False: #for paper
	wilson_height_othersfloating.append(16-num-spacing)
        line_wilson_othersfloating.append(TLine(cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_down[num]),16-num-spacing,cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_up[num]),16-num-spacing))
	print '[' +str(round(1*(bestfit_othersfloating[num]+uncert_othersfloating_down[num]),2)) + '; '+ str(round(1*(bestfit_othersfloating[num]+uncert_othersfloating_up[num]),2))+']'
        line_wilson_othersfloating[-1].SetLineWidth(4)
        line_wilson_othersfloating[-1].SetLineColor(1)
	if do2sigma:
	    line_wilson_othersfloating_2sigma.append(TLine(cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_2sigma_down[num]),16-num-spacing,cmunu*(bestfit_othersfloating[num]+uncert_othersfloating_2sigma_up[num]),16-num-spacing))
	    line_wilson_othersfloating_2sigma[-1].SetLineWidth(2)
	    line_wilson_othersfloating_2sigma[-1].SetLineColor(1)

    if doSingle:
        line_wilson_single[-1].Draw()
        print 'single done'
    if doMultiple:
        line_wilson_multiple[-1].Draw()
	print 'multiple done'
    if doOthersFloating: 
	if do2sigma:
	    line_wilson_othersfloating_2sigma[-1].Draw()
        line_wilson_othersfloating[-1].Draw("same")
	#print 'othersfloating done'

#   addLineWilsonSingle(i)
 #   addLineWilsonMultiple(i)

print 'Filling numbers'

if doSingle:
    x_single = cmunu*np.array(bestfit_single, dtype='double')
    y_single = np.array(wilson_height_single, dtype='double')
if doMultiple:
    x_multiple = cmunu*np.array(bestfit_multiple, dtype='double')
    y_multiple = np.array(wilson_height_multiple, dtype='double')
if doOthersFloating:
    x_othersfloating = cmunu*np.array(bestfit_othersfloating, dtype='double')
    y_othersfloating = np.array(wilson_height_othersfloating, dtype='double')

print 'Making graphs'

marker_style = 20
if doMultiple and doOthersFloating:
    marker_size = 0.8
else:
    marker_size = 1.0
    if do2sigma:
	marker_size = 1.2

if doSingle:
    hist_bestfit_single = TGraph(16, x_single, y_single)
    hist_bestfit_single.SetMarkerStyle(marker_style)
    hist_bestfit_single.SetMarkerSize(marker_size)
    hist_bestfit_single.SetLineWidth(2)

if doMultiple:
    hist_bestfit_multiple = TGraph(16, x_multiple, y_multiple)
    hist_bestfit_multiple.SetMarkerStyle(marker_style)
    hist_bestfit_multiple.SetMarkerSize(marker_size)
    hist_bestfit_multiple.SetMarkerColor(2)
    hist_bestfit_multiple.SetLineColor(2)
    hist_bestfit_multiple.SetLineWidth(2)

if doOthersFloating:
    hist_bestfit_othersfloating = TGraph(16, x_othersfloating, y_othersfloating)
    hist_bestfit_othersfloating.SetMarkerStyle(marker_style)
    hist_bestfit_othersfloating.SetMarkerSize(marker_size)
    hist_bestfit_othersfloating.SetMarkerColor(8)
    if doSingle==True:
        hist_bestfit_othersfloating.SetMarkerColor(8)
        hist_bestfit_othersfloating.SetLineColor(8)
    else:
        hist_bestfit_othersfloating.SetMarkerColor(1)
        hist_bestfit_othersfloating.SetLineColor(1)
    hist_bestfit_othersfloating.SetLineWidth(2)
    if do2sigma:
	hist_bestfit_othersfloating.SetLineWidth(4)
	hist_2sigma_othersfloating = hist_bestfit_othersfloating.Clone()
	hist_2sigma_othersfloating.SetName('hist_2sigma_othersfloating')
	hist_2sigma_othersfloating.SetLineWidth(2)

print 'Drawing graphs'

if doSingle:
    hist_bestfit_single.Draw("Psame")
if doMultiple:
    hist_bestfit_multiple.Draw("Psame")
if doOthersFloating:
    hist_bestfit_othersfloating.Draw("Psame")

print 'Making legend'

#x_legend = 0.69
#y_legend = 0.76
x_legend = 0.17
y_legend = 0.73

if do2sigma==False:
    if doMultiple:
	legend = TLegend(x_legend,y_legend,x_legend+0.35,y_legend+0.18,'Fit '+asimov+' 68% CL')
    else:
	legend = TLegend(x_legend,y_legend+0.05,x_legend+0.35,y_legend+0.18,'68% CL')
    #legend = TLegend(x_legend,y_legend,x_legend+0.35,y_legend+0.18,'Fit '+asimov+' 68% CL')
    legend.SetBorderSize(0)
    if doOthersFloating==True and doMultiple==True:
	legend.SetTextSize(0.027)
    else:
	legend.SetTextSize(0.035)
    if doSingle:
	legend.AddEntry(hist_bestfit_single, "Single Wilson, others fixed to SM", "lp")
	#legend.AddEntry(line_wilson_single[0], "Single Wilson, others fixed to SM", "lp")
    if doOthersFloating==True:
	legend.AddEntry(hist_bestfit_othersfloating, "Single Wilson, three others floating", "lp")
	#legend.AddEntry(line_wilson_othersfloating[0], "Single Wilson, others floating", "lp")
    if doMultiple==True:
	legend.AddEntry(hist_bestfit_multiple, "4 Wilson simultaneously", "lp")
	#legend.AddEntry(line_wilson_multiple[0], "4 Wilson simultaneously", "lp")
    if doOthersFloating==False or doSingle==True or doMultiple==True:
	legend.Draw()
else:
    if doOthersFloating==True and doSingle==False and doMultiple==False:
	
	x_legend = 0.75
	y_legend = 0.8
	legend = TLegend(x_legend,y_legend,x_legend+0.18,y_legend+0.1,'')
	legend.SetBorderSize(0)
	legend.SetTextSize(0.035)
	legend.AddEntry(hist_bestfit_othersfloating, "68% CL", "lp")
	legend.AddEntry(hist_2sigma_othersfloating, "95% CL", "l")
	legend.Draw()



canvas.Update()

print 'Adding luminosity text'

if asimov=='asimov':
    sim=True
else:
    sim=False
if(year=='2016'):
    tdr.cmsPrel(36300., 13.,simOnly=sim, thisIsPrelim=True)
elif(year=='2017'):
   tdr.cmsPrel(41500., 13.,simOnly=sim, thisIsPrelim=True)
elif (year=='Comb'):
   tdr.cmsPrel(77800,13.,simOnly=sim, thisIsPrelim=False)

print 'Saving'

picName = 'impacts/'+year+'/'
#if asimov==True:
picName += asimov+'/'
picName += observable+'_WilsonPlot_'+year+'_'+asimov
if doOthersFloating==True and doMultiple==False:
    picName += '_forPaper'
picName += '.pdf'

canvas.SaveAs(picName)

raw_input()
exit()

text = ''
text += '\\begin{table}[h!]'
text += '\n' + '\\begin{center}'
text += '\n' +'\\begin{tabular}{|c|c|c|c|}'
text += '\n' +'\\hline '
text += '\n' +'Wilson coefficient & 2016 & 2017 & Combination\\\\'
text += '\n' +'\\hline '

for i in range(16):
    if (i==0 or i==4 or i==8 or i==12): text += '\n' +'\\hline '
    if (asimov=='asimov'):
        textline = '\n' +'$'+getwilsontext(wilson[i]) + '$ & $' + str(round(uncert_2016[i], 2)) + '\\times 10^{-3}$ & $' + str(round(uncert_2017[i], 2)) + '\\times 10^{-3}$ & $' + str(round(uncert_Comb[i], 2)) + '\\times 10^{-3}$  \\\\'
    else:
        textline = '\n' +'$'+getwilsontext(wilson[i]) + '$ & ' + str(round(bestfit_2016[i], 2)) + ' +' + str(round(uncert_2016_up[i], 2)) + ' ' + str(round(uncert_2016_down[i], 2)) + ' $\\times 10^{-3}$ & ' + str(round(bestfit_2017[i], 2)) + ' +' + str(round(uncert_2017_up[i], 2)) + ' ' + str(round(uncert_2017_down[i], 2))+ ' $\\times 10^{-3}$ & ' + str(round(bestfit_Comb[i], 2)) + ' +' + str(round(uncert_Comb_up[i], 2)) + ' ' + str(round(uncert_Comb_down[i], 2))+ ' $\\times 10^{-3}$  \\\\'
    text += '\n' +textline

text += '\n' +'\\hline '
text += '\n' +'\\end{tabular}'
if asimov=='asimov':
    text += '\n' +'\\caption{\\label{SMEresultsAllWilson}1-$\sigma$ precision (symmetrized) expected on the SME coefficients in 2016 and 2017 Asimov datasets (assuming SM pseudo-data).}'
else:
    text += '\n' +'\\caption{\\label{SMEresultsAllWilson}1-$\sigma$ precision (symmetrized) expected on the SME coefficients in 2016 and 2017 data.}'
text += '\n' +'\\end{center}'
text += '\n' +'\\end{table}'
text += '\n'


outname = './impacts/Comb/'+asimov+'/Table_Results_'+smultiple+observable+'_Comb'
if asimov == 'asimov':
    outname += '_'+asimov
print 'Write results in '+outname+'.txt'
fileout = open(outname+'.txt','w')
fileout.write(text)
fileout.close()



