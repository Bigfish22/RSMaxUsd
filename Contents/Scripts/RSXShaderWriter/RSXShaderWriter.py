import maxUsd
import usd_utils
import pymxs
from pymxs import runtime as rt
from pxr import UsdShade, Sdf, Gf
import RSPreviewWriter
import usd_utils
import traceback
import os
import re

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Float3,
                rt.StandardUVGen : Sdf.ValueTypeNames.Token,
                rt.BitMap : Sdf.ValueTypeNames.Token,
                rt.point2 : Sdf.ValueTypeNames.Float2,
                rt.material : Sdf.ValueTypeNames.Token}
                    
#Key: maxClass : [Houdini/core Name, Output Pin Name(if the node has multi outputs, we can get this from max]
maxShaderToRS = {rt.MultiOutputChannelTexmapToTexmap : ["", 'out'],
                rt.rsAmbientOcclusion : ['AmbientOcclusion', 'out'],
                rt.rsMathAbs : ['RSMathAbs', 'out'],
                rt.rsMathAdd : ['RSMathAdd', 'out'],
                rt.rsMathATan2 : ['RSMathArcTan2', 'out'],
                rt.rsMathACos : ['RSMathArcCos', 'out'],
                rt.rsMathASin : ['RSMathArcSin', 'out'],
                rt.rsMathATan : ['RSMathArcTan', 'out'],
                rt.rsMathBias : ['RSMathBias', 'out'],
                rt.rsBitmap : ['TextureSampler', 'outColor'],
                rt.rsBrick : ['Brick', 'outColor'],
                rt.rsBumpBlender : ['BumpBlender', 'outDisplacementVector'],
                rt.rsBumpMap : ['BumpMap', 'out'],
                rt.rsCameraMap : ['RSCameraMap', 'outColor'],
                rt.rsMathRange : ['RSMathRange', 'out'],
                rt.rsMathAbsColor : ['RSMathAbsColor', 'outColor'],
                rt.rsMathBiasColor : ['RSMathBiasColor', 'outColor'],
                rt.rsColorRange : ['RSColorRange', 'out'],
                rt.rsColorConstant : ['RSColorConstant', 'outColor'],
                rt.rsMathExpColor : ['RSMathExpColor', 'outColor'],
                rt.rsMathGainColor : ['RSMathGainColor', 'outColor'],
                rt.rsMathInvColor : ['RSMathInvertColor', 'out'],
                rt.rsColorMaker : ['RSColorMaker', 'outColor'],
                rt.rsColorMix : ['RSColorMix', 'outColor'],
                rt.rsMathSaturateColor : ['RSMathSaturateColor', 'outColor'],
                rt.rsColorSplitter : ['RSColorSplitter', ''],
                rt.rsMathSubColor : ['RSMathSubColor', 'outColor'],
                rt.rsColor2HSV : ['RSColor2HSV', 'outColor'],
                rt.rsUserDataColor : ['RSUserDataColor', 'out'],
                rt.rsMathCos : ['RSMathCos', 'out'],
                rt.rsMathCrossVector : ['RSCrossProduct', 'out'],
                rt.rsCurvature : ['RSCurvature', 'out'],
                rt.rsDisplacement : ['Displacement', 'out'],
                rt.rsDisplacementBlender : ['DisplacementBlender', 'out'],
                rt.rsMathDiv : ['RSMathDiv', 'out'],
                rt.rsMathDotVector : ['RSDotProduct', 'out'],
                rt.rsEnvironment : ['RSEnvironment', 'outColor'],
                rt.rsMathExp : ['RSMathExp', 'out'],
                rt.rsFlakes : ['RSFlakes', 'out'],
                rt.rsMathFloor : ['RSMathFloor', 'out'],
                rt.rsMathFrac : ['RSMathFrac', 'out'],
                rt.rsFresnel : ['RSFresnel', 'out'],
                rt.rsMathGain : ['RSMathGain', 'out'],
                rt.rsHSV2Color : ['RSHSVToColor', 'outColor'],
                rt.rsHairPosition : ['RSHairPosition', 'outVector'],
                rt.rsHairRandomColor : ['RSHairRandomColor', 'out'],
                rt.rsIORToMetalTints : ['RSIORToMetalTints', ''],
                rt.rsUserDataInteger : ['RSUserDataInteger', 'out'],
                rt.rsMathInv : ['RSMathInv', 'out'],
                rt.rsJitter : ['Jitter', 'outColor'],
                rt.rsMathLn : ['RSMathLn', 'out'],
                rt.rsMathLog : ['RSMathLog', 'out'],
                rt.rsMatCap : ['RSMatCap', 'out'],
                rt.rsMathMax : ['RSMathMax', 'out'],
                rt.rsMaxonNoise : ['MaxonNoise', 'outColor'],
                rt.rsMathMin : ['RSMathMin', 'out'],
                rt.rsMathMix : ['RSMathMix', 'out'],
                rt.rsMathMod : ['RSMathMod', 'out'],
                rt.rsMathMul : ['RSMathMul', 'out'],
                rt.rsMathNeg : ['RSMathNeg', 'out'],
                rt.rsMathNormalizeVector : ['RSMathNormalizeVector', 'out'],
                rt.rsOSLMap : ['rsOSL', ''],
                rt.rsPavement : ['RSPavement', ''],
                rt.rsPhysicalSky : ['RSPhysicalSky', 'outColor'],
                rt.rsMathPow : ['RSMathPow', 'out'],
                rt.rsRaySwitch : ['RaySwitch', 'outColor'],
                rt.rsMathRcp : ['RSMathRcp', 'out'],
                rt.rsRoundCorners : ['RoundCorners', 'out'],
                rt.rsMathSaturate : ['RSMathSaturate', 'out'],
                rt.rsUserDataScalar : ['RSUserDataScalar', 'out'],
                rt.rsShaderSwitch : ['RSShaderSwitch', 'outColor'],
                rt.rsShave : ['RSShave', 'out'],
                rt.rsMathSign : ['RSMathSign', 'out'],
                rt.rsMathSin : ['RSMathSin', 'out'],
                rt.rsMathSqrt : ['RSMathSqrt', 'out'],
                rt.rsState : ['State', 'out'],
                rt.rsMathSub : ['RSMathSub', 'out'],
                rt.rsMathTan : ['RSMathTan', 'out'],
                rt.rsTexture : ['TextureSampler', 'outColor'],
                rt.rsTiles : ['RSTiles', ''],
                rt.rsTriPlanar : ['TriPlanar', 'outColor'],
                rt.rsUVProjection : ['UVProjection', 'out'],
                rt.rsMathAbsVector : ['RSMathAbsVector', 'out'],
                rt.rsMathAddVector : ['RSMathAddVector', 'out'],
                rt.rsMathBiasVector : ['RSMathBiasVector', 'out'],
                rt.rsMathRangeVector : ['RSMathRangeVector', 'out'],
                rt.rsMathDivVector : ['RSMathDivVector', 'out'],
                rt.rsMathExpVector : ['RSMathExpVector', 'out'],
                rt.rsMathFloorVector : ['RSMathFloorVector', 'out'],
                rt.rsMathFracVector : ['RSMathFracVector', 'out'],
                rt.rsMathGainVector : ['RSMathGainVector', 'out'],
                rt.rsMathInvVector : ['RSMathInvVector', 'out'],
                rt.rsMathLengthVector : ['RSMathLengthVector', 'out'],
                rt.rsMathLnVector : ['RSMathLnVector', 'out'],
                rt.rsMathLogVector : ['RSMathLogVector', 'out'],
                rt.rsVectorMaker : ['RSVectorMaker', 'out'],
                rt.rsMathMaxVector : ['RSMathMaxVector', 'out'],
                rt.rsMathMinVector : ['RSMathMinVector', 'out'],
                rt.rsMathMixVector : ['RSMathMixVector', 'out'],
                rt.rsMathModVector : ['RSMathModVector', 'out'],
                rt.rsMathMulVector : ['RSMathMulVector', 'out'],
                rt.rsMathNegVector : ['RSMathNegVector', 'out'],
                rt.rsMathPowVector : ['RSMathPowVector', 'out'],
                rt.rsMathRcpVector : ['RSMathRcpVector', 'out'],
                rt.rsMathSaturateVector : ['RSMathSaturateVector', 'out'],
                rt.rsMathSignVector : ['RSMathSignVector', 'out'],
                rt.rsMathSqrtVector : ['RSMathSqrtVector', 'out'],
                rt.rsMathSubVector : ['RSMathSubVector', 'out'],
                rt.rsVectorToScalars : ['RSVectorToScalars', 'out'],
                rt.rsUserDataVector : ['RSUserDataVector', 'out'],
                rt.rsWireFrame : ['WireFrame', 'out'],
                rt.rsStandardMaterial : ['StandardMaterial', 'outColor'],
                rt.rsMaterialSwitch : ["RSShaderSwitch", 'outClosure'],
                rt.rsPrincipledHair : ['Hair2', 'out'],
                rt.rsSprite : ['Sprite', 'outColor'],
                rt.rsMaterialBlender : ['MaterialBlender', 'out'],
                rt.rsVolume : ['Volume', 'outColor'],
                rt.rsIncandescent : ['Incandescent', 'outColor'],
                rt.rsStoreColorToAOV : ['StoreColorToAOV', 'outColor'],
                rt.rsColorCorrection : ['RSColorCorrection', 'outColor'],
                rt.CompositeMap :      ['RSColorLayer', 'outColor'],
                rt.VertexColor  :      ['RSUserDataColor', 'out'],
                rt.rsStandardVolume :  ['StandardVolume', 'outColor'],
                rt.rsVolumeColorAttribute : ['VolumeColorAttribute', 'outColor'],
                rt.rsVolumeScalarAttribute : ['VolumeScalarAttribute', 'out'],
                rt.rsToonMaterial : ['ToonMaterial', 'outColor'],
                rt.rsContour : ['Contour', 'outColor'],
                rt.rsTonemapPattern : ['TonemapPattern', 'outColor'],
                rt.rsMaterialOutput : ['', '']}
                    
PropertyRemaps = {rt.rsOSLMap : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'},
                  rt.rsTexture: {"scale_x" : "scale", "scale_y": "scale", "offset_x" : "offset", "offset_y" : "offset"}}



class RSShaderWriter(maxUsd.ShaderWriter):
    def Write(self):
        try:
            self.nodeTranslators = {rt.CompositeMap: self.NodeTranslateComposite,
                                    rt.Gradient_Ramp : self.NodeTranslateGradientRamp,
                                    rt.VertexColor : self.NodeTranslateVertexColor}
            
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
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def AddProperty(self, prim, node, prop, template):
        if(str(prop).endswith(("_map","_mapamount", "_mapenable", "_enable", "_input"))):
            return
        
        nodeClass = rt.ClassOf(node)
        
        value = getattr(node, str(prop))
        animated = False
        if rt.getPropertyController(node, str(prop)):
            animated = True
        if not (nodeClass == rt.rsOSLMap):
            if value == getattr(template, str(prop)) and not animated:
                return #The property is still at its defualt value and it is not animated, so we can just skip doing anything with it
            
        type = rt.classOf(value)
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
        elif rt.classof(node) == rt.rsTexture and str(prop).endswith(('_x', '_y')):
            value = Gf.Vec2f(getattr(node, str(prop)[:-2] + '_x'), getattr(node, str(prop)[:-2] + '_y'))
            self.type = rt.point2
        return value
            
    def ResolveString(self, prim, value, prop, node):
        #is it a filepath? if so we need to store it as an asset. Relative file paths don't seem to resolve, need to work out how works.
        nodeClass = rt.classOf(node)
        if re.search("\....$", value):
            assetPath = self.RelativeAssetPath(value)
            propertyName = str(prop)
            if propertyName == "tex0_filename":
                propertyName = "tex0"
                try:  #sprites dont have tiling mode, classic stitch up there
                    if getattr(node, "tilingmode") == 1:
                        assetPath = re.sub("1[0-9]{3}", "<UDIM>", assetPath)
                except:
                    pass
            if rt.ClassOf(node) in PropertyRemaps:
                if str(prop) in PropertyRemaps[nodeClass]:
                    propertyName = PropertyRemaps[nodeClass][str(prop)]
                    prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)

                    return
            prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)
        else:
            prim.CreateInput(str(prop), Sdf.ValueTypeNames.String).Set(value)

    
    def ResolveUVGen(self, prim, value):
        prim.CreateInput("scale", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(value.U_Tiling, value.V_Tiling))
        prim.CreateInput("rotate", Sdf.ValueTypeNames.Float).Set(value.W_Angle)
        prim.CreateInput("offset", Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(value.U_Offset, value.V_Offset))
        
    def AddShader(self, parentPrim, parentNode, prop, propertyOverride = None, nodeOverride = None):
        if not (str(prop)).endswith(("_map", "p_input")) and nodeOverride == None and str(prop) not in (('surface', 'Volume', 'contour', 'displacement', 'bumpMap', 'environment')): #TODO: should probably just be checking if this is a textureMap class, this will catch undefined and properties, assuming superClassOf doesn't fail for undefined.
            return
        
        #some node translators might need to provide a specific max node, instead of just the property
        if nodeOverride is not None:
            maxShader = nodeOverride
        else:
            maxShader = getattr(parentNode, str(prop))
        
        #if we have nothing return early
        if maxShader == rt.undefined:
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
        relPath = rt.pathConfig.convertPathToAbsolute(path)
        relPath = usd_utils.safe_relpath(relPath, os.path.dirname(self.GetFilename()))
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
        pass
        
    def NodeTranslateVertexColor(self, parentPrim, parentNode, node, propertName):
        primName = node.name.replace(" ", "_").replace("#", "_")
        usdShader = UsdShade.Shader.Define(self.GetUsdStage(), ((self.GetUsdPath()).GetParentPath()).AppendPath(primName))
        usdShader.CreateIdAttr("redshift::RSUserDataColor")
        usdShader.CreateInput("attribute", Sdf.ValueTypeNames.String).Set("vertexColor")
        
        parentPrim.CreateInput(self.CleanMapProperty(propertName), Sdf.ValueTypeNames.Token).ConnectToSource(usdShader.ConnectableAPI(), "out")
        
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
