# 5 V to 3.3 V, 1 A LDO circuit

Prepared 2026-10-05. This supersedes STM32-LDO-preliminary.md. The circuit is a regulator design candidate with completed WEBENCH electrical simulations; PCB thermal performance and the full STM32 circuit remain to be verified.

## Circuit

See STM32-LDO-schematic.png. WEBENCH design 1 uses TPS7A8101DRBR, with 4.75–5.25 V input, 3.3 V / 1 A output target, and 30 °C ambient.

| Reference | Value / part | Connection |
|---|---|---|
| U1 | TI TPS7A8101DRBR, 8-pin SON with exposed pad | IN pins 7,8 to 5 V; OUT pins 1,2 to 3.3 V |
| C1 | 1 µF, 16 V X7R, Taiyo Yuden EMK107B7105KA-T | IN to GND, close to U1 |
| C2 | 10 µF, 10 V X7R, TDK C2012X7R1A106K125AC | OUT to GND, close to U1 |
| R1 | 31.2 kΩ, 0.1%, 0603 | OUT to FB pin 3 |
| R2 | 10.0 kΩ, 1% | FB pin 3 to GND |
| C3 | 470 nF ceramic | NR pin 6 to GND |
| C4 | 470 nF ceramic | OUT to FB, parallel with R1 |

Tie EN pin 5 to IN for always-enabled operation. Connect GND pin 4 and the exposed pad to ground. R1 is a custom WEBENCH value; a supplier part number still needs selection. Select actual C3/C4 parts and confirm voltage ratings before procurement.

Nominal divider voltage: 0.8 × (1 + 31.2 / 10.0) = 3.296 V. This is a nominal calculation, not a guaranteed tolerance. WEBENCH reports an output tolerance estimate of 3.87% with the selected components.

WEBENCH initially supplied a 28.7 kΩ top resistor that produced approximately 3.10 V, and an output capacitor derated below the regulator's required effective capacitance. Both were corrected before simulation. The selected C2 is estimated by WEBENCH at 8.8 µF after DC-bias derating; C1 at 0.9 µF. The regulator requires at least 4.7 µF effective output capacitance. Account for tolerance, bias and temperature in the final capacitor selection.

## Completed WEBENCH simulations

All three jobs completed successfully in the signed-in account:

| Job | Conditions | Observed result |
|---|---|---|
| Startup - 1 | Input 0→5 V, 10 µs delay and 10 µs rise; 3.3 Ω load | Output rises and settles near 3.3 V; a startup overshoot is visible |
| Load Transient - 2 | 5 V input; load 1→0.1→1 A; 1 µs edges; 120 ms pulse | Output remains near 3.3 V; displayed waveform spans approximately 3.294–3.296 V |
| Input Transient - 3 | 1 A load; input 4.75→5.25→4.75 V; 1 µs edges; 120 ms pulse | Output remains around 3.294 V in the model |

Saved screenshots: WEBENCH-startup.png and WEBENCH-load-transient.png. Waveform values are approximate readings from the displayed axes, not exported sample extrema. Simulation completion and idealized electrical results do not establish real hardware transient performance or thermal safety.

## Correct power architecture

12 V → Buck #2 → 5 V rail → this LDO → 3.3 V STM32 rail.

Any device needing 5 V must branch from the 5 V rail before the LDO. The motor driver retains its separate 12 V power feed. The motor's A/B feedback lines suggest the separate 5 V connection may power an encoder; confirm this with the motor documentation. A 5→3.3 V LDO cannot provide a 5 V output.

STM32 control outputs command a motor driver; motor winding current flows through the driver, not the MCU power rail. Treat 1 A here as requested rail capacity, not established STM32 consumption. If the LDO actually supplies 1 A and other loads share the 5 V rail, the proposed 5 V / 1 A buck has insufficient current margin. Size it for the combined loads plus regulator ground current and margin.

## PCB and MCU integration

At 1 A, dissipation is approximately (5−3.3)×1 = 1.7 W; at 5.25 V it is about 1.95 W, excluding ground current. Using the datasheet's 47.8 °C/W junction-to-ambient value gives a rough junction estimate of 123 °C at 30 °C ambient and 1.95 W, close to the 125 °C recommended maximum. This is a reference-board calculation, not a thermal simulation or prediction for your layout. Use the exposed pad, adequate ground copper and thermal vias, then verify temperature on the final board. A direct 12→3.3 V buck is worth considering if sustained 1 A is actually required.

Place the input/output capacitors close to U1; keep feedback routing short and away from motor switching currents. This schematic covers the regulator only. Add MCU VDD/VDDA decoupling, VCAP components where required, reset and boot circuitry using the exact STM32 datasheet. Confirm 3.3 V motor-driver logic compatibility and whether encoder outputs need level shifting. A Nucleo model is not needed for this generic regulator design; it is needed only to identify its exact onboard circuitry or MCU-specific requirements.

## Sources

## BNO085 IMU addition

The IMU is a parallel load on the supply, not powered through an STM32 GPIO. For a bare BNO085, 3.3 V can supply both VDD (recommended 2.4–3.6 V) and VDDIO (1.7–3.6 V), with the manufacturer's local decoupling. VDD must reach its specified level before or at the same time as VDDIO. For the Adafruit breakout, connect the shared 3.3 V rail to VIN and common ground to GND, following Adafruit's recommendation to match VIN to MCU logic voltage. Its 3Vo pin is an output; do not connect it to the external LDO output.

CEVA revision 1.17, section 6.10, Figure 6-17 gives typical BNO085 currents measured with VDDIO = 3 V and VDD = 3.3 V using SPI. Summing the two rail currents gives approximately 11.0 mA at 100 Hz fusion, 12.84 mA at 200 Hz, 14.4 mA at 400 Hz, and 14.64 mA at 1 kHz gyro rotation vector. These are typical sample configurations, not guaranteed peaks or measurements of the Adafruit board. Allocate 30 mA provisionally for the IMU branch, then measure the actual breakout, operating mode and startup peaks. This allowance is engineering margin, not a datasheet maximum.

The total rail budget is I_STM32 + I_IMU + I_other_3V3. The existing 1 A regulator is sufficient only if that combined load fits within its rating with margin and passes thermal checks. If the STM32 really requires 1 A by itself, adding the IMU exceeds the selected regulator's capacity; do not simply run another simulation above its 1 A rating. The earlier 1 A simulations cover the combined rail only up to 1 A and did not model IMU startup independently.

Sources for this addition:
- CEVA: https://www.ceva-ip.com/wp-content/uploads/BNO080_085-Datasheet.pdf
- Adafruit: https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085/pinouts

## Regulator sources

- TI TPS7A8101 datasheet: https://www.ti.com/lit/ds/symlink/tps7a8101.pdf
- TI product page: https://www.ti.com/product/TPS7A8101
- TDK capacitor: https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=C2012X7R1A106K125AC
- Signed-in WEBENCH design: https://webench.ti.com/power-designer/switching-regulator/simulate/1
