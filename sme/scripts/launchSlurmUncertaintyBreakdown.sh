#!/bin/bash

for year in Comb
do
  echo sbatch scripts/slurm_UncertaintyBreakdown.sh ${year}
  sbatch scripts/slurm_UncertaintyBreakdown.sh ${year}
done
