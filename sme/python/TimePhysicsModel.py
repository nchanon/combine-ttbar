
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
        self.wilson = ''
        self.process = ''

    def setPhysicsOptions(self,physOptions):
        for po in physOptions:
            for c in wilson_list:
                if c in po:
                    print 'wilson coefficient : '+c
                    self.process = c
                    self.wilson = c



    def setModelBuilder(self, modelBuilder):
        PhysicsModel.setModelBuilder(self,modelBuilder)

    def getYieldScale(self,bin,process):
        if process == self.process: 
            return "sme_func"
        elif process == "signal":
            return "bkd_func"
        else:
            return 1
            
    def doParametersOfInterest(self):

        if not self.modelBuilder.out.var(self.wilson):
            self.modelBuilder.doVar(self.wilson+"[0.0,-5.,5.]")
        
        
        self.modelBuilder.factory_("expr::sme_func(\"@0\", "+self.wilson+")")
        #self.modelBuilder.factory_( "expr::sig_func(\"@0-sqrt(@0)\", "+self.wilson+")")
        self.modelBuilder.factory_( "expr::bkd_func(\"1-@0\", "+self.wilson+")")
        
        
        self.modelBuilder.doSet("POI",self.wilson)
        
timeModel = TimeModel()
