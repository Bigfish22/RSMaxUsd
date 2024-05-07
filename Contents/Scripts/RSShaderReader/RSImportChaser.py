import maxUsd
from pxr import Usd, Sdf
from pymxs import runtime as rt
import traceback

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

class RSImportChaser(maxUsd.ImportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        super(RSImportChaser, self).__init__(factoryContext, *args, **kwargs)

        self.primsToNodeHandles = factoryContext.GetPrimsToNodeHandles()

        self.stage = factoryContext.GetStage()
        
    def PostImport(self):
        try:
            for prim_path, node_handle in self.primsToNodeHandles.items():
                node = rt.maxOps.getNodeByHandle(node_handle)
                prim = self.stage.GetPrimAtPath(prim_path)
                
                #RS Mesh Params
                tessAttr = prim.GetAttribute("primvars:redshift:object:RS_objprop_rstess_enable")
                dispAttr = prim.GetAttribute("primvars:redshift:object:RS_objprop_displace_enabl")
                if tessAttr or dispAttr:
                    meshParams = rt.RedshiftMeshParams()
                    rt.addModifier(node, meshParams)
                    
                    for property in rsModifierProps:
                        attr = prim.GetAttribute(rsModifierProps[property])
                        if attr:
                            rt.setProperty(meshParams, property, attr.Get())
                #Vis/Matte    
                for prop in rsObjectProps:
                    attr = prim.GetAttribute(rsObjectProps[prop])
                    if attr:
                        rt.setUserPropVal(node, prop, attr.Get())


        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        return True


maxUsd.ImportChaser.Register(RSImportChaser, "RSImportChaser", "Import RS object properties", "Import RS object properties")