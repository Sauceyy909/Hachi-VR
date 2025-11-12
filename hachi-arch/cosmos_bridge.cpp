/*
 * HTC Vive Cosmos Linux Driver Bridge
 * This driver attempts to interface with the Cosmos inside-out tracking
 * 
 * Compile with:
 * g++ -o cosmos_bridge cosmos_bridge.cpp -lusb-1.0 -lpthread -std=c++17
 */

#include <iostream>
#include <libusb-1.0/libusb.h>
#include <thread>
#include <atomic>
#include <cstring>
#include <vector>
#include <chrono>
#include <iomanip>

// Cosmos USB IDs
#define VENDOR_ID_HTC    0x0bb4
#define PRODUCT_ID_COSMOS 0x0313
#define PRODUCT_ID_CAMERA 0x0178

class CosmosDevice {
private:
    libusb_context *ctx;
    libusb_device_handle *dev_handle;
    std::atomic<bool> running;
    std::thread read_thread;
    
    // Camera tracking data buffer
    std::vector<unsigned char> tracking_buffer;
    
public:
    CosmosDevice() : ctx(nullptr), dev_handle(nullptr), running(false) {
        tracking_buffer.resize(4096); // Adjust based on actual data size
    }
    
    ~CosmosDevice() {
        stop();
        if (dev_handle) {
            libusb_release_interface(dev_handle, 0);
            libusb_close(dev_handle);
        }
        if (ctx) {
            libusb_exit(ctx);
        }
    }
    
    bool initialize() {
        int ret = libusb_init(&ctx);
        if (ret < 0) {
            std::cerr << "Failed to initialize libusb: " << libusb_error_name(ret) << std::endl;
            return false;
        }
        
        std::cout << "Searching for HTC Vive Cosmos..." << std::endl;
        
        // Try to find the Cosmos headset
        dev_handle = libusb_open_device_with_vid_pid(ctx, VENDOR_ID_HTC, PRODUCT_ID_COSMOS);
        if (!dev_handle) {
            std::cerr << "Could not find Cosmos headset (0x" << std::hex 
                      << VENDOR_ID_HTC << ":0x" << PRODUCT_ID_COSMOS << ")" << std::endl;
            std::cerr << "Make sure:" << std::endl;
            std::cerr << "  1. The headset is plugged in and powered on" << std::endl;
            std::cerr << "  2. udev rules are installed correctly" << std::endl;
            std::cerr << "  3. You have permission to access USB devices" << std::endl;
            return false;
        }
        
        std::cout << "Found Cosmos headset!" << std::endl;
        
        // Check if kernel driver is attached
        if (libusb_kernel_driver_active(dev_handle, 0) == 1) {
            std::cout << "Kernel driver is active, attempting to detach..." << std::endl;
            if (libusb_detach_kernel_driver(dev_handle, 0) != 0) {
                std::cerr << "Failed to detach kernel driver" << std::endl;
                // Continue anyway, might work
            } else {
                std::cout << "Kernel driver detached successfully" << std::endl;
            }
        }
        
        // Claim interface
        ret = libusb_claim_interface(dev_handle, 0);
        if (ret < 0) {
            std::cerr << "Failed to claim interface: " << libusb_error_name(ret) << std::endl;
            return false;
        }
        
        std::cout << "Interface claimed successfully" << std::endl;
        return true;
    }
    
    void printDeviceInfo() {
        if (!dev_handle) return;
        
        libusb_device *dev = libusb_get_device(dev_handle);
        struct libusb_device_descriptor desc;
        
        if (libusb_get_device_descriptor(dev, &desc) == 0) {
            std::cout << "\n=== Device Information ===" << std::endl;
            std::cout << "Vendor ID:  0x" << std::hex << desc.idVendor << std::endl;
            std::cout << "Product ID: 0x" << std::hex << desc.idProduct << std::endl;
            std::cout << "USB Version: " << std::dec 
                      << (desc.bcdUSB >> 8) << "." << (desc.bcdUSB & 0xFF) << std::endl;
            
            // Try to get string descriptors
            unsigned char buffer[256];
            if (desc.iManufacturer) {
                libusb_get_string_descriptor_ascii(dev_handle, desc.iManufacturer, buffer, sizeof(buffer));
                std::cout << "Manufacturer: " << buffer << std::endl;
            }
            if (desc.iProduct) {
                libusb_get_string_descriptor_ascii(dev_handle, desc.iProduct, buffer, sizeof(buffer));
                std::cout << "Product: " << buffer << std::endl;
            }
            if (desc.iSerialNumber) {
                libusb_get_string_descriptor_ascii(dev_handle, desc.iSerialNumber, buffer, sizeof(buffer));
                std::cout << "Serial: " << buffer << std::endl;
            }
            std::cout << "=========================\n" << std::endl;
        }
    }
    
    bool sendInitSequence() {
        std::cout << "Sending initialization sequence..." << std::endl;
        
        // These are example commands - actual Cosmos init sequence would need to be
        // reverse-engineered from Windows driver or official SDK
        unsigned char init_cmd1[] = {0x01, 0x00, 0x00, 0x00};
        unsigned char init_cmd2[] = {0x02, 0x01, 0x00, 0x00};
        
        int transferred = 0;
        int ret;
        
        // Send first init command (example - may not be correct)
        ret = libusb_control_transfer(
            dev_handle,
            LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_OUT,
            0x01, // bRequest
            0x00, // wValue
            0x00, // wIndex
            init_cmd1,
            sizeof(init_cmd1),
            1000 // timeout ms
        );
        
        if (ret < 0) {
            std::cerr << "Init command 1 failed: " << libusb_error_name(ret) << std::endl;
            return false;
        }
        
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // Send second init command (example)
        ret = libusb_control_transfer(
            dev_handle,
            LIBUSB_REQUEST_TYPE_VENDOR | LIBUSB_RECIPIENT_DEVICE | LIBUSB_ENDPOINT_OUT,
            0x02,
            0x01,
            0x00,
            init_cmd2,
            sizeof(init_cmd2),
            1000
        );
        
        if (ret < 0) {
            std::cerr << "Init command 2 failed: " << libusb_error_name(ret) << std::endl;
            return false;
        }
        
        std::cout << "Initialization sequence sent (experimental)" << std::endl;
        return true;
    }
    
    void readLoop() {
        std::cout << "Starting read loop..." << std::endl;
        
        int transferred = 0;
        int ret;
        
        while (running) {
            // Try to read from bulk endpoint (typical for HMD data)
            // Endpoint address would need to be determined from device configuration
            unsigned char endpoint = 0x81; // IN endpoint 1 (example)
            
            ret = libusb_bulk_transfer(
                dev_handle,
                endpoint,
                tracking_buffer.data(),
                tracking_buffer.size(),
                &transferred,
                100 // timeout ms
            );
            
            if (ret == 0 && transferred > 0) {
                // Successfully read data
                processTrackingData(tracking_buffer.data(), transferred);
            } else if (ret == LIBUSB_ERROR_TIMEOUT) {
                // Timeout is normal, just continue
                continue;
            } else if (ret != 0) {
                std::cerr << "Read error: " << libusb_error_name(ret) << std::endl;
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
        }
        
        std::cout << "Read loop stopped" << std::endl;
    }
    
    void processTrackingData(unsigned char* data, int length) {
        // This would need to be reverse-engineered or obtained from documentation
        // For now, just print hex dump of received data
        static int packet_count = 0;
        
        if (packet_count % 100 == 0) { // Print every 100th packet
            std::cout << "Packet " << packet_count << " (" << length << " bytes): ";
            for (int i = 0; i < std::min(length, 16); i++) {
                std::cout << std::hex << std::setw(2) << std::setfill('0') 
                          << (int)data[i] << " ";
            }
            if (length > 16) std::cout << "...";
            std::cout << std::dec << std::endl;
        }
        packet_count++;
        
        // TODO: Parse IMU data, tracking data, button states, etc.
        // This requires knowledge of the Cosmos data protocol
    }
    
    void start() {
        if (running) return;
        
        running = true;
        read_thread = std::thread(&CosmosDevice::readLoop, this);
        std::cout << "Device streaming started" << std::endl;
    }
    
    void stop() {
        if (!running) return;
        
        running = false;
        if (read_thread.joinable()) {
            read_thread.join();
        }
        std::cout << "Device streaming stopped" << std::endl;
    }
};

void printUsage(const char* program) {
    std::cout << "Usage: " << program << " [options]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  -i, --info     Show device info and exit" << std::endl;
    std::cout << "  -s, --stream   Start streaming data" << std::endl;
    std::cout << "  -h, --help     Show this help" << std::endl;
}

int main(int argc, char* argv[]) {
    std::cout << "HTC Vive Cosmos Linux Driver Bridge" << std::endl;
    std::cout << "===================================\n" << std::endl;
    
    bool stream_mode = false;
    bool info_mode = false;
    
    // Parse arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "-s" || arg == "--stream") {
            stream_mode = true;
        } else if (arg == "-i" || arg == "--info") {
            info_mode = true;
        } else if (arg == "-h" || arg == "--help") {
            printUsage(argv[0]);
            return 0;
        }
    }
    
    if (!stream_mode && !info_mode) {
        stream_mode = true; // Default to streaming
    }
    
    CosmosDevice cosmos;
    
    if (!cosmos.initialize()) {
        std::cerr << "Failed to initialize device" << std::endl;
        return 1;
    }
    
    cosmos.printDeviceInfo();
    
    if (info_mode) {
        return 0;
    }
    
    // Try to initialize the device
    cosmos.sendInitSequence();
    
    if (stream_mode) {
        cosmos.start();
        
        std::cout << "\nStreaming data (Press Ctrl+C to stop)..." << std::endl;
        std::cout << "Note: This is experimental code. The Cosmos protocol" << std::endl;
        std::cout << "      needs to be properly reverse-engineered for full support.\n" << std::endl;
        
        // Run until interrupted
        std::this_thread::sleep_for(std::chrono::seconds(3600)); // 1 hour max
        
        cosmos.stop();
    }
    
    return 0;
}
