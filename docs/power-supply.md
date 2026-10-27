# Power supply integration

The power supply is split into hierarchical sheets. The root schematic keeps the 12 V input connector J2, fuse F1 and bulk capacitor C36. The Input Protection sheet sits between F1 and +12V (reverse-battery P-FET Q1, TVS D13, battery sense). Each sheet connects through global labels (VBAT_FUSED, +12V, GND and the rail names).

`J2 -> VBAT_IN -> F1 (10 A) -> VBAT_FUSED -> Q1 -> +12V (D13 TVS, C36 bulk, buck inputs, servo fuse F3)`

| Sheet file | Sheet name | Regulator | Input | Output net |
| --- | --- | --- | --- | --- |
| Buck_5V_2A.kicad_sch | Buck 5V SYS | TPS54202HDDCR (U3) | +12V | +5V_SYS |
| Buck_5V_6A.kicad_sch | Buck 5V PI | TPS56637RPAR (U2) | +12V | +5V_PI |
| Buck_5V_6A_AUX.kicad_sch | Buck 5V AUX | TPS56637RPAR (U5) | +12V | +5V_AUX |
| LDO_3V3.kicad_sch | LDO Power | TPS7A8101DRBR (U4) | +5V_SYS | +3V3 |

Each buck sheet has hierarchical labels VIN_12V (input), GND and VOUT_5V (output). The buck outputs are separate nets and must not be tied together. +5V_PI feeds the off-board Raspberry Pi 5 directly through J14 (no fuse: U2's cycle-by-cycle current limit and hiccup mode protect the pigtail). +5V_AUX comes from a second, independent copy of the 6 A buck (U5, L3, C28-C33, R14-R16, R62) and feeds four peripheral ports (Notecard, LiDAR, GNSS, IMU) on the AUX Outputs sheet, each through its own 1.5 A PTC, plus the payload-compartment interior light (J24, through PTC F12 on the Interior Light sheet). The design load is 3.0 A (2.5 A for the ports, 0.5 A for the light, capped in firmware) on the 6 A converter. U5 is enabled by AUX_EN: the Pi's 3V3 through D15, with a 100k pull-down (R43) and a bench force-on jumper (J22).

## Battery input (J2)

The board is powered from a DJLBERMPW 12V 50Ah LiFePO4 battery (12.8 V nominal, 50 A BMS). The battery has M8 (5/16 in) bolt terminals, so it connects to the PCB through a short harness rather than directly:

`battery M8 terminals -> M8 ring lugs -> inline fuse at the battery -> 16 AWG pair -> AMASS XT30U-F plug -> J2`

Negative side (added 2026-10-27): `battery - -> 50 A / 75 mV shunt -> common ground lug -> (J2 pin 1 lead, MDD20A VB-, charger -)`

| Item | Part | Notes |
| --- | --- | --- |
| J2 (PCB) | AMASS XT30PW-M, right-angle PCB male | Footprint `Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal`. Rated 15 A continuous, 30 A short-term, 500 V. Keyed housing prevents reversed mating. |
| Harness plug | AMASS XT30U-F | Female on the battery side so no exposed live contacts when unplugged. |
| Battery lugs | M8 (5/16 in) ring terminals for 16 AWG | Crimp and heat-shrink. |
| Harness fuse | Inline fuse close to the battery + terminal | Protects the harness; F1 on the PCB only protects downstream of J2. 15 A, above F1 (10 A). |
| Current shunt | 50 A / 75 mV (1.5 mOhm, class 0.5) in the battery - lead | Off-board, read by U13 (INA228) through J23. Everything that returns to battery - must go through it. See [design-change-2026-10-27.md](design-change-2026-10-27.md). |

J2 pin 2 (the pad marked + on the footprint silkscreen) is battery + to F1; pin 1 (marked -) is GND. Confirm the polarity of the assembled XT30U-F harness against the board silkscreen with a meter before first power-up.

**Reverse-polarity protection (decision 2026-10-15: P-FET plus TVS).** Q1 (Vishay SQJ409EP, -40 V, 7 mOhm at VGS = -10 V) is a high-side P-FET after F1: drain on VBAT_FUSED, source on +12V. A reversed battery leaves its body diode reverse-biased and VGS = 0, so nothing after Q1 ever sees negative voltage. This now covers a harness crimped backwards at the battery lugs, which the keyed XT30 did not. D12 (12 V zener) keeps VGS under the 20 V limit and R36 holds the gate at GND. Loss is about 0.2 W at 5 A. D13 (SMBJ16A: 16 V stand-off, 26 V clamp at 23 A) clamps hot-plug and harness spikes below the buck converters' input abs max (TPS54202H 30 V, TPS56637 32 V). It cannot absorb motor regen if the BMS opens (about 20 J); that must be clamped on the motor-driver side. Still meter-check harness polarity before first power-up.

**Input bulk capacitance.** C36, a 220 uF / 35 V low-ESR aluminium electrolytic (Panasonic EEU-FR1V221, 8 x 11.5 mm radial), sits on +12V after Q1, next to the U2/U5 input capacitors, so it is never reverse-biased. It supplies load steps and damps the harness inductance together with the buck input ceramics.

**Battery sense.** R37 100k / R38 22.1k (1 %) and C37 100 nF divide +12V into VBAT_SENSE on PA0 (ADC_IN0): VBAT = V(PA0) x 5.525, so 14.6 V reads 2.64 V. U13 (INA228, Battery Monitor sheet) also reads +12V on its VBUS pin, which gives a second voltage reading over I2C.

**Battery current.** The shunt sits in the battery negative lead, between battery - and the robot's common ground lug, where the J2 pin 1 lead, the MDD20A VB- lead and the charger - all land. Two Kelvin sense wires run from the shunt's sense screws to J23. U13 measures the shunt voltage, so motor current never flows through the board (requirement 2.13). Because the shunt is on the low side, the sense wires sit within about 0.1 V of GND, so a chafed sense wire cannot short the battery. Board GND sits up to about 60 mV above the shunt because of harness drop. That puts IN- at about -135 mV at 50 A, inside the INA228's -0.3 V common-mode limit.

J2 carries the board electronics and the latch-servo feed (about 8.4 A worst case with the servo stalled and the interior light off by interlock; see [fuse-selection.md](fuse-selection.md)). The MDD20A motor driver connects to the battery through its own wiring and protection, not through J2.

## Regulator notes

The original TPSM63606 modules and TPS54202 went out of stock on 2026-10-27 and were replaced with in-stock TI parts. Values come from TI WEBENCH designs at 10-15 V in, 5 V out. See [design-change-2026-10-27-regulators.md](design-change-2026-10-27-regulators.md) for the part list, simulations and layout.

- U2/U5 (TPS56637, 6 A, 557 kHz): R4/R15 = 73.2k and R5/R16 = 10k set 4.99 V with the 0.6 V reference. R2/R14 (20k) + C10/C31 (100 pF) are the feed-forward network across the top resistor. MODE is tied to GND (Eco-mode at light load). U2's EN floats (internal pull-up = enabled); U5's EN is AUX_EN (EN abs max 6 V, driven from 3.3 V). PG has a 100k pull-up to the rail (R61/R62) but is not used elsewhere.
- U3 (TPS54202H, 2 A, 500 kHz): EN is pulled down internally on the H version, so R63 (442k) pulls it up to VIN. R6 = 100k and R7 = 13.7k give 4.946 V with the 0.596 V reference; C16 = 68 pF feed-forward. C49 (100 nF) is the input bypass right at U3's VIN/GND pins; C14 (22 uF) is the bulk input cap.

The TPS7A8101 LDO in LDO_3V3.kicad_sch is supplied by the +5V_SYS rail. Its +3V3 output supplies the STM32 digital power pins, associated decoupling, programming-header supply, and the FB2 input feeding the separate +3.3VA analog rail. The two buck outputs are separate nets.

The LDO uses U4, R8/R9 and C24-C27. R8 = 35.7k / R9 = 11.5k (E96) set VOUT = 0.8 x (1 + 35.7/11.5) = 3.284 V. The former VDD power symbols use +3V3 to connect these loads to the regulator. The 1 A rating is combined rail capacity, not measured MCU current consumption. Full-load dissipation would be about 1.7 W at 5 V input, but the real 3.3 V load is about 150 mA (about 0.25 W). C26 (NR) and C27 (bypass across R8) are 10 nF, so start-up is about 1.7 ms (170,000 x C26) and +3V3 follows +5V_SYS closely; with 470 nF it took 80 ms, during which 5 V encoder signals could reach unpowered MCU pins.

See ../LDO_KiCad/README.md for component values, the standalone example and reuse instructions. See ../LDO_KiCad/footprint-verification/VERIFICATION.md for the LDO footprint review. The TPS56637 RPA0010A footprint and the Wurth WE-XHMI-7070 inductor footprint in libs/project_footprints.pretty were drawn from the TI and Wurth land-pattern drawings.

The project-local symbol and footprint tables include all supplied custom power components. They use paths relative to the project directory.

All system resistors R1-R9 use Resistor_SMD:R_0805_2012Metric to meet the team's 0805 package requirement. The reusable LDO example uses the same resistor footprint. Resistance values and tolerances are unchanged; select purchasing parts in 0805 with suitable power and working-voltage ratings. Footprint assignment alone does not establish those ratings.

[passive-selection-review.md](passive-selection-review.md) covers the original (2026-10-05) buck passives; the buck converter parts in it are superseded by [design-change-2026-10-27-regulators.md](design-change-2026-10-27-regulators.md).

## Integration validation

validation/verify_integration.py checks the KiCad-exported system netlist against validation/before-integration.xml. It verifies the five LDO nets, all nine U4 pads, MCU supply connections, analog filter input, unique component references, and preservation of the original circuit except the intended VDD/+3V3 merge.

Run it from the repository with a Python installation after exporting system-netlist.xml:

    kicad-cli sch export netlist --format kicadxml -o system-netlist.xml delivery_robot_1.kicad_sch
    python validation/verify_integration.py

This check covers power integration. Run full-system ERC and, once a PCB exists, DRC separately.
