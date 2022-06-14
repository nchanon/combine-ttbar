import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')

args = parser.parse_args()
observable = args.observable

os.system('cp inputs/2016/'+observable+'_datacard.txt ./'+observable+'_datacard_2016.txt')
os.system('cp inputs/2017/'+observable+'_datacard.txt ./'+observable+'_datacard_2017.txt')

cmd = 'combineCards.py '+observable+'_datacard_2016.txt '+observable+'_datacard_2017.txt > inputs/Comb/'+observable+'_datacard.txt'
os.system(cmd)

#file = open('inputs/Comb/'+observable+'_datacard.txt','a')
#file.write('timedep group = lumi_stability_2016 lumi_linearity_2016 lumi_stability_2017 lumi_linearity_2017 syst_em_trig_2017\n')
#file.write('timeindep group = rttx rsingletop rdibosons rvjets syst_elec_reco syst_elec_id syst_muon_id syst_muon_iso syst_pu syst_b syst_pt_top syst_prefiring lumi_flat_uncor_2016 lumi_flat_uncor_2017 lumi_flat_cor CP5 hdamp erdOn QCDinspired GluonMove mtop jec syst_em_trig_2016 syst_em_trig_2017')
#file.close()

os.system('rm '+observable+'_datacard_2016.txt')
os.system('rm '+observable+'_datacard_2017.txt')

os.system('python scripts/workspace_creator.py '+observable+' Comb')

