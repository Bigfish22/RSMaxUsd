# Job Contexts allow to customize several options during a maxUsd export
#   - 'chaser'
#   - 'chaserArgs'
#   - 'convertMaterialsTo'
#
# This sample will add a "Custom Context Demo" option in the "PlugIn configuration" drop down in maxUsd exports
def RSShaderWriterContext():
    # build a dictionary of the options to set using the context
    extraArgs = {}
    extraArgs['chaser']  = ['RSObjectProperties']
    extraArgs['convertMaterialsTo']  = ['redshift_usd_material']
    return extraArgs

import maxUsd
maxUsd.JobContextRegistry.RegisterExportJobContext("redshift_usd_material", "Redshift", "Cnnfiguration for exporting Redshift materials", RSShaderWriterContext)
maxUsd.ShadingModeRegistry.RegisterExportConversion("redshift_usd_material", "Redshift", "Redshift", "Exports bound materials as a RS UsdShade network.")