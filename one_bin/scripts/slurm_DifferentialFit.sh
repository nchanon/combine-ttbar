#!/bin/bash
#
#SBATCH --ntasks=1

srun -n1 --exclusive python scripts/launch_multidimfitNorm.py ${1} ${2} ${3} &

wait
