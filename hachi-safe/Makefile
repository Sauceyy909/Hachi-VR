# Makefile for HTC Vive Cosmos Linux Driver Bridge

CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
LDFLAGS = -lusb-1.0 -lpthread
TARGET = cosmos_bridge
MONITOR = cosmos_monitor.py

.PHONY: all clean install uninstall deps check

all: $(TARGET)
	@echo "Build complete!"
	@echo "Run with: ./$(TARGET) --stream"

$(TARGET): cosmos_bridge.cpp
	$(CXX) $(CXXFLAGS) -o $@ $< $(LDFLAGS)

deps:
	@echo "Installing dependencies for Bazzite Linux..."
	@echo "This requires rpm-ostree and a reboot after installation"
	rpm-ostree install --assumeyes --allow-inactive \
		libusb-devel \
		hidapi-devel \
		python3-pyusb \
		gcc-c++ \
		make

check:
	@echo "Checking system configuration..."
	@echo ""
	@echo "=== USB Devices ==="
	@lsusb | grep -i "0bb4\|28de" || echo "No HTC/Valve devices found"
	@echo ""
	@echo "=== Udev Rules ==="
	@ls -la /etc/udev/rules.d/*vive* 2>/dev/null || echo "No Vive udev rules found"
	@echo ""
	@echo "=== User Groups ==="
	@groups | grep plugdev && echo "✓ User in plugdev group" || echo "✗ User NOT in plugdev group"
	@echo ""
	@echo "=== libusb ==="
	@pkg-config --modversion libusb-1.0 2>/dev/null && echo "✓ libusb found" || echo "✗ libusb NOT found"

install: $(TARGET)
	@echo "Installing Cosmos bridge driver..."
	sudo install -m 755 $(TARGET) /usr/local/bin/
	sudo install -m 755 $(MONITOR) /usr/local/bin/cosmos_monitor
	@echo "Installation complete!"
	@echo "Run with: $(TARGET) --stream"

uninstall:
	@echo "Uninstalling Cosmos bridge driver..."
	sudo rm -f /usr/local/bin/$(TARGET)
	sudo rm -f /usr/local/bin/cosmos_monitor
	@echo "Uninstall complete!"

clean:
	rm -f $(TARGET) *.o
	@echo "Clean complete!"

help:
	@echo "Available targets:"
	@echo "  make          - Build the cosmos_bridge driver"
	@echo "  make deps     - Install build dependencies (requires reboot)"
	@echo "  make check    - Check system configuration"
	@echo "  make install  - Install to /usr/local/bin"
	@echo "  make uninstall- Remove installed files"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make help     - Show this help"
