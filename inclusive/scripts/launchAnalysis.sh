python scripts/workspace_creator.py ${1} 2016
python scripts/workspace_creator.py ${1} 2017
python scripts/combine_years.py ${1}
python scripts/uncertainty_breakdown.py ${1}

python scripts/impacts.py ${1} 2016 asimov
python scripts/impacts.py ${1} 2017 asimov
python scripts/impacts.py ${1} Comb asimov
python scripts/impacts.py ${1} 2016 data
python scripts/impacts.py ${1} 2017 data
python scripts/impacts.py ${1} Comb data


