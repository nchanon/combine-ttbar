import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
asimov = args.asimov

results_2016 = open('impacts/2016/'+asimov+'/fit_'+observable+'_2016_'+asimov+'.txt')
results_2017 = open('impacts/2017/'+asimov+'/fit_'+observable+'_2017_'+asimov+'.txt')
results_Comb = open('impacts/Comb/'+asimov+'/fit_'+observable+'_Comb_'+asimov+'.txt')

cmunu = 0.001

wilson = []
uncert_2016 = []
uncert_2017 = []
uncert_Comb = []


for line in results_2016:
    i=0
    uncert = 0
    for word in line.split():
	#print(word)
	if (i==0): wilson.append(word)
	if (i==2): uncert = -float(word)
	if (i==3): 
	    uncert = uncert + float(word)
	    uncert_2016.append(uncert/2.)
	i = i+1

for line in results_2017:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
        if (i==2): uncert = -float(word)
        if (i==3):
            uncert = uncert + float(word)
            uncert_2017.append(uncert/2.)
        i = i+1

for line in results_Comb:
    i=0
    uncert = 0
    for word in line.split():
        #print(word)
        if (i==2): uncert = -float(word)
        if (i==3):
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

print '\\begin{table}[h!]'
print '\\begin{center}'
print '\\begin{tabular}{|c|c|c|c|}'
print '\\hline '
print 'Wilson coefficient & 2016 & 2017 & Combination\\\\'
print '\\hline '

for i in range(16):
    if (i==0 or i==4 or i==8 or i==12): print '\\hline '
    text = '$'+getwilsontext(wilson[i]) + '$ & $' + str(round(uncert_2016[i], 2)) + '\\times 10^{-3}$ & $' + str(round(uncert_2017[i], 2)) + '\\times 10^{-3}$ & $' + str(round(uncert_Comb[i], 2)) + '\\times 10^{-3}$  \\\\'
    print text

print '\\hline '
print '\\end{tabular}'
print '\\caption{\\label{SMEresultsAllWilson}1-$\sigma$ precision (symmetrized) expected on the SME coefficients in 2016 and 2017 Asimov datasets (assuming SM pseudo-data).}'
print '\\end{center}'
print '\\end{table}'


