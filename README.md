# Delivery Robot PCB

KiCad design files for the ECE49022 Team 22 senior design delivery robot control board.

This repository is the shared workspace for the board schematic, PCB layout, project libraries and design documentation.

## System overview

The current schematic includes an STM32F091RC microcontroller core, programming/debug and UART headers, reset and boot circuitry, clock and decoupling components, test points, and power conversion from 12 V to 5 V and 3.3 V.

Motor-driver and IMU interfaces are part of the planned system and still need to be completed and reviewed in the board design.

## Getting started

1. Install KiCad 10 with its standard symbol and footprint libraries.
2. Clone this repository.
3. Open delivery_robot_1.kicad_pro in KiCad Manager.
4. Open delivery_robot_1.kicad_sch to view the complete schematic. Use the Schematic Hierarchy panel to navigate between sheets.

Custom symbol and footprint libraries are included and registered in the project library tables. Keep the directory structure intact so project-relative library paths resolve.

## Repository contents

| Path | Purpose |
| --- | --- |
| delivery_robot_1.kicad_pro | Active KiCad project settings |
| delivery_robot_1.kicad_sch | Main board schematic |
| LDO_3V3.kicad_sch | Hierarchical 3.3 V power supply sheet |
| libs/ | Custom buck converter symbols and footprints |
| LDO_KiCad/ | Reusable LDO example, libraries and footprint review |
| sym-lib-table, fp-lib-table | Project-specific library configuration |
| docs/ | Subsystem documentation and design notes |
| validation/ | Connectivity checks and reference netlist |
| system-ERC-report.txt | Saved electrical rules check results |
| system-netlist.xml | Exported system connectivity |
| system-preview/ | Rendered schematic sheets |
| received-project-settings/ | Archived initial settings; not the active project |

Power supply details are documented in [docs/power-supply.md](docs/power-supply.md). Earlier simulation notes are in [STM32-LDO-design.md](STM32-LDO-design.md).

## Design status

The project is in schematic development. No system PCB layout has been committed yet.

The saved ERC report from October 5, 2026 contains 7 errors and 55 warnings. Remaining work includes reviewing power connectivity and symbol definitions, completing peripheral interfaces, finalizing component values and footprints, and designing and checking the PCB layout.

Saved reports describe the checked revision. Regenerate them after relevant design changes.

## Team workflow

- Use the active delivery_robot_1 project for board work.
- Pull current changes before editing and coordinate ownership of schematic sheets and the PCB.
- Work on branches and review changes before merging.
- Save files in KiCad before committing. Include required project-local libraries with design changes.
- Run ERC after schematic changes and DRC after layout changes. Review outstanding findings before ordering boards.

Editing locks, local UI settings and automatic backups are excluded from Git. Edit the native KiCad sources directly; regenerating files from older scripts may overwrite manual changes.
