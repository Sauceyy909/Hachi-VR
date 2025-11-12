#include "cosmos_driver.h"
#include <openvr_driver.h>
#include <cstring>
#include <cmath>
#include <chrono>
#include <libusb-1.0/libusb.h>

using namespace vr;
using namespace vr::cosmos;

// USB Vendor and Product IDs for HTC Vive Cosmos
#define COSMOS_VID 0x0bb4
#define COSMOS_PID 0x0abb

// Global driver instance
CosmosServerDriver g_ServerDriver;

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
CosmosHMDDevice::CosmosHMDDevice()
    : m_unObjectId(vr::k_unTrackedDeviceIndexInvalid)
    , m_ulPropertyContainer(vr::k_ulInvalidPropertyContainer)
    , m_bIsConnected(false)
    , m_bIsActivated(false)
    , m_pUSBHandle(nullptr)
{
    // Initialize pose to default
    m_Pose = {};
    m_Pose.poseIsValid = true;
    m_Pose.result = TrackingResult_Running_OK;
    m_Pose.deviceIsConnected = true;
    
    // Initialize position
    m_Pose.vecPosition[0] = 0.0;
    m_Pose.vecPosition[1] = 1.0;  // 1 meter off ground
    m_Pose.vecPosition[2] = 0.0;
    
    // Initialize rotation (identity quaternion)
    m_Pose.qRotation.w = 1.0;
    m_Pose.qRotation.x = 0.0;
    m_Pose.qRotation.y = 0.0;
    m_Pose.qRotation.z = 0.0;
    
    // Initialize velocity
    m_Pose.vecVelocity[0] = 0.0;
    m_Pose.vecVelocity[1] = 0.0;
    m_Pose.vecVelocity[2] = 0.0;
    
    m_Pose.vecAngularVelocity[0] = 0.0;
    m_Pose.vecAngularVelocity[1] = 0.0;
    m_Pose.vecAngularVelocity[2] = 0.0;
    
    m_Pose.poseTimeOffset = 0.0;
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
CosmosHMDDevice::~CosmosHMDDevice()
{
    DisconnectUSB();
}

//-----------------------------------------------------------------------------
// Purpose: Activate the device
//-----------------------------------------------------------------------------
vr::EVRInitError CosmosHMDDevice::Activate(uint32_t unObjectId)
{
    m_unObjectId = unObjectId;
    m_ulPropertyContainer = vr::VRProperties()->TrackedDeviceToPropertyContainer(m_unObjectId);
    
    // Set device properties
    vr::VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_ModelNumber_String, "Vive Cosmos");
    vr::VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_ManufacturerName_String, "HTC");
    vr::VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_RenderModelName_String, "{htc}vive_cosmos");
    vr::VRProperties()->SetStringProperty(m_ulPropertyContainer, Prop_TrackingSystemName_String, "cosmos_tracking");
    
    // Display properties
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_UserIpdMeters_Float, 0.063f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_UserHeadToEyeDepthMeters_Float, 0.0f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DisplayFrequency_Float, 90.0f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_SecondsFromVsyncToPhotons_Float, 0.011f);
    
    // Display resolution
    vr::VRProperties()->SetInt32Property(m_ulPropertyContainer, Prop_DisplayMCImageWidth_Int32, 1440);
    vr::VRProperties()->SetInt32Property(m_ulPropertyContainer, Prop_DisplayMCImageHeight_Int32, 1700);
    
    // Field of view
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DisplayMCImageLeft_Float, -0.5f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DisplayMCImageRight_Float, 0.5f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DisplayMCImageTop_Float, 0.5f);
    vr::VRProperties()->SetFloatProperty(m_ulPropertyContainer, Prop_DisplayMCImageBottom_Float, -0.5f);
    
    // Device specific
    vr::VRProperties()->SetBoolProperty(m_ulPropertyContainer, Prop_IsOnDesktop_Bool, false);
    vr::VRProperties()->SetBoolProperty(m_ulPropertyContainer, Prop_DisplayDebugMode_Bool, false);
    
    // Connect to USB device
    if (!ConnectUSB()) {
        return VRInitError_Driver_Failed;
    }
    
    m_bIsActivated = true;
    m_bIsConnected = true;
    
    return VRInitError_None;
}

//-----------------------------------------------------------------------------
// Purpose: Deactivate the device
//-----------------------------------------------------------------------------
void CosmosHMDDevice::Deactivate()
{
    m_bIsActivated = false;
    DisconnectUSB();
    m_unObjectId = vr::k_unTrackedDeviceIndexInvalid;
}

//-----------------------------------------------------------------------------
// Purpose: Enter standby mode
//-----------------------------------------------------------------------------
void CosmosHMDDevice::EnterStandby()
{
}

//-----------------------------------------------------------------------------
// Purpose: Get device component
//-----------------------------------------------------------------------------
void *CosmosHMDDevice::GetComponent(const char *pchComponentNameAndVersion)
{
    if (strcmp(pchComponentNameAndVersion, vr::IVRDisplayComponent_Version) == 0) {
        return nullptr;  // We don't implement IVRDisplayComponent
    }
    return nullptr;
}

//-----------------------------------------------------------------------------
// Purpose: Handle debug requests
//-----------------------------------------------------------------------------
void CosmosHMDDevice::DebugRequest(const char *pchRequest, char *pchResponseBuffer, uint32_t unResponseBufferSize)
{
    if (unResponseBufferSize >= 1) {
        pchResponseBuffer[0] = 0;
    }
}

//-----------------------------------------------------------------------------
// Purpose: Get current pose
//-----------------------------------------------------------------------------
vr::DriverPose_t CosmosHMDDevice::GetPose()
{
    std::lock_guard<std::mutex> lock(m_PoseMutex);
    return m_Pose;
}

//-----------------------------------------------------------------------------
// Purpose: Update pose with new tracking data
//-----------------------------------------------------------------------------
void CosmosHMDDevice::UpdatePose()
{
    if (!m_bIsConnected || !m_bIsActivated) {
        return;
    }
    
    // Read tracking data from USB
    if (ReadTrackingData()) {
        std::lock_guard<std::mutex> lock(m_PoseMutex);
        
        // Update pose timestamp
        m_Pose.poseTimeOffset = 0.0;
        
        // Update connection state
        m_Pose.deviceIsConnected = m_bIsConnected;
        m_Pose.poseIsValid = true;
        m_Pose.result = TrackingResult_Running_OK;
        
        // Send pose update to SteamVR
        if (m_unObjectId != vr::k_unTrackedDeviceIndexInvalid) {
            vr::VRServerDriverHost()->TrackedDevicePoseUpdated(m_unObjectId, m_Pose, sizeof(DriverPose_t));
        }
    }
}

//-----------------------------------------------------------------------------
// Purpose: Called every frame
//-----------------------------------------------------------------------------
void CosmosHMDDevice::RunFrame()
{
    UpdatePose();
}

//-----------------------------------------------------------------------------
// Purpose: Connect to USB device
//-----------------------------------------------------------------------------
bool CosmosHMDDevice::ConnectUSB()
{
    libusb_context *ctx = nullptr;
    libusb_device_handle *handle = nullptr;
    
    // Initialize libusb
    int ret = libusb_init(&ctx);
    if (ret < 0) {
        return false;
    }
    
    // Find and open the Cosmos device
    handle = libusb_open_device_with_vid_pid(ctx, COSMOS_VID, COSMOS_PID);
    if (handle == nullptr) {
        libusb_exit(ctx);
        return false;
    }
    
    // Claim interface
    ret = libusb_claim_interface(handle, 0);
    if (ret < 0) {
        libusb_close(handle);
        libusb_exit(ctx);
        return false;
    }
    
    m_pUSBHandle = handle;
    m_bIsConnected = true;
    
    return true;
}

//-----------------------------------------------------------------------------
// Purpose: Disconnect from USB device
//-----------------------------------------------------------------------------
void CosmosHMDDevice::DisconnectUSB()
{
    if (m_pUSBHandle) {
        libusb_device_handle *handle = static_cast<libusb_device_handle*>(m_pUSBHandle);
        libusb_release_interface(handle, 0);
        libusb_close(handle);
        m_pUSBHandle = nullptr;
    }
    m_bIsConnected = false;
}

//-----------------------------------------------------------------------------
// Purpose: Read tracking data from USB
//-----------------------------------------------------------------------------
bool CosmosHMDDevice::ReadTrackingData()
{
    if (!m_pUSBHandle) {
        return false;
    }
    
    // Buffer for USB data
    unsigned char data[64];
    int transferred = 0;
    
    // Read from USB endpoint
    libusb_device_handle *handle = static_cast<libusb_device_handle*>(m_pUSBHandle);
    int ret = libusb_interrupt_transfer(handle, 0x81, data, sizeof(data), &transferred, 100);
    
    if (ret == 0 && transferred > 0) {
        std::lock_guard<std::mutex> lock(m_PoseMutex);
        
        // Parse tracking data
        // This is simplified - actual Cosmos protocol would need proper parsing
        // For now, we'll just keep the pose stable
        
        // The actual implementation would parse IMU data, camera data, etc.
        // and update m_Pose accordingly
        
        return true;
    }
    
    return false;
}

//=============================================================================
// Server Driver Implementation
//=============================================================================

//-----------------------------------------------------------------------------
// Purpose: Constructor
//-----------------------------------------------------------------------------
CosmosServerDriver::CosmosServerDriver()
    : m_pHMDDevice(nullptr)
    , m_bRunning(false)
{
}

//-----------------------------------------------------------------------------
// Purpose: Destructor
//-----------------------------------------------------------------------------
CosmosServerDriver::~CosmosServerDriver()
{
    Cleanup();
}

//-----------------------------------------------------------------------------
// Purpose: Initialize the driver
//-----------------------------------------------------------------------------
vr::EVRInitError CosmosServerDriver::Init(vr::IVRDriverContext *pDriverContext)
{
    VR_INIT_SERVER_DRIVER_CONTEXT(pDriverContext);
    
    // Create HMD device
    m_pHMDDevice = new CosmosHMDDevice();
    if (!m_pHMDDevice) {
        return VRInitError_Driver_Failed;
    }
    
    // Add device to SteamVR
    vr::VRServerDriverHost()->TrackedDeviceAdded(
        "cosmos_hmd",
        vr::TrackedDeviceClass_HMD,
        m_pHMDDevice
    );
    
    // Start update thread
    m_bRunning = true;
    m_tUpdateThread = std::thread(&CosmosServerDriver::UpdateThread, this);
    
    return VRInitError_None;
}

//-----------------------------------------------------------------------------
// Purpose: Cleanup the driver
//-----------------------------------------------------------------------------
void CosmosServerDriver::Cleanup()
{
    // Stop update thread
    m_bRunning = false;
    if (m_tUpdateThread.joinable()) {
        m_tUpdateThread.join();
    }
    
    // Delete HMD device
    if (m_pHMDDevice) {
        delete m_pHMDDevice;
        m_pHMDDevice = nullptr;
    }
    
    VR_CLEANUP_SERVER_DRIVER_CONTEXT();
}

//-----------------------------------------------------------------------------
// Purpose: Called every frame by SteamVR
//-----------------------------------------------------------------------------
void CosmosServerDriver::RunFrame()
{
    if (m_pHMDDevice && m_pHMDDevice->IsConnected()) {
        m_pHMDDevice->RunFrame();
    }
}

//-----------------------------------------------------------------------------
// Purpose: Update thread for continuous tracking
//-----------------------------------------------------------------------------
void CosmosServerDriver::UpdateThread()
{
    while (m_bRunning) {
        if (m_pHMDDevice && m_pHMDDevice->IsConnected()) {
            m_pHMDDevice->UpdatePose();
        }
        
        // Run at ~90 Hz
        std::this_thread::sleep_for(std::chrono::milliseconds(11));
    }
}

//=============================================================================
// Driver Entry Points
//=============================================================================

extern "C" __attribute__((visibility("default"))) void *HmdDriverFactory(const char *pInterfaceName, int *pReturnCode)
{
    if (strcmp(vr::IServerTrackedDeviceProvider_Version, pInterfaceName) == 0) {
        return &g_ServerDriver;
    }
    
    if (pReturnCode) {
        *pReturnCode = VRInitError_Init_InterfaceNotFound;
    }
    
    return nullptr;
}
