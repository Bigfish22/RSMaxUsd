import maxUsd
from pymxs import runtime as rt
from pxr import UsdShade, Sdf, Gf
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
                rt.BitMap : Sdf.ValueTypeNames.Token}
                    
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
                rt.rsUserDataColor : ['RSUserDataColor', 'outColor'],
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
                rt.rsMathInvVector : ['RSMathInvertVector', 'out'],
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
                rt.rsMaterialBlender : ['MaterialBlender', 'outColor'],
                rt.rsVolume : ['Volume', 'outColor'],
                rt.rsIncandescent : ['Incandescent', 'outColor'],
                rt.rsStoreColorToAOV : ['StoreColorToAOV', 'outColor'],
                rt.rsColorCorrection : ['RSColorCorrection', 'outColor']}
                    
PropertyRemaps = {rt.rsOSLMap : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'}}


class rsxshaderwriter(maxUsd.ShaderWriter):
    def Write(self):
        try:
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
            
            
            nodeShader = UsdShade.Shader.Define(self.GetUsdStage(), (self.GetUsdPath()))
            nodeShader.CreateIdAttr("redshift::" + maxShaderToRS[rt.classOf(material)][0])
            
            if rt.classOf(material) == rt.rsVolume:
                surfaceShader.CreateInput('Volume', Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), "outColor")
            else:
                surfaceShader.CreateInput('Surface', Sdf.ValueTypeNames.Token).ConnectToSource(nodeShader.ConnectableAPI(), "outColor")
            
            
            templateDef = rt.classOf(material)
            templateClass = templateDef()
            for property in rt.getPropNames(material):
                self.addProperty(nodeShader, material, property, templateClass)
                self.addShader(nodeShader, material, property)
            self.addDisplacement(material, surfaceShader)
            return True

        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def addProperty(self, Prim, Node, Property, template):
        if(str(Property).endswith(("_map","_mapamount", "_mapenable", "_enable", "_input"))):
            return
        
        nodeClass = rt.ClassOf(Node)
        
        value = getattr(Node, str(Property))
        animated = False
        if rt.getPropertyController(Node, str(Property)):
            animated = True
        if not (nodeClass == rt.rsOSLMap):
            if value == getattr(template, str(Property)) and not animated: #TODO: This should also check if a value is animated, if its animated we should probably write its values.
                return #The property is still at its defualt value and it is not animated, so we can just skip doing anything with it
            
        type = rt.classOf(value)
        
        if not (type in maxTypeToSdf):
            rt.UsdExporter.Log(rt.Name("warn"), (str(Property) + "has unsupported type conversion" + str(type)))
            return
            
        sdfType = maxTypeToSdf[type]
        
        value = self.resolveValue(Prim, type, value, Property, Node)
        if value is None:
            return
        
        propertyName = str(Property)
        if nodeClass in PropertyRemaps:
            if str(Property) in PropertyRemaps[nodeClass]:
                propertyName = PropertyRemaps[nodeClass][str(Property)]
                
        inputAttribute = Prim.CreateInput(propertyName, sdfType)
        if not animated or self.animationMode == maxUsd.TimeMode.CurrentFrame:
            inputAttribute.Set(value)
        else:
            currentStep = self.startTime
            while currentStep < self.endTime:
                with pymxs.attime(currentStep):
                    value = getattr(Node, str(Property))
                value = self.resolveValue(Prim, type, value, Property, Node)
                inputAttribute.Set(value, currentStep)
                currentStep += 1 / self.timeStep
    
    def resolveValue(self, prim, type, value, Property, Node):
        if type == rt.Color:
            value = (value.r/255, value.g/255, value.b/255)
        elif type == rt.point3:
            value = Gf.Vec3f(value.x, value.y, value.z)
        elif type == rt.Double or type == rt.Integer or type == rt.BooleanClass:
            return value
        elif type == rt.string:
            self.resolveString(prim, value, Property, Node)
            value = None
        elif type == rt.StandardUVGen:
            self.resolveUVGen(prim, value)
            value = None
        elif type == rt.BitMap:
            value = None
        return value
            
    def resolveString(self, prim, value, Property, Node):
        #is it a filepath? if so we need to store it as an asset. Relative file paths don't seem to resolve, need to work out how works.
        if re.search("\....$", value):
            assetPath = self.relativeAssetPath(value)
            propertyName = str(Property)
            if propertyName == "tex0_filename":
                propertyName = "tex0"
                try:  #sprites dont have tiling mode, classic stitch up there
                    if getattr(Node, "tilingmode") == 1:
                        assetPath = re.sub("1[0-9]{3}", "<UDIM>", assetPath)
                except:
                    pass
            if rt.ClassOf(Node) in PropertyRemaps:
                if str(Property) in PropertyRemaps[nodeClass]:
                    propertyName = PropertyRemaps[nodeClass][str(Property)]
                    prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)
                    return
            prim.CreateInput(propertyName, Sdf.ValueTypeNames.Asset).Set(assetPath)
        else:
            print(str(Property))
            prim.CreateInput(str(Property), Sdf.ValueTypeNames.String).Set(value)
    
    def resolveUVGen(self, prim, value):
        prim.CreateInput("scale_x", Sdf.ValueTypeNames.Float).Set(value.U_Tiling)
        prim.CreateInput("scale_y", Sdf.ValueTypeNames.Float).Set(value.V_Tiling)
        prim.CreateInput("Rotate", Sdf.ValueTypeNames.Float).Set(value.W_Angle)
        prim.CreateInput("offset_X", Sdf.ValueTypeNames.Float).Set(value.U_Offset)
        prim.CreateInput("offset_Y", Sdf.ValueTypeNames.Float).Set(value.V_Offset)
        
    def addShader(self, parentPrim, parentNode, Property):
        if not (str(Property)).endswith(("_map", "p_input")): #TODO: should probably just be checking if this is a textureMap class, this will catch undefined and properties, assuming superClassOf doesn't fail for undefined.
            return
            
        maxShader = getattr(parentNode, str(Property))
        if maxShader == rt.undefined:
            return
        
        
        maxClass = rt.classOf(maxShader)
        if not (maxClass in maxShaderToRS):
            rt.UsdExporter.Log(rt.Name("warn"), (str(maxClass) + "is not supported, this node and any children will be skipped!"))
            return
            
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
        tidyProperty = str(Property).replace("_map", "")
        tidyProperty = tidyProperty[0].lower() + tidyProperty[1:] #were not even going to talk about this
        
        if tidyProperty == "bump_input":
            parentSdfType = Sdf.ValueTypeNames.Int
        elif not (hasattr(parentNode, tidyProperty)):
            parentSdfType = Sdf.ValueTypeNames.Int
        elif rt.superClassOf(getattr(parentNode, tidyProperty)) == rt.textureMap:
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
                self.addProperty(usdShader, maxShader, shaderProperty, templateClass)
                self.addShader(usdShader, maxShader, shaderProperty)
        
    def relativeAssetPath(self, path):
        #This doesn't seem to resolve in houdini and I dont handle it on import, so leaving it as full file paths for now.
        """
        exportFolder = os.path.dirname(self.GetFilename())
        if exportFolder in path:
            return path.replace(exportFolder + "\\", "../").replace(os.sep, "/")
        """
        return path.replace(os.sep, "/")
        
    def addDisplacement(self, material, surfacePrim):
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
                self.addProperty(usdShader, material.displacement_input, property, templateClass)
                self.addShader(usdShader, material.displacement_input, property)
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
        
        
    @classmethod
    def CanExport(cls, exportArgs):
        if exportArgs.GetConvertMaterialsTo() == "redshift_usd_material":
            return maxUsd.ShaderWriter.ContextSupport.Supported
        return maxUsd.ShaderWriter.ContextSupport.Unsupported

# Register the writer.
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Standard Material")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Principled Hair")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Sprite")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Material Blender")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Volume")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Incandescent")
maxUsd.ShaderWriter.Register(rsxshaderwriter, "RS Store Color To AOV")