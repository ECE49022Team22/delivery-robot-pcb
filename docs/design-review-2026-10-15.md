# Design review changes, 2026-10-15

This branch implements the decisions from the 2026-10-15 design review. ERC is clean (0/0). DRC has no clearance, short, courtyard or schematic-parity errors; the only warnings are three 0.5 mm reference texts (FB2, C22, C23) that were already there. Venya's existing tracks and vias are unchanged.

## What changed

| Area | Change | Why |
|---|---|---|
| Input (new sheet *Input Protection*) | Q1 SQJ409EP reverse-battery P-FET after F1, D12 12 V gate clamp, R36 gate pull-down. D13 SMBJ16A TVS on +12V. C36 now on +12V after Q1. | A harness crimped backwards at the battery lugs would have reverse-biased C36 and both bucks. The TPS54202 abs max is 30 V; D13 clamps to about 26 V. |
| Input | F1 7.5 A -> 10 A (0297010.L); battery harness fuse 15 A. Nets named VBAT_IN (J2-F1) and VBAT_FUSED (F1-Q1). | The new AUX ports and servo feed raise worst-case input to about 8.4 A. See [fuse-selection.md](fuse-selection.md). |
| Battery sense | R37 100k / R38 22.1k / C37 100 nF -> PA0 (ADC_IN0). | Firmware can read battery voltage: VBAT = V(PA0) x 5.525. |
| AUX (new sheet *AUX Outputs*) | Four 2-pin top-entry JST XH ports J18-J21 (Notecard, LiDAR, GNSS, IMU), one 1.5 A PTC each. Cables plug in from above; use pre-made 2-pin XH cables (no crimping). | +5V_AUX had no outputs. One port's short trips only that port. |
| AUX enable | U5 EN = AUX_EN: Pi 3V3 through D15, 100k pull-down R43, 1 nF C40, force-on jumper J22. | AUX peripherals run only while the Pi is up; J22 for bench work. |
| Pi link | J13 is now a 6-pin JST XH: TXD, RXD, GND, Pi 3V3 (enables AUX), PI_RESET (Q2 -> NRST), PI_BOOT0 (R47 1k -> BOOT0). R12/R13 100R -> 1k. TP2 removed (it duplicated TP1 once F2 was gone). | The Pi can reset and reflash the STM32 (stm32flash over USART2, a ROM-bootloader port on F09x). With 1k, an unpowered Pi or STM32 sees at most a few mA injected (PA2/PA3 are TTa, 5 mA max). |
| Servo (new sheet *Servo Interface*) | J17 3-pin terminal: GND, VBAT_SERVO (through F3, a 5 A SMD fuse), SERVO_SIG. U8 SN74LVC1T45 translates PB10 (3.3 V) to the 5 V servo bus; PB11 = direction. 10k pull-ups as in Hiwonder's reference, D14 ESD. | Hiwonder HTS-30HS: 9-12.6 V, 3.2 A stall, half-duplex UART at 115200 baud on a 5 V bus. A full battery (14.6 V) exceeds 12.6 V, so an external buck set to 11.1-12 V is required. |
| Encoders | U9/U10 74LVC2G17 buffers on +3V3 between the encoder lines and the MCU. Series resistors 100R -> 1k with 1 nF (1 us filter). F8/F9 0.2 A PTC + 1 uF on each encoder supply. J7/J15 pin order is now 5V, GND, A, B, matching the encoder plug. | +3V3 used to come up 80 ms after +5V_SYS, leaving 5 V encoder signals on unpowered MCU pins (ST allows 3.6 V). A shorted encoder cable no longer drops +5V_SYS. |
| LDO | C26/C27 470 nF -> 10 nF. | Start-up 80 ms -> about 1.7 ms. |
| Motor driver | R52/R53 10k pull-downs on both PWM lines; F10/F11 PTC in series with J6/J16 pin 3 (driver signal ground). | The MDD20A brakes on PWM low, so a resetting MCU always means brake. The PTC opens if motor current tries to return through the board. |
| ESD | Spare USBLC6 channels now cover J16 (U6, at J6) and J15 (U7, at J7). | Motor 2 had no ESD protection. |
| Breakouts | J8 = PA0-PA12 + PA15 (1x15), J9 = PB0-PB15 (1x17), in port order, with every pin, used or not. | Consistent breakouts: motor 1's pins were missing while other used pins were present. |
| Clock | Y3/C5/C6 fitted (were DNP). | HSI48 is -4.1/+3.7 % over temperature, too loose for the Pi UART. |
| U3 | C49 100 nF / 50 V right at U3 VIN/GND. | Shortens the switching loop (C14's ground was 9.5 mm from pin 1). |
| J5 | Pin order +12V, GND, +5V_AUX, +5V_SYS, +3V3, +3.3VA. | +12V is no longer next to +5V_AUX. |
| U2/U5 footprint | Fixed in `libs/project_footprints.pretty`, not just on the board: the 8 thermal vias belong to PGND (pads 17-20), 0.3 mm drill, tented bottom, solid zone connection; courtyard added; stray "Designator34" text removed; reference moved off the pads. Value is TPSM63606RDLR (no P prefix). | Fixed the 40 DRC errors from those vias. Fixing the library means "Update footprints from library" keeps the fix. |
| Net classes | HighCurrent clearance 0.3 -> 0.2 mm (the module's own pads are 0.25 mm apart). Stale +5V_LOGIC pattern -> +5V_SYS. New patterns: VBAT_IN, VBAT_FUSED, VBAT_SERVO (HighCurrent); AUX?_5V, ENC?_5V (Power). | |
| Zones | The In1 GND plane and all F.Cu GND zones use thermal reliefs on through-hole pads only (SMD stays solid). | Through-hole GND pins flooded into an inner plane are very hard to hand-solder. The U2/U5 thermal vias override this to solid. |

## New MCU pin jobs (firmware)

| Pin | Net | Use |
|---|---|---|
| PA0 | VBAT_SENSE | ADC_IN0. VBAT = V x 5.525. |
| PB10 | SERVO_TX | USART3_TX (AF4), single-wire half-duplex (HDSEL), **open-drain** (R39 pull-up). Discard your own echoed bytes. |
| PB11 | SERVO_DIR | Output. High before sending, low as soon as TC sets. Pulled low (receive) at reset. |
| PA15, PB3, PA8, PA9 | ENC1_A/B, ENC2_A/B | Now driven by the 3.3 V buffers. Do not enable internal pull-ups. |
| PF0/PF1 | OSC_IN/OSC_OUT | 8 MHz HSE crystal is fitted. |

Pi side: J13 pins 1-6 go to Pi header pins 8 (TXD), 10 (RXD), 6 (GND), 1 (3V3), 16 (GPIO23 = reset), 18 (GPIO24 = BOOT0). To reflash: BOOT0 high, pulse reset, `stm32flash -b 115200 -m 8e1`, BOOT0 low, pulse reset.

## Layout state and what is left

Removed after review (2026-10-15): the DNP encoder pull-ups (R48-R51) and the Pi-alive sense (R44/R45; PA1 is a spare pin again).

The 49 new parts are **parked to the right of the board** in nine labeled groups (titles on the User.Comments layer say where each group belongs), ready for manual placement. Nothing of Venya's routing or placement (LEDs, R12/R13, R26-R33, U6/U7, TP3) was touched. Changes to existing items on the board:

| Item | Change | Why |
|---|---|---|
| C36 | Down next to the U2/U5 input caps | Frees the spot right after F1 for Q1, D12, R36 and D13 |
| J8-J10 | Up 12 mm | Frees the bottom-left edge for the AUX ports J18-J21 |
| J13 | Same slot | New 6-pin XH footprint |
| LEDs D3-D11 | References back to the schematic names; the rail names (3V3, 12V, AUX, SYS, HB, PI, MOT) stay as silkscreen text in the same spot | Board references must match the schematic for parity and assembly |

Placement suggestions: J17 fits on the top edge between J1 and J4 (the right edge is now blocked by the PI LED); keep F3 and D14 at J17 and U8 near PB10/PB11; put U9/U10 and their 1 nF caps between R28/R29 (R32/R33) and the MCU; C49 goes right at U3's VIN/GND pins, between U3 and C14.

Still to do, in suggested order:
1. Place the parked parts (see the group titles), then route the input chain on wide pours, top and In2 together: J2 -> F1 -> Q1 tab -> +12V. Put D13's GND pad on short, wide copper with several vias.
2. Route +12V to U2/U5 inputs, U3 (C49 first, then C14), and F3 (servo feed, about 3 A).
3. Route the +5V_PI path U2 -> J14 as a top-layer pour with a via array, rated for 5 A on 1 oz. In2 inner copper is only 0.5 oz at OSH Park and JLC. Do the same for +5V_AUX from U5 to the PTCs and ports.
4. U3: put a GND via right at C49's ground pad, next to U3 pin 1's vias.
5. Route the signals: encoders through U9/U10 to PA15/PB3/PA8/PA9; motor-driver lines; servo (PB10/PB11 to U8); J13 signals (PA2/PA3, NRST via Q2, BOOT0 via R47, PA1, AUX_EN via D15).
6. Optional: move U6 between J6 and J16, and U7 between J7 and J15, so each ESD array is close to both connectors it now protects.
7. Optionally add a B.Cu GND pour, and stitch it to In1.

## Bring-up order

1. Unpowered: check with a meter whether the MDD20A's signal GND is connected to its VB- terminal.
2. Bench supply 12 V, 0.5 A limit, nothing connected. Check the J5 rails, and TP1 (+5V_PI) before wiring J14.
3. Reverse the bench supply briefly (current-limited): nothing should draw current.
4. Program over SWD (J1). Then test Pi reflash over J13.
5. Scope +5V_SYS and +3V3 together at power-on: +3V3 should follow within about 2 ms.
6. Scope encoder A/B at the connector. If the outputs are open-collector, bodge 4.7k pull-ups from A/B to ENCn_5V.
7. With the MDD20A powered, measure the open-circuit voltage on its PWM/DIR inputs (MCU side is 3.3 V).
8. Load-test J14 at 5 A, then connect the Pi. On the Pi, set `usb_max_current_enable=1` in config.txt and `PSU_MAX_CURRENT=5000` in the EEPROM.
9. Servo: set the external buck to 11.1-12 V before connecting the HTS-30HS.
10. Check U2's temperature at 4-5 A.

## Parts verified (DigiKey stock, 2026-10-15)

| Part | MPN |
|---|---|
| Q1 | SQJ409EP-T1_BE3 |
| D12 | MMSZ5242BT1G |
| D13 | SMBJ16A |
| F1 insert | 0297010.L |
| F3 | 0451005.MRL |
| F4-F7 | 1812L150/16DR |
| F8-F11 | MF-NSMF020X-2 |
| U8 | SN74LVC1T45DBVR |
| U9/U10 | SN74LVC2G17DBVR |
| Q2 | DMN63D8L-7 (switches fully from a 3.3 V gate) |
| D15 | BAT54WS-E3-18 |
| D14 | D5V0L1B2WS-7 |
| J13 | S6B-XH-A(LF)(SN); use a pre-made 6-pin XH cable (or XHP-6 + SXH-001T-P0.6 if you crimp) |
| J18-J21 | B2B-XH-A(LF)(SN) top-entry; pre-made 2-pin XH cables |
| Capacitors | C0603C104K5RACTU (100 nF), GRM1885C1H102JA01D (1 nF), GRM188R72A103KA01D (10 nF), C1608X7R1C105K080AC (1 uF) |
