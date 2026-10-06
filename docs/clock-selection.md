# STM32 HSE crystal and load-capacitor selection

Selected 2026-10-05 for U1, STM32F091RCTx. Y3/C5/C6 are marked DNP: their selected parts and PCB footprints are retained, but initial assembly leaves them unpopulated. Firmware must use an internal clock while these parts are DNP. Populate all three together before enabling crystal HSE mode. No wires or pin assignments change. This is the high-speed system-clock crystal, not a 32.768 kHz RTC crystal or a powered clock oscillator.

| Reference | Purchasing part | Specification | Footprint |
|---|---|---|---|
| Y3 | Abracon ABM3B-8.000MHZ-B2-T | 8 MHz fundamental, CL 18 pF, ESR max 200 ohm, shunt C0 max 7 pF; +/-20 ppm initial tolerance, +/-50 ppm stability, -20 to +70 C | Crystal:Crystal_SMD_Abracon_ABM3B-4Pin_5.0x3.2mm |
| C5, C6 | Murata GRM1885C1H160JA01D | 16 pF, +/-5%, 50 V, C0G/NP0, 0603 (1.6 x 0.8 mm), -55 to +125 C | project_footprints:C_Murata_GRM1885C1H160JA01 |

## Frequency and loading

[STM32F091xB/xC datasheet, DocID026284 Rev 4](https://www.st.com/resource/en/datasheet/stm32f091rc.pdf), section 6.3.7, Table 39 and accompanying text, page 69, allows a 4-32 MHz HSE crystal and specifies 10 mA/V minimum startup transconductance. Eight MHz supports a 48 MHz system clock using HSE /1 and PLL x6. Firmware must select crystal HSE mode (HSE ON, not external-clock BYPASS), use HSE_VALUE=8000000 and configure the appropriate PLL. Existing team firmware was not provided or verified. The crystal temperature option covers the team's previously stated -10 to +40 C range.

[ST AN2867 oscillator design guide](https://www.st.com/resource/en/application_note/cd00221665-oscillator-design-guide-for-stm8af-al-s-stm32-mcus-and-mpus-stmicroelectronics.pdf), sections 3.3-3.5, explains load capacitance and startup/drive checks. For equal capacitors, CL = C/2 + Cs. The MCU datasheet suggests **10 pF as a rough combined pin/board capacitance estimate**, so C = 2 x (18 - 10) = **16 pF each**. This meets its typical 5-20 pF external-capacitor recommendation. Sixteen pF is an actual standard purchasing value; it is not a placeholder or a required 0805 resistor package. C0G avoids the capacitance drift of high-permittivity dielectrics; 50 V is the available part rating, not the oscillator voltage.

The 10 pF estimate is not a measurement or guaranteed parasitic capacitance. If actual Cs is 5 pF, this pair would load the crystal at approximately 13 pF rather than 18 pF, shifting frequency. Final capacitor values must follow the completed PCB parasitics and measured clock frequency. The 7 pF crystal shunt capacitance C0 belongs in the startup calculation below; do not add it again as Cs in the load calculation.

## Startup screening and drive limit

Using Abracon's maximum ESR and C0 from [ABM3B Rev U, pages 1-2](https://abracon.com/Resonators/abm3b.pdf), the AN2867 screening equation gives:

`gmcrit = 4 x 200 x (2*pi*8e6)^2 x ((7+18)*1e-12)^2 = 1.263 mA/V`

`gain margin = gm_min/gmcrit = 10/1.263 = 7.92`

This exceeds ST's recommended minimum margin of 5 at the specified crystal load. It screens compatibility; it does not replace startup measurements on the assembled board. Abracon specifies 10 uW typical / 100 uW maximum drive. Crystal power cannot be established from the schematic alone. Follow AN2867 section 3.5 to measure drive and section 3.8 for practical startup-margin verification; if drive exceeds 100 uW, introduce/tune a series resistor on OSC_OUT and repeat the startup-margin check. There is currently no series-resistor footprint in this circuit. Reserve space during layout for that possible adjustment, and do not release the clock network for production without the drive check.

## Footprint justification

**Y3:** Abracon page 3 gives a 5.00 +/-0.10 x 3.20 +/-0.10 mm body, maximum height 1.10 mm. Its recommended lands are four 1.80 x 1.20 mm pads with center pitches 4.00 mm horizontally and 2.40 mm vertically. The installed KiCad ABM3B footprint has these exact dimensions: centers (+/-2.00, +/-1.20) mm. Top-view pin numbering matches the manufacturer: 1 lower left, 2 lower right, 3 upper right, 4 upper left; pins 1/3 are crystal terminals and 2/4 are ground. The existing symbol and nets match this mapping. We use the existing standard footprint; no custom crystal symbol or footprint is required.

**C5/C6:** [Murata GRM1885C1H160JA01-01A reference sheet](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM1885C1H160JA01-01A.pdf), page 2, specifies the body as 1.6 +/-0.1 x 0.8 +/-0.1 mm. Page 27, Table 2, GRM18 within +/-0.10 mm, recommends reflow gap a=0.6-0.8, pad length b=0.6-0.7, pad width c=0.6-0.8 mm. The project-local pattern chooses a=0.70, b=0.65, c=0.70: two **0.65 x 0.70 mm pads**, centers +/-0.675 mm, giving a **0.70 mm inner gap**. Its courtyard encloses maximum body and pad extents with at least 0.25 mm clearance. This pattern is derived from Murata's drawing, not imported vendor CAD. The installed generic 0603 has 0.90 x 0.95 mm pads and was not used because those dimensions exceed this reflow recommendation. Assembly process review is still required; a hand-soldering pattern would need a separate assessment.

## Layout and verification

Place Y3 and both capacitors immediately next to PF0/OSC_IN and PF1/OSC_OUT; use short traces and short capacitor ground returns. Ground Y3 pins 2/4. Keep switching nodes, inductors, motor PWM and fast signals away from the oscillator, including adjacent layers. Follow AN2867 layout guidance and account for ground shielding in the final parasitic estimate. Measure clock frequency via an MCU clock-output pin where possible; directly probing crystal pins adds capacitance and can disturb oscillation. Verify startup over the intended supply/temperature range and across boards.

KiCad CLI netlist export and pcbnew footprint measurements confirm the implemented values, pad numbers, pad dimensions and unchanged component-pin net sets. Only Y3/C5/C6 have new nominal values/footprint assignments; their original DNP flags are retained. Before/after ERC reports have identical findings: 5 existing errors and 56 existing warnings, with no new findings. Existing KiCad field-order/formatting edits were preserved. These checks do not simulate crystal startup or certify drive level. F1 was subsequently selected; see [fuse-selection.md](fuse-selection.md). J2 remains the system's missing footprint selection.
