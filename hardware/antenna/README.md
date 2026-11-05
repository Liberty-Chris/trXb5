# Rev A1 interchangeable panel

Open [Rev A2](RevA2/Panel_A2.kicad_pro) for the 150 mm panel with the 68 pF shunt trim population. [Fabrication and assembly](../../releases/RevA2/panel/ORDER.md)

Open [Panel_A1.kicad_pro](RevA1/Panel_A1.kicad_pro) in KiCad 10. The [schematic](RevA1/Panel_A1.pdf) and [BOM](RevA1/BOM.csv) apply to one panel. Use the same panel for the disconnectable primary or any of the four optional ports.

The PCB is 150 × 150 mm. There are four 3.2 mm mounting holes on a 126 mm square. A 2 mm copper trace follows the 140 mm centerline loop. Matching components and the vertical SMA are accessible at the feed end. Leave the aperture clear and use nonconductive mounting hardware for the first measurement.

C401/C402/C403 are shunt capacitance. C404/C405/C406 are series capacitance. C402 and C405 are unpopulated coarse positions. The two trimmers have positive tool clearance on the component side. Measure installed impedance and stress before selecting final population or assembly files. [Calculations and tuning procedure](../../docs/validation/REV_A1.md)
