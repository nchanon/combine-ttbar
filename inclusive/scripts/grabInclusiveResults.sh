#!/bin/bash

#Parameter ${1}: observable

mkdir -p results
cp impacts/Comb/Latex_UncertaintyBreakdown_${1}_punew.txt results/
cp impacts/*/asimov/${1}_inclusive_impacts_*_punew_*.pdf results/ 
cp impacts/*/${1}_inclusive_impacts_*_punew_*.pdf results/
cp impacts/CorrelationMatrixParameters_${1}_*_punew.pdf results/
cp impacts/*/${1}_*_punew_P*-fit.pdf results/
cp impacts/*/goodnessOfFit_${1}_*_punew.pdf results/
