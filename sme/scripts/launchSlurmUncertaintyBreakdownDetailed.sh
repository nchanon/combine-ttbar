#!/bin/bash


#breakdown="time"

#for year in 2016 2017 Comb
#for year in 2016 2017
for year in Comb
do
    for wilson in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    #for wilson in cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    do
	#for breakdown in "time"
	#for breakdown in "smedecay"
	for breakdown in "time" "kind" "exp" #"theory" #"putrigsmedecay"
	do
	    #sbatch scripts/slurm_UncertaintyBreakdownDetailed.sh ${year} ${breakdown} ${wilson} asimov
	    sbatch scripts/slurm_UncertaintyBreakdownDetailed_new.sh ${year} ${breakdown} ${wilson} asimov
            #sbatch scripts/slurm_UncertaintyBreakdownDetailed_new.sh ${year} ${breakdown} ${wilson} injectiontest
	    echo ${year} ${breakdown} ${wilson} 
	done
    done
done


#for year in 2016 2017 Comb
#do
#        for breakdown in "time" "kind" "exp" "theory" #"putrigsmedecay"
#        do
#            python scripts/uncertainty_breakdown_detailed_new.py n_bjets ${year} ${breakdown}_breakdown sme_all asimov
#        done
#done

