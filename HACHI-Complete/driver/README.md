# HACHI Cosmos Bridge Driver Assets

This directory contains a small user-space helper that interrogates the USB
links on Linux systems to confirm whether an HTC Vive Cosmos headset is visible
to the operating system. The binary **does not** replace Valve's official
SteamVR device driver; it simply validates connectivity and exposes a
machine-readable status check that the Control Center can display.

## Binary

`cosmos_bridge` is a C++17 program built against `libusb-1.0`. It scans the USB
bus for well-known vendor/product identifiers associated with the Vive Cosmos
family and reports the result either as human-readable text or JSON. Exit codes:

| Code | Meaning                          |
| ---- | -------------------------------- |
| 0    | Headset detected and accessible  |
| 2    | Headset not detected             |
| 3    | Detected but access denied       |
| 1    | Other error                      |

Useful arguments:

```
cosmos_bridge            # Single probe with human output
cosmos_bridge --json     # Emit JSON payload for tooling
cosmos_bridge --monitor  # Continuous polling until interrupted
```

The installer compiles this helper automatically (after installing build and
libusb dependencies) and places the binary under
`~/.local/share/hachi/driver/cosmos_bridge` alongside this README.

## SteamVR Integration

SteamVR still supplies the actual runtime driver that interfaces with the
OpenVR stack. The Control Center surfaces both the health of the locally-built
bridge helper and, when available, the SteamVR Vive Cosmos driver binary so you
can confirm that both components are present.

If SteamVR does not detect your headset after installation, launch SteamVR once
so it can provision its own drivers, then run the HACHI installer again to
refresh the status snapshot.
