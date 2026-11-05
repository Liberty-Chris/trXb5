> Historical A0 target. Read [CORRECTIONS.md](CORRECTIONS.md) and the current [protocol evidence](../../../docs/research/PROTOCOL.md) before implementation. The archived schematic and original text below predate later protocol findings.

# ROACH NFC reader and writer. Revision A0

This package is a preliminary electrical target for implementation in KiCad. It contains a six sheet PDF schematic, editable SVG sheets and a CSV of verified reader pin connections. It is not a native KiCad project and it is not a completed circuit for manufacture. The amplifier, protection circuit, selector part numbers and interlock implementation remain engineering work. No component should be ordered solely from this package.

## Agreed product target

One reader and amplifier module. One primary local antenna with a disconnectable connection. Four optional external antennas with SMA connectors. Five selectable RF paths total. Flat PCB magnetic loops with a nominal 150 by 150 mm outline. Fine RF trimmer capacitors and coarse solder selectable capacitor positions on each antenna panel. A larger antenna may be substituted during testing.

The working cavity is approximately 457 mm on each side inside a metal vending machine. Desired maximum writing distance is approximately 305 mm. These dimensions are goals rather than demonstrated coverage. Antenna orientation and product dwell time have not been established. A four color label may need approximately 25 to 30 seconds for its full refresh. Confirm the actual cycle time with the production unit.

Current label is the Santek EZ Sign 2.9 inch four color version, nominal SE0290C1 and 296 by 128 pixels, based on the supplied manual and listing. Exact tag IC, air protocol and display commands remain unconfirmed. Balto describes PN532 compatibility as a hypothesis. A generic NFC memory read and write API is not sufficient evidence of display compatibility.

## Desktop ChatGPT handoff prompt

Implement this ROACH NFC target as a hierarchical KiCad project with a controller board and a reusable antenna panel board. Read all six schematic sheets and this document first. Preserve the five selectable paths and manual antenna tuning. Use the supplied Connection_Intent.csv as a checked starting point for ST25R3916B QFN32 connections, then verify every pin against the current official datasheet and the exact orderable part.

Start with the ST25R3916B direct single ended coax path using ST AN5592 and its matching tool. Complete the actual circuit symbols, regulator bypassing, crystal network, host interface, connectors and protection. Use a measured or simulated coil model for the panel. Do not copy application note matching values from an antenna with different dimensions. Keep RF values visibly marked as provisional until the measurements exist.

Build one matched 150 by 150 mm loop panel with series and shunt capacitor tuning and fixed selectable Q damping. Provide voltage rated RF trimmers and coarse capacitor footprints. Place the primary antenna region away from the controller electronics and retain a removable RF connection. If a local daughterboard is necessary for clean RF geometry, identify the mechanical change before treating it as the final integrated primary antenna.

Design five SPDT RF relay paths, each selecting either the shared RF bus or a rated 50 ohm damping termination at its antenna port. Select exact relay and driver parts from verified datasheets. Use a driver per coil with default pulldown and flyback protection. Account for contact voltage and current, off capacitance, isolation at 13.56 MHz, hot switching limitations and relay lifetime. A0 is suitable as a slow bench selector target; qualify relay lifetime or redesign switching before frequent production scanning.

Do not interpret the damped unused ports as proven inactive antenna isolation. Model and measure all panels together. If the loops still perturb the field, assess a series loop break or switched damping located on each panel. Those options may require extra control wiring or a separately engineered bias arrangement over coax. Do not silently assume the four SMA cables provide that control.

Implement an actual hardware interlock and fault latch. Permit RF only when exactly one antenna is selected and stable. Inhibit selector changes while RF is active. RF must be off during relay settling. A software command to disable U101 is not by itself a hardware interlock: U101 has no generic RF_ENABLE pin in this target. Engineer a hardware shutdown, such as supervised reader supply gating plus digital I/O isolation, and verify it cannot backpower the reader or violate power sequencing. PA enable must have a hardware default off. Blank neither the field nor the receive path during an active tag reply or display refresh.

Include an optional PA development region with a removable direct bypass. Complete a successful label refresh with the direct path before energizing the PA. Select the PA topology using NFC envelope and receive requirements, not just 13.56 MHz gain. Preserve protocol specific ASK depth, timing and sidebands. Sense tag load modulation from the antenna bus after the PA output filter, using a properly designed attenuator and receiver protection. Account for forward carrier rejection and close tag loading. Verify U101 input limits and thermal operation at every approved drive level. Document required PA supply and measured allowable output power. Do not invent a supported power level or assert twelve inch range.

Deliver the KiCad project, custom symbol and footprint libraries, BOM with manufacturer part numbers, circuit review notes and an ERC report. Mark remaining unimplemented subcircuits explicitly. Review the complete circuit before creating a PCB layout. Do not generate manufacturing files while RF or PA design items remain unresolved.

## Important corrections and circuit interpretation

The ST25R3916B is a candidate reader rather than a confirmed Santek solution. The QFN32 pin map comes from DS13541 Rev 11 Table 2. ST25R3917B has different functions at some pins and is not a substitute.

Automatic antenna tuning is not included in this coax architecture. AN5592 section 2.4 says its AAT configuration is not possible for its single ended antenna with cable topology. An independent remote tuning design could be explored later. AAT_A and AAT_B being present on the IC does not make remote panel tuning automatic.

The baseline matches the reader driver impedance to a nominal 50 ohm RF bus and each antenna panel to 50 ohms. Fifty ohms is an interface design choice, not the raw impedance of the loop or reader outputs. Fix and document actual coax type, connector and length during panel tuning.

Panel circuit: SMA center to CS401, then RQ401, then the loop and ground return. CT401 is parallel with CS401 for series capacitance adjustment. CP401 and optional CT402 connect the SMA input node to ground as shunt matching elements. Select the final topology and values with the ST matching model and measured assembly. This is a matching starting point and does not prove field performance.

RF_BUS_50 on sheet 3 must connect to either the direct output link or the PA output link, never both. The drawing shows candidate routes, not permanently paralleled outputs. Implement two mutually exclusive link pairs with defined unpopulated states in KiCad. The receive sampling connection remains on the selected output side in both modes. Unused RFO2 and RFI2 must follow the approved single ended configuration from the datasheet and ST guidance; do not guess their termination.

The host connector is a proposed 3.3 V SPI header and is not a Raspberry Pi or Jetson standard pinout. No MCU or USB controller is selected. Implement a host adapter or add an MCU and USB interface deliberately if the desired product connection requires it. PA_LEVEL_CTL has no defined electrical scaling yet; select DAC, filtered PWM or digital control once the PA is designed. Five host requests are logical inputs, not instructions to drive relay coils from GPIO.

Bench 5 V input and host I/O input are placeholders for controlled bench supplies. No vending machine supply voltage, peak current, PA supply or protection rating has been approved. Keep internal U101 regulator outputs separate from external rails. VDD and VDD_TX use the same supply. VDD_AM bypass capacitance depends on the selected modulation mode. Check actual RF voltage across capacitors, resistors, relays and connectors before choosing ratings.

Metal walls, ferrite material, wall clearance and product contents are part of the antenna assembly. Install and tune inside the actual cavity. Do not place copper ground fill behind the active loop. Connector area may have a local ground region outside the active loop. Avoid assuming that the RF ground and machine chassis should be bonded at every panel; plan the chassis connection and measure the resulting system.

## Validation before layout release

Confirm NFC technology and read only identification using a supported reader or phone. Obtain or capture a successful vendor display update to establish command sequence, image packing and field hold time. Preserve tag identifier throughout the transaction. Camera verification establishes that the intended image is visible; protocol acknowledgement alone does not.

Measure inductance, loss and self resonance of each loop. Match the whole cable and panel assembly in its installed location. Validate modulation bandwidth and usable field, not only return loss. Start with low drive and test both closest and farthest product positions. Measure heat and RF stress when the tag is absent as well as present.

Test every selectable path with all inactive panels installed. Select a path before beginning an update and retain it through refresh. Do not perform all antenna polling with an RF relay on every host loop without a lifetime calculation.

Map complete image refresh success, identification success, response verification and camera verification separately. Record orientation, position, product contents, drive setting, cable length, retries, update duration and temperature. Use those results to decide final loop dimensions, amplifier power and mechanical product positioning.

## Primary sources

ST DS13541 Rev 11, retrieved for this target:
https://www.st.com/resource/en/datasheet/st25r3916b.pdf

ST AN5592 Rev 1, especially section 2.3 and section 2.4:
https://www.st.com/resource/en/application_note/an5592-st25r-single-ended-antenna-matching-stmicroelectronics.pdf

ST AN5276 antenna design:
https://www.st.com/resource/en/application_note/an5276-antenna-design-for-st25r391616b-st25r391717b-st25r3918-and-st25r392020b-devices-stmicroelectronics.pdf

NXP AN13219 for antenna matching and metal environment effects:
https://www.nxp.com/docs/en/application-note/AN13219.pdf

Santek product listing supplied by Chris:
https://www.amazon.com/dp/B0G36Y8YVK

Santek support and device behavior:
https://www.santekshop.com/pages/faqs

Existing Balto research:
https://github.com/Liberty-Chris/Balto/blob/main/docs/hardware-paths.md
https://github.com/Liberty-Chris/Balto/blob/main/docs/eink-protocol.md

## Files

ROACH_NFC_RevA0_Schematic.pdf contains the six review sheets. Sheet_01.svg through Sheet_06.svg are editable vector versions of the same sheets. Connection_Intent.csv is a limited pin intent table, not a complete electrical netlist. BOM_Target.csv distinguishes selected candidate parts from unresolved selections. START_HERE.md contains this handoff.
