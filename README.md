# Delivery Robot PCB

KiCad design files for the ECE49022 Team 22 senior design delivery robot control board.

This repository is the shared workspace for the board schematic, PCB layout, project libraries and design documentation.

## System overview

The current schematic includes an STM32F091RC microcontroller core, programming/debug and UART headers, reset and boot circuitry, clock and decoupling components, test points, and power conversion from 12 V to 5 V and 3.3 V. The 12 V input has a fuse, a reverse-battery P-FET, a TVS and a battery-voltage sense. The board also feeds four 5 V peripheral ports, a latch servo (half-duplex UART plus a fused battery feed), two MDD20A motor channels and two encoders, and links to the Raspberry Pi 5 (UART, AUX enable from the Pi 3V3, STM32 reset and BOOT0). An INA228 measures battery current and charge on an off-board shunt in the battery negative lead, and a buffered 5 V data line drives the payload-compartment WS2812B interior light.

The IMU (BNO085) is not on this board; it is wired to the robot off-board.

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
| Buck_5V_2A.kicad_sch | Hierarchical 12 V to 5 V, 2 A buck sheet (TPS54202H, U3) |
| Buck_5V_6A.kicad_sch | Hierarchical 12 V to 5 V, 6 A buck sheet (TPS56637, U2), feeds the Pi 5 |
| Buck_5V_6A_AUX.kicad_sch | Second 12 V to 5 V, 6 A buck sheet (TPS56637, U5), +5V_AUX rail |
| LDO_3V3.kicad_sch | Hierarchical 3.3 V power supply sheet |
| Pi5_Interface.kicad_sch | Raspberry Pi 5 link J13 (6-pin JST XH: UART via R12/R13 1k, GND, Pi 3V3 for the AUX enable, STM32 reset Q2, BOOT0) and Pi power output J14 |
| GPIO_Breakout.kicad_sch | 2x8 2.54 mm expansion header J8 with spare MCU pins only: 1 +3V3, 2/16 GND, ADC (PC0/PA1/PA4), SPI2 (PB13 SCK, PC2 MISO, PB15 MOSI, PB9 CS), PWM (PC6/PC7), USART3 (PC10/PC11), I2C1 (PB6/PB7, now a shared bus with on-board 4.7k pull-ups R56/R57 and the INA228 U13 at 0x40). Unused MCU pins are no-connect. |
| Power_Indicators.kicad_sch | Green power LED per rail (+12V, +5V_PI, +5V_AUX, +5V_SYS, +3V3) and yellow STM32 debug LEDs (PA5, PB12, PB14) |
| Motor_Control.kicad_sch | MDD20A driver terminals (J6, J16) and encoder terminals (J7, J15) for two motors, PWM pull-downs, PTC on each driver ground, encoder buffers U9/U10 (74LVC2G17) with 1k + 1 nF filters, PTC-protected encoder supplies, USBLC6-4SC6 ESD arrays U6 (J6 + J16) and U7 (J7 + J15), STM32 pin table |
| Test_Points.kicad_sch | Power test points: J5 1x06 2.54 mm header (+12V, GND, +5V_AUX, +5V_SYS, +3V3, +3.3VA) and TP3 scope GND loop |
| Input_Protection.kicad_sch | Reverse-battery P-FET Q1 with gate clamp, SMBJ16A TVS D13 on +12V, battery-voltage divider to PA0 |
| AUX_Outputs.kicad_sch | Four +5V_AUX peripheral ports J18-J21 (top-entry JST XH), one 1.5 A PTC each |
| Servo_Interface.kicad_sch | Latch servo port J17 (fused battery feed for an external buck, half-duplex UART through U8 SN74LVC1T45) |
| Battery_Monitor.kicad_sch | Battery current monitor: U13 INA228 on an off-board 50 A / 75 mV shunt in the battery - lead (Kelvin sense on J23), 10R/100 nF input filter, I2C1 on PB6/PB7 at 0x40, ALERT to PB4, VBUS on +12V |
| Interior_Light.kicad_sch | Payload-compartment WS2812B light J24 (3-pin top-entry JST XH): +5V_AUX through PTC F12, U14 SN74LV1T125 buffers PB5 (SPI1_MOSI) data to 5 V, D16 ESD |
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

The 2026-10-15 design review changes are summarized in [docs/design-review-2026-10-15.md](docs/design-review-2026-10-15.md). The 2026-10-27 battery current monitor and interior light are described in [docs/design-change-2026-10-27.md](docs/design-change-2026-10-27.md).

Component-selection rationale is in [docs/passive-selection-review.md](docs/passive-selection-review.md), [docs/clock-selection.md](docs/clock-selection.md) and [docs/fuse-selection.md](docs/fuse-selection.md). The fuse selection includes both the PCB-mounted holder and its separately purchased insert.

## Design status

Schematic: ERC is clean (0 errors, 0 warnings). PCB: 100 x 100 mm, 4 layers with an In1 GND plane. The board was fully routed as of commit 789cabe (2026-10-26), including outer-layer GND pours with stitching vias and widened high-current paths.

The `feat/battery-monitor-interior-light` branch (2026-10-27) added 18 parts: U13, U14, J23, J24, F12, D16, R54-R60 and C52-C56. They are placed and routed. DRC is clean, with 0 unconnected and 0 schematic parity issues. Layout notes are in [docs/design-change-2026-10-27.md](docs/design-change-2026-10-27.md#layout).

The saved ERC report and netlist (system-ERC-report.txt, system-netlist.xml) were regenerated on 2026-10-27 for that branch. validation/verify_2026_10_27.py checks the branch against the netlist of its parent commit. validation/verify_integration.py checks against the older October 5 connectivity.

Saved reports describe the checked revision. Regenerate them after relevant design changes.

## Team workflow

- Use the active delivery_robot_1 project for board work.
- Pull current changes before editing and coordinate ownership of schematic sheets and the PCB.
- Work on branches and review changes before merging.
- Save files in KiCad before committing. Include required project-local libraries with design changes.
- Run ERC after schematic changes and DRC after layout changes. Review outstanding findings before ordering boards.
- Enable the repository hooks once per clone with `git config core.hooksPath tools/hooks`. The pre-commit hook then re-plots delivery_robot_1.pdf from the staged schematic files and adds it to any commit that changes a `.kicad_sch` or `.kicad_pro` file. It needs KiCad installed; set `KICAD_CLI` if kicad-cli is not in the default location.

Editing locks, local UI settings and automatic backups are excluded from Git. Edit the native KiCad sources directly; regenerating files from older scripts may overwrite manual changes.
