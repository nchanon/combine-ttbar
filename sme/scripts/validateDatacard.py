import os, sys
sys.path.append('./')

import math
import argparse
import subprocess


###################
## Initialisation
###################


parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')
parser.add_argument('wilson', help='display your wilson coefficient')
parser.add_argument('asimov',nargs='?', help='set if asimov test', default='')

args = parser.parse_args()
observable = args.observable
wilson = args.wilson
asimov = args.asimov
year = args.year


os.system('cp inputs/'+year+'/'+observable+'_'+wilson+'_datacard.txt .')

os.system('ValidateDatacards.py '+observable+'_'+wilson+'_datacard.txt')

os.system('ValidateDatacards.py '+observable+'_'+wilson+'_datacard.txt --checkUncertOver 0.1')



os.system('rm '+observable+'_'+wilson+'_datacard.txt')


