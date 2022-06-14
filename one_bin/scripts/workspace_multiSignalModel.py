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

def r_range(value, min, max):
    return '['+str(value)+','+str(min)+','+str(max)+']'

n = 24 
inpath = './inputs/'+year+'/'
outpath = './inputs/'
outcard = 'combine_'+observable+'_'+str(n)+'bins_'+year+'_card.txt'
outwork = 'combine_'+observable+'_'+str(n)+'bins_'+year+'_workspace.root'
#text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel  --PO verbose --PO 'map=ch1/signal:r_1[1,0,10]' --PO 'map=ch2/signal:r_2[1,0,10]' inputs/essaie.txt -o essaiEworkspace.root


cmd = 'text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel '
cmd += '--PO verbose '
for i in range(n):
    if (year!='Comb'): cmd += "--PO 'map=ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,0,10)+"' "
    else: cmd += "--PO 'map=ch1_ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,0,10)+"' " +"--PO 'map=ch2_ch"+str(i+1)+'/signal:r_'+str(i)+r_range(1,0,10)+"' " 
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
