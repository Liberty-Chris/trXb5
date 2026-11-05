# Protocol evidence and implementation leads

The most specific accessible implementation is JUN-KOBAYASHI/ezsign-nfc-tools. Its README explicitly describes EZ Sign 2.9 inch and 4.2 inch displays using an ESP32 and PN5180. Its protocol document states 13.56 MHz ISO 14443 Type A, APDUs and activation through RATS into ISO 14443 part 4. The document attributes earlier reverse engineering to niw and alt-core. See SOURCES.md for exact links and reviewed blob identifiers.

These are independently documented product family findings. They have not yet been reproduced on Chris's exact physical label by this PCB project. They do not establish the actual chip model, range or amplifier compatibility.

| Topic | Source documented behavior | Project consequence |
| :--- | :--- | :--- |
| Carrier and activation | 13.56 MHz, Type A, RATS and ISO 14443 part 4 | Reader must expose the required activation and exchange behavior |
| Application selection | AID D2 76 00 00 85 01 01 | Profile lead; an AID alone does not identify the chip |
| Authentication | Command 00 20 00 01 04 20 09 12 10 | External reference value, not a reason to blindly authenticate an unknown unit |
| Device information | Command 00 D1 00 00 00 with TLV response | Start investigation with documented information retrieval |
| Image transfer | Proprietary D3 packets with compression and fragmentation | Generic memory block writing is insufficient |
| Refresh | Separate command and completion behavior | Keep field power through the required interval |
| Transport timing | Chaining and processing delays need explicit handling | Review WTX and timeout behavior in actual transport code |
| Image orientation | 2.9 inch orientation handling and device variation | Validate a physical test pattern before automating production images |

Preserve factory display configuration. Compatible FMSC projects distinguish writing image data from replacing display driver configuration. Do not copy configuration or waveform recipes from a different screen simply because the controller family appears similar.

The owner pointed to Balto's original vendor files. Static extraction of the NFC application recovered Windows PC/SC transport symbols, LZO compression and literal SELECT, AUTH and GET INFO commands. A separate 1.2.6 archive contains a serial application. Earlier Balto Python code simulated writes. The working in-house writer and a trace from the physical label remain outstanding. [Vendor payload hashes and offsets](VENDOR-PAYLOAD.md) · [Recovered team artifacts](RECOVERY.md)

solar2ain/ink-nfc-fmsc-by-pn532 provides a second FMSC implementation reference with PN532 compatible UART readers. Its tested boards differ from the Santek label. Treat it as comparative evidence, not proof of Santek compatibility. Its documentation warns that some operations overwrite factory display configuration.

The original RevA0 package's broad statement that the air protocol is unknown is superseded by the evidence above. Exact physical unit compatibility and the location of our own completed reverse engineering artifacts remain open.
