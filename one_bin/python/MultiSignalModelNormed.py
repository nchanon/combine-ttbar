
from HiggsAnalysis.CombinedLimit.PhysicsModel import *

### This is the base python class to study the Higgs width

#class MultiSignalModelNormed(MultiSignalModel):
class MultiSignalModelNormed(PhysicsModel):
    def __init__(self):
        PhysicsModel.__init__(self)
        #self.wilson = []
        #self.process = []
	self.fractions = []
	self.signalstrengths = []
	self.signalstrength_avg = ""
	self.poiList = ""

    def setPhysicsOptions(self,physOptions):

        for po in physOptions:
	    if po.find("f_")!=-1:
		self.fractions.append(po)
		self.signalstrengths.append(po.replace("f_","r_"))
		print "Fraction "+self.fractions[-1]+" associated with signal strength "+self.signalstrengths[-1]
	    if po.find("r_avg")!=-1:
		self.signalstrengths.append("r_23")
		self.signalstrength_avg = po
		print "Averaged signal strength "+self.signalstrength_avg
	
            #for c in wilson_list:
            #    if c in po:
            #        print 'wilson coefficient : '+c
            #        self.process.append(c)
            #        self.wilson.append(c)


    def setModelBuilder(self, modelBuilder):
        PhysicsModel.setModelBuilder(self,modelBuilder)

    def getYieldScale(self,bin,process):

	#print bin + ' ' + process
	isSignal = False
	for mu in self.signalstrengths:
	    num=int(mu.split("r_")[1])+1
	    #print "ch"+str(num)+"/signal"
	    if (bin=="ch"+str(num) or bin=="ch"+str(num+24)) and process=="signal": #process=="signal" + how to check for channel?
                #print "ch"+str(num)+"/signal"
		print bin+"/signal"
	        return "get_fraction_"+mu 
		isSignal = True
	    #elif process=="r_23":
		#return "get_fraction_"+mu
	
	#for c in self.process:
        #    if process == c: 
        #        return ("sme_func"+c)
	#if process == "signal":
        #    return "bkd_func"
	#elif process.find("XX")!=-1 or process.find("XY")!=-1 or process.find("XZ")!=-1 or process.find("YZ")!=-1:
	#    return 0
        if isSignal==False:
            return 1
            
    def doParametersOfInterest(self):

        if not self.modelBuilder.out.var(self.signalstrength_avg):
            self.modelBuilder.doVar(self.signalstrength_avg+"[1.0,0.,2.]")
	    self.poiList = self.signalstrength_avg

	fracAllMinusOne = ""
        for frac in self.fractions:
	    mu = frac.replace("f_","r_")
	    if not self.modelBuilder.out.var(frac):
		self.modelBuilder.doVar(frac+"[1.0,0.,2.]")
		#if mu!="r_23":
                self.modelBuilder.factory_("expr::get_fraction_"+mu+"(\"@0*@1"+"\", "+self.signalstrength_avg+","+frac+")")
		print "expr::get_fraction_"+mu+"(\"@0*@1"+"\", "+self.signalstrength_avg+","+frac+")"
		self.poiList += "," + frac
		#if mu=="r_23":
		if frac != self.fractions[-1]:
		    fracAllMinusOne += frac + ","
		if frac == self.fractions[-1]:
		    fracAllMinusOne += frac 

	self.modelBuilder.factory_("expr::get_fraction_r_23(\"@0*(24-@1-@2-@3-@4-@5-@6-@7-@8-@9-@10-@11-@12-@13-@14-@15-@16-@17-@18-@19-@20-@21-@22-@23)"+"\", "+self.signalstrength_avg+","+fracAllMinusOne+")")
	print "expr::get_fraction_r_23(\"@0*(24-@1-@2-@3-@4-@5-@6-@7-@8-@9-@10-@11-@12-@13-@14-@15-@16-@17-@18-@19-@20-@21-@22-@23)"+"\", "+self.signalstrength_avg+","+fracAllMinusOne+")"

	
        self.modelBuilder.doSet("POI",self.poiList)


'''
	expr_muavg = "("
	muall = ""
	for i in range(len(self.signalstrengths)):
	    expr_muavg += "@"+str(i+1)
	    muall += self.signalstrengths[i]
	    if i!=range(len(self.signalstrengths))-1:
		expr_muavg += "+"
		muall += ","
	    expr_muavg += ")/"+str(range(len(self.signalstrengths)))
	print "expr_muavg="+expr_muavg


	for frac in self.fractions:
	    mu = frac.replace("f_","r_")
	    if not self.modelBuilder.out.var(frac):
                self.modelBuilder.doVar(frac+"[1.0,0.,2.]")
		#muall = ""
		#for j in len(range(self.signalstrengths)):
		    #if self.signalstrengths[j]!=mu:
		#    muall += self.signalstrengths[j]
		#    if j!=len(range(self.signalstrengths))-1:
		#	muall += ","
		#print "mu="+mu+" muall="+muall
		#self.modelBuilder.factory_("expr::get_fraction_"+mu+"(\"@0/(@0+@1+@2+@3+@4+@5+@6+@7+@8+@9+@10+@11+@12+@13+@14+@15+@16+@17+@18+@19+@20+@21+@22+@23)\", "+mu+","+murest+")")
		self.modelBuilder.factory_("expr::get_fraction_"+mu+"(\"@0*"+expr_muavg+"\", "+frac+","+muall+")")

	self.modelBuilder.doSet("POI",self.fractions)
'''	
'''	
	cList = ""
	for c in self.wilson:
            if not self.modelBuilder.out.var(c):
                self.modelBuilder.doVar(c+"[0.0,-100.,100.]")
         	cList += c 
		if c!=self.wilson[-1]:
		    cList += ","
                self.modelBuilder.factory_("expr::sme_func"+c+"(\"@0\", "+c+")")

        self.modelBuilder.doSet("POI",cList)

        if len(self.wilson)==1:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0\", "+self.wilson[0]+")")
        if len(self.wilson)==2:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1\", "+self.wilson[0]+","+self.wilson[1]+")")
        if len(self.wilson)==4:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1-@2-@3\", "+self.wilson[0]+","+self.wilson[1]+","+self.wilson[2]+","+self.wilson[3]+")")
        if len(self.wilson)==16:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1-@2-@3-@4-@5-@6-@7-@8-@9-@10-@11-@12-@13-@14-@15\", "+self.wilson[0]+","+self.wilson[1]+","+self.wilson[2]+","+self.wilson[3]+","+self.wilson[4]+","+self.wilson[5]+","+self.wilson[6]+","+self.wilson[7]+","+self.wilson[8]+","+self.wilson[9]+","+self.wilson[10]+","+self.wilson[11]+","+self.wilson[12]+","+self.wilson[13]+","+self.wilson[14]+","+self.wilson[15]+")")
'''

 
multiSignalModelNormed = MultiSignalModelNormed()
#physicsModelNormed = PhysicsModelNormed()
