#!/bin/bash

for seed in `seq 0 199` #199
do
    sbatch scripts/slurm_RunToys.sh ${seed}
done


#for year in 2016 2017 Comb
#do
#  for breakdown in time_breakdown kind_breakdown exp_breakdown theory_breakdown
#  do 
    #echo sbatch scripts/slurm_UncertaintyBreakdown.sh ${year} ${breakdown}
    #sbatch scripts/slurm_UncertaintyBreakdown.sh ${year} ${breakdown}
#    python scripts/uncertainty_breakdown_detailed_normalized.py n_bjets ${year} ${breakdown} asimov

#  done 
#done
