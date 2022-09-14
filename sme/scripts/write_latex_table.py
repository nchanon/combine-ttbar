import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('asimov',nargs='?', help='set if asimov test')
parser.add_argument('multiple',help='set if multiple fit', default='single')

args = parser.parse_args()
observable = args.observable
asimov = args.asimov
multiple = args.multiple

if asimov=='asimov':
    sasimov='_asimov'
else:
    sasimov='_data'

if multiple=='multiple':
    smultiple = 'multiple_'
else:
    smultiple = ''


results_2016 = open('impacts/2016/'+asimov+'/fit_'+smultiple+observable+'_2016'+sasimov+'.txt')
results_2017 = open('impacts/2017/'+asimov+'/fit_'+smultiple+observable+'_2017'+sasimov+'.txt')
results_Comb = open('impacts/Comb/'+asimov+'/fit_'+smultiple+observable+'_Comb'+sasimov+'.txt')

cmunu = 0.001

wilson = []
bestfit_2016 = []
bestfit_2017 = []
bestfit_Comb = []
uncert_2016 = []
uncert_2017 = []
uncert_Comb = []
uncert_2016_up = []
uncert_2017_up = []
uncert_Comb_up = []
uncert_2016_down = []
uncert_2017_down = []
uncert_Comb_down = []


for line in results_2016:
    i=0
    uncert = 0
    for word in line.split():
	#print(word)
	if (i==0): wilson.append(word)
	if (i==1): bestfit_2016.append(float(word))
	if (i==2):
	    uncert_2016_down.append(float(word)) 
	    uncert = -float(word)
	if (i==3): 
	    uncert_2016_up.append(float(word))
	    uncert = uncert + float(word)
	    uncert_2016.append(uncert/2.)
	i = i+1

for line in results_2017:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
	if (i==1): bestfit_2017.append(float(word))
        if (i==2):
	    uncert_2017_down.append(float(word)) 
	    uncert = -float(word)
        if (i==3):
	    uncert_2017_up.append(float(word))
            uncert = uncert + float(word)
            uncert_2017.append(uncert/2.)
        i = i+1

for line in results_Comb:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
	if (i==1): bestfit_Comb.append(float(word))
        if (i==2):
	    uncert_Comb_down.append(float(word)) 
	    uncert = -float(word)
        if (i==3):
	    uncert_Comb_up.append(float(word))
            uncert = uncert + float(word)
            uncert_Comb.append(uncert/2.)
        i = i+1

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


outname = './impacts/'+year+'/'+asimov+'/Table_Results_'+smultiple+observable+'_'+year
if asimov == 'asimov':
    outname += '_'+asimov
print 'Write results in '+outname+'.txt'
fileout = open(outname+'.txt','w')
fileout.write(text)
fileout.close()



