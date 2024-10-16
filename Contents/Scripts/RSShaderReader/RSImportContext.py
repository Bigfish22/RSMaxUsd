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

def RSShaderImporterContext():
    extraArgs = {}
    extraArgs['chaser']  = ['RSImportChaser']
    extraArgs['chaserNames']  = ['RSImportChaser']
    extraArgs['convertMaterialsTo']  = ['redshift_usd_material']
    return extraArgs

import maxUsd
maxUsd.ShadingModeRegistry.RegisterImportConversion("RedshiftShaders", "Redshift", "Redshift Shaders", "import redshift usd materials")
maxUsd.JobContextRegistry.RegisterImportJobContext("Redshift", "Redshift", "Custom plug-in configuration", RSShaderImporterContext)