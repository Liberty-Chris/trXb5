# Label and antenna bench tools

Use a physical ISO 14443-4 PC/SC reader for the vendor-compatible host bench. It is a separate transport from the Pi-to-PN5180 SPI probe. Install the pinned Python dependencies in a virtual environment, enumerate readers and substitute the exact name and a new private record path.

```sh
python -m pip install -r software/requirements-bench.txt
python software/ezsign_bench.py readers
python software/ezsign_bench.py identify --reader "reader name" --fixture bench-01 --record identity.jsonl
```

The default identification sends SELECT and GET INFO. If the label requires the documented session authentication before GET INFO, use `--authenticate-for-info` on the physically isolated EZ Sign. This mode sends SELECT, AUTH and GET INFO. Keep only that label in the field. Record the C1 identifier and device-order geometry before a deliberate image test.

```sh
python software/ezsign_bench.py write --reader "reader name" --fixture bench-01 --device-id 12345678 --geometry 296x128 --raster test-pattern.2bpp --record write.jsonl
```

Replace the sample ID with the observed unit's C1. The raster must be 9,472 device-order bytes. For this first profile, use a sparse orientation pattern with four distinct corners and a job identifier. The tool checks that each 2,000-byte block compresses into one short D3 fragment before connecting. Images exceeding that limit require a qualified multi-fragment implementation. For authenticated discovery, pass the same flag to `write`.

The JSONL records attempted and acknowledged blocks, uncertain acknowledgements, refresh acceptance and completion. If status is lost after issuing refresh, the tool holds the session for the rest of its 90-second observation window and records uncertainty. The PC/SC reader and driver own RF continuity and ISO-DEP WTX/chaining. Scope the field. Associate an independently captured photo and its hash with the journal and raster hash. Physical records may contain unit identifiers and should stay outside version control.

Use `python software/panel_match.py --help` for the installed-panel model. The [engineering record](../docs/validation/REV_A1.md) includes reproducible examples and assumptions.
