#!/bin/bash
#
#SBATCH --ntasks=1

#srun -n1 --exclusive python scripts/launch_multidimfit.py ${1} ${2} ${3} &
srun -n1 --exclusive python scripts/prepostfit_plots_differentialNorm.py ${1} ${2} ${3} "number of b-jets #times sidereal time bin" &


wait
