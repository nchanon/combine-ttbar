from ROOT import TFile, TH1, TCanvas, TH1F, TH2F, THStack, TString
from ROOT import TLegend, TApplication, TRatioPlot, TPad, TFrame
from ROOT import TPaletteAxis, TGraphAsymmErrors
from ROOT import gStyle

def plot2Dmatrix(hCov, title, doSave):
    gStyle.SetPaintTextFormat("2.2f")
    canvas = TCanvas(title,title,1000,800)
    pad = TPad("pad","pad",0,0,1,1)
    pad.SetLeftMargin(0.1)
    pad.SetBottomMargin(0.1)
    pad.SetRightMargin(0.12)
    pad.Draw()
    pad.cd()
    for i in range(24):
        hCov.GetXaxis().SetBinLabel(1+i, "r_"+str(i))
        hCov.GetYaxis().SetBinLabel(1+i, "r_"+str(i))
    hCov.GetXaxis().LabelsOption("v")
    hCov.GetXaxis().SetLabelSize(0.025)
    hCov.GetYaxis().SetLabelSize(0.025)
    hCov.GetZaxis().SetLabelSize(0.025)
    hCov.SetTitle("Signal strengths "+title)
    palette = hCov.GetListOfFunctions().FindObject("palette")
    palette = TPaletteAxis()
    palette.SetX1NDC(0.92)
    palette.SetX2NDC(0.94)
    palette.SetY1NDC(0.2)
    palette.SetY2NDC(0.9)
    hCov.Draw("COLZTEXT")
    #raw_input()
    if (doSave==True):
	canvas.Print("impacts/"+title+"_SignalStrength.pdf")

def getPOIcorrMatrix(fDiagnostics, title, hCovPOI):
    
    hCov = fDiagnostics.Get("covariance_fit_s")
    #hCovPOI = TH2F("covariance_fit_s_POI"+title,"covariance_fit_s_POI"+title,24,0,24,24,0,24)
    for i in range(24):
        for j in range(24):
            corrval = hCov.GetBinContent(hCov.GetXaxis().FindBin("r_"+str(i)), hCov.GetYaxis().FindBin("r_"+str(j)))
            hCovPOI.SetBinContent(i+1,j+1,corrval)

    #hCovPOI.Draw("COLZTEXT")
    #plot2Dmatrix(hCovPOI, title, False)

    #return hCovPOI
