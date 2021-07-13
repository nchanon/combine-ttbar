import json
import argparse
from ROOT import TH1F, TFile, TCanvas, TGraphAsymmErrors

parser = argparse.ArgumentParser()
parser.add_argument('observable', help='observable')
parser.add_argument('asimov', help='azimov or nothing')
args = parser.parse_args() 

observable = args.observable
asimov = args.asimov

nbin = 24
# azimov 
if asimov == 'asimov':
    direct = '/asimov' 
else: 
    direct = ''

##############################################################################
##############################################################################

def path(observable, directory, option):
    return './impacts/'+directory+option+'/'+observable+'_impacts'+directory+'.json'

def get_value(data, value):
    if(value == 'value'):
        return data[1]
    elif(value == 'up'):
        return data[1]-data[0]
    elif(value == 'down'):
        return data[2]-data[1]
    else:
        print 'argument need to be "value", "up" or "down"'

def get_global(input_json, value):
    tmp  = json.dumps(input_json[0])
    data = json.loads(tmp)
    return get_value(data['fit'], value)


def get(input_json, value):
    foo = []
    tmp  = json.dumps(input_json['params'])
    data = json.loads(tmp)
    for i in data:
        if(value == 'name'):
            foo.append(i['name'])
        else:
            foo.append(get_value(i['r'], value))
    return foo

def style_hist(hist):
    hist.SetStats(0)
    hist.GetYaxis().SetTitle('r')
    hist.GetXaxis().SetTitle('sidereal time')
    hist.Write()

def histogram_gen(value, syst):
    c = TCanvas();
    hist   = TH1F(observable, observable, nbin, 0, nbin)
    for i in range(nbin):
        hist.SetBinContent(i+1, value[i])
        hist.SetBinError(i+1, syst[i])
    style_hist(hist)
    hist.Draw()
    if asimov == 'asimov':
        c.SaveAs('./export/asimov_'+observable+'_time.png')    
        c.SaveAs('./export/asimov_'+observable+'_time.pdf')
    else:
        c.SaveAs('./export/'+observable+'_time.png')    
        c.SaveAs('./export/'+observable+'_time.pdf')        

def histogram_syst_gen(index, name, value, syst):
    c = TCanvas(name[0][index]+'_'+str(index), name[0][index]+'_'+str(index));
    hist   = TH1F(name[0][index], name[0][index], nbin, 0, nbin)
    for i in range(nbin):
        hist.SetBinContent(i+1, value[i][index])
        hist.SetBinError(i+1, syst[i][index])
    style_hist(hist)
    hist.Draw()
    if asimov == 'asimov':
        c.SaveAs('./export/asimov_'+observable+'_'+name[0][index]+'_'+str(index)+'_time.png')    
        c.SaveAs('./export/asimov_'+observable+'_'+name[0][index]+'_'+str(index)+'_time.pdf')    
    else:
        c.SaveAs('./export/'+observable+'_'+name[0][index]+'_'+str(index)+'_time.png')    
        c.SaveAs('./export/'+observable+'_'+name[0][index]+'_'+str(index)+'_time.pdf')            

##############################################################################
##############################################################################

bin_content    = []
bin_error_up   = []
bin_error_down = []

syst_name       = [] 
syst_content    = []
syst_error_up   = []
syst_error_down = []

for i in range(nbin):
    with open(path(observable, str(i), direct)) as json_file:
        data = json.load(json_file)
        bin_content.append(get_global(data['POIs'], 'value'))
        bin_error_up.append(get_global(data['POIs'], 'up'))
        bin_error_down.append(get_global(data['POIs'], 'down'))
        '''
        syst_name.append([])
        syst_content.append([])
        syst_error_up.append([])
        syst_error_down.append([])
        syst_name[i]       = get(data, 'name')
        syst_content[i]    = ##############################################################################get(data, 'value')
        syst_error_up[i]   = get(data, 'up')
        syst_error_down[i] = get(data, 'down')
        '''
        syst_name.append(get(data, 'name'))
        syst_content.append(get(data, 'value'))
        syst_error_up.append(get(data, 'up'))
        syst_error_down.append(get(data, 'down'))

#print syst_name[0]
#print syst_content[0]

'''
ttt = json.dumps(data['params'])
ddd = json.loads(ttt)
print ddd[1]['r']
'''

if asimov == 'asimov':
    newfile = TFile('./results/asimov_'+observable+'.root', 'RECREATE')
else:
    newfile = TFile('./results/'+observable+'.root', 'RECREATE')

histogram_gen(bin_content, bin_error_up)
for i in range(len(syst_name[0])):
    histogram_syst_gen(i, syst_name, syst_content, syst_error_up)

newfile.Close()

'''
graph = TGraphAsymmErrors(hist)
for i in range(nbin):
    graph.SetPointEYhigh(i+1, bin_error_up[i])
    graph.SetPointEYlow(i+1, bin_error_down[i])
    graph.SetPointEXhigh(i+1, 0)
    graph.SetPointEXlow(i+1, 0)
'''
