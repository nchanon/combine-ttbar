
wilson_list = [
    'cLXX',
    'cRXX',
    'cXX',
    'dXX',
    'cLXY',
    'cRXY',
    'cXY',
    'dXY',
    'cLXZ',
    'cRXZ',
    'cXZ',
    'dXZ',
    'cLYZ',
    'cRYZ',
    'cYZ',
    'dYZ'
]

from HiggsAnalysis.CombinedLimit.PhysicsModel import *

### This is the base python class to study the Higgs width

class TimeModel(PhysicsModel):
    def __init__(self):
        self.wilson = []
        self.process = []

    def setPhysicsOptions(self,physOptions):
        for po in physOptions:
            for c in wilson_list:
                if c in po:
                    print 'wilson coefficient : '+c
                    self.process.append(c)
                    self.wilson.append(c)

	#self.process.append("cLXX")
        #self.wilson.append("cLXX")



    def setModelBuilder(self, modelBuilder):
        PhysicsModel.setModelBuilder(self,modelBuilder)

    def getYieldScale(self,bin,process):
	for c in self.process:
            if process == c: 
                return ("sme_func"+c)

	#if process=="cLXX":
	#    return ("sme_funccLXX")

	if process == "signal":
            return "bkd_func"
	elif process.find("XX")!=-1 or process.find("XY")!=-1 or process.find("XZ")!=-1 or process.find("YZ")!=-1:
	    return 0
        else:
            return 1
            
    def doParametersOfInterest(self):
	
	cList = ""
	for c in self.wilson:
            if not self.modelBuilder.out.var(c):
                self.modelBuilder.doVar(c+"[0.0,-100.,100.]")
         	cList += c 
		if c!=self.wilson[-1]:
		    cList += ","
                self.modelBuilder.factory_("expr::sme_func"+c+"(\"@0\", "+c+")")

        #self.modelBuilder.factory_( "expr::sme_funccLXX(\"1-@0\", cLXX)")
	#self.modelBuilder.doVar("cLXX[0.0,-10.,10.]")
        
	#self.modelBuilder.doSet("POI","cLXX")
        self.modelBuilder.doSet("POI",cList)

        if len(self.wilson)==1:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0\", "+self.wilson[0]+")")
        if len(self.wilson)==2:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1\", "+self.wilson[0]+","+self.wilson[1]+")")
        if len(self.wilson)==4:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1-@2-@3\", "+self.wilson[0]+","+self.wilson[1]+","+self.wilson[2]+","+self.wilson[3]+")")
        if len(self.wilson)==16:
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0-@1-@2-@3-@4-@5-@6-@7-@8-@9-@10-@11-@12-@13-@14-@15\", "+self.wilson[0]+","+self.wilson[1]+","+self.wilson[2]+","+self.wilson[3]+","+self.wilson[4]+","+self.wilson[5]+","+self.wilson[6]+","+self.wilson[7]+","+self.wilson[8]+","+self.wilson[9]+","+self.wilson[10]+","+self.wilson[11]+","+self.wilson[12]+","+self.wilson[13]+","+self.wilson[14]+","+self.wilson[15]+")")


 
timeModel = TimeModel()
