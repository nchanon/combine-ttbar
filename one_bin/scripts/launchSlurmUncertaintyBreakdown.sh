#!/bin/bash

for year in Comb
#for year in 2016 2017 Comb
do
  for breakdown in kind_breakdown exp_breakdown theory_breakdown timeNew_breakdown
#  for breakdown in time_breakdown kind_breakdown exp_breakdown theory_breakdown timeNew_breakdown
#  for breakdown in timeNew_breakdown
  do 
    for asi in data
    #for asi in asimov data
    do
        echo sbatch scripts/slurm_UncertaintyBreakdown.sh ${year} ${breakdown}
        sbatch scripts/slurm_UncertaintyBreakdown.sh ${year} ${breakdown} ${asi}
    done
  done 
done
