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

srun -n1 --exclusive python scripts/uncertainty_breakdown_detailed_new.py n_bjets ${1} ${2}_breakdown ${3} asimov  &
#uncertainty_breakdown_detailed.py n_bjets ${1} theory_breakdown asimov ${1} &

wait
