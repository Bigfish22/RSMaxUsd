import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom, Sdf, UsdVol
from pxr import UsdLux
from pxr import Gf
import pymxs
import usd_utils
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
                    prim.CreateAttribute('redshift:light:RSL_visible', Sdf.ValueTypeNames.Bool).Set(node.areavisible)
                    prim.CreateAttribute('redshift:light:RSL_bidirectional', Sdf.ValueTypeNames.Bool).Set(node.areabidirectional)
                    prim.CreateAttribute('redshift:light:RSL_spread', Sdf.ValueTypeNames.Float).Set(node.areaspread)
                    lightPrim.CreateNormalizeAttr().Set(node.areanormalize)
                    if node.colorMode == 1:
                        lightPrim.CreateEnableColorTemperatureAttr(True)
                    WriteProperty(lightPrim.CreateColorTemperatureAttr(), node, "temperature", usdTime)
                WritePropertyColor(lightPrim.CreateColorAttr(), node, "color", usdTime)
                
                lightPrim.CreateDiffuseAttr().Set(node.diffusescale)
                lightPrim.CreateSpecularAttr().Set(node.reflectionscale)
                
                #can probably do this better
                if prim.GetTypeName() == "RectLight":
                    WriteProperty(lightPrim.CreateWidthAttr(), node, "width", usdTime)
                    WriteProperty(lightPrim.CreateHeightAttr(),node, "length", usdTime)
                elif prim.GetTypeName() == "DiskLight":
                    lightPrim = UsdLux.DiskLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(), node, "width", usdTime)
                elif prim.GetTypeName() == "SphereLight":
                    lightPrim = UsdLux.SphereLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(), node, "width", usdTime)
                elif prim.GetTypeName() == "CylinderLight":
                    lightPrim = UsdLux.CylinderLight(prim)
                    WriteProperty(lightPrim.CreateRadiusAttr(), node, "width", usdTime)
                    WriteProperty(lightPrim.CreateLengthAttr(), node, "length", usdTime)
                    lightPrim.AddRotateZOp().Set(90)
                elif prim.GetTypeName() == "Xform":
                    print("Mesh Light Not Supported Yet")
                elif prim.GetTypeName() == "DomeLight":
                    lightPrim = UsdLux.DomeLight(prim)
                    hdriImage = node.tex0_filename
                    lightPrim.CreateTextureFileAttr(usd_utils.safe_relpath(hdriImage,os.path.dirname(self.GetFilename())))
                    
                    lightPrim.AddRotateYOp().Set(node.rotation.angle + 90)
                    lightPrim.AddTransformOp(opSuffix="t1").Set(Gf.Matrix4d())
            if prim.GetTypeName() != "DomeLight":        
                prim.CreateAttribute('redshift:light:RSL_matteShadow', Sdf.ValueTypeNames.Bool).Set(node.matteshadowilluminator)
                prim.CreateAttribute('redshift:light:RSL_affectedByRefraction', Sdf.ValueTypeNames.Int).Set(node.affectedbyrefraction)
                prim.CreateAttribute('redshift:light:RSL_indirectMaxTraceDepth', Sdf.ValueTypeNames.Int).Set(node.indirectmaxtracedepth)
                prim.CreateAttribute('redshift:light:RSL_transmissionScale', Sdf.ValueTypeNames.Float).Set(node.transmissionscale)
                prim.CreateAttribute('redshift:light:RSL_sssScale', Sdf.ValueTypeNames.Float).Set(node.singlescatteringscale)
                prim.CreateAttribute('redshift:light:RSL_multisssScale', Sdf.ValueTypeNames.Float).Set(node.multiplescatteringscale)
                prim.CreateAttribute('redshift:light:RSL_indirectScale', Sdf.ValueTypeNames.Float).Set(node.indirectscale)
                prim.CreateAttribute('redshift:light:RSL_volumeScale', Sdf.ValueTypeNames.Float).Set(node.volumecontributionscale)
                prim.CreateAttribute('redshift:light:RSL_volumeSamples', Sdf.ValueTypeNames.Int).Set(node.volumesamples)
                if node.aovLightGroup:
                    prim.CreateAttribute('redshift:light:RSL_lightGroup', Sdf.ValueTypeNames.String).Set(node.aovLightGroup)
                prim.CreateAttribute('redshift:light:RSL_samples', Sdf.ValueTypeNames.Int).Set(node.areasamples)
                prim.CreateAttribute('redshift:light:RSL_emitCausticPhotons', Sdf.ValueTypeNames.Bool).Set(node.causticphotonemit)
                prim.CreateAttribute('redshift:light:RSL_causticIntensity', Sdf.ValueTypeNames.Float).Set(node.causticphotonmultiplier)
                prim.CreateAttribute('redshift:light:RSL_causticPhotons', Sdf.ValueTypeNames.Int).Set(node.causticphotoncount)
                #prim.CreateAttribute('redshift:light:RSL_emitGIPhotons', Sdf.ValueTypeNames.Bool).Set(node.  ???
                #prim.CreateAttribute('redshift:light:RSL_giIntensity', Sdf.ValueTypeNames.Float).Set(node.   ???
                #prim.CreateAttribute('redshift:light:RSL_giPhotons', Sdf.ValueTypeNames.Int).Set(node.       ???
                prim.CreateAttribute('redshift:light:RSL_softnessAffectsGobo', Sdf.ValueTypeNames.Int).Set(node.softnessAffectsGobo)
                prim.CreateAttribute('redshift:light:SetEnableLegacyNonAreaLightIntensity', Sdf.ValueTypeNames.Bool).Set(node.legacyNonAreaLightIntensity)
                prim.CreateAttribute('redshift:light:SetEnableLegacySoftShadowTechnique', Sdf.ValueTypeNames.Bool).Set(node.legacySoftShadowTechnique)
                
                prim.CreateAttribute('redshift:light:unitsType', Sdf.ValueTypeNames.Int).Set(node.unitsType)
                prim.CreateAttribute('redshift:light:lumensperwatt', Sdf.ValueTypeNames.Float).Set(node.lumensperwatt)
                
                
                #lightLinking
                WriteLightLinking(node, prim, self.GetNodesToPrims())
                
            return True

        except Exception as e:
            print('Write - Error: %s' % str(e))
            print(traceback.format_exc())
            return False

    def GetValidityInterval(self, timeFrame):
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
            
            WriteLightLinking(node, prim, self.GetNodesToPrims())
            
            return True
            
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False

    def GetValidityInterval(self, timeFrame):
        return maxUsd.Interval(timeFrame,timeFrame)
            
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
            
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_file", Sdf.ValueTypeNames.String).Set(node.file)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrID", Sdf.ValueTypeNames.Bool).Set(node.overrideobjectid)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTess", Sdf.ValueTypeNames.Bool).Set(node.overridetessdisp)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrTraceS", Sdf.ValueTypeNames.Bool).Set(node.overridetracesets)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrUserDat", Sdf.ValueTypeNames.Bool).Set(node.overrideuserdata)
            prim.CreateAttribute("primvars:redshift:object:RS_objprop_proxy_ovrVis", Sdf.ValueTypeNames.Bool).Set(node.overridevisibility)
            
            
            return True

        except Exception as e:
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
            
            filePath = node.file
            startframe = node.startframe
            endframe = node.endframe
            pattern = node.pattern
            frameoffset = node.frameoffset
            
            volumePrim = UsdVol.Volume(prim)
            for grid in node.grids:
                vdbAsset = UsdVol.OpenVDBAsset.Define(stage, (prim.GetPath().AppendPath(grid)))
                vdbFilePath = usd_utils.safe_relpath(node.file, os.path.dirname(self.GetFilename()))
                filePathAttr = vdbAsset.CreateFilePathAttr(vdbFilePath)
                if node.issequence:
                    for i in range(startframe, endframe + 1):
                        frameIndex = i + frameoffset
                        fileName = pattern % frameIndex
                        fullFramePath = usd_utils.safe_relpath(os.path.join(os.path.dirname(filePath), fileName), os.path.dirname(self.GetFilename()))
                        filePathAttr.Set(fullFramePath, i)
                vdbAsset.CreateFieldNameAttr(grid)
                vdbAsset.CreateFieldIndexAttr(0)
                volumePrim.CreateFieldRelationship(grid, vdbAsset.GetPath())
            
            return True
   
        except Exception as e:
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

def WriteLightLinking(node, prim, nodesToPrims):
    lightPrim = UsdLux.LightAPI(prim)
    lightCollection = lightPrim.GetLightLinkCollectionAPI()
    shadowCollection = lightPrim.GetShadowLinkCollectionAPI()
    
    #Illumination
    if node.inclExclType == 1 or node.inclExclType == 3:
        if node.includeList != None:
            includeRel = lightCollection.CreateIncludesRel()
            lightCollection.CreateIncludeRootAttr().Set(False)
            for object in node.includeList:
                sdfPath = nodesToPrims[object.handle]
                includeRel.AddTarget(sdfPath)
        elif node.excludeList != None:
            excludeRel = lightCollection.CreateExcludesRel()
            for object in node.excludeList:
                sdfPath = nodesToPrims[object.handle]
                excludeRel.AddTarget(sdfPath)
    #Shadows
    if node.inclExclType == 2 or node.inclExclType == 3:
        if node.includeList != None:
            includeRel = shadowCollection.CreateIncludesRel()
            shadowCollection.CreateIncludeRootAttr().Set(False)
            for object in node.includeList:
                sdfPath = nodesToPrims[object.handle]
                includeRel.AddTarget(sdfPath)
        elif node.excludeList != None:
            excludeRel = shadowCollection.CreateExcludesRel()
            for object in node.excludeList:
                sdfPath = nodesToPrims[object.handle]
                excludeRel.AddTarget(sdfPath)


maxUsd.PrimWriter.Register(RSLightWriter, "RSLightWriter")
maxUsd.PrimWriter.Register(RSSunWriter, "RSSunWriter")
maxUsd.PrimWriter.Register(RSProxyWriter, "RSProxyWriter")
maxUsd.PrimWriter.Register(RSVolumeWriter, "RSVolumeWriter")
   
