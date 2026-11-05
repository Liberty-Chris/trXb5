# Raspberry Pi reader probe

The A1 bench probe resets the PN5180 and sends READ_EEPROM for the six version bytes at address 0x10. It outputs a JSON record and reasserts reset on exit. This first probe neither enables a carrier nor writes label data. A working custom-board label transport still requires Type A activation, ISO-DEP and physical verification.

On Linux use Python bindings for libgpiod v2 and spidev, enable SPI0 and identify the GPIO chip serving the 40-pin connector with `gpioinfo`. J3 is a custom harness. In pin order it carries host 3.3 V, ground, NSS (GPIO5), SCK (GPIO11), MOSI (GPIO10), RESET_N (GPIO6), MISO (GPIO9), BUSY (GPIO25). Leave the Pi hardware CE0 pin unwired. Connect both grounds and feed the controller from its own current-limited 5 V supply.

With the selector and hardware enables verified according to the [commissioning sequence](../docs/validation/REV_A1.md), run this command using the actual chip and fixture name.

```sh
python3 firmware/pi_reader_probe.py --gpiochip /dev/gpiochip0 --fixture bench-A1
```

J4 pins 1–8 are host 3.3 V, GND, A0, A1, A2, SET, RESET, RUN. J5 pins 1–8 are host 3.3 V, GND, position bits 0–4 and ARM. These connections also allow a 3.3 V ESP32 harness. An ESP32 firmware build remains open.

For the optional Pi selector harness, connect J4 pins 3–8 to GPIO12, 13, 16, 17, 27 and 22. Connect J5 pins 3–8 to GPIO4, 18, 19, 20, 21 and 26. Use GPIO line offsets, not connector pin numbers. After the hardware decay, contact and shutdown checks, add `--port 0` to the probe command to use the primary path, or choose 1–4 for an external panel. This mode drops RUN, waits for decay, resets any competing ports with individual 20 ms pulses, verifies the five position bits and asserts RUN only for the version read. It releases RUN on success and on failure. Without the flag the probe only operates J3 and the bench fixture supplies selector control.
