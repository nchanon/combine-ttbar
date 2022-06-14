#!/bin/bash

year=Comb

for wilson in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ 
do
  echo sbatch scripts/slurm_ImpactPlot.sh ${year} ${wilson} 
  sbatch scripts/slurm_ImpactPlot.sh ${year} ${wilson}
done
