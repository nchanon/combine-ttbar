#!/bin/bash


for year in Comb
#for year in 2016 2017 Comb
do
    for w in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
    do
        python scripts/goodnessoffit_new.py n_bjets ${year} ${w} 40 -99
    done

    #for w in "cLXX,cLXY,cLXZ,cLYZ" "cRXX,cRXY,cRXZ,cRYZ" "cXX,cXY,cXZ,cYZ" "dXX,dXY,dXZ,dYZ"
    #do
    #	python scripts/goodnessoffit_new.py n_bjets ${year} ${w} 10 -99
    #done

done

