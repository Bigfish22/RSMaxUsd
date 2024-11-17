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
import os
from pxr import Usd, Sdf, UsdRender, UsdGeom, Gf
from pymxs import runtime as rt
import traceback

maxTypeToSdf = {rt.Double : Sdf.ValueTypeNames.Float,
                rt.Integer : Sdf.ValueTypeNames.Int,
                rt.Color : Sdf.ValueTypeNames.Color3f,
                rt.BooleanClass : Sdf.ValueTypeNames.Bool,
                rt.string : Sdf.ValueTypeNames.String,
                rt.name : Sdf.ValueTypeNames.String,
                rt.point3 : Sdf.ValueTypeNames.Color3f}
                    
aovSourceMap = {"rsAmbientOcclusionRenderElement" : {"sourceName" : "rs:ao"},
                "RsBackground" : {"sourceName" : "rs:background"},
                "RsBeauty" : {"sourceName" : "rs:beauty"},
                "RsBumpNormals" : {"sourceName" : "rs:bnormals"},
                "RsCaustics" : {"sourceName" : "rs:caustics"},
                "RsCausticsRaw" : {"sourceName" : "rs:caustics_raw"},
                "RsCryptomatte" : {"sourceName" : "rs:cryptomatte"},
                "RsCustom" : {"sourceName" : "rs:custom"},
                "RsDepth" : {"sourceName" : "rs:depth"},
                "RsDiffuseFilter" : {"sourceName" : "rs:diffuse_filter"},
                "RsDiffuseLighting" : {"sourceName" : "rs:diffuse"},
                "RsDiffuseLightingRaw" : {"sourceName" : "rs:diffuse_raw"},
                "RsEmission" : {"sourceName" : "rs:emission"},
                "RsGlobalIllumination" : {"sourceName" : "rs:gi"},
                "RsGlobalIlluminationRaw" : {"sourceName" : "rs:gi_raw"},
                "RsMatte" : {"sourceName" : "rs:matte"},
                "RsMotionVectors" : {"sourceName" : "rs:motionvectors"},
                "RsNormals" : {"sourceName" : "rs:normals"},
                "RsObjectID" : {"sourceName" : "rs:objectid"},
                "RsObjectSpaceBumpNormals" : {"sourceName" : "rs:object_bump_normal"},
                "RsObjectSpacePositions" : {"sourceName" : "rs:object_position"},
                "RsPuzzleMatte" : {"sourceName" : "rs:puzzle"},
                "RsReflections" : {"sourceName" : "rs:reflections"},
                "RsReflectionsFilter" : {"sourceName" : "rs:reflections_filter"},
                "RsReflectionsRaw" : {"sourceName" : "rs:reflections_raw"},
                "RsRefractions" : {"sourceName" : "rs:refractions"},
                "RsRefractionsFilter" : {"sourceName" : "rs:refractions_filter"},
                "RsRefractionsRaw" : {"sourceName" : "rs:refractions_raw"},
                "RsShadows" : {"sourceName" : "rs:shadows"},
                "RsSpecularLighting" : {"sourceName" : "rs:specular"},
                "rsSubSurfaceScatterRenderElement" : {"sourceName" : "rs:sss"},
                "RsSubSurfaceScatterRaw" : {"sourceName" : "rs:sss_raw"},
                "RsTotalDiffuseLightingRaw" : {"sourceName" : "rs:total_diffuse_raw"},
                "RsTotalTranslucencyLightingRaw" : {"sourceName" : "rs:total_translucency_raw"},
                "RsTranslucencyFilter" : {"sourceName" : "rs:translucency_filter"},
                "RsTranslucencyGIRaw" : {"sourceName" : "rs:translucency_gi_raw"},
                "RsTranslucencyLightingRaw" : {"sourceName" : "rs:translucency_raw"},
                "RsVolumeDepth" : {"sourceName" : "rs:volumeDepth"},
                "RsVolumeFogEmission" : {"sourceName" : "rs:volume_fog_emission"},
                "RsVolumeFogTint" : {"sourceName" : "rs:volume_fog_tint"},
                "RsVolumeLighting" : {"sourceName" : "rs:volume"},
                "RsWorldPosition" : {"sourceName" : "rs:world"}}

class RSRenderSettingsChaser(maxUsd.ExportChaser):
    def __init__(self, factoryContext, *args, **kwargs):
        super(RSRenderSettingsChaser, self).__init__(factoryContext, *args, **kwargs)
        self.primsToNodeHandles = factoryContext.GetPrimsToNodeHandles()
        self.stage = factoryContext.GetStage()

    def PostExport(self):
        try:
            if "Redshift" not in rt.getClassName(rt.renderers.current):
                return False
                
                
            UsdGeom.Scope.Define(self.stage, "/Render")
            UsdGeom.Scope.Define(self.stage, "/Render/Products")
            UsdGeom.Scope.Define(self.stage, "/Render/Products/Vars")
            
            #This holds render settings
            renderSettings = UsdRender.Settings.Define(self.stage, "/Render/Redshift1")
            renderSettings.CreateResolutionAttr().Set(Gf.Vec2i(rt.renderWidth, rt.renderHeight))
            renderSettingsPrim = self.stage.GetPrimAtPath("/Render/Redshift1")  #I thought inheritance was supposed to make it so I don't have to do chaotic stuff...
            props = rt.getPropNames(rt.renderers.current)

            #Get The camera for rendering
            cam = rt.viewport.GetCamera()
            if cam:
                nodeHandle = cam.handle
                CameraPrimPath = list(self.primsToNodeHandles.keys())[list(self.primsToNodeHandles.values()).index(nodeHandle)]
                camRel = renderSettingsPrim.CreateRelationship("camera")
                camRel.SetTargets([CameraPrimPath])

            #Redshift needs this to save a file
            renderSettingsPrim.CreateAttribute("redshift:global:RS_outputEnable", Sdf.ValueTypeNames.Bool).Set(True)

            renderSettingSkip = ["BlockSize"]
            for prop in props:
                try:
                    #TODO: Remap any render settings where the names do not match max.
                    if str(prop) in renderSettingSkip:
                        continue
                    propAttr = getattr(rt.renderers.current, str(prop))
                    type = rt.classOf(propAttr)
                    if type == rt.name:
                        propAttr = str(propAttr)
                    if type == rt.color:
                        propAttr = (propAttr.r/255, propAttr.g/255, propAttr.b/255)

                    renderSettingsPrim.CreateAttribute("redshift:global:" + str(prop), maxTypeToSdf[type]).Set(propAttr)
                except:
                    pass

            #Block sizes seem to use the index of the enum                              #curious
            blockSizes = ["RS_BLOCKSIZE_64", "RS_BLOCKSIZE_128", "RS_BLOCKSIZE_256", "512"]
            blockSizeIndex = blockSizes.index(str(rt.renderers.current.BlockSize))
            renderSettingsPrim.CreateAttribute("redshift:global:BlockSize", Sdf.ValueTypeNames.String).Set(str(blockSizeIndex))

            #Render Product (the actual target to disk)
            renderProduct = UsdRender.Product.Define(self.stage, "/Render/Products/MultiLayer")
            renderProduct.CreateResolutionAttr().Set(Gf.Vec2i(rt.renderWidth, rt.renderHeight))
            self.generateFilePaths(renderSettingsPrim, renderProduct)
            renderSettings.CreateProductsRel().AddTarget("/Render/Products/MultiLayer")
            
            #Beauty pass setup
            colorAov = UsdRender.Var.Define(self.stage, "/Render/Products/Vars/color")
            colorAov.CreateSourceNameAttr().Set("color")
            colorAov.CreateDataTypeAttr().Set("color4f")
            colorAov.CreateSourceTypeAttr().Set("raw")
            
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:clearValue", Sdf.ValueTypeNames.Int).Set(0)
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:format", Sdf.ValueTypeNames.Token).Set("color4h")
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:multiSampled", Sdf.ValueTypeNames.Bool).Set(False)
            colorAov.GetPrim().CreateAttribute("driver:parameters:aov:name", Sdf.ValueTypeNames.String).Set("rgba")
            
            
            orderedVarsRel = renderProduct.GetOrderedVarsRel()
            orderedVarsRel.AddTarget("/Render/Products/Vars/color")
            
            #Aovs and there associated settings
            ElementManager = rt.maxOps.GetCurRenderElementMgr()
            for i in range(0, ElementManager.NumRenderElements()):
                rendElement = ElementManager.GetRenderElement(i)
                elementClass = str(rt.classOf(rendElement))
                if elementClass in aovSourceMap:
                    elementMap = aovSourceMap[elementClass]
                    aovPath = Sdf.Path("/Render/Products/Vars").AppendPath(rendElement.elementName)
                    aov = UsdRender.Var.Define(self.stage, aovPath)
                    aov.CreateSourceNameAttr().Set(elementMap["sourceName"])
                    aov.GetPrim().CreateAttribute("driver:parameters:aov:name", Sdf.ValueTypeNames.String).Set(rendElement.elementName)
                    orderedVarsRel.AddTarget(aovPath)

            #Volume scattering
            atmosCount = rt.numAtmospherics
            for i in range(atmosCount):
                atmos = rt.getAtmospheric(i+1)
                if rt.classOf(atmos) == rt.rsVolumeScattering:
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingEnabled", Sdf.ValueTypeNames.Bool).Set(True)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingScatteringCoefficient", Sdf.ValueTypeNames.Float).Set(atmos.scatteringAmount)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingExtinctionCoefficient", Sdf.ValueTypeNames.Float).Set(atmos.attenuationAmount)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingApplyExposureCompensation", Sdf.ValueTypeNames.Bool).Set(atmos.cameraRayContributionScale) 
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingFogAmbient", Sdf.ValueTypeNames.Float3).Set((atmos.fogEmission.r/255, atmos.fogEmission.g/255, atmos.fogEmission.b/255))
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingFogHeight", Sdf.ValueTypeNames.Float).Set(atmos.fogHeight)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingFogHorizonBlur", Sdf.ValueTypeNames.Float).Set(atmos.fogHorizonBlur)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingFogNormal", Sdf.ValueTypeNames.Float3).Set(Gf.Vec3f(atmos.fogGroundNormalX, atmos.fogGroundNormalZ, atmos.fogGroundNormalY))
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingFogOrigin", Sdf.ValueTypeNames.Float3).Set(Gf.Vec3f(atmos.fogGroundPointX, atmos.fogGroundPointY, atmos.fogGroundPointZ))
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingPhase", Sdf.ValueTypeNames.Float).Set(atmos.phase)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingRayContributionCamera", Sdf.ValueTypeNames.Float).Set(atmos.cameraRayContributionScale)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingRayContributionEnvironment", Sdf.ValueTypeNames.Float).Set(atmos.environmentRayContributionScale)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingRayContributionGI", Sdf.ValueTypeNames.Float).Set(atmos.GIRayContributionScale)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingRayContributionReflection", Sdf.ValueTypeNames.Float).Set(atmos.reflectionRayContributionScale)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingReplaceAlphaOnEnvironment",   Sdf.ValueTypeNames.Bool).Set(atmos.environmentAlphaReplace)
                    renderSettingsPrim.CreateAttribute("redshift:global:VolLightingTint", Sdf.ValueTypeNames.Float3).Set((atmos.tint.r/255, atmos.tint.g/255, atmos.tint.b/255))
                    #renderSettingsPrim.CreateAttribute("redshift:global:VolLightingTintShader"
            
        except Exception as e:
            print('Write - Error: %s' % str(e))
            print(traceback.format_exc())
            return False
        
        return True
        
    def generateFilePaths(self, renderSettings, renderProduct):
        productName = renderProduct.CreateProductNameAttr()
        rsFilePathAttribute = renderSettings.CreateAttribute("redshift:global:RS_outputFileName", Sdf.ValueTypeNames.String)
        if rt.rendTimeType == 1:
            productName.Set(rt.rendOutputFilename)
            rsFilePathAttribute.Set(rt.rendOutputFilename)
            return
        elif rt.rendTimeType == 2:
            for i in range(int(rt.animationRange.start.frame), int(rt.animationRange.end.frame) + 1):
                pathSplit = os.path.splitext(rt.rendOutputFilename)
                finalPath = f"{pathSplit[0]}_{i:0>{4}}{pathSplit[1]}",
                productName.Set(finalPath, i)
                rsFilePathAttribute.Set(finalPath, i)
            return
        elif rt.rendTimeType == 3:
            for i in range(int(rt.rendStart.frame), int(rt.rendEnd.frame) + 1):
                pathSplit = os.path.splitext(rt.rendOutputFilename)
                finalPath = f"{pathSplit[0]}_{i:0>{4}}{pathSplit[1]}"
                productName.Set(finalPath, i)
                rsFilePathAttribute.Set(finalPath, i)
            return
        return
            
        
maxUsd.ExportChaser.Register(RSRenderSettingsChaser, "RSRenderSettingsChaser", "Redshift object Properties", "Chaser to export RS Object properties")