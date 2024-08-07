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

import maxUsd
import pymxs
from pymxs import runtime as rt
from pxr import UsdShade, Sdf, Ar
import usd_utils
import traceback
import glob

maxTypeToSdf = {Sdf.ValueTypeNames.Float : rt.Double,
                Sdf.ValueTypeNames.Int : rt.Integer,
                Sdf.ValueTypeNames.Color3f : rt.Color,
                Sdf.ValueTypeNames.Color4f : rt.Color,
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
                 'redshift::RSMathInvVector': rt.rsMathInvVector,
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
                 'redshift::RSColorCorrection': rt.rsColorCorrection,
                 'redshift::StandardVolume' : rt.rsStandardVolume,
                 'redshift::VolumeColorAttribute' : rt.rsVolumeColorAttribute,
                 'redshift::VolumeScalarAttribute' : rt.rsVolumeScalarAttribute,
                 'redshift::ToonMaterial' : rt.rsToonMaterial,
                 'redshift::Contour' : rt.rsContour,
                 'redshift::TonemapPattern' : rt.rsTonemapPattern}

PropertyRemaps = {rt.rsOSLMap : {'OSLCode':'RS_osl_code', 'oslFilename':'RS_osl_file', 'oslSource':'RS_osl_source'},
                  rt.rsTexture: {"scale_x" : "scale", "scale_y": "scale", "offset_x" : "offset", "offset_y" : "offset", "tex0_filename" : "tex0"}}
                      
class RSShaderReaderBase():
    def Read(self, prim, args = None):
        try:
            self.MapLibrary = {}
            
            #TimeConfig
            self.animated = False
            self.animStart = 0
            self.animEnd = 0
            if args != None:
                importSettings = args
                timeMode = importSettings.GetTimeMode()
                if timeMode == maxUsd.ImportTimeMode.CustomRange:
                    self.animStart = importSettings.GetStartTimeCode()
                    self.animEnd = importSettings.GetEndTimeCode()
                    if self.animStart != self.animEnd:
                        self.animated = True
                        
            
            maxNode = rt.rsMaterialOutput()
            handle = rt.GetHandleByAnim(maxNode)
            
            shaderPrim = UsdShade.Shader(prim)
            for input in shaderPrim.GetInputs():
                connections = input.GetAttr().GetConnections()
                propertyName = input.GetBaseName()
                if len(connections) > 0 and hasattr(maxNode, propertyName):
                    MapPropertyName, Map = self.AddNode(prim, propertyName, connections)
                    rt.USDImporter.SetMaterialParamByName(maxNode, propertyName, Map)
            
            self.MapLibrary[prim] = handle
            return handle
            
        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    def AddNode(self, prim, propertyName, connection):
        
        shader = prim.GetPrimAtPath(connection[0].GetPrimPath())
        shaderID = shader.GetAttribute("info:id").Get()
        shaderName = shader.GetName()
        
        MapPropertyName = propertyName
        if not propertyName.endswith("_input"):
            MapPropertyName = propertyName + "_map"

        if not (shaderID in schemaToMax):
                print(shaderID, "is not supported by this reader!")
                return (None, None)
                
        if shader in self.MapLibrary:
            maxNode = rt.getAnimByHandle(self.MapLibrary[shader])
            if hasattr(maxNode, "numIMultipleOutputChannels"):
                MultiOutput = rt.MultiOutputChannelTexmapToTexmap()
                MultiOutput.sourcemap = maxNode
                outPutName = connection[0].pathString.split(":")[1]  #path should have something that does this, but maybe not in python?
                for index in range(1, (maxNode.numIMultipleOutputChannels + 1)):
                    if maxNode.getIMultipleOutputChannelName(index) == outPutName:
                        MultiOutput.outputChannelIndex = index
                maxNode = MultiOutput
            return (MapPropertyName, maxNode) # We should be able to return here, this skips setting properties if the map already existed
        else:
            maxNode = schemaToMax[shaderID]()
            maxNode.name = shaderName
            
        map = True
        if rt.superclassof(maxNode) == rt.material:
            map = False

        if rt.classOf(maxNode) == rt.rsOSLMap: #set these first if its an osl node, or we will not have any paramters to set :D
            if shader.GetAttribute("inputs:RS_osl_code"):
                maxNode.OSLCode = shader.GetAttribute("inputs:RS_osl_code").Get()
            if shader.GetAttribute("inputs:RS_osl_file"):
                try:
                    maxNode.oslFilename = shader.GetAttribute("inputs:RS_osl_file").Get().path
                except:
                    pass #if this isn't correctly defined as a asset type it will fail
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
            tex0attr = shader.GetAttribute("inputs:tex0")
            if tex0attr:
                if "<UDIM>" in tex0attr.Get().path:
                    maxNode.tilingmode = 1

        shaderPrim = UsdShade.Shader(shader)
        for input in shaderPrim.GetInputs():
            connections = input.GetAttr().GetConnections()
            childpropertyName = input.GetBaseName()
            if childpropertyName == 'tex0':
                childpropertyName = 'tex0_filename'
            if hasattr(maxNode, childpropertyName) or hasattr(maxNode, childpropertyName + "_map"):
                if len(connections) > 0:
                    childMapPropertyName, Map = self.AddNode(prim, childpropertyName, connections)
                    if childMapPropertyName:
                        if map:
                            rt.USDImporter.SetTexmapParamByName(maxNode, childMapPropertyName, Map)
                        else:
                            rt.USDImporter.SetMaterialParamByName(maxNode, childMapPropertyName, Map)
                        continue
                
                attr = input.GetAttr()
                value = self.ResolveMaxValue(attr, 0)
                if value == None or getattr(maxNode, childpropertyName) == None:
                    continue #skip doing all the slow stuff
                varying = False
                if self.animated:
                    varying = attr.ValueMightBeTimeVarying()
                animateValue = self.animated and varying
                with pymxs.animate(animateValue):
                    for frame in range(int(self.animStart), int(self.animEnd) + 1):
                        with pymxs.attime(frame):
                            value = self.ResolveMaxValue(attr, frame)
                            try:
                                rt.setProperty(maxNode, childpropertyName, value)
                            except:
                                print("potentially invalid value for: ", childpropertyName, "with value: ", value)
                            if not animateValue:
                                break
                                
                                
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
    
    
    def ResolveMaxValue(self, usdAttr, frame):
        sdfType = usdAttr.GetTypeName()
        if sdfType not in maxTypeToSdf:
            return None
        sdfValue = usdAttr.Get(frame)
        if sdfValue == None:
            return None
            
        maxValue = sdfValue
        if sdfType == Sdf.ValueTypeNames.Color3f:
            maxValue = rt.color(sdfValue[0]*255, sdfValue[1]*255, sdfValue[2]*255, 255)
        elif sdfType == Sdf.ValueTypeNames.Color4f:
            maxValue = rt.point4(sdfValue[0], sdfValue[1], sdfValue[2], sdfValue[3])
        elif sdfType == Sdf.ValueTypeNames.Float3:
            maxValue = rt.point3(sdfValue[0], sdfValue[1], sdfValue[2])
        elif sdfType == Sdf.ValueTypeNames.Asset:
            maxValue = sdfValue.path
            if "<UDIM>" in maxValue:
                maxValue = maxValue.replace("<UDIM>", "*")
                maxValue = glob.glob(maxValue)[0]
            maxValue = self.ResolveAsset(maxValue)
        return maxValue
        
    def ResolveAsset(self, assetPath):
        resolver = Ar.GetResolver()
        resolvedPath = resolver.Resolve(assetPath)
        return str(resolvedPath)
        
    
    @classmethod
    def CanImport(cls, importArgs):
        return maxUsd.ShaderReader.ContextSupport.Supported
        

class RSShaderReader(maxUsd.ShaderReader):
    def Read(self):
        reader = RSShaderReaderBase()
        prim = self.GetUsdPrim() #Turn this into a max material
        args = self.GetArgs()
        
        handle = reader.Read(prim, args)
        
        
        
        self.RegisterCreatedMaterial(prim.GetPrimPath(), handle) #Register here and hopefully max will assign the material we made?
        return True
        
    @classmethod
    def CanImport(cls, importArgs):
        return maxUsd.ShaderReader.ContextSupport.Supported
        
        
maxUsd.ShaderReader.Register(RSShaderReader, "redshift_usd_material")