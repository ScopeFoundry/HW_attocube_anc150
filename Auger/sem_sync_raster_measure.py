'''
Created on Feb 4, 2015

@author: Hao Wu
ESB 2016-07-19

'''

from ScopeFoundry.scanning.base_cartesian_scan import BaseCartesian2DScan
from SEM.sem_equipment.rate_converter import RateConverter
import numpy as np

class SemSyncRasterScan(BaseCartesian2DScan):

    name = "sem_sync_raster_scan"
    
    def setup(self):
        self.h_unit = self.v_unit = "V"
        self.h_limits = self.v_limits = (-10,10)
        
        BaseCartesian2DScan.setup(self)
                
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        self.scan_mode = self.add_logged_quantity("scan_mode", dtype=str, 
                                                        ro=False,
                                                        initial='image',
                                                        choices=[('image','image'),('movie','movie')])

    
        self.recovery_time = self.add_logged_quantity("recovery_time", dtype=float, 
                                                    ro=True,
                                                    initial=0.07)
        
        
        self.scanDAQ = self.app.hardware['SemSyncRasterDAQ']
        
        self.scan_on=False
        
        if hasattr(self.gui,'sem_remcon'):
            self.sem_remcon=self.app.sem_remcon
        

    def run(self):
        self.current_scan_index = 0,0,0
        # Compute data arrays
        print "computing scan arrays"
        self.compute_scan_arrays()
        print "computing scan arrays... done"
        
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
               
        ms_per_frame = self.Npixels*0.01 # FIXME 

        self.scanDAQ.connect()         

        
        try:
            print("scan started")
            if self.scan_mode.val=="image":
                print("Acquiring Image")
                #self.scanner.callback_mode.update_value('line')
                #if ms_per_frame>2e6:
                #    self.single_scan_callback()
                #else:
                self.current_scan_index = 0,0,0
                while not self.interrupt_measurement_called:
                    self.single_scan_regular()
                
            elif self.scan_mode.val=="movie":
                print("Acquring Movie")
                self.continous_scan()
            print("scan done")
        finally:
            """        if self.scanner.auto_blanking.val:
                        if hasattr(self,"sem_remcon"):
                            if self.sem_remcon.connected.val:
                                self.sem_remcon.beam_blanking.update_value(1)
            """        
            self.scanDAQ.disconnect()         
        
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
    
    def single_scan_regular(self):
        #connect to SEM scanner module, which calculates the voltage output,
        #create detector channels and creates the scanning task
        self.scanDAQ.sync_mode.update_value('regular')
        self.scanDAQ.connect()
        #self.setup_imagedata("regular")
        # fix 
        self.scanDAQ.setup_io_with_data(self.scan_h_positions, -1*self.scan_v_positions)
        self.scanDAQ.sync_analog_io.start()            
        
        #self.images.read_all() -- old way everything hiding in image_display object

        self.ai_data = self.scanDAQ.read_ai_chans()
        
        # TODO read Counters
        #self.display_image_map[self.scan_index_array] = self.ai_data[0,:]
        self.display_image_map[0,:,:] = self.ai_data[:,1].reshape(self.settings['Nv'], self.settings['Nh'])
        
        # TODO save data
        
        self.scanDAQ.sync_analog_io.stop()
        #self.scanDAQ.sync_analog_io.close()
        
    def update_display(self):
        BaseCartesian2DScan.update_display(self)
        
    
