import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
#parser.add_argument('wilson', help='display your wilson coefficient')
#parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
#wilson = args.wilson
#asimov = args.asimov

wilson_list_all = [
    'cLXX',
    'cLXY',
    'cLXZ',
    'cLYZ',
    'cRXX',
    'cRXY',
    'cRXZ',
    'cRYZ',
    'cXX',
    'cXY',
    'cXZ',
    'cYZ',
    'dXX',
    'dXY',
    'dXZ',
    'dYZ'
]

wilson_list_multiple = [
    'cLXX,cLXY,cLXZ,cLYZ',
    'cRXX,cRXY,cRXZ,cRYZ',
    'cXX,cXY,cXZ,cYZ',
    'dXX,dXY,dXZ,dYZ'
]

#Single fits
for wilson in wilson_list_all:
    os.system('cp inputs/2016/'+observable+'_'+wilson+'_datacard.txt ./'+observable+'_'+wilson+'_datacard_2016.txt')
    os.system('cp inputs/2017/'+observable+'_'+wilson+'_datacard.txt ./'+observable+'_'+wilson+'_datacard_2017.txt')

    cmd = 'combineCards.py '+observable+'_'+wilson+'_datacard_2016.txt '+observable+'_'+wilson+'_datacard_2017.txt > inputs/Comb/'+observable+'_'+wilson+'_datacard.txt'
    print cmd
    os.system(cmd)

    os.system('rm '+observable+'_'+wilson+'_datacard_2016.txt')
    os.system('rm '+observable+'_'+wilson+'_datacard_2017.txt')

    os.system('python scripts/workspace_creator.py '+observable+' Comb '+wilson)

#Multiple fits
os.system('cp inputs/2016/'+observable+'_sme_all_datacard.txt ./'+observable+'_sme_all_datacard_2016.txt')
os.system('cp inputs/2017/'+observable+'_sme_all_datacard.txt ./'+observable+'_sme_all_datacard_2017.txt')

cmd = 'combineCards.py '+observable+'_sme_all_datacard_2016.txt '+observable+'_sme_all_datacard_2017.txt > inputs/Comb/'+observable+'_sme_all_datacard.txt'
print cmd
os.system(cmd)

os.system('rm '+observable+'_sme_all_datacard_2016.txt')
os.system('rm '+observable+'_sme_all_datacard_2017.txt')

for wilson in wilson_list_multiple:
    os.system('python scripts/workspace_creator.py '+observable+' Comb '+wilson)    


