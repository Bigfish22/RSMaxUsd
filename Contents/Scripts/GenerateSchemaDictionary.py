from pymxs import runtime as rt

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
                rt.rsColorConstant : ['RSColorConstant', 'out'],
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
                rt.rsStoreColorToAOV : ['StoreColorToAOV', 'outColor']}
                    

schemaToMax = {}

for i in maxShaderToRS:
    maxClass = i
    coreClass = "redshift::" + maxShaderToRS[i][0]
    schemaToMax[coreClass] = i.internalName
    
print(schemaToMax)