# Vendor payload evidence

The owner identified [Balto's original vendor files](https://github.com/Liberty-Chris/Balto/tree/b37a8c54490d3e98c58753e27abee4e6a4fd31ce/original). This commit adds two binaries relative to the older desktop clone. The files contain different applications. All observations below came from reading the archives and inspecting bytes. No vendor program, installer or hardware transaction was executed.

| Artifact | Git blob or SHA-256 | Finding |
| --- | --- | --- |
| EZ_Sign_NFC_windows.exe | Git `4f21386930479671eae59ba663b4c2fd02d92978` | Byte-identical to the local vendor v1.0.2 bootstrapper. |
| NFC payload, app.so | SHA-256 `9fc942b8bb673144a1be33269b8786aa5c39454fc484b2a8db010a0201b7e728` | Flutter application payload contains Windows PC/SC library, reader enumeration, card connection and transmit symbols plus LZO1X compression identifiers. |
| EZ_Sign_1.2.6.0-x86.rar | Git `6ccb0f7cb102920ccca3772b5fc971bd8f58282f`, SHA-256 `ce6e0169ea050a46bb8b3a4b591533b4ea2e3cfa9881c42723a3b260ed45fb1d` | Contains a single MSI. Its cabinet contains a managed EZSign.exe and SerialPortHelp.dll. |
| Serial application, EZSign.exe_1 | SHA-256 `5f6ef062615e44656f15f5d5ca545a9a50106f670ca60751b6bd6d7d80c8383e` | Managed metadata names serial-port operations for image transfer, power and factory settings. This is a different host path. |

**NFC command evidence.** The following literal ASCII hex strings occur at zero-based offsets in the NFC app.so.

| Offset | Decoded command | Interpretation against the independent reference |
| --- | --- | --- |
| 0x2c7010 | `00 A4 04 00 07 D2 76 00 00 85 01 01` | Select application by AID |
| 0x3816d0 | `00 20 00 01 04 20 09 12 10` | Authentication sequence |
| 0x47a2a0 | `00 D1 00 00 00` | Get device information |

**Reproduce locally.** Use 7-Zip to extract the PE overlay named `[0]` from the NFC installer. In this precise blob the embedded CAB starts at overlay offset 1,759,232. Complement its first 512 bytes, read the little-endian cabinet length at header offset 8 (17,783,249), and append bytes 512 through length minus one from the original cabinet. Extract app.so, confirm its hash, then inspect the ASCII bytes at the offsets above. For the RAR use the sequence RAR → MSI → disk1.cab → EZSign.exe_1. The MSI SHA-256 is `02ff8224cfb04299ff138398c19f1a87a38215b6da81f2fa2edc8194aeb81d41`. Keep vendor binaries outside the design deliverables.

This independently corroborates the AID, AUTH and GET INFO from the published EZ Sign work. PC/SC is the vendor's host-facing path. Captures from a powered label are still needed for command order on this unit, ACK timing, image orientation, uninterrupted field requirements and visible completion. No factory-setting command belongs in the bench writer.
