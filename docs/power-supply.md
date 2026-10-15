# Power supply integration

The power supply is split into hierarchical sheets. The root schematic keeps the 12 V input connector J2, fuse F1 and bulk capacitor C36. The Input Protection sheet sits between F1 and +12V (reverse-battery P-FET Q1, TVS D13, battery sense). Each sheet connects through global labels (VBAT_FUSED, +12V, GND and the rail names).

`J2 -> VBAT_IN -> F1 (10 A) -> VBAT_FUSED -> Q1 -> +12V (D13 TVS, C36 bulk, buck inputs, servo fuse F3)`

| Sheet file | Sheet name | Regulator | Input | Output net |
| --- | --- | --- | --- | --- |
| Buck_5V_2A.kicad_sch | Buck 5V SYS | TPS54202DDCR (U3) | +12V | +5V_SYS |
| Buck_5V_6A.kicad_sch | Buck 5V PI | TPSM63606RDLR (U2) | +12V | +5V_PI |
| Buck_5V_6A_AUX.kicad_sch | Buck 5V AUX | TPSM63606RDLR (U5) | +12V | +5V_AUX |
| LDO_3V3.kicad_sch | LDO Power | TPS7A8101DRBR (U4) | +5V_SYS | +3V3 |

Each buck sheet has hierarchical labels VIN_12V (input), GND and VOUT_5V (output). The buck outputs are separate nets and must not be tied together. +5V_PI feeds the off-board Raspberry Pi 5 directly through J14 (no fuse: U2's cycle-by-cycle current limit and hiccup mode protect the pigtail). +5V_AUX comes from a second, independent copy of the 6 A buck (U5, C28-C33, R14-R16) and feeds four peripheral ports (Notecard, LiDAR, GNSS, IMU) on the AUX Outputs sheet, each through its own 1.5 A PTC. U5 is enabled by AUX_EN: the Pi's 3V3 through D15, with a 100k pull-down (R43) and a bench force-on jumper (J22).

## Battery input (J2)

The board is powered from a DJLBERMPW 12V 50Ah LiFePO4 battery (12.8 V nominal, 50 A BMS). The battery has M8 (5/16 in) bolt terminals, so it connects to the PCB through a short harness rather than directly:

`battery M8 terminals -> M8 ring lugs -> inline fuse at the battery -> 16 AWG pair -> AMASS XT30U-F plug -> J2`

| Item | Part | Notes |
| --- | --- | --- |
| J2 (PCB) | AMASS XT30PW-M, right-angle PCB male | Footprint `Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal`. Rated 15 A continuous, 30 A short-term, 500 V. Keyed housing prevents reversed mating. |
| Harness plug | AMASS XT30U-F | Female on the battery side so no exposed live contacts when unplugged. |
| Battery lugs | M8 (5/16 in) ring terminals for 16 AWG | Crimp and heat-shrink. |
| Harness fuse | Inline fuse close to the battery + terminal | Protects the harness; F1 on the PCB only protects downstream of J2. 15 A, above F1 (10 A). |

J2 pin 2 (the pad marked + on the footprint silkscreen) is battery + to F1; pin 1 (marked -) is GND. Confirm the polarity of the assembled XT30U-F harness against the board silkscreen with a meter before first power-up.

**Reverse-polarity protection (decision 2026-10-15: P-FET plus TVS).** Q1 (Vishay SQJ409EP, -40 V, 7 mOhm at VGS = -10 V) is a high-side P-FET after F1: drain on VBAT_FUSED, source on +12V. A reversed battery leaves its body diode reverse-biased and VGS = 0, so nothing after Q1 ever sees negative voltage. This now covers a harness crimped backwards at the battery lugs, which the keyed XT30 did not. D12 (12 V zener) keeps VGS under the 20 V limit and R36 holds the gate at GND. Loss is about 0.2 W at 5 A. D13 (SMBJ16A: 16 V stand-off, 26 V clamp at 23 A) clamps hot-plug and harness spikes below the TPS54202's 30 V abs max. It cannot absorb motor regen if the BMS opens (about 20 J); that must be clamped on the motor-driver side. Still meter-check harness polarity before first power-up.

**Input bulk capacitance.** C36, a 220 uF / 35 V low-ESR aluminium electrolytic (Panasonic EEU-FR1V221, 8 x 11.5 mm radial), sits on +12V after Q1, next to the U2/U5 input capacitors, so it is never reverse-biased. It supplies load steps and damps the harness inductance together with the buck input ceramics.

**Battery sense.** R37 100k / R38 22.1k (1 %) and C37 100 nF divide +12V into VBAT_SENSE on PA0 (ADC_IN0): VBAT = V(PA0) x 5.525, so 14.6 V reads 2.64 V.

J2 carries the board electronics and the latch-servo feed (about 8.3 A worst case with the servo stalled; see [fuse-selection.md](fuse-selection.md)). The MDD20A motor driver connects to the battery through its own wiring and protection, not through J2.

## Regulator notes

The regulator symbols (U2, U3) carry the datasheet link, product page, key specifications and design notes in their symbol properties.

Notes (open items from the sheet split, resolved in the 2026-10-15 review):
- U2/U5: VCC (pin 7) has an internal 1 uF and must not be loaded (SLVSGB4B pin table), so leaving it NC is correct. C9/C30 are the VLDOIN capacitors.
- U2: R4 = 41.2k and R5 = 10k (E96) set the Pi rail to 5.12 V (5.1 V target). U5: R15 = 40.2k / R16 = 10k give 5.02 V on the AUX rail.
- U3: a floating EN (pin 5) is allowed; TPS54202 EN has an internal pull-up.
- U3: R6 = 100k and R7 = 13.7k give 4.946 V with the 0.596 V reference. C49 (100 nF / 50 V) sits right at U3's VIN/GND pins to keep the switching loop short; C14 is the bulk part.

The TPS7A8101 LDO in LDO_3V3.kicad_sch is supplied by the +5V_SYS rail. Its +3V3 output supplies the STM32 digital power pins, associated decoupling, programming-header supply, and the FB2 input feeding the separate +3.3VA analog rail. The two buck outputs are separate nets.

The LDO uses U4, R8/R9 and C24-C27. R8 = 35.7k / R9 = 11.5k (E96) set VOUT = 0.8 x (1 + 35.7/11.5) = 3.284 V. The former VDD power symbols use +3V3 to connect these loads to the regulator. The 1 A rating is combined rail capacity, not measured MCU current consumption. Full-load dissipation would be about 1.7 W at 5 V input, but the real 3.3 V load is about 150 mA (about 0.25 W). C26 (NR) and C27 (bypass across R8) are 10 nF, so start-up is about 1.7 ms (170,000 x C26) and +3V3 follows +5V_SYS closely; with 470 nF it took 80 ms, during which 5 V encoder signals could reach unpowered MCU pins.

See ../LDO_KiCad/README.md for component values, the standalone example and reuse instructions. See ../LDO_KiCad/footprint-verification/VERIFICATION.md for the LDO footprint review. Existing buck footprints resolve to supplied files, but their physical dimensions have not been reviewed here.

The project-local symbol and footprint tables include all supplied custom power components. They use paths relative to the project directory.

All system resistors R1-R9 use Resistor_SMD:R_0805_2012Metric to meet the team's 0805 package requirement. The reusable LDO example uses the same resistor footprint. Resistance values and tolerances are unchanged; select purchasing parts in 0805 with suitable power and working-voltage ratings. Footprint assignment alone does not establish those ratings.

See [passive-selection-review.md](passive-selection-review.md) for the capacitor/inductor purchasing candidates, manufacturer dimensions, L1's 15 uH selection, and outstanding transient checks.

## Integration validation

validation/verify_integration.py checks the KiCad-exported system netlist against validation/before-integration.xml. It verifies the five LDO nets, all nine U4 pads, MCU supply connections, analog filter input, unique component references, and preservation of the original circuit except the intended VDD/+3V3 merge.

Run it from the repository with a Python installation after exporting system-netlist.xml:

    kicad-cli sch export netlist --format kicadxml -o system-netlist.xml delivery_robot_1.kicad_sch
    python validation/verify_integration.py

This check covers power integration. Run full-system ERC and, once a PCB exists, DRC separately.
