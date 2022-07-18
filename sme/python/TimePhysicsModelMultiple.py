
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



    def setModelBuilder(self, modelBuilder):
        PhysicsModel.setModelBuilder(self,modelBuilder)

    def getYieldScale(self,bin,process):
	for c in self.process:
            if process == c: 
                return "sme_func"

	if process == "signal":
            return "bkd_func"
        else:
            return 1
            
    def doParametersOfInterest(self):
	
	for c in self.wilson:
            if not self.modelBuilder.out.var(c):
                self.modelBuilder.doVar(c+"[0.0,-5.,5.]")
        
            self.modelBuilder.factory_("expr::sme_func(\"@0\", "+c+")")
            #self.modelBuilder.factory_( "expr::sig_func(\"@0-sqrt(@0)\", "+self.wilson+")")
            self.modelBuilder.factory_( "expr::bkd_func(\"1-@0\", "+c+")")
        
        
            self.modelBuilder.doSet("POI",c)
        
timeModel = TimeModel()
