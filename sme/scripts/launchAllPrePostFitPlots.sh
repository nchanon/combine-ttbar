#!/bin/bash

#for w in cLXX cLXY cLXZ cLYZ cRXX cRXY cXX cXY
#for w in cRXZ cRYZ cXZ cYZ dXX dXY dXZ dYZ
for w in cLXX cLXY cLXZ cLYZ cRXX cRXY cRXZ cRYZ cXX cXY cXZ cYZ dXX dXY dXZ dYZ
do
    #python scripts/prepostfit_plots_sme.py  n_bjets Comb data ${w}  "number of b-jets #times sidereal time bin"
    python scripts/prepostfit_plots_sme_othersfloating.py  n_bjets Comb data ${w}  "number of b-jets #times sidereal time bin"
done

#for w in "cLXX_cLXY_cLXZ_cLYZ" "cRXX_cRXY_cRXZ_cRYZ" "cXX_cXY_cXZ_cYZ" "dXX_dXY_dXZ_dYZ"
#do
#    python scripts/prepostfit_plots_sme_multiple.py n_bjets Comb data $w "number of b-jets #times sidereal time bin"
#done
