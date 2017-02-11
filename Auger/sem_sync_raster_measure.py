'''
Created on Feb 4, 2015

@author: Hao Wu
ESB 2016-07-19

'''

from ScopeFoundry.scanning.base_cartesian_scan import BaseCartesian2DScan
from SEM.sem_equipment.rate_converter import RateConverter
import numpy as np
import time

class SemSyncRasterScan(BaseCartesian2DScan):

    name = "sem_sync_raster_scan"
    
    def setup(self):
        self.h_unit = self.v_unit = "V"
        self.h_limits = self.v_limits = (-10,10)
        
        BaseCartesian2DScan.setup(self)
            
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
            #FIX what does this do dfo 2/10/17
        self.recovery_time = self.add_logged_quantity("recovery_time", dtype=float, 
                                                    ro=True,
                                                    initial=0.07)
        
        
        self.scanDAQ = self.app.hardware['SemSyncRasterDAQ']        
        self.scan_on=False
        
        if hasattr(self.gui,'sem_remcon'):#FIX re-implement later
            self.sem_remcon=self.app.sem_remcon
        

    def run(self):
        self.current_scan_index = 0,0,0
        # Compute data arrays
        self.log.debug( "computing scan arrays")
        self.compute_scan_arrays()
        self.log.debug( "computing scan arrays... done")
        
        self.initial_scan_setup_plotting = True
        
        self.display_image_map = np.zeros(self.scan_shape, dtype=float)
    
    
        
        """        #Connect to RemCon and turn on External Scan for SEM
                if hasattr(self,"sem_remcon"):
                    if self.sem_remcon.connected.val:
                        self.sem_remcon.remcon.write_external_scan(1)
                   
                #self.setup_scale()
                
                if self.scanner.auto_blanking.val:
                    if hasattr(self,"sem_remcon"):
                        if self.sem_remcon.connected.val:
                            self.sem_remcon.remcon.write_beam_blanking(0)
        """                    
                        
        # previously set samples_per_point in scanDAQ hardware
               
        # if hardware is not connected, connect it
        # we need to wait while the task is created before 
        # measurement thread continues
        if not self.scanDAQ.settings.connected:
            self.scanDAQ.settings.connected.update_value(True)         
            time.sleep(0.2)
        
 
        try:
            while not self.interrupt_measurement_called:
                self.pixel_index = 0
                
                #### old get full image while blocking measurement thread
                #self.ai_data = self.scanDAQ.single_scan_regular(self.scan_h_positions, -1*self.scan_v_positions)
                #self.display_image_map[0,:,:] = self.ai_data[:,1].reshape(self.settings['Nv'], self.settings['Nh'])       
                ####
                
                self.scanDAQ.setup_io_with_data(self.scan_h_positions, -1*self.scan_v_positions)
                #compute pixel display increment
                # need at least one
                num_pixels_per_block = max(1, int(np.round(0.010 / self.scanDAQ.pixel_time)))
                
                # Data array
                self.adc_pixels = np.zeros((self.Npixels, self.scanDAQ.adc_chan_count), dtype=float)
                
                self.scanDAQ.start()
                
                while self.pixel_index < self.Npixels:
                    print('block', self.pixel_index, num_pixels_per_block,  self.Npixels)
                    if self.interrupt_measurement_called:
                        break
                    remaining_pixels = self.Npixels - self.pixel_index
                    dii = acq_n_pixel = min(remaining_pixels, num_pixels_per_block)
                    
                    print('block', self.pixel_index, num_pixels_per_block,  self.Npixels, remaining_pixels)

                    
                    # read num_pixels_per_block
                    buf = self.scanDAQ.read_ai_chan_pixels(acq_n_pixel) # shape (n_pixels, n_chan, n_samp)
                    print(buf.shape)
                    # average over samples
                    buf = buf.mean(axis=2)
                    
                    
                    
                    #stuff into pixel data array
                    ii = self.pixel_index
                    self.adc_pixels[ii: ii + dii] = buf
                    
                    DISPLAY_CHAN = 1
                    self.display_image_map[ self.scan_index_array[ii:ii+dii] ] = self.adc_pixels[ii:ii+dii, DISPLAY_CHAN]
                    
                    self.pixel_index += acq_n_pixel 

                # TODO read Counters
                # FIX handle serpentine scans
                #self.display_image_map[self.scan_index_array] = self.ai_data[0,:]
                # TODO save data
                self.scanDAQ.stop()
        finally:
            pass
        
#     def fast_movie_scan(self,collection):
#         self.scanner.sync_mode.update_value('callback')
#         self.scanner.connect()
#         self.setup_imagedata('block_callback',collection=collection)    
# #         self.scan_check=ScanCheck(self.images,self,delay=0.05)
#         self.scanner.sync_analog_io.write_output_data_to_buffer(self.xy_raster_volts)
#         self.scanner.sync_analog_io.start()            
#             
#         self.scan_check.wait()
#             
#         self.scanner.sync_analog_io.stop()
#         
#         
#         self.scanner.sync_analog_io.close()
#         self.scan_on=False       
        
    def single_scan_callback(self):
        '''
        create ScanCheck object which update the scan progress and check to see if a scan has finished,
        delay is in seconds, and is the interval at which scan check runs
        '''
        #connect to SEM scanner module, which calculates the voltage output,
        #create detector channels and creates the scanning task
        self.scanner.sync_mode.update_value('callback')
        self.scanner.connect()
        self.setup_imagedata('callback')
#         self.scan_check=ScanCheck(self.images,self,delay=0.05) 

        self.scan_on=True
        
        self.scanner.write_XY_out_data_to_buffer(self.scan_h_positions, self.scan_y_positions)    

        self.scanner.sync_analog_io.start()            
            
        self.scan_check.wait()# ???
            
        self.scanner.sync_analog_io.stop()
        
        
        self.scanner.sync_analog_io.close()
        self.scan_on=False       
    
    def update_display(self):
        BaseCartesian2DScan.update_display(self)
        
    
