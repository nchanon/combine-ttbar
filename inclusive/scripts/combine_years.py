import os, sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='display your observable')
parser.add_argument('timebin', help='display the time bin')

args = parser.parse_args()
observable = args.observable
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

os.system('cp inputs/2016/'+observable+'_datacard'+stimebin+'.txt ./'+observable+'_datacard_2016'+stimebin+'.txt')
os.system('cp inputs/2017/'+observable+'_datacard'+stimebin+'.txt ./'+observable+'_datacard_2017'+stimebin+'.txt')

cmd = 'combineCards.py '+observable+'_datacard_2016'+stimebin+'.txt '+observable+'_datacard_2017'+stimebin+'.txt > inputs/Comb/'+observable+'_datacard'+stimebin+'.txt'
os.system(cmd)

#file = open('inputs/Comb/'+observable+'_datacard.txt','a')
#file.write('timedep group = lumi_stability_2016 lumi_linearity_2016 lumi_stability_2017 lumi_linearity_2017 syst_em_trig_2017\n')
#file.write('timeindep group = rttx rsingletop rdibosons rvjets syst_elec_reco syst_elec_id syst_muon_id syst_muon_iso syst_pu syst_b syst_pt_top syst_prefiring lumi_flat_uncor_2016 lumi_flat_uncor_2017 lumi_flat_cor CP5 hdamp erdOn QCDinspired GluonMove mtop jec syst_em_trig_2016 syst_em_trig_2017')
#file.close()

os.system('rm '+observable+'_datacard_2016'+stimebin+'.txt')
os.system('rm '+observable+'_datacard_2017'+stimebin+'.txt')

os.system('python scripts/workspace_creator.py '+observable+' Comb '+ args.timebin)

