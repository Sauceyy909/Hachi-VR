#!/bin/bash

# Quick VR Launch Script for HTC Vive Cosmos on Linux

# Set environment variables for VR
export XR_RUNTIME_JSON=/usr/share/openxr/1/openxr_monado.json

# MODIFIED: Added Intel ICD path
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/nvidia_icd.json:/usr/share/vulkan/icd.d/radeon_icd.x86_64.json:/usr/share/vulkan/icd.d/intel_icd.x86_64.json

echo "Starting HTC Vive Cosmos VR Session..."
echo "======================================="
echo ""

# Check if device is connected
if ! lsusb | grep -q "0bb4:0313"; then
    echo "⚠️  WARNING: Vive Cosmos not detected!"
    echo "Please ensure the headset is plugged in and powered on."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Monado service
echo "Starting Monado OpenXR runtime..."
if pgrep -x "monado-service" > /dev/null; then
    echo "✓ Monado is already running"
else
    monado-service &
    MONADO_PID=$!
    echo "✓ Monado started (PID: $MONADO_PID)"
    
    # Give Monado time to initialize
    echo "Waiting for Monado to initialize..."
    sleep 3
fi

# Launch SteamVR
echo ""
echo "Launching SteamVR..."
echo "Note: SteamVR window should open. Put on your headset!"
echo ""

steam -applaunch 250820 &
STEAM_PID=$!

echo "VR Session is running!"
echo "======================"
echo ""
echo "To stop VR:"
echo "  - Close SteamVR normally, or"
echo "  - Press Ctrl+C in this terminal"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping VR session..."
    kill $STEAM_PID 2>/dev/null || true
    killall vrserver 2>/dev/null || true
    killall vrcompositor 2>/dev/null || true
    # Keep Monado running for next session
    echo "✓ VR session ended"
    echo "(Monado service is still running in background)"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Wait for SteamVR to exit
wait $STEAM_PID 2>/dev/null