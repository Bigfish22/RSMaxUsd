import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom
from pxr import UsdLux
from pxr import Gf
import pymxs
import traceback
                                                                            #mesh lights are gonna be weird
LightClasses = ["RectLight", "DiskLight", "SphereLight", "CylinderLight", "RectLight", "DomeLight"]

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
            
            lightPrim = UsdLux.RectLight(prim)
            
            if self.lightType == 5:
                lightPrim.CreateIntensityAttr(node.multiplier)
                lightPrim.CreateExposureAttr(node.tex0_exposure)
            else:
                lightPrim.CreateIntensityAttr(node.intensity)
                lightPrim.CreateExposureAttr(node.exposure)
                if node.colorMode == 1:
                    lightPrim.CreateEnableColorTemperatureAttr(True)
                lightPrim.CreateColorTemperatureAttr(node.temperature)
            lightPrim.CreateColorAttr((node.color.r/255, node.color.g/255, node.color.b/255))
            
            #can probably do this better
            if self.lightType == 0:
                lightPrim.CreateWidthAttr(node.width)
                lightPrim.CreateHeightAttr(node.length)
            elif self.lightType == 1:
                lightPrim = UsdLux.DiskLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
            elif self.lightType == 2:
                lightPrim = UsdLux.SphereLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
            elif self.lightType == 3:
                lightPrim = UsdLux.CylinderLight(prim)
                lightPrim.CreateRadiusAttr(node.width)
                lightPrim.CreateLengthAttr(node.length)
            elif self.lightType == 4:
                print("Mesh Light Not Supported Yet")
            elif self.lightType == 5:
                lightPrim = UsdLux.DomeLight(prim)
                hdriImage = node.tex0_filename
                lightPrim.CreateTextureFileAttr(hdriImage)
        
                XformAcces = UsdGeom.Xformable(prim)
                Flip = XformAcces.AddRotateXZYOp(opSuffix="axisChange")
                Flip.Set(value = (90, 90, 0))
            
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

   
# Register the writer.
# First argument is the class, second argument is the Writer name, which will be used as an ID internaly.
maxUsd.PrimWriter.Register(RSLightWriter, "RSLightWriter")