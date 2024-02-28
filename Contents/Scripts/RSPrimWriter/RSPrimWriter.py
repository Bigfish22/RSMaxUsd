import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom, Sdf, UsdVol
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
            
            usdTime = time.GetUsdTime()
            maxTime = time.GetMaxTime()
            
            yUp = True
            with pymxs.attime(maxTime):
                if prim.GetTypeName() == "DomeLightNoXform":
                    lightPrim = UsdLux.DomeLight.Define(stage, prim.GetPath())
                    WriteProperty(lightPrim.CreateIntensityAttr(), node, "multiplier", usdTime)
                    WriteProperty(lightPrim.CreateExposureAttr(), node, "tex0_exposure", usdTime)
                else:
                    lightPrim = UsdLux.RectLight(prim)
                    WriteProperty(lightPrim.CreateIntensityAttr(), node, "intensity", usdTime)
                    WriteProperty(lightPrim.CreateExposureAttr(), node, "exposure", usdTime)
                    if node.colorMode == 1:
                        lightPrim.CreateEnableColorTemperatureAttr(True)
                    WriteProperty(lightPrim.CreateColorTemperatureAttr(), node, "temperature", usdTime)
                WritePropertyColor(lightPrim.CreateColorAttr(), node, "color", usdTime)
                
                #can probably do this better
                if prim.GetTypeName() == "RectLight":
                    WriteProperty(lightPrim.CreateWidthAttr(), node, "width", usdTime)
                    WriteProperty(lightPrim.CreateHeightAttr(),node, "length", usdTime)
                elif prim.GetTypeName() == "DiskLight":
                    lightPrim = UsdLux.DiskLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(). node, "width", usdTime)
                elif prim.GetTypeName() == "SphereLight":
                    lightPrim = UsdLux.SphereLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(), node, "width", usdTime)
                elif prim.GetTypeName() == "CylinderLight":
                    lightPrim = UsdLux.CylinderLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(), node, "width", usdTime)
                    WriteProperty(lightPrim.CreateLengthAttr(), node, "length", usdTime)
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


class RSSunWriter(maxUsd.PrimWriter):
    def GetPrimType(self):
        return "DistantLight"
        
    def Write(self, prim, applyOffset, time):
        try:
            nodeHandle = self.GetNodeHandle()
            stage = prim.GetStage()
            opts = self.GetExportArgs()
            node = rt.maxOps.getNodeByHandle(nodeHandle)
            
            usdTime = time.GetUsdTime()
            maxTime = time.GetMaxTime()
            
            lightPrim = UsdLux.DistantLight(prim)
            with pymxs.attime(maxTime):
                WriteProperty(lightPrim.CreateIntensityAttr(), node, "intensity", usdTime)
            
            if rt.classOf(rt.environmentMap) == rt.rsPhysicalSky:
                if rt.environmentMap.sun_node == node:
                    prim.CreateAttribute("redshift:light:sunSkyLight", Sdf.ValueTypeNames.Bool).Set(rt.useEnvironmentMap) #just incase somebody wants there settings but its disabled at the time.
            
            return True
            
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
            
    @classmethod
    def CanExport(cls, nodeHandle, exportArgs):
        node = rt.maxOps.getNodeByHandle(nodeHandle)
        if rt.classOf(node) == rt.rsSunLight:
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
        
class RSVolumeWriter(maxUsd.PrimWriter):
    def GetPrimType(self):
        return "Volume"
        
    def Write(self, prim, applyOffset, time):
        try: 
            nodeHandle = self.GetNodeHandle()
            stage = prim.GetStage()
            opts = self.GetExportArgs()
            node = rt.maxOps.getNodeByHandle(nodeHandle)
            
            volumePrim = UsdVol.Volume(prim)
            for grid in node.grids:
                vdbAsset = UsdVol.OpenVDBAsset.Define(stage, (prim.GetPath().AppendPath(grid)))
                vdbAsset.CreateFilePathAttr(node.file)
                vdbAsset.CreateFieldNameAttr(grid)
                vdbAsset.CreateFieldIndexAttr(0)
                volumePrim.CreateFieldRelationship(grid, vdbAsset.GetPath())
            
            return True
   
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
            
    @classmethod
    def CanExport(cls, nodeHandle, exportArgs):
        node = rt.maxOps.getNodeByHandle(nodeHandle)
        if rt.classOf(node) == rt.RedshiftVolumeGrid:
            return maxUsd.PrimWriter.ContextSupport.Supported
        return maxUsd.PrimWriter.ContextSupport.Unsupported


def WriteProperty(usdAttribute, maxNode, maxProperty, usdTime):
    if rt.getPropertyController(maxNode, maxProperty):
        usdAttribute.Set(getattr(maxNode, maxProperty), usdTime)
    else:
        usdAttribute.Set(getattr(maxNode, maxProperty))
        
def WritePropertyColor(usdAttribute, maxNode, maxProperty, usdTime):
    if rt.getPropertyController(maxNode, maxProperty):
        value = getattr(maxNode, maxProperty)
        usdAttribute.Set((value.r/255, value.g/255, value.b/255), usdTime)
    else:
        value = getattr(maxNode, maxProperty)
        usdAttribute.Set((value.r/255, value.g/255, value.b/255))


maxUsd.PrimWriter.Register(RSLightWriter, "RSLightWriter")
maxUsd.PrimWriter.Register(RSSunWriter, "RSSunWriter")
maxUsd.PrimWriter.Register(RSProxyWriter, "RSProxyWriter")
maxUsd.PrimWriter.Register(RSVolumeWriter, "RSVolumeWriter")
   
