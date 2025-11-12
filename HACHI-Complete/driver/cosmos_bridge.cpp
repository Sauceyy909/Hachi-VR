#include <libusb-1.0/libusb.h>

#include <algorithm>
#include <chrono>
#include <csignal>
#include <cstdint>
#include <cstdlib>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {

struct Candidate {
    uint16_t vendor_id;
    uint16_t product_id;
    const char* label;
};

const Candidate kCandidates[] = {
    {0x0bb4, 0x0309, "HTC Vive Cosmos"},
    {0x0bb4, 0x0316, "HTC Vive Cosmos Elite"},
    {0x0bb4, 0x0317, "HTC Vive Cosmos External"},
    {0x0bb4, 0x0400, "HTC Vive Link Box"},
};

volatile std::sig_atomic_t g_should_exit = 0;

void handle_signal(int) {
    g_should_exit = 1;
}

std::string iso_timestamp() {
    using clock = std::chrono::system_clock;
    const auto now = clock::now();
    const std::time_t tt = clock::to_time_t(now);
    std::tm tm{};
#ifdef _WIN32
    gmtime_s(&tm, &tt);
#else
    gmtime_r(&tt, &tm);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%dT%H:%M:%SZ");
    return oss.str();
}

std::string escape_json(const std::string& value) {
    std::ostringstream oss;
    for (const char ch : value) {
        switch (ch) {
            case '\\': oss << "\\\\"; break;
            case '"': oss << "\\\""; break;
            case '\n': oss << "\\n"; break;
            case '\r': oss << "\\r"; break;
            case '\t': oss << "\\t"; break;
            default:
                if (static_cast<unsigned char>(ch) < 0x20) {
                    oss << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                        << static_cast<int>(static_cast<unsigned char>(ch))
                        << std::dec << std::setfill(' ');
                } else {
                    oss << ch;
                }
        }
    }
    return oss.str();
}

std::string format_hex(uint16_t value) {
    std::ostringstream oss;
    oss << "0x" << std::hex << std::uppercase << std::setw(4) << std::setfill('0')
        << value;
    return oss.str();
}

std::string format_port_path(const std::vector<uint8_t>& ports) {
    if (ports.empty()) {
        return "";
    }

    std::ostringstream oss;
    for (size_t i = 0; i < ports.size(); ++i) {
        if (i != 0) {
            oss << '.';
        }
        oss << static_cast<int>(ports[i]);
    }
    return oss.str();
}

struct ProbeResult {
    bool found = false;
    bool permission_denied = false;
    bool open_attempted = false;
    uint16_t vendor_id = 0;
    uint16_t product_id = 0;
    std::string label;
    std::string product_string;
    uint8_t bus = 0;
    uint8_t address = 0;
    std::vector<uint8_t> ports;
    std::string message;
    std::string error;
};

ProbeResult probe_headset(libusb_context* ctx, bool attempt_open) {
    ProbeResult result;

    libusb_device** list = nullptr;
    const ssize_t count = libusb_get_device_list(ctx, &list);
    if (count < 0) {
        result.error = libusb_error_name(static_cast<int>(count));
        return result;
    }

    for (ssize_t i = 0; i < count && !result.found; ++i) {
        libusb_device* device = list[i];
        libusb_device_descriptor desc{};
        if (libusb_get_device_descriptor(device, &desc) != LIBUSB_SUCCESS) {
            continue;
        }

        for (const auto& candidate : kCandidates) {
            if (desc.idVendor == candidate.vendor_id &&
                desc.idProduct == candidate.product_id) {
                result.found = true;
                result.vendor_id = desc.idVendor;
                result.product_id = desc.idProduct;
                result.label = candidate.label;
                result.bus = libusb_get_bus_number(device);
                result.address = libusb_get_device_address(device);

                std::vector<uint8_t> buffer(8);
                const int port_count = libusb_get_port_numbers(
                    device, buffer.data(), static_cast<int>(buffer.size()));
                if (port_count > 0) {
                    result.ports.assign(buffer.begin(), buffer.begin() + port_count);
                }

                if (attempt_open) {
                    libusb_device_handle* handle = nullptr;
                    const int open_status = libusb_open(device, &handle);
                    result.open_attempted = true;
                    if (open_status == LIBUSB_ERROR_ACCESS) {
                        result.permission_denied = true;
                        result.message =
                            "Headset detected, but USB permissions blocked access."
                            " Add udev rules or run the installer again.";
                    } else if (open_status == LIBUSB_SUCCESS && handle != nullptr) {
                        unsigned char product[256];
                        if (desc.iProduct != 0) {
                            const int len = libusb_get_string_descriptor_ascii(
                                handle, desc.iProduct, product,
                                static_cast<int>(sizeof(product)));
                            if (len > 0) {
                                result.product_string =
                                    std::string(reinterpret_cast<char*>(product), len);
                            }
                        }
                        libusb_close(handle);
                        result.message =
                            "Headset detected and accessible over USB.";
                    } else if (open_status != LIBUSB_SUCCESS) {
                        result.message = "Headset detected, but could not be opened: ";
                        result.message += libusb_error_name(open_status);
                    }
                } else {
                    result.message =
                        "Headset detected. USB open skipped at caller request.";
                }

                break;
            }
        }
    }

    libusb_free_device_list(list, 1);

    if (!result.found && result.error.empty()) {
        result.message = "Vive Cosmos headset not detected.";
    }

    return result;
}

struct Options {
    bool json = false;
    bool monitor = false;
    int interval_seconds = 3;
    bool attempt_open = true;
};

void print_usage(const char* name) {
    std::cerr << "Usage: " << name << " [--json] [--monitor] [--interval N] [--no-open]\n";
}

int render_json(const ProbeResult& probe, int exit_code) {
    std::cout << '{'
              << "\"timestamp\":\"" << iso_timestamp() << "\",";
    std::cout << "\"present\":" << (probe.found ? "true" : "false") << ',';
    std::cout << "\"permission_denied\":"
              << (probe.permission_denied ? "true" : "false") << ',';
    std::cout << "\"open_attempted\":"
              << (probe.open_attempted ? "true" : "false") << ',';
    if (probe.found) {
        std::cout << "\"vendor_id\":\"" << format_hex(probe.vendor_id) << "\",";
        std::cout << "\"product_id\":\"" << format_hex(probe.product_id) << "\",";
        std::cout << "\"bus\":" << static_cast<int>(probe.bus) << ',';
        std::cout << "\"address\":" << static_cast<int>(probe.address) << ',';
        std::cout << "\"port_path\":\""
                  << escape_json(format_port_path(probe.ports)) << "\",";
        std::cout << "\"label\":\"" << escape_json(probe.label) << "\",";
        std::cout << "\"product_string\":\""
                  << escape_json(probe.product_string) << "\",";
    } else {
        std::cout << "\"vendor_id\":null,\"product_id\":null,\"bus\":null,\"address\":null,"
                  << "\"port_path\":\"\",\"label\":\"\",\"product_string\":\"\",";
    }
    std::cout << "\"message\":\"" << escape_json(probe.message) << "\",";
    std::cout << "\"error\":\"" << escape_json(probe.error) << "\",";
    std::cout << "\"return_code\":" << exit_code << '}';
    std::cout << std::endl;
    return exit_code;
}

void render_human(const ProbeResult& probe) {
    std::cout << "[" << iso_timestamp() << "] ";
    if (!probe.error.empty()) {
        std::cout << "Error: " << probe.error << std::endl;
        return;
    }

    std::cout << probe.message << std::endl;
    if (probe.found) {
        std::cout << "    Vendor: " << format_hex(probe.vendor_id)
                  << "  Product: " << format_hex(probe.product_id) << std::endl;
        std::cout << "    Label: " << probe.label << std::endl;
        if (!probe.product_string.empty()) {
            std::cout << "    USB Product String: " << probe.product_string << std::endl;
        }
        std::cout << "    Bus: " << static_cast<int>(probe.bus)
                  << "  Address: " << static_cast<int>(probe.address) << std::endl;
        if (!probe.ports.empty()) {
            std::cout << "    Port Path: " << format_port_path(probe.ports) << std::endl;
        }
        if (probe.permission_denied) {
            std::cout << "    Permission: denied (udev rule required)" << std::endl;
        }
    }
}

int classify_exit_code(const ProbeResult& probe) {
    if (!probe.error.empty()) {
        return 1;
    }
    if (!probe.found) {
        return 2;
    }
    if (probe.permission_denied) {
        return 3;
    }
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    Options options;

    for (int i = 1; i < argc; ++i) {
        const std::string arg(argv[i]);
        if (arg == "--json") {
            options.json = true;
        } else if (arg == "--monitor") {
            options.monitor = true;
        } else if (arg == "--interval" && i + 1 < argc) {
            options.interval_seconds = std::max(1, std::atoi(argv[++i]));
        } else if (arg == "--no-open") {
            options.attempt_open = false;
        } else if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            std::cerr << "Unknown option: " << arg << std::endl;
            return 64;
        }
    }

    libusb_context* ctx = nullptr;
    const int init_code = libusb_init(&ctx);
    if (init_code != LIBUSB_SUCCESS) {
        ProbeResult probe;
        probe.error = std::string("libusb_init failed: ") + libusb_error_name(init_code);
        if (options.json) {
            return render_json(probe, 1);
        }
        render_human(probe);
        return 1;
    }

    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    int exit_code = 0;

    if (options.monitor) {
        while (!g_should_exit) {
            const ProbeResult probe = probe_headset(ctx, options.attempt_open);
            exit_code = classify_exit_code(probe);
            if (options.json) {
                render_json(probe, exit_code);
            } else {
                render_human(probe);
            }
            if (g_should_exit) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::seconds(options.interval_seconds));
        }
    } else {
        const ProbeResult probe = probe_headset(ctx, options.attempt_open);
        exit_code = classify_exit_code(probe);
        if (options.json) {
            render_json(probe, exit_code);
        } else {
            render_human(probe);
        }
    }

    libusb_exit(ctx);
    return exit_code;
}
