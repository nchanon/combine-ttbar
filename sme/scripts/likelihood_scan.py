import os, sys
sys.path.append('./')

import math
import argparse
import subprocess

import numpy as np

from tools.style_manager import *

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString, TGraph
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

import tools.tdrstyle as tdr
tdr.setTDRStyle()


###################
## Initialisation
###################


parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
#parser.add_argument('nuisancegroup', help='nuisance group', default='')
parser.add_argument('wilson', help='display your wilson coefficient', default='sme_all')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='asimov')

args = parser.parse_args()
observable = args.observable
wilson = args.wilson
#asimov = args.asimov
year = args.year
#nuisancegroup = args.nuisancegroup


def wilsonserie(w):
    if w=='cLXX' or w=='cLXY' or w=='cLXZ' or w=='cLYZ': return 'cLXX_cLXY_cLXZ_cLYZ'
    if w=='cRXX' or w=='cRXY' or w=='cRXZ' or w=='cRYZ': return 'cRXX_cRXY_cRXZ_cRYZ'
    if w=='cXX' or w=='cXY' or w=='cXZ' or w=='cYZ': return 'cXX_cXY_cXZ_cYZ'
    if w=='dXX' or w=='dXY' or w=='dXZ' or w=='dYZ': return 'dXX_dXY_dXZ_dYZ'

def param_grid(w, asimov, fitkind):
    sasimov=''
    wrange=''
    if w[-2:]=='XX' or w[-2:]=='XY':
	if fitkind=='single':
	    wrange='5'
	if fitkind=='multiple':
	    wrange='5'
    if w[-2:]=='XZ' or w[-2:]=='YZ':
	if fitkind=='single':
	    wrange='40'
        if fitkind=='multiple':
            wrange='40'
    if fitkind=='multiple':
	sasimov = ' -P '+w+' '
	#sasimov = ' -P '+w+' --floatOtherPOIs=1 '
	#sasimov = ' --redefineSignalPOIs '+w+' '
    if asimov == 'asimov':
        sasimov += '--setParameters '+w+'=0 -t -1'
    elif asimov == 'injectiontest':
        sasimov += '--setParameters '+w+'=1 -t -1 '
    if asimov == 'data':
        sasimov += '--setParameters '+w+'=0'
    sasimov += '  --setParameterRanges '+w+'=-'+wrange+','+wrange
    if fitkind=='multiple':
        sasimov += ' --floatOtherPOIs=1 '#--cl=0.68 '
    return sasimov

def param_cross(wlist, asimov):
    wrange=''
    asi = ' --setParameters '
    for w in wlist:
        asi += w+'=0'
        if w!=wlist[-1]:
            asi += ','
    asi += ' --setParameterRanges '
    for w in wlist:
	if w[-2:]=='XX' or w[-2:]=='XY':
	    wrange='5'
	if w[-2:]=='XZ' or w[-2:]=='YZ':
	    wrange='40'
        asi += w+'=-'+wrange+','+wrange+''
        if w!=wlist[-1]:
            asi += ':'
    if asimov == 'asimov':
        asi += ' -t -1'
    return asi


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

doFit=True
#doFit=False

###################
## Core
###################

optim = ' --cminDefaultMinimizerStrategy 0 '
npoints=10


#for asi in ["data"]:
#for asi in ["asimov"]:
for asi in ["asimov","data"]:

    cmd1 = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+wilson+'_single_'+asi + optim
    cmd1 +=' -d ./inputs/'+observable+'_'+wilson+'_workspace_'+year+'.root '
    cmd1 += param_grid(wilson, asi, 'single') + ' --algo grid --points '+str(npoints)

    cmd2 = 'combine -M MultiDimFit -n .cross_snapshot_'+observable+'_'+year+'_'+wilsonserie(wilson)+'_multiple_'+asi + optim
    cmd2 +=' -d ./inputs/'+observable+'_'+wilsonserie(wilson)+'_workspace_'+year+'.root '
    cmd2 += param_cross(wilsonserie(wilson).split("_"), asi) + ' --algo cross --cl=0.68 '
    cmd2 += ' --saveWorkspace' 

    cmd2bis = 'combine -M MultiDimFit -n .nominal_'+observable+'_'+year+'_'+wilson+'_multiple_'+asi + optim
    cmd2bis += ' -d higgsCombine.cross_snapshot_'+observable+'_'+year+'_'+wilsonserie(wilson)+'_multiple_'+asi+'.MultiDimFit.mH120.root'
    cmd2bis += ' -P '+wilson #+ ' --floatOtherPOIs=1 '
    cmd2bis += param_cross(wilsonserie(wilson).split("_"), asi) 
    cmd2bis += ' --algo grid --points '+str(npoints)
    #cmd2bis += param_grid(wilson, asi, 'multiple') + ' --algo grid --points '+str(npoints)
    cmd2bis += ' --floatOtherPOIs=1 --skipInitialFit --saveInactivePOI 1'

    print cmd1
    print cmd2
    print cmd2bis
    if doFit==True:
	#os.system(cmd1)
        #os.system(cmd2)
        os.system(cmd2bis)

x_sample = []
y_sample = []
treelist = []
#x_array = []
#y_array = []
graph_list = [] 
for asi in ["asimov","data"]:
    for fitkind in ["single","multiple"]:

	filename = "higgsCombine.nominal_"+observable+"_"+year+"_"+wilson+"_"+fitkind+"_"+asi+".MultiDimFit.mH120.root"
	print filename
	filein = TFile(filename, "READ")
	treelist.append(filein.Get("limit"))
	treelist[-1].ls()

	x = []
	y = []
	list_double = []
	print asi+" "+fitkind
	for j in range(npoints):
	    treelist[-1].GetEvent(j)
	    print treelist[-1].GetLeaf(wilson).GetValue()
	    x.append(treelist[-1].GetLeaf(wilson).GetValue())
	    y.append(treelist[-1].GetLeaf("deltaNLL").GetValue())
	    list_double.append([x[-1], y[-1]])
	print asi+" "+fitkind+": x="+str(x)
	print asi+" "+fitkind+": y="+str(y)

	list_double.sort(key=lambda row: row[0])
	print  list_double

	x_sorted = [row[0] for row in list_double]
	y_sorted = [row[1] for row in list_double]

	x_array = np.array(x_sorted, dtype='double')
	y_array = np.array(y_sorted, dtype='double')

	graph_list.append(TGraph(npoints, x_array, y_array))
        graph_list[-1].SetLineWidth(2)
	graph_list[-1].SetName(asi+"_"+fitkind)

	if asi=='asimov':
	    graph_list[-1].SetLineStyle(9)
	if fitkind=='single':
	    graph_list[-1].SetMarkerColor(1)
	    graph_list[-1].SetLineColor(1)
        if fitkind=='multiple':
            graph_list[-1].SetMarkerColor(2)
            graph_list[-1].SetLineColor(2)


#print x_sample
#print y_sample


canvas = TCanvas("Likelihood scan", "Likelihood scan", 800, 800)
grid = TH2F("grid","grid",100,-5,5,100,0,10)

grid.Draw()
graph_list[0].Draw("Csame")
graph_list[1].Draw("Csame")
graph_list[2].Draw("Csame")
graph_list[3].Draw("Csame")

raw_input()
exit()

