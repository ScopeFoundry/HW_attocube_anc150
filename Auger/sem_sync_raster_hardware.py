'''
Created on Feb 4, 2015

@author: Hao Wu
Rewritten 2016-07-11 ESB

'''
from hardware_components import HardwareComponent
from ScopeFoundry.logged_quantity import LoggedQuantity
try:
    from SEM.sem_equipment.raster_generator import RasterGenerator
    from SEM.sem_equipment.rate_converter import RateConverter

    from equipment.NI_Daq import Sync
    from equipment.NI_CallBack import SyncCallBack
except Exception as err:
    print "could not load modules needed for AttoCubeECC100:", err

import numpy as np

class SemSyncRasterDAQ(HardwareComponent):
    
    name = 'SemSyncRasterDAQ'
    
    def setup(self):
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        self.sync_mode=self.add_logged_quantity('sync_mode',initial='callback',
                                                dtype=str)
        
        self.callback_mode = self.add_logged_quantity("callback_mode", dtype=str, 
                                                    ro=False,
                                                    initial='line',
                                                    choices=[('Slow','line'),('Fast','block')])
        

        self.scan_voltage = self.add_logged_quantity("scan_voltage", dtype=float, 
                                                    ro=False, 
                                                    initial=10.0, 
                                                    vmin=0, 
                                                    vmax=50.0,
                                                    unit='V')
        
        self.sample_rate = self.add_logged_quantity("sample_rate", dtype=float, 
                                                    ro=False, 
                                                    initial=2e6, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz')
        
        self.output_rate = self.add_logged_quantity("output_rate", dtype=float, 
                                                    ro=True, 
                                                    initial=5e5, 
                                                    vmin=1, 
                                                    vmax=2e6,
                                                    unit='Hz')
        
        self.sample_per_point = self.add_logged_quantity("sample_per_point", dtype=int, 
                                                    ro=True, 
                                                    initial=1, 
                                                    vmin=1, 
                                                    vmax=1e10,
                                                    unit='samples')
        
        self.ms_per_unit=self.add_logged_quantity("ms_per_unit",dtype=float,
                                                  ro=False,
                                                  initial=3,
                                                  vmin=0.0005,
                                                  vmax=1e10)
        
        self.unit_of_rate=self.add_logged_quantity("unit_of_rate",dtype=int,
                                                   ro=False,
                                                   initial=1,
                                                   choices=[('ms/pixel',0),('ms/line',1),('ms/frame',2)])
        
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
        
        self.auto_blanking=self.add_logged_quantity('auto_blanking', initial=True,
                                                   dtype=bool,
                                                   ro=False)
        
        self.timeout= self.add_logged_quantity("timeout",dtype=float,
                                               ro=False,
                                               initial=999,
                                               vmin=1,
                                               vmax=1e5) # unit?
        
        self.ext_clock_enable = self.add_logged_quantity("ext_clock_enable", dtype=bool, initial=False)
        self.ext_clock_source = self.add_logged_quantity("ext_clock_source", dtype=str, initial="/X-6368/PFI0")
        
        
        self.lq_lock_on_connect = ['output_channel_addresses', 'input_channel_addresses', 'counter_channel_addresses', 'counter_channel_terminals']
        
    def connect(self):        
        if self.debug_mode.val: print "connecting to {}".format(self.name)

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
            self.sync_analog_io = Sync(out_chan  = self.output_channel_addresses.val,
                                       in_chan   = self.input_channel_addresses.val,
                                       ctr_chans = self.counter_channel_addresses.val.split(','),
                                       ctr_terms = self.counter_channel_terminals.val.split(','),
                                       clock_source = clock_source,
                                       trigger_output_term = "/X-6368/PXI_Trig0",
                                       )
        elif self.sync_mode.val=='callback':
            self.sync_analog_io= SyncCallBack(self.output_channel_addresses.val,self.input_channel_addresses.val,self.counter_channel_addresses.val.split(','),self.counter_channel_terminals.val.split(','))
      
        self.ctr_num=2
        
        #from sample per point and sample rate, calculate the output(scan rate)
        self.output_rate.update_value(self.sample_rate.val/self.sample_per_point.val)
        
        
        #self.setup_io()

#     def setup_io(self):
#         #self.sync_analog_io.setup(rate_out=self.sample_rate.val, count_out=self.num_pixels, 
#         #                          rate_in=self.sample_rate.val, count_in=self.num_pixels )
#         if self.sync_mode.val=='regular':
#             self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.num_samples),is_finite=True)
#         else:
#             if self.callback_mode.val=='line':
#                 self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.points.val*self.sample_per_point.val),is_finite=False)
#             elif self.callback_mode.val=='block':
#                 self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.lines.val*self.points.val*self.sample_per_point.val),is_finite=False)


    def setup_io_with_data(self, X, Y):
        assert len(X) == len(Y)        
        self.num_pixels = len(X)
        self.num_samples = int(self.num_pixels *self.sample_per_point.val)        

        self.XY = self.interleave_xy_arrays(X, Y)
        
        if self.sync_mode.val=='regular':
            self.sync_analog_io.setup(rate_out = self.output_rate.val,
                                      count_out = self.num_pixels, 
                                      rate_in = self.sample_rate.val,
                                      count_in = self.num_samples, 
                                      #pad = ?,
                                      is_finite=True)
        else: # callback
            if self.callback_mode.val=='line':
                self.sync_analog_io.setup(rate_out = self.output_rate.val,
                                          count_out = self.num_pixels,
                                          rate_in = self.sample_rate.val,
                                          count_in = self.points.val*self.sample_per_point.val, # FIXME
                                          is_finite=False)
            elif self.callback_mode.val=='block':
                self.sync_analog_io.setup(rate_out = self.output_rate.val,
                                          count_out = self.num_pixels,
                                          rate_in = self.sample_rate.val,
                                          count_in = self.lines.val*self.points.val*self.sample_per_point.val,
                                          is_finite=False)
     
        self.sync_analog_io.write_output_data_to_buffer(self.XY)


    def disconnect(self):
        
        for lqname in self.lq_lock_on_connect:
            lq = self.settings.get_lq(lqname)
            lq.change_readonly(False)

        #disconnect logged quantities from hardware
        for lq in self.settings.as_dict().values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None

        #disconnect hardware
        try:
            self.sync_analog_io.stop()
        finally:
            pass
        
        try:
            self.sync_analog_io.close()
        finally:
            pass
        
        # clean up hardware object
        del self.sync_analog_io


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
        

    def write_XY_out_data_to_buffer(self, X, Y):
        self.XY = self.interleave_xy_arrays(X, Y)
        self.sync_analog_io.write_output_data_to_buffer(self.XY)
        
    def read_ai_buffer(self):
        # interleaved buffer
        return self.sync_analog_io.read_adc_buffer(timeout=self.timeout.val)
    
    def read_ai_chans(self):
        return self.sync_analog_io.read_adc_buffer_reshaped(timeout=self.timeout.val)
    
    def read_counter_buffer(self, i):
        return self.sync_analog_io.read_ctr_buffer_diff(i, timeout=self.timeout.val)

    #def read_counters(self):
    
# TODO handle buffer size:
"""self.ms_per_frame=self.rate_converter.ms_per_frame
        buff_size = self.Npixels*self.scanner.sample_per_point.val
        
        if buff_size>5.0e7:
            coeff=5.0e7/buff_size
            self.scanner.sample_rate.update_value(coeff*self.scanner.sample_rate.val)
            self.rate_converter=RateConverter(self.scanner.points.val,self.scanner.lines.val,self.scanner.sample_rate.val)

        self.scanner.sample_per_point.update_value(self.rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val))
"""

# TODO incorporate computation of rates
        