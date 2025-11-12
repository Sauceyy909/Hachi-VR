// Minimal OpenVR driver header
#pragma once
#include <stdint.h>
#include <string>

namespace vr {
    typedef uint32_t TrackedDeviceIndex_t;
    static const TrackedDeviceIndex_t k_unTrackedDeviceIndexInvalid = 0xFFFFFFFF;
    
    typedef uint64_t PropertyContainerHandle_t;
    static const PropertyContainerHandle_t k_ulInvalidPropertyContainer = 0;
    
    enum EVRInitError {
        VRInitError_None = 0,
        VRInitError_Driver_Failed = 108,
        VRInitError_Init_InterfaceNotFound = 112
    };
    
    enum ETrackedDeviceClass {
        TrackedDeviceClass_Invalid = 0,
        TrackedDeviceClass_HMD = 1
    };
    
    enum ETrackingResult {
        TrackingResult_Running_OK = 200
    };
    
    enum ETrackedDeviceProperty {
        Prop_ModelNumber_String = 1000,
        Prop_ManufacturerName_String = 1002,
        Prop_RenderModelName_String = 1003,
        Prop_TrackingSystemName_String = 1006,
        Prop_UserIpdMeters_Float = 1013,
        Prop_UserHeadToEyeDepthMeters_Float = 1014,
        Prop_DisplayFrequency_Float = 1018,
        Prop_SecondsFromVsyncToPhotons_Float = 1019,
        Prop_DisplayMCImageWidth_Int32 = 1020,
        Prop_DisplayMCImageHeight_Int32 = 1021,
        Prop_DisplayMCImageLeft_Float = 1022,
        Prop_DisplayMCImageRight_Float = 1023,
        Prop_DisplayMCImageTop_Float = 1024,
        Prop_DisplayMCImageBottom_Float = 1025,
        Prop_IsOnDesktop_Bool = 1031,
        Prop_DisplayDebugMode_Bool = 1034
    };
    
    struct HmdQuaternion_t {
        double w, x, y, z;
    };
    
    struct DriverPose_t {
        double vecPosition[3];
        HmdQuaternion_t qRotation;
        double vecVelocity[3];
        double vecAngularVelocity[3];
        ETrackingResult result;
        bool poseIsValid;
        bool deviceIsConnected;
        double poseTimeOffset;
    };
    
    class ITrackedDeviceServerDriver {
    public:
        virtual ~ITrackedDeviceServerDriver() {}
        virtual EVRInitError Activate(uint32_t unObjectId) = 0;
        virtual void Deactivate() = 0;
        virtual void EnterStandby() = 0;
        virtual void *GetComponent(const char *pchComponentNameAndVersion) = 0;
        virtual void DebugRequest(const char *pchRequest, char *pchResponseBuffer, uint32_t unResponseBufferSize) = 0;
        virtual DriverPose_t GetPose() = 0;
    };
    
    class IServerTrackedDeviceProvider {
    public:
        virtual ~IServerTrackedDeviceProvider() {}
        virtual EVRInitError Init(class IVRDriverContext *pDriverContext) = 0;
        virtual void Cleanup() = 0;
        virtual const char * const *GetInterfaceVersions() = 0;
        virtual void RunFrame() = 0;
        virtual bool ShouldBlockStandbyMode() = 0;
        virtual void EnterStandby() = 0;
        virtual void LeaveStandby() = 0;
    };
    
    class IVRDriverContext {};
    class IVRProperties {
    public:
        PropertyContainerHandle_t TrackedDeviceToPropertyContainer(TrackedDeviceIndex_t device) { return 0; }
        void SetStringProperty(PropertyContainerHandle_t, ETrackedDeviceProperty, const char*) {}
        void SetFloatProperty(PropertyContainerHandle_t, ETrackedDeviceProperty, float) {}
        void SetInt32Property(PropertyContainerHandle_t, ETrackedDeviceProperty, int32_t) {}
        void SetBoolProperty(PropertyContainerHandle_t, ETrackedDeviceProperty, bool) {}
    };
    
    class IVRServerDriverHost {
    public:
        bool TrackedDeviceAdded(const char*, ETrackedDeviceClass, ITrackedDeviceServerDriver*) { return true; }
        void TrackedDevicePoseUpdated(TrackedDeviceIndex_t, const DriverPose_t&, uint32_t) {}
    };
    
    static IVRProperties* VRProperties() { static IVRProperties p; return &p; }
    static IVRServerDriverHost* VRServerDriverHost() { static IVRServerDriverHost h; return &h; }
    
    static const char IVRDisplayComponent_Version[] = "IVRDisplayComponent_002";
    static const char IServerTrackedDeviceProvider_Version[] = "IServerTrackedDeviceProvider_005";
    static const char * const k_InterfaceVersions[] = { IServerTrackedDeviceProvider_Version, nullptr };
    
    #define VR_INIT_SERVER_DRIVER_CONTEXT(x)
    #define VR_CLEANUP_SERVER_DRIVER_CONTEXT()
}
