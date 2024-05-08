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
import usd_utils
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

class RSMtlxWriter(maxUsd.ShaderWriter):
    def Write(self):
        try:
            material = rt.GetAnimByHandle(self.GetMaterial())

            # create the Shader prim
            nodeShader = UsdShade.Shader.Define(self.GetUsdStage(), self.GetUsdPath())
            nodeShader.CreateIdAttr("ND_standard_surface_surfaceshader")
            
            self.SetUsdPrim(nodeShader.GetPrim())
            return True

        except Exception as e:
            print('Write() - Error: %s' % str(e))
            print(traceback.format_exc())
            
    @classmethod
    def CanExport(cls, exportArgs):
        if exportArgs.GetConvertMaterialsTo() == "mtlxstandard_surface":
            return maxUsd.ShaderWriter.ContextSupport.Supported
        return maxUsd.ShaderWriter.ContextSupport.Unsupported

maxUsd.ShaderWriter.Register(RSMtlxWriter, "RS Standard Material")