# Reusable LDO schematic for KiCad

Created and verified with KiCad 10.0.6. All files are kept in this folder under Senior Design.

## Open and edit

Open this repository's LDO_KiCad/STM32_LDO.kicad_pro in KiCad Manager, then open STM32_LDO.kicad_sch and select LDO Power (page 2). The separately pinned original folder is not this repository copy.

The schematic was opened and saved through KiCad 10.0.6 on 2026-10-05 to apply its automatic format repair and conversion. ERC and the exported-netlist connection checks passed again after that save. Do not regenerate it from the original builder, which would overwrite these native editor saves.

Open **STM32_LDO.kicad_pro** in KiCad. Open its schematic, then enter the **LDO Power** hierarchical sheet. The circuit itself is **LDO_Power.kicad_sch**. The top sheet is an integration example with external-source PWR_FLAG symbols and an optional 3.3 V test point. The reusable child contains U1, R1/R2 and C1–C4 only.

The three sheet connections are:

| Sheet pin | Connect to |
|---|---|
| VIN_5V | Buck converter's regulated 5 V supply |
| VOUT_3V3 | STM32, IMU and other 3.3 V supply branches |
| GND | Common system ground |

No global power symbols are used in the child, so importing it will not silently merge rail names elsewhere. EN is tied to input for always-on operation. Both IN and OUT pins are wired; ground pin 4 and exposed pad 9 are grounded.

## Import into your teammates' system schematic

1. Copy `LDO_Power.kicad_sch`, `LDO_Power.kicad_sym` and the `LDO_Power.pretty` folder into their project folder. Keep their existing project and library tables.
2. In **Preferences → Manage Symbol Libraries → Project Specific Libraries**, add `LDO_Power.kicad_sym` with nickname `LDO_Power`. Use `${KIPRJMOD}/LDO_Power.kicad_sym` as its path.
3. In **Preferences → Manage Footprint Libraries → Project Specific Libraries**, add the `LDO_Power.pretty` folder with nickname `LDO_Power`. Use `${KIPRJMOD}/LDO_Power.pretty`.
4. In the system schematic editor, place a hierarchical sheet. Set its file to the copied `LDO_Power.kicad_sch` and keep the existing file contents. Give the sheet a name such as `LDO Power`.
5. Use **Import Sheet Pins** to bring in `VIN_5V`, `VOUT_3V3` and `GND`; wire them to the system rails.
6. Reannotate as needed to avoid duplicate U/R/C references. Run ERC on the complete system and update the PCB from that system schematic.

Do not replace your teammates' `sym-lib-table` or `fp-lib-table` with ours; add the two local entries instead. Symbols are embedded in the schematic for rendering, while the supplied library supports editing and consistency checks. The supplied footprint makes the regulator independent of a globally installed custom footprint library.

You can also copy/paste the components and wires into a flat system schematic, retaining the local libraries and replacing the hierarchical labels with that schematic's rail connections. The hierarchical-sheet method keeps this module easier to edit and reuse.

## Circuit and review status

- TPS7A8101DRBR, 5 V nominal input, 3.296 V nominal output, **1 A combined rail capacity**.
- R1 31.2 kΩ / 0.1%; R2 10 kΩ / 1%; C1 1 µF; C2 10 µF; C3/C4 470 nF.
- C1 Taiyo Yuden EMK107B7105KA-T; C2 TDK C2012X7R1A106K125AC. Resistor and C3/C4 procurement part numbers remain TBD; footprints and ratings are assigned.
- Custom U1 symbol follows TI's pin-function table. Pad 9 represents the exposed ground pad. OUT pin 2 is typed passive to represent its intentional connection to OUT pin 1 without declaring a second independent power source.
- Local footprint was dimensionally verified and corrected against TI DRB0008A drawing 4218875/A: 0.65 mm pitch, 0.6 × 0.31 mm lead pads, 1.5 × 1.75 mm central exposed pad with four narrow extensions, and TI's central paste aperture plus four extensions. See `footprint-verification/VERIFICATION.md` for the full comparison and actual KiCad layer plots. Thermal vias must be added during PCB layout; confirm fabrication and assembly requirements before manufacturing.
- KiCad ERC passed with **0 errors and 0 warnings** on the parent + child project. The exported netlist was checked against the intended five circuit nets and all nine U1 pads.
- WEBENCH electrical simulations from the earlier design are documented in `../STM32-LDO-design.md`. This KiCad schematic does not contain a SPICE simulation model.
- This is a schematic module, not a routed PCB. MCU/IMU local decoupling belongs with those devices in the complete system. A 5 V encoder supply branches before the LDO.
- At 1 A, heat is roughly 1.7 W at 5 V input. Confirm actual combined load, thermal copper/vias and operating temperature before finalizing the PCB.

`preview/` contains KiCad-rendered previews. `ERC-report.txt` and `LDO-netlist.xml` record validation. Edit the supplied native KiCad sources directly.

Source: https://www.ti.com/lit/ds/symlink/tps7a8101.pdf (pin table and DRB0008A drawing 4218875/A).
