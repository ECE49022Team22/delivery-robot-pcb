# F1 battery-input fuse and holder

Selected 2026-10-05. The user confirmed that the requested "F2" means the existing F1, between the J2 battery input (+ pin) and the +12V net feeding both buck converters. F1 is populated. Connectivity and all other part selections are unchanged. This branch supplies the PCB/Pi electronics; it does not include the separately wired 12 V motor-driver power branch.

## Purchasing and assembly

| F1 assembly item | Manufacturer / part number | Quantity | Role |
|---|---|---|---|
| Holder | Keystone Electronics **3568** | 1 | Through-hole MINI blade-fuse holder soldered to the PCB |
| Fuse | Littelfuse **029707.5L** | 1 | Replaceable 7.5 A, 32 VDC, silver-plated MINI fuse inserted into the holder |

The schematic's main Manufacturer/MPN/Datasheet fields describe the **PCB-mounted holder**, since that is what its footprint represents. FuseManufacturer, FuseMPN and FuseDatasheet identify the separately purchased insert. **Order both items.** A BOM exporter using only the main MPN column will omit the fuse; expand F1 into these two purchasing rows. `fuse-selection.json` explicitly records both quantities. The .L suffix is Littelfuse's 50-piece package designation, not a different electrical rating; distributor single-piece purchases are acceptable when the actual manufacturer part and ratings match.

Assigned footprint: `Fuse:Fuseholder_Blade_Mini_Keystone_3568`. No custom symbol or footprint is required. Standard MINI and low-profile MINI/ATO are different mechanical formats; use the specified standard MINI fuse.

## Electrical sizing

The existing outputs are 5 V / 6 A and 5 V / 2 A, totaling **40 W** at their full rated loads. The LDO is already supplied from the 2 A branch; its load must not be counted again. Using the supplied battery's 10.8 V minimum normal voltage and an **assumed 85% combined conversion efficiency**:

`Iinput = (5*6 + 5*2) / (10.8*0.85) = 4.36 A`

This is a sizing estimate, not a measured maximum or guaranteed converter efficiency. At 14.6 V with the same efficiency, it is 3.22 A. Quiescent current, actual thermal efficiency, fuse/connector/wire voltage drops, load peaks and startup must be included in the final measurements. No additional direct 12 V loads are included; revisit the selection if such loads are added to the fused net.

[Littelfuse MINI 32 V datasheet, revised 2024-09-27](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-297-mini32v?assetguid=42c9dd21-a88e-4328-8e67-2f832444faf1), page 3, provides a typical allowed-current table with a 20% temperature security margin. At 40 C, its 5 A fuse allows 4.0 A, while its 7.5 A fuse allows 6.0 A. Thus **7.5 A is the lowest standard option in this series above the estimated 4.36 A continuous load at the team's 40 C ambient limit**. The allowance decreases to 5.5 A at 60 C and 5.1 A at 80 C. Use the actual temperature near the fuse, including enclosure and converter heating. These are application-dependent typical recommendations, not guaranteed hold-current limits. Do not apply another generic derating factor to this already derated table without identifying why it is needed.

The same datasheet, pages 1-2, specifies **32 VDC** operation and **1000 A interruption at 32 VDC**, exceeding the 14.6 V normal battery maximum. The 7.5 A insert has 10.85 milliohm typical cold resistance, giving approximately 0.21 W cold-element loss at 4.36 A, excluding holder contact loss and hot-resistance increase. [Keystone's 3568 product specification](https://www.keyelco.com/product.cfm/product_id/306) lists a 30 A holder and explicitly names Littelfuse 297/997 compatibility. Holder current capability therefore exceeds the selected fuse and expected continuous current. The holder's current rating does not establish the fuse assembly's fault-interruption capacity.

The fuse remains a **protection candidate pending coordination with the final conductors and source**. Battery BMS limits of 50 A continuous and 150 A briefly do not bound prospective short-circuit current. Confirm the battery/source and wiring cannot deliver a fault exceeding the fuse's 1000 A DC interrupt rating, or select protection with sufficient interruption capacity. The seller battery PDF does not provide the needed short-circuit/clearing specification.

## Verified mechanical footprint

[Keystone drawing 3568, revision E, 2023-05-17](https://www.keyelco.com/product-pdf.cfm?p=306) gives four holes on **9.92 x 3.40 mm** centers and **1.60 mm minimum hole diameter**. The manufacturer drawing was inspected from this [distributor-hosted copy](https://static.maritex.eu/file/display/oKaI5t3ooLkeEAjZJtX48nclaUUGNRNT/KEYSTONE-3568.pdf) when direct download was blocked. The drawing shows a 16.00 x 6.73 mm holder body, 7.37 mm above-board height and 2.79 mm lead extension; its dimensions are unrelated to an 0805 resistor package.

pcbnew loads the installed KiCad footprint and confirms:

- Terminal 1: pads at (0,0) and (0,3.40) mm.
- Terminal 2: pads at (9.92,0) and (9.92,3.40) mm.
- All four pads: **1.78 mm plated-hole drill**, **2.78 mm copper diameter**. The holes exceed the manufacturer's 1.60 mm minimum; annular-ring width is 0.50 mm nominal. Confirm the PCB fabricator's finished-hole/plating tolerances.
- Both holes of each physical contact have the same pad number. This correctly maps the four mechanical leads to the two electrical fuse terminals. Route adequate copper to both pads of each terminal.

The 297 insert's 2.8 x 0.8 mm blades match the holder family specified by Keystone. The fuse goes into the holder; it is not soldered directly into these four PCB holes. Reserve clearance above the installed fuse and room to grip/remove it; the holder's 7.37 mm height alone is not the assembled height. Position it near J2 with appropriately rated input copper and accessible service space.

## Protection boundaries and remaining verification

A 7.5 A fuse does **not** open immediately at 7.5 A. The datasheet page 3 opening-time limits include 0.15-5 seconds at 200% rating (15 A) and 0.03-0.1 seconds at 600% (45 A). Verify that J2, wires, copper, vias and contacts tolerate the applicable overload/clearing energy; their final geometry/rating is not established yet. Use the time-current curve and measured input startup pulse to check nuisance blowing. The 82 A2s typical pre-arcing I2t is not a guaranteed total-clearing-energy limit and cannot alone certify PCB protection.

F1 provides branch overcurrent protection; it is not a TVS, reverse-polarity protector or a guarantee against semiconductor damage. The PCB fuse does not protect the battery cable segment before F1; protection near the battery must cover that segment. Motor-branch fusing and regenerative transient suppression require their own design. Do not size this PCB fuse to the battery's 50 A BMS rating.

KiCad export verifies that only F1's purchasing fields/value/footprint changed and all component-pin net sets are identical. Clock Y3/C5/C6 remain DNP. J2 was later assigned the AMASS XT30PW-M footprint; see [power-supply.md](power-supply.md#battery-input-j2). Physical fit has been checked against the holder drawing; inrush, thermal and fault-current coordination have not been measured or simulated.
