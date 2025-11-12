#ifndef COSMOS_DRIVER_H
#define COSMOS_DRIVER_H

#include <openvr_driver.h>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>

namespace vr {
namespace cosmos {

// Forward declarations
class CosmosHMDDevice;
class CosmosServerDriver;

/**
 * Main HMD Device Class
 * Handles the Vive Cosmos headset connection and tracking
 */
class CosmosHMDDevice : public vr::ITrackedDeviceServerDriver {
public:
    CosmosHMDDevice();
    virtual ~CosmosHMDDevice();

    // ITrackedDeviceServerDriver interface
    virtual vr::EVRInitError Activate(uint32_t unObjectId) override;
    virtual void Deactivate() override;
    virtual void EnterStandby() override;
    virtual void *GetComponent(const char *pchComponentNameAndVersion) override;
    virtual void DebugRequest(const char *pchRequest, char *pchResponseBuffer, uint32_t unResponseBufferSize) override;
    virtual vr::DriverPose_t GetPose() override;

    // Custom methods
    bool IsConnected() const { return m_bIsConnected; }
    void UpdatePose();
    void RunFrame();

private:
    // Device properties
    uint32_t m_unObjectId;
    vr::PropertyContainerHandle_t m_ulPropertyContainer;
    
    // Connection state
    std::atomic<bool> m_bIsConnected;
    std::atomic<bool> m_bIsActivated;
    
    // Tracking data
    vr::DriverPose_t m_Pose;
    std::mutex m_PoseMutex;
    
    // USB communication
    void *m_pUSBHandle;
    
    // Helper methods
    bool ConnectUSB();
    void DisconnectUSB();
    bool ReadTrackingData();
    void UpdateDeviceProperties();
};

/**
 * Server Driver Class
 * Main entry point for the driver
 */
class CosmosServerDriver : public vr::IServerTrackedDeviceProvider {
public:
    CosmosServerDriver();
    virtual ~CosmosServerDriver();

    // IServerTrackedDeviceProvider interface
    virtual vr::EVRInitError Init(vr::IVRDriverContext *pDriverContext) override;
    virtual void Cleanup() override;
    virtual const char * const *GetInterfaceVersions() override { return vr::k_InterfaceVersions; }
    virtual void RunFrame() override;
    virtual bool ShouldBlockStandbyMode() override { return false; }
    virtual void EnterStandby() override {}
    virtual void LeaveStandby() override {}

    // Custom methods
    void AddDevice(CosmosHMDDevice *pDevice);

private:
    CosmosHMDDevice *m_pHMDDevice;
    std::thread m_tUpdateThread;
    std::atomic<bool> m_bRunning;
    
    void UpdateThread();
};

// Global driver instance
extern CosmosServerDriver g_ServerDriver;

} // namespace cosmos
} // namespace vr

#endif // COSMOS_DRIVER_H
