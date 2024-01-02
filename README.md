# RSMaxUsd
max plugins for importing and exporting redshift USD data.

Handles material export and import and light export, more features to come.

## Install instructions
clone into your autodesk application plugins folder:
* C:\ProgramData\Autodesk\ApplicationPlugins\

## What can this do?
* export rs materials, maps and shader graphs
* import rs materials, maps and shader graphs from usd into max
* export rs lights as usd lights.
* materials exported will render within the redshift hydra delegate in houdini/solaris.

## Limitations
* only supports rs nodes
* some nodes will not appear in hydra due to extreme differences between the max and houdini versions. (rs state being an example)
* rs bitmap is converted to rs texture
* ramp UI inputs are not supported (effects rs brick)
* no ramp or composite support
* legacy rs nodes are not supported (rs material, rs normal etc)
* displacement in blend materials is not yet supported.
* animated materials will not export keys