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

def RSRenderSettingsContext():
    # build a dictionary of the options to set using the context
    extraArgs = {}
    extraArgs['chaser']  = ['RSRenderSettingsChaser']
    return extraArgs
    
def RSmtlxWriterContext():
    # build a dictionary of the options to set using the context
    extraArgs = {}
    extraArgs['chaser']  = ['RSObjectProperties']
    extraArgs['convertMaterialsTo']  = ['mtlxstandard_surface']
    return extraArgs

import maxUsd
maxUsd.JobContextRegistry.RegisterExportJobContext("redshift_usd_material", "Redshift", "Configuration for exporting Redshift materials", RSShaderWriterContext)
maxUsd.JobContextRegistry.RegisterExportJobContext("mtlxstandard_surface", "Redshift mtlx", "Configuration for exporting Redshift materials", RSmtlxWriterContext)
maxUsd.JobContextRegistry.RegisterExportJobContext("redshift", "Redshift Render Settings", "Exports Render Redshift Render Settings", RSRenderSettingsContext)
maxUsd.ShadingModeRegistry.RegisterExportConversion("redshift_usd_material", "Redshift", "Redshift", "Exports bound materials as a RS UsdShade network.")
maxUsd.ShadingModeRegistry.RegisterExportConversion("mtlxstandard_surface", "mtlx", "mtlx", "Exports bound materials as a mtlx UsdShade network.")