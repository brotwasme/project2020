import os.path
import numpy as np
import matplotlib.pyplot as plt
import scipy
import refnx
from refnx.dataset import ReflectDataset, Data1D
from refnx.analysis import Transform, CurveFitter, Objective, GlobalObjective, Model, Parameter
from refnx.reflect import SLD, Slab, ReflectModel
print('refnx: %s\nscipy: %s\nnumpy: %s' % (refnx.version.version,
                   scipy.version.version, np.version.version))

def getObjective(data, nLayers, bs_contrast_layer=None,
                 contrast_layer=None,
                 limits = None, doMCMC=False,
                 logpExtra=None, onlyStructure=False,
                 both=False, globalObjective=False):

    if globalObjective:
        if bs_contrast_layer is None:
            bs_contrast_layer = 6
        if contrast_layer is None:
            contrast_layer = 1
#         print("data, nLayers, bs_contrast_layer=None,\n contrast_layer=None,\nlimits = None, doMCMC=False,\nlogpExtra=None, onlyStructure=False,\nboth=False, globalObjective=False: ",
#                      data, nLayers, bs_contrast_layer,
#                      contrast_layer,
#                      limits, doMCMC,
#                      logpExtra, onlyStructure,
#                      both, globalObjective)

    air = SLD(0,name="air layer")
    airSlab = air(10,0)

    sio2 = SLD(10,name="bottem layer")
    sio2Slab = sio2(10,0)


    if limits is None:
        limits = [350,50,4,6]
    
#     maxThick = 350
#     lowerThick = 50
#     upperThick = maxThick - nLayers*lowerThick
#     lowerB = 4
#     upperB = 6

    maxThick = float(limits[0])
    lowerThick = limits[1]
    upperThick = maxThick - nLayers*lowerThick
    lowerB = limits[2]
    upperB = limits[3]

    if globalObjective:
        thick_contrast_layer=Parameter(maxThick/nLayers,
                                        "layer1 thickness")
        rough_contrast_layer=Parameter(0,
                                    "layer0/contrast roughness")
        sldcontrastA=SLD(5,name="contrast A layer")
        sldcontrastASlab= sldcontrastA(thick_contrast_layer,rough_contrast_layer)
        sldcontrastASlab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sldcontrastASlab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

        sldcontrastB=SLD(5,name="contrast B layer")
        sldcontrastBSlab = sldcontrastB(thick_contrast_layer,rough_contrast_layer)
        sldcontrastBSlab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sldcontrastBSlab.sld.real.setp(vary=True, bounds=(lowerB,upperB))


    if nLayers>=1 and not globalObjective:
        sld1 = SLD(5,name="first layer")
        sld1Slab = sld1(maxThick/nLayers,0)
        sld1Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sld1Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

    if nLayers>=2:
        sld2 = SLD(5,name="second layer")
        sld2Slab = sld2(maxThick/nLayers,0)
        sld2Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sld2Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

    if nLayers>=3:
        sld3 = SLD(5,name="third layer")
        sld3Slab = sld3(maxThick/nLayers,0)
        sld3Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sld3Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

    if nLayers>=4:
        sld4 = SLD(5,name="forth layer")
        sld4Slab = sld4(maxThick/nLayers,0)
        sld4Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
        sld4Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

#     if nLayers>=1:
#         sld1Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
#         sld1Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

#     if nLayers>=2:
#         sld2Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
#         sld2Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

#     if nLayers>=3:
#         sld3Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
#         sld3Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

#     if nLayers>=4:
#         sld4Slab.thick.setp(vary=True, bounds=(lowerThick,upperThick))
#         sld4Slab.sld.real.setp(vary=True, bounds=(lowerB,upperB))

    if globalObjective and contrast_layer==1:
        if nLayers==1:
            structure1 = airSlab|sldcontrastASlab|sio2Slab
            structure2 = airSlab|sldcontrastBSlab|sio2Slab
        if nLayers==2:
            structure1 = airSlab|sldcontrastASlab|sld2Slab|sio2Slab
            structure2 = airSlab|sldcontrastBSlab|sld2Slab|sio2Slab
        if nLayers==3:
            structure1 = airSlab|sldcontrastASlab|sld2Slab|sld3Slab|sio2Slab
            structure2 = airSlab|sldcontrastBSlab|sld2Slab|sld3Slab|sio2Slab
        if nLayers==4:
            structure1 = airSlab|sldcontrastASlab|sld2Slab|sld3Slab|sld4Slab|sio2Slab
            structure2 = airSlab|sldcontrastBSlab|sld2Slab|sld3Slab|sld4Slab|sio2Slab
        if onlyStructure:
            returns = structure1,structure2
        elif both:
            model1 = ReflectModel(structure1, bkg=3e-6, dq=5.0)
            model1.scale.setp(bounds=(0.85, 1.2), vary=True)
            model1.bkg.setp(bounds=(1e-9, 9e-6), vary=True)
            objective1 = Objective(model1, data[0],
                      transform=Transform('logY'),
                      logp_extra=logpExtra)
            model2 = ReflectModel(structure2, bkg=3e-6, dq=5.0)
            model2.scale.setp(bounds=(0.85, 1.2), vary=True)
            model2.bkg.setp(bounds=(1e-9, 9e-6), vary=True)
            objective2 = Objective(model2, data[1],
                      transform=Transform('logY'),
                      logp_extra=logpExtra)
            returns = GlobalObjective([objective1, objective2]), structure1, structure2
            print("GlobalObjective and 2 structures")
        else:
            model1 = ReflectModel(structure1, bkg=3e-6, dq=5.0)
            model1.scale.setp(bounds=(0.85, 1.2), vary=True)
            model1.bkg.setp(bounds=(1e-9, 9e-6), vary=True)
            objective1 = Objective(model1, data[0],
                      transform=Transform('logY'),
                      logp_extra=logpExtra)
            model2 = ReflectModel(structure2, bkg=3e-6, dq=5.0)
            model2.scale.setp(bounds=(0.85, 1.2), vary=True)
            model2.bkg.setp(bounds=(1e-9, 9e-6), vary=True)
            objective2 = Objective(model2, data[1],
                      transform=Transform('logY'),
                      logp_extra=logpExtra)
            returns = GlobalObjective([objective1, objective2])

    elif not globalObjective:
        if nLayers==1:
            structure = airSlab|sld1Slab|sio2Slab
        if nLayers==2:
            structure = airSlab|sld1Slab|sld2Slab|sio2Slab
        if nLayers==3:
            structure = airSlab|sld1Slab|sld2Slab|sld3Slab|sio2Slab
        if nLayers==4:
            structure = airSlab|sld1Slab|sld2Slab|sld3Slab|sld4Slab|sio2Slab
        if onlyStructure:
            returns = structure
        elif both:
            model = ReflectModel(structure, bkg=3e-6, dq=5.0)
            objective = Objective(model, data,
                      transform=Transform('logY'),
                      logp_extra=logpExtra)
            returns = objective, structure
        else:
            model = ReflectModel(structure, bkg=3e-6, dq=5.0)
            objective = Objective(model, data, transform=Transform('logY'),logp_extra=logpExtra)
            returns = objective
    else:
        print("error contrast layer not at sld1Slab ie contrast_layer!=0")
#     print(returns)
    return returns

