# Copyright 2024 Benjamin Mikhaiel

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

USERELATIVEPATHING = True #TODO: expose as a setting

import maxUsd
import usd_utils
import pymxs
from pymxs import runtime as rt
from pxr import UsdShade, Sdf, Gf, Vt
import RSPreviewWriter
import usd_utils
import traceback
import os
import re
import json

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.Color_RGBA : Sdf.ValueTypeNames.Color4f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Float3,
                rt.StandardUVGen : Sdf.ValueTypeNames.Token,
                rt.BitMap : Sdf.ValueTypeNames.Token,
                rt.point2 : Sdf.ValueTypeNames.Float2,
                rt.material : Sdf.ValueTypeNames.Token}
                                    

#Key: maxClass : [Houdini/core Name, Output Pin Name(if the node has multi outputs, we can get this from max]
maxShaderToRS = {}
with open(os.path.dirname(os.path.abspath(__file__)) + "/classList.json", "r") as classList:
    classJson = json.load(classList)
    for classStr, list in classJson.items():
        if hasattr(rt, classStr):
            maxShaderToRS[getattr(rt, classStr)] = list
                    
PropertyRemaps = {rt.rsOSLMap : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'},
                  rt.rsOSLMaterial : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'},
                  rt.rsTexture: {"scale_x" : "scale", "scale_y": "scale", "offset_x" : "offset", "offset_y" : "offset", "tex0_colorspace" : "tex0_colorSpace", "tex0_filename" : "tex0"},
                  rt.rsSprite : {"tex0_filename" : "tex0", "repeats_x" : "repeats", "repeats_y" : "repeats"},
                  rt.rsBitmap : {"tex0_colorspace" : "tex0_colorSpace", "tex0_filename" : "tex0"}}


class RSShaderWriter(maxUsd.ShaderWriter):
    def Write(self):
        try:
            self.nodeTranslators = {rt.CompositeMap: self.NodeTranslateComposite,
                                    rt.Gradient_Ramp : self.NodeTranslateGradientRamp,
                                    rt.VertexColor : self.NodeTranslateVertexColor}
            if hasattr(rt, "ForestColor"): #just incase forest doesn't exist
                self.nodeTranslators[getattr(rt, "ForestColor")] = self.NodeTranslateForestColor
                                        
            #if its targetting a different file we need this for relative pathing
            stage = self.GetUsdStage()
            targetLayer = stage.GetEditTarget().GetLayer()
            self.outputFile = self.GetFilename()
            if not targetLayer.anonymous:
                self.outputFile = targetLayer.identifier
            
            material = rt.GetAnimByHandle(self.GetMaterial())
            isMultiTarget = len(self.GetExportArgs().GetAllMaterialConversions()) > 1
            
            exportSettings = self.GetExportArgs() #TODO: Get animation start, end and interval, for getting animated values from properties
            self.startTime = exportSettings.GetStartFrame()
            self.endTime   = exportSettings.GetEndFrame()
            self.timeStep  = exportSettings.GetSamplesPerFrame()
            self.animationMode = exportSettings.GetTimeMode()
            
            
            surfaceShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath("redshift_usd_material1"))
            surfaceShader.CreateIdAttr("redshift_usd_material")
            
            if isMultiTarget:
                nodeGraphPassthrough = UsdShade.NodeGraph.Get(self.GetUsdStage(), (self.GetUsdPath()).GetParentPath())
                materialPrim = UsdShade.Material.Get(self.GetUsdStage(), (self.GetUsdPath()).GetParentPath().GetParentPath())
                materialPrim.CreateSurfaceOutput('Redshift').ConnectToSource(nodeGraphPassthrough.ConnectableAPI(), "shader")
                nodeGraphPassthrough.CreateOutput('shader', Sdf.ValueTypeNames.Token).ConnectToSource(surfaceShader.ConnectableAPI(), "shader")
            else:
                materialPrim = UsdShade.Material.Get(self.GetUsdStage(), (self.GetUsdPath()).GetParentPath())
                materialPrim.CreateSurfaceOutput('Redshift').ConnectToSource(surfaceShader.ConnectableAPI(), "shader")
            
            if rt.classOf(material) == rt.rsMaterialOutput:
                nodeShader = surfaceShader
            else:
                nodeShader = UsdShade.Shader.Define(self.GetUsdStage(), (self.GetUsdPath()))
                nodeShader.CreateIdAttr("redshift::" + maxShaderToRS[rt.classOf(material)][0])
            
            if rt.classOf(material) == rt.rsVolume or rt.classOf(material) == rt.rsStandardVolume:
                surfaceShader.CreateInput('Volume', Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), "outColor")
            elif rt.classOf(material) == rt.rsOslMaterial:
                surfaceShader.CreateInput('Surface', Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), material.oslClosureOutput)
            elif rt.classOf(material) != rt.rsMaterialOutput:
                surfaceShader.CreateInput('Surface', Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), "outColor")
            
            
            templateDef = rt.classOf(material)
            templateClass = templateDef()
            for property in rt.getPropNames(material):
                self.AddProperty(nodeShader, material, property, templateClass)
                self.AddShader(nodeShader, material, property)
            self.AddDisplacement(material, surfaceShader)
            return True

        except Exception as e:
            print('Write - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def TypeOf(self, prop, value, template):
        type = rt.classOf(value)
        if type == rt.Color:
            try:
                rt.setPropertyController(template, prop,  rt.Color_RGBA())
                return rt.Color_RGBA
            except:
                return type
        return type

    def AddProperty(self, prim, node, prop, template):
        if(str(prop).endswith(("_map","_mapamount", "_mapenable", "_enable", "_input"))):
            return
        
        nodeClass = rt.ClassOf(node)
        
        value = getattr(node, str(prop))
        animated = False
        if rt.getPropertyController(node, str(prop)):
            animated = True
        if not ((nodeClass == rt.rsOSLMap) or (nodeClass == rt.rsOSLMaterial)):
            if value == getattr(template, str(prop)) and not animated:
                return #The property is still at its defualt value and it is not animated, so we can just skip doing anything with it
            
        type = self.TypeOf(prop, value, template)
        if not (type in maxTypeToSdf):
            rt.UsdExporter.Log(rt.Name("warn"), (str(prop) + "has unsupported type conversion" + str(type)))
            return
            
        
        value = self.ResolveValue(prim, type, value, prop, node)
        if value is None:
            return
            
        sdfType = maxTypeToSdf[self.type]
        
        propertyName = str(prop)
        if nodeClass in PropertyRemaps:
            if str(prop) in PropertyRemaps[nodeClass]:
                propertyName = PropertyRemaps[nodeClass][str(prop)]
                
        inputAttribute = prim.CreateInput(propertyName, sdfType)
        if not animated or self.animationMode == maxUsd.TimeMode.CurrentFrame:
            inputAttribute.Set(value)
        else:
            currentStep = self.startTime
            while currentStep < self.endTime:
                with pymxs.attime(currentStep):
                    value = getattr(node, str(prop))
                value = self.ResolveValue(prim, type, value, prop, node)
                inputAttribute.Set(value, currentStep)
                currentStep += 1 / self.timeStep
    
    def ResolveValue(self, prim, type, value, prop, node):
        self.type = type
        if type == rt.Color:
            value = (value.r/255, value.g/255, value.b/255)
        if type == rt.Color_RGBA:
            value = (value.r/255, value.g/255, value.b/255, value.a/255)
        elif type == rt.point3:
            value = Gf.Vec3f(value.x, value.y, value.z)
        elif type == rt.string:
            self.ResolveString(prim, value, prop, node)
            value = None
        elif type == rt.StandardUVGen:
            self.ResolveUVGen(prim, value)
            value = None
        elif type == rt.BitMap:
            value = None
        elif (rt.classof(node) == rt.rsTexture or rt.rsSprite) and str(prop).endswith(('_x', '_y')):
            value = Gf.Vec2f(getattr(node, str(prop)[:-2] + '_x'), getattr(node, str(prop)[:-2] + '_y'))
            self.type = rt.point2
        return value
            
    def ResolveString(self, prim, value, prop, node):
        nodeClass = rt.classOf(node)
        if nodeClass in PropertyRemaps:
            if str(prop) in PropertyRemaps[nodeClass]:
                    propertyName = PropertyRemaps[nodeClass][str(prop)]
            else:
                propertyName = str(prop)
        else:
            propertyName = str(prop)
            
        if re.search("\....$", value):
            assetPath = self.RelativeAssetPath(value)
            if propertyName == "tex0":
                try:  #sprites dont have tiling mode, classic stitch up there
                    if getattr(node, "tilingmode") == 1:
                        assetPath = re.sub("1[0-9]{3}", "<UDIM>", assetPath)
                except:
                    pass
                prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)
                return
            prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)
        else:
            prim.CreateInput(propertyName, Sdf.ValueTypeNames.String).Set(value)

    
    def ResolveUVGen(self, prim, value):
        prim.CreateInput("scale", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(value.U_Tiling, value.V_Tiling))
        prim.CreateInput("rotate", Sdf.ValueTypeNames.Float).Set(value.W_Angle)
        prim.CreateInput("offset", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(value.U_Offset, value.V_Offset))
        
    def AddShader(self, parentPrim, parentNode, prop, propertyOverride = None, nodeOverride = None):
        
        #some node translators might need to provide a specific max node, instead of just the property
        if nodeOverride is not None:
            maxShader = nodeOverride
        else:
            maxShader = getattr(parentNode, str(prop))
        
        #if we have nothing return early
        if rt.superClassOf(maxShader) not in ((rt.textureMap, rt.material)):
            return
        
        #do we even support this? if not return early, log to the user.
        maxClass = rt.classOf(maxShader)
        if not (maxClass in maxShaderToRS):
            rt.UsdExporter.Log(rt.Name("warn"), (str(maxClass) + "is not supported, this node and any children will be skipped!"))
            return
            
        #this section handles if we need a full custom function to handle this node, because it needs bulk translation work.
        if maxClass in self.nodeTranslators:
            if propertyOverride != None:  
                self.nodeTranslators[maxClass](parentPrim, parentNode, maxShader, propertyOverride)
            else:
                self.nodeTranslators[maxClass](parentPrim, parentNode, maxShader, str(prop))
            return
        
        #multiOutput swizzling chaos
        outPutName = maxShaderToRS[maxClass][1]
        if maxClass == rt.MultiOutputChannelTexmapToTexmap:
            outPutName = maxShader.sourcemap.getIMultipleOutputChannelName(maxShader.outputChannelIndex)
            maxShader = maxShader.sourceMap
            maxClass = rt.classOf(maxShader)
        elif maxClass == rt.rsOSLMap:  #catch for osl maps with a single output, multi output ones will be caught above ^
            outPutName = maxShader.getIMultipleOutputChannelName(1)
        elif maxClass == rt.rsOSLMaterial:  #catch for osl maps with a single output, multi output ones will be caught above ^
            outPutName = maxShader.oslClosureOutput
        
        
        primName = maxShader.name.replace(" ", "_").replace("#", "_")
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        usdShader.CreateIdAttr("redshift::" + maxShaderToRS[maxClass][0])
        
        #Theres is a pretty good chance this could break on some shader property name somewhere
        tidyProperty = self.CleanMapProperty(str(prop))
        
        if tidyProperty == "bump_input":
            parentSdfType = Sdf.ValueTypeNames.Int
        elif propertyOverride is not None:
            tidyProperty = propertyOverride
            parentSdfType = Sdf.ValueTypeNames.Token
        elif not (hasattr(parentNode, tidyProperty)):
            parentSdfType = Sdf.ValueTypeNames.Int
        elif rt.superClassOf(getattr(parentNode, tidyProperty)) == rt.textureMap:
            parentSdfType = Sdf.ValueTypeNames.Token
        elif rt.superClassOf(getattr(parentNode, tidyProperty)) == rt.material:
            parentSdfType = Sdf.ValueTypeNames.Token
        elif hasattr(parentNode, tidyProperty):
            parentPropertyType = rt.classOf(getattr(parentNode, tidyProperty))
            parentSdfType = maxTypeToSdf[parentPropertyType]
        else:
            parentSdfType = Sdf.ValueTypeNames.Token
        
        parentPrim.CreateInput(tidyProperty, parentSdfType).ConnectToSource(usdShader.ConnectableAPI(), outPutName)
        
        
        templateDef = maxClass
        templateClass = templateDef()
        for shaderProperty in rt.getPropNames(maxShader):
                self.AddProperty(usdShader, maxShader, shaderProperty, templateClass)
                self.AddShader(usdShader, maxShader, shaderProperty)
        
    def RelativeAssetPath(self, path):
        if USERELATIVEPATHING:
            relPath = rt.pathConfig.convertPathToAbsolute(path)
            relPath = usd_utils.safe_relpath(relPath, os.path.dirname(self.outputFile))
        else:
            relPath = path
        return relPath.replace(os.sep, "/")
    
    def CleanMapProperty(self, prop):
        tidyProperty = prop.replace("_map", "")
        tidyProperty = tidyProperty[0].lower() + tidyProperty[1:] #were not even going to talk about this
        if tidyProperty in (('surface', 'volume', 'contour', 'displacement', 'bumpMap', 'environment')):
            tidyProperty = tidyProperty[0].upper() + tidyProperty[1:]
        return tidyProperty
        
    def AddDisplacement(self, material, surfacePrim):
        if rt.classOf(material) not in [rt.rsStandardMaterial, rt.rsMaterialBlender, rt.rsSprite, rt.rsIncandescent]:
            return #if the material isn't one of these, then there cant be a displacement in the graph so we can just do nothing.
            
        if rt.classOf(material) == rt.rsStandardMaterial:
            #most likely shader first
            if material.displacement_input == rt.undefined:
                return #no displacement
                
            primName = material.displacement_input.name.replace(" ", "_").replace("#", "_")
            maxClass = rt.classOf(material.displacement_input)
            usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
            usdShader.CreateIdAttr("redshift::" + maxShaderToRS[maxClass][0])
            surfacePrim.CreateInput('Displacement', Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "out")
                
            templateDef = maxClass
            templateClass = templateDef()
            for property in rt.getPropNames(material.displacement_input):
                self.AddProperty(usdShader, material.displacement_input, property, templateClass)
                self.AddShader(usdShader, material.displacement_input, property)
            return
        
        """
        if rt.classOf(material) == rt.rsMaterialBlender:
            displacementFound = False
            for i in rt.getPropNames(material):
                childMat = getattr(str(i))
                if classof(childMat) == rt.rsStandardMaterial:
                    if childMat.displacement_input != rt.undefined:
                        displacementFound = True
                        break
            return #TODO: deal with the possibility of blended displacements from different materials
        """
    def NodeTranslateComposite(self, parentPrim, parentNode, node, propertName):
        blendModeMap = {0:0,  #Normal
                        1:1,  #Average
                        2:2,  #Add 
                        3:3,  #Subtract
                        5:4,  #Multiply
                        19:5, #Difference
                        8:6,  #Lighten
                        4:7,  #Darken
                        9:8,  #Screen
                        16:9, #Hardlight
                        15:10,#Softlight
                        6:11, #Burn
                        10:12,#Dodge
                        14:13}#Overlay
                            
        primName = node.name.replace(" ", "_").replace("#", "_")
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        
        rt.execute("fn animControllerHelper value = (return value.controller)") #helper maxscript function to get animation controller
        
        arrayCount = min(len(node.mapList), 8)
        for i in range(0, arrayCount):
            animated = False
            
            propNameBase = 'base'
            if i != 0:
                propNameBase = 'layer' + str(i)
                
            self.AddShader(usdShader, node, node.mapList[i], propNameBase + '_color', node.mapList[i])
            if node.mask[i] != rt.undefined:
                self.AddShader(usdShader, node, node.mask[i], propNameBase + '_mask', node.mask[i])
            else:
                opacityAttr = usdShader.CreateInput(propNameBase + '_mask', Sdf.ValueTypeNames.Float)
                if rt.animControllerHelper(node.opacity[i]) is not None:
                    animated = True
                if animated and self.animationMode != maxUsd.TimeMode.CurrentFrame:
                    currentStep = self.startTime
                    while currentStep < self.endTime:
                        with pymxs.attime(currentStep):
                            value = node.opacity[i] / 100.0
                        opacityAttr.Set(value, currentStep)
                        currentStep += 1 / self.timeStep
                else:
                    opacityAttr.Set(node.opacity[i] / 100.0)
                
            usdShader.CreateInput(propNameBase + '_enable', Sdf.ValueTypeNames.Int).Set(int(node.mapEnabled[i]))
            
            if node.blendMode[i] in blendModeMap.keys():
                usdShader.CreateInput(propNameBase + '_blend_mode', Sdf.ValueTypeNames.Int).Set(blendModeMap[node.blendMode[i]])
            else:
                rt.UsdExporter.Log(rt.Name("warn"), f"unsupported blend mode in use on {primName}, this will use defualt")
                
        usdShader.CreateIdAttr("redshift::RSColorLayer")
        parentPrim.CreateInput(self.CleanMapProperty(propertName), Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "outColor")
        
    def NodeTranslateGradientRamp(self, parentPrim, parentNode, node, propertName):
        primName = node.name.replace(" ", "_").replace("#", "_")
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        usdShader.CreateIdAttr("redshift::RSRamp")
        
        knotCount = 0
        interp = []
        positions = []
        values = []
        
        interType = "linear"
        #This cant be accessed from maxscript..
        
        
        endColor = 0
        for knotName in rt.getPropNames(node.Gradient_Ramp):
            knotCount += 1
            knot = getattr(node.Gradient_Ramp, str(knotName))
            #knot 1 and 2 are always the first and last, the others are by order added
            if knotCount == 1:
                values.append((knot.color.x/255, knot.color.y/255, knot.color.z/255))
                interp.append(interType)
                positions.append(0.0)
            elif knotCount == 2:
                endColor = ((knot.color.x/255, knot.color.y/255, knot.color.z/255))
            elif knotCount > 2:
                interp.append(interType)
                positions.append(knot.position / 100)
                values.append((knot.color.x/255, knot.color.y/255, knot.color.z/255))
                
        positions.append(1.0)
        interp.append(interType)
        values.append(endColor)
        
        usdShader.CreateInput("inputInvert", Sdf.ValueTypeNames.Int).Set(0)
        usdShader.CreateInput("inputMapping", Sdf.ValueTypeNames.Token).Set('1') #to go the same direction as max, also why is this a token?
        
        usdShader.CreateInput("ramp", Sdf.ValueTypeNames.Int).Set(knotCount)
        usdShader.CreateInput("ramp_basis", Sdf.ValueTypeNames.TokenArray).Set(Vt.TokenArray(interp))
        usdShader.CreateInput("ramp_keys", Sdf.ValueTypeNames.FloatArray).Set(Vt.FloatArray(positions))
        usdShader.CreateInput("ramp_values", Sdf.ValueTypeNames.Color3fArray).Set(Vt.Vec3fArray(values))
        if node.Source_Map != rt.undefined:
            self.AddShader(usdShader, node, node.Source_Map, "input", node.Source_Map)
        
        parentPrim.CreateInput(self.CleanMapProperty(propertName), Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "outColor")
        
    def NodeTranslateVertexColor(self, parentPrim, parentNode, node, propertName):
        primName = node.name.replace(" ", "_").replace("#", "_")
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        usdShader.CreateIdAttr("redshift::RSUserDataColor")
        usdShader.CreateInput("attribute", Sdf.ValueTypeNames.String).Set("vertexColor")
        
        parentPrim.CreateInput(self.CleanMapProperty(propertName), Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "out")
        
    def NodeTranslateForestColor(self, parentPrim, parentNode, node, propertName):
                   #Normal, #Color, #Additive, #Average, #Multiply
        tintModes = ["0", "4", "2", "1", "4"]
        primName = node.name.replace(" ", "_").replace("#", "_")
        
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        usdShader.CreateIdAttr("redshift::RSColorLayer")
        
        self.AddShader(usdShader, node, node.mapbase, 'base_color', node.mapbase)
        
        attrShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName + "_forestAttr"))
        attrShader.CreateIdAttr("redshift::RSUserDataColor")
        attrShader.CreateInput("attribute", Sdf.ValueTypeNames.String).Set("displayColor")
        usdShader.CreateInput("layer1_color", Sdf.ValueTypeNames.Token).ConnectToSource(attrShader.ConnectableAPI(), "out")
        usdShader.CreateInput("layer1_blend_mode", Sdf.ValueTypeNames.Token).Set(tintModes[node.tintmixmode])
        
        parentPrim.CreateInput(self.CleanMapProperty(propertName), Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "outColor")
        
    @classmethod
    def CanExport(cls, exportArgs):
        if exportArgs.GetConvertMaterialsTo() == "redshift_usd_material":
            return maxUsd.ShaderWriter.ContextSupport.Supported
        return maxUsd.ShaderWriter.ContextSupport.Unsupported

# Register the writer.
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Standard Material")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Principled Hair")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Sprite")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Material Blender")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Volume")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Incandescent")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Store Color To AOV")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Standard Volume")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Toon Material")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS Material Output")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS OSL Material")
maxUsd.ShaderWriter.Register(RSShaderWriter, "RS OpenPBR Material")
