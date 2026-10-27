# Design change, 2026-10-27: battery current monitor and interior light

Branch `feat/battery-monitor-interior-light`. This is a schematic and docs change only. The PCB file is unchanged. The 18 new parts still need "Update PCB from Schematic", placement and routing (see the [layout to-do](#layout-to-do) below). ERC is clean (0 errors, 0 warnings).

Two new hierarchical sheets, both connected through global labels and power symbols like *AUX Outputs* and *Servo Interface*:

| Sheet file | Sheet name | What it adds |
|---|---|---|
| Battery_Monitor.kicad_sch | Battery Monitor | U13 INA228 on an off-board shunt: battery current, voltage and charge over I2C1 |
| Interior_Light.kicad_sch | Interior Light | J24 port for a WS2812B strip in the payload compartment, with U14 buffering the data to 5 V (S17.2) |

Battery *voltage* sensing on PA0 (R37/R38/C37, requirement 1.7) is unchanged.

## Change 1: battery current monitor

**Target requirement (draft, the team will finalize the numbers):** the Control Board shall measure total battery current from -40 A to +40 A (positive = discharge) with an error of +/-1 % of reading +/-0.05 A after a one-point calibration. It shall report battery current, voltage and the charge drawn since the last full charge to the Raspberry Pi at 10 Hz.

**Architecture.** The motor current must not flow through the board (requirement 2.13), so the shunt is off-board.

- A 50 A / 75 mV shunt (1.5 mOhm, class 0.5) sits in the battery **negative** lead. One side goes to the battery - terminal. The other side is the robot's common ground lug, where the Control Board harness GND (the J2 pin 1 lead), the MDD20A VB- lead and the charger - all land.
- Two Kelvin sense wires run from the shunt's sense screws to J23.
- The shunt is on the low side, so the sense wires sit within about 0.1 V of ground. A chafed sense wire then can't short the battery.
- U13 (INA228) measures the shunt voltage over I2C1 and accumulates charge in hardware.
- **Range check.** Harness drop puts board GND up to about 60 mV above the shunt. That leaves IN- at about -135 mV at 50 A, inside the INA228's -0.3 V common-mode limit. Full scale (ADCRANGE = 0) is +/-163.84 mV, about +/-109 A.
- **Accuracy budget.** INA228 gain error is 0.05 % max and offset is about 1 uV (0.7 mA referred to the shunt), so the shunt sets the accuracy. Its 0.5 % tolerance is calibrated out. Its temperature drift is not, so check the shunt's tempco and self-heating against the +/-1 % target. R54 + R55 (20 Ohm) against the INA228's 92 kOhm differential input impedance adds about 0.02 % gain error, which the calibration also removes.

### Datasheet checks

- **INA228 pinout** (TI SLYS021A, table 5-1): 1 A1, 2 A0, 3 ALERT (open-drain, active low), 4 SDA, 5 SCL, 6 VS, 7 GND, 8 VBUS, 9 IN-, 10 IN+. The KiCad `Sensor_Energy:INA228` symbol (an alias of INA226) matches pin for pin, so no project symbol was needed. For low-side sensing the datasheet puts IN+ on the load side of the shunt and IN- on the ground side; J23 is wired that way. A0 = A1 = GND gives address 0x40 (1000000b).
- **Input filter.** Section 8.1.4 recommends at most 100 Ohm per input with 0.1-1 uF, and says 10 Ohm in each input protects against dV/dt failure up to the 40 V differential rating. R54/R55 10 Ohm + C52 100 nF follow that (about 80 kHz).
- **Power sequencing.** The input common-mode range is independent of VS (section 7.3.1), so the sense inputs may see voltage while +3V3 is down.
- **Footprint.** KiCad 10 has no `Package_SO:VSSOP-10_3x3mm_P0.5mm`. U13 uses `Package_SO:TSSOP-10_3x3mm_P0.5mm`, which is drawn from TI's DGS outline (MPDS035) and is the INA228 symbol's default. It fits INA228AIDGSR (VSSOP-10, DGS).

### Parts

| Ref | Part | Value / MPN | Footprint |
|---|---|---|---|
| U13 | TI INA228 | INA228AIDGSR | Package_SO:TSSOP-10_3x3mm_P0.5mm (TI DGS) |
| J23 | Shunt sense terminal, 2-pin, 2.54 mm | Phoenix Contact 1725656 (MPT 0,5/2-2,54) | TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-2-2.54_1x02_P2.54mm_Horizontal |
| R54, R55 | Input filter resistors | 10 Ohm 1 %, Yageo RC0805FR-0710RL | 0805 |
| C52 | Differential filter across IN+ / IN- | 100 nF 50 V X7R, KEMET C0805C104K5RACTU | 0805 |
| C53 | U13 VS decoupling | 100 nF 50 V X7R, KEMET C0805C104K5RACTU | 0805 |
| R56, R57 | I2C1 pull-ups (SCL, SDA) | 4.7 kOhm 1 %, Yageo RC0805FR-074K7L | 0805 |
| R58 | ALERT pull-up | 10 kOhm 1 %, Yageo RC0805FR-0710KL | 0805 |

J23 has a different footprint from J14 (Pi power) on purpose, so the two can't be mixed up. Its value field is "SHUNT SENSE: LOAD / BATT". Add that as silkscreen text during layout.

### Connections

| Pin | Net |
|---|---|
| J23 pin 1 (load side of shunt) | `/Battery Monitor/SH_LOAD` -> R54 -> `/Battery Monitor/INA_INP` -> U13 IN+ (10) |
| J23 pin 2 (battery - side of shunt) | `/Battery Monitor/SH_BATT` -> R55 -> `/Battery Monitor/INA_INN` -> U13 IN- (9) |
| C52 | Between INA_INP and INA_INN. There is no ground connection at the inputs, and IN+ must not tie to board GND on the board |
| U13 VS (6) | +3V3, with C53 to GND |
| U13 GND (7) | GND |
| U13 VBUS (8) | +12V (after Q1, so reverse polarity never reaches it; D13 limits it to 26 V, inside the 85 V rating). This gives a second voltage reading alongside PA0 |
| U13 A0 (2), A1 (1) | GND (address 0x40) |
| U13 SCL (5) / SDA (4) | Global labels PB6 / PB7 (existing nets), with R56 and R57 to +3V3 |
| U13 ALERT (3) | New global label BATT_ALERT -> U1 pin 56 (PB4), with R58 to +3V3 |

## Change 2: interior NeoPixel light

**Target requirement: S17.2.** When the lid opens, the Payload Compartment interior light shall turn on within 0.5 s. It shall turn off within 2 s after the lid closes. The light is an off-board WS2812B strip of up to 16 LEDs in the compartment, and firmware caps its draw at 0.5 A. The lid Hall sensor is a separate change.

**Design.**

- Power comes from +5V_AUX through its own PTC (F12, the same part as the four AUX ports). The light is therefore only powered while the Pi is up. U5 is a 6 A module, and the AUX budget becomes 2.5 A for the ports plus 0.5 A for the light.
- WS2812B data needs a high level of at least 0.7 x VDD (3.5 V), so 3.3 V data from the STM32 is marginal. U14 buffers it to 5 V. Its VIH is 2.03 V at VCC = 5 V, and its VOH is at least 4.5 V at 8 mA.
- Data comes from SPI1 MOSI on PB5 (AF0), TX-only with DMA. SPI1 SCK is not mapped to a pin, because both candidate pins (PA5, PB3) are already in use.

**U14 with VCC = 0 (checked, TI SCLS745D).** The STM32 can drive PB5 while +5V_AUX is off, so U14's input must tolerate voltage with VCC = 0. It does, so U14 stays on +5V_AUX:

- Section 8.3.1 / figure 8-2: the inputs have negative clamp diodes only, with no diode to VCC, so 3.3 V on A can't back-power the 5 V rail.
- Section 6.1: the input voltage rating is -0.5 V to 7.0 V and is not referenced to VCC.
- Section 6.5: input leakage is +/-1 uA with VCC = 0 V among the listed supply conditions.

The alternate part (SN74AHCT1G125DBVR) has the same pinout but was not checked for this. Check its datasheet before substituting it.

### Parts

| Ref | Part | Value / MPN | Footprint |
|---|---|---|---|
| U14 | 3.3 V -> 5 V single buffer | TI SN74LV1T125DBVR (alternate: SN74AHCT1G125DBVR, same pinout) | Package_TO_SOT_SMD:SOT-23-5 |
| C54 | U14 decoupling | 100 nF 50 V X7R, KEMET C0805C104K5RACTU | 0805 |
| R59 | Data pull-down at U14 input (keeps data low while the MCU resets) | 100 kOhm 1 %, Yageo RC0805FR-07100KL | 0805 |
| R60 | Data series resistor | 330 Ohm 1 %, Yageo RC0805FR-07330RL | 0805 |
| D16 | Data line ESD (same part as D14) | Diodes Inc. D5V0L1B2WS-7 | Diode_SMD:D_SOD-323 |
| F12 | Light supply PTC (same part as F4-F7) | Littelfuse 1812L150/16DR, 1.5 A hold | Fuse:Fuse_1812_4532Metric |
| C55 | Bulk at J24 | 10 uF 16 V X7R, Samsung CL21B106KOQNNNE | 0805 (the 0805 part exists, so 1206 was not needed) |
| C56 | HF bypass at J24 | 100 nF 50 V X7R, KEMET C0805C104K5RACTU | 0805 |
| J24 | Light connector, 3-pin, top entry | JST B3B-XH-A(LF)(SN) | Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical |

### Connections

| Pin | Net |
|---|---|
| U1 pin 57 (PB5) | New global label LIGHT_DATA -> R59 to GND -> U14 A (2) |
| U14 OE# (1) | GND (always enabled) |
| U14 VCC (5) | +5V_AUX, with C54 to GND |
| U14 Y (4) | `/Interior Light/LIGHT_DIN_BUF` -> R60 -> `/Interior Light/LIGHT_DIN` -> J24 pin 2, with D16 to GND |
| F12 | +5V_AUX -> `/Interior Light/LIGHT_5V` |
| J24 pin 1 | LIGHT_5V, with C55 and C56 to GND |
| J24 pin 3 | GND |
| Net class | `*/LIGHT_5V` added to the Power net class patterns |

## Root sheet and MCU pins

Both sheets sit on the root sheet, right of U1 and below *Pi 5 Interface*. U1 pins 56 and 57 lost their no-connect flags and now carry global labels.

| Pin | Net | Use |
|---|---|---|
| PB4 (56) | BATT_ALERT | Input, EXTI4, open-drain alert from U13 (active low). R58 pulls it up |
| PB5 (57) | LIGHT_DATA | SPI1_MOSI (AF0), TX-only master with DMA. R59 holds it low through reset |
| PB6 / PB7 (58/59) | PB6 / PB7 | I2C1 SCL / SDA (AF1), now with on-board 4.7k pull-ups. U13 is at 0x40. Still on J8 pins 13-14 as a shared bus; anything added on J8 must not use 0x40 |

## Notes

**Harness change.**

- The shunt goes in the battery - lead.
- Everything that returns to battery - must go through it: the Control Board GND, the MDD20A VB- lead, and the charger - if charging should be counted.
- Run the sense leads as a twisted 22-24 AWG pair away from the motor leads. Land them on the shunt's small sense screws, not the big lugs.
- If the charger clips straight onto the battery terminals, firmware resets the charge count when the battery is full.

**Open shunt-to-ground-lug joint.** If that joint opens, the robot's return current tries to reach battery - through J2 GND, U13's input ESD diodes, R54 and the SH_LOAD sense wire. R54 limits it to about 1.3 A and will burn open. Expect to replace U13, R54 and R55 after this fault. The sense wire itself is not at risk. Use lock washers on both shunt lugs.

**Off-board, for the light.** Put a 470-1000 uF / 10 V electrolytic across the strip's power at the strip end.

**Firmware, INA228.**

- Set ADCRANGE = 0 (+/-163.84 mV).
- SHUNT_CAL = 13107.2e6 x CURRENT_LSB x 0.0015, with CURRENT_LSB = 250 uA. That gives 4915.2, so write 4915. The current register then reaches 131 A, above the 109 A ADC full scale.
- Read the CHARGE register for coulomb counting. One LSB is 250 uC, so 50 Ah is about 7.2e8 counts, well inside the 40-bit register.
- Positive current = discharge.
- Choose ADC_CONFIG so an averaged result is ready well within 100 ms, for the 10 Hz report.

**Firmware, light.**

- Run SPI1 at 6 MHz (48 MHz / 8), with one SPI byte per WS2812 bit: 0 -> 0xC0 (333 ns high), 1 -> 0xF0 (667 ns high), 1.33 us per bit.
- End each frame with at least 300 us of zeros.
- Fallback if this misbehaves: TIM16_CH1 on PB8 (AF2) with DMA. That would need a schematic change.

**Firmware interlock.** The light is off whenever the latch servo moves. The latch only moves with the lid closed (12.9), so this only shortens the S17.2 off-delay. It keeps the worst-case input current at the 8.4 A already analysed; without it the worst case is about 8.7 A (see [fuse-selection.md](fuse-selection.md)).

## Layout to-do

This is for the person doing placement, not part of this change.

- **U13 and its filter:** place U13, R54, R55 and C52 next to J23, on a board edge away from U2/U5 and L1. Route INA_INP/INA_INN as a tight pair with no vias, and do not touch them with any GND pour connection. Add the silkscreen text "SHUNT SENSE: LOAD / BATT" at J23.
- **Light circuit:** put U14, R60, D16, C55, C56 and F12 at J24. Place J24 on the edge facing the payload compartment.
- **I2C pull-ups:** put R56 and R57 near U1 pins 58/59.

## Verification

- `kicad-cli sch erc --severity-all --exit-code-violations`: 0 errors, 0 warnings (system-ERC-report.txt).
- `validation/verify_2026_10_27.py` compares system-netlist.xml with the netlist of the parent commit (789cabe). It checks:
  - every pin-to-net pair in both connection tables;
  - that the shunt-sense and data nets carry nothing else;
  - that PB6/PB7 gained exactly U13 plus R56/R57;
  - that no pre-existing pin changed nets except U1 56/57, and no net lost a pin;
  - that all 156 existing parts are unchanged;
  - that the 18 new parts are unique, carry Manufacturer, MPN, Datasheet and Description, and use the footprints above.
- The netlist export warns "schematic has annotation errors". That comes from a duplicate `#PWR0103` power-symbol reference (root sheet and Input Protection) that predates this change. It does not affect connectivity. The new power symbols use #PWR0256-#PWR0270.
