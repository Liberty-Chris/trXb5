# Bench validation plan

Use the actual hardware revision and firmware commit in every record. An empty record is not a passed test. Store raw captures and measurement conditions with the result.

| Stage | Procedure | Acceptance evidence |
| :--- | :--- | :--- |
| Supplies | Current limited input, rail checks, reset and host disconnected tests | No overvoltage, no backpower and RF default off |
| Reader | SPI identity and documented read only label discovery | Correct reader identity and repeatable label metadata |
| Direct RF | One matched panel with amplifier bypassed | Complete vendor compatible image transfer and visible refresh |
| Interlock | Invalid antenna requests, fault and host reset | RF disabled independently of host software |
| Selector | Switch only after RF decay; inspect settled path | Correct selected port and measured isolation |
| Panel tuning | Measure loop L, loss, resonance and assembled match | Saved traces with cable, ferrite and cavity configuration |
| Modulation | Measure outgoing modulation and incoming replies | Protocol compatible timing and receiver input stress within limits |
| PA | Increase drive only through justified operating envelope | Clean modulation, successful RX, acceptable heating and component stress |
| Coupling | All inactive panels physically installed | Measured effects; mitigation when necessary |
| Coverage | Required positions, orientations and product contents | Complete refresh and camera verification at approved conditions |

Record closest and farthest cases, empty cavity behavior, tag absent behavior and repeated updates. Determine allowed dwell time from measured refresh behavior. Verify identity remains associated with the same product throughout read, write and final verification.

Separate identification success, transfer acknowledgement, refresh completion, protocol status and visible camera verification. Do not label a test successful merely because an APDU returned 9000.
