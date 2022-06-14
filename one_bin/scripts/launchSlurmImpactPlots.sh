#!/bin/bash

for year in 2016 2017 Comb
do
  echo sbatch scripts/slurm_ImpactPlot.sh ${year}
  sbatch scripts/slurm_ImpactPlot.sh ${year}
done
