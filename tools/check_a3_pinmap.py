"""Check critical device pin numbers against the reviewed Rev A3 net names."""
import sys
import xml.etree.ElementTree as ET

def verify(xml):
    tree = ET.parse(xml)
    pins = {(p.get("ref"), int(p.get("pin"))):net.get("name").split("/")[-1]
            for net in tree.findall("nets/net") for p in net.findall("node")}
    checked = set()
    def check(ref, *names):
        for pin, net in enumerate(names,1):
            if net == "-":
                assert pins[ref,pin].startswith("unconnected-"), (ref,pin,pins[ref,pin])
            else:
                assert pins[ref,pin] == net, (ref,pin,net,pins.get((ref,pin)))
            checked.add((ref,pin))
    check("U1","VIN_5V","GND","VIN_5V","-","PRE_3V3")
    check("U2","PRE_3V3","GND","ARM","-","RF_3V3","RF_3V3")
    check("U101", *("NSS DWL_REQ MOSI GND MISO RF_3V3 SCK BUSY GND RESET_N - RF_3V3 RF_3V3 - "
                    "RXN RXP VMID TX2 GND - TX1 RF_3V3 - - VDHF RF_3V3 GND CORE_1V8 CORE_1V8 "
                    "CORE_1V8 - - - - - CLK1 CLK2 - IRQ_TP - GND").split())
    check("U201","MID","INV","PA_BIASED","GND","-","AMP_OUT","PA_POS","PA_ENABLE","GND")
    check("U202","LED_A","GND","PA_ENABLE","OPTO_C")
    check("U203","ISO_ON","GND","ISO_GATE","COIL_REF","COIL_RES")
    check("U204","COIL_RES","-","COIL_LOW","GND","GND","COIL_RES","ISO_ON","COIL_RES","GND")
    check("U301", *"RUN_VALID RUN_VALID PRE_3V3 LOW_WIN PORT_SUM PORT_SUM HIGH_WIN HALF RUN_DELAY QUIET_HOLD QUIET_REF GND QUIET_RAW ARM".split())
    check("U302", *"A0 A1 A2 GND GND COIL_OK - GND - - Y4 Y3 Y2 Y1 Y0 PRE_3V3".split())
    for ref, mr, output, sense in [("U303","RUN_VALID","ARM","PRE_3V3"), ("U304","QUIET_RAW","COIL_OK","PRE_3V3"),
                                   ("U305","PRE_3V3","RUN_VALID","PRE_3V3"), ("U306","RUN_VALID","ARM","RES_SENSE")]:
        check(ref,output,"GND",mr,"-",sense,"PRE_3V3")
    check("K200","COIL_RES","-","DRIVE_SEC","DIRECT_J","RF_BUS","PICK_FEED","-","COIL_LOW","GND","GND")
    check("T201","BAL_N","-","BAL_P","DRIVE_SEC","-","GND")
    check("T202","GND","-","PICK","SAMP_P","-","SAMP_N")
    check("Q301","ENV_GATE","GND","QUIET_RAW")
    check("J209","PA_RAW","GND","-")
    check("Y101","XTAL1","GND","XTAL2","GND")
    for i in range(5):
        check(f"K{301+i}",f"COIL_P{i}",f"DAMP{i}",f"PORT{i}","RF_BUS","PRE_3V3",f"SENSE{i}","GND",f"COIL_N{i}")
        check(f"U{310+i}","VIN_5V",f"COIL_P{i}",f"COIL_N{i}","GND","RESET","SET",f"Y{i}","PRE_3V3","GND")
    check("U3", *"HOST_3V3 H_NSS H_SCK H_MOSI H_RESET_N H_MISO H_BUSY GND GND BUSY MISO RESET_N MOSI SCK NSS RF_3V3".split())
    check("U4", *"HOST_3V3 H_ADDR0 H_ADDR1 H_ADDR2 H_SET H_CLEAR H_RUN GND GND HOST_RUN RESET SET A2 A1 A0 PRE_3V3".split())
    check("U5", *"PRE_3V3 SENSE0 SENSE1 SENSE2 SENSE3 SENSE4 ARM GND GND FB_ARM FB_SENSE4 FB_SENSE3 FB_SENSE2 FB_SENSE1 FB_SENSE0 HOST_3V3".split())
    print(f"Verified {len(checked)} numbered pins on {len({ref for ref,_ in checked})} devices against exported connectivity.")

if __name__=="__main__":
    verify(sys.argv[1])
