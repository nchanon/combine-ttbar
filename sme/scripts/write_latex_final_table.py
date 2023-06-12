import os, sys
sys.path.append('./')

import argparse
import subprocess
import numpy as np

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame, TColor, TLine, TGraph
from ROOT import gPad, gStyle, TGraphAsymmErrors

import tools.tdrstyle as tdr
tdr.setTDRStyle()

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
#parser.add_argument('asimov',nargs='?', help='set if asimov test')
#parser.add_argument('multiple',help='set if multiple fit', default='single')

args = parser.parse_args()
observable = args.observable
#asimov = args.asimov
year = args.year
#multiple = args.multiple

#if asimov=='asimov':
#    sasimov='_asimov'
#else:
#    sasimov='_data'

#results_single_asimov = open('impacts/'+year+'/asimov/fit_'+observable+'_'+year+'_asimov.txt')
#results_multiple_asimov = open('impacts/'+year+'/asimov/fit_multiple_'+observable+'_'+year+'_asimov.txt')
#results_single_data = open('impacts/'+year+'/data/fit_'+observable+'_'+year+'_data.txt')
#results_multiple_data = open('impacts/'+year+'/data/fit_multiple_'+observable+'_'+year+'_data.txt')


#cmunu = 0.001
cmunu = 1e-3

wilson = []

bestfit_single = []
bestfit_multiple = []
uncert_single = []
uncert_multiple = []
uncert_single_up = []
uncert_multiple_up = []
uncert_single_down = []
uncert_multiple_down = []


def read_results(asi, fitkind):
    filename = 'impacts/'+year+'/'+asi+'/fit_'
    if fitkind=="multiple":
	filename += 'multiple_'
    elif fitkind=="othersfloating":
	filename += 'othersfloating_'
    filename += observable+'_'+year+'_'+asi+'.txt'
    results = open(filename)
    wilson = []
    bestfit = []
    uncert_up = []
    uncert_down = []
    uncert_avg = []
    for line in results:
	i=0
	uncert = 0
	for word in line.split():
	    #print(word)
	    if (i==0): wilson.append(word)
	    if (i==1): bestfit.append(float(word))
	    if (i==2):
		uncert_down.append(float(word))
		uncert = -float(word)
	    if (i==3):
		uncert_up.append(float(word))
		uncert = uncert + float(word)
		uncert_avg.append(uncert/2.)
	    i = i+1
    return wilson, bestfit, uncert_up, uncert_down, uncert_avg

'''
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
'''

def getwilsontext(wilson):
    if (wilson=="cLXX"): modwilson = "c_{L,XX}=-c_{L,YY}"
    if (wilson=="cLXY"): modwilson = "c_{L,XY}=c_{L,YX}"
    if (wilson=="cLXZ"): modwilson = "c_{L,XZ}=c_{L,ZX}"
    if (wilson=="cLYZ"): modwilson = "c_{L,YZ}=c_{L,ZY}"
    if (wilson=="cRXX"): modwilson = "c_{R,XX}=-c_{R,YY}"
    if (wilson=="cRXY"): modwilson = "c_{R,XY}=c_{R,YX}"
    if (wilson=="cRXZ"): modwilson = "c_{R,XZ}=c_{R,ZX}"
    if (wilson=="cRYZ"): modwilson = "c_{R,YZ}=c_{R,ZY}"
    if (wilson=="cXX"): modwilson = "c_{XX}=-c_{YY}"
    if (wilson=="cXY"): modwilson = "c_{XY}=c_{YX}"
    if (wilson=="cXZ"): modwilson = "c_{XZ}=c_{ZX}"
    if (wilson=="cYZ"): modwilson = "c_{YZ}=c_{ZY}"
    if (wilson=="dXX"): modwilson = "d_{XX}=-d_{YY}"
    if (wilson=="dXY"): modwilson = "d_{XY}=d_{YX}"
    if (wilson=="dXZ"): modwilson = "d_{XZ}=d_{ZX}"
    if (wilson=="dYZ"): modwilson = "d_{YZ}=d_{ZY}"
    return modwilson

def getwilsontextForPaper(wilson):
    if (wilson=="cLXX"): modwilson = "$c_{L,XX}$ & $-c_{L,YY}$"
    if (wilson=="cLXY"): modwilson = "$c_{L,XY}$ & $c_{L,YX}$"
    if (wilson=="cLXZ"): modwilson = "$c_{L,XZ}$ & $c_{L,ZX}$"
    if (wilson=="cLYZ"): modwilson = "$c_{L,YZ}$ & $c_{L,ZY}$"
    if (wilson=="cRXX"): modwilson = "$c_{R,XX}$ & $-c_{R,YY}$"
    if (wilson=="cRXY"): modwilson = "$c_{R,XY}$ & $c_{R,YX}$"
    if (wilson=="cRXZ"): modwilson = "$c_{R,XZ}$ & $c_{R,ZX}$"
    if (wilson=="cRYZ"): modwilson = "$c_{R,YZ}$ & $c_{R,ZY}$"
    if (wilson=="cXX"): modwilson = "$c_{XX}$ & $-c_{YY}$"
    if (wilson=="cXY"): modwilson = "$c_{XY}$ & $c_{YX}$"
    if (wilson=="cXZ"): modwilson = "$c_{XZ}$ & $c_{ZX}$"
    if (wilson=="cYZ"): modwilson = "$c_{YZ}$ & $c_{ZY}$"
    if (wilson=="dXX"): modwilson = "$d_{XX}$ & $-d_{YY}$"
    if (wilson=="dXY"): modwilson = "$d_{XY}$ & $d_{YX}$"
    if (wilson=="dXZ"): modwilson = "$d_{XZ}$ & $d_{ZX}$"
    if (wilson=="dYZ"): modwilson = "$d_{YZ}$ & $d_{ZY}$"
    return modwilson


doOthersFloating = True
doMultiple = False

results = []
results.append(read_results("asimov", "single"))
results.append(read_results("asimov", "othersfloating"))
#results.append(read_results("asimov", "multiple"))
results.append(read_results("data", "single"))
results.append(read_results("data", "othersfloating"))
#results.append(read_results("data", "multiple"))

wilson = results[0][0]
print wilson

#doForPaper=True
doForPaper=False

if doForPaper==False:
    text = ''
    text += '\\begin{table}[h!]'
    text += '\n' + '\\begin{center}'
    text += '\n' +'\\begin{tabular}{|c|c|c|c|c|}'
    text += '\n' +'\\hline '
    text += '\n' +' & SM expected & Data & SM expected & Data\\\\'
    text += '\n' +'Wilson coefficient & Single coeff. fit  & Single coeff. fit &  4 coeff. fit & 4 coeff. fit\\\\'
    text += '\n' +' & ($10^{-3}$ unit) & ($10^{-3}$ unit) & ($10^{-3}$ unit) & ($10^{-3}$ unit)\\\\'
    text += '\n' +'\\hline '

    for i in range(len(wilson)):
	text += '\n' +'$'+getwilsontext(wilson[i]) 
	text += '$ & $[' + str(round(results[0][1][i]+results[0][3][i], 2)) + ' ; '+ str(round(results[0][1][i]+results[0][2][i], 2)) + ']'
	text += '$ & $[' + str(round(results[2][1][i]+results[2][3][i], 2)) + ' ; '+ str(round(results[2][1][i]+results[2][2][i], 2)) + ']'
	text += '$ & $[' + str(round(results[1][1][i]+results[1][3][i], 2)) + ' ; '+ str(round(results[1][1][i]+results[1][2][i], 2)) + ']'
	text += '$ & $[' + str(round(results[3][1][i]+results[3][3][i], 2)) + ' ; '+ str(round(results[3][1][i]+results[3][2][i], 2)) + ']$ \\\\'
	if (i+1) % 4 == 0:
	    text += '\n \\hline' 

    text += '\n' +'\\end{tabular}'
    text += '\n' +'\\caption{\\label{SMEresultsAsimDataSingleMultiple}Expected and observed 1$\sigma$ interval measured for the SME fits of single coefficients separately'
    if doOthersFloating:
	text += ' and while coefficients for the three other directions are floating,' 
    if doMultiple:
        text += ' and four coefficients simultaneously.' # All values are to be multiplied by $ 10^{-3}$.}'
    text += '\n' +'\\end{center}'
    text += '\n' +'\\end{table}'
    text += '\n'

if doForPaper==True:   
    text = ''
    text += '\\begin{table}[hp!]'
    text += '\n' + '\\centering'
    text += '\n' + '\\topcaption{\\label{SMEresultsAsimDataSingleMultiple}Expected and observed 1$\sigma$ interval measured for the SME fits of single coefficients while the others are fixed to their SM value, and while coefficients for the three other directions are floating.}'
    text += '\n' + '\\begin{tabular}{r@{${}={}$}l>{[}r@{; }l<{]}>{[}r@{; }l<{]}>{[}r@{; }l<{]}>{[}r@{; }l<{]}}'
    text += '\n' + '\\multicolumn{2}{c}{} & \\multicolumn{2}{c}{SM expected} & \\multicolumn{2}{c}{Data} & \\multicolumn{2}{c}{SM expected} & \\multicolumn{2}{c}{Data} \\\\' 
    text += '\n' + '\\multicolumn{2}{c}{Wilson coefficient} & \\multicolumn{2}{c}{Others fixed to SM}  & \\multicolumn{2}{c}{Others fixed to SM} & \\multicolumn{2}{c}{Others floating} & \\multicolumn{2}{c}{Others floating} \\\\'
    text += '\n' + '\\multicolumn{2}{c}{} & \\multicolumn{2}{c}{($10^{-3}$ units)} & \\multicolumn{2}{c}{($10^{-3}$ units)} & \\multicolumn{2}{c}{($10^{-3}$ units)} & \\multicolumn{2}{c}{($10^{-3}$ units)} \\\\'
    text += '\n' +'\\hline '

    for i in range(len(wilson)):
        text += '\n' + getwilsontextForPaper(wilson[i])
        text += ' & $' + str(round(results[0][1][i]+results[0][3][i], 2)) + '$ & $'+ str(round(results[0][1][i]+results[0][2][i], 2)) + '$' 
        text += ' & $' + str(round(results[2][1][i]+results[2][3][i], 2)) + '$ & $'+ str(round(results[2][1][i]+results[2][2][i], 2)) + '$'
        text += ' & $' + str(round(results[1][1][i]+results[1][3][i], 2)) + '$ & $'+ str(round(results[1][1][i]+results[1][2][i], 2)) + '$' 
        text += ' & $' + str(round(results[3][1][i]+results[3][3][i], 2)) + '$ & $'+ str(round(results[3][1][i]+results[3][2][i], 2)) + '$ \\\\'
        if (i+1) % 4 == 0 and i!=15:
            text += '[\\cmsTabSkip]'

    text += '\n' +'\\end{tabular}'
    text += '\n' +'\\end{table}'


print text

outname = './impacts/Comb/Table_Results_Final'
if doForPaper:
    outname += '_ForPaper'
print 'Wrote '+outname+'.txt'
fileout = open(outname+'.txt','w')
fileout.write(text)
fileout.close()

exit()

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
xmin = -0.0305
xmax = 0.0305

canvas = TCanvas('Compare single/multiple SME fits', 'Compare single/multiple SME fits', 800, 600)
#pad = TPad("pad", "pad", 0, 0, 1, 1)

grid = TH2F('grid','grid',300,xmin,xmax,16,0,16)
for i in range(16):
   grid.GetYaxis().SetBinLabel(16-i,getwilsontext(wilson[i]))
grid.SetXTitle("Wilson coefficient value")
grid.GetXaxis().SetTitleSize(0.04)
grid.GetXaxis().SetLabelSize(0.04)
gPad.SetGridx(1)

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
line_wilson_multiple = []
wilson_height_single = []
wilson_height_multiple = []
for num in range(16):
    wilson_height_single.append(16-num-0.3)
    line_wilson_single.append(TLine(cmunu*(bestfit_single[num]+uncert_single_down[num]),16-num-0.3,cmunu*(bestfit_single[num]+uncert_single_up[num]),16-num-0.3))
    line_wilson_single[-1].SetLineWidth(2)
    wilson_height_multiple.append(16-num-0.6)
    line_wilson_multiple.append(TLine(cmunu*(bestfit_multiple[num]+uncert_multiple_down[num]),16-num-0.6,cmunu*(bestfit_multiple[num]+uncert_multiple_up[num]),16-num-0.6))
    line_wilson_multiple[-1].SetLineWidth(2)
    line_wilson_multiple[-1].SetLineColor(2)
    line_wilson_single[-1].Draw()
    line_wilson_multiple[-1].Draw() 
#   addLineWilsonSingle(i)
 #   addLineWilsonMultiple(i)

x_single = cmunu*np.array(bestfit_single, dtype='double')
y_single = np.array(wilson_height_single, dtype='double')
x_multiple = cmunu*np.array(bestfit_multiple, dtype='double')
y_multiple = np.array(wilson_height_multiple, dtype='double')

hist_bestfit_single = TGraph(16, x_single, y_single)
hist_bestfit_multiple = TGraph(16, x_multiple, y_multiple)
hist_bestfit_single.SetMarkerStyle(20)
hist_bestfit_single.SetMarkerSize(0.8)
hist_bestfit_multiple.SetMarkerStyle(20)
hist_bestfit_multiple.SetMarkerSize(0.8)
hist_bestfit_multiple.SetMarkerColor(2)

hist_bestfit_single.Draw("Psame")
hist_bestfit_multiple.Draw("Psame")

#x_legend = 0.69
#y_legend = 0.76
x_legend = 0.17
y_legend = 0.76
legend = TLegend(x_legend,y_legend,x_legend+0.26,y_legend+0.18,asimov+' 68% CL')
#legend.SetTextSize(0.03)
legend.AddEntry(line_wilson_single[0], "Single Wilson fit", "l")
legend.AddEntry(line_wilson_multiple[0], "4 Wilson fit", "l")
legend.Draw()

canvas.Update()

if asimov=='asimov':
    sim=True
else:
    sim=False
if(year=='2016'):
    tdr.cmsPrel(35900., 13.,simOnly=sim, thisIsPrelim=True)
elif(year=='2017'):
   tdr.cmsPrel(41500., 13.,simOnly=sim, thisIsPrelim=True)
elif (year=='Comb'):
   tdr.cmsPrel(77400,13.,simOnly=sim, thisIsPrelim=True)

picName = 'impacts/'+year+'/'
#if asimov==True:
picName += asimov+'/'
picName += observable+'_WilsonPlot_'+year+'_'+asimov+'.pdf'

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



