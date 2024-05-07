import maxUsd
import usd_utils
from pymxs import runtime as rt
from pxr import UsdShade, Sdf, Gf
import usd_utils
import traceback
import os
import re

valueMapping = {"diffuseColor"  :"base_color",
            "metallic"         :"metalness",
            "specularcolor"    :"refl_color",
            "roughness"        :"refl_roughness",
            "emissiveColor"    :"emission_color",
            "ior"              :"refl_ior",
            "clearcoat"        :"coat_weight",
            "clearcoatRoughness":"coat_roughness"}
            
textureMapping = {"diffuseColor" :{"maxProp" :"base_color_map", "channel" : "rgb"},
            "metallic"     :{"maxProp" :"metalness_map", "channel" : "r"},
            "specularColor":{"maxProp" :"refl_color_map", "channel" : "rgb"},
            "roughness"    :{"maxProp" :"refl_roughness_map", "channel" : "r"},
            "normal"       :{"maxProp" :"bump_input", "channel" : "rgb"},
            "emissiveColor":{"maxProp" :"emission_color_map", "channel" : "rgb"},
            "ior"          :{"maxProp" :"refl_ior_map", "channel" : "r"},
            "clearcoat"    :{"maxProp" :"coat_weight_map", "channel" : "r"},
            "clearcoatRoughness":{"maxProp" :"coat_roughness_map", "channel" : "r"}}

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Float3,
                rt.StandardUVGen : Sdf.ValueTypeNames.Token,
                rt.BitMap : Sdf.ValueTypeNames.Token}

class RSPreviewWriter(maxUsd.ShaderWriter):
    def Write(self):
        try:
            material = rt.GetAnimByHandle(self.GetMaterial())

            nodeShader = UsdShade.Shader.Define(self.GetUsdStage(), self.GetUsdPath())
            nodeShader.CreateIdAttr("UsdPreviewSurface")
            
            for usdProp, valueName in valueMapping.items():
                value = rt.getProperty(material, valueName)
                type = rt.classOf(value)
                if type == rt.color:
                    value = Gf.Vec3f(value.r/255, value.g/255, value.b/255)
                if usdProp == "emissiveColor":
                    value = value * material.emission_weight
                nodeShader.CreateInput(usdProp, maxTypeToSdf[type]).Set(value)
            
            for usdProp, data in textureMapping.items():
                map = rt.getProperty(material, data["maxProp"])
                if rt.classOf(map) == rt.rsTexture or rt.classOf(map) == rt.rsBitmap:
                    mapPrim = self.AddTexture(nodeShader, data["maxProp"], material)
                    nodeShader.CreateInput(usdProp, Sdf.ValueTypeNames.Token).ConnectToSource(mapPrim.ConnectableAPI(), data["channel"])
                elif rt.classOf(map) == rt.rsBumpMap:
                    mapPrim = self.AddTexture(nodeShader, "Input_map", map)
                    nodeShader.CreateInput(usdProp, Sdf.ValueTypeNames.Token).ConnectToSource(mapPrim.ConnectableAPI(), data["channel"])
            
            self.SetUsdPrim(nodeShader.GetPrim())
            return True

        except Exception as e:
            print('Write - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def AddTexture(self, prim, property, parentNode):
        node = getattr(parentNode, property)
        primName = node.name.replace(" ", "_").replace("#", "_")
        filePath = node.tex0_filename
        filePath = re.sub("1[0-9]{3}", "<UDIM>", filePath)
        filePath = usd_utils.safe_relpath(filePath, os.path.dirname(self.GetFilename()))
        texturePrim = UsdShade.Shader.Define(self.GetUsdStage(), self.GetUsdPath().GetParentPath().AppendPath(primName))
        texturePrim.CreateIdAttr("UsdUVTexture")
        texturePrim.CreateInput("file", Sdf.ValueTypeNames.Asset).Set(filePath)
        
        texturePrim.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
        texturePrim.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
        
        colorSpace = 'Auto'
        if node.tex0_colorspace == "sRGB":
            colorSpace = "sRGB"
        elif node.tex0_colorspace == "Raw":
            colorSpace = "Raw"
            
        texturePrim.CreateInput("sourceColorSpace", Sdf.ValueTypeNames.Token).Set(colorSpace)
        
        
        primVarReadPrim = UsdShade.Shader.Define(self.GetUsdStage(), self.GetUsdPath().GetParentPath().AppendPath(primName + "_primvar_float2"))
        primVarReadPrim.CreateIdAttr("UsdPrimvarReader_float2")
        primVarReadPrim.CreateInput("varname", Sdf.ValueTypeNames.String).Set("st")
        
        texturePrim.CreateInput("st", Sdf.ValueTypeNames.Token).ConnectToSource(primVarReadPrim.ConnectableAPI(), "result")
        
        return texturePrim
            
    @classmethod
    def CanExport(cls, exportArgs):
        if exportArgs.GetConvertMaterialsTo() == "UsdPreviewSurface":
            return maxUsd.ShaderWriter.ContextSupport.Supported
        return maxUsd.ShaderWriter.ContextSupport.Unsupported

maxUsd.ShaderWriter.Register(RSPreviewWriter, "RS Standard Material")