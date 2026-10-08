# Power supply integration

The power supply is split into hierarchical sheets. The root schematic keeps the 12 V input: connector J2, fuse F1 and bulk capacitor C36, and connects each sheet through global labels (+12V, GND and the rail names).

| Sheet file | Sheet name | Regulator | Input | Output net |
| --- | --- | --- | --- | --- |
| Buck_5V_2A.kicad_sch | Buck 12V-5V 2A | TPS54202DDCR (U3) | +12V | +5V, 2A |
| Buck_5V_6A.kicad_sch | Buck 12V-5V 6A PI | TPSM63606RDLR (U2) | +12V | +5V, 6A PI |
| Buck_5V_6A_AUX.kicad_sch | Buck 12V-5V 6A AUX | TPSM63606RDLR (U5) | +12V | +5V, 6A AUX |
| LDO_3V3.kicad_sch | LDO Power | TPS7A8101DRBR (U4) | +5V, 2A | +3V3 |

Each buck sheet has hierarchical labels VIN_12V (input), GND and VOUT_5V (output). The buck outputs are separate nets and must not be tied together. +5V, 6A PI feeds the off-board Raspberry Pi 5 through F2 and J14. +5V, 6A AUX comes from a second, independent copy of the 6 A buck (U5, C28-C33, R14-R16) and has no loads assigned yet. The AUX sheet inherits the open items listed for U2 below (C9 -> C30 placement).

## Battery input (J2)

The board is powered from a DJLBERMPW 12V 50Ah LiFePO4 battery (12.8 V nominal, 50 A BMS). The battery has M8 (5/16 in) bolt terminals, so it connects to the PCB through a short harness rather than directly:

`battery M8 terminals -> M8 ring lugs -> inline fuse at the battery -> 16 AWG pair -> AMASS XT30U-F plug -> J2`

| Item | Part | Notes |
| --- | --- | --- |
| J2 (PCB) | AMASS XT30PW-M, right-angle PCB male | Footprint `Connector_AMASS:AMASS_XT30PW-M_1x02_P2.50mm_Horizontal`. Rated 15 A continuous, 30 A short-term, 500 V. Keyed housing prevents reversed mating. |
| Harness plug | AMASS XT30U-F | Female on the battery side so no exposed live contacts when unplugged. |
| Battery lugs | M8 (5/16 in) ring terminals for 16 AWG | Crimp and heat-shrink. |
| Harness fuse | Inline fuse close to the battery + terminal | Protects the harness; F1 on the PCB only protects downstream of J2. Size it to the wire and above F1 (7.5 A), e.g. 10 A for 16 AWG. |

J2 pin 2 (the pad marked + on the footprint silkscreen) is battery + to F1; pin 1 (marked -) is GND. Confirm the polarity of the assembled XT30U-F harness against the board silkscreen with a meter before first power-up.

**Reverse-polarity protection (decision: rely on the keyed XT30).** There is no reverse-polarity circuit on the board. The XT30 housing is keyed and cannot be mated reversed, and leaving out a series P-FET avoids an extra part and its conduction loss in the 4-8 A input path. What this does not cover is a harness crimped backwards at the battery M8 lugs: that would put -12 V on both buck converters and the polarized input capacitor C36 until F1 blows, which can damage them. Mitigation: check harness polarity with a meter (+ to J2 pin 2) before first power-up and after any harness rework.

**Input bulk capacitance.** C36, a 220 uF / 35 V low-ESR aluminium electrolytic (Panasonic EEU-FR1V221, 8 x 11.5 mm radial), sits on +12V right after F1, near J2. It supplies load steps and damps the harness inductance together with the buck input ceramics.

J2 carries only the board electronics (about 4.4 A estimated maximum; see [fuse-selection.md](fuse-selection.md)). The MDD20A motor driver connects to the battery through its own wiring and protection, not through J2.

## Regulator notes

The regulator symbols (U2, U3) carry the datasheet link, product page, key specifications and design notes in their symbol properties.

Open items from the sheet split:
- U2: C9 (1 uF) sits on VLDOIN/VOUT while VCC (pin 7) is flagged no-connect. The datasheet calls for 1 uF from VCC to AGND, so C9 placement needs checking.
- U2: R4 = 41.2k and R5 = 10k (E96) set the Pi rail to 5.12 V (5.1 V target). U5: R15 = 40.2k / R16 = 10k give 5.02 V on the AUX rail.
- U3: EN (pin 5) is flagged no-connect; confirm a floating EN is allowed, otherwise tie it to VIN.
- U3: R6 = 100k and R7 = 13.7k give about 4.95 V assuming a 0.596 V reference; verify against the datasheet.

The TPS7A8101 LDO in LDO_3V3.kicad_sch is supplied by the +5V, 2A rail. Its +3V3 output supplies the STM32 digital power pins, associated decoupling, programming-header supply, and the FB2 input feeding the separate +3.3VA analog rail. The two buck outputs are separate nets.

The LDO uses U4, R8/R9 and C24-C27. R8 = 35.7k / R9 = 11.5k (E96) set VOUT = 0.8 x (1 + 35.7/11.5) = 3.284 V. The former VDD power symbols use +3V3 to connect these loads to the regulator. The 1 A rating is combined rail capacity, not measured MCU current consumption. Full-load dissipation is approximately 1.7 W at 5 V input; PCB thermal copper and vias remain to be designed.

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
