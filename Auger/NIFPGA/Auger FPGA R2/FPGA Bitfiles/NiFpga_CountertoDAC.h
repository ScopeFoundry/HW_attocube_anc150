/*
 * Generated with the FPGA Interface C API Generator 14.0.0
 * for NI-RIO 14.0.0 or later.
 */

#ifndef __NiFpga_CountertoDAC_h__
#define __NiFpga_CountertoDAC_h__

#ifndef NiFpga_Version
   #define NiFpga_Version 1400
#endif

#include "NiFpga.h"

/**
 * The filename of the FPGA bitfile.
 *
 * This is a #define to allow for string literal concatenation. For example:
 *
 *    static const char* const Bitfile = "C:\\" NiFpga_CountertoDAC_Bitfile;
 */
#define NiFpga_CountertoDAC_Bitfile "NiFpga_CountertoDAC.lvbitx"

/**
 * The signature of the FPGA bitfile.
 */
static const char* const NiFpga_CountertoDAC_Signature = "43998F2D6084B694AFF2B174B59D45C6";

typedef enum
{
   NiFpga_CountertoDAC_IndicatorBool_CtrOverflow = 0x813A,
   NiFpga_CountertoDAC_IndicatorBool_Triggered = 0x811A,
} NiFpga_CountertoDAC_IndicatorBool;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorI16_DAC1 = 0x8156,
   NiFpga_CountertoDAC_IndicatorI16_DAC2 = 0x8152,
} NiFpga_CountertoDAC_IndicatorI16;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorU16_loopelapsed = 0x814E,
} NiFpga_CountertoDAC_IndicatorU16;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorU32_BlocksTransfered = 0x8134,
   NiFpga_CountertoDAC_IndicatorU32_CtrElapsed = 0x8130,
} NiFpga_CountertoDAC_IndicatorU32;

typedef enum
{
   NiFpga_CountertoDAC_ControlBool_CtrFIFO = 0x813E,
   NiFpga_CountertoDAC_ControlBool_ExtTrigEnable = 0x8112,
   NiFpga_CountertoDAC_ControlBool_FIFOflag = 0x8116,
} NiFpga_CountertoDAC_ControlBool;

typedef enum
{
   NiFpga_CountertoDAC_ControlI16_Offset1 = 0x812A,
   NiFpga_CountertoDAC_ControlI16_Offset2 = 0x8126,
   NiFpga_CountertoDAC_ControlI16_Scale1 = 0x8122,
   NiFpga_CountertoDAC_ControlI16_Scale2 = 0x811E,
} NiFpga_CountertoDAC_ControlI16;

typedef enum
{
   NiFpga_CountertoDAC_ControlU32_Counterticks = 0x812C,
   NiFpga_CountertoDAC_ControlU32_Rate = 0x810C,
} NiFpga_CountertoDAC_ControlU32;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorArrayBool_InputsDIO810 = 0x8146,
} NiFpga_CountertoDAC_IndicatorArrayBool;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorArrayBoolSize_InputsDIO810 = 3,
} NiFpga_CountertoDAC_IndicatorArrayBoolSize;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorArrayU32_Counts = 0x8148,
} NiFpga_CountertoDAC_IndicatorArrayU32;

typedef enum
{
   NiFpga_CountertoDAC_IndicatorArrayU32Size_Counts = 8,
} NiFpga_CountertoDAC_IndicatorArrayU32Size;

typedef enum
{
   NiFpga_CountertoDAC_ControlArrayBool_Dac1add = 0x8166,
   NiFpga_CountertoDAC_ControlArrayBool_Dac1sub = 0x8162,
   NiFpga_CountertoDAC_ControlArrayBool_Dac2add = 0x815E,
   NiFpga_CountertoDAC_ControlArrayBool_Dac2sub = 0x815A,
   NiFpga_CountertoDAC_ControlArrayBool_OutputsDIO1214 = 0x8142,
} NiFpga_CountertoDAC_ControlArrayBool;

typedef enum
{
   NiFpga_CountertoDAC_ControlArrayBoolSize_Dac1add = 8,
   NiFpga_CountertoDAC_ControlArrayBoolSize_Dac1sub = 8,
   NiFpga_CountertoDAC_ControlArrayBoolSize_Dac2add = 8,
   NiFpga_CountertoDAC_ControlArrayBoolSize_Dac2sub = 8,
   NiFpga_CountertoDAC_ControlArrayBoolSize_OutputsDIO1214 = 4,
} NiFpga_CountertoDAC_ControlArrayBoolSize;

typedef enum
{
   NiFpga_CountertoDAC_TargetToHostFifoU32_CounterFIFO = 0,
} NiFpga_CountertoDAC_TargetToHostFifoU32;

#endif
