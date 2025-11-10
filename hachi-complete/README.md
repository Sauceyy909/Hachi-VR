# HTC Vive Cosmos Linux Driver for Bazzite

This repository contains drivers and utilities to get the HTC Vive Cosmos working on Bazzite Linux. 

⚠️ **WARNING**: The Cosmos has limited official Linux support. This is experimental software and may not provide full functionality, especially for inside-out tracking.

## What Works / What Doesn't

### ✅ Currently Working
- Basic device detection
- USB communication
- Integration with Monado OpenXR runtime
- Basic SteamVR compatibility (limited)
- IMU data reading (experimental)

### ❌ Known Limitations
- Inside-out tracking cameras may not work properly
- Room-scale tracking is unreliable
- Controllers may have connectivity issues
- Display might not achieve full refresh rate
- Some features require Windows for firmware updates

## Quick Start

### 1. Run the Setup Script

```bash
chmod +x vive_cosmos_setup.sh
./vive_cosmos_setup.sh
```

**Important**: You MUST reboot after running the setup script!

### 2. Build the Bridge Driver

```bash
make
sudo make install
```

Or manually:

```bash
g++ -o cosmos_bridge cosmos_bridge.cpp -lusb-1.0 -lpthread -std=c++17
```

### 3. Test Your Setup

```bash
# Check system configuration
make check

# Monitor devices
sudo python3 cosmos_monitor.py

# Test the bridge driver
sudo ./cosmos_bridge --info
```

### 4. Launch VR

```bash
# Option A: Use the launcher script
./launch_cosmos_vr.sh

# Option B: Launch manually
export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json
monado-service &
steam -applaunch 250820
```

## Installation Details

### System Requirements

- **OS**: Bazzite Linux (Fedora Atomic-based)
- **GPU**: NVIDIA or AMD with Vulkan support
- **RAM**: 8GB minimum, 16GB recommended
- **USB**: USB 3.0 port for headset
- **CPU**: Modern multi-core processor

### Dependencies

The setup script installs:
- libusb-devel
- hidapi-devel
- cmake, gcc-c++
- kernel-devel
- Monado OpenXR runtime
- Python USB libraries

## Usage

### Monitor Tool

The Python monitor tool helps debug device issues:

```bash
sudo python3 cosmos_monitor.py
```

Features:
1. Scan for connected devices
2. Show detailed device information
3. Test USB communication
4. Real-time device monitoring
5. Check system configuration

### Bridge Driver

The C++ bridge driver attempts to communicate with the Cosmos:

```bash
# Show device info
sudo ./cosmos_bridge --info

# Stream data (experimental)
sudo ./cosmos_bridge --stream
```

## Troubleshooting

### Device Not Detected

```bash
# Check if device is visible
lsusb | grep 0bb4

# Check udev rules
ls -la /etc/udev/rules.d/*vive*

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check permissions
groups | grep plugdev
```

If not in plugdev group:
```bash
sudo usermod -a -G plugdev $USER
# REBOOT REQUIRED
```

### SteamVR Issues

1. **SteamVR won't start**:
   ```bash
   # Check SteamVR installation
   ls ~/.steam/steam/steamapps/common/SteamVR
   
   # Clear SteamVR cache
   rm -rf ~/.steam/steam/steamapps/common/SteamVR/cache
   ```

2. **No headset detected**:
   ```bash
   # Try resetting SteamVR settings
   rm ~/.steam/steam/config/steamvr.vrsettings
   ```

3. **Compositor crashes**:
   - Update GPU drivers
   - Try using Monado instead of SteamVR

### Monado Issues

```bash
# Check if Monado service is running
ps aux | grep monado

# Check logs
journalctl -u monado-service -f

# Restart Monado
killall monado-service
monado-service &
```

### Display Issues

1. **No picture in headset**:
   - Check HDMI/DisplayPort connection
   - Verify GPU supports required resolution
   - Try different display port

2. **Low refresh rate**:
   - Cosmos Elite supports 90Hz
   - Original Cosmos may be limited to 75Hz
   - Check cable quality

### Tracking Issues

**Inside-out tracking is the biggest challenge on Linux.**

Workarounds:
1. Use in seated mode instead of room-scale
2. Consider using external base stations (if you have Cosmos Elite)
3. Update firmware on Windows before using on Linux
4. Use the "Developer mode" in SteamVR for debugging

### Permission Errors

If you get "Permission denied" errors:

```bash
# Run with sudo (not ideal for production)
sudo ./cosmos_bridge --stream

# Or fix permissions permanently
sudo usermod -a -G plugdev $USER
# REBOOT REQUIRED
```

## Advanced Configuration

### Custom udev Rules

Edit `/etc/udev/rules.d/99-vive-cosmos.rules`:

```bash
sudo nano /etc/udev/rules.d/99-vive-cosmos.rules
```

Then reload:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Monado Configuration

Monado config location: `~/.config/monado/`

To enable debug logging:
```bash
export MONADO_LOG=debug
monado-service
```

### SteamVR Configuration

SteamVR settings: `~/.steam/steam/config/steamvr.vrsettings`

Enable direct mode:
```json
{
   "steamvr" : {
      "requireHmd" : false,
      "forcedDriver" : "null",
      "activateMultipleDrivers" : true,
      "directMode" : true
   }
}
```

## Development

### Reverse Engineering the Protocol

The Cosmos protocol is not publicly documented. To help reverse engineer:

1. Use Wireshark with usbmon to capture USB traffic on Windows
2. Analyze the capture with the bridge driver's output
3. Update `cosmos_bridge.cpp` with findings

### Contributing

If you make progress with Cosmos support:
1. Document your findings
2. Submit improvements to the Monado project
3. Share udev rules and configurations

## Known Issues

1. **Camera tracking doesn't work**: The inside-out tracking cameras require proprietary drivers that aren't available on Linux
2. **Audio cutting out**: USB audio may be unstable, consider using separate audio
3. **Controllers disconnecting**: Bluetooth pairing can be flaky
4. **Performance**: May not match Windows performance due to driver limitations

## Alternative Approaches

If the Cosmos doesn't work well:

1. **Use Windows in a VM**: Run Windows in a VM with USB passthrough (requires VT-d/IOMMU)
2. **Dual boot**: Keep Windows for VR gaming
3. **Different headset**: Consider a Vive Pro, Index, or other headset with better Linux support
4. **Wait for updates**: Monado and SteamVR Linux support is actively being developed

## Resources

- [Monado OpenXR Runtime](https://gitlab.freedesktop.org/monado/monado)
- [SteamVR Linux](https://github.com/ValveSoftware/SteamVR-for-Linux)
- [USB Protocol Documentation](https://www.usb.org/documents)
- [Bazzite Documentation](https://bazzite.gg)

## Support

For issues:
1. Check the troubleshooting section
2. Run `make check` to verify configuration
3. Check Monado and SteamVR logs
4. Ask in the Bazzite or Monado communities

## Legal

This is unofficial, community-created software. HTC does not officially support Linux for the Vive Cosmos. Use at your own risk.

The code is provided as-is for educational and experimental purposes.

## Credits

Created by the Linux VR community. Special thanks to:
- The Monado XR project
- The SteamVR Linux team
- The libusb developers
- Everyone working on Linux VR support
