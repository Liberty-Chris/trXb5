# Controller A3 order

| Option | Selection |
| --- | --- |
| Board | Single rectangular 160 × 112 mm board, 4-layer FR-4, nominal 1.6 mm, green mask, white top legend, lead-free ENIG |
| Stack | JLC04161H-7628, outer 1 oz finished copper, inner 0.5 oz. F.Cu RF and local circuitry, In1.Cu continuous ground reference, In2.Cu signals and power/ground fill, B.Cu signals and ground |
| RF impedance | Select controlled impedance, single-ended 50 Ω ±10% for 0.36 mm outer RF feeds referenced to In1.Cu. Confirm the selected stack on the engineering drawing. Retain narrow component escape traces as drawn. No copper balancing changes in the RF region |
| Drills | Import separate metric PTH and NPTH files. Four unplated 3.2 mm M3 holes at 5 mm edge offsets. Open all connector, header, optocoupler and radial lead holes |
| Via covering | Select **epoxy filled and copper capped via-in-pad**. Planarize both faces. Apply to every 0.20 and 0.30 mm plated hole, including footprint-defined thermal holes in exposed pads. All component lead holes are 0.80 mm and larger. The CAM report gives counts by drill diameter |
| Assembly | Standard PCBA, **top only, SMT reflow plus factory insertion and wave/selective solder of all listed through-hole leads**. Permit removable process rails and tooling outside the finished outline. Flying-probe test. No serialization on pads, RF feeds or SMA lands |
| Stencil | Laser-cut 0.10 mm stainless, top paste Gerber as supplied, no bottom stencil. Retain the DDA and DSG segmented apertures. Inspect filled lands before paste and X-ray U101, U201, U204 and U310–U314 after reflow |

The 0.2104 mm outer prepreg and 0.035 mm outer copper give approximately 49 Ω for a 0.36 mm trace using an IPC-style microstrip estimate with relative permittivity 4.4. The estimate excludes solder mask and launch discontinuities. The order tolerance applies to representative feed geometry. Measure the assembled launches, RF bus and relay stubs with a VNA. [JLCPCB stack calculator](https://jlcpcb.com/impedance) · [Published stack example](https://jlcpcb.com/blog/pcb-esd-protection) · [Via process](https://jlcpcb.com/help/article/pcb-via-covering)


Quote five bare boards and populate two, using the supplied BOM and CPL. Include the nine SMA connectors, J1–J5 and J209 headers/connectors, C204, C218 and U202 in the factory insertion pass. The routing and paste layers are single-sided for assembly. Leave all five SMA holes per connector open. Use a wave pallet or selective process as appropriate for the bottom copper and the plugged vias. Allow removable 5 mm process rails outside the finished outline.

Review the numbered drawing before programming the machines. K200 is spring return. K301–K305 have the eight-lead Omron latching body. Orient the marked coil end toward pins 1/8. Observe cathode bands, the two transformer dot pairs, optocoupler pin 1, positive electrolytic pads and the keyed JST shroud. U101, U201 and the six DSG drivers use exposed lands. Retain the supplied stencil windows. Confirm the copper-capped exposed lands are planar and inspect solder coverage by X-ray. Supply the finished board with the HARD ARM jumper open. A shunt, mating plugs, power cables, coax, host and test loads are external fixtures.

Upload the Gerber archive first, then match all 185 designators using the BOM and CPL. All eight distinct through-hole parts in this job have a JLCPCB Wave Soldering listing. [JLC mixed assembly capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) · [Parts and assembly audit](../../../docs/validation/REV_A3.md)
