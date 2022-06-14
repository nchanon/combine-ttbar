
##   Combine tools for ttbar Lorentz analysis

This repository contains a set of scripts to call Combine tool to produce ttbar Lorentz analysis results.

# Install Combine

See https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/

Choose version CC7 with CMSSW_10_2_13

On the CMSSW_10_2_13/src directory:

    > bash <(curl -s https://raw.githubusercontent.com/cms-analysis/CombineHarvester/master/CombineTools/scripts/sparse-checkout-https.sh)

On lyoui machines:

    > cms_env
    > cmsenv

Compile with scramv1 b.

# Installation :

In your terminal type following commands: 

    > git clone https://github.com/nchanon/combine-ttbar.git

The up-to-date directories are: inclusive, one_bin and sme. Unrolled is not used anymore. 

At first installation, a few directories need to be created:

    > source createDir.sh

The inputs are generated by PyPlotFramework (PPFv2, see https://github.com/nchanon/PPFv2).  
PPFv2 has a script (combine_export) to export the inputs for combine, stored for instance in:

inclusive/inputs/'year' directory

# Inclusive analysis

As an example, running the full time-integrated analysis using the observable n_bjets requires the following.

    > cd inclusive

First create the workspaces:

    > python scripts/workspace_creator.py n_bjets 2016
    > python scripts/workspace_creator.py n_bjets 2017

Make the combined workspace:

    > python scripts/combine_years.py n_bjets

Then perform the inclusive fits (providing stat+syst breakdown) for each year, on asimov and data:

    > python scripts/uncertainty_breakdown.py n_bjets

Make the impact plots:

    > python scripts/impacts.py n_bjets 2016 asimov
    > python scripts/impacts.py n_bjets 2017 asimov
    > python scripts/impacts.py n_bjets Comb asimov
    > python scripts/impacts.py n_bjets 2016 data
    > python scripts/impacts.py n_bjets 2017 data
    > python scripts/impacts.py n_bjets Comb data

Make the pre-fit (showing data/mc comparison with uncertainty band) and post-fit plots:

    > python scripts/prepostfit_plots.py n_bjets 2016 asimov "number of b-jets"
    > python scripts/prepostfit_plots.py n_bjets 2017 asimov "number of b-jets"

In python scripts/prepostfit_plots.py, combine must be run. 
There is an option to not running, if willing to adjust the plots.
Also, the pre-fit and post-fit options can be set by editing the script.


Make the goodness-of-fit tests (take some time, because it is running 500 toys each):

    > python scripts/goodnessoffit.py n_bjets 2016
    > python scripts/goodnessoffit.py n_bjets 2017
    > python scripts/goodnessoffit.py n_bjets Comb

In scripts/goodnessoffit.py, combine must be run. There is an option to not run it, if willing to adjust the plots.


# Differential analysis 

    > cd one_bin

To generate the workspaces (still on the example of n_bjets): 
    
    > python scripts/workspace_multiSignalModel.py n_bjets 2016
    > python scripts/workspace_multiSignalModel.py n_bjets 2017

A workspace will be created in 'inputs' directory.

Making the combined workspace:

    > python scripts/combine_years.py n_bjets
    > python scripts/workspace_multiSignalModel.py n_bjets Comb

Running simple fit and producing the plot of signal strength vs sidereal time:

    > python scripts/launch_multidimfit.py n_bjets 2016 asimov
    > python scripts/launch_multidimfit.py n_bjets 2017 asimov
    > python scripts/launch_multidimfit.py n_bjets Comb asimov

Running impact plots (extremely CPU intensive... not to be done!):

    > python scripts/uncorrelated_impacts.py n_bjets 2016 asimov
    > python scripts/uncorrelated_impacts.py n_bjets 2017 asimov
    > python scripts/uncorrelated_impacts.py n_bjets Comb asimov

Running the fit with uncertainty breakdown in stat+syst (not so useful since detailed breakdown are also possible):

    > python scripts/uncertainty_breakdown.py n_bjets 2016 asimov
    > python scripts/uncertainty_breakdown.py n_bjets 2017 asimov
    > python scripts/uncertainty_breakdown.py n_bjets Comb asimov

Uncertainty breakdown details (here example of Comb only):

    > python scripts/uncertainty_breakdown_detailed.py n_bjets Comb time_breakdown asimov > log_time_breakdown
    > python scripts/uncertainty_breakdown_detailed.py n_bjets Comb kind_breakdown asimov > log_kind_breakdown
    > python scripts/uncertainty_breakdown_detailed.py n_bjets Comb exp_breakdown asimov > log_exp_breakdown
    > python scripts/uncertainty_breakdown_detailed.py n_bjets Comb theory_breakdown asimov > log_theory_breakdown

(Redirection is useful to check if everything went fine)

Running pre-fit plots:

    > scripts/prepostfit_plots_differential.py n_bjets 2016 asimov "number of b jets #times sidereal time bin"
    > scripts/prepostfit_plots_differential.py n_bjets 2017 asimov "number of b jets #times sidereal time bin"



# c_munu fit

    > cd sme

Create the workspace with the good physics model :

    > python scripts/workspace_creator.py 'observable' 'year' 'wilson'

The wilson coefficient is ssomething like "cLXX, dXY, ... etc" 

To make the fit : 

    > python scripts/fit_alone.py 'observable' 'year' 'wilson' 'asimov'

exemple : 

    > python scripts/fit_alone.py m_dilep 2016 cLXX asimov

For impacts : 

    > python scripts/impacts.py m_dilep 2016 cLXX asimov

Impacts plots are stored in 'impacts' directory 



