#!/bin/bash
#
#SBATCH --ntasks=1

#export EOS_MGM_URL=root://lyoeos.in2p3.fr

#srun -n1 --exclusive ./runLHEtoNanoGEN.sh root://lyoeos.in2p3.fr//home/nchanon/TTbarNanoGEN/Test/PROC_SM_ttbar_emu_13TeV_LHE_test.lhe &
#srun -n1 --exclusive ./runLHEtoNanoGEN.sh /gridgroup/cms/nchanon/CMSSW_10_6_27/src/TTbarLO_test/slurm/PROC_SM_ttbar_emu_13TeV_LHE_test.lhe &

#for i in `seq 0 9`
#do
#  srun -n1 --exclusive ./runLHEtoNanoGEN.sh PROC_SM_ttbar_emu_13TeV_LHE_${i} &
#done

# Comb asimov 

#srun -n1 --exclusive combine -M MultiDimFit higgsCombine.snapshot_n_bjets_Comb_theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco.MultiDimFit.mH120.root -n .freezehdamp_n_bjets_Comb_theory_pttop_mtop_ps_qcdscale_pdfas_hdamp_uetune_colorreco_toy_${1}  --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01  --setParameters r_0=1,r_1=1,r_2=1,r_3=1,r_4=1,r_5=1,r_6=1,r_7=1,r_8=1,r_9=1,r_10=1,r_11=1,r_12=1,r_13=1,r_14=1,r_15=1,r_16=1,r_17=1,r_18=1,r_19=1,r_20=1,r_21=1,r_22=1,r_23=1 --setParameterRanges r_0=0.5,2.0:r_1=0.5,2.0:r_2=0.5,2.0:r_3=0.5,2.0:r_4=0.5,2.0:r_5=0.5,2.0:r_6=0.5,2.0:r_7=0.5,2.0:r_8=0.5,2.0:r_9=0.5,2.0:r_10=0.5,2.0:r_11=0.5,2.0:r_12=0.5,2.0:r_13=0.5,2.0:r_14=0.5,2.0:r_15=0.5,2.0:r_16=0.5,2.0:r_17=0.5,2.0:r_18=0.5,2.0:r_19=0.5,2.0:r_20=0.5,2.0:r_21=0.5,2.0:r_22=0.5,2.0:r_23=0.5,2.0 -t 1 -s ${1} --toysFrequentist --freezeParameters hdamp --snapshotName MultiDimFit --algo=singles --saveFitResult --saveToys  &

#srun -n1 --exclusive combine -M MultiDimFit higgsCombine.snapshot_n_bjets_Comb_exp_theory_bkgdnorm_lumi_mcstat.MultiDimFit.mH120.root -n .freezetheory_n_bjets_Comb_exp_theory_bkgdnorm_lumi_mcstat_toy_${1}  --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01  --setParameters r_0=1,r_1=1,r_2=1,r_3=1,r_4=1,r_5=1,r_6=1,r_7=1,r_8=1,r_9=1,r_10=1,r_11=1,r_12=1,r_13=1,r_14=1,r_15=1,r_16=1,r_17=1,r_18=1,r_19=1,r_20=1,r_21=1,r_22=1,r_23=1 --setParameterRanges r_0=0.5,2.0:r_1=0.5,2.0:r_2=0.5,2.0:r_3=0.5,2.0:r_4=0.5,2.0:r_5=0.5,2.0:r_6=0.5,2.0:r_7=0.5,2.0:r_8=0.5,2.0:r_9=0.5,2.0:r_10=0.5,2.0:r_11=0.5,2.0:r_12=0.5,2.0:r_13=0.5,2.0:r_14=0.5,2.0:r_15=0.5,2.0:r_16=0.5,2.0:r_17=0.5,2.0:r_18=0.5,2.0:r_19=0.5,2.0:r_20=0.5,2.0:r_21=0.5,2.0:r_22=0.5,2.0:r_23=0.5,2.0 -t 1 -s ${1} --freezeParameters syst_pt_top,rgx{syst_ps_isr.*},rgx{syst_ps_fsr.*},rgx{syst_qcdscale.*},syst_pdfas,hdamp,CP5,erdOn,GluonMove,QCDinspired,mtop --snapshotName MultiDimFit --algo=singles  --saveWorkspace --saveFitResult --saveToys  &

#srun -n1 --exclusive combine -M MultiDimFit higgsCombine.snapshot_n_bjets_Comb_exp_theory_bkgdnorm_lumi_mcstat.MultiDimFit.mH120.root -n .freezebkgd_norm_n_bjets_Comb_exp_theory_bkgdnorm_lumi_mcstat_toy_${1}  --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01  --setParameters r_0=1,r_1=1,r_2=1,r_3=1,r_4=1,r_5=1,r_6=1,r_7=1,r_8=1,r_9=1,r_10=1,r_11=1,r_12=1,r_13=1,r_14=1,r_15=1,r_16=1,r_17=1,r_18=1,r_19=1,r_20=1,r_21=1,r_22=1,r_23=1 --setParameterRanges r_0=0.5,2.0:r_1=0.5,2.0:r_2=0.5,2.0:r_3=0.5,2.0:r_4=0.5,2.0:r_5=0.5,2.0:r_6=0.5,2.0:r_7=0.5,2.0:r_8=0.5,2.0:r_9=0.5,2.0:r_10=0.5,2.0:r_11=0.5,2.0:r_12=0.5,2.0:r_13=0.5,2.0:r_14=0.5,2.0:r_15=0.5,2.0:r_16=0.5,2.0:r_17=0.5,2.0:r_18=0.5,2.0:r_19=0.5,2.0:r_20=0.5,2.0:r_21=0.5,2.0:r_22=0.5,2.0:r_23=0.5,2.0 -t 1 -s ${1} --freezeParameters rttx,rsingletop,rdibosons,rvjets --snapshotName MultiDimFit --algo=singles  --saveWorkspace --saveFitResult --saveToys  &

# Comb data

srun -n1 --exclusive combine -M MultiDimFit higgsCombine.snapshot_n_bjets_Comb_time_flat_uncorr_corr_mcstat_data.MultiDimFit.mH120.root -n .freezetime_flat_n_bjets_Comb_time_flat_uncorr_corr_mcstat_data_${1}  --cminDefaultMinimizerStrategy 0 --cminDefaultMinimizerTolerance 0.01  --setParameters r_0=1,r_1=1,r_2=1,r_3=1,r_4=1,r_5=1,r_6=1,r_7=1,r_8=1,r_9=1,r_10=1,r_11=1,r_12=1,r_13=1,r_14=1,r_15=1,r_16=1,r_17=1,r_18=1,r_19=1,r_20=1,r_21=1,r_22=1,r_23=1 --setParameterRanges r_0=0.5,2.0:r_1=0.5,2.0:r_2=0.5,2.0:r_3=0.5,2.0:r_4=0.5,2.0:r_5=0.5,2.0:r_6=0.5,2.0:r_7=0.5,2.0:r_8=0.5,2.0:r_9=0.5,2.0:r_10=0.5,2.0:r_11=0.5,2.0:r_12=0.5,2.0:r_13=0.5,2.0:r_14=0.5,2.0:r_15=0.5,2.0:r_16=0.5,2.0:r_17=0.5,2.0:r_18=0.5,2.0:r_19=0.5,2.0:r_20=0.5,2.0:r_21=0.5,2.0:r_22=0.5,2.0:r_23=0.5,2.0 -t 1 -s ${1} --freezeParameters rgx{lumi_flat_uncor_.*},lumi_flat_cor,rttx,rsingletop,rdibosons,rvjets,syst_pt_top,rgx{syst_ps_isr.*},rgx{syst_ps_fsr.*},rgx{syst_qcdscale.*},syst_pdfas,hdamp,CP5,erdOn,GluonMove,QCDinspired,mtop,FlavorPureGluon_jec,FlavorPureBottom_jec --snapshotName MultiDimFit --algo=singles  --saveWorkspace --saveFitResult  --saveToys  &


wait
