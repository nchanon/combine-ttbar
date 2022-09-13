import os, sys
sys.path.append('./')

import argparse 
import numpy as np

from tools.style_manager import *

from ROOT import TFile, TH1, TCanvas, TH1F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TGraphAsymmErrors

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

doFit=True
#doFit=False

###################
## Core
###################

if doFit:
    cmd = 'combine -M MultiDimFit '
    cmd += asi
    cmd += ' -d inputs/combine_'+observable+'_24bins_'+year+'_workspace.root'
    #ucmd += ' --robustFit 1'
    #cmd += ' --cminDefaultMinimizerStrategy 0'
    cmd += ' --algo=cross'
    #cmd += ' --algo=singles'
    cmd += ' -n differential_'+observable+'_'+year+'_'+asimov
    cmd += ' > log_differential_'+observable+'_'+year+'_'+asimov

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

i=0
file = open('log_differential_'+observable+'_'+year+'_'+asimov)
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

resultname = './impacts/'+year+'/'+observable+'_differential_'+year+'_'+sasimov

#rootfile_output = TFile(resultname+'.root', "RECREATE")
#canvas.Write()
#canvas.SaveAs(resultname+'.png')
canvas.SaveAs(resultname+'.pdf')
#rootfile_output.Close()

raw_input('exit')


