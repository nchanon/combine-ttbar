#!/bin/bash

echo `pwd`

#cp /tmp/x509up_u2487 .

#export EOS_MGM_URL=root://lyoeos.in2p3.fr

DIR="/gridgroup/cms/nchanon/CMSSW_10_2_13/src/combine-ttbar/sme/"

cd ${DIR}

python scripts/uncertainty_breakdown.py n_bjets ${1} asimov

