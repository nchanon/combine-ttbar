import os, sys
import argparse 

from ROOT import TFile, TH1, TH2, TCanvas, TH1F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

###################
## Initialisation
###################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')
parser.add_argument('timebin', help='display the time bin')

args = parser.parse_args()
observable = args.observable
year = args.year
asimov = args.asimov
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

doPrePostFitOnly = False

###################
## Core
###################



print '-------------------------'
print ' >>> combine on datacard '
print '-------------------------'
    
if (doPrePostFitOnly==False):
    cmd1 = 'combineTool.py -M Impacts -n .Impact_'+observable+'_'+year+stimebin+sasimov+' -d inputs/'+observable+'_inclusive'+stimebin+'_workspace_'+year+'.root '+asi+' -m 125 '
    cmd2 = cmd1
    cmd3 = cmd1
    cmd1 += '--doInitialFit --robustFit 1 ' #--cminDefaultMinimizerStrategy 0 ' #--robustFit 1
    cmd2 += '--robustFit 1 --doFits'  #--cminDefaultMinimizerStrategy 0
    cmd3 += '-o '+observable+'_inclusive_impacts_'+year+stimebin+sasimov+'.json '

    cmd4 = 'plotImpacts.py -i '+observable+'_inclusive_impacts_'+year+stimebin+sasimov+'.json -o '+observable+'_inclusive_impacts_'+year+stimebin+sasimov

    print cmd1        
    os.system(cmd1)
    print cmd2
    os.system(cmd2)
    print cmd3
    os.system(cmd3)
    print cmd4
    os.system(cmd4)

    if asimov == 'asimov':
        os.system('mv '+observable+'_inclusive_impacts_'+year+'*.pdf impacts/'+year+'/asimov/')
        #os.system('mv *Impact_'+year+'*.root impacts/'+year+'/asimov/')
    else:
        os.system('mv '+observable+'_inclusive_impacts_'+year+'*.pdf impacts/'+year+'/')
        #os.system('mv *Impact_'+year+'*.root  impacts/'+year+'/')


#cmd5 = 'combineTool.py -M FitDiagnostics inputs/'+observable+'_inclusive_workspace_'+year+'.root '+' -m 125 --rMin 0 --rMax 10 --cminDefaultMinimizerStrategy 0 --saveShapes --saveWithUncertainties '
#cmd5 += ' --skipBOnlyFit --plots'
#cmd += ' -o fitDiagnostics.Test.'+observable+'_inclusive_impacts_'+year+sasimov+'.root '

#cmd6 = 'python diffNuisances.py fitDiagnostics.Test.root --skipFitB --all -g '+nuisances+'.root'

#os.system(cmd5)
#os.system(cmd6)


    
    
