# Power supply integration

The root schematic contains two separate buck converter outputs:
- TPS54202: +5V, 2A.
- TPSM63606: +5V, 6A.

The TPS7A8101 LDO in LDO_3V3.kicad_sch is supplied by the +5V, 2A rail. Its +3V3 output supplies the STM32 digital power pins, associated decoupling, programming-header supply, and the FB2 input feeding the separate +3.3VA analog rail. The two buck outputs are separate nets.

The LDO uses U4, R8/R9 and C24-C27. The former VDD power symbols use +3V3 to connect these loads to the regulator. The 1 A rating is combined rail capacity, not measured MCU current consumption. Full-load dissipation is approximately 1.7 W at 5 V input; PCB thermal copper and vias remain to be designed.

See ../LDO_KiCad/README.md for component values, the standalone example and reuse instructions. See ../LDO_KiCad/footprint-verification/VERIFICATION.md for the LDO footprint review. Existing buck footprints resolve to supplied files, but their physical dimensions have not been reviewed here.

The project-local symbol and footprint tables include all supplied custom power components. They use paths relative to the project directory.

## Integration validation

validation/verify_integration.py checks the KiCad-exported system netlist against validation/before-integration.xml. It verifies the five LDO nets, all nine U4 pads, MCU supply connections, analog filter input, unique component references, and preservation of the original circuit except the intended VDD/+3V3 merge.

Run it from the repository with a Python installation after exporting system-netlist.xml:

    kicad-cli sch export netlist --format kicadxml -o system-netlist.xml delivery_robot_1.kicad_sch
    python validation/verify_integration.py

This check covers power integration. Run full-system ERC and, once a PCB exists, DRC separately.
