# TPS7A8101DRBR footprint verification

Reviewed 2026-10-05 with KiCad 10.0.6. Result: the corrected library footprint matches the nominal geometry of TI's DRB0008A recommended land pattern and stencil example. This is dimensional verification, not approval of a finished board or assembly process.

## Source and method

Source: the TPS7A8101 datasheet downloaded directly from TI, stored here as `TI-TPS7A8101-datasheet.pdf`. Pages 25–27 contain drawing **DRB0008A, 4218875/A (01/2018)**: package outline, example board layout and example stencil. Page 3 supplies the top-view pin mapping. Ordering information identifies TPS7A8101DRBR as the eight-lead DRB package. Verify the purchase order uses this exact part/package.

https://www.ti.com/lit/ds/symlink/tps7a8101.pdf?ts=1781253131486

I visually reviewed those drawings, loaded the saved `.kicad_mod` through KiCad's `pcbnew` library, checked its actual numerical pad geometry, and exported the six relevant layers through KiCad. `geometry-check-results.json` records passing checks and SHA-256 hashes of the footprint and source PDF. `check_footprint.py` is the reproducible geometry check.

## Comparison

All dimensions are millimeters. Coordinates below are relative to the footprint center, viewed from the top of the PCB, with positive Y downward.

| Feature | TI drawing | Corrected KiCad footprint | Result |
|---|---|---|---|
| Body outline | 3.0 × 3.0 nominal, 2.9–3.1 range | 3.0 × 3.0 fabrication outline | Match nominal |
| Lead pitch | 0.65 | 0.65 | Match |
| Opposite lead-pad center spacing | 2.8 | X = ±1.4 | Match |
| Lead copper pads | 0.6 × 0.31, R0.05 | 0.6 × 0.31, R0.05 | Match |
| Lead row positions | 1.95 span across four rows | Y = −0.975, −0.325, +0.325, +0.975 | Match |
| Central exposed-pad land | 1.5 × 1.75 | 1.5 × 1.75 | Match |
| Four narrow ground-land extensions | 0.23 wide; center spacing 0.65; outer ends 0.825 beyond first/last lead row | X = ±0.325; end Y = ±1.8 | Match |
| Central paste aperture | 1.34 × 1.55 | 1.34 × 1.55 | Match |
| Four paste extensions | 0.23 × 0.725; total end-to-end span 2.674 | X = ±0.325, Y = ±0.9745 | Match |
| Preferred non-solder-mask-defined opening | At least 0.07 outward clearance | Explicit +0.07 footprint mask margin | Matches nominal minimum |
| Lead paste | Same nominal aperture as lead land | Explicit zero additional shrink | Match |
| Pin numbering | Top PCB view: 1 upper left, down to 4 lower left; 5 lower right, up to 8 upper right | Same arrangement; exposed land uses pad 9 | Match |

The ground extensions overlap the central pad by 0.05 to form a continuous rounded copper shape. All five copper primitives are numbered **9** and therefore connect to the same ground net. Five paste-only primitives form the stencil opening; they are not extra electrical terminals. The central paste has no blanket full-pad opening added on top of it.

TI labels its example as 84% exposed-pad paste coverage for a 0.125 mm thick stencil. That percentage refers to its device/stencil design, not simply the area of our rectangular central copper land. The footprint adopts TI's aperture dimensions; the assembler must select stencil thickness and processing.

## Corrections made during this review

The original eight lead pads, numbering and central exposed-pad dimensions were correct. The original footprint omitted the narrow ground-land extensions and used four simple paste windows rather than TI's illustrated central aperture plus extensions. Those features were corrected. Explicit mask/paste overrides were added, the courtyard was enlarged to contain the extended copper and pin-1 marker, and silkscreen lines were split to avoid the extended mask openings. A chamfer was added to the fabrication outline at pin 1. The library filename and schematic footprint reference remain unchanged.

The pre-review version is retained as `original-footprint-before-review.txt` for audit only. Do not use it as a library footprint. The original generator was updated so a later regeneration will not restore the old geometry, but do not rerun that generator over hand-edited schematics.

## Inspection files and integration

- `FOOTPRINT_CHECK_ONLY.kicad_pcb`: a single-component inspection board; NOT the system PCB or a production layout.
- `FOOTPRINT_CHECK_ONLY.pdf`: six enlarged KiCad layer plots at 20× scale, NOT a 1:1 paper fit template.
- `kicad-layer-plots/`: SVG versions of copper, paste, mask, silkscreen, fabrication and courtyard.
- The PNG images are crops rendered from those actual KiCad-exported layer plots.

The corrected file is `../LDO_Power.pretty/TI_DRB0008A_VSON8_3x3mm.kicad_mod`. Any future placement from this library will use the corrected footprint. If a PCB already contains the old footprint, use **Tools → Update Footprints from Library** in PCB Editor, then inspect the updated copper, paste and mask. PCB footprints are stored as copies; editing the library alone does not update an existing placement.

The schematic's pin-to-function mapping was also checked: 1/2 OUT, 3 FB, 4 GND, 5 EN, 6 NR, 7/8 IN, exposed pad ground. Existing electrical netlist checks confirm these nets and the exposed pad connection.

## Remaining board-specific work

Thermal vias are not included automatically. TI provides optional example via locations; select via construction with the fabricator/assembler and avoid uncontrolled solder loss into open vias under paste. The system board still needs its ground copper, routing, thermal design, board-level DRC and final fabrication-output review. A 1 A LDO load can dissipate about 1.7 W. No thermal analysis or physical component-fit measurement was performed in this dimensional check.

The footprint has no 3D model; its absence does not change the copper pads. This verification establishes conformity with the cited nominal land pattern. Final assembly acceptance depends on fabrication tolerances, stencil/process choices and the exact part purchased.
