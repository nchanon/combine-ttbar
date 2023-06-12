#!/bin/bash


#breakdown="time"

#for year in 2016 2017 Comb
#for year in 2016 2017
for year in Comb
do
    #for wilson in sme_all
    for wilson in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    #for wilson in cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    do
	#for breakdown in "timeNew"
	#for breakdown in "smedecay"
	for breakdown in "timeNew" "kind" "exp" "theory" "smedecay" #"putrigsmedecay"
	do
	    for asi in asimov data #injectiontest
	    do
		
		sbatch scripts/slurm_UncertaintyBreakdownDetailed_othersfloating.sh ${year} ${breakdown} ${wilson} ${asi}
	        sbatch scripts/slurm_UncertaintyBreakdownDetailed_new.sh ${year} ${breakdown} ${wilson} ${asi}
                #sbatch scripts/slurm_UncertaintyBreakdownDetailed_new.sh ${year} ${breakdown} ${wilson} injectiontest
	        echo ${year} ${breakdown} ${wilson} ${asi}
	    done
	done
    done
done


#for year in 2016 2017 Comb
#do
#        for breakdown in "timeNew" "kind" "exp" "theory" "smedecay"
#        do
#		sbatch scripts/slurm_UncertaintyBreakdownDetailed_othersfloating.sh ${year} ${breakdown} sme_all ${asi}
#	done
#done

