'''
Created on Oct 4, 2015

@author: lab
'''
import os
import ctypes
from collections import OrderedDict

class PI_Enum(object):
    
    def __init__(self, name, byname_dict):
        self.name = name
        self.byname = dict(byname_dict)
        self.bysname = dict() # ShortName
        self.bynum  = dict()
        self.bynums  = dict()
        for name, num in self.byname.items():
            self.bynum[num] = name
            sname = name.split('_')[1]
            self.bysname[sname] = num
            self.bynums[num] = sname
"""
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* pil_platform.h - Princeton Instruments Library Platform Support            */
/*                                                                            */
/*  Supported Platforms:                                                      */
/*      - PIL_WIN64                                                           */
/*      - PIL_WIN32                                                           */
/*      - PIL_LIN64                                                           */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
#if !defined PIL_PLATFORM_H
#define PIL_PLATFORM_H

/******************************************************************************/
/* OS Detection                                                               */
/******************************************************************************/
#if defined _WIN64
#    define PIL_WIN64
#elif defined _WIN32
#    define PIL_WIN32
#elif defined __linux__ && defined __x86_64__
#    define PIL_LIN64
#else
#   error PI Library - Platform Not Supported
#endif

/******************************************************************************/
/* Basic Native Data Types                                                    */
/******************************************************************************/
typedef          int    piint;  /* integer native to platform                 */
typedef          double piflt;  /* floating point native to platform          */
typedef          int    pibln;  /* boolean native to platform                 */
typedef          char   pichar; /* character native to platform               */
typedef unsigned char   pibyte; /* byte native to platform                    */
#if defined __cplusplus
    typedef      bool   pibool; /* C++ boolean native to platform             */
#endif

/******************************************************************************/
/* Basic Sized Data Types                                                     */
/******************************************************************************/
#if defined PIL_WIN64
    typedef signed   char      pi8s;  /* 8-bit signed integer                 */
    typedef unsigned char      pi8u;  /* 8-bit unsigned integer               */
    typedef          short     pi16s; /* 16-bit signed integer                */
    typedef unsigned short     pi16u; /* 16-bit unsigned integer              */
    typedef          long      pi32s; /* 32-bit signed integer                */
    typedef unsigned long      pi32u; /* 32-bit unsigned integer              */
    typedef          long long pi64s; /* 64-bit signed integer                */
    typedef unsigned long long pi64u; /* 64-bit unsigned integer              */
    typedef          float     pi32f; /* 32-bit floating point                */
    typedef          double    pi64f; /* 64-bit floating point                */
#elif defined PIL_WIN32
    typedef signed   char      pi8s;  /* 8-bit signed integer                 */
    typedef unsigned char      pi8u;  /* 8-bit unsigned integer               */
    typedef          short     pi16s; /* 16-bit signed integer                */
    typedef unsigned short     pi16u; /* 16-bit unsigned integer              */
    typedef          long      pi32s; /* 32-bit signed integer                */
    typedef unsigned long      pi32u; /* 32-bit unsigned integer              */
    typedef          long long pi64s; /* 64-bit signed integer                */
    typedef unsigned long long pi64u; /* 64-bit unsigned integer              */
    typedef          float     pi32f; /* 32-bit floating point                */
    typedef          double    pi64f; /* 64-bit floating point                */
#elif defined PIL_LIN64
    typedef signed   char      pi8s;  /* 8-bit signed integer                 */
    typedef unsigned char      pi8u;  /* 8-bit unsigned integer               */
    typedef          short     pi16s; /* 16-bit signed integer                */
    typedef unsigned short     pi16u; /* 16-bit unsigned integer              */
    typedef          int       pi32s; /* 32-bit signed integer                */
    typedef unsigned int       pi32u; /* 32-bit unsigned integer              */
    typedef          long      pi64s; /* 64-bit signed integer                */
    typedef unsigned long      pi64u; /* 64-bit unsigned integer              */
    typedef          float     pi32f; /* 32-bit floating point                */
    typedef          double    pi64f; /* 64-bit floating point                */
#else
#   error PI Library - Platform Missing Sized Data Type Definition
#endif

/******************************************************************************/
/* Function Declarations                                                      */
/******************************************************************************/
#if defined PIL_WIN64
#   define PIL_EXPORT_DEF extern "C"
#   define PIL_EXPORT     __declspec(dllexport)
#   define PIL_IMPORT     __declspec(dllimport)
#   define PIL_CALL       __stdcall
#elif defined PIL_WIN32
#   define PIL_EXPORT_DEF extern "C"
#   define PIL_EXPORT     __declspec(dllexport)
#   define PIL_IMPORT     __declspec(dllimport)
#   define PIL_CALL       __stdcall
#elif defined PIL_LIN64
#   define PIL_EXPORT_DEF extern "C" __attribute__((visibility("default")))
#   define PIL_EXPORT     __attribute__((visibility("default")))
#   define PIL_IMPORT     
#   define PIL_CALL       
#else
#   error PI Library - Platform Missing Function Declaration Definition
#endif

#endif
"""

#typedef          int    piint;  /* integer native to platform                 */
piint = ctypes.c_int
#typedef          double piflt;  /* floating point native to platform          */
piflt = ctypes.c_double
#typedef          int    pibln;  /* boolean native to platform                 */
pibln = ctypes.c_int
#typedef          char   pichar; /* character native to platform               */
pichar = ctypes.c_char
#typedef unsigned char   pibyte; /* byte native to platform                    */
pibyte = ctypes.c_ubyte
#if defined __cplusplus
#    typedef      bool   pibool; /* C++ boolean native to platform             */
#endif
pibool = ctypes.c_bool

#typedef signed   char      pi8s;  /* 8-bit signed integer                 */
pi8s = ctypes.c_int8    
#typedef unsigned char      pi8u;  /* 8-bit unsigned integer               */
pi8u = ctypes.c_uint8
#typedef          short     pi16s; /* 16-bit signed integer                */
pi16s = ctypes.c_int16
#typedef unsigned short     pi16u; /* 16-bit unsigned integer              */
pi32u = ctypes.c_uint32
#typedef          long      pi32s; /* 32-bit signed integer                */
pi32s = ctypes.c_int32
#typedef unsigned long      pi32u; /* 32-bit unsigned integer              */
pi32u = ctypes.c_uint32
#typedef          long long pi64s; /* 64-bit signed integer                */
pi64s = ctypes.c_int64
#typedef unsigned long long pi64u; /* 64-bit unsigned integer              */
pi64u = ctypes.c_uint64
#typedef          float     pi32f; /* 32-bit floating point                */
pi32f = ctypes.c_float
#typedef          double    pi64f; /* 64-bit floating point                */
pi64f = ctypes.c_double

"""
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* picam.h - Princeton Instruments Camera Control API                         */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
#if !defined PICAM_H
#define PICAM_H

#include "pil_platform.h"

/******************************************************************************/
/* C++ Prologue                                                               */
/******************************************************************************/
#if defined __cplusplus && !defined PICAM_EXPORTS
    extern "C"
    {
#endif

/******************************************************************************/
/* Function Declarations                                                      */
/******************************************************************************/
#if defined PICAM_EXPORTS
#   define PICAM_FUNCTION PIL_EXPORT_DEF
#else
#   define PICAM_FUNCTION PIL_IMPORT    
#endif
#define PICAM_API PICAM_FUNCTION PicamError PIL_CALL

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* General Library Usage - Error Codes, Version, Initialization and Strings   */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/

/*----------------------------------------------------------------------------*/
/* Function Return Error Codes -----------------------------------------------*/
/*----------------------------------------------------------------------------*/
"""

"""
typedef enum PicamError
{
    /*------------------------------------------------------------------------*/
    /* Success ---------------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_None                                =  0,
    /*------------------------------------------------------------------------*/
    /* General Errors --------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_UnexpectedError                     =  4,
    PicamError_UnexpectedNullPointer               =  3,
    PicamError_InvalidPointer                      = 35,
    PicamError_InvalidCount                        = 39,
    PicamError_InvalidOperation                    = 42,
    PicamError_OperationCanceled                   = 43,
    /*------------------------------------------------------------------------*/
    /* Library Initialization Errors -----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_LibraryNotInitialized               =  1,
    PicamError_LibraryAlreadyInitialized           =  5,
    /*------------------------------------------------------------------------*/
    /* General String Handling Errors ----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_InvalidEnumeratedType               = 16,
    PicamError_EnumerationValueNotDefined          = 17,
    /*------------------------------------------------------------------------*/
    /* Plug 'n Play Discovery Errors -----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_NotDiscoveringCameras               = 18,
    PicamError_AlreadyDiscoveringCameras           = 19,
    /*------------------------------------------------------------------------*/
    /* Camera Access Errors --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_NoCamerasAvailable                  = 34,
    PicamError_CameraAlreadyOpened                 =  7,
    PicamError_InvalidCameraID                     =  8,
    PicamError_InvalidHandle                       =  9,
    PicamError_DeviceCommunicationFailed           = 15,
    PicamError_DeviceDisconnected                  = 23,
    PicamError_DeviceOpenElsewhere                 = 24,
    /*------------------------------------------------------------------------*/
    /* Demo Errors -----------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_InvalidDemoModel                    =  6,
    PicamError_InvalidDemoSerialNumber             = 21,
    PicamError_DemoAlreadyConnected                = 22,
    PicamError_DemoNotSupported                    = 40,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Access Errors ----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_ParameterHasInvalidValueType        = 11,
    PicamError_ParameterHasInvalidConstraintType   = 13,
    PicamError_ParameterDoesNotExist               = 12,
    PicamError_ParameterValueIsReadOnly            = 10,
    PicamError_InvalidParameterValue               =  2,
    PicamError_InvalidConstraintCategory           = 38,
    PicamError_ParameterValueIsIrrelevant          = 14,
    PicamError_ParameterIsNotOnlineable            = 25,
    PicamError_ParameterIsNotReadable              = 26,
    /*------------------------------------------------------------------------*/
    /* Camera Data Acquisition Errors ----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamError_InvalidParameterValues              = 28,
    PicamError_ParametersNotCommitted              = 29,
    PicamError_InvalidAcquisitionBuffer            = 30,
    PicamError_InvalidReadoutCount                 = 36,
    PicamError_InvalidReadoutTimeOut               = 37,
    PicamError_InsufficientMemory                  = 31,
    PicamError_AcquisitionInProgress               = 20,
    PicamError_AcquisitionNotInProgress            = 27,
    PicamError_TimeOutOccurred                     = 32,
    PicamError_AcquisitionUpdatedHandlerRegistered = 33,
    PicamError_InvalidAcquisitionState             = 44,
    PicamError_NondestructiveReadoutEnabled        = 41
    /*------------------------------------------------------------------------*/
} PicamError; /* (45) */
"""
PicamErrorEnum = PI_Enum(
    "PicamError", dict (
    #/*------------------------------------------------------------------------*/
    #/* Success ---------------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_None                                =  0,
    #/*------------------------------------------------------------------------*/
    #/* General Errors --------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_UnexpectedError                     =  4,
    PicamError_UnexpectedNullPointer               =  3,
    PicamError_InvalidPointer                      = 35,
    PicamError_InvalidCount                        = 39,
    PicamError_InvalidOperation                    = 42,
    PicamError_OperationCanceled                   = 43,
    #/*------------------------------------------------------------------------*/
    #/* Library Initialization Errors -----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_LibraryNotInitialized               =  1,
    PicamError_LibraryAlreadyInitialized           =  5,
    #/*------------------------------------------------------------------------*/
    #/* General String Handling Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidEnumeratedType               = 16,
    PicamError_EnumerationValueNotDefined          = 17,
    #/*------------------------------------------------------------------------*/
    #/* Plug 'n Play Discovery Errors -----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_NotDiscoveringCameras               = 18,
    PicamError_AlreadyDiscoveringCameras           = 19,
    #/*------------------------------------------------------------------------*/
    #/* Camera Access Errors --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_NoCamerasAvailable                  = 34,
    PicamError_CameraAlreadyOpened                 =  7,
    PicamError_InvalidCameraID                     =  8,
    PicamError_InvalidHandle                       =  9,
    PicamError_DeviceCommunicationFailed           = 15,
    PicamError_DeviceDisconnected                  = 23,
    PicamError_DeviceOpenElsewhere                 = 24,
    #/*------------------------------------------------------------------------*/
    #/* Demo Errors -----------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidDemoModel                    =  6,
    PicamError_InvalidDemoSerialNumber             = 21,
    PicamError_DemoAlreadyConnected                = 22,
    PicamError_DemoNotSupported                    = 40,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Access Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_ParameterHasInvalidValueType        = 11,
    PicamError_ParameterHasInvalidConstraintType   = 13,
    PicamError_ParameterDoesNotExist               = 12,
    PicamError_ParameterValueIsReadOnly            = 10,
    PicamError_InvalidParameterValue               =  2,
    PicamError_InvalidConstraintCategory           = 38,
    PicamError_ParameterValueIsIrrelevant          = 14,
    PicamError_ParameterIsNotOnlineable            = 25,
    PicamError_ParameterIsNotReadable              = 26,
    #/*------------------------------------------------------------------------*/
    #/* Camera Data Acquisition Errors ----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamError_InvalidParameterValues              = 28,
    PicamError_ParametersNotCommitted              = 29,
    PicamError_InvalidAcquisitionBuffer            = 30,
    PicamError_InvalidReadoutCount                 = 36,
    PicamError_InvalidReadoutTimeOut               = 37,
    PicamError_InsufficientMemory                  = 31,
    PicamError_AcquisitionInProgress               = 20,
    PicamError_AcquisitionNotInProgress            = 27,
    PicamError_TimeOutOccurred                     = 32,
    PicamError_AcquisitionUpdatedHandlerRegistered = 33,
    PicamError_InvalidAcquisitionState             = 44,
    PicamError_NondestructiveReadoutEnabled        = 41                   
    )
)
"""
/*----------------------------------------------------------------------------*/
/* Library Version -----------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetVersion(
    piint* major,
    piint* minor,
    piint* distribution,
    piint* released );
/*----------------------------------------------------------------------------*/
/* Library Initialization ----------------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsLibraryInitialized( pibln* inited );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_InitializeLibrary( void );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_UninitializeLibrary( void );
/*----------------------------------------------------------------------------*/
/* General String Handling ---------------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyString( const pichar* s );
/*----------------------------------------------------------------------------*/
typedef enum PicamEnumeratedType
{
    /*------------------------------------------------------------------------*/
    /* Function Return Error Codes -------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_Error                      =  1,
    /*------------------------------------------------------------------------*/
    /* General String Handling -----------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_EnumeratedType             = 29,
    /*------------------------------------------------------------------------*/
    /* Camera Identification -------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_Model                      =  2,
    PicamEnumeratedType_ComputerInterface          =  3,
    /*------------------------------------------------------------------------*/
    /* Camera Plug 'n Play Discovery -----------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_DiscoveryAction            = 26,
    /*------------------------------------------------------------------------*/
    /* Camera Access ---------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_HandleType                 = 27,
    /*------------------------------------------------------------------------*/
    /* Camera Parameters -----------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueType                  =  4,
    PicamEnumeratedType_ConstraintType             =  5,
    PicamEnumeratedType_Parameter                  =  6,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Values - Enumerated Types ----------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_AdcAnalogGain              =  7,
    PicamEnumeratedType_AdcQuality                 =  8,
    PicamEnumeratedType_CcdCharacteristicsMask     =  9,
    PicamEnumeratedType_GateTrackingMask           = 36,
    PicamEnumeratedType_GatingMode                 = 34,
    PicamEnumeratedType_GatingSpeed                = 38,
    PicamEnumeratedType_EMIccdGainControlMode      = 42,
    PicamEnumeratedType_IntensifierOptionsMask     = 35,
    PicamEnumeratedType_IntensifierStatus          = 33,
    PicamEnumeratedType_ModulationTrackingMask     = 41,
    PicamEnumeratedType_OrientationMask            = 10,
    PicamEnumeratedType_OutputSignal               = 11,
    PicamEnumeratedType_PhosphorType               = 39,
    PicamEnumeratedType_PhotocathodeSensitivity    = 40,
    PicamEnumeratedType_PhotonDetectionMode        = 43,
    PicamEnumeratedType_PixelFormat                = 12,
    PicamEnumeratedType_ReadoutControlMode         = 13,
    PicamEnumeratedType_SensorTemperatureStatus    = 14,
    PicamEnumeratedType_SensorType                 = 15,
    PicamEnumeratedType_ShutterTimingMode          = 16,
    PicamEnumeratedType_TimeStampsMask             = 17,
    PicamEnumeratedType_TriggerCoupling            = 30,
    PicamEnumeratedType_TriggerDetermination       = 18,
    PicamEnumeratedType_TriggerResponse            = 19,
    PicamEnumeratedType_TriggerSource              = 31,
    PicamEnumeratedType_TriggerTermination         = 32,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Information - Value Access ---------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueAccess                = 20,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Information - Dynamics -------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_DynamicsMask               = 28,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Constraints - Enumerated Types -----------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_ConstraintScope            = 21,
    PicamEnumeratedType_ConstraintSeverity         = 22,
    PicamEnumeratedType_ConstraintCategory         = 23,
    /*------------------------------------------------------------------------*/
    /* Camera Parameter Constraints - Regions Of Interest --------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_RoisConstraintRulesMask    = 24,
    /*------------------------------------------------------------------------*/
    /* Acquisition Control ---------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionErrorsMask      = 25,
    /*------------------------------------------------------------------------*/
    /* Acquisition Notification ----------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionState           = 37,
    PicamEnumeratedType_AcquisitionStateErrorsMask = 44
    /*------------------------------------------------------------------------*/
} PicamEnumeratedType; /* (45) */
"""
PicamEnumeratedTypeEnum = PI_Enum(
    "PicamEnumeratedType", dict(
    #/*------------------------------------------------------------------------*/
    #/* Function Return Error Codes -------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_Error                      =  1,
    #/*------------------------------------------------------------------------*/
    #/* General String Handling -----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_EnumeratedType             = 29,
    #/*------------------------------------------------------------------------*/
    #/* Camera Identification -------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_Model                      =  2,
    PicamEnumeratedType_ComputerInterface          =  3,
    #/*------------------------------------------------------------------------*/
    #/* Camera Plug 'n Play Discovery -----------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_DiscoveryAction            = 26,
    #/*------------------------------------------------------------------------*/
    #/* Camera Access ---------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_HandleType                 = 27,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameters -----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueType                  =  4,
    PicamEnumeratedType_ConstraintType             =  5,
    PicamEnumeratedType_Parameter                  =  6,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Values - Enumerated Types ----------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_AdcAnalogGain              =  7,
    PicamEnumeratedType_AdcQuality                 =  8,
    PicamEnumeratedType_CcdCharacteristicsMask     =  9,
    PicamEnumeratedType_GateTrackingMask           = 36,
    PicamEnumeratedType_GatingMode                 = 34,
    PicamEnumeratedType_GatingSpeed                = 38,
    PicamEnumeratedType_EMIccdGainControlMode      = 42,
    PicamEnumeratedType_IntensifierOptionsMask     = 35,
    PicamEnumeratedType_IntensifierStatus          = 33,
    PicamEnumeratedType_ModulationTrackingMask     = 41,
    PicamEnumeratedType_OrientationMask            = 10,
    PicamEnumeratedType_OutputSignal               = 11,
    PicamEnumeratedType_PhosphorType               = 39,
    PicamEnumeratedType_PhotocathodeSensitivity    = 40,
    PicamEnumeratedType_PhotonDetectionMode        = 43,
    PicamEnumeratedType_PixelFormat                = 12,
    PicamEnumeratedType_ReadoutControlMode         = 13,
    PicamEnumeratedType_SensorTemperatureStatus    = 14,
    PicamEnumeratedType_SensorType                 = 15,
    PicamEnumeratedType_ShutterTimingMode          = 16,
    PicamEnumeratedType_TimeStampsMask             = 17,
    PicamEnumeratedType_TriggerCoupling            = 30,
    PicamEnumeratedType_TriggerDetermination       = 18,
    PicamEnumeratedType_TriggerResponse            = 19,
    PicamEnumeratedType_TriggerSource              = 31,
    PicamEnumeratedType_TriggerTermination         = 32,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Information - Value Access ---------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ValueAccess                = 20,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Information - Dynamics -------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_DynamicsMask               = 28,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Constraints - Enumerated Types -----------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_ConstraintScope            = 21,
    PicamEnumeratedType_ConstraintSeverity         = 22,
    PicamEnumeratedType_ConstraintCategory         = 23,
    #/*------------------------------------------------------------------------*/
    #/* Camera Parameter Constraints - Regions Of Interest --------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_RoisConstraintRulesMask    = 24,
    #/*------------------------------------------------------------------------*/
    #/* Acquisition Control ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionErrorsMask      = 25,
    #/*------------------------------------------------------------------------*/
    #/* Acquisition Notification ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamEnumeratedType_AcquisitionState           = 37,
    PicamEnumeratedType_AcquisitionStateErrorsMask = 44
    #/*------------------------------------------------------------------------*/
    ))
"""
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetEnumerationString(
    PicamEnumeratedType type,
    piint               value,
    const pichar**      s ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera Identification, Access, Information and Demo                        */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/

/*----------------------------------------------------------------------------*/
/* Camera Identification -----------------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamModel
{
    /*------------------------------------------------------------------------*/
    /* PI-MTE Series (1419) --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PIMteSeries              = 1400,
    /* PI-MTE 1024 Series ----------------------------------------------------*/
    PicamModel_PIMte1024Series          = 1401,
    PicamModel_PIMte1024F               = 1402,
    PicamModel_PIMte1024B               = 1403,
    PicamModel_PIMte1024BR              = 1405,
    PicamModel_PIMte1024BUV             = 1404,
    /* PI-MTE 1024FT Series --------------------------------------------------*/
    PicamModel_PIMte1024FTSeries        = 1406,
    PicamModel_PIMte1024FT              = 1407,
    PicamModel_PIMte1024BFT             = 1408,
    /* PI-MTE 1300 Series ----------------------------------------------------*/
    PicamModel_PIMte1300Series          = 1412,
    PicamModel_PIMte1300B               = 1413,
    PicamModel_PIMte1300R               = 1414,
    PicamModel_PIMte1300BR              = 1415,
    /* PI-MTE 2048 Series ----------------------------------------------------*/
    PicamModel_PIMte2048Series          = 1416,
    PicamModel_PIMte2048B               = 1417,
    PicamModel_PIMte2048BR              = 1418,
    /* PI-MTE 2K Series ------------------------------------------------------*/
    PicamModel_PIMte2KSeries            = 1409,
    PicamModel_PIMte2KB                 = 1410,
    PicamModel_PIMte2KBUV               = 1411,
    /*------------------------------------------------------------------------*/
    /* PIXIS Series (76) -----------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PixisSeries              =    0,
    /* PIXIS 100 Series ------------------------------------------------------*/
    PicamModel_Pixis100Series           =    1,
    PicamModel_Pixis100F                =    2,
    PicamModel_Pixis100B                =    6,
    PicamModel_Pixis100R                =    3,
    PicamModel_Pixis100C                =    4,
    PicamModel_Pixis100BR               =    5,
    PicamModel_Pixis100BExcelon         =   54,
    PicamModel_Pixis100BRExcelon        =   55,
    PicamModel_PixisXO100B              =    7,
    PicamModel_PixisXO100BR             =    8,
    PicamModel_PixisXB100B              =   68,
    PicamModel_PixisXB100BR             =   69,
    /* PIXIS 256 Series ------------------------------------------------------*/
    PicamModel_Pixis256Series           =   26,
    PicamModel_Pixis256F                =   27,
    PicamModel_Pixis256B                =   29,
    PicamModel_Pixis256E                =   28,
    PicamModel_Pixis256BR               =   30,
    PicamModel_PixisXB256BR             =   31,
    /* PIXIS 400 Series ------------------------------------------------------*/
    PicamModel_Pixis400Series           =   37,
    PicamModel_Pixis400F                =   38,
    PicamModel_Pixis400B                =   40,
    PicamModel_Pixis400R                =   39,
    PicamModel_Pixis400BR               =   41,
    PicamModel_Pixis400BExcelon         =   56,
    PicamModel_Pixis400BRExcelon        =   57,
    PicamModel_PixisXO400B              =   42,
    PicamModel_PixisXB400BR             =   70,
    /* PIXIS 512 Series ------------------------------------------------------*/
    PicamModel_Pixis512Series           =   43,
    PicamModel_Pixis512F                =   44,
    PicamModel_Pixis512B                =   45,
    PicamModel_Pixis512BUV              =   46,
    PicamModel_Pixis512BExcelon         =   58,
    PicamModel_PixisXO512F              =   49,
    PicamModel_PixisXO512B              =   50,
    PicamModel_PixisXF512F              =   48,
    PicamModel_PixisXF512B              =   47,
    /* PIXIS 1024 Series -----------------------------------------------------*/
    PicamModel_Pixis1024Series          =    9,
    PicamModel_Pixis1024F               =   10,
    PicamModel_Pixis1024B               =   11,
    PicamModel_Pixis1024BR              =   13,
    PicamModel_Pixis1024BUV             =   12,
    PicamModel_Pixis1024BExcelon        =   59,
    PicamModel_Pixis1024BRExcelon       =   60,
    PicamModel_PixisXO1024F             =   16,
    PicamModel_PixisXO1024B             =   14,
    PicamModel_PixisXO1024BR            =   15,
    PicamModel_PixisXF1024F             =   17,
    PicamModel_PixisXF1024B             =   18,
    PicamModel_PixisXB1024BR            =   71,
    /* PIXIS 1300 Series -----------------------------------------------------*/
    PicamModel_Pixis1300Series          =   51,
    PicamModel_Pixis1300F               =   52,
    PicamModel_Pixis1300F_2             =   75,
    PicamModel_Pixis1300B               =   53,
    PicamModel_Pixis1300BR              =   73,
    PicamModel_Pixis1300BExcelon        =   61,
    PicamModel_Pixis1300BRExcelon       =   62,
    PicamModel_PixisXO1300B             =   65,
    PicamModel_PixisXF1300B             =   66,
    PicamModel_PixisXB1300R             =   72,
    /* PIXIS 2048 Series -----------------------------------------------------*/
    PicamModel_Pixis2048Series          =   20,
    PicamModel_Pixis2048F               =   21,
    PicamModel_Pixis2048B               =   22,
    PicamModel_Pixis2048BR              =   67,
    PicamModel_Pixis2048BExcelon        =   63,
    PicamModel_Pixis2048BRExcelon       =   74,
    PicamModel_PixisXO2048B             =   23,
    PicamModel_PixisXF2048F             =   25,
    PicamModel_PixisXF2048B             =   24,
    /* PIXIS 2K Series -------------------------------------------------------*/
    PicamModel_Pixis2KSeries            =   32,
    PicamModel_Pixis2KF                 =   33,
    PicamModel_Pixis2KB                 =   34,
    PicamModel_Pixis2KBUV               =   36,
    PicamModel_Pixis2KBExcelon          =   64,
    PicamModel_PixisXO2KB               =   35,
    /*------------------------------------------------------------------------*/
    /* Quad-RO Series (104) --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_QuadroSeries             =  100,
    PicamModel_Quadro4096               =  101,
    PicamModel_Quadro4096_2             =  103,
    PicamModel_Quadro4320               =  102,
    /*------------------------------------------------------------------------*/
    /* ProEM Series (214) ----------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_ProEMSeries              =  200,
    /* ProEM 512 Series ------------------------------------------------------*/
    PicamModel_ProEM512Series           =  203,
    PicamModel_ProEM512B                =  201,
    PicamModel_ProEM512BK               =  205,
    PicamModel_ProEM512BExcelon         =  204,
    PicamModel_ProEM512BKExcelon        =  206,
    /* ProEM 1024 Series -----------------------------------------------------*/
    PicamModel_ProEM1024Series          =  207,
    PicamModel_ProEM1024B               =  202,
    PicamModel_ProEM1024BExcelon        =  208,
    /* ProEM 1600 Series -----------------------------------------------------*/
    PicamModel_ProEM1600Series          =  209,
    PicamModel_ProEM1600xx2B            =  212,
    PicamModel_ProEM1600xx2BExcelon     =  210,
    PicamModel_ProEM1600xx4B            =  213,
    PicamModel_ProEM1600xx4BExcelon     =  211,
    /*------------------------------------------------------------------------*/
    /* ProEM+ Series (614) ---------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_ProEMPlusSeries          =  600,
    /* ProEM+ 512 Series -----------------------------------------------------*/
    PicamModel_ProEMPlus512Series       =  603,
    PicamModel_ProEMPlus512B            =  601,
    PicamModel_ProEMPlus512BK           =  605,
    PicamModel_ProEMPlus512BExcelon     =  604,
    PicamModel_ProEMPlus512BKExcelon    =  606,
    /* ProEM+ 1024 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1024Series      =  607,
    PicamModel_ProEMPlus1024B           =  602,
    PicamModel_ProEMPlus1024BExcelon    =  608,
    /* ProEM+ 1600 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1600Series      =  609,
    PicamModel_ProEMPlus1600xx2B        =  612,
    PicamModel_ProEMPlus1600xx2BExcelon =  610,
    PicamModel_ProEMPlus1600xx4B        =  613,
    PicamModel_ProEMPlus1600xx4BExcelon =  611,
    /*------------------------------------------------------------------------*/
    /* ProEM-HS Series (1209) ------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_ProEMHSSeries            = 1200,
    /* ProEM-HS 512 Series ---------------------------------------------------*/
    PicamModel_ProEMHS512Series         = 1201,
    PicamModel_ProEMHS512B              = 1202,
    PicamModel_ProEMHS512BK             = 1207,
    PicamModel_ProEMHS512BExcelon       = 1203,
    PicamModel_ProEMHS512BKExcelon      = 1208,
    /* ProEM-HS 1024 Series --------------------------------------------------*/
    PicamModel_ProEMHS1024Series        = 1204,
    PicamModel_ProEMHS1024B             = 1205,
    PicamModel_ProEMHS1024BExcelon      = 1206,
    /*------------------------------------------------------------------------*/
    /* PI-MAX3 Series (303) --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PIMax3Series             =  300,
    PicamModel_PIMax31024I              =  301,
    PicamModel_PIMax31024x256           =  302,
    /*------------------------------------------------------------------------*/
    /* PI-MAX4 Series (721) --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PIMax4Series             =  700,
    /* PI-MAX4 1024i Series --------------------------------------------------*/
    PicamModel_PIMax41024ISeries        =  703,
    PicamModel_PIMax41024I              =  701,
    PicamModel_PIMax41024IRF            =  704,
    /* PI-MAX4 1024f Series --------------------------------------------------*/
    PicamModel_PIMax41024FSeries        =  710,
    PicamModel_PIMax41024F              =  711,
    PicamModel_PIMax41024FRF            =  712,
    /* PI-MAX4 1024x256 Series -----------------------------------------------*/
    PicamModel_PIMax41024x256Series     =  705,
    PicamModel_PIMax41024x256           =  702,
    PicamModel_PIMax41024x256RF         =  706,
    /* PI-MAX4 2048 Series ---------------------------------------------------*/
    PicamModel_PIMax42048Series         =  716,
    PicamModel_PIMax42048F              =  717,
    PicamModel_PIMax42048B              =  718,
    PicamModel_PIMax42048FRF            =  719,
    PicamModel_PIMax42048BRF            =  720,
    /* PI-MAX4 512EM Series --------------------------------------------------*/
    PicamModel_PIMax4512EMSeries        =  708,
    PicamModel_PIMax4512EM              =  707,
    PicamModel_PIMax4512BEM             =  709,
    /* PI-MAX4 1024EM Series -------------------------------------------------*/
    PicamModel_PIMax41024EMSeries       =  713,
    PicamModel_PIMax41024EM             =  715,
    PicamModel_PIMax41024BEM            =  714,
    /*------------------------------------------------------------------------*/
    /* PyLoN Series (439) ----------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PylonSeries              =  400,
    /* PyLoN 100 Series ------------------------------------------------------*/
    PicamModel_Pylon100Series           =  418,
    PicamModel_Pylon100F                =  404,
    PicamModel_Pylon100B                =  401,
    PicamModel_Pylon100BR               =  407,
    PicamModel_Pylon100BExcelon         =  425,
    PicamModel_Pylon100BRExcelon        =  426,
    /* PyLoN 256 Series ------------------------------------------------------*/
    PicamModel_Pylon256Series           =  419,
    PicamModel_Pylon256F                =  409,
    PicamModel_Pylon256B                =  410,
    PicamModel_Pylon256E                =  411,
    PicamModel_Pylon256BR               =  412,
    /* PyLoN 400 Series ------------------------------------------------------*/
    PicamModel_Pylon400Series           =  420,
    PicamModel_Pylon400F                =  405,
    PicamModel_Pylon400B                =  402,
    PicamModel_Pylon400BR               =  408,
    PicamModel_Pylon400BExcelon         =  427,
    PicamModel_Pylon400BRExcelon        =  428,
    /* PyLoN 1024 Series -----------------------------------------------------*/
    PicamModel_Pylon1024Series          =  421,
    PicamModel_Pylon1024B               =  417,
    PicamModel_Pylon1024BExcelon        =  429,
    /* PyLoN 1300 Series -----------------------------------------------------*/
    PicamModel_Pylon1300Series          =  422,
    PicamModel_Pylon1300F               =  406,
    PicamModel_Pylon1300B               =  403,
    PicamModel_Pylon1300R               =  438,
    PicamModel_Pylon1300BR              =  432,
    PicamModel_Pylon1300BExcelon        =  430,
    PicamModel_Pylon1300BRExcelon       =  433,
    /* PyLoN 2048 Series -----------------------------------------------------*/
    PicamModel_Pylon2048Series          =  423,
    PicamModel_Pylon2048F               =  415,
    PicamModel_Pylon2048B               =  434,
    PicamModel_Pylon2048BR              =  416,
    PicamModel_Pylon2048BExcelon        =  435,
    PicamModel_Pylon2048BRExcelon       =  436,
    /* PyLoN 2K Series -------------------------------------------------------*/
    PicamModel_Pylon2KSeries            =  424,
    PicamModel_Pylon2KF                 =  413,
    PicamModel_Pylon2KB                 =  414,
    PicamModel_Pylon2KBUV               =  437,
    PicamModel_Pylon2KBExcelon          =  431,
    /*------------------------------------------------------------------------*/
    /* PyLoN-IR Series (904) -------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PylonirSeries            =  900,
    /* PyLoN-IR 1024 Series --------------------------------------------------*/
    PicamModel_Pylonir1024Series        =  901,
    PicamModel_Pylonir102422            =  902,
    PicamModel_Pylonir102417            =  903,
    /*------------------------------------------------------------------------*/
    /* PIoNIR Series (502) ---------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_PionirSeries             =  500,
    PicamModel_Pionir640                =  501,
    /*------------------------------------------------------------------------*/
    /* NIRvana Series (802) --------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_NirvanaSeries            =  800,
    PicamModel_Nirvana640               =  801,
    /*------------------------------------------------------------------------*/
    /* NIRvana ST Series (1302) ----------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_NirvanaSTSeries          = 1300,
    PicamModel_NirvanaST640             = 1301,
    /*------------------------------------------------------------------------*/
    /* NIRvana-LN Series (1102) ----------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamModel_NirvanaLNSeries          = 1100,
    PicamModel_NirvanaLN640             = 1101
    /*------------------------------------------------------------------------*/
} PicamModel;
"""
PicamModelEnum = PI_Enum(
    "PicamModelEnum", dict(
    #/*------------------------------------------------------------------------*/
    #/* PI-MTE Series (1419) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMteSeries              = 1400,
    #/* PI-MTE 1024 Series ----------------------------------------------------*/
    PicamModel_PIMte1024Series          = 1401,
    PicamModel_PIMte1024F               = 1402,
    PicamModel_PIMte1024B               = 1403,
    PicamModel_PIMte1024BR              = 1405,
    PicamModel_PIMte1024BUV             = 1404,
    #/* PI-MTE 1024FT Series --------------------------------------------------*/
    PicamModel_PIMte1024FTSeries        = 1406,
    PicamModel_PIMte1024FT              = 1407,
    PicamModel_PIMte1024BFT             = 1408,
    #/* PI-MTE 1300 Series ----------------------------------------------------*/
    PicamModel_PIMte1300Series          = 1412,
    PicamModel_PIMte1300B               = 1413,
    PicamModel_PIMte1300R               = 1414,
    PicamModel_PIMte1300BR              = 1415,
    #/* PI-MTE 2048 Series ----------------------------------------------------*/
    PicamModel_PIMte2048Series          = 1416,
    PicamModel_PIMte2048B               = 1417,
    PicamModel_PIMte2048BR              = 1418,
    #/* PI-MTE 2K Series ------------------------------------------------------*/
    PicamModel_PIMte2KSeries            = 1409,
    PicamModel_PIMte2KB                 = 1410,
    PicamModel_PIMte2KBUV               = 1411,
    #/*------------------------------------------------------------------------*/
    #/* PIXIS Series (76) -----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PixisSeries              =    0,
    #/* PIXIS 100 Series ------------------------------------------------------*/
    PicamModel_Pixis100Series           =    1,
    PicamModel_Pixis100F                =    2,
    PicamModel_Pixis100B                =    6,
    PicamModel_Pixis100R                =    3,
    PicamModel_Pixis100C                =    4,
    PicamModel_Pixis100BR               =    5,
    PicamModel_Pixis100BExcelon         =   54,
    PicamModel_Pixis100BRExcelon        =   55,
    PicamModel_PixisXO100B              =    7,
    PicamModel_PixisXO100BR             =    8,
    PicamModel_PixisXB100B              =   68,
    PicamModel_PixisXB100BR             =   69,
    #/* PIXIS 256 Series ------------------------------------------------------*/
    PicamModel_Pixis256Series           =   26,
    PicamModel_Pixis256F                =   27,
    PicamModel_Pixis256B                =   29,
    PicamModel_Pixis256E                =   28,
    PicamModel_Pixis256BR               =   30,
    PicamModel_PixisXB256BR             =   31,
    #/* PIXIS 400 Series ------------------------------------------------------*/
    PicamModel_Pixis400Series           =   37,
    PicamModel_Pixis400F                =   38,
    PicamModel_Pixis400B                =   40,
    PicamModel_Pixis400R                =   39,
    PicamModel_Pixis400BR               =   41,
    PicamModel_Pixis400BExcelon         =   56,
    PicamModel_Pixis400BRExcelon        =   57,
    PicamModel_PixisXO400B              =   42,
    PicamModel_PixisXB400BR             =   70,
    #/* PIXIS 512 Series ------------------------------------------------------*/
    PicamModel_Pixis512Series           =   43,
    PicamModel_Pixis512F                =   44,
    PicamModel_Pixis512B                =   45,
    PicamModel_Pixis512BUV              =   46,
    PicamModel_Pixis512BExcelon         =   58,
    PicamModel_PixisXO512F              =   49,
    PicamModel_PixisXO512B              =   50,
    PicamModel_PixisXF512F              =   48,
    PicamModel_PixisXF512B              =   47,
    #/* PIXIS 1024 Series -----------------------------------------------------*/
    PicamModel_Pixis1024Series          =    9,
    PicamModel_Pixis1024F               =   10,
    PicamModel_Pixis1024B               =   11,
    PicamModel_Pixis1024BR              =   13,
    PicamModel_Pixis1024BUV             =   12,
    PicamModel_Pixis1024BExcelon        =   59,
    PicamModel_Pixis1024BRExcelon       =   60,
    PicamModel_PixisXO1024F             =   16,
    PicamModel_PixisXO1024B             =   14,
    PicamModel_PixisXO1024BR            =   15,
    PicamModel_PixisXF1024F             =   17,
    PicamModel_PixisXF1024B             =   18,
    PicamModel_PixisXB1024BR            =   71,
    #/* PIXIS 1300 Series -----------------------------------------------------*/
    PicamModel_Pixis1300Series          =   51,
    PicamModel_Pixis1300F               =   52,
    PicamModel_Pixis1300F_2             =   75,
    PicamModel_Pixis1300B               =   53,
    PicamModel_Pixis1300BR              =   73,
    PicamModel_Pixis1300BExcelon        =   61,
    PicamModel_Pixis1300BRExcelon       =   62,
    PicamModel_PixisXO1300B             =   65,
    PicamModel_PixisXF1300B             =   66,
    PicamModel_PixisXB1300R             =   72,
    #/* PIXIS 2048 Series -----------------------------------------------------*/
    PicamModel_Pixis2048Series          =   20,
    PicamModel_Pixis2048F               =   21,
    PicamModel_Pixis2048B               =   22,
    PicamModel_Pixis2048BR              =   67,
    PicamModel_Pixis2048BExcelon        =   63,
    PicamModel_Pixis2048BRExcelon       =   74,
    PicamModel_PixisXO2048B             =   23,
    PicamModel_PixisXF2048F             =   25,
    PicamModel_PixisXF2048B             =   24,
    #/* PIXIS 2K Series -------------------------------------------------------*/
    PicamModel_Pixis2KSeries            =   32,
    PicamModel_Pixis2KF                 =   33,
    PicamModel_Pixis2KB                 =   34,
    PicamModel_Pixis2KBUV               =   36,
    PicamModel_Pixis2KBExcelon          =   64,
    PicamModel_PixisXO2KB               =   35,
    #/*------------------------------------------------------------------------*/
    #/* Quad-RO Series (104) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_QuadroSeries             =  100,
    PicamModel_Quadro4096               =  101,
    PicamModel_Quadro4096_2             =  103,
    PicamModel_Quadro4320               =  102,
    #/*------------------------------------------------------------------------*/
    #/* ProEM Series (214) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMSeries              =  200,
    #/* ProEM 512 Series ------------------------------------------------------*/
    PicamModel_ProEM512Series           =  203,
    PicamModel_ProEM512B                =  201,
    PicamModel_ProEM512BK               =  205,
    PicamModel_ProEM512BExcelon         =  204,
    PicamModel_ProEM512BKExcelon        =  206,
    #/* ProEM 1024 Series -----------------------------------------------------*/
    PicamModel_ProEM1024Series          =  207,
    PicamModel_ProEM1024B               =  202,
    PicamModel_ProEM1024BExcelon        =  208,
    #/* ProEM 1600 Series -----------------------------------------------------*/
    PicamModel_ProEM1600Series          =  209,
    PicamModel_ProEM1600xx2B            =  212,
    PicamModel_ProEM1600xx2BExcelon     =  210,
    PicamModel_ProEM1600xx4B            =  213,
    PicamModel_ProEM1600xx4BExcelon     =  211,
    #/*------------------------------------------------------------------------*/
    #/* ProEM+ Series (614) ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMPlusSeries          =  600,
    #/* ProEM+ 512 Series -----------------------------------------------------*/
    PicamModel_ProEMPlus512Series       =  603,
    PicamModel_ProEMPlus512B            =  601,
    PicamModel_ProEMPlus512BK           =  605,
    PicamModel_ProEMPlus512BExcelon     =  604,
    PicamModel_ProEMPlus512BKExcelon    =  606,
    #/* ProEM+ 1024 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1024Series      =  607,
    PicamModel_ProEMPlus1024B           =  602,
    PicamModel_ProEMPlus1024BExcelon    =  608,
    #/* ProEM+ 1600 Series ----------------------------------------------------*/
    PicamModel_ProEMPlus1600Series      =  609,
    PicamModel_ProEMPlus1600xx2B        =  612,
    PicamModel_ProEMPlus1600xx2BExcelon =  610,
    PicamModel_ProEMPlus1600xx4B        =  613,
    PicamModel_ProEMPlus1600xx4BExcelon =  611,
    #/*------------------------------------------------------------------------*/
    #/* ProEM-HS Series (1209) ------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_ProEMHSSeries            = 1200,
    #/* ProEM-HS 512 Series ---------------------------------------------------*/
    PicamModel_ProEMHS512Series         = 1201,
    PicamModel_ProEMHS512B              = 1202,
    PicamModel_ProEMHS512BK             = 1207,
    PicamModel_ProEMHS512BExcelon       = 1203,
    PicamModel_ProEMHS512BKExcelon      = 1208,
    #/* ProEM-HS 1024 Series --------------------------------------------------*/
    PicamModel_ProEMHS1024Series        = 1204,
    PicamModel_ProEMHS1024B             = 1205,
    PicamModel_ProEMHS1024BExcelon      = 1206,
    #/*------------------------------------------------------------------------*/
    #/* PI-MAX3 Series (303) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMax3Series             =  300,
    PicamModel_PIMax31024I              =  301,
    PicamModel_PIMax31024x256           =  302,
    #/*------------------------------------------------------------------------*/
    #/* PI-MAX4 Series (721) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PIMax4Series             =  700,
    #/* PI-MAX4 1024i Series --------------------------------------------------*/
    PicamModel_PIMax41024ISeries        =  703,
    PicamModel_PIMax41024I              =  701,
    PicamModel_PIMax41024IRF            =  704,
    #/* PI-MAX4 1024f Series --------------------------------------------------*/
    PicamModel_PIMax41024FSeries        =  710,
    PicamModel_PIMax41024F              =  711,
    PicamModel_PIMax41024FRF            =  712,
    #/* PI-MAX4 1024x256 Series -----------------------------------------------*/
    PicamModel_PIMax41024x256Series     =  705,
    PicamModel_PIMax41024x256           =  702,
    PicamModel_PIMax41024x256RF         =  706,
    #/* PI-MAX4 2048 Series ---------------------------------------------------*/
    PicamModel_PIMax42048Series         =  716,
    PicamModel_PIMax42048F              =  717,
    PicamModel_PIMax42048B              =  718,
    PicamModel_PIMax42048FRF            =  719,
    PicamModel_PIMax42048BRF            =  720,
    #/* PI-MAX4 512EM Series --------------------------------------------------*/
    PicamModel_PIMax4512EMSeries        =  708,
    PicamModel_PIMax4512EM              =  707,
    PicamModel_PIMax4512BEM             =  709,
    #/* PI-MAX4 1024EM Series -------------------------------------------------*/
    PicamModel_PIMax41024EMSeries       =  713,
    PicamModel_PIMax41024EM             =  715,
    PicamModel_PIMax41024BEM            =  714,
    #/*------------------------------------------------------------------------*/
    #/* PyLoN Series (439) ----------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PylonSeries              =  400,
    #/* PyLoN 100 Series ------------------------------------------------------*/
    PicamModel_Pylon100Series           =  418,
    PicamModel_Pylon100F                =  404,
    PicamModel_Pylon100B                =  401,
    PicamModel_Pylon100BR               =  407,
    PicamModel_Pylon100BExcelon         =  425,
    PicamModel_Pylon100BRExcelon        =  426,
    #/* PyLoN 256 Series ------------------------------------------------------*/
    PicamModel_Pylon256Series           =  419,
    PicamModel_Pylon256F                =  409,
    PicamModel_Pylon256B                =  410,
    PicamModel_Pylon256E                =  411,
    PicamModel_Pylon256BR               =  412,
    #/* PyLoN 400 Series ------------------------------------------------------*/
    PicamModel_Pylon400Series           =  420,
    PicamModel_Pylon400F                =  405,
    PicamModel_Pylon400B                =  402,
    PicamModel_Pylon400BR               =  408,
    PicamModel_Pylon400BExcelon         =  427,
    PicamModel_Pylon400BRExcelon        =  428,
    #/* PyLoN 1024 Series -----------------------------------------------------*/
    PicamModel_Pylon1024Series          =  421,
    PicamModel_Pylon1024B               =  417,
    PicamModel_Pylon1024BExcelon        =  429,
    #/* PyLoN 1300 Series -----------------------------------------------------*/
    PicamModel_Pylon1300Series          =  422,
    PicamModel_Pylon1300F               =  406,
    PicamModel_Pylon1300B               =  403,
    PicamModel_Pylon1300R               =  438,
    PicamModel_Pylon1300BR              =  432,
    PicamModel_Pylon1300BExcelon        =  430,
    PicamModel_Pylon1300BRExcelon       =  433,
    #/* PyLoN 2048 Series -----------------------------------------------------*/
    PicamModel_Pylon2048Series          =  423,
    PicamModel_Pylon2048F               =  415,
    PicamModel_Pylon2048B               =  434,
    PicamModel_Pylon2048BR              =  416,
    PicamModel_Pylon2048BExcelon        =  435,
    PicamModel_Pylon2048BRExcelon       =  436,
    #/* PyLoN 2K Series -------------------------------------------------------*/
    PicamModel_Pylon2KSeries            =  424,
    PicamModel_Pylon2KF                 =  413,
    PicamModel_Pylon2KB                 =  414,
    PicamModel_Pylon2KBUV               =  437,
    PicamModel_Pylon2KBExcelon          =  431,
    #/*------------------------------------------------------------------------*/
    #/* PyLoN-IR Series (904) -------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PylonirSeries            =  900,
    #/* PyLoN-IR 1024 Series --------------------------------------------------*/
    PicamModel_Pylonir1024Series        =  901,
    PicamModel_Pylonir102422            =  902,
    PicamModel_Pylonir102417            =  903,
    #/*------------------------------------------------------------------------*/
    #/* PIoNIR Series (502) ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_PionirSeries             =  500,
    PicamModel_Pionir640                =  501,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana Series (802) --------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaSeries            =  800,
    PicamModel_Nirvana640               =  801,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana ST Series (1302) ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaSTSeries          = 1300,
    PicamModel_NirvanaST640             = 1301,
    #/*------------------------------------------------------------------------*/
    #/* NIRvana-LN Series (1102) ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamModel_NirvanaLNSeries          = 1100,
    PicamModel_NirvanaLN640             = 1101
    #/*------------------------------------------------------------------------*/
    ))

"""
/*----------------------------------------------------------------------------*/
typedef enum PicamComputerInterface
{
    PicamComputerInterface_Usb2            = 1,
    PicamComputerInterface_1394A           = 2,
    PicamComputerInterface_GigabitEthernet = 3
} PicamComputerInterface; /* (4) */
"""
PicamComputerInterfaceEnum = PI_Enum(
    "PicamComputerInterface", dict(
    PicamComputerInterface_Usb2            = 1,
    PicamComputerInterface_1394A           = 2,
    PicamComputerInterface_GigabitEthernet = 3                                   
    ))
"""/*----------------------------------------------------------------------------*/
typedef enum PicamStringSize
{
    PicamStringSize_SensorName     =  64,
    PicamStringSize_SerialNumber   =  64,
    PicamStringSize_FirmwareName   =  64,
    PicamStringSize_FirmwareDetail = 256
} PicamStringSize;
"""
PicamStringSizeEnum = PI_Enum(
    "PicamStringSize", dict(
    PicamStringSize_SensorName     =  64,
    PicamStringSize_SerialNumber   =  64,
    PicamStringSize_FirmwareName   =  64,
    PicamStringSize_FirmwareDetail = 256                       
    ))

"""
/*----------------------------------------------------------------------------*/
typedef struct PicamCameraID
{
    PicamModel             model;
    PicamComputerInterface computer_interface;
    pichar                 sensor_name[PicamStringSize_SensorName];
    pichar                 serial_number[PicamStringSize_SerialNumber];
} PicamCameraID;
"""
class PicamCameraID(ctypes.Structure):
    _fields_ = [("model", ctypes.c_int),
                ("PicamComputerInterface", ctypes.c_int),
                ("sensor_name", pichar * PicamStringSizeEnum.bysname['SensorName']),
                ("serial_number", pichar * PicamStringSizeEnum.bysname['SerialNumber'])
                ]
"""
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyCameraIDs( const PicamCameraID* id_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetAvailableCameraIDs(
    const PicamCameraID** id_array,
    piint*                id_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetUnavailableCameraIDs(
    const PicamCameraID** id_array,
    piint*                id_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsCameraIDConnected(
    const PicamCameraID* id,
    pibln*               connected );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsCameraIDOpenElsewhere(
    const PicamCameraID* id,
    pibln*               open_elsewhere );
/*----------------------------------------------------------------------------*/
/* Camera Access -------------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef void* PicamHandle;
"""
PicamHandle = ctypes.c_void_p
"""
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyHandles( const PicamHandle* handle_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_OpenFirstCamera( PicamHandle* camera );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_OpenCamera(
    const PicamCameraID* id,
    PicamHandle*         camera );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CloseCamera( PicamHandle camera );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetOpenCameras(
    const PicamHandle** camera_array,
    piint*              camera_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsCameraConnected(
    PicamHandle camera,
    pibln*      connected );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetCameraID(
    PicamHandle    camera,
    PicamCameraID* id );
/*----------------------------------------------------------------------------*/
/* Camera Information --------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamFirmwareDetail
{
    pichar name[PicamStringSize_FirmwareName];
    pichar detail[PicamStringSize_FirmwareDetail];
} PicamFirmwareDetail;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyFirmwareDetails(
    const PicamFirmwareDetail* firmware_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetFirmwareDetails(
    const PicamCameraID*        id,
    const PicamFirmwareDetail** firmware_array,
    piint*                      firmware_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Demo Camera ---------------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyModels( const PicamModel* model_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetAvailableDemoCameraModels(
    const PicamModel** model_array,
    piint*             model_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_ConnectDemoCamera(
    PicamModel     model,
    const pichar*  serial_number,
    PicamCameraID* id );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DisconnectDemoCamera( const PicamCameraID* id );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsDemoCamera(
    const PicamCameraID* id,
    pibln*               demo );
/*----------------------------------------------------------------------------*/

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera Parameter Values, Information, Constraints and Commitment           */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/

/*----------------------------------------------------------------------------*/
/* Camera Parameters ---------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamValueType
{
    /*------------------------------------------------------------------------*/
    /* Integral Types --------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_Integer       = 1,
    PicamValueType_Boolean       = 3,
    PicamValueType_Enumeration   = 4,
    /*------------------------------------------------------------------------*/
    /* Large Integral Type ---------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_LargeInteger  = 6,
    /*------------------------------------------------------------------------*/
    /* Floating Point Type ---------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_FloatingPoint = 2,
    /*------------------------------------------------------------------------*/
    /* Regions of Interest Type ----------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_Rois          = 5,
    /*------------------------------------------------------------------------*/
    /* Pulse Type ------------------------------------------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_Pulse         = 7,
    /*------------------------------------------------------------------------*/
    /* Custom Intensifier Modulation Sequence Type ---------------------------*/
    /*------------------------------------------------------------------------*/
    PicamValueType_Modulations   = 8
    /*------------------------------------------------------------------------*/
} PicamValueType; /* (9) */
"""
PicamValueTypeEnum  = PI_Enum(
    "PicamValueType",  dict(
    #/*------------------------------------------------------------------------*/
    #/* Integral Types --------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Integer       = 1,
    PicamValueType_Boolean       = 3,
    PicamValueType_Enumeration   = 4,
    #/*------------------------------------------------------------------------*/
    #/* Large Integral Type ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_LargeInteger  = 6,
    #/*------------------------------------------------------------------------*/
    #/* Floating Point Type ---------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_FloatingPoint = 2,
    #/*------------------------------------------------------------------------*/
    #/* Regions of Interest Type ----------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Rois          = 5,
    #/*------------------------------------------------------------------------*/
    #/* Pulse Type ------------------------------------------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Pulse         = 7,
    #/*------------------------------------------------------------------------*/
    #/* Custom Intensifier Modulation Sequence Type ---------------------------*/
    #/*------------------------------------------------------------------------*/
    PicamValueType_Modulations   = 8
    #/*------------------------------------------------------------------------*/
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamConstraintType
{
    PicamConstraintType_None        = 1,
    PicamConstraintType_Range       = 2,
    PicamConstraintType_Collection  = 3,
    PicamConstraintType_Rois        = 4,
    PicamConstraintType_Pulse       = 5,
    PicamConstraintType_Modulations = 6
} PicamConstraintType; /* (7) */
/*-----------------------------------------------------------------------------------------*/
"""
PicamConstraintTypeEnum = PI_Enum(
    "PicamConstraintType", dict(
    PicamConstraintType_None        = 1,
    PicamConstraintType_Range       = 2,
    PicamConstraintType_Collection  = 3,
    PicamConstraintType_Rois        = 4,
    PicamConstraintType_Pulse       = 5,
    PicamConstraintType_Modulations = 6
    ))
"""
typedef enum PicamParameter
{
#define PI_V(v,c,n) (((PicamConstraintType_##c)<<24)+((PicamValueType_##v)<<16)+(n))
    /*-------------------------------------------------------------------------------------*/
    /* Shutter Timing ---------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_ExposureTime                      = PI_V(FloatingPoint, Range,        23),
    PicamParameter_ShutterTimingMode                 = PI_V(Enumeration,   Collection,   24),
    PicamParameter_ShutterOpeningDelay               = PI_V(FloatingPoint, Range,        46),
    PicamParameter_ShutterClosingDelay               = PI_V(FloatingPoint, Range,        25),
    PicamParameter_ShutterDelayResolution            = PI_V(FloatingPoint, Collection,   47),
    /*-------------------------------------------------------------------------------------*/
    /* Intensifier ------------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_EnableIntensifier                 = PI_V(Boolean,       Collection,   86),
    PicamParameter_IntensifierStatus                 = PI_V(Enumeration,   None,         87),
    PicamParameter_IntensifierGain                   = PI_V(Integer,       Range,        88),
    PicamParameter_EMIccdGainControlMode             = PI_V(Enumeration,   Collection,  123),
    PicamParameter_EMIccdGain                        = PI_V(Integer,       Range,       124),
    PicamParameter_PhosphorDecayDelay                = PI_V(FloatingPoint, Range,        89),
    PicamParameter_PhosphorDecayDelayResolution      = PI_V(FloatingPoint, Collection,   90),
    PicamParameter_GatingMode                        = PI_V(Enumeration,   Collection,   93),
    PicamParameter_RepetitiveGate                    = PI_V("Pulse",         "Pulse",        94),
    PicamParameter_SequentialStartingGate            = PI_V("Pulse",         "Pulse",        95),
    PicamParameter_SequentialEndingGate              = PI_V("Pulse",         "Pulse",        96),
    PicamParameter_SequentialGateStepCount           = PI_V(LargeInteger,  Range,        97),
    PicamParameter_SequentialGateStepIterations      = PI_V(LargeInteger,  Range,        98),
    PicamParameter_DifStartingGate                   = PI_V("Pulse",         "Pulse",       102),
    PicamParameter_DifEndingGate                     = PI_V("Pulse",         "Pulse",       103),
    PicamParameter_BracketGating                     = PI_V(Boolean,       Collection,  100),
    PicamParameter_IntensifierOptions                = PI_V(Enumeration,   None,        101),
    PicamParameter_EnableModulation                  = PI_V(Boolean,       Collection,  111),
    PicamParameter_ModulationDuration                = PI_V(FloatingPoint, Range,       118),
    PicamParameter_ModulationFrequency               = PI_V(FloatingPoint, Range,       112),
    PicamParameter_RepetitiveModulationPhase         = PI_V(FloatingPoint, Range,       113),
    PicamParameter_SequentialStartingModulationPhase = PI_V(FloatingPoint, Range,       114),
    PicamParameter_SequentialEndingModulationPhase   = PI_V(FloatingPoint, Range,       115),
    PicamParameter_CustomModulationSequence          = PI_V("Modulations",   "Modulations", 119),
    PicamParameter_PhotocathodeSensitivity           = PI_V(Enumeration,   None,        107),
    PicamParameter_GatingSpeed                       = PI_V(Enumeration,   None,        108),
    PicamParameter_PhosphorType                      = PI_V(Enumeration,   None,        109),
    PicamParameter_IntensifierDiameter               = PI_V(FloatingPoint, None,        110),
    /*-------------------------------------------------------------------------------------*/
    /* Analog to Digital Conversion -------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_AdcSpeed                          = PI_V(FloatingPoint, Collection,   33),
    PicamParameter_AdcBitDepth                       = PI_V(Integer,       Collection,   34),
    PicamParameter_AdcAnalogGain                     = PI_V(Enumeration,   Collection,   35),
    PicamParameter_AdcQuality                        = PI_V(Enumeration,   Collection,   36),
    PicamParameter_AdcEMGain                         = PI_V(Integer,       Range,        53),
    PicamParameter_CorrectPixelBias                  = PI_V(Boolean,       Collection,  106),
    /*-------------------------------------------------------------------------------------*/
    /* Hardware I/O -----------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_TriggerSource                     = PI_V(Enumeration,   Collection,   79),
    PicamParameter_TriggerResponse                   = PI_V(Enumeration,   Collection,   30),
    PicamParameter_TriggerDetermination              = PI_V(Enumeration,   Collection,   31),
    PicamParameter_TriggerFrequency                  = PI_V(FloatingPoint, Range,        80),
    PicamParameter_TriggerTermination                = PI_V(Enumeration,   Collection,   81),
    PicamParameter_TriggerCoupling                   = PI_V(Enumeration,   Collection,   82),
    PicamParameter_TriggerThreshold                  = PI_V(FloatingPoint, Range,        83),
    PicamParameter_OutputSignal                      = PI_V(Enumeration,   Collection,   32),
    PicamParameter_InvertOutputSignal                = PI_V(Boolean,       Collection,   52),
    PicamParameter_AuxOutput                         = PI_V("Pulse",         "Pulse",        91),
    PicamParameter_EnableSyncMaster                  = PI_V(Boolean,       Collection,   84),
    PicamParameter_SyncMaster2Delay                  = PI_V(FloatingPoint, Range,        85),
    PicamParameter_EnableModulationOutputSignal      = PI_V(Boolean,       Collection,  116),
    PicamParameter_ModulationOutputSignalFrequency   = PI_V(FloatingPoint, Range,       117),
    PicamParameter_ModulationOutputSignalAmplitude   = PI_V(FloatingPoint, Range,       120),
    PicamParameter_AnticipateTrigger                 = PI_V(Boolean,       Collection,  131),
    PicamParameter_DelayFromPreTrigger               = PI_V(FloatingPoint, Range,       132),
    /*-------------------------------------------------------------------------------------*/
    /* Readout Control --------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_ReadoutControlMode                = PI_V(Enumeration,   Collection,   26),
    PicamParameter_ReadoutTimeCalculation            = PI_V(FloatingPoint, None,         27),
    PicamParameter_ReadoutPortCount                  = PI_V(Integer,       Collection,   28),
    PicamParameter_ReadoutOrientation                = PI_V(Enumeration,   None,         54),
    PicamParameter_KineticsWindowHeight              = PI_V(Integer,       Range,        56),
    PicamParameter_VerticalShiftRate                 = PI_V(FloatingPoint, Collection,   13),
    PicamParameter_Accumulations                     = PI_V(LargeInteger,  Range,        92),
    PicamParameter_EnableNondestructiveReadout       = PI_V(Boolean,       Collection,  128),
    PicamParameter_NondestructiveReadoutPeriod       = PI_V(FloatingPoint, Range,       129),
    /*-------------------------------------------------------------------------------------*/
    /* Data Acquisition -------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_Rois                              = PI_V(Rois,          Rois,         37),
    PicamParameter_NormalizeOrientation              = PI_V(Boolean,       Collection,   39),
    PicamParameter_DisableDataFormatting             = PI_V(Boolean,       Collection,   55),
    PicamParameter_ReadoutCount                      = PI_V(LargeInteger,  Range,        40),
    PicamParameter_ExactReadoutCountMaximum          = PI_V(LargeInteger,  None,         77),
    PicamParameter_PhotonDetectionMode               = PI_V(Enumeration,   Collection,  125),
    PicamParameter_PhotonDetectionThreshold          = PI_V(FloatingPoint, Range,       126),
    PicamParameter_PixelFormat                       = PI_V(Enumeration,   Collection,   41),
    PicamParameter_FrameSize                         = PI_V(Integer,       None,         42),
    PicamParameter_FrameStride                       = PI_V(Integer,       None,         43),
    PicamParameter_FramesPerReadout                  = PI_V(Integer,       None,         44),
    PicamParameter_ReadoutStride                     = PI_V(Integer,       None,         45),
    PicamParameter_PixelBitDepth                     = PI_V(Integer,       None,         48),
    PicamParameter_ReadoutRateCalculation            = PI_V(FloatingPoint, None,         50),
    PicamParameter_OnlineReadoutRateCalculation      = PI_V(FloatingPoint, None,         99),
    PicamParameter_FrameRateCalculation              = PI_V(FloatingPoint, None,         51),
    PicamParameter_Orientation                       = PI_V(Enumeration,   None,         38),
    PicamParameter_TimeStamps                        = PI_V(Enumeration,   Collection,   68),
    PicamParameter_TimeStampResolution               = PI_V(LargeInteger,  Collection,   69),
    PicamParameter_TimeStampBitDepth                 = PI_V(Integer,       Collection,   70),
    PicamParameter_TrackFrames                       = PI_V(Boolean,       Collection,   71),
    PicamParameter_FrameTrackingBitDepth             = PI_V(Integer,       Collection,   72),
    PicamParameter_GateTracking                      = PI_V(Enumeration,   Collection,  104),
    PicamParameter_GateTrackingBitDepth              = PI_V(Integer,       Collection,  105),
    PicamParameter_ModulationTracking                = PI_V(Enumeration,   Collection,  121),
    PicamParameter_ModulationTrackingBitDepth        = PI_V(Integer,       Collection,  122),
    /*-------------------------------------------------------------------------------------*/
    /* Sensor Information -----------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_SensorType                        = PI_V(Enumeration,   None,         57),
    PicamParameter_CcdCharacteristics                = PI_V(Enumeration,   None,         58),
    PicamParameter_SensorActiveWidth                 = PI_V(Integer,       None,         59),
    PicamParameter_SensorActiveHeight                = PI_V(Integer,       None,         60),
    PicamParameter_SensorActiveLeftMargin            = PI_V(Integer,       None,         61),
    PicamParameter_SensorActiveTopMargin             = PI_V(Integer,       None,         62),
    PicamParameter_SensorActiveRightMargin           = PI_V(Integer,       None,         63),
    PicamParameter_SensorActiveBottomMargin          = PI_V(Integer,       None,         64),
    PicamParameter_SensorMaskedHeight                = PI_V(Integer,       None,         65),
    PicamParameter_SensorMaskedTopMargin             = PI_V(Integer,       None,         66),
    PicamParameter_SensorMaskedBottomMargin          = PI_V(Integer,       None,         67),
    PicamParameter_SensorSecondaryMaskedHeight       = PI_V(Integer,       None,         49),
    PicamParameter_SensorSecondaryActiveHeight       = PI_V(Integer,       None,         74),
    PicamParameter_PixelWidth                        = PI_V(FloatingPoint, None,          9),
    PicamParameter_PixelHeight                       = PI_V(FloatingPoint, None,         10),
    PicamParameter_PixelGapWidth                     = PI_V(FloatingPoint, None,         11),
    PicamParameter_PixelGapHeight                    = PI_V(FloatingPoint, None,         12),
    /*-------------------------------------------------------------------------------------*/
    /* Sensor Layout ----------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_ActiveWidth                       = PI_V(Integer,       Range,         1),
    PicamParameter_ActiveHeight                      = PI_V(Integer,       Range,         2),
    PicamParameter_ActiveLeftMargin                  = PI_V(Integer,       Range,         3),
    PicamParameter_ActiveTopMargin                   = PI_V(Integer,       Range,         4),
    PicamParameter_ActiveRightMargin                 = PI_V(Integer,       Range,         5),
    PicamParameter_ActiveBottomMargin                = PI_V(Integer,       Range,         6),
    PicamParameter_MaskedHeight                      = PI_V(Integer,       Range,         7),
    PicamParameter_MaskedTopMargin                   = PI_V(Integer,       Range,         8),
    PicamParameter_MaskedBottomMargin                = PI_V(Integer,       Range,        73),
    PicamParameter_SecondaryMaskedHeight             = PI_V(Integer,       Range,        75),
    PicamParameter_SecondaryActiveHeight             = PI_V(Integer,       Range,        76),
    /*-------------------------------------------------------------------------------------*/
    /* Sensor Cleaning --------------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_CleanSectionFinalHeight           = PI_V(Integer,       Range,        17),
    PicamParameter_CleanSectionFinalHeightCount      = PI_V(Integer,       Range,        18),
    PicamParameter_CleanSerialRegister               = PI_V(Boolean,       Collection,   19),
    PicamParameter_CleanCycleCount                   = PI_V(Integer,       Range,        20),
    PicamParameter_CleanCycleHeight                  = PI_V(Integer,       Range,        21),
    PicamParameter_CleanBeforeExposure               = PI_V(Boolean,       Collection,   78),
    PicamParameter_CleanUntilTrigger                 = PI_V(Boolean,       Collection,   22),
    PicamParameter_StopCleaningOnPreTrigger          = PI_V(Boolean,       Collection,  130),
    /*-------------------------------------------------------------------------------------*/
    /* Sensor Temperature -----------------------------------------------------------------*/
    /*-------------------------------------------------------------------------------------*/
    PicamParameter_SensorTemperatureSetPoint         = PI_V(FloatingPoint, Range,        14),
    PicamParameter_SensorTemperatureReading          = PI_V(FloatingPoint, None,         15),
    PicamParameter_SensorTemperatureStatus           = PI_V(Enumeration,   None,         16),
    PicamParameter_DisableCoolingFan                 = PI_V(Boolean,       Collection,   29),
    PicamParameter_EnableSensorWindowHeater          = PI_V(Boolean,       Collection,  127)
    /*-------------------------------------------------------------------------------------*/
#undef PI_V
} PicamParameter; /* (133) */
"""
class PI_Param(object):

    def __init__(self, param_type,constraint_type, offset_n):
        
        self.name = None
        self.param_type = param_type
        self.constraint_type = constraint_type
        n = self.offset_n = offset_n
        
        c = PicamConstraintTypeEnum.bysname[self.constraint_type]
        v = PicamValueTypeEnum.bysname[self.param_type]
        self.enum = (c<<24)+(v<<16)+(n)

PicamParameter = OrderedDict([
#define PI_V(v,c,n) (((PicamConstraintType_##c)<<24)+((PicamValueType_##v)<<16)+(n))
    #/*-------------------------------------------------------------------------------------*/
    #/* Shutter Timing ---------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ExposureTime"                      , PI_Param("FloatingPoint", "Range",        23) ),
    ("PicamParameter_ShutterTimingMode"                 , PI_Param("Enumeration",   "Collection",   24) ),
    ("PicamParameter_ShutterOpeningDelay"               , PI_Param("FloatingPoint", "Range",        46) ),
    ("PicamParameter_ShutterClosingDelay"               , PI_Param("FloatingPoint", "Range",        25) ),
    ("PicamParameter_ShutterDelayResolution"            , PI_Param("FloatingPoint", "Collection",   47) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Intensifier ------------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_EnableIntensifier"                 , PI_Param("Boolean",       "Collection",   86) ),
    ("PicamParameter_IntensifierStatus"                 , PI_Param("Enumeration",   "None",         87) ),
    ("PicamParameter_IntensifierGain"                   , PI_Param("Integer",       "Range",        88) ),
    ("PicamParameter_EMIccdGainControlMode"             , PI_Param("Enumeration",   "Collection",  123) ),
    ("PicamParameter_EMIccdGain"                        , PI_Param("Integer",       "Range",       124) ),
    ("PicamParameter_PhosphorDecayDelay"                , PI_Param("FloatingPoint", "Range",        89) ),
    ("PicamParameter_PhosphorDecayDelayResolution"      , PI_Param("FloatingPoint", "Collection",   90) ),
    ("PicamParameter_GatingMode"                        , PI_Param("Enumeration",   "Collection",   93) ),
    ("PicamParameter_RepetitiveGate"                    , PI_Param("Pulse",         "Pulse",        94) ),
    ("PicamParameter_SequentialStartingGate"            , PI_Param("Pulse",         "Pulse",        95) ),
    ("PicamParameter_SequentialEndingGate"              , PI_Param("Pulse",         "Pulse",        96) ),
    ("PicamParameter_SequentialGateStepCount"           , PI_Param("LargeInteger",  "Range",        97) ),
    ("PicamParameter_SequentialGateStepIterations"      , PI_Param("LargeInteger",  "Range",        98) ),
    ("PicamParameter_DifStartingGate"                   , PI_Param("Pulse",         "Pulse",       102) ),
    ("PicamParameter_DifEndingGate"                     , PI_Param("Pulse",         "Pulse",       103) ),
    ("PicamParameter_BracketGating"                     , PI_Param("Boolean",       "Collection",  100) ),
    ("PicamParameter_IntensifierOptions"                , PI_Param("Enumeration",   "None",        101) ),
    ("PicamParameter_EnableModulation"                  , PI_Param("Boolean",       "Collection",  111) ),
    ("PicamParameter_ModulationDuration"                , PI_Param("FloatingPoint", "Range",       118) ),
    ("PicamParameter_ModulationFrequency"               , PI_Param("FloatingPoint", "Range",       112) ),
    ("PicamParameter_RepetitiveModulationPhase"         , PI_Param("FloatingPoint", "Range",       113) ),
    ("PicamParameter_SequentialStartingModulationPhase" , PI_Param("FloatingPoint", "Range",       114) ),
    ("PicamParameter_SequentialEndingModulationPhase"   , PI_Param("FloatingPoint", "Range",       115) ),
    ("PicamParameter_CustomModulationSequence"          , PI_Param("Modulations",   "Modulations", 119) ),
    ("PicamParameter_PhotocathodeSensitivity"           , PI_Param("Enumeration",   "None",        107) ),
    ("PicamParameter_GatingSpeed"                       , PI_Param("Enumeration",   "None",        108) ),
    ("PicamParameter_PhosphorType"                      , PI_Param("Enumeration",   "None",        109) ),
    ("PicamParameter_IntensifierDiameter"               , PI_Param("FloatingPoint", "None",        110) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Analog to Digital Conversion -------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_AdcSpeed"                          , PI_Param("FloatingPoint", "Collection",   33) ),
    ("PicamParameter_AdcBitDepth"                       , PI_Param("Integer",       "Collection",   34) ),
    ("PicamParameter_AdcAnalogGain"                     , PI_Param("Enumeration",   "Collection",   35) ),
    ("PicamParameter_AdcQuality"                        , PI_Param("Enumeration",   "Collection",   36) ),
    ("PicamParameter_AdcEMGain"                         , PI_Param("Integer",       "Range",        53) ),
    ("PicamParameter_CorrectPixelBias"                  , PI_Param("Boolean",       "Collection",  106) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Hardware I/O -----------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_TriggerSource"                     , PI_Param("Enumeration",   "Collection",   79) ),
    ("PicamParameter_TriggerResponse"                   , PI_Param("Enumeration",   "Collection",   30) ),
    ("PicamParameter_TriggerDetermination"              , PI_Param("Enumeration",   "Collection",   31) ),
    ("PicamParameter_TriggerFrequency"                  , PI_Param("FloatingPoint", "Range",        80) ),
    ("PicamParameter_TriggerTermination"                , PI_Param("Enumeration",   "Collection",   81) ),
    ("PicamParameter_TriggerCoupling"                   , PI_Param("Enumeration",   "Collection",   82) ),
    ("PicamParameter_TriggerThreshold"                  , PI_Param("FloatingPoint", "Range",        83) ),
    ("PicamParameter_OutputSignal"                      , PI_Param("Enumeration",   "Collection",   32) ),
    ("PicamParameter_InvertOutputSignal"                , PI_Param("Boolean",       "Collection",   52) ),
    ("PicamParameter_AuxOutput"                         , PI_Param("Pulse",         "Pulse",        91) ),
    ("PicamParameter_EnableSyncMaster"                  , PI_Param("Boolean",       "Collection",   84) ),
    ("PicamParameter_SyncMaster2Delay"                  , PI_Param("FloatingPoint", "Range",        85) ),
    ("PicamParameter_EnableModulationOutputSignal"      , PI_Param("Boolean",       "Collection",  116) ),
    ("PicamParameter_ModulationOutputSignalFrequency"   , PI_Param("FloatingPoint", "Range",       117) ),
    ("PicamParameter_ModulationOutputSignalAmplitude"   , PI_Param("FloatingPoint", "Range",       120) ),
    ("PicamParameter_AnticipateTrigger"                 , PI_Param("Boolean",       "Collection",  131) ),
    ("PicamParameter_DelayFromPreTrigger"               , PI_Param("FloatingPoint", "Range",       132) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Readout Control --------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ReadoutControlMode"                , PI_Param("Enumeration",   "Collection",   26) ),
    ("PicamParameter_ReadoutTimeCalculation"            , PI_Param("FloatingPoint", "None",         27) ),
    ("PicamParameter_ReadoutPortCount"                  , PI_Param("Integer",       "Collection",   28) ),
    ("PicamParameter_ReadoutOrientation"                , PI_Param("Enumeration",   "None",         54) ),
    ("PicamParameter_KineticsWindowHeight"              , PI_Param("Integer",       "Range",        56) ),
    ("PicamParameter_VerticalShiftRate"                 , PI_Param("FloatingPoint", "Collection",   13) ),
    ("PicamParameter_Accumulations"                     , PI_Param("LargeInteger",  "Range",        92) ),
    ("PicamParameter_EnableNondestructiveReadout"       , PI_Param("Boolean",       "Collection",  128) ),
    ("PicamParameter_NondestructiveReadoutPeriod"       , PI_Param("FloatingPoint", "Range",       129) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Data Acquisition -------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_Rois"                              , PI_Param("Rois",          "Rois",         37) ),
    ("PicamParameter_NormalizeOrientation"              , PI_Param("Boolean",       "Collection",   39) ),
    ("PicamParameter_DisableDataFormatting"             , PI_Param("Boolean",       "Collection",   55) ),
    ("PicamParameter_ReadoutCount"                      , PI_Param("LargeInteger",  "Range",        40) ),
    ("PicamParameter_ExactReadoutCountMaximum"          , PI_Param("LargeInteger",  "None",         77) ),
    ("PicamParameter_PhotonDetectionMode"               , PI_Param("Enumeration",   "Collection",  125) ),
    ("PicamParameter_PhotonDetectionThreshold"          , PI_Param("FloatingPoint", "Range",       126) ),
    ("PicamParameter_PixelFormat"                       , PI_Param("Enumeration",   "Collection",   41) ),
    ("PicamParameter_FrameSize"                         , PI_Param("Integer",       "None",         42) ),
    ("PicamParameter_FrameStride"                       , PI_Param("Integer",       "None",         43) ),
    ("PicamParameter_FramesPerReadout"                  , PI_Param("Integer",       "None",         44) ),
    ("PicamParameter_ReadoutStride"                     , PI_Param("Integer",       "None",         45) ),
    ("PicamParameter_PixelBitDepth"                     , PI_Param("Integer",       "None",         48) ),
    ("PicamParameter_ReadoutRateCalculation"            , PI_Param("FloatingPoint", "None",         50) ),
    ("PicamParameter_OnlineReadoutRateCalculation"      , PI_Param("FloatingPoint", "None",         99) ),
    ("PicamParameter_FrameRateCalculation"              , PI_Param("FloatingPoint", "None",         51) ),
    ("PicamParameter_Orientation"                       , PI_Param("Enumeration",   "None",         38) ),
    ("PicamParameter_TimeStamps"                        , PI_Param("Enumeration",   "Collection",   68) ),
    ("PicamParameter_TimeStampResolution"               , PI_Param("LargeInteger",  "Collection",   69) ),
    ("PicamParameter_TimeStampBitDepth"                 , PI_Param("Integer",       "Collection",   70) ),
    ("PicamParameter_TrackFrames"                       , PI_Param("Boolean",       "Collection",   71) ),
    ("PicamParameter_FrameTrackingBitDepth"             , PI_Param("Integer",       "Collection",   72) ),
    ("PicamParameter_GateTracking"                      , PI_Param("Enumeration",   "Collection",  104) ),
    ("PicamParameter_GateTrackingBitDepth"              , PI_Param("Integer",       "Collection",  105) ),
    ("PicamParameter_ModulationTracking"                , PI_Param("Enumeration",   "Collection",  121) ),
    ("PicamParameter_ModulationTrackingBitDepth"        , PI_Param("Integer",       "Collection",  122) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Information -----------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_SensorType"                        , PI_Param("Enumeration",   "None",         57) ),
    ("PicamParameter_CcdCharacteristics"                , PI_Param("Enumeration",   "None",         58) ),
    ("PicamParameter_SensorActiveWidth"                 , PI_Param("Integer",       "None",         59) ),
    ("PicamParameter_SensorActiveHeight"                , PI_Param("Integer",       "None",         60) ),
    ("PicamParameter_SensorActiveLeftMargin"            , PI_Param("Integer",       "None",         61) ),
    ("PicamParameter_SensorActiveTopMargin"             , PI_Param("Integer",       "None",         62) ),
    ("PicamParameter_SensorActiveRightMargin"           , PI_Param("Integer",       "None",         63) ),
    ("PicamParameter_SensorActiveBottomMargin"          , PI_Param("Integer",       "None",         64) ),
    ("PicamParameter_SensorMaskedHeight"                , PI_Param("Integer",       "None",         65) ),
    ("PicamParameter_SensorMaskedTopMargin"             , PI_Param("Integer",       "None",         66) ),
    ("PicamParameter_SensorMaskedBottomMargin"          , PI_Param("Integer",       "None",         67) ),
    ("PicamParameter_SensorSecondaryMaskedHeight"       , PI_Param("Integer",       "None",         49) ),
    ("PicamParameter_SensorSecondaryActiveHeight"       , PI_Param("Integer",       "None",         74) ),
    ("PicamParameter_PixelWidth"                        , PI_Param("FloatingPoint", "None",          9) ),
    ("PicamParameter_PixelHeight"                       , PI_Param("FloatingPoint", "None",         10) ),
    ("PicamParameter_PixelGapWidth"                     , PI_Param("FloatingPoint", "None",         11) ),
    ("PicamParameter_PixelGapHeight"                    , PI_Param("FloatingPoint", "None",         12) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Layout ----------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_ActiveWidth"                       , PI_Param("Integer",       "Range",         1) ),
    ("PicamParameter_ActiveHeight"                      , PI_Param("Integer",       "Range",         2) ),
    ("PicamParameter_ActiveLeftMargin"                  , PI_Param("Integer",       "Range",         3) ),
    ("PicamParameter_ActiveTopMargin"                   , PI_Param("Integer",       "Range",         4) ),
    ("PicamParameter_ActiveRightMargin"                 , PI_Param("Integer",       "Range",         5) ),
    ("PicamParameter_ActiveBottomMargin"                , PI_Param("Integer",       "Range",         6) ),
    ("PicamParameter_MaskedHeight"                      , PI_Param("Integer",       "Range",         7) ),
    ("PicamParameter_MaskedTopMargin"                   , PI_Param("Integer",       "Range",         8) ),
    ("PicamParameter_MaskedBottomMargin"                , PI_Param("Integer",       "Range",        73) ),
    ("PicamParameter_SecondaryMaskedHeight"             , PI_Param("Integer",       "Range",        75) ),
    ("PicamParameter_SecondaryActiveHeight"             , PI_Param("Integer",       "Range",        76) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Cleaning --------------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_CleanSectionFinalHeight"           , PI_Param("Integer",       "Range",        17) ),
    ("PicamParameter_CleanSectionFinalHeightCount"      , PI_Param("Integer",       "Range",        18) ),
    ("PicamParameter_CleanSerialRegister"               , PI_Param("Boolean",       "Collection",   19) ),
    ("PicamParameter_CleanCycleCount"                   , PI_Param("Integer",       "Range",        20) ),
    ("PicamParameter_CleanCycleHeight"                  , PI_Param("Integer",       "Range",        21) ),
    ("PicamParameter_CleanBeforeExposure"               , PI_Param("Boolean",       "Collection",   78) ),
    ("PicamParameter_CleanUntilTrigger"                 , PI_Param("Boolean",       "Collection",   22) ),
    ("PicamParameter_StopCleaningOnPreTrigger"          , PI_Param("Boolean",       "Collection",  130) ),
    #/*-------------------------------------------------------------------------------------*/
    #/* Sensor Temperature -----------------------------------------------------------------*/
    #/*-------------------------------------------------------------------------------------*/
    ("PicamParameter_SensorTemperatureSetPoint"         , PI_Param("FloatingPoint", "Range",        14) ),
    ("PicamParameter_SensorTemperatureReading"          , PI_Param("FloatingPoint", "None",         15) ),
    ("PicamParameter_SensorTemperatureStatus"           , PI_Param("Enumeration",   "None",         16) ),
    ("PicamParameter_DisableCoolingFan"                 , PI_Param("Boolean",       "Collection",   29) ),
    ("PicamParameter_EnableSensorWindowHeater"          , PI_Param("Boolean",       "Collection",  127) )
    #/*-------------------------------------------------------------------------------------*/
    ])
for name,param in PicamParameter.items():
    param.name = name
    param.short_name = name.split("_")[1]

PicamParam = dict()
for name, param in PicamParameter.items():
    PicamParam[param.short_name] = param

#provide a direct enum to parameters
PicamParameterEnum = PI_Enum(
    "PicamParameter",
    {name:param.enum for name,param in PicamParameter.items()})

"""
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Integer -----------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piint*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piint          value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piint          value,
    pibln*         settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Large Integer -----------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterLargeIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    pi64s*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterLargeIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    pi64s          value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterLargeIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    pi64s          value,
    pibln*         settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Floating Point ----------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterFloatingPointValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterFloatingPointValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt          value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterFloatingPointValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt          value,
    pibln*         settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Regions of Interest -----------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamRoi
{
    piint x;
    piint width;
    piint x_binning;
    piint y;
    piint height;
    piint y_binning;
} PicamRoi;
"""
class PicamRoi(ctypes.Structure):
    _fields_ = [("x", piint),
                ("width", piint),
                ("x_binning", piint),
                ("y", piint),
                ("height", piint),
                ("y_binning", piint),
                ]
    def __str__(self):
        return "PicamRoi: "+" ".join(["{}->{}; ".format(fname, getattr(self, fname))
                          for fname, ftype in self._fields_])
            
"""
/*----------------------------------------------------------------------------*/
typedef struct PicamRois
{
    PicamRoi* roi_array;
    piint     roi_count;
} PicamRois;
"""
class PicamRois(ctypes.Structure):
    _fields_ = [("roi_array", ctypes.POINTER(PicamRoi)),
                ("roi_count", piint),
                ]
"""
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyRois( const PicamRois* rois );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterRoisValue(
    PicamHandle       camera,
    PicamParameter    parameter,
    const PicamRois** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterRoisValue(
    PicamHandle      camera,
    PicamParameter   parameter,
    const PicamRois* value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterRoisValue(
    PicamHandle      camera,
    PicamParameter   parameter,
    const PicamRois* value,
    pibln*           settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Pulse -------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamPulse
{
    piflt delay;
    piflt width;
} PicamPulse;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyPulses( const PicamPulse* pulses );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterPulseValue(
    PicamHandle        camera,
    PicamParameter     parameter,
    const PicamPulse** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterPulseValue(
    PicamHandle       camera,
    PicamParameter    parameter,
    const PicamPulse* value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterPulseValue(
    PicamHandle       camera,
    PicamParameter    parameter,
    const PicamPulse* value,
    pibln*            settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Custom Intensifier Modulation Sequence ----------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamModulation
{
    piflt duration;
    piflt frequency;
    piflt phase;
    piflt output_signal_frequency;
} PicamModulation;
/*----------------------------------------------------------------------------*/
typedef struct PicamModulations
{
    PicamModulation* modulation_array;
    piint            modulation_count;
} PicamModulations;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyModulations( const PicamModulations* modulations );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterModulationsValue(
    PicamHandle              camera,
    PicamParameter           parameter,
    const PicamModulations** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterModulationsValue(
    PicamHandle             camera,
    PicamParameter          parameter,
    const PicamModulations* value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterModulationsValue(
    PicamHandle             camera,
    PicamParameter          parameter,
    const PicamModulations* value,
    pibln*                  settable );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Enumerated Types --------------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamAdcAnalogGain
{
    PicamAdcAnalogGain_Low    = 1,
    PicamAdcAnalogGain_Medium = 2,
    PicamAdcAnalogGain_High   = 3
} PicamAdcAnalogGain; /* (4) */
"""
PicamAdcAnalogGainEnum = PI_Enum(
    "PicamAdcAnalogGain", dict(
    PicamAdcAnalogGain_Low    = 1,
    PicamAdcAnalogGain_Medium = 2,
    PicamAdcAnalogGain_High   = 3
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamAdcQuality
{
    PicamAdcQuality_LowNoise           = 1,
    PicamAdcQuality_HighCapacity       = 2,
    PicamAdcQuality_HighSpeed          = 4,
    PicamAdcQuality_ElectronMultiplied = 3
} PicamAdcQuality; /* (5) */
"""
PicamAdcQualityEnum = PI_Enum(
    "PicamAdcQuality", dict(
    PicamAdcQuality_LowNoise           = 1,
    PicamAdcQuality_HighCapacity       = 2,
    PicamAdcQuality_HighSpeed          = 4,
    PicamAdcQuality_ElectronMultiplied = 3
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamCcdCharacteristicsMask
{
    PicamCcdCharacteristicsMask_None                 = 0x000,
    PicamCcdCharacteristicsMask_BackIlluminated      = 0x001,
    PicamCcdCharacteristicsMask_DeepDepleted         = 0x002,
    PicamCcdCharacteristicsMask_OpenElectrode        = 0x004,
    PicamCcdCharacteristicsMask_UVEnhanced           = 0x008,
    PicamCcdCharacteristicsMask_ExcelonEnabled       = 0x010,
    PicamCcdCharacteristicsMask_SecondaryMask        = 0x020,
    PicamCcdCharacteristicsMask_Multiport            = 0x040,
    PicamCcdCharacteristicsMask_AdvancedInvertedMode = 0x080,
    PicamCcdCharacteristicsMask_HighResistivity      = 0x100
} PicamCcdCharacteristicsMask; /* (0x200) */
"""
PicamCcdCharacteristicsMaskEnum = PI_Enum(
    "PicamCcdCharacteristicsMask", dict(
    PicamCcdCharacteristicsMask_None                 = 0x000,
    PicamCcdCharacteristicsMask_BackIlluminated      = 0x001,
    PicamCcdCharacteristicsMask_DeepDepleted         = 0x002,
    PicamCcdCharacteristicsMask_OpenElectrode        = 0x004,
    PicamCcdCharacteristicsMask_UVEnhanced           = 0x008,
    PicamCcdCharacteristicsMask_ExcelonEnabled       = 0x010,
    PicamCcdCharacteristicsMask_SecondaryMask        = 0x020,
    PicamCcdCharacteristicsMask_Multiport            = 0x040,
    PicamCcdCharacteristicsMask_AdvancedInvertedMode = 0x080,
    PicamCcdCharacteristicsMask_HighResistivity      = 0x100
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamEMIccdGainControlMode
{
    PicamEMIccdGainControlMode_Optimal = 1,
    PicamEMIccdGainControlMode_Manual  = 2
} PicamEMIccdGainControlMode; /* (3) */
"""
PicamEMIccdGainControlModeEnum = PI_Enum(
    "PicamEMIccdGainControlMode", dict(
    PicamEMIccdGainControlMode_Optimal = 1,
    PicamEMIccdGainControlMode_Manual  = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamGateTrackingMask
{
    PicamGateTrackingMask_None  = 0x0,
    PicamGateTrackingMask_Delay = 0x1,
    PicamGateTrackingMask_Width = 0x2
} PicamGateTrackingMask; /* (0x4) */
"""
PicamGateTrackingMaskEnum = PI_Enum(
    "PicamGateTrackingMask", dict(
    PicamGateTrackingMask_None  = 0x0,
    PicamGateTrackingMask_Delay = 0x1,
    PicamGateTrackingMask_Width = 0x2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamGatingMode
{
    PicamGatingMode_Repetitive = 1,
    PicamGatingMode_Sequential = 2,
    PicamGatingMode_Custom     = 3
} PicamGatingMode; /* (4) */
"""
PicamGatingModeEnum = PI_Enum(
    "PicamGatingMode", dict(
    PicamGatingMode_Repetitive = 1,
    PicamGatingMode_Sequential = 2,
    PicamGatingMode_Custom     = 3
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamGatingSpeed
{
    PicamGatingSpeed_Fast = 1,
    PicamGatingSpeed_Slow = 2
} PicamGatingSpeed; /* (3) */
"""
PicamGatingSpeedEnum = PI_Enum(
    "PicamGatingSpeed", dict(
    PicamGatingSpeed_Fast = 1,
    PicamGatingSpeed_Slow = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamIntensifierOptionsMask
{
    PicamIntensifierOptionsMask_None                = 0x0,
    PicamIntensifierOptionsMask_McpGating           = 0x1,
    PicamIntensifierOptionsMask_SubNanosecondGating = 0x2,
    PicamIntensifierOptionsMask_Modulation          = 0x4
} PicamIntensifierOptionsMask; /* (0x8) */
"""
PicamIntensifierOptionsMaskEnum = PI_Enum(
    "PicamIntensifierOptionsMask", dict(
    PicamIntensifierOptionsMask_None                = 0x0,
    PicamIntensifierOptionsMask_McpGating           = 0x1,
    PicamIntensifierOptionsMask_SubNanosecondGating = 0x2,
    PicamIntensifierOptionsMask_Modulation          = 0x4
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamIntensifierStatus
{
    PicamIntensifierStatus_PoweredOff = 1,
    PicamIntensifierStatus_PoweredOn  = 2
} PicamIntensifierStatus; /* (3) */
"""
PicamIntensifierStatusEnum = PI_Enum(
    "PicamIntensifierStatus", dict(
    PicamIntensifierStatus_PoweredOff = 1,
    PicamIntensifierStatus_PoweredOn  = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamModulationTrackingMask
{
    PicamModulationTrackingMask_None                  = 0x0,
    PicamModulationTrackingMask_Duration              = 0x1,
    PicamModulationTrackingMask_Frequency             = 0x2,
    PicamModulationTrackingMask_Phase                 = 0x4,
    PicamModulationTrackingMask_OutputSignalFrequency = 0x8
} PicamModulationTrackingMask; /* (0x10) */
/*----------------------------------------------------------------------------*/
"""
PicamModulationTrackingMaskEnum = PI_Enum(
    "PicamModulationTrackingMask", dict(
    PicamModulationTrackingMask_None                  = 0x0,
    PicamModulationTrackingMask_Duration              = 0x1,
    PicamModulationTrackingMask_Frequency             = 0x2,
    PicamModulationTrackingMask_Phase                 = 0x4,
    PicamModulationTrackingMask_OutputSignalFrequency = 0x8
    ))
"""
typedef enum PicamOrientationMask
{
    PicamOrientationMask_Normal              = 0x0,
    PicamOrientationMask_FlippedHorizontally = 0x1,
    PicamOrientationMask_FlippedVertically   = 0x2
} PicamOrientationMask; /* (0x4) */
/*----------------------------------------------------------------------------*/
"""
PicamOrientationMaskEnum = PI_Enum(
    "PicamOrientationMask", dict(
    PicamOrientationMask_Normal              = 0x0,
    PicamOrientationMask_FlippedHorizontally = 0x1,
    PicamOrientationMask_FlippedVertically   = 0x2
    ))
"""
typedef enum PicamOutputSignal
{
    PicamOutputSignal_NotReadingOut       =  1,
    PicamOutputSignal_ShutterOpen         =  2,
    PicamOutputSignal_Busy                =  3,
    PicamOutputSignal_AlwaysLow           =  4,
    PicamOutputSignal_AlwaysHigh          =  5,
    PicamOutputSignal_Acquiring           =  6, 
    PicamOutputSignal_ShiftingUnderMask   =  7,
    PicamOutputSignal_Exposing            =  8,
    PicamOutputSignal_EffectivelyExposing =  9,
    PicamOutputSignal_ReadingOut          = 10,
    PicamOutputSignal_WaitingForTrigger   = 11
} PicamOutputSignal; /* (12) */
"""
PicamOutputSignalEnum = PI_Enum(
    "PicamOutputSignal", dict(
    PicamOutputSignal_NotReadingOut       =  1,
    PicamOutputSignal_ShutterOpen         =  2,
    PicamOutputSignal_Busy                =  3,
    PicamOutputSignal_AlwaysLow           =  4,
    PicamOutputSignal_AlwaysHigh          =  5,
    PicamOutputSignal_Acquiring           =  6, 
    PicamOutputSignal_ShiftingUnderMask   =  7,
    PicamOutputSignal_Exposing            =  8,
    PicamOutputSignal_EffectivelyExposing =  9,
    PicamOutputSignal_ReadingOut          = 10,
    PicamOutputSignal_WaitingForTrigger   = 11
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamPhosphorType
{
    PicamPhosphorType_P43 = 1,
    PicamPhosphorType_P46 = 2
} PicamPhosphorType; /* (3) */
"""
PicamPhosphorTypeEnum = PI_Enum(
    "PicamPhosphorType", dict(
    PicamPhosphorType_P43 = 1,
    PicamPhosphorType_P46 = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamPhotocathodeSensitivity
{
    PicamPhotocathodeSensitivity_RedBlue          =  1,
    PicamPhotocathodeSensitivity_SuperRed         =  7,
    PicamPhotocathodeSensitivity_SuperBlue        =  2,
    PicamPhotocathodeSensitivity_UV               =  3,
    PicamPhotocathodeSensitivity_SolarBlind       = 10,
    PicamPhotocathodeSensitivity_Unigen2Filmless  =  4,
    PicamPhotocathodeSensitivity_InGaAsFilmless   =  9,
    PicamPhotocathodeSensitivity_HighQEFilmless   =  5,
    PicamPhotocathodeSensitivity_HighRedFilmless  =  8,
    PicamPhotocathodeSensitivity_HighBlueFilmless =  6
} PicamPhotocathodeSensitivity; /* (11) */
"""
PicamPhotocathodeSensitivityEnum = PI_Enum(
    "PicamPhotocathodeSensitivity", dict(
    PicamPhotocathodeSensitivity_RedBlue          =  1,
    PicamPhotocathodeSensitivity_SuperRed         =  7,
    PicamPhotocathodeSensitivity_SuperBlue        =  2,
    PicamPhotocathodeSensitivity_UV               =  3,
    PicamPhotocathodeSensitivity_SolarBlind       = 10,
    PicamPhotocathodeSensitivity_Unigen2Filmless  =  4,
    PicamPhotocathodeSensitivity_InGaAsFilmless   =  9,
    PicamPhotocathodeSensitivity_HighQEFilmless   =  5,
    PicamPhotocathodeSensitivity_HighRedFilmless  =  8,
    PicamPhotocathodeSensitivity_HighBlueFilmless =  6
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamPhotonDetectionMode
{
    PicamPhotonDetectionMode_Disabled     = 1,
    PicamPhotonDetectionMode_Thresholding = 2,
    PicamPhotonDetectionMode_Clipping     = 3
} PicamPhotonDetectionMode; /* (4) */
"""
PicamPhotonDetectionModeEnum = PI_Enum(
    "PicamPhotonDetectionMode", dict(
    PicamPhotonDetectionMode_Disabled     = 1,
    PicamPhotonDetectionMode_Thresholding = 2,
    PicamPhotonDetectionMode_Clipping     = 3
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamPixelFormat
{
    PicamPixelFormat_Monochrome16Bit = 1
} PicamPixelFormat; /* (2) */
"""
PicamPixelFormatEnum = PI_Enum(
    "PicamPixelFormat", dict(
    PicamPixelFormat_Monochrome16Bit = 1
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamReadoutControlMode
{
    PicamReadoutControlMode_FullFrame       = 1,  
    PicamReadoutControlMode_FrameTransfer   = 2,
    PicamReadoutControlMode_Interline       = 5,
    PicamReadoutControlMode_Kinetics        = 3,
    PicamReadoutControlMode_SpectraKinetics = 4,
    PicamReadoutControlMode_Dif             = 6
} PicamReadoutControlMode; /* (7) */
"""
PicamReadoutControlModeEnum = PI_Enum(
    "PicamReadoutControlMode", dict(
    PicamReadoutControlMode_FullFrame       = 1,  
    PicamReadoutControlMode_FrameTransfer   = 2,
    PicamReadoutControlMode_Interline       = 5,
    PicamReadoutControlMode_Kinetics        = 3,
    PicamReadoutControlMode_SpectraKinetics = 4,
    PicamReadoutControlMode_Dif             = 6
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamSensorTemperatureStatus
{
    PicamSensorTemperatureStatus_Unlocked = 1,
    PicamSensorTemperatureStatus_Locked   = 2
} PicamSensorTemperatureStatus; /* (3) */
"""
PicamSensorTemperatureStatusEnum = PI_Enum(                                
    "PicamSensorTemperatureStatus" , dict(
    PicamSensorTemperatureStatus_Unlocked = 1,
    PicamSensorTemperatureStatus_Locked   = 2                                               
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamSensorType
{
    PicamSensorType_Ccd    = 1,
    PicamSensorType_InGaAs = 2
} PicamSensorType; /* (3) */
"""
PicamSensorTypeEnum = PI_Enum(
    "PicamSensorType", dict(
    PicamSensorType_Ccd    = 1,
    PicamSensorType_InGaAs = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamShutterTimingMode
{
    PicamShutterTimingMode_Normal            = 1,
    PicamShutterTimingMode_AlwaysClosed      = 2,
    PicamShutterTimingMode_AlwaysOpen        = 3,
    PicamShutterTimingMode_OpenBeforeTrigger = 4
} PicamShutterTimingMode; /* (5) */
"""
PicamShutterTimingModeEnum = PI_Enum(
    "PicamShutterTimingMode", dict(
    PicamShutterTimingMode_Normal            = 1,
    PicamShutterTimingMode_AlwaysClosed      = 2,
    PicamShutterTimingMode_AlwaysOpen        = 3,
    PicamShutterTimingMode_OpenBeforeTrigger = 4
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTimeStampsMask
{
    PicamTimeStampsMask_None            = 0x0,
    PicamTimeStampsMask_ExposureStarted = 0x1,
    PicamTimeStampsMask_ExposureEnded   = 0x2
} PicamTimeStampsMask; /* (0x4) */
"""
PicamTimeStampsMaskEnum = PI_Enum(
    "PicamTimeStampsMask", dict(
    PicamTimeStampsMask_None            = 0x0,
    PicamTimeStampsMask_ExposureStarted = 0x1,
    PicamTimeStampsMask_ExposureEnded   = 0x2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTriggerCoupling
{
    PicamTriggerCoupling_AC = 1,
    PicamTriggerCoupling_DC = 2
} PicamTriggerCoupling; /* (3) */
"""
PicamTriggerCouplingEnum = PI_Enum(
    "PicamTriggerCoupling", dict(
    PicamTriggerCoupling_AC = 1,
    PicamTriggerCoupling_DC = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTriggerDetermination
{
    PicamTriggerDetermination_PositivePolarity = 1,
    PicamTriggerDetermination_NegativePolarity = 2,
    PicamTriggerDetermination_RisingEdge       = 3,
    PicamTriggerDetermination_FallingEdge      = 4
} PicamTriggerDetermination; /* (5) */
"""
PicamTriggerDeterminationEnum = PI_Enum(
    "PicamTriggerDetermination", dict(
    PicamTriggerDetermination_PositivePolarity = 1,
    PicamTriggerDetermination_NegativePolarity = 2,
    PicamTriggerDetermination_RisingEdge       = 3,
    PicamTriggerDetermination_FallingEdge      = 4
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTriggerResponse
{
    PicamTriggerResponse_NoResponse               = 1,
    PicamTriggerResponse_ReadoutPerTrigger        = 2,
    PicamTriggerResponse_ShiftPerTrigger          = 3,
    PicamTriggerResponse_ExposeDuringTriggerPulse = 4,
    PicamTriggerResponse_StartOnSingleTrigger     = 5
} PicamTriggerResponse; /* (6) */
"""
PicamTriggerResponseEnum = PI_Enum(
    "PicamTriggerResponse", dict(
    PicamTriggerResponse_NoResponse               = 1,
    PicamTriggerResponse_ReadoutPerTrigger        = 2,
    PicamTriggerResponse_ShiftPerTrigger          = 3,
    PicamTriggerResponse_ExposeDuringTriggerPulse = 4,
    PicamTriggerResponse_StartOnSingleTrigger     = 5
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTriggerSource
{
    PicamTriggerSource_External = 1,
    PicamTriggerSource_Internal = 2
} PicamTriggerSource; /* (3) */
"""
PicamTriggerSourceEnum = PI_Enum(
    "PicamTriggerSource", dict(
    PicamTriggerSource_External = 1,
    PicamTriggerSource_Internal = 2
    ))
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamTriggerTermination
{
    PicamTriggerTermination_FiftyOhms     = 1,
    PicamTriggerTermination_HighImpedance = 2
} PicamTriggerTermination; /* (3) */
"""
PicamTriggerTerminationEnum = PI_Enum(
    "PicamTriggerTermination", dict(
    PicamTriggerTermination_FiftyOhms     = 1,
    PicamTriggerTermination_HighImpedance = 2
    ))
"""
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Default -----------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterIntegerDefaultValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piint*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterLargeIntegerDefaultValue(
    PicamHandle    camera,
    PicamParameter parameter,
    pi64s*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterFloatingPointDefaultValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterRoisDefaultValue(
    PicamHandle       camera,
    PicamParameter    parameter,
    const PicamRois** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterPulseDefaultValue(
    PicamHandle        camera,
    PicamParameter     parameter,
    const PicamPulse** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterModulationsDefaultValue(
    PicamHandle              camera,
    PicamParameter           parameter,
    const PicamModulations** value ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Online ------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanSetParameterOnline(
    PicamHandle    camera,
    PicamParameter parameter,
    pibln*         onlineable );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterIntegerValueOnline(
    PicamHandle    camera,
    PicamParameter parameter,
    piint          value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterFloatingPointValueOnline(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt          value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_SetParameterPulseValueOnline(
    PicamHandle       camera,
    PicamParameter    parameter,
    const PicamPulse* value );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Values - Reading -----------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CanReadParameter(
    PicamHandle    camera,
    PicamParameter parameter,
    pibln*         readable );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_ReadParameterIntegerValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piint*         value );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_ReadParameterFloatingPointValue(
    PicamHandle    camera,
    PicamParameter parameter,
    piflt*         value );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Information - Available Parameters -----------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyParameters( const PicamParameter* parameter_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameters(
    PicamHandle            camera,
    const PicamParameter** parameter_array,
    piint*                 parameter_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DoesParameterExist(
    PicamHandle    camera,
    PicamParameter parameter,
    pibln*         exists );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Information - Relevance ----------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsParameterRelevant(
    PicamHandle    camera,
    PicamParameter parameter,
    pibln*         relevant );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Information - Value Type ---------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterValueType(
    PicamHandle     camera,
    PicamParameter  parameter,
    PicamValueType* type );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterEnumeratedType(
    PicamHandle          camera,
    PicamParameter       parameter,
    PicamEnumeratedType* type );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Information - Value Access -------------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamValueAccess
{
    PicamValueAccess_ReadOnly         = 1,
    PicamValueAccess_ReadWriteTrivial = 3,
    PicamValueAccess_ReadWrite        = 2
} PicamValueAccess; /* (4) */
"""
PicamValueAccess_num = dict(
    PicamValueAccess_ReadOnly         = 1,
    PicamValueAccess_ReadWriteTrivial = 3,
    PicamValueAccess_ReadWrite        = 2                        
    )
PicamValueAccess = dict()
for k,v in PicamValueAccess_num.items():
    PicamValueAccess[v] = k

"""    
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterValueAccess(
    PicamHandle       camera,
    PicamParameter    parameter,
    PicamValueAccess* access );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Constraint Type ----------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterConstraintType(
    PicamHandle          camera,
    PicamParameter       parameter,
    PicamConstraintType* type );
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Enumerated Types ---------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamConstraintScope
{
    PicamConstraintScope_Independent = 1,
    PicamConstraintScope_Dependent   = 2
} PicamConstraintScope; /* (3) */
/*----------------------------------------------------------------------------*/
typedef enum PicamConstraintSeverity
{
    PicamConstraintSeverity_Error   = 1,
    PicamConstraintSeverity_Warning = 2
} PicamConstraintSeverity; /* (3) */
/*----------------------------------------------------------------------------*/
typedef enum PicamConstraintCategory
{
    PicamConstraintCategory_Capable     = 1,
    PicamConstraintCategory_Required    = 2,
    PicamConstraintCategory_Recommended = 3
} PicamConstraintCategory; /* (4) */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Collection ---------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamCollectionConstraint
{
    PicamConstraintScope    scope;
    PicamConstraintSeverity severity;
    const piflt*            values_array;
    piint                   values_count;
} PicamCollectionConstraint;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyCollectionConstraints(
    const PicamCollectionConstraint* constraint_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterCollectionConstraint(
    PicamHandle                       camera,
    PicamParameter                    parameter,
    PicamConstraintCategory           category,
    const PicamCollectionConstraint** constraint ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Range --------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamRangeConstraint
{
    PicamConstraintScope    scope;
    PicamConstraintSeverity severity;
    pibln                   empty_set;
    piflt                   minimum;
    piflt                   maximum;
    piflt                   increment;
    const piflt*            excluded_values_array;
    piint                   excluded_values_count;
    const piflt*            outlying_values_array;
    piint                   outlying_values_count;
} PicamRangeConstraint;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyRangeConstraints(
    const PicamRangeConstraint* constraint_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterRangeConstraint(
    PicamHandle                  camera,
    PicamParameter               parameter,
    PicamConstraintCategory      category,
    const PicamRangeConstraint** constraint ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Regions Of Interest ------------------------*/
/*----------------------------------------------------------------------------*/
typedef enum PicamRoisConstraintRulesMask
{
    PicamRoisConstraintRulesMask_None                  = 0x00,
    PicamRoisConstraintRulesMask_XBinningAlignment     = 0x01,
    PicamRoisConstraintRulesMask_YBinningAlignment     = 0x02,
    PicamRoisConstraintRulesMask_HorizontalSymmetry    = 0x04,
    PicamRoisConstraintRulesMask_VerticalSymmetry      = 0x08,
    PicamRoisConstraintRulesMask_SymmetryBoundsBinning = 0x10
} PicamRoisConstraintRulesMask; /* (0x20) */
/*----------------------------------------------------------------------------*/
typedef struct PicamRoisConstraint
{
    PicamConstraintScope         scope;
    PicamConstraintSeverity      severity;
    pibln                        empty_set;
    PicamRoisConstraintRulesMask rules;
    piint                        maximum_roi_count;
    PicamRangeConstraint         x_constraint;
    PicamRangeConstraint         width_constraint;
    const piint*                 x_binning_limits_array;
    piint                        x_binning_limits_count;
    PicamRangeConstraint         y_constraint;
    PicamRangeConstraint         height_constraint;
    const piint*                 y_binning_limits_array;
    piint                        y_binning_limits_count;
} PicamRoisConstraint;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyRoisConstraints(
    const PicamRoisConstraint* constraint_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterRoisConstraint(
    PicamHandle                 camera,
    PicamParameter              parameter,
    PicamConstraintCategory     category,
    const PicamRoisConstraint** constraint ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Pulse --------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamPulseConstraint
{
    PicamConstraintScope         scope;
    PicamConstraintSeverity      severity;
    pibln                        empty_set;
    PicamRangeConstraint         delay_constraint;
    PicamRangeConstraint         width_constraint;
    piflt                        minimum_duration;
    piflt                        maximum_duration;
} PicamPulseConstraint;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyPulseConstraints(
    const PicamPulseConstraint* constraint_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterPulseConstraint(
    PicamHandle                  camera,
    PicamParameter               parameter,
    PicamConstraintCategory      category,
    const PicamPulseConstraint** constraint ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Camera Parameter Constraints - Custom Intensifier Modulation Sequence -----*/
/*----------------------------------------------------------------------------*/
typedef struct PicamModulationsConstraint
{
    PicamConstraintScope    scope;
    PicamConstraintSeverity severity;
    pibln                   empty_set;
    piint                   maximum_modulation_count;
    PicamRangeConstraint    duration_constraint;
    PicamRangeConstraint    frequency_constraint;
    PicamRangeConstraint    phase_constraint;
    PicamRangeConstraint    output_signal_frequency_constraint;
} PicamModulationsConstraint;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_DestroyModulationsConstraints(
    const PicamModulationsConstraint* constraint_array );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_GetParameterModulationsConstraint(
    PicamHandle                        camera,
    PicamParameter                     parameter,
    PicamConstraintCategory            category,
    const PicamModulationsConstraint** constraint ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/
/* Parameter Commitment ------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
PICAM_API Picam_AreParametersCommitted(
    PicamHandle camera,
    pibln*      committed );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_CommitParameters(
    PicamHandle            camera,
    const PicamParameter** failed_parameter_array,
    piint*                 failed_parameter_count ); /* ALLOCATES */
/*----------------------------------------------------------------------------*/

/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/* Camera Data Acquisition                                                    */
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/
/******************************************************************************/

/*----------------------------------------------------------------------------*/
/* Acquisition Control -------------------------------------------------------*/
/*----------------------------------------------------------------------------*/
typedef struct PicamAvailableData
{
    void* initial_readout;
    pi64s readout_count;
} PicamAvailableData;
"""
class PicamAvailableData(ctypes.Structure):
    _fields_ = [("initial_readout",ctypes.c_void_p),
                ("readout_count",pi64s)
                ]
"""
/*----------------------------------------------------------------------------*/
typedef enum PicamAcquisitionErrorsMask
{
    PicamAcquisitionErrorsMask_None           = 0x0,
    PicamAcquisitionErrorsMask_DataLost       = 0x1,
    PicamAcquisitionErrorsMask_ConnectionLost = 0x2
} PicamAcquisitionErrorsMask; /* (0x4) */
"""
PicamAcquisitionErrorsMask_num = dict(
    PicamAcquisitionErrorsMask_None           = 0x0,
    PicamAcquisitionErrorsMask_DataLost       = 0x1,
    PicamAcquisitionErrorsMask_ConnectionLost = 0x2                                     
                                      )
PicamAcquisitionErrorsMask = dict()
for k,v in PicamAcquisitionErrorsMask.items():
    PicamAcquisitionErrorsMask[v] = k
    
"""
/*----------------------------------------------------------------------------*/
PICAM_API Picam_Acquire(
    PicamHandle                 camera,
    pi64s                       readout_count,
    piint                       readout_time_out,
    PicamAvailableData*         available,
    PicamAcquisitionErrorsMask* errors );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_StartAcquisition( PicamHandle camera );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_StopAcquisition( PicamHandle camera );
/*----------------------------------------------------------------------------*/
PICAM_API Picam_IsAcquisitionRunning(
    PicamHandle camera,
    pibln*      running );
/*----------------------------------------------------------------------------*/
typedef struct PicamAcquisitionStatus
{
    pibln                      running;
    PicamAcquisitionErrorsMask errors;
    piflt                      readout_rate;
} PicamAcquisitionStatus;
/*----------------------------------------------------------------------------*/
PICAM_API Picam_WaitForAcquisitionUpdate(
    PicamHandle             camera,
    piint                   readout_time_out,
    PicamAvailableData*     available,
    PicamAcquisitionStatus* status );
/*----------------------------------------------------------------------------*/

/******************************************************************************/
/* C++ Epilogue                                                               */
/******************************************************************************/
#if defined __cplusplus && !defined PICAM_EXPORTS
    }   /* end extern "C" */
#endif

#endif
"""