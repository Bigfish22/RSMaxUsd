import maxUsd
from pymxs import runtime as rt
from pxr import UsdGeom, UsdLux, UsdVol, UsdShade, Ar
import usd_utils
import pymxs
import traceback
import RSShaderReader


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
                node.areaShape = 0
                node.colorMode = 1
                node.temperature = lightPrim.GetColorTemperatureAttr().Get()
            else:
                lightColor = lightPrim.GetColorAttr().Get()
                node.color = rt.point4(lightColor[0]*255, lightColor[1]*255, lightColor[2]*255, 1)
                
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
            node.tex0_filename = lightPrim.GetTextureFileAttr().Get().path

            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            #self.ReadXformable()
            
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
   
   
class RSSunSkyReader(maxUsd.PrimReader):
    def Read(self):
        try:
            usdPrim = self.GetUsdPrim()
            node = rt.rsSunLight()
            node.name = usdPrim.GetName()
            
            node.targeted = False
            
            #Basic light values
            lightPrim = UsdLux.DistantLight(usdPrim)
            node.intensity = lightPrim.GetIntensityAttr().Get()
            
            
            #Build physical sky
            SkyAttribute = usdPrim.GetAttribute("redshift:light:sunSkyLight")
            if SkyAttribute:
                if SkyAttribute.Get():
                    PhysicalSky = rt.rsPhysicalSky()
                    sun_node = node
                    
                    #Set all the sky properties on the light/and physical sky
                    
                    rt.environmentMap = PhysicalSky
            
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
                node.parent=rt.GetAnimByHandle(parentHandle)
            
            material = UsdShade.MaterialBindingAPI(usdPrim).ComputeBoundMaterial()
            if material[0]:
                print(material)
            #    materialPath = material[0].GetPath().AppendPath("redshift_usd_material").AppendPath("redshift_usd_material1")
            #    #materialHandle = self.GetJobContext().GetNodeHandle(, False)
            #    #node.material = rt.getAnimByHandle(materialHandle)
            #    print(materialPath)
            #    #print(materialHandle)
            #    #print(node.material)
                
            
            
            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            self.ReadXformable()
            
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Read() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
   
   
class RSVolumeReader(maxUsd.PrimReader):
    @classmethod
    def CanImport(cls, args, prim):
        return maxUsd.PrimReader.ContextSupport.Supported
        
    def Read(self):
        try:
            usdPrim = self.GetUsdPrim()
            node = rt.RedshiftVolumeGrid()
            node.name = usdPrim.GetName()
            
            UsdVolume = UsdVol.Volume(usdPrim)
            gridDict = UsdVolume.GetFieldPaths()
            for grid in gridDict:
                VdbPrim = UsdVol.OpenVDBAsset(usdPrim.GetStage().GetPrimAtPath(gridDict[grid]))
                node.file = ResolveAsset(VdbPrim.GetFilePathAttr().Get().path)
                break
                
            parentHandle = self.GetJobContext().GetNodeHandle(usdPrim.GetPath().GetParentPath(), False)
            if (parentHandle):
                node.parent=rt.GetAnimByHandle(parentHandle)
                
            try:
                material = UsdShade.MaterialBindingAPI(usdPrim).ComputeBoundMaterial()
                if material[0]:
                    redshift_usd_mat = material[0].GetSurfaceOutput("Redshift").GetConnectedSources()[0][0].source.GetPrim()
                    if redshift_usd_mat.GetTypeName() == "NodeGraph":
                        usdAttribute = redshift_usd_mat.GetAttribute("outputs:shader")
                        Connections = usdAttribute.GetConnections()
                        redshift_usd_mat = redshift_usd_mat.GetPrimAtPath(Connections[0].GetPrimPath())
                    reader = RSShaderReader.RSShaderReaderBase()
                    materialHandle = reader.Read(redshift_usd_mat)
                    
                    node.material = rt.getAnimByHandle(materialHandle)
            except:
                print("Failed to import volume shader")
            
            
            self.GetJobContext().RegisterCreatedNode(usdPrim.GetPath(), rt.GetHandleByAnim(node))
            self.ReadXformable()
            
            return True
            
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Read() - Error: %s' % str(e))
            print(traceback.format_exc())
            return False


def ResolveAsset(assetPath):
    resolver = Ar.GetResolver()
    resolvedPath = resolver.Resolve(assetPath)
    return str(resolvedPath)

maxUsd.PrimReader.Register(RSLightReader, "UsdLuxRectLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxDiskLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxSphereLight")
maxUsd.PrimReader.Register(RSLightReader, "UsdLuxCylinderLight")
maxUsd.PrimReader.Register(RSDomeReader, "UsdLuxDomeLight")
maxUsd.PrimReader.Register(RSSunSkyReader, "UsdLuxDistantLight")

maxUsd.PrimReader.Register(RSProxyPrimReader, "UsdRedshiftProxy")

maxUsd.PrimReader.Register(RSVolumeReader, "UsdVolVolume")
