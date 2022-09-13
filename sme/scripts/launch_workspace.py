import os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('year', help='year of samples')


args = parser.parse_args()
observable = args.observable
year = args.year

wilson_list_all = [
    'cLXX',
    'cRXX',
    'cXX',
    'dXX',
    'cLXY',
    'cRXY',
    'cXY',
    'dXY',
    'cLXZ',
    'cRXZ',
    'cXZ',
    'dXZ',
    'cLYZ',
    'cRYZ',
    'cYZ',
    'dYZ',
    'cLXX,cLXY,cLXZ,cLYZ',
    'cRXX,cRXY,cRXZ,cRYZ',
    'cXX,cXY,cXZ,cYZ',
    'dXX,dXY,dXZ,dYZ'
]

wilson_list = wilson_list_all

for l in wilson_list:
    os.system('python scripts/workspace_creator.py '+observable+' '+year+' '+l)
