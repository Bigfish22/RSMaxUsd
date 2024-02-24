import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom, UsdLux
from pxr import Gf as pyGf
import pymxs
import traceback


class RSLightReader(maxUsd.PrimReader):

    def Read(self):
        try: 
            usdPrim = self.GetUsdPrim()
            lightType = usdPrim.GetTypeName()
            
            parentHandle = self.GetJobContext().GetNodeHandle(usdPrim.GetPath().GetParentPath(), False)
            if (parentHandle):
                node = rt.rsPhysicalLight()
                node.parent = rt.GetAnimByHandle(parentHandle)
            else:
                node = rt.rsPhysicalLight()
                
            lightPrim = UsdLux.RectLight(usdPrim)
            node.intensity = lightPrim.GetIntensityAttr().Get()
            node.exposure = lightPrim.GetExposureAttr().Get()
            if lightPrim.GetEnableColorTemperatureAttr().Get():
                node.colorMode = 1
                node.temperature = lightPrim.GetColorTemperatureAttr().Get()
            else:
                lightColor = lightPrim.GetColorAttr().Get()
                node.color = rt.point4(lightColor[0], lightColor[1], lightColor[2], 1)
                
            if lightType == "RectLight":
                node.width= lightPrim.GetWidthAttr().Get()
                node.length= lightPrim.GetHeightAttr().Get()
            elif lightType == "DiskLight":
                lightPrim = UsdLux.DiskLight(usdPrim)
                node.areaShape = 1
                node.width = lightPrim.GetRadiusAttr().Get()
            elif lightType == "SphereLight":
                lightPrim = UsdLux.SphereLight(usdPrim)
                node.areaShape = 2
                node.width = lightPrim.GetRadiusAttr().Get()
            elif lightType == "CylinderLight":
                lightPrim = UsdLux.CylinderLight(usdPrim)
                node.areaShape = 3
                node.width = lightPrim.GetRadiusAttr().Get()
                node.length = lightPrim.GetLengthAttr().Get()

            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            self.ReadXformable()
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Read() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
            
    @classmethod
    def CanImport(cls, args, prim):
        #Need to check if we are in a redshift import context.
        return maxUsd.PrimReader.ContextSupport.Supported
        
class RSDomeReader(maxUsd.PrimReader):
    def Read(self):
        try: 
            usdPrim = self.GetUsdPrim()
            lightType = usdPrim.GetTypeName()
            node = rt.rsDomeLight()
        
            parentHandle = self.GetJobContext().GetNodeHandle(usdPrim.GetPath().GetParentPath(), False)
            if (parentHandle):
                node.parent = rt.GetAnimByHandle(parentHandle)
            
            lightPrim = UsdLux.DomeLight(usdPrim)
            node.multiplier = lightPrim.GetIntensityAttr().Get()
            node.tex0_exposure = lightPrim.GetExposureAttr().Get()
            node.tex0_filename = lightPrim.GetTextureFileAttr(hdriImage).Get()

            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            self.ReadXformable()
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Read() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
            
    @classmethod
    def CanImport(cls, args, prim):
        #Need to check if we are in a redshift import context.
        return maxUsd.PrimReader.ContextSupport.Supported


class RSProxyPrimReader(maxUsd.PrimReader):
    '''
    Prim reader for rs proxy into max
    '''

    @classmethod
    def CanImport(cls, args, prim):
        return maxUsd.PrimReader.ContextSupport.Supported

    def Read(self):
        try: 
            usdPrim = self.GetUsdPrim()
            node = rt.RedshiftProxy()
            node.name = usdPrim.GetName()
            
            node.file = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_file").Get()
            node.overrideobjectid = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_ovrID").Get()
            node.overridetessdisp = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTess").Get()
            node.overridetracesets = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTraceS").Get()
            node.overrideuserdata = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_ovrUserDat").Get()
            node.overridevisibility = usdPrim.GetAttribute("primvars:redshift:object:RS_objprop_proxy_ovrVis").Get()
            
            
            parentHandle = self.GetJobContext().GetNodeHandle(usdPrim.GetPath().GetParentPath(), False)
            if (parentHandle):
                parent=rt.GetAnimByHandle(parentHandle)

            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            self.ReadXformable()
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Read() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
   


maxUsd.PrimReader.Register(RSLightReader, "UsdLuxRectLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxDiskLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxSphereLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxCylinderLight")
maxUsd.PrimReader.Register(RSDomeReader, "DomeLight")

maxUsd.PrimReader.Register(RSProxyPrimReader, "UsdRedshiftProxy")