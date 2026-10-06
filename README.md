# Delivery robot PCB

KiCad 10 project workspace for the senior design delivery robot.

## Current status: system schematic transfer incomplete

The teammate supplied delivery_robot.kicad_pro (project settings) and an editing lock file. The lock is deliberately excluded. Neither file contains the schematic's components or wires.

The project settings reference Root and Microcontroller Associated Elements sheets. The actual root delivery_robot.kicad_sch and all referenced child .kicad_sch files have not been received. Do not create a blank root schematic to replace the missing design.

Ask the teammate for a ZIP of the complete KiCad project directory containing:
- delivery_robot.kicad_pro and delivery_robot.kicad_sch.
- All child .kicad_sch files.
- delivery_robot.kicad_pcb if PCB layout has started.
- sym-lib-table, fp-lib-table, any custom .kicad_sym libraries and .pretty footprint folders.
- Any external simulation models, custom design-rule .kicad_dru files, and custom 3D models the project uses.

Standard KiCad libraries can come from the matching KiCad installation. Custom libraries should use project-relative paths such as ${KIPRJMOD}. A modern schematic embeds symbols for display, but that does not ensure custom libraries, footprints or models are available for editing and PCB layout.

Library completeness, system ERC and LDO integration cannot be checked until the actual schematic arrives.

## Available LDO module

Open LDO_KiCad/STM32_LDO.kicad_pro to inspect the standalone 5 V to 3.3 V TPS7A8101 LDO example. The reusable child is LDO_KiCad/LDO_Power.kicad_sch. Its local symbol and footprint libraries are included.

See LDO_KiCad/README.md for importing the child sheet into the system project. Merge library-table entries; do not overwrite the system's existing tables. Reannotate references as needed, connect VIN_5V, VOUT_3V3 and GND, and run ERC on the combined design.

The 1 A figure is the combined 3.3 V rail capacity. At 5 V input it can dissipate approximately 1.7 W; final PCB thermal design remains pending. This repository contains no routed system PCB. The board in footprint-verification is only a footprint inspection fixture.

## Team workflow

Save KiCad files before committing. Avoid simultaneous edits to the same schematic sheet or PCB file. Use separate branches and review changes before merging.

This repository tracks design sources, project-local libraries and review evidence. It excludes editing locks, local UI settings and automatic backups. The original working LDO folder remains separate; use this repository's copy for team work from now on.

Private team repository: https://github.com/ECE49022Team22/delivery-robot-pcb
