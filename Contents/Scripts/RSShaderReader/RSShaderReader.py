import maxUsd
from pymxs import runtime as rt
from pxr import UsdShade, Sdf
import usd_utils
import pymxs
import traceback
import glob

maxTypeToSdf = {Sdf.ValueTypeNames.Float : rt.Double,
                Sdf.ValueTypeNames.Int : rt.Integer,
                Sdf.ValueTypeNames.Color3f : rt.Color,
                Sdf.ValueTypeNames.Bool : rt.BooleanClass,
                Sdf.ValueTypeNames.String : rt.string,
                Sdf.ValueTypeNames.Float3 : rt.point3,
                Sdf.ValueTypeNames.Asset  : rt.string,
                Sdf.ValueTypeNames.Float2 : rt.point2}

schemaToMax = {'redshift::': rt.MultiOutputChannelTexmapToTexmap,
                 'redshift::AmbientOcclusion': rt.rsAmbientOcclusion,
                 'redshift::RSMathAbs': rt.rsMathAbs,
                 'redshift::RSMathAdd': rt.rsMathAdd,
                 'redshift::RSMathArcTan2': rt.rsMathATan2,
                 'redshift::RSMathArcCos': rt.rsMathACos,
                 'redshift::RSMathArcSin': rt.rsMathASin,
                 'redshift::RSMathArcTan': rt.rsMathATan,
                 'redshift::RSMathBias': rt.rsMathBias,
                 'redshift::TextureSampler': rt.rsTexture,
                 'redshift::Brick': rt.rsBrick,
                 'redshift::BumpBlender': rt.rsBumpBlender,
                 'redshift::BumpMap': rt.rsBumpMap,
                 'redshift::RSCameraMap': rt.rsCameraMap,
                 'redshift::RSMathRange': rt.rsMathRange,
                 'redshift::RSMathAbsColor': rt.rsMathAbsColor,
                 'redshift::RSMathBiasColor': rt.rsMathBiasColor,
                 'redshift::RSColorRange': rt.rsColorRange,
                 'redshift::RSColorConstant': rt.rsColorConstant,
                 'redshift::RSMathExpColor': rt.rsMathExpColor,
                 'redshift::RSMathGainColor': rt.rsMathGainColor,
                 'redshift::RSMathInvertColor': rt.rsMathInvColor,
                 'redshift::RSColorMaker': rt.rsColorMaker,
                 'redshift::RSColorMix': rt.rsColorMix,
                 'redshift::RSMathSaturateColor': rt.rsMathSaturateColor,
                 'redshift::RSColorSplitter': rt.rsColorSplitter,
                 'redshift::RSMathSubColor': rt.rsMathSubColor,
                 'redshift::RSColor2HSV': rt.rsColor2HSV,
                 'redshift::RSUserDataColor': rt.rsUserDataColor,
                 'redshift::RSMathCos': rt.rsMathCos,
                 'redshift::RSCrossProduct': rt.rsMathCrossVector,
                 'redshift::RSCurvature': rt.rsCurvature,
                 'redshift::Displacement': rt.rsDisplacement,
                 'redshift::DisplacementBlender': rt.rsDisplacementBlender,
                 'redshift::RSMathDiv': rt.rsMathDiv,
                 'redshift::RSDotProduct': rt.rsMathDotVector,
                 'redshift::RSEnvironment': rt.rsEnvironment,
                 'redshift::RSMathExp': rt.rsMathExp,
                 'redshift::RSFlakes': rt.rsFlakes,
                 'redshift::RSMathFloor': rt.rsMathFloor,
                 'redshift::RSMathFrac': rt.rsMathFrac,
                 'redshift::RSFresnel': rt.rsFresnel,
                 'redshift::RSMathGain': rt.rsMathGain,
                 'redshift::RSHSVToColor': rt.rsHSV2Color,
                 'redshift::RSHairPosition': rt.rsHairPosition,
                 'redshift::RSHairRandomColor': rt.rsHairRandomColor,
                 'redshift::RSIORToMetalTints': rt.rsIORToMetalTints,
                 'redshift::RSUserDataInteger': rt.rsUserDataInteger,
                 'redshift::RSMathInv': rt.rsMathInv,
                 'redshift::Jitter': rt.rsJitter,
                 'redshift::RSMathLn': rt.rsMathLn,
                 'redshift::RSMathLog': rt.rsMathLog,
                 'redshift::RSMatCap': rt.rsMatCap,
                 'redshift::RSMathMax': rt.rsMathMax,
                 'redshift::MaxonNoise': rt.rsMaxonNoise,
                 'redshift::RSMathMin': rt.rsMathMin,
                 'redshift::RSMathMix': rt.rsMathMix,
                 'redshift::RSMathMod': rt.rsMathMod,
                 'redshift::RSMathMul': rt.rsMathMul,
                 'redshift::RSMathNeg': rt.rsMathNeg,
                 'redshift::RSMathNormalizeVector': rt.rsMathNormalizeVector,
                 'redshift::rsOSL': rt.rsOSLMap,
                 'redshift::RSPavement': rt.rsPavement,
                 'redshift::RSPhysicalSky': rt.rsPhysicalSky,
                 'redshift::RSMathPow': rt.rsMathPow,
                 'redshift::RaySwitch': rt.rsRaySwitch,
                 'redshift::RSMathRcp': rt.rsMathRcp,
                 'redshift::RoundCorners': rt.rsRoundCorners,
                 'redshift::RSMathSaturate': rt.rsMathSaturate,
                 'redshift::RSUserDataScalar': rt.rsUserDataScalar,
                 'redshift::RSShaderSwitch': rt.rsMaterialSwitch,
                 'redshift::RSShave': rt.rsShave,
                 'redshift::RSMathSign': rt.rsMathSign,
                 'redshift::RSMathSin': rt.rsMathSin,
                 'redshift::RSMathSqrt': rt.rsMathSqrt,
                 'redshift::State': rt.rsState,
                 'redshift::RSMathSub': rt.rsMathSub,
                 'redshift::RSMathTan': rt.rsMathTan,
                 'redshift::RSTiles': rt.rsTiles,
                 'redshift::TriPlanar': rt.rsTriPlanar,
                 'redshift::UVProjection': rt.rsUVProjection,
                 'redshift::RSMathAbsVector': rt.rsMathAbsVector,
                 'redshift::RSMathAddVector': rt.rsMathAddVector,
                 'redshift::RSMathBiasVector': rt.rsMathBiasVector,
                 'redshift::RSMathRangeVector': rt.rsMathRangeVector,
                 'redshift::RSMathDivVector': rt.rsMathDivVector,
                 'redshift::RSMathExpVector': rt.rsMathExpVector,
                 'redshift::RSMathFloorVector': rt.rsMathFloorVector,
                 'redshift::RSMathFracVector': rt.rsMathFracVector,
                 'redshift::RSMathGainVector': rt.rsMathGainVector,
                 'redshift::RSMathInvertVector': rt.rsMathInvVector,
                 'redshift::RSMathLengthVector': rt.rsMathLengthVector,
                 'redshift::RSMathLnVector': rt.rsMathLnVector,
                 'redshift::RSMathLogVector': rt.rsMathLogVector,
                 'redshift::RSVectorMaker': rt.rsVectorMaker,
                 'redshift::RSMathMaxVector': rt.rsMathMaxVector,
                 'redshift::RSMathMinVector': rt.rsMathMinVector,
                 'redshift::RSMathMixVector': rt.rsMathMixVector,
                 'redshift::RSMathModVector': rt.rsMathModVector,
                 'redshift::RSMathMulVector': rt.rsMathMulVector,
                 'redshift::RSMathNegVector': rt.rsMathNegVector,
                 'redshift::RSMathPowVector': rt.rsMathPowVector,
                 'redshift::RSMathRcpVector': rt.rsMathRcpVector,
                 'redshift::RSMathSaturateVector': rt.rsMathSaturateVector,
                 'redshift::RSMathSignVector': rt.rsMathSignVector,
                 'redshift::RSMathSqrtVector': rt.rsMathSqrtVector,
                 'redshift::RSMathSubVector': rt.rsMathSubVector,
                 'redshift::RSVectorToScalars': rt.rsVectorToScalars,
                 'redshift::RSUserDataVector': rt.rsUserDataVector,
                 'redshift::WireFrame': rt.rsWireFrame,
                 'redshift::StandardMaterial': rt.rsStandardMaterial,
                 'redshift::Hair2': rt.rsPrincipledHair,
                 'redshift::Sprite': rt.rsSprite,
                 'redshift::MaterialBlender': rt.rsMaterialBlender,
                 'redshift::Volume': rt.rsVolume,
                 'redshift::Incandescent': rt.rsIncandescent,
                 'redshift::StoreColorToAOV': rt.rsStoreColorToAOV,
                 'redshift::RSColorCorrection': rt.rsColorCorrection}

PropertyRemaps = {rt.rsOSLMap : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'},
                  rt.rsTexture: {"scale_x" : "scale", "scale_y": "scale", "offset_x" : "offset", "offset_y" : "offset"}}
                      
class RSShaderReader(maxUsd.ShaderReader):
    def Read(self):
        try:
            self.MapLibrary = {}
            
            prim = self.GetUsdPrim() #Turn this into a max material
            
            surfaceConnection = prim.GetAttribute('inputs:Surface').GetConnections()
            
            displacementConnection = prim.GetAttribute('inputs:Displacement').GetConnections()
            
            if prim.GetAttribute('inputs:Volume'):
                volumeConnection = prim.GetAttribute('inputs:Volume').GetConnections()
                shader = prim.GetPrimAtPath(volumeConnection[0].GetPrimPath())
            else:    
                shader = prim.GetPrimAtPath(surfaceConnection[0].GetPrimPath())
                
            shaderID = shader.GetAttribute("info:id").Get()
            
            if not (shaderID in schemaToMax):
                print(shaderID, "is not supported by this reader!")
                return False
            
            maxNode = schemaToMax[shaderID]()
            handle = rt.GetHandleByAnim(maxNode)
            
            
            for i in shader.GetPropertyNames():
                if i.startswith('inputs:'):
                    propertyName = i.split(":")[1]
                    if hasattr(maxNode, propertyName) or hasattr(maxNode, propertyName + "_map"):
                        usdAttribute = shader.GetAttribute(i)
                        Connections = usdAttribute.GetConnections()
                        if len(Connections) > 0:
                            MapPropertyName, Map = self.AddNode(prim, propertyName, Connections)
                            if MapPropertyName:
                                rt.USDImporter.SetMaterialParamByName(maxNode, MapPropertyName, Map)
                        value = self.ResolveMaxValue(usdAttribute)
                        if value:
                            if propertyName == "tex0":  #SCREAMING
                                propertyName = "tex0_filename"
                            rt.USDImporter.SetMaterialParamByName(maxNode, propertyName, value)
                            
            #plob displacement back in if its a standard material
            if rt.classOf(maxNode) == rt.rsStandardMaterial:
                if prim.GetAttribute('inputs:Displacement'):
                    dispConnections = prim.GetAttribute('inputs:Displacement').GetConnections()
                    MapPropertyName, Map = self.AddNode(prim, "Displacement_input", dispConnections)
                    if MapPropertyName:
                        rt.USDImporter.SetMaterialParamByName(maxNode, MapPropertyName, Map)
             
            self.RegisterCreatedMaterial(prim.GetPrimPath(), handle) #Register here and hopefully max will assign the material we made?
            self.MapLibrary[prim] = handle
            return True
            
        except Exception as e:
            # Quite useful to debug errors in a Python callback
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def AddNode(self, prim, propertyName, connection):
        
        shader = prim.GetPrimAtPath(connection[0].GetPrimPath())
        shaderID = shader.GetAttribute("info:id").Get()
        shaderName = shader.GetName()
        
        if not (shaderID in schemaToMax):
                print(shaderID, "is not supported by this reader!")
                return (None, None)
                
        if shader in self.MapLibrary:
            maxNode = rt.getAnimByHandle(self.MapLibrary[shader])
        else:
            maxNode = schemaToMax[shaderID]()
            maxNode.name = shaderName
            
        MapPropertyName = propertyName
        if not propertyName.endswith("_input"):
            MapPropertyName = propertyName + "_map"
        
        if rt.classOf(maxNode) == rt.rsOSLMap: #set these first if its an osl node, or we will not have any paramters to set :D
            if shader.GetAttribute("inputs:RS_osl_code"):
                maxNode.OSLCode = shader.GetAttribute("inputs:RS_osl_code").Get()
            if shader.GetAttribute("inputs:RS_osl_file"):    
                maxNode.oslFilename = shader.GetAttribute("inputs:RS_osl_file").Get().path
            if shader.GetAttribute("inputs:RS_osl_source"):
                maxNode.oslSource = shader.GetAttribute("inputs:RS_osl_source").Get()
                
        if rt.classOf(maxNode) == rt.rsTexture:
            scaleAttr = shader.GetAttribute("inputs:scale")
            if scaleAttr:
                maxNode.scale_x = scaleAttr.Get()[0]
                maxNode.scale_y = scaleAttr.Get()[1]
            offsetAttr = shader.GetAttribute("inputs:offset")
            if offsetAttr:
                maxNode.offset_x = offsetAttr.Get()[0] 
                maxNode.offset_y = offsetAttr.Get()[1]
        
        for i in shader.GetPropertyNames():
                if i.startswith('inputs:'):
                    ChildpropertyName = i.split(":")[1]
                    if hasattr(maxNode, ChildpropertyName) or hasattr(maxNode, ChildpropertyName + "_map"):
                        usdAttribute = shader.GetAttribute(i)
                        Connections = usdAttribute.GetConnections()
                        if len(Connections) > 0:
                            ChildMapPropertyName, Map = self.AddNode(prim, ChildpropertyName, Connections)
                            if ChildMapPropertyName:
                                #probably fix this later, it should probably still be faster if mostly it hits texmaps first
                                try:
                                    rt.USDImporter.SetTexmapParamByName(maxNode, ChildMapPropertyName, Map)
                                except:
                                    rt.USDImporter.SetMaterialParamByName(maxNode, ChildMapPropertyName, Map)
                                    
                        value = self.ResolveMaxValue(usdAttribute)
                        if value:
                            if ChildpropertyName == "tex0":  #SCREAMING
                                ChildpropertyName = "tex0_filename"
                            try:
                                rt.USDImporter.SetTexmapParamByName(maxNode, ChildpropertyName, value)
                            except:
                                rt.USDImporter.SetMaterialParamByName(maxNode, ChildpropertyName, value)
                                
                                
        self.MapLibrary[shader] = rt.getHandleByAnim(maxNode)
        
        #are we a multioutput?
        if hasattr(maxNode, "numIMultipleOutputChannels"):
            MultiOutput = rt.MultiOutputChannelTexmapToTexmap()
            MultiOutput.sourcemap = maxNode
            outPutName = connection[0].pathString.split(":")[1]  #path should have something that does this, but maybe not in python?
            for index in range(1, (maxNode.numIMultipleOutputChannels + 1)):
                if maxNode.getIMultipleOutputChannelName(index) == outPutName:
                    MultiOutput.outputChannelIndex = index
            maxNode = MultiOutput
        
        return (MapPropertyName, maxNode)
        
    def ResolveMaxValue(self, usdAttr):
        sdfType = usdAttr.GetTypeName()
        if sdfType not in maxTypeToSdf:
            return None
        sdfValue = usdAttr.Get()
        if sdfValue == None:
            return None
        maxValue = sdfValue
        if sdfType == Sdf.ValueTypeNames.Color3f:
            maxValue = rt.point4(sdfValue[0], sdfValue[1], sdfValue[2], 1)
        if sdfType == Sdf.ValueTypeNames.Asset:
            maxValue = sdfValue.path
            maxValue = maxValue.replace("<UDIM>", "*")
            maxValue = glob.glob(maxValue)[0]
        return maxValue
    
    @classmethod
    def CanImport(cls, importArgs):
        return maxUsd.ShaderReader.ContextSupport.Supported
        
        
maxUsd.ShaderReader.Register(RSShaderReader, "redshift_usd_material")