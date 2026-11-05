# Firmware workspace

No firmware implementation is included at initialization. Reader and host interface decisions precede implementation.

Implement reader transport, label profile, ISO 14443 part 4 behavior, antenna selection, RF level control, fault handling and structured job evidence. Handle processing time extensions and chaining as required by the actual reader stack. Keep RF off during antenna switching and maintain field power throughout the required refresh interval.

Preserve factory configuration. Treat device metadata, image transfer and display driver reconfiguration as distinct operations. Camera verification remains an external visible result check.
