def RSShaderImporterContext():
    extraArgs = {}
    extraArgs['chaser']  = ['RSImportChaser']
    extraArgs['convertMaterialsTo']  = ['redshift_usd_material']
    return extraArgs

import maxUsd
maxUsd.ShadingModeRegistry.RegisterImportConversion("RedshiftShaders", "Redshift", "Redshift Shaders", "import redshift usd materials")
maxUsd.JobContextRegistry.RegisterImportJobContext("Redshift", "Redshift", "Custom plug-in configuration", RSShaderImporterContext)