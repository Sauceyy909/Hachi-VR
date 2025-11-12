cmake_minimum_required(VERSION 3.10)
project(vive_cosmos_driver)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenVR
find_library(OPENVR_LIB openvr_api PATHS "${CMAKE_SOURCE_DIR}/lib/linux64")
if(NOT OPENVR_LIB)
    message(FATAL_ERROR "Could not find OpenVR library")
endif()

# Find libusb
find_package(PkgConfig REQUIRED)
pkg_check_modules(LIBUSB REQUIRED libusb-1.0)

# Source files
set(SOURCES
    cosmos_driver.cpp
    cosmos_driver.h
)

# Create shared library
add_library(driver_cosmos SHARED ${SOURCES})

# Include directories
target_include_directories(driver_cosmos PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${LIBUSB_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(driver_cosmos
    ${OPENVR_LIB}
    ${LIBUSB_LIBRARIES}
    pthread
)

# Set output directory
set_target_properties(driver_cosmos PROPERTIES
    PREFIX ""
    OUTPUT_NAME "driver_cosmos"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/linux64"
)

# Installation rules
install(TARGETS driver_cosmos
    LIBRARY DESTINATION bin/linux64
)

install(FILES
    ${CMAKE_SOURCE_DIR}/driver.vrdrivermanifest
    ${CMAKE_SOURCE_DIR}/resources.vrsettings
    DESTINATION .
)
