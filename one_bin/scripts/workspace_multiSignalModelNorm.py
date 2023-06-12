import os
import argparse

################################################################################
## Initialisation stuff
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='observable')
parser.add_argument('year', help='year of samples')

args = parser.parse_args() 
observable = args.observable
year = args.year


################################################################################
## function
################################################################################

doNormed = True

range_min = 0
range_max = 2

def r_range(value, min, max):
    return '['+str(value)+','+str(min)+','+str(max)+']'

n = 24 
inpath = './inputs/'+year+'/'
outpath = './inputs/'
outcard = 'combine_'+observable+'_'+str(n)+'bins_'+year+'_card_norm.txt'
outwork = 'combine_'+observable+'_'+str(n)+'bins_'+year+'_workspace_norm.root'
#text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel  --PO verbose --PO 'map=ch1/signal:r_1[1,0,10]' --PO 'map=ch2/signal:r_2[1,0,10]' inputs/essaie.txt -o essaiEworkspace.root


cmd = 'text2workspace.py -P HiggsAnalysis.CombinedLimit.MultiSignalModelNormed:multiSignalModelNormed '
cmd += '--X-exclude-nuisance=stat_muon_iso_2017.* --X-exclude-nuisance=syst_l_uncorrelated_2017.* --X-exclude-nuisance=RelativeSample_2017_jec.* '
#cmd += '--X-exclude-nuisance=FlavorPureCharm_jec --X-exclude-nuisance=FlavorPureQuark_jec'
#cmd += '--X-exclude-nuisance=syst_elec_reco.* '
#cmd += '--X-exclude-nuisance=syst_b_correlated.* --X-exclude-nuisance=syst_l_correlated.* '
#cmd += '--no-b-only '
#cmd += '--no-wrappers '
#cmd += '--PO verbose '
cmd += '--optimize-simpdf-constraints=cms '
#cmd += '--optimize-simpdf-constraints=none '
for i in range(n):
    if i!=n-1:
        cmd += "--PO f_"+str(i)+" "
    else:
	cmd += "--PO r_avg"+" "
    if (year!='Comb'):
	cmd += "--PO 'map=ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' "
    #if (year!='Comb'): cmd += "--PO 'map=ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' "
    #else: cmd += "--PO 'map=ch1_ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' " +"--PO 'map=ch2_ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' " 
    else: 
	cmd += "--PO 'map=ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' " +"--PO 'map=ch"+str(n+i+1)+'/signal:r_'+str(i)+r_range(1,range_min,range_max)+"' " 
    #else: cmd += "--PO 'map=ch*_ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,0,10)+"' "
cmd += inpath + outcard
cmd += ' -o '+outpath + outwork

#print cmd

## new datacard
if (year!='Comb'):
   print('Cards merging')
#    os.system('cd '+inpath+' && combineCards.py '+observable+'*_datacard.txt > '+outcard)
   cmd2 = "cd "+inpath+" && "
   cmd2 += "combineCards.py "
   for i in range(n):
     cmd2 += observable+'_'+str(n)+'_'+str(i)+'_datacard.txt '
   cmd2 += '> '+outcard 
   print cmd2
   os.system(cmd2)

## workspace generator
print('Workspace generator')
#os.system(cmd2)
print cmd
os.system(cmd)
