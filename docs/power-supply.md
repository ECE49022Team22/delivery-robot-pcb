# Power supply integration

The power supply is split into hierarchical sheets. The root schematic keeps the 12 V input connector and fuse (J2, F1) and connects each sheet through global labels (+12V, GND and the rail names).

| Sheet file | Sheet name | Regulator | Input | Output net |
| --- | --- | --- | --- | --- |
| Buck_5V_2A.kicad_sch | Buck 12V-5V 2A | TPS54202DDCR (U3) | +12V | +5V, 2A |
| Buck_5V_6A.kicad_sch | Buck 12V-5V 6A | TPSM63606RDLR (U2) | +12V | +5V, 6A |
| LDO_3V3.kicad_sch | LDO Power | TPS7A8101DRBR (U4) | +5V, 2A | +3V3 |

Each buck sheet has hierarchical labels VIN_12V (input), GND and VOUT_5V (output). The two buck outputs are separate nets and must not be tied together. The +5V, 6A net currently has no loads other than U2's own output capacitors.

The regulator symbols (U2, U3) carry the datasheet link, product page, key specifications and design notes in their symbol properties.

Open items from the sheet split:
- U2: C9 (1 uF) sits on VLDOIN/VOUT while VCC (pin 7) is flagged no-connect. The datasheet calls for 1 uF from VCC to AGND, so C9 placement needs checking.
- U2: R4 = 40k and R5 = 10k give about 5.0 V, while the old schematic note said 5.1 V.
- U3: EN (pin 5) is flagged no-connect; confirm a floating EN is allowed, otherwise tie it to VIN.
- U3: R6 = 100k and R7 = 13.7k give about 4.95 V assuming a 0.596 V reference; verify against the datasheet.

The TPS7A8101 LDO in LDO_3V3.kicad_sch is supplied by the +5V, 2A rail. Its +3V3 output supplies the STM32 digital power pins, associated decoupling, programming-header supply, and the FB2 input feeding the separate +3.3VA analog rail. The two buck outputs are separate nets.

The LDO uses U4, R8/R9 and C24-C27. The former VDD power symbols use +3V3 to connect these loads to the regulator. The 1 A rating is combined rail capacity, not measured MCU current consumption. Full-load dissipation is approximately 1.7 W at 5 V input; PCB thermal copper and vias remain to be designed.

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
