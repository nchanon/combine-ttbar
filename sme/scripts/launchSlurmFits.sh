#!/bin/bash



for year in 2016 2017 Comb
do
    for asim in asimov data
    do
	sbatch scripts/slurm_SingleWilsonFit.py n_bjets ${year} ${asim}
        sbatch scripts/slurm_OthersFloatingWilsonFit.py n_bjets ${year} ${asim}
	sbatch scripts/slurm_MultipleWilsonFit.py n_bjets ${year} ${asim}

    done
done
