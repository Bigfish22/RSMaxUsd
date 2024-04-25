# Job Contexts allow to customize several options during a maxUsd export
#   - 'chaser'
#   - 'chaserArgs'
#   - 'convertMaterialsTo'
#
# This sample will add a "Custom Context Demo" option in the "PlugIn configuration" drop down in maxUsd exports
def RSShaderImporterContext():
    # build a dictionary of the options to set using the context
    extraArgs = {}
    extraArgs['chaser']  = ['RSImportChaser']
    extraArgs['convertMaterialsTo']  = ['redshift_usd_material']
    return extraArgs

import maxUsd
maxUsd.ShadingModeRegistry.RegisterImportConversion("RedshiftShaders", "Redshift", "Redshift Shaders", "import redshift usd materials")
maxUsd.JobContextRegistry.RegisterImportJobContext("Redshift", "Redshift", "Custom plug-in configuration", RSShaderImporterContext)