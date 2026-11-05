# Electrical architecture

The controller contains a candidate NFC reader, host interface, protected supply, direct RF path, optional development PA path, receive feedback and five selectable antenna paths. The PA is an intended development feature, not a selected or proven circuit.

The original A0 target uses ST25R3916B QFN32. PN5180 has an independent EZ Sign implementation and must be evaluated before freezing the reader. Its software compatibility evidence does not prove PA compatibility or extended range. Record the final choice in the decision log.

For the current cable target, transform the reader output impedance to a nominal 50 ohm RF bus and match each panel to that interface. Raw reader outputs and raw loops are not inherently 50 ohms. Cable length, relay parasitics, connectors and installed loading belong in the model.

The selector concept uses five SPDT RF relay paths. Each antenna port selects the RF bus or a 50 ohm damping load. This is a proposed bench topology. Relay part numbers, lifetime, damping load dissipation and inactive loop coupling are unresolved. Remote loop interruption or damping might require separate control wiring and is not assumed to work through an SMA cable alone.

The primary antenna is initially integrated or locally mounted with a disconnectable connection. External panels use SMA. Select only one port, with RF off during relay changes and settling. Do not scan antennas during an active image transfer or refresh.

Each panel provides series and shunt capacitor adjustment and fixed selectable Q damping. Avoid resistive tuning pots. RF trimmer ranges and ratings follow actual RF stress. Nearby metal can create eddy current loss and detuning; ferrite backing and wall clearance are part of the installed antenna design.

The ST AN5592 automatic tuning arrangement does not directly apply to its single ended coax cable topology. Use manual panel tuning for the baseline. Any remote automatic tuning requires a separate engineered design.

PA design must preserve outgoing modulation and permit reception of label load modulation. A generic RF amplifier is insufficient without NFC validation. Receive feedback is sampled after the PA output path and requires engineered attenuation, carrier handling and protection. Direct and amplified output links must be mutually exclusive.

A real hardware RF shutdown is required. ST25R3916B has no generic RF_ENABLE pin. Reader supply switching and I/O isolation are one possible approach, subject to power sequencing and no backpower validation. Host software alone is not the hardware interlock. Output power and component ratings remain unassigned until the circuit is engineered.
