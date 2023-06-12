import os, sys
import argparse
import subprocess

from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov

doFit=True
#doFit=False


def asimov_param(wlist):
    asi = ' --setParameters '
    for w in wlist:
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
    if asimov == 'asimov':
	asi += ' -t -1'
    return asi

wilson_list_all = [
    'cLXX_cLXY_cLXZ_cLYZ',
    'cRXX_cRXY_cRXZ_cRYZ',
    'cXX_cXY_cXZ_cYZ',
    'dXX_dXY_dXZ_dYZ'
]

wilson_list = wilson_list_all    

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
    #canvas.Print("impacts/"+title+"_NormDifferentialFit_"+observable+"_"+year+"_"+asimov+".pdf")

    outname = './impacts/'+year+'/'+asimov+'/'+title+'_fit_multiple_'+observable+'_'+year
    if asimov == 'asimov':
        outname += '_'+asimov
    else:
        outname += '_data'
    canvas.SaveAs(outname+'.pdf')


if asimov == 'asimov':
    print ''
    print '### Asimov test ###'
    print ''

workspace_input = []
for wlist in wilson_list:
    wilson_string = ""
    wlist_splitted = wlist.split("_")
    for w in wlist_splitted:
        wilson_string += w
        if w!=wlist_splitted[-1]:
            wilson_string += '_'
    workspace_input.append('./inputs/'+observable+'_'+wilson_string+'_workspace_'+year+'.root')

#for i in range(1):
for i in range(len(wilson_list)):
    cmd = 'combine -M MultiDimFit --algo=cross --cl=0.68 --cminDefaultMinimizerStrategy 0 '
    cmd += workspace_input[i]
    cmd += asimov_param(wilson_list[i].split("_"))
    cmd += ' --saveFitResult '
    cmd += ' -n .cross_'+observable+'_'+year+'_'+wilson_list[i]+'_'+asimov
    print cmd
    if doFit==True:
        os.system(cmd)


coeff_serie_central = []
coeff_serie_up = []
coeff_serie_down = []

hCorrPOI = [] #= TH2F("hCorrPOI","hCorrPOI",16,0,16,16,0,16)

#for i in range(1):
for i in range(len(wilson_list)):

    coeff_central = []
    coeff_up = []
    coeff_down = []

    wlist = wilson_list[i].split("_")
    fResult = TFile('higgsCombine.cross_'+observable+'_'+year+'_'+wilson_list[i]+'_'+asimov+'.MultiDimFit.mH120.root')
    tResult = fResult.Get('limit')

    #tResult.GetEvent(0)
    #for w in wlist:
	#print 'Best fit: '+w+'='+str(tResult.GetLeaf(w).GetValue())
        #coeff_central.append(tResult.GetLeaf(w).GetValue())

    for iw in range(len(wlist)):
	tResult.GetEvent(0)
	coeff_central.append(tResult.GetLeaf(wlist[iw]).GetValue())
	tResult.GetEvent(1+iw*2)
	#print wlist[iw]+' down='+str(tResult.GetLeaf(wlist[iw]).GetValue())
	coeff_down.append(tResult.GetLeaf(wlist[iw]).GetValue()-coeff_central[-1]) 
	#for j in range(len(wlist)):
	#    print str(tResult.GetLeaf(wlist[j]).GetValue()) 
        tResult.GetEvent(1+iw*2+1)
        #for j in range(len(wlist)):
        #    print str(tResult.GetLeaf(wlist[j]).GetValue())
        #print wlist[iw]+' up='+str(tResult.GetLeaf(wlist[iw]).GetValue())
	coeff_up.append(tResult.GetLeaf(wlist[iw]).GetValue()-coeff_central[-1])

    #fFit = TFile('multidimfit.cross_'+observable+'_'+year+'_'+wilson_list[i]+'_'+asimov+'.root')
    #if fFit != 0:
    #    fitResult = fFit.Get("fit_mdf")
    #    hCorrPOI.append(TH2F("hCorrPOI","hCorrPOI",4,0,4,4,0,4))
    #    for j in range(len(wlist)):
	#    for k in range(len(wlist)):
	#        corrval = fitResult.correlation(wlist[j], wlist[k])
	#        hCorrPOI[i].SetBinContent(1+j, 1+k, corrval)
	#        plot2Dmatrix(hCorrPOI[i], "CorrelationMatrix_"+wilson_list[i])
    #else:
	#print 'No multidimfit file' 

    coeff_serie_central.append(coeff_central)
    coeff_serie_up.append(coeff_up)
    coeff_serie_down.append(coeff_down)

#for i in range(len(wilson_list)):
#    plot2Dmatrix(hCorr[i], "CorrelationMatrix_"+wilson_list[i])


text = ''
for i in range(len(wilson_list)):
    wlist = wilson_list[i].split("_")
    for iw in range(len(wlist)):
	print wlist[iw]+'='+str(coeff_serie_central[i][iw])+' +'+str(coeff_serie_up[i][iw])+' '+str(coeff_serie_down[i][iw])
	text += wlist[iw]+' '+str(round(coeff_serie_central[i][iw],3))+' '+str(round(coeff_serie_down[i][iw],3))+' '+str(round(coeff_serie_up[i][iw],3))+'\n'

outname = './impacts/'+year+'/'+asimov+'/fit_multiple_'+observable+'_'+year
if asimov == 'asimov':
    outname += '_'+asimov
else:
    outname += '_data'

print 'Write results in '+outname+'.txt'
fileout = open(outname+'.txt','w')
fileout.write(text)
fileout.close()

exit()






## Methodes

def getValues(line):
    r = line[0]
    x = float(line[2])
    uncertainty = line[3].split('/')
    down = float(uncertainty[0])
    up   = float(uncertainty[1])
    return [r,x,down,up]


## Fit

fit_values = []

for i in range(len(cmd_input)):

    print '-------------------'
    print ' >>> Fit '+wilson_list[i]
    print '-------------------'

    cmd = ['combine', 
           '-M', 
           'MultiDimFit',
           '--algo=singles',
	   ' --cminDefaultMinimizerStrategy',
	   '0', 
           #'--robustFit',
           #'1',
           cmd_input[i]]
    for a in asimov_param(wilson_list[i]):
        cmd.append(a)
    #if (asimov=="" and (wilson_list[i].find("XZ")!=-1 or wilson_list[i].find("YZ")!=-1)):
    cmd.append('--setParameterRanges')
    cmd.append(wilson_list[i]+'=-30,30')

    print cmd

    output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    output = output.splitlines()
    output.sort()
    for line in output:
        if line.find(wilson_list[i]+' :') != -1:
            print line 
            fit_values.append(getValues(line.split()))

## Core
	
text = ''
for l in fit_values:
    for i in l:
        text += str(i) + ' '
    text += '\n'

outname = './impacts/'+year+'/'+asimov+'/fit_'+observable+'_'+year
if asimov == 'asimov':
    outname += '_asimov'
else:
    outname += '_data'

file = open(outname+'.txt','w') 
file.write(text) 
file.close()

