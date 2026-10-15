# F1 battery-input fuse and holder

**Updated 2026-10-15:** the insert changed from 7.5 A to **10 A** (Littelfuse 0297010.L) because +12V now also carries four +5V_AUX peripheral ports and the latch-servo feed (F3). The battery harness fuse is 15 A. Other board fuses are listed at the end.

Selected 2026-10-05. The user confirmed that the requested "F2" means the existing F1, between the J2 battery input (+ pin) and the +12V net feeding both buck converters. F1 is populated. Connectivity and all other part selections are unchanged. This branch supplies the PCB/Pi electronics; it does not include the separately wired 12 V motor-driver power branch.

## Purchasing and assembly

| F1 assembly item | Manufacturer / part number | Quantity | Role |
|---|---|---|---|
| Holder | Keystone Electronics **3568** | 1 | Through-hole MINI blade-fuse holder soldered to the PCB |
| Fuse | Littelfuse **0297010.L** | 1 | Replaceable 10 A, 32 VDC, silver-plated MINI fuse inserted into the holder |

The schematic's main Manufacturer/MPN/Datasheet fields describe the **PCB-mounted holder**, since that is what its footprint represents. FuseManufacturer, FuseMPN and FuseDatasheet identify the separately purchased insert. **Order both items.** A BOM exporter using only the main MPN column will omit the fuse; expand F1 into these two purchasing rows. `fuse-selection.json` explicitly records both quantities. The .L suffix is Littelfuse's 50-piece package designation, not a different electrical rating; distributor single-piece purchases are acceptable when the actual manufacturer part and ratings match.

Assigned footprint: `Fuse:Fuseholder_Blade_Mini_Keystone_3568`. No custom symbol or footprint is required. Standard MINI and low-profile MINI/ATO are different mechanical formats; use the specified standard MINI fuse.

## Electrical sizing

Estimated input current at the 10.8 V minimum normal battery voltage, 85 % combined conversion efficiency for the bucks and 90 % for the servo's external buck (estimates, not measurements):

| Load | Power | Input current |
|---|---|---|
| Raspberry Pi 5 at 5 A (+5V_PI) | 25.5 W | 2.78 A |
| +5V_AUX peripherals, 2.5 A design value | 12.5 W | 1.36 A |
| +5V_SYS (MCU, LDO, encoders, logic, LEDs), 0.5 A | 2.5 W | 0.27 A |
| Board total, servo idle | | about 4.5 A |
| Latch servo stalled (3.2 A at 12 V through an external buck) | 38.4 W | 3.95 A |
| Worst case, servo stalled | | about 8.4 A |

[Littelfuse MINI 32 V datasheet, revised 2024-09-27](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-297-mini32v?assetguid=42c9dd21-a88e-4328-8e67-2f832444faf1), page 3, gives typical allowed currents with a 20 % temperature margin: the 10 A fuse allows 9.2 A at 20 C, 8.6 A at 40 C and 8.0 A at 60 C. The normal 4.5 A load has plenty of margin. The 8.4 A stalled-servo case is close to the 40 C limit but brief (the latch stalls only at its end stop), so 10 A is the right size; 7.5 A (6.0 A at 40 C) would nuisance-blow. Use the actual temperature near the fuse, including enclosure and converter heating.

The same datasheet, pages 1-2, specifies **32 VDC** operation and **1000 A interruption at 32 VDC**, exceeding the 14.6 V normal battery maximum. The 10 A insert has 7.42 milliohm typical cold resistance, giving approximately 0.15 W cold-element loss at 4.5 A, excluding holder contact loss and hot-resistance increase. [Keystone's 3568 product specification](https://www.keyelco.com/product.cfm/product_id/306) lists a 30 A holder and explicitly names Littelfuse 297/997 compatibility. Holder current capability therefore exceeds the selected fuse and expected continuous current. The holder's current rating does not establish the fuse assembly's fault-interruption capacity.

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

A 10 A fuse does **not** open immediately at 10 A. The datasheet page 3 opening-time limits include 0.15-5 seconds at 200% rating (20 A) and 0.03-0.1 seconds at 600% (60 A). Verify that J2, wires, copper, vias and contacts tolerate the applicable overload/clearing energy; their final geometry/rating is not established yet. Use the time-current curve and measured input startup pulse to check nuisance blowing. The 122 A2s typical I2t of the 10 A insert is not a guaranteed total-clearing-energy limit and cannot alone certify PCB protection.

F1 provides branch overcurrent protection; it is not a TVS, reverse-polarity protector or a guarantee against semiconductor damage. The PCB fuse does not protect the battery cable segment before F1; protection near the battery must cover that segment. Motor-branch fusing and regenerative transient suppression require their own design. Do not size this PCB fuse to the battery's 50 A BMS rating.

KiCad export verifies that only F1's purchasing fields/value/footprint changed and all component-pin net sets are identical. Clock Y3/C5/C6 are fitted as of 2026-10-15. J2 was later assigned the AMASS XT30PW-M footprint; see [power-supply.md](power-supply.md#battery-input-j2). Physical fit has been checked against the holder drawing; inrush, thermal and fault-current coordination have not been measured or simulated.

## Other fuses and PTCs (added 2026-10-15)

| Ref | Part | Rating | Protects |
|---|---|---|---|
| Harness | Inline fuse at the battery + lug | 15 A | Battery cable up to J2 |
| F3 | Littelfuse 0451005.MRL (NANO2, SMD) | 5 A very fast, 125 V | Latch-servo battery feed (J17 pin 2). No SMD PTC exists at >= 3.5 A hold and >= 24 V, so this is replaceable, not resettable. Servo stall draws about 3 A here. |
| F4-F7 | Littelfuse 1812L150/16DR (1812 PTC) | 1.5 A hold, 2.8 A trip, 16 V | One per +5V_AUX port (J18-J21) |
| F8, F9 | Bourns MF-NSMF020X-2 (1206 PTC) | 0.2 A hold, 30 V | Encoder 5 V feeds (J7/J15 pin 1) |
| F10, F11 | Bourns MF-NSMF020X-2 (1206 PTC) | 0.2 A hold, 30 V | MDD20A signal-ground returns (J6/J16 pin 3). Opens if the driver's battery-negative lead loosens and motor current tries to return through the board. |

