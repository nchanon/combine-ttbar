#!/bin/bash
#
#SBATCH --ntasks=1

srun -n1 --exclusive python scripts/goodnessoffitNorm.py ${1} ${2} ${3} ${4} &

wait
