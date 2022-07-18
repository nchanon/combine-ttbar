#!/bin/bash


breakdown="time"

#for year in 2016 2017 Comb
#for year in 2016 2017
for year in Comb
do
    #for wilson in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    for wilson in cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    do
	for breakdown in "time" "kind" "exp" "putrigsmedecay"
	do
	    #sbatch scripts/slurm_UncertaintyBreakdownDetailed.sh ${year} ${breakdown} ${wilson} 
	    sbatch scripts/slurm_UncertaintyBreakdownDetailed_new.sh ${year} ${breakdown} ${wilson}

	done
    done
done
