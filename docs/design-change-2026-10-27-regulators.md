# Design change, 2026-10-27: replacement buck converters

The TPSM63606 modules (U2 Pi 5 V, U5 AUX 5 V) and the TPS54202DDCR (U3, +5V_SYS) went out of stock at DigiKey. All three were replaced with in-stock TI converters. Component values come from TI WEBENCH designs (input 10-15 V, output 5 V), and each layout follows the layout example in the converter's datasheet.

## Parts

| Rail | Converter | Inductor | Input caps | Output cap | Feedback |
| --- | --- | --- | --- | --- | --- |
| +5V_PI (U2), 6 A | TPS56637RPAR | Wurth 74439387033, 3.3 uH, 6.4 mOhm, 18.2 A (L2) | 2x 10 uF 25 V X7R 1206 GRM31CR71E106KA12L (C7, C8) + 100 nF (C9) | 2x 47 uF 16 V 1210 GRM32ER61C476KE15L (C11, C57) | 75k / 10k (R4, R5; 5.10 V, see below), 20k + 100 pF feed-forward (R2, C10), 100k PG pull-up (R61), 100 nF boot (C12) |
| +5V_AUX (U5), 6 A | TPS56637RPAR | Wurth 74439387033 (L3) | C28, C29 + C30 | C32, C58 | R15, R16, R14, C31, R62, boot C33 |
| +5V_SYS (U3), 2 A | TPS54202HDDCR | TDK VLS6045EX-100M, 10 uH, 47 mOhm, 3.4 A (L1) | 22 uF 25 V 1210 GRM32ER61E226KE15L (C14) + 100 nF (C49) | 47 uF 16 V 1210 GRM32ER61C476KE15L (C17) | 100k / 13.7k (R6, R7), 68 pF (C16), 442k EN pull-up (R63), 100 nF boot (C15) |

DigiKey stock on 2026-10-27: TPS56637RPAR 14,313; TPS54202HDDCR 34,376; 74439387033 977; VLS6045EX-100M 69,621; GRM31CR71E106KA12L 28,918; GRM32ER61C476KE15L 75,400; GRM32ER61E226KE15L 413,233. The Yageo 20k was out of stock, so R2/R14 use Panasonic ERJ-6ENF2002V.

### Changes from the WEBENCH BOM

- WEBENCH's inductors (Coilcraft XAL7070, NIC NPI105C) are not sold by DigiKey. The 6 A designs use the Wurth part from WEBENCH's alternate list. The 2 A design uses the TDK VLS6045EX-100M (entered as a custom part with its L/DCR/IDC) because the Bourns SRN8040 alternate did not fit the U3 area. Both were re-simulated.
- WEBENCH's 0201/0402/0603 resistors and small capacitors are 0805 (same values) for the team's 0805 rule. The 2 A input cap is a 1210 of the same value because the WEBENCH 1206 part was out of stock.
- U3's TPS54202H needs the EN pull-up (WEBENCH's Ren); the old TPS54202 floated EN.
- 2026-10-29 (TA review): U2 and U5 have a second 47 uF output capacitor (C57, C58) in parallel with C11/C32, as in the two-Cout layout of datasheet Figure 34. The WEBENCH simulations below were run with one output capacitor; the second one adds capacitance and lowers the output ripple and load-step droop.
- 2026-10-28: R4 (U2 top feedback resistor) is 75k (Yageo RC0805FR-0775KL) instead of WEBENCH's 73.2k. VOUT = 0.6 V x (1 + 75/10) = 5.10 V, so the Pi rail matches the original design's 5.1 V target and keeps margin for harness drop at 5 A. U5 keeps 73.2k (4.99 V). The feed-forward network (R2 20k + C10 100 pF) is unchanged; TI's 5 V table uses the same values.

## Simulations (WEBENCH load transient)

| Design | Load step | Vout range | Settling |
| --- | --- | --- | --- |
| TPS56637, final parts | 0.6 A -> 6 A -> 0.6 A | 4.912 V to 5.056 V (81 mV undershoot) | 0.29 ms |
| TPS54202H, final parts | 0.2 A -> 2 A -> 0.2 A | 4.718 V to 5.212 V (253 mV undershoot) | 0.28 ms |

WEBENCH steady-state estimates: TPS56637 94.7 % at 15 V / 6 A, 558 kHz; TPS54202H 88.9 % at 15 V / 2 A, 500 kHz.

## Layout

- U2 and U5 follow TPS56637 datasheet Figure 34, each rotated as a group: VIN copper with the input caps on one side of the IC, the inductor and output cap on the other, the feedback, feed-forward and PG resistors on a separate AGND island next to pins 1-4, via arrays on VIN (to the In2 +12V plane), PGND, VOUT (to the In2 rail plane) and the AGND island, and GND on In2 under the power stage. U2 stays in its old area; U5 moved below J8 next to the AUX outputs. U5's MODE pin goes straight to PGND pin 9 because the AUX_EN trace has to cross the island.
- U3 follows TPS54202H datasheet Figure 10-1: the bypass and input caps sit left of the IC between GND (top) and VIN (bottom) copper, the SW node goes through vias to an In2 SW pour that runs under the caps to the inductor, the output cap runs from the inductor's VOUT pad into GND, the boost cap goes to a SW via, and a separate VOUT trace across the top feeds the feedback network on the right. The inductor end has 3 SW vias (4 in the figure); a fourth would sit on the bottom-layer +5V_SYS feed.
- Rerouted to make room: PB7 (bottom layer around NRST), PI_BOOT0, USART2_RX, the +5V_SYS feed vias, and the F3 +12V feed vias. The J8 pin legends were split into two lines each.
- 2026-10-29 TA review:
  - C57 sits directly above C11. F1 moved up 1 mm to make room, and the VBAT_IN copper grew with it. C58 sits directly below C32.
  - Extra PGND vias were added next to the output caps, between the inductor and the IC, and at the input caps. U2 went from 20 to 27 and U5 from 25 to 33.
  - On U3, C14 moved down 1 mm so its GND pad has a via on each side, as in Figure 10-1. C49's GND pad gained a via on its right side.
- New library parts: `libs/TPS56637RPAR.kicad_sym`, `TI_RPA0010A_VQFN-HR-10_3x3mm` (TI RPA0010A land pattern) and `L_Wuerth_WE-XHMI-7070` (Wurth land pattern; no vias or traces between the pads).

The TPS56637 has its pads under the body (VQFN-HR), so it needs hot air or a hot plate, as the TPSM63606 did.
