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

def RSShaderWriterContext():
    extraArgs = {}
    extraArgs['chaser']  = ['RSObjectProperties']
    extraArgs['chaserNames']  = ['RSObjectProperties']
    extraArgs['convertMaterialsTo']  = ['redshift_usd_material']
    return extraArgs

def RSRenderSettingsContext():
    extraArgs = {}
    extraArgs['chaser']  = ['RSRenderSettingsChaser']
    extraArgs['chaserNames']  = ['RSRenderSettingsChaser']
    return extraArgs
    
def RSmtlxWriterContext():
    extraArgs = {}
    extraArgs['chaser'] = ['RSObjectProperties']
    extraArgs['chaserNames'] = ['RSObjectProperties']
    extraArgs['convertMaterialsTo']  = ['mtlxstandard_surface']
    return extraArgs

import maxUsd
maxUsd.JobContextRegistry.RegisterExportJobContext("redshift_usd_material", "Redshift", "Configuration for exporting Redshift materials", RSShaderWriterContext)
maxUsd.JobContextRegistry.RegisterExportJobContext("mtlxstandard_surface", "Redshift mtlx", "Configuration for exporting Redshift materials", RSmtlxWriterContext)
maxUsd.JobContextRegistry.RegisterExportJobContext("redshift", "Redshift Render Settings", "Exports Render Redshift Render Settings", RSRenderSettingsContext)
maxUsd.ShadingModeRegistry.RegisterExportConversion("redshift_usd_material", "Redshift", "Redshift", "Exports bound materials as a RS UsdShade network.")
maxUsd.ShadingModeRegistry.RegisterExportConversion("mtlxstandard_surface", "mtlx", "mtlx", "Exports bound materials as a mtlx UsdShade network.")