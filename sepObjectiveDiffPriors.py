import os.path
import numpy as np
import matplotlib.pyplot as plt
import scipy
import refnx
from refnx.dataset import ReflectDataset, Data1D
from refnx.analysis import Transform, CurveFitter, Objective, Model, Parameter#, GlobalObjective
from refnx.reflect import SLD, Slab, ReflectModel
print('refnx: %s\nscipy: %s\nnumpy: %s' % (refnx.version.version,
                   scipy.version.version, np.version.version))

class variable:
    def __init__(self, startPoint, lower, upper, roughness=None, vary=True):
        self.startPoint=float(startPoint)
        self.lower=float(lower)
        self.upper=float(upper)
        if (None==roughness):
            roughness=0
        self.roughness=roughness
#         print("... ", self.roughness)
        self.vary=float(vary)



def getObjective(data, thicknesses, slds, layerNames, logpExtra=None):

    air = SLD(0,name="air layer")
    airSlab = air(10,0)
    sio2 = SLD(10,name="bottem layer")
    sio2Slab = sio2(10,0)
    
#     print(" ... ",slds[0].startPoint)
    if len(layerNames)>=1:
        i=0
        sld1 = SLD(float(slds[i].startPoint),name=layerNames[i])
        sld1Slab = sld1(thicknesses[i].startPoint, thicknesses[i].roughness)
        sld1Slab.thick.setp(vary=thicknesses[i].vary, bounds=(thicknesses[i].lower,thicknesses[i].upper))
        sld1Slab.sld.real.setp(vary=slds[i].vary, bounds=(slds[i].lower,slds[i].upper))
    else:
        print(layerNames, " : variable 'layerNames' is empty")

    if len(layerNames)>=2:
        i=1
        sld2 = SLD(slds[i].startPoint,name=layerNames[i])
        sld2Slab = sld2(thicknesses[i].startPoint, thicknesses[i].roughness)
        sld2Slab.thick.setp(vary=thicknesses[i].vary, bounds=(thicknesses[i].lower,thicknesses[i].upper))
        sld2Slab.sld.real.setp(vary=slds[i].vary, bounds=(slds[i].lower,slds[i].upper))

    if len(layerNames)>=3:
        i=2
        sld3 = SLD(slds[i].startPoint,name=layerNames[i])
        sld3Slab = sld3(thicknesses[i].startPoint, thicknesses[i].roughness)
        sld3Slab.thick.setp(vary=thicknesses[i].vary, bounds=(thicknesses[i].lower,thicknesses[i].upper))
        sld3Slab.sld.real.setp(vary=slds[i].vary, bounds=(slds[i].lower,slds[i].upper))

    if len(layerNames)>=4:
        i=3
        sld4 = SLD(slds[i].startPoint,name=layerNames[i])
        sld4Slab = sld4(thicknesses[i].startPoint, thicknesses[i].roughness)
        sld4Slab.thick.setp(vary=thicknesses[i].vary, bounds=(thicknesses[i].lower,thicknesses[i].upper))
        sld4Slab.sld.real.setp(vary=slds[i].vary, bounds=(slds[i].lower,slds[i].upper))

    if len(layerNames)==1:
        structure = airSlab|sld1Slab|sio2Slab
    if len(layerNames)==2:
        structure = airSlab|sld1Slab|sld2Slab|sio2Slab
    if len(layerNames)==3:
        structure = airSlab|sld1Slab|sld2Slab|sld3Slab|sio2Slab
    if len(layerNames)==4:
        structure = airSlab|sld1Slab|sld2Slab|sld3Slab|sld4Slab|sio2Slab
    model = ReflectModel(structure, bkg=3e-6, dq=5.0)
    objective = Objective(model, data,
              transform=Transform('logY'),
              logp_extra=logpExtra)
    return objective, structure