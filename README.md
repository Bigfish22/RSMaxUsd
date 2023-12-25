# RSMaxUsd
max plugins for importing and exporting redshift USD data.

Currently only handles shader writing and reading. Lights and redshift specific objects will come later.

## Install instructions
clone into your autodesk application plugins folder:
* C:\ProgramData\Autodesk\ApplicationPlugins\

## What can this do?
* export rs materials, maps and shader graphs
* import rs materials, maps and shader graphs from usd into max
* materials exported will render within the redshift hydra delegate in houdini/solaris.

## Limitations
* only supports rs nodes
* some nodes will not appear in hydra do to extreme differences between the max and houdini versions. (rs state being an example)
* osl nodes will cause the export to fail (This will be fixed soon)
* rs bitmap is converted to rs texture
* ramp UI inputs are not supported (effects brick and tile shaders)
* no ramp or composite support
* legacy rs nodes are not supported (rs material, rs normal etc)
* displacement in blend materials is not yet supported.
* animated materials will not export keys