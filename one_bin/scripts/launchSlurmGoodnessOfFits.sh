#!/bin/bash

#for year in Comb
for year in 2016 2017 Comb
do
    for algo in saturated
    #for algo in saturated KS AD
    do
	for muValue in muSM
	#for muValue in muSM muIncData
	do
            sbatch scripts/slurm_GoodnessOfFit.sh n_bjets ${year} ${algo} ${muValue}
	done
    done
done

