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

#def asimov_param(w):
#    if asimov == 'asimov':
#        return ['--setParameters',w+'=0','-t','-1']
#    return []

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


for wilson in wilson_list_all:
    os.system('cp inputs/2016/'+observable+'_'+wilson+'_datacard.txt ./'+observable+'_'+wilson+'_datacard_2016.txt')
    os.system('cp inputs/2017/'+observable+'_'+wilson+'_datacard.txt ./'+observable+'_'+wilson+'_datacard_2017.txt')

    cmd = 'combineCards.py '+observable+'_'+wilson+'_datacard_2016.txt '+observable+'_'+wilson+'_datacard_2017.txt > inputs/Comb/'+observable+'_'+wilson+'_datacard.txt'
    os.system(cmd)

    #file = open('inputs/Comb/'+observable+'_'+wilson+'_datacard.txt','a')
    #file.write('timedep group = lumi_stability_2016 lumi_linearity_2016 emu_trig_2016 lumi_stability_2017 lumi_linearity_2017 emu_trig_2017\n')
    #file.write('timeindep group = rttx rsingletop rdibosons rvjets syst_elec_reco syst_elec_id syst_muon_id syst_muon_iso syst_pu syst_b syst_pt_top syst_prefiring lumi_flat_uncor_2016 lumi_flat_uncor_2017 lumi_flat_cor CP5 hdamp erdOn QCDinspired GluonMove mtop jec')
    #file.close()

    os.system('rm '+observable+'_'+wilson+'_datacard_2016.txt')
    os.system('rm '+observable+'_'+wilson+'_datacard_2017.txt')

    os.system('python scripts/workspace_creator.py '+observable+' Comb '+wilson)

#os.system('python scripts/fit_alone.py '+observable+' Comb '+wilson+' '+asimov)
