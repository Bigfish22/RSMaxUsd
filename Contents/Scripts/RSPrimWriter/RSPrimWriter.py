import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom, Sdf
from pxr import UsdLux
from pxr import Gf
import pymxs
import traceback
import os
                                                                            #mesh lights are gonna be weird
LightClasses = ["RectLight", "DiskLight", "SphereLight", "CylinderLight", "Xform", "DomeLightNoXform"]

class RSLightWriter(maxUsd.PrimWriter):

    def GetPrimType(self):
        lightType = LightClasses[self.lightType]
        return lightType

    def Write(self, prim, applyOffset, time):
        try: 
            nodeHandle = self.GetNodeHandle()
            stage = prim.GetStage()
            opts = self.GetExportArgs()
            node = rt.maxOps.getNodeByHandle(nodeHandle)
            
            yUp = True
            
            if prim.GetTypeName() == "DomeLightNoXform":
                lightPrim = UsdLux.DomeLight.Define(stage, prim.GetPath())
                lightPrim.CreateIntensityAttr(node.multiplier)
                lightPrim.CreateExposureAttr(node.tex0_exposure)
            else:
                lightPrim = UsdLux.RectLight(prim)
                lightPrim.CreateIntensityAttr(node.intensity)
                lightPrim.CreateExposureAttr(node.exposure)
                if node.colorMode == 1:
                    lightPrim.CreateEnableColorTemperatureAttr(True)
                lightPrim.CreateColorTemperatureAttr(node.temperature)
            lightPrim.CreateColorAttr((node.color.r/255, node.color.g/255, node.color.b/255))
            
            #can probably do this better
            if prim.GetTypeName() == "RectLight":
                lightPrim.CreateWidthAttr(node.width)
                lightPrim.CreateHeightAttr(node.length)
            elif prim.GetTypeName() == "DiskLight":
                lightPrim = UsdLux.DiskLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
            elif prim.GetTypeName() == "SphereLight":
                lightPrim = UsdLux.SphereLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
            elif prim.GetTypeName() == "CylinderLight":
                lightPrim = UsdLux.CylinderLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
                lightPrim.CreateLengthAttr(node.length)
            elif prim.GetTypeName() == "Xform":
                print("Mesh Light Not Supported Yet")
            elif prim.GetTypeName() == "DomeLight":
                lightPrim = UsdLux.DomeLight(prim)
                hdriImage = node.tex0_filename
                lightPrim.CreateTextureFileAttr(hdriImage)
                
                maxXform = node.transform
                XformAcces = UsdGeom.Xformable(prim) #maybe just make this work for y up...
                xform = XformAcces.AddTransformOp(opSuffix="t1")
                if yUp:
                    lightTransform = Gf.Matrix4d()
                                                 
                xform.Set(lightTransform)
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False

    def GetValidityInterval(self, timeFrame):
        # The base implementation of GetValidityInterval() will return the object's validity interval.
        # So the write() method would only be called when the object changes. 
        # for demonstration purposes, lets force the exporter to call the object's write every frame, 
        # by telling it that what we export at each frame is only valid at that exact frame.
        return maxUsd.Interval(timeFrame,timeFrame)

    @classmethod
    def CanExport(cls, nodeHandle, exportArgs):
        node = rt.maxOps.getNodeByHandle(nodeHandle)
        if rt.classOf(node) == rt.rsPhysicalLight:
            cls.lightType = node.areashape
            return maxUsd.PrimWriter.ContextSupport.Supported
        if rt.classOf(node) == rt.rsDomeLight:
            cls.lightType = 5
            return maxUsd.PrimWriter.ContextSupport.Supported
        return maxUsd.PrimWriter.ContextSupport.Unsupported


class RSProxyWriter(maxUsd.PrimWriter):
    def GetPrimType(self):
        return "RedshiftProxy"

    def Write(self, prim, applyOffset, time):
        try: 
            nodeHandle = self.GetNodeHandle()
            stage = prim.GetStage()
            opts = self.GetExportArgs()
            node = rt.maxOps.getNodeByHandle(nodeHandle)
            
            
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_file", Sdf.ValueTypeNames.String).Set(node.file.replace(os.sep, "/"))
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrID", Sdf.ValueTypeNames.Bool).Set(node.overrideobjectid)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTess", Sdf.ValueTypeNames.Bool).Set(node.overridetessdisp)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTraceS", Sdf.ValueTypeNames.Bool).Set(node.overridetracesets)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrUserDat", Sdf.ValueTypeNames.Bool).Set(node.overrideuserdata)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrVis", Sdf.ValueTypeNames.Bool).Set(node.overridevisibility)
            
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False

    @classmethod
    def CanExport(cls, nodeHandle, exportArgs):
        node = rt.maxOps.getNodeByHandle(nodeHandle)
        if rt.classOf(node) == rt.RedshiftProxy:
            return maxUsd.PrimWriter.ContextSupport.Supported
        return maxUsd.PrimWriter.ContextSupport.Unsupported
   


maxUsd.PrimWriter.Register(RSLightWriter, "RSLightWriter")
maxUsd.PrimWriter.Register(RSProxyWriter, "RSProxyWriter")
   
