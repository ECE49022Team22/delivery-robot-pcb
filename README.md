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
| Buck_5V_2A.kicad_sch | Hierarchical 12 V to 5 V, 2 A buck sheet (TPS54202) |
| Buck_5V_6A.kicad_sch | Hierarchical 12 V to 5 V, 6 A buck sheet (TPSM63606), feeds the Pi 5 |
| Buck_5V_6A_AUX.kicad_sch | Second 12 V to 5 V, 6 A buck sheet (TPSM63606), +5V_AUX rail |
| LDO_3V3.kicad_sch | Hierarchical 3.3 V power supply sheet |
| Pi5_Interface.kicad_sch | Raspberry Pi 5 UART (J13, R12/R13 100R) and fused power output (F2, J14) |
| GPIO_Breakout.kicad_sch | 2.54 mm headers J8-J10 for all spare STM32 pins (global labels) |
| Power_Indicators.kicad_sch | Green power LED per rail (+12V, +5V_PI, +5V_AUX, +5V_SYS, +3V3) and yellow STM32 debug LEDs (PA5, PB12-PB14) |
| Motor_Control.kicad_sch | MDD20A driver terminals (J6, J16) and encoder terminals (J7, J15) for two motors, 100R series resistors, USBLC6-4SC6 ESD arrays on J6 (U6) and J7 (U7), STM32 pin table |
| Test_Points.kicad_sch | Power test points: J5 1x06 2.54 mm header (GND, +3V3, +3.3VA, +5V_SYS, +5V_AUX, +12V) and TP3 scope GND loop |
| IMU_Interface.kicad_sch | Off-board BNO085: J11 STEMMA QT I2C, J12 INT/RST with 100R series resistors, DNP I2C pull-ups |
| delivery_robot_1.pdf | Plot of all schematic sheets, regenerated automatically on every schematic commit |
| tools/hooks/ | Git hooks (pre-commit regenerates the schematic PDF) |
| libs/ | Project libraries: custom buck converter symbols/footprints, and project_symbols.kicad_sym (STM32F091RCTx and Crystal_GND24 frozen at the versions this design uses) |
| LDO_KiCad/ | Reusable LDO example, libraries and footprint review |
| sym-lib-table, fp-lib-table | Project-specific library configuration |
| docs/ | Subsystem documentation and design notes |
| validation/ | Connectivity checks and reference netlist |
| system-ERC-report.txt | Saved electrical rules check results |
| system-netlist.xml | Exported system connectivity |
| system-preview/ | Rendered schematic sheets |
| received-project-settings/ | Archived initial settings; not the active project |

Power supply details are documented in [docs/power-supply.md](docs/power-supply.md). Earlier simulation notes are in [STM32-LDO-design.md](STM32-LDO-design.md).

Component-selection rationale is in [docs/passive-selection-review.md](docs/passive-selection-review.md), [docs/clock-selection.md](docs/clock-selection.md) and [docs/fuse-selection.md](docs/fuse-selection.md). The fuse selection includes both the PCB-mounted holder and its separately purchased insert.

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
- Enable the repository hooks once per clone with `git config core.hooksPath tools/hooks`. The pre-commit hook then re-plots delivery_robot_1.pdf from the staged schematic files and adds it to any commit that changes a `.kicad_sch` or `.kicad_pro` file. It needs KiCad installed; set `KICAD_CLI` if kicad-cli is not in the default location.

Editing locks, local UI settings and automatic backups are excluded from Git. Edit the native KiCad sources directly; regenerating files from older scripts may overwrite manual changes.
