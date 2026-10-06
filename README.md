# Delivery robot PCB

Private team repository: https://github.com/ECE49022Team22/delivery-robot-pcb

## Open the integrated schematic

Open delivery_robot_1.kicad_pro in KiCad 10, then delivery_robot_1.kicad_sch. LDO Power (page 2) contains the TPS7A8101 5 V to 3.3 V regulator.

The system schematic and custom buck symbol/footprint libraries came from the top-level files in senior_design.zip. That version has no missing child-sheet references. No routed system PCB was supplied.

## Integrated LDO

- Input: +5V, 2A from the TPS54202 buck output, selected by the user. The separate +5V, 6A rail is not connected to this input.
- Output: +3V3 feeds STM32 supply pins 1, 19, 32, 48 and 64, digital decoupling, programming-header supply, and FB2's input for the separate +3.3VA analog rail.
- Former VDD power symbols now use +3V3 so the MCU is actually connected to the LDO output. Original component values and other net connections are preserved.
- Regulator U4, divider R8/R9, capacitors C24-C27. LDO_3V3.kicad_sch is the integrated child. The LDO_KiCad directory retains the independent reusable example.
- Project library tables include both teammate custom buck libraries and the LDO libraries, using project-relative paths.
- Added the previously missing footprint library table and corrected the two custom buck footprint library names.

## Validation and remaining work

The actual KiCad-exported netlist passed validation/verify_integration.py: all five LDO nets, all nine U4 pads, MCU supply connections, analog filter input, component-reference uniqueness, and preservation of existing component values/connections except the intended VDD/+3V3 merge.

ERC before integration: 9 errors and 55 warnings. After integration: 7 errors and 55 warnings, with no findings in the LDO child. Remaining power-driver errors and system warnings require review; do not declare the full board production-ready. Several existing system components still lack footprints or finalized values.

The 1 A figure is combined 3.3 V rail capacity. At 5 V input, full-load LDO dissipation is approximately 1.7 W. PCB thermal copper/vias, actual loads and component procurement remain to be finalized. Buck footprints are present and resolve; their physical dimensions were not reviewed in this integration.

system-ERC-report.txt and system-netlist.xml contain the system checks. system-preview contains rendered sheets. The archived initial project settings are in received-project-settings; they are not the active project.

## Team workflow

Use this repository's delivery_robot_1 project for combined-system work. Save KiCad files before committing. Avoid concurrent edits to the same sheet or PCB. Review schematic changes before merging. Locks, local UI settings and automatic backups are excluded from Git.

Do not rerun the original LDO generator over these sources. Edit the native KiCad project files.
