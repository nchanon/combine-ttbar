#!/bin/bash

for year in 2016 2017 Comb
do
    for asim in asimov data
    do
        sbatch scripts/slurm_DifferentialFit.sh n_bjets ${year} ${asim}
    done
done

