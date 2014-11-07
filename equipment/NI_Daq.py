'''
Created on Aug 22, 2014

@author: Frank Ogletree
'''
from __future__ import division
import numpy as np
import PyDAQmx as mx

class NamedTask(mx.Task):
    ''' replaces __init__ with one that accepts a name for the task, otherwise identical to PyDaqmx task
        override PyDAQmx definition, which does not support named tasks
        no special chars in names, space OK
    '''
    def __init__(self, name= ''):
        self.taskHandle = mx.TaskHandle(0)
        mx.DAQmxCreateTask(name, mx.byref(self.taskHandle))

class NI(object):
    '''
    class to wrap National Instruments tasks using DAQmx drivers
    '''
    def __init__(self, name = '' ):
        '''
        Constructor
        '''
        self._error_list = []
        self._channel = self._task_name = self._mode = ''
        self._chan_count = self._rate = 0
        self.make_task( name )
    
    def make_task(self, name = '' ):
        ''' creates a [named] task, should not fail if DAQmx present'''
        self._task_name = name
        try:
            self.task = NamedTask(name)        
        except mx.DAQError as err:
            self.error( err )
            self.task = None               
        
    def error(self, err ):
            self._error_list.append(err)
            print 'Error calling "{}": {}'.format( err.fname, err.mess )

    def stop(self):
        try:
            self.task.StopTask()
        except mx.DAQError as err:
            self.error(err)
        
    def start(self):
        try:
            self.task.StartTask()
        except mx.DAQError as err:
            self.error(err)
    
    def clear(self):
        try:
            self.task.ClearTask()
        except mx.DAQError as err:
            self.error(err)
        finally:
            self.task = None
    def unreserve(self):
        ''' releases resources for other tasks to use without destroying task'''
        try:
            self.task.TaskControl(mx.DAQmx_Val_Task_Unreserve)
        except mx.DAQError as err:
            self.error(err)
            
    def ready(self):
        ''' validates params, reserves resources, ready to start'''
        try:
            self.task.TaskControl(mx.DAQmx_Val_Task_Commit)
        except mx.DAQError as err:
            self.error(err)
        
    def is_done(self):
        ''' checks for task done'''
        status = mx.bool32(0)
        try:
            self.task.GetTaskComplete( mx.byref(status));
        except mx.DAQError as err:
            self.error(err)
        if status.value:
            return True
        else:
            return False
        
    def get_rate(self):
        return self._rate
    
    def get_chan_count(self):
        return self._chan_count
    
    def wait(self, timeout = 10.0 ):
        try:
            self.task.WaitUntilTaskDone( timeout)
        except mx.DAQError as err:
            self.error(err)        
    
    def get_devices(self):
        '''
        polls for installed NI devices
        '''
        buffSize = 2048
        buff = mx.create_string_buffer( buffSize )
        try:
            mx.DAQmxGetSysDevNames( buff, buffSize );
        except mx.DAQError as err:
            self.error( err )
        dev_list = buff.value.split(',')
        for i in range(len(dev_list)):
            dev_list[i] = dev_list[i].strip()
        self._device_list = dev_list       
        #mx.DAQmxGetDevAIPhysicalChans( AIdev, chanList, buffSize )
    
class Adc(NI):
    '''
    Analog to digital input task, inherits from abstract NI task
    '''
    def __init__(self, channel, range = 10.0, name = '' ):
        ''' creates ADC task'''
        NI.__init__(self, name)       
        if self.task:
            self.set_channel(channel, range)
            
    def set_channel(self, channel, adc_range = 10.0 ):
        ''' adds input channel[s] to existing task, tries voltage range +/- 1, 2, 5, 10'''
        #  could use GetTaskDevices followed by GetDevAIVoltageRngs to validate max volts
        #  also can check for simultaneous, max single, max multi rates
        self._channel = channel
        self._input_range = min( abs(adc_range), 10.0 ) #error if range exceeds device maximum
        self._sample_count = 0
        adc_max = mx.float64(  self._input_range )
        adc_min = mx.float64( -self._input_range )

        try:                
            #int32 CreateAIVoltageChan( const char physicalChannel[], const char nameToAssignToChannel[], 
            #    int32 terminalConfig, float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
            self.task.CreateAIVoltageChan(self._channel, '', mx.DAQmx_Val_Cfg_Default,
                                          adc_min, adc_max, mx.DAQmx_Val_Volts, '')            
            chan_count = mx.uInt32(0) 
            self.task.GetTaskNumChans(mx.byref(chan_count))
            self._chan_count = chan_count.value
            self._mode = 'single'   #until buffer created
        except mx.DAQError as err:
            self._chan_count = 0
            self.error(err)
            
    def set_rate(self, rate = 1e4, count = 1000, finite = True):
        """
        Input buffer
            In continuous mode, count determines per-channel buffer size only if
                count EXCEEDS default buffer (1 MS over 1 MHz, 100 kS over 10 kHz, 10 kS over 100 Hz, 1 kS <= 100 Hz
                unless buffer explicitly set by DAQmxCfgInputBuffer()

            In finite mode, buffer size determined by count
         """
        if finite:
            adc_mode = mx.int32(mx.DAQmx_Val_FiniteSamps)
        else:
            adc_mode = mx.int32(mx.DAQmx_Val_ContSamps)
        adc_rate = mx.float64(rate)   #override python type
        adc_count = mx.uInt64(int(count))
        
        self.stop() #make sure task not running, 
        #  CfgSampClkTiming ( const char source[], float64 rate, int32 activeEdge, 
        #                        int32 sampleMode, uInt64 sampsPerChan );
        #  default clock source is subsystem acquisition clock
        try:                 
            self.task.CfgSampClkTiming("", adc_rate, mx.DAQmx_Val_Rising, adc_mode, adc_count) 
            adc_rate = mx.float64(0)
            #exact rate depends on hardware timer properties, may be slightly different from requested rate
            self.task.GetSampClkRate(mx.byref(adc_rate));
            self._rate = adc_rate.value
            self._count = count
            self._mode = 'buffered'
        except mx.DAQError as err:
            self.error(err)
            self._rate = 0
            
    def set_single(self):
        ''' single-value [multi channel] input, no clock or buffer
                   
            For unbuffered input (one sample per channel no timing or clock),
            if task STARTed BEFORE reading, in tight loop overhead between consecutive reads ~ 36 us with some jitter
                task remains in RUN, must be STOPed or cleared to modify
            if task is COMMITted  before reading, overhead ~ 116 us 
                (implicit transition back to COMMIT instead of staying in RUNNING)
            if task is STOPed before reading, requiring START read STOP overhead 4 ms
         '''
        if self._mode != 'single':
            self.clear()    #delete old task
            self.make_task(self._task_name)
            self.set_channel(self._channel, self._input_range)
            self._mode = 'single'
            
    def get(self):
        ''' reads one sample per channel in immediate (non buffered) mode, fastest if task pre-started'''
        data = np.zeros(self._chan_count, dtype = np.float64 )
        if self._mode != 'single':
            self.set_single()
            self.start()
        read_size = mx.uInt32(self._chan_count)
        read_count = mx.int32(0)
        timeout = mx.float64( 1.0 )
        try:
            # ReadAnalogF64( int32 numSampsPerChan, float64 timeout, bool32 fillMode, 
            #    float64 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
            self.task.ReadAnalogF64(1, timeout, mx.DAQmx_Val_GroupByScanNumber, 
                                  data, read_size, mx.byref(read_count), None)
        except mx.DAQError as err:
            self.error(err)
#        print "samples {} written {}".format( self._sample_count, writeCount.value)
        assert read_count.value == 1, \
            "sample count {} transfer count {}".format( 1, read_count.value )
        return data
              
    def read_buffer(self, count = 0, timeout = 1.0):
        ''' reads block of input data, defaults to block size from set_rate()
            for now allocates data buffer, possible performace hit
            in continuous mode, reads all samples available up to block_size
            in finite mode, waits for samples to be available, up to smaller of block_size or
                _chan_cout * _count
                
            for now return interspersed array, latter may reshape into 
        '''
        if count == 0:
            count = self._count
        block_size = count * self._chan_count
        data = np.zeros(block_size, dtype = np.float64)
        read_size = mx.uInt32(block_size)
        read_count = mx.int32(0)    #returns samples per chan read
        adc_timeout = mx.float64( timeout )
        try:
            # ReadAnalogF64( int32 numSampsPerChan, float64 timeout, bool32 fillMode, 
            #    float64 readArray[], uInt32 arraySizeInSamps, int32 *sampsPerChanRead, bool32 *reserved);
            self.task.ReadAnalogF64(-1, adc_timeout, mx.DAQmx_Val_GroupByScanNumber, 
                                  data, read_size, mx.byref(read_count), None)
        except mx.DAQError as err:
            self.error(err)
            #not sure how to handle actual samples read, resize array??
        if read_count.value < count:
            print 'requested {} values for {} channels, only {} read'.format( count, self._chan_count, read_count.value)
#        print "samples {} written {}".format( self._sample_count, writeCount.value)
#        assert read_count.value == 1, \
#           "sample count {} transfer count {}".format( 1, read_count.value )
        return data
              
            
class Dac(NI):
    '''
    Digital-to-Analog output task, inherits from abstract NI task
    '''
    def __init__(self, channel, name = '' ):
        ''' creates DAC task'''
        NI.__init__(self, name)       
        if self.task:
            self.set_channel(channel)
            
    def set_channel(self, channel ):
        ''' adds output channel[s] to existing task, always voltage range +/- 10 no scaling'''
        self._channel = channel
        self._sample_count = 0
        try:                
            # CreateAOVoltageChan ( const char physicalChannel[], const char nameToAssignToChannel[], 
            #    float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
            self.task.CreateAOVoltageChan(self._channel, '', -10.0, +10.0, mx.DAQmx_Val_Volts, '')
            
            chan_count = mx.uInt32(0) 
            self.task.GetTaskNumChans(mx.byref(chan_count))
            self._chan_count = chan_count.value
            self._mode = 'single'   #until buffer created
        except mx.DAQError as err:
            self._chan_count = 0
            self.error(err)
            
    def set_rate(self, rate = 1e4, count = 1000, finite = True):
        """
        Output buffer size determined by amount of data written, unless explicitly set by DAQmxCfgOutputBuffer()
        
        In Finite output mode, count is samples per channel to transfer on Start()
               if count > buffer size, output loops over buffer
               if count < buffer size, partial output, next start resumes from this point in buffer
        waiting for finite task to complete then restarting task has > 1 ms overhead, unclear why,
            overhead can fluctuate by 1.00 ms amounts. stupid old c clock??
        
        In Cont output mode, count is not used, output loops over buffer until stopped
            restarts at beginning of buffer
            stop/restart also has 2 ms overhead

        For unbuffered output (one sample per channel no timing or clock) with autostart enabled,
            if task STARTed BEFORE writing, in tight loop overhead between consecutive writes 18 us with some jitter
            if task is COMMITted  before writing, overhead 40 us 
                (implicit transition back to COMMIT instead of staying in RUNNING)
         """
        if finite:
            dac_mode = mx.int32(mx.DAQmx_Val_FiniteSamps)
        else:
            dac_mode = mx.int32(mx.DAQmx_Val_ContSamps)
        #  CfgSampClkTiming ( const char source[], float64 rate, int32 activeEdge, 
        #                        int32 sampleMode, uInt64 sampsPerChan );
        #  default clock source is subsystem acquisition clock
        try:                 
            dac_rate = mx.float64(rate)   #override python type
            dac_count = mx.uInt64(int(count))
            self.stop() #make sure task not running, 
            self.task.CfgSampClkTiming("", dac_rate, mx.DAQmx_Val_Rising, dac_mode, dac_count) 
            dac_rate = mx.float64(0)
            #exact rate depends on hardware timer properties, may be slightly different from requested rate
            self.task.GetSampClkRate(mx.byref(dac_rate));
            self._rate = dac_rate.value
            self._mode = 'buffered'
        except mx.DAQError as err:
            self.error(err)
            self._rate = 0
            
    def set_single(self):
        ''' single-value [multi channel] output, no clock or buffer
        
        For unbuffered output (one sample per channel no timing or clock) with autostart enabled,
            if task STARTed BEFORE writing, in tight loop overhead between consecutive writes 21 us with some jitter
                (no implicit mode transition)
            if task is COMMITted  before writing, overhead 40 us 
                (implicit transition back to COMMIT instead of staying in RUNNING)
            if task stopped, autostart takes ~ 5 ms per write
                (implicit start stop)
                
        No clean way to change from buffered to single point output without creating new task
         '''
        if self._mode != 'single':
            self.clear()    #delete old task
            self.make_task(self._task_name)
            self.set_channel(self._channel)
            self._mode = 'single'
              
    def load_buffer(self, data, auto = False ):
        '''  writes data to output buffer, array-like objects converted to np arrays if required
            data is interleved, i.e. x1, y1, x2, y2, x3, y3... for output on x and y
            implicitly COMMITs task, also starts if autostart is True
        '''
        if not isinstance( data, np.ndarray ) or data.dtype != np.float64:
            data = np.asarray(data, dtype = np.float64 )
        dac_samples = mx.int32( int(len(data) / self._chan_count) )
        self._sample_count = dac_samples.value
        writeCount = mx.int32(0)
        if auto:
            auto_start = mx.bool32(1)
        else:
            auto_start = mx.bool32(0)       
        try:
            #  WriteAnalogF64 (int32 numSampsPerChan, bool32 autoStart, float64 timeout, 
            #    bool32 dataLayout, float64 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved)
            #self.task.SetWriteRelativeTo(mx.DAQmx_Val_FirstSample)
            self.task.WriteAnalogF64(dac_samples, auto_start, 1.0, mx.DAQmx_Val_GroupByScanNumber, 
                                  data, mx.byref(writeCount), None)
        except mx.DAQError as err:
            self.error(err)
        #print "samples {} written {}".format( self._sample_count, writeCount.value)
        if writeCount.value != self._sample_count:
            "sample load count {} transfer count {}".format( self._sample_count, writeCount.value )

    def set(self, data):
        ''' writes one sample per channel in immediate (non buffered) mode, fastest if task pre-started'''
        if not isinstance( data, np.ndarray ) or data.dtype != np.float64:
            data = np.asarray(data, dtype = np.float64 )
        if self._mode != 'single':
            self.set_single()
            self.start()
        writeCount = mx.int32(0)
        auto_start = mx.bool32(1)
        try:
            #  WriteAnalogF64 (int32 numSampsPerChan, bool32 autoStart, float64 timeout, 
            #    bool32 dataLayout, float64 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved)
            self.task.WriteAnalogF64(1, auto_start, 1.0, mx.DAQmx_Val_GroupByChannel, 
                                  data, mx.byref(writeCount), None)
        except mx.DAQError as err:
            self.error(err)
#        print "samples {} written {}".format( self._sample_count, writeCount.value)
        assert writeCount.value == 1, \
            "sample count {} transfer count {}".format( 1, writeCount.value )

 #  various test code 
if __name__ == '__main__':
    import time
    import matplotlib.pyplot as plt
    
    dac = Dac('X-6368/ao0:1', 'SEM ext scan')
    data = np.arange(0, 10, 0.001, dtype = np.float64)
    
    adc = Adc('X-6368/ai2:3', 5, name = 'chan 2-3')
    test = 'dual'
    
    if test == 'dual':
        block = 1000
        rate = 1.0e5
        adc.set_rate(rate, block)   #finite read
        dac.set_rate(rate, len(data)/2, finite=True)
        out1 = np.sin( np.linspace( 0, 3*np.pi, block) )
        out2 = np.sin( np.linspace( 0 + np.pi/2, 3*np.pi+ np.pi/2, block) )
        buff_out = np.zeros( len(out1) + len(out2) )
        buff_out[::2] = out1
        buff_out[1::2] = out2
        
        plt.plot( out1 )
        plt.plot( out2 )
        plt.show()
        
        buffSize = 512
        buff = mx.create_string_buffer( buffSize )
        adc.task.GetNthTaskDevice(1, buff, buffSize)    #DAQmx name for input device
        trig_name = '/' + buff.value + '/ai/StartTrigger'
        print 'trigger name' , trig_name 
        dac.task.CfgDigEdgeStartTrig(trig_name, mx.DAQmx_Val_Rising)
        dac.load_buffer(buff_out)
        dac.start() #start dac first, waits for trigger from ADC to output data
        adc.start()

        x = adc.read_buffer()
        plt.subplot(211)
        plt.plot(x[::2])
        plt.plot(out1)
        plt.subplot(212)
        plt.plot(x[1::2])
        plt.plot(out2)
        plt.show()
        
    if test == 'read block':
        adc.set_rate( 1e5, 1000 )   #finite read
        x = adc.read_buffer()
        #plt.ion()
        plt.subplot(211)
        plt.plot(x[::2])
        plt.subplot(212)
        plt.plot(x[1::2])
        plt.show()
        #raw_input("press enter")
        for i in range(5):
            x = adc.read_buffer()
            plt.subplot(211)
            plt.plot(x[::2])
            plt.subplot(212)
            plt.plot(x[1::2])
            plt.show()      
            #raw_input("press enter")
            
    if test == 'read single':
        dac.set((0.5,-1))
        for i in range(16): 
            data = adc.get()
            print 'cycle {}, {}, {}'.format( i, data[0], data[1] )
        count = 10000
        #adc.set_single_read()
        adc.start()
        elapsed = time.clock()
        for i in range(count):
            adc.get()
        elapsed = time.clock() - elapsed
        print 'read {} single samples @ {} us per sample'.format( count, 1e6*elapsed/count )       
        
                
    if test == 'start stop' or test == 'all':
        dac.set_rate(2e6, len(data)/2, finite=True)
        dac.load_buffer(data)
        dac.ready()
        elapsed = time.clock()
        for i in range(16):
            dac.start()
            dac.wait()
            dac.stop()
        elapsed = time.clock() - elapsed
        print 'output buffer 16 times of {} 2-channel points in {} sec'.format( dac._sample_count, elapsed )
        
    if test == 'single' or test == 'all':
        data0 = np.zeros(2, dtype=np.float64)
        data1 = np.zeros(2, dtype=np.float64)
        data0[0] = data1[1] = 0.5
        count = 10000

        #dac.set_single()
        dac.start()
        elapsed = time.clock()
        for i in range(count):
            dac.set(data0)
            dac.set(data1)
        elapsed = time.clock() - elapsed
        print 'wrote {} single samples @ {} us per sample'.format( 2*count, 1e6*elapsed/(2*count) )
        
    if test == 'auto' or test == 'all':
        dac.set_rate(2e6, len(data)/2, finite=True)
        elapsed = time.clock()
        for i in range(16):
            dac.stop()
            dac.load_buffer(data, auto=True)   
            #dac.start()
            dac.wait()
            #dac.stop()
        elapsed = time.clock() - elapsed
        print 'wrote 16 autostart buffers of {} 2-channel points in {} sec'.format( dac._sample_count, elapsed )

print 'done'