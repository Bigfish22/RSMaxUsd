
import maxUsd
from pxr import Usd, Sdf
from pymxs import runtime as rt
import traceback

#Displacement
rsModifierProps = {"autoBumpMap": "primvars:redshift:object:RS_objprop_displace_autob",
                    "enableDisplacement": "primvars:redshift:object:RS_objprop_displace_enabl",
                    "maxDisplacement": "primvars:redshift:object:RS_objprop_displace_max",
                    "displacementScale": "primvars:redshift:object:RS_objprop_displace_scale",
                    #Tessalation
                    "enableSubdivision": "primvars:redshift:object:RS_objprop_rstess_enable",
                    "limitOutOfFrustumTessellation": "primvars:redshift:object:RS_objprop_rstess_looft",
                    "maxOutOfFrustumTessellationSubdivs": "primvars:redshift:object:RS_objprop_rstess_looftSubd",
                    "maxTessellationSubdivs": "primvars:redshift:object:RS_objprop_rstess_maxsubd",
                    "minTessellationLength": "primvars:redshift:object:RS_objprop_rstess_melenght",
                    "outOfFrustumTessellationFactor": "primvars:redshift:object:RS_objprop_rstess_ooftf",
                    "subdivisionRule": "primvars:redshift:object:RS_objprop_rstess_rule",
                    "doSmoothUVBoundaries": "primvars:redshift:object:RS_objprop_rstess_smoothBound",
                    "doSmoothSubdivision": "primvars:redshift:object:RS_objprop_rstess_smoothsub",
                    "screenSpaceAdaptive": "primvars:redshift:object:RS_objprop_rstess_ssadaptive"}

#matte
rsObjectProps = {"RS_MATTE_AFFECTEDBYMATTELIGHTS": "primvars:redshift:object:RS_objprop_matte_abyml",
                "RS_MATTE_ALPHA": "primvars:redshift:object:RS_objprop_matte_alpha",
                "RS_MATTE_APPLYTOSECONDARYRAYS": "primvars:redshift:object:RS_objprop_matte_applysec",
                "RS_MATTE_DIFFUSESCALE": "primvars:redshift:object:RS_objprop_matte_diffscale",
                "RS_MATTE_ENABLE": "primvars:redshift:object:RS_objprop_matte_enable",
                "RS_MATTE_INCLUDEINPUZZLEMATTE": "primvars:redshift:object:RS_objprop_matte_includePM",
                "RS_MATTE_REFLECTIONSCALE": "primvars:redshift:object:RS_objprop_matte_reflscale",
                "RS_MATTE_REFRACTIONSCALE": "primvars:redshift:object:RS_objprop_matte_refrscale",
                "RS_MATTE_SHADOWAFFECTSALPHA": "primvars:redshift:object:RS_objprop_matte_shadowalpha",
                "RS_MATTE_SHADOWCOLOR": "primvars:redshift:object:RS_objprop_matte_shadowcolor",
                "RS_MATTE_ENABLESHADOW": "primvars:redshift:object:RS_objprop_matte_shadowenable",
                "RS_MATTE_RECEIVESHADOWSFROMMATTES": "primvars:redshift:object:RS_objprop_matte_shadowsFromM",
                "RS_MATTE_SHADOWTRANSARENCY": "primvars:redshift:object:RS_objprop_matte_shadowtrans",
                "RS_MATTE_SHOWBACKGROUND": "primvars:redshift:object:RS_objprop_matte_showbackg",
                #object properties
                "RS_VIS_AOCASTER": "primvars:redshift:object:MESHFLAG_AOCASTER",
                "RS_VIS_CAUSTICCASTER": "primvars:redshift:object:MESHFLAG_CAUSTICCASTER",
                "RS_VIS_CAUSTICSRECEIVER": "primvars:redshift:object:MESHFLAG_CAUSTICSRECEIVER",
                "RS_VIS_CAUSTICVISIBLE": "primvars:redshift:object:MESHFLAG_CAUSTICVISIBLE",
                "RS_VIS_FGCASTER": "primvars:redshift:object:MESHFLAG_FGCASTER",
                "RS_VIS_FGVISIBLE": "primvars:redshift:object:MESHFLAG_FGVISIBLE",
                "RS_VIS_FORCEBRUTEFORCEGI": "primvars:redshift:object:MESHFLAG_FORCEBRUTEFORCEGI",
                "RS_VIS_SELFSHADOWS": "primvars:redshift:object:MESHFLAG_NOSELFSHADOW",
                "RS_VIS_PRIMARYRAYVISIBLE": "primvars:redshift:object:MESHFLAG_PRIMARYRAYVISIBLE",
                "RS_VIS_REFLECTIONCASTER": "primvars:redshift:object:MESHFLAG_REFLECTIONCASTER",
                "RS_VIS_REFLECTIONVISIBLE": "primvars:redshift:object:MESHFLAG_REFLECTIONVISIBLE",
                "RS_VIS_REFRACTIONCASTER": "primvars:redshift:object:MESHFLAG_REFRACTIONCASTER",
                "RS_VIS_REFRACTIONVISIBLE": "primvars:redshift:object:MESHFLAG_REFRACTIONVISIBLE",
                "RS_VIS_SECONDARYRAYVISIBLE": "primvars:redshift:object:MESHFLAG_SECONDARYRAYVISIBLE",
                "RS_VIS_SHADOWCASTER": "primvars:redshift:object:MESHFLAG_SHADOWCASTER",
                "RS_VIS_SHADOWRECEIVER": "primvars:redshift:object:MESHFLAG_SHADOWRECEIVER"}

rsCameraProps = {"optical":{
                    # MB parameters
                    'motionBlur':'redshift:camera:RS_campro_mb',
                    'cameraMotion':'redshift:camera:RS_campro_mbCamera',
                    'shutterEfficiency':'redshift:camera:RS_campro_mbEfficiency',
                    'shutterType':'redshift:camera:RS_campro_mbShutterType',
                    'shutterTime':'redshift:camera:RS_campro_mbTimeSec',
                    'shutterAngle':'redshift:camera:RS_campro_mbTimeAngle',
                    'shutterTimeOffset':'redshift:camera:RS_campro_mbOffsetSec',
                    'shutterAngleOffset':'redshift:camera:RS_campro_mbOffsetAngle',
                    # DOF parameters
                    'bokeh':'redshift:camera:RS_campro_dofEnable',
                    'focusDeriveFromCamera' :'redshift:camera:RS_campro_dofUseHoudiniCamera',
                    'focusDistance':'redshift:camera:RS_campro_dofDistance',
                    #'redshift:camera:RS_campro_dofCoC'
                    #'redshift:camera:RS_campro_dofPower'
                    #'redshift:camera:RS_campro_dofApect'
                    'bokehBlades':'redshift:camera:RS_campro_dofBladesCount',
                    'bokehAngle':'redshift:camera:RS_campro_dofBladesAngle',
                    #'redshift:camera:RS_campro_dofBokehNorm'
                    'bokehImage_filename':'redshift:camera:RS_campro_dofBokehImage',
                    #'focusObject':'redshift:camera:RS_campro_dofObject',
                    'focusObjectOffset':'redshift:camera:RS_campro_dofObjectOffset',
                    'fStop':'redshift:camera:RS_campro_dofAperture',
                    #'redshift:camera:RS_campro_dofDiaphragm'
                    # Photographic exposure parameters
                    'toneMapEnabled':'redshift:camera:RS_campro_PyCamEnable',
                    'iso':'redshift:camera:RS_campro_PyCamISO',
                    'shutterTime':'redshift:camera:RS_campro_PyCamShutter',
                    'fStop':'redshift:camera:RS_campro_PyCamfstop',
                    'whitepoint':'redshift:camera:RS_campro_PyCamWPoint',
                    'vignetting':'redshift:camera:RS_campro_PyCamVignetting',
                    'highlights':'redshift:camera:RS_campro_PyCamOverExp',
                    'desaturateHighlights':'redshift:camera:RS_campro_PyCamAllowDesat',
                    'blacksThreshold':'redshift:camera:RS_campro_PyCamCrushT',
                    'blacks':'redshift:camera:RS_campro_PyCamCrushA',
                    'saturation':'redshift:camera:RS_campro_PyCamSaturation',
                    'exposureType':'redshift:camera:RS_campro_PyCamExposureType',
                    'exposure':'redshift:camera:RS_campro_PyCamExposureEV',
                    # Lens distortion parameters
                    'distortion':'redshift:camera:RS_campro_distortionEnable',
                    'distortionImage_filename':'redshift:camera:RS_campro_distortionImage'},
                "lut":{
                    'enabled':'redshift:camera:RS_campro_enablePFX',
                    #'redshift:camera:RS_campro_applyPFX'
                    'enabled':'redshift:camera:RS_campro_lutEnable',
                    'filename':'redshift:camera:RS_campro_lutFile',
                    'apply_before_color_management':'redshift:camera:RS_campro_lutBeforeCM',
                    'log_input':'redshift:camera:RS_campro_lutIsLog',
                    'strength':'redshift:camera:RS_campro_lutStrength'},
                "colorControl":{
                    'enabled':'redshift:camera:RS_campro_colorEnable',
                    'exposure':'redshift:camera:RS_campro_colorExposure',
                    'contrast':'redshift:camera:RS_campro_colorContrast'},
                "bloom":{
                    'enabled':'redshift:camera:RS_campro_bloomEnable',
                    'threshold':'redshift:camera:RS_campro_bloomThreshold',
                    'softness':'redshift:camera:RS_campro_bloomSoftness',
                    'intensity':'redshift:camera:RS_campro_bloomIntensity',
                    'tint0':'redshift:camera:RS_campro_bloomTint1',
                    'tint1':'redshift:camera:RS_campro_bloomTint2',
                    'tint2':'redshift:camera:RS_campro_bloomTint3',
                    'tint3':'redshift:camera:RS_campro_bloomTint4',
                    'tint4':'redshift:camera:RS_campro_bloomTint5'},
                "flare":{
                    'enabled':'redshift:camera:RS_campro_flareEnable',
                    'threshold':'redshift:camera:RS_campro_flareThreshold',
                    'softness':'redshift:camera:RS_campro_flareSoftness',
                    'chromatic':'redshift:camera:RS_campro_flareChromatic',
                    'size':'redshift:camera:RS_campro_flareSize',
                    'halo':'redshift:camera:RS_campro_flareHalo',
                    'intensity':'redshift:camera:RS_campro_flareIntensity',
                    'tint0':'redshift:camera:RS_campro_flareTint1',
                    'tint1':'redshift:camera:RS_campro_flareTint2',
                    'tint2':'redshift:camera:RS_campro_flareTint3',
                    'tint3':'redshift:camera:RS_campro_flareTint4',
                    'tint4':'redshift:camera:RS_campro_flareTint5',
                    'tint5':'redshift:camera:RS_campro_flareTint6'},
                "streak":{
                    'enabled':'redshift:camera:RS_campro_streakEnable',
                    'threshold':'redshift:camera:RS_campro_streakThreshold',
                    'tail':'redshift:camera:RS_campro_streakTail',
                    'softness':'redshift:camera:RS_campro_streakSoftness',
                    'number':'redshift:camera:RS_campro_streakNumber',
                    'angle':'redshift:camera:RS_campro_streakAngle',
                    'intensity':'redshift:camera:RS_campro_streakIntensity'}
}

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Color3f}

class RSObjectPropertiesChaser(maxUsd.ExportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        super(RSObjectPropertiesChaser, self).__init__(factoryContext, *args, **kwargs)
        self.primsToNodeHandles = factoryContext.GetPrimsToNodeHandles()
        #self.nodeHandlesToPrims = dict((v, k) for k, v in self.primsToNodeHandles.items())

        # retrieve the USD stage being written to
        self.stage = factoryContext.GetStage()
        
    def PostExport(self):
        try:
            for prim_path, node_handle in self.primsToNodeHandles.items():
                node = rt.maxOps.getNodeByHandle(node_handle)
                prim = self.stage.GetPrimAtPath(prim_path)
                
                #Handle writing mesh params
                for mod in node.modifiers:
                    if rt.classOf(mod) == rt.RedshiftMeshParams:
                        for prop in rsModifierProps:
                            value = getattr(mod, prop)
                            type = rt.classOf(value)
                            prim.CreateAttribute(rsModifierProps[prop], maxTypeToSdf[type]).Set(self.resolveValue(value, type))
                    elif rt.classOf(mod) == rt.RedshiftCameraAttributes:
                        for section in rsCameraProps:
                            subSection = getattr(mod, section)
                            for prop in rsCameraProps[section]:
                                value = getattr(subSection, prop)
                                type = rt.classOf(value)
                                try:
                                    prim.CreateAttribute(rsCameraProps[section][prop], maxTypeToSdf[type]).Set(self.resolveValue(value, type))
                                except:
                                    print("something weird on camera is broken")

                        diaphragm = ['circular','bladed','image']
                        prim.CreateAttribute('redshift:camera:RS_campro_dofDiaphragm', Sdf.ValueTypeNames.String).Set(diaphragm[mod.optical.bokehShape])
                        
                        focusObject = mod.optical.focusObject
                        if focusObject:
                            handle = rt.getHandleByAnim(focusObject)
                
                #write user props if they exist
                for prop in rsObjectProps:
                    userProp = rt.getUserPropVal(node, prop)
                    if userProp is rt.undefined:
                        continue
                    type = rt.classOf(userProp)
                    prim.CreateAttribute(rsObjectProps[prop], maxTypeToSdf[type]).Set(self.resolveValue(userProp, type))
                    
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        
        return True
        
    def resolveValue(self, value, type):
        if type == rt.Color:
            return (value.r/255, value.g/255, value.b/255)
        if type == rt.point3:
            return (value[0], value[1], value[2])
        else:
            return value
            

maxUsd.ExportChaser.Register(RSObjectPropertiesChaser, "RSObjectProperties", "Redshift object Properties", "Chaser to export RS Object properties")