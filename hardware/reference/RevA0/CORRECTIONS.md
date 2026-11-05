# Corrections to the historical A0 target

The package predates discovery of the independent EZ Sign implementation. Its statements that the exact air protocol is wholly unknown are superseded by docs/research/PROTOCOL.md. Type A, ISO 14443 part 4 and proprietary APDU behavior are externally documented for the product family. Actual unit validation is still pending.

The original ST25R3916B pin intent and circuit sketches remain candidate starting points. Reader selection must compare PN5180, which has an independent EZ Sign implementation. Do not automatically carry the ST reader choice into a final PCB.

No completed PA circuit, selected RF relay, native KiCad file or demonstrated range is contained here. The PDF and SVGs are conceptual and contain unresolved blocks. Five damped ports do not establish isolation. Automatic antenna tuning is not implemented for the coax baseline. Direct and amplified paths are mutually exclusive rather than parallel outputs.

Read current architecture, decision and handoff documents before continuing. This historical material is retained for traceability rather than presented as a complete schematic.
