# Capacitor and inductor selections

Selected on 2026-10-05 for the existing 5 V buck rails and 3.3 V LDO. The user supplied a 10.8-14.6 V normal battery range for the 4S LiFePO4 pack. This range is user-provided, not independently verified from a battery manufacturer datasheet. Motor transients are not bounded by the charge voltage. These selections establish component packages and purchasing candidates; they do not constitute a completed transient, loop-stability, thermal, or input-protection validation.

The resistor-only 0805 requirement is preserved. Capacitor values and wiring are unchanged. L1 changes from 10 uH to 15 uH for ripple-current margin. Schematic fields contain Manufacturer, MPN, Datasheet and (for root-sheet parts) Specification. `passive-selections.json` records the selections in machine-readable form.

## Parts and packages

| References | Selected part | Electrical specification | KiCad footprint |
|---|---|---|---|
| C7, C8 | Murata GRM32ER71H106KA12L | 10 uF, 50 V, X7R, 10% | Capacitor_SMD:C_1210_3225Metric |
| C9, C24 | Murata GRM188R71C105KA12D | 1 uF, 16 V, X7R, 10% | Capacitor_SMD:C_0603_1608Metric |
| C10 | Murata GRM1885C1H8R2DA01D | 8.2 pF, 50 V, C0G, +/-0.5 pF | Capacitor_SMD:C_0603_1608Metric |
| C11, C12, C17 | Murata GRM32ER71A476ME15L | 47 uF, 10 V, X7R, 20% | project_footprints:C_Murata_GRM32ER71A476ME15 |
| C14 | TDK C5750X7R1H226M250KB | 22 uF, 50 V, X7R, 20% | project_footprints:C_TDK_C5750X7R1H226M250KB |
| C15 | TDK C1608X7R1H104K080AA | 100 nF, 50 V, X7R, 10% | Capacitor_SMD:C_0603_1608Metric |
| C16 | Murata GRM1885C1H680JA01D | 68 pF, 50 V, C0G, 5% | Capacitor_SMD:C_0603_1608Metric |
| C25, retained | TDK C2012X7R1A106K125AC | 10 uF, 10 V, X7R, 10% | Capacitor_SMD:C_0805_2012Metric |
| C26, C27 | Murata GRM188R71C474KA88D | 470 nF, 16 V, X7R, 10% | Capacitor_SMD:C_0603_1608Metric |
| L1 | Coilcraft XAL6060-153MEC | 15 uH, 20%, shielded power inductor | Inductor_SMD:L_Coilcraft_XAL6060-XXX |

The reusable LDO example uses the same C24/C26/C27 parts as C1/C3/C4. C24 replaces the previously specified Taiyo Yuden ordering number; capacitance, voltage rating and package are preserved.

## Electrical rationale

[TI TPSM63606, SLVSGB4B Rev. B](https://www.ti.com/lit/ds/symlink/tpsm63606.pdf), sections 8.3.3/8.3.4 and Tables 8-1/8-2/8-3, pages 16-17: the input requires two 10 uF ceramics in 1206 or 1210. C7/C8 use the exact Murata 50 V, 1210 part listed in Table 8-2. At 5 V output, Table 8-1 specifies 30 uF effective output capacitance. C11/C12 use a Table 8-3 47 uF X7R candidate in 1210. Section 9.2.1.2.5, page 24, describes two 47 uF ceramics with approximately 52 uF effective at 25 C and 38 uF at -40 C. These are example estimates, not guaranteed limits for every production part. Use the stricter table requirement rather than the conflicting 25 uF prose value. C9 remains a small bias bypass; C10 uses C0G for stable feedforward capacitance. The existing C10 value is retained; package selection does not verify phase margin.

[TI TPS54202, SLVSD26C Rev. C](https://www.ti.com/lit/gpn/tps54202), section 7.2.3.5, pages 15-17, and Table 7-2: 15 uH is the 5 V example selection. With 2 A output, 5 V output, 390 kHz minimum oscillator frequency and 12 uH minimum inductance (15 uH minus 20%), estimated ripple is 0.703 A peak-to-peak at 14.6 V, giving 2.352 A peak and 2.010 A RMS. At the IC's 28 V operating limit the estimate is 2.439 A peak, versus 2.658 A for a 10 uH part at its -20% tolerance. The 15 uH selection improves margin against the 2.5 A minimum high-side current-limit threshold. These calculations omit further inductance reduction under DC current and temperature; confirm the operating curve and actual converter behavior.

[Coilcraft XAL60xx, Document 887 Rev. 02/25/26](https://www.coilcraft.com/getmedia/ea51f14b-7f32-4dc6-8dfe-d4b70549040f/xal60xx.pdf), page 1: XAL6060-153 has 43.75 milliohm maximum DCR, 5.8 A typical 30%-drop saturation current and 4.5/6.0 A thermal reference currents for 20/40 C rise at 25 C ambient. This provides current margin including the IC's 3.9/4.3 A maximum high/low-side thresholds. Normal 2 A copper loss is about 0.18 W using maximum DCR; temperature derating and total AC loss still require checking in the PCB. Its size is chosen for these ratings, not to force an 0805 inductor.

C14 retains 22 uF with a 50 V X7R part to provide voltage headroom and room for a substantial ceramic capacitor on the battery input. Its 2220 body is larger than a 25 V candidate; this is a conservative selection rather than a minimum-area optimization. C15's 50 V rating exceeds the approximately 5 V bootstrap-capacitor differential; C16 uses C0G to retain its small feedforward value. C17 preserves the existing single 47 uF output capacitor with a 1210 purchasing candidate. **The single-capacitor C17 network still needs a load-transient and effective-capacitance check:** TI's 1.5 A, 5% example requires 24 uF at 500 kHz; a 2 A step at 390 kHz requires about 41 uF effective for a 0.25 V droop target. A nominal 47 uF ceramic cannot be assumed to meet that after bias, tolerance and temperature. Add capacitance if the final transient requirement demands it; no additional capacitor or simulated transient result is implied by this commit.

[TI TPS7A8101](https://www.ti.com/lit/gpn/tps7a8101) requires adequate effective output capacitance for stability (4.7 uF minimum). The existing C25 10 uF 0805 selection is retained; its [TDK specification and characteristic data](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1A106K125AC) must be used when checking DC-bias/tolerance/temperature margin. C24 and C26/C27 are 16 V X7R parts for the 5 V input and low-voltage noise/bypass nodes. Replacing part-number placeholders does not change those functions.

## Mechanical sources and checks

- [Murata 10 uF, 50 V reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER71H106KA12-04A.pdf): 3.2 x 2.5 mm body, 1210.
- [Murata 47 uF, 10 V reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM32ER71A476ME15-04CA.pdf): 3225 metric / 1210.
- [Murata 1 uF reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188R71C105KA12-01.pdf): 1.6 x 0.8 mm, 0603.
- [Murata 8.2 pF reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM1885C1H8R2DA01-01A.pdf) and [68 pF reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM1885C1H680JA01-01A.pdf): 0603, C0G.
- [TDK C14 specifications](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C5750X7R1H226M250KB): body 5.70 +/-0.40 x 5.00 +/-0.40 mm, height 2.50 +/-0.30 mm; recommended PA 4.10-4.80, PB 1.20-1.40, PC 4.00-5.00 mm. The supplied project-local footprint uses 4.2 mm inner gap, 1.3 mm pad width, 5.0 mm pad height and a courtyard covering maximum body dimensions. The generic KiCad 2220 footprint's 3.3 mm inner gap was not used. This footprint is derived from TDK dimensions, not imported from TDK. Verify assembly tolerances with the board assembler.
- [TDK C15 specifications](https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C1608X7R1H104K080AA): 0603, 100 nF, 50 V.
- [Murata 470 nF reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188R71C474KA88-01A.pdf): 0603, 16 V X7R.
- Coilcraft Document 887, page 4: nominal body 6.56 x 6.36 mm, maximum height 6.1 mm; recommended two 1.43 x 5.50 mm pads on 4.04 mm centers. The installed KiCad XAL6060 footprint exactly matches those pad sizes and center spacing. Place the marked winding start toward the SW node as recommended for EMI; the inductor is electrically nonpolarized.

Existing MCU bypass-capacitor footprints are retained; this power-passive selection does not assign their purchasing part numbers. Y3 and C5/C6 were subsequently selected together; see [clock-selection.md](clock-selection.md) for the 8 MHz crystal, 16 pF C0G pair and manufacturer land-pattern checks. F1/J2 remain outstanding footprint choices. Input transient suppression, input bulk damping, capacitor RMS heating, final loop stability and PCB thermal/layout review remain separate work.

## Verification

KiCad 10.0.6 successfully exported the edited system schematic. Before/after component-pin net sets are identical. Capacitances and all unrelated values are unchanged; L1 is the sole nominal-value change. All selected footprint files exist. pcbnew loads the C14 footprint and confirms both pads against the TDK ranges; it also confirms the L1 pads against Coilcraft's drawing. Full-system ERC has existing findings and is not a manufacturing sign-off. No converter simulations were rerun in this task.

## Murata output-capacitor land-pattern verification

C11/C12/C17 use a project-local footprint derived from the selected part's reference sheet GRM32ER71A476ME15-04CA, page 27, Table 2 (Reflow Soldering). For GRM32, Murata gives a (inner gap) = 2.0-2.4 mm, b (pad length) = 1.0-1.2 mm, c (pad width) = 1.8-2.3 mm. We choose the midpoint of each range: 2.2 mm gap and two 1.1 x 2.1 mm pads, on 3.3 mm centers. The generic KiCad 1210 pattern had a 1.8 mm gap and 2.7 mm pad width, outside those recommendations, although its IPC nominal package designation was correct. The new courtyard includes the maximum body dimensions (3.5 x 2.7 mm) and copper pad extents with 0.25 mm clearance. Pads 1/2 are nonpolarized and retain their net assignments. pcbnew loading and measured pad dimensions verify the implementation; exported system netlists confirm no component value or connectivity changes. This verifies physical land geometry, not C17 effective capacitance or converter transient response. Other capacitor footprints have not been certified against every manufacturer reflow range by this correction.
