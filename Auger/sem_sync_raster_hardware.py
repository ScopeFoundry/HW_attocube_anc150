'''
Created on Feb 4, 2015

@author: Hao Wu
Rewritten 2016-07-11 ESB
Rewritten 2017-01-27 ESB

'''
from ScopeFoundry import HardwareComponent
try:
    from SEM.sem_equipment.raster_generator import RasterGenerator
    from SEM.sem_equipment.rate_converter import RateConverter

    from ScopeFoundryHW.ni_daq import NI_SyncTaskSet
    from ScopeFoundryHW.ni_daq.NI_CallBack import SyncCallBack
except Exception as err:
    print("could not load modules needed for SemSyncRasterDAQ:", err)

import numpy as np

class SemSyncRasterDAQ(HardwareComponent):
    
    name = 'SemSyncRasterDAQ'
    
    def setup(self):
        self.display_update_period = 0.050 #seconds

        # Create logged quantities, set limits and defaults
        #    several of these do not work as of 2/8/17
        
        self.sync_mode=self.add_logged_quantity('sync_mode',initial='regular',
                                                dtype=str)
            #FIX sync_mode = callback  broken
        
        self.callback_mode = self.add_logged_quantity("callback_mode", dtype=str, 
                                                    ro=False,
                                                    initial='line',
                                                    choices=[('Slow','line'),('Fast','block')])
            #FIX callback mode disabled
        

        self.scan_voltage = self.add_logged_quantity("scan_voltage", dtype=float, 
                                                    ro=False, 
                                                    initial=10.0, 
                                                    vmin=0, 
                                                    vmax=50.0,
                                                    unit='V')
            #FIX this does not appear to do anything
        
        self.sample_rate = self.add_logged_quantity("sample_rate", dtype=float, 
                                                    ro=False, 
                                                    initial=2e6, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz',
                                                    si=True)
        
        self.output_rate = self.add_logged_quantity("output_rate", dtype=float, 
                                                    ro=True, 
                                                    initial=5e5, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz')
        
        self.sample_per_point = self.add_logged_quantity("sample_per_point", dtype=int, 
                                                    ro=False, 
                                                    initial=1, 
                                                    vmin=1, 
                                                    vmax=1e10,
                                                    unit='samples')
        
#         self.ms_per_unit=self.add_logged_quantity("ms_per_unit",dtype=float,
#                                                   ro=False,
#                                                   initial=3,
#                                                   vmin=0.0005,
#                                                   vmax=1e10)
#         
#         self.unit_of_rate=self.add_logged_quantity("unit_of_rate",dtype=int,
#                                                    ro=False,
#                                                    initial=1,
#                                                    choices=[('ms/pixel',0),('ms/line',1),('ms/frame',2)])
#         
        self.output_channel_addresses= self.add_logged_quantity("output_channel_addresses",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ao0:1')
        
        self.input_channel_addresses= self.add_logged_quantity("input_channel_addresses",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ai1')        
        
        self.input_channel_names= self.add_logged_quantity("input_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='SE')
        
        self.counter_channel_addresses= self.add_logged_quantity("counter_channel_addresses",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ctr0,X-6363/ctr1')

        self.counter_channel_names= self.add_logged_quantity("counter_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='PMT,PMT2')
        
        self.counter_channel_terminals= self.add_logged_quantity("counter_channel_terminals",dtype=str,
                                                        ro=False,
                                                        initial='PFI0,PFI12')
        
        
        self.counter_unit=self.add_logged_quantity("counter_unit",dtype=str,
                                                        ro=False,
                                                        initial='count',
                                                        choices=[('count','count'),('Hz','Hz')])
        
#             #FIX implement in SemSyncRasterScan
#         self.auto_blanking=self.add_logged_quantity('auto_blanking', initial=True,
#                                                    dtype=bool,
#                                                    ro=False)
#         
        self.timeout= self.add_logged_quantity("timeout",dtype=float,
                                               ro=False,
                                               initial=999,
                                               vmin=1,
                                               vmax=1e5,
                                               unit='s')
        
        self.ext_clock_enable = self.add_logged_quantity("ext_clock_enable", dtype=bool, initial=False)
        self.ext_clock_source = self.add_logged_quantity("ext_clock_source", dtype=str, initial="/X-6368/PFI0")
        
             #parameters that cannot change during image acquisition
        self.lq_lock_on_connect = ['output_channel_addresses', 'input_channel_addresses',
                                    'counter_channel_addresses', 'counter_channel_terminals',
                                    'ext_clock_source']
       
        
    def connect(self):        
        if self.debug_mode.val: self.log.debug( "connecting to {}".format(self.name))
        

        #self.remcon=self.app.hardware['sem_remcon']        
        
#         self.scan_voltage.update_value(10.0)
        
        # lock logged quantities during connection
        for lqname in self.lq_lock_on_connect:
            lq = self.settings.get_lq(lqname)
            lq.change_readonly(True)

        #setup tasks
        if self.sync_mode.val=='regular':
            if self.settings['ext_clock_enable']:
                clock_source = self.settings['ext_clock_source']
            else:
                clock_source = "" 
            self.sync_analog_io = NI_SyncTaskSet(out_chan  = self.output_channel_addresses.val,
                                       in_chan   = self.input_channel_addresses.val,
                                       ctr_chans = self.counter_channel_addresses.val.split(','),
                                       ctr_terms = self.counter_channel_terminals.val.split(','),
                                       clock_source = clock_source,
                                       trigger_output_term = "/X-6368/PXI_Trig0",
                                       )
            # FIX this is broken
        elif self.sync_mode.val=='callback':
            self.sync_analog_io= SyncCallBack(self.output_channel_addresses.val,self.input_channel_addresses.val,self.counter_channel_addresses.val.split(','),self.counter_channel_terminals.val.split(','))
      
        self.ctr_num=2
        
        #from sample per point and sample rate, calculate the output(scan rate)
        #self.output_rate.update_value(self.sample_rate.val/self.sample_per_point.val)
        
        self.adc_chan_count  = self.sync_analog_io.get_adc_chan_count()
        
        #self.setup_io()

    def disconnect(self):
        
        for lqname in self.lq_lock_on_connect:
            lq = self.settings.get_lq(lqname)
            lq.change_readonly(False)

        #disconnect logged quantities from hardware
        for lq in self.settings.as_dict().values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None

        #disconnect hardware
        if hasattr(self, "sync_analog_io"):
            self.sync_analog_io.stop()
            self.sync_analog_io.close()
        
            # clean up hardware object
            del self.sync_analog_io

       
    def setup_io_with_data(self, X, Y):
        assert len(X) == len(Y)        
        self.num_pixels = len(X)
        self.num_samples = int(self.num_pixels *self.sample_per_point.val)
        self.pixel_time = self.sample_per_point.val / self.sample_rate.val        
        self.timeout.update_value(1.5 * self.pixel_time * self.num_pixels  )            
        self.output_rate.update_value(self.sample_rate.val/self.sample_per_point.val)
         
        if self.sync_mode.val=='regular':
            finite = True
        else: # callback (hao version)
            finite = False
        
        self.sync_analog_io.setup(rate_out = self.output_rate.val,
                                      count_out = self.num_pixels, 
                                      rate_in = self.sample_rate.val,
                                      count_in = self.num_samples, 
                                      #pad = ?,
                                      is_finite=finite)
        
        self.XY = self.interleave_xy_arrays(X, Y)                
        self.sync_analog_io.write_output_data_to_buffer(self.XY)
        
    def interleave_xy_arrays(self, X, Y):
        """take 1D X and Y arrays to create a flat interleaved XY array
        of the form [x0, y0, x1, y1, .... xN, yN]
        """
        assert len(X) == len(Y)
        N = len(X)
        XY = np.zeros(2*N, dtype=float)
        XY[0::2] = X
        XY[1::2] = Y
        return XY       
          
   
    def single_scan_data_block(self):
        self.ai_data = self.read_ai_chans()
            #handle oversampled ADC data
        self.ai_data =\
            self.ai_data.reshape(-1,self.sample_per_point.val,self.adc_chan_count)
        self.ai_data = self.ai_data.mean(axis=1)
        
        self.sync_analog_io.stop()
        #self.scanDAQ.sync_analog_io.close()
        return self.ai_data

        
    def read_ai_buffer(self):
        # interleaved buffer
        return self.sync_analog_io.read_adc_buffer(timeout=self.timeout.val)
    
    def read_ai_chans(self):
        return self.sync_analog_io.read_adc_buffer_reshaped(timeout=self.timeout.val)
    
    def read_ai_chan_pixels(self, n_pixels):
        # Grabs n_pixels worth of multi-channel, multi-sample 
        # data shaped as (n_pixels, n_chan, n_samp)
        n_samples = int(n_pixels * self.sample_per_point.val)
        buf = self.sync_analog_io.read_adc_buffer(count = n_samples, timeout=self.timeout.val)
        print('read_ai_chan_pixels', n_pixels, self.adc_chan_count, n_samples, buf.shape)

        return buf.reshape(n_pixels, self.sample_per_point.val, self.adc_chan_count).swapaxes(1,2)
        
    
    def read_counter_buffer(self, i):
        return self.sync_analog_io.read_ctr_buffer_diff(i, timeout=self.timeout.val)

    def start(self):
        self.sync_analog_io.start()
        
    def stop(self):
        self.sync_analog_io.stop()

    #def read_counters(self):
    
    


    #replaced by block graphics update 2/9/17
    def single_scan_regular(self, X_pos, Y_pos):
        #connect to SEM scanner module, which calculates the voltage output,
        #create detector channels and creates the scanning task
            #overrides lq to force "regular" mode

        self.setup_io_with_data(X_pos, Y_pos)
        self.sync_analog_io.start()            
        
        #self.images.read_all() -- old way everything hiding in image_display object

        self.ai_data = self.read_ai_chans()
            #handle oversampled ADC data
        self.ai_data =\
            self.ai_data.reshape(-1,self.sample_per_point.val,self.sync_analog_io.get_adc_chan_count())
        self.ai_data = self.ai_data.mean(axis=1)
        
        self.sync_analog_io.stop()
        #self.scanDAQ.sync_analog_io.close()
        return self.ai_data

        