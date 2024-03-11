# RSMaxUsd
max plugins for importing and exporting redshift USD data.

Handles material, light, and proxy export and import.

## Install instructions
1. Install the latest max usd plugin
1. Clone into your autodesk application plugins folder: **C:\ProgramData\Autodesk\ApplicationPlugins**
1. Copy the files from:  
**C:\ProgramData\Redshift\Plugins\Solaris\<LatestVerison>\RSHydraSchemas\resources**
into:  
**C:\ProgramData\Autodesk\ApplicationPlugins\RSMaxUsd\Contents\Scripts\resources**
## What can this do?
* export rs materials, maps and shader graphs
* import rs materials, maps and shader graphs from usd into max
* export rs lights as usd lights.
* import usd lights as redshift lights. (prim reader must be manually loaded for now)
* export rs proxies
* import rs proxies
* export rs Volumes to UsdVolume
* export rs mesh params and object properties
* materials, lights, Volumes and proxies exported will render within the redshift hydra delegate in solaris.

## Limitations
* MATERIAL NODES WITH IDENTICAL NAMES IN A SINGLE GRAPH CAN CAUSE HOUDINI TO HANG!
* only supports rs nodes + (max composite and max vertex color)
* some nodes will not appear in hydra due to extreme differences between the max and houdini versions. (rs state being an example)
* rs bitmap is converted to rs texture
* ramp UI inputs are not supported (effects rs brick)
* no gradient ramp
* legacy rs nodes are not supported (rs material, rs normal etc)
* displacement in blend materials is not yet supported.
