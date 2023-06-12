#!/bin/bash


for year in Comb
#for year in 2016 2017 Comb
do
    for w in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    do
	for seed in `seq 0 24`
	do
	    sbatch scripts/slurm_GoodnessOfFit.sh n_bjets ${year} ${w} 40 ${seed}
	done
    done

    for w in "cLXX,cLXY,cLXZ,cLYZ" "cRXX,cRXY,cRXZ,cRYZ" "cXX,cXY,cXZ,cYZ" "dXX,dXY,dXZ,dYZ"
    do
	for seed in `seq 0 99`
	do
            sbatch scripts/slurm_GoodnessOfFit.sh n_bjets ${year} ${w} 10 ${seed}
	done
    done

done
