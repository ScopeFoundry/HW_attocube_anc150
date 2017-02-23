'''

Hao Wu  Feb 4, 2015
ESB 2016-07-19
ESB 2017-02-17

'''

from ScopeFoundry.scanning import BaseRaster2DScan
import numpy as np
import time

class SemSyncRasterScan(BaseRaster2DScan):

    name = "sem_sync_raster_scan"
    
    def setup(self):
        self.h_unit = self.v_unit = "V"
        self.h_limits = self.v_limits = (-10,10)
        
        BaseRaster2DScan.setup(self)
        self.Nh.update_value(1000)
        self.Nv.update_value(1000)
                
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        
        #FIX what does this do dfo 2/10/17
        self.recovery_time = self.add_logged_quantity("recovery_time", dtype=float, 
                                                    ro=True,
                                                    initial=0.07)
        
        
        self.scanDAQ = self.app.hardware['SemSyncRasterDAQ']        
        self.scan_on=False
        
        if hasattr(self.app,'sem_remcon'):#FIX re-implement later
            self.sem_remcon=self.app.sem_remcon
        
    def run(self):
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
            self.pixel_index = 0
            self.current_scan_index = self.scan_index_array[0]
            
            #### old get full image while blocking measurement thread
            #self.ai_data = self.scanDAQ.single_scan_regular(self.scan_h_positions, -1*self.scan_v_positions)
            #self.display_image_map[0,:,:] = self.ai_data[:,1].reshape(self.settings['Nv'], self.settings['Nh'])       
            ####
            
            ##### load XY positions in to DAC
            self.scanDAQ.setup_io_with_data(self.scan_h_positions, -1*self.scan_v_positions)
            
            ###### compute pixel acquisition block size 
            # need at least one, and needs to an integer divisor of Npixels
            
            num_pixels_per_block = max(1, int(np.ceil(self.display_update_period / self.scanDAQ.pixel_time)))
            if num_pixels_per_block > self.Nh.val:
                num_pixels_per_block = self.Nh.val*np.ceil( num_pixels_per_block / self.Nh.val )
    
            num_blocks = int(max(1, np.floor(self.Npixels / num_pixels_per_block)))
            
            while self.Npixels % num_blocks != 0:
                num_blocks -= 1
                print("num_blocks", num_blocks)
        
            self.num_pixels_per_block = num_pixels_per_block = int(self.Npixels / num_blocks)
            print("num_pixels_per_block", num_pixels_per_block)
            
            ##### Data array
            self.adc_pixels = np.zeros((self.Npixels, self.scanDAQ.adc_chan_count), dtype=float)
            self.pixels_remaining = self.Npixels # in frame
            self.new_data_queue = []
            
            self.task_done = False
            
            # register callbacks
            self.scanDAQ.set_adc_n_pixel_callback(
                num_pixels_per_block, self.every_n_callback_func)
            self.scanDAQ.sync_analog_io.adc.set_done_callback(
                self.done_callback_func )
                        
            
            self.pre_scan_setup()

            #### Start scan daq 
            self.scanDAQ.start()
            
            #### Wait until done
            while not self.task_done and not self.interrupt_measurement_called:
                self.handle_new_data()
                time.sleep(self.display_update_period)
                            
            # TODO read Counters
            # FIX handle serpentine scans
            #self.display_image_map[self.scan_index_array] = self.ai_data[0,:]
            # TODO save data
            

        finally:
            # When done, stop tasks
            self.scanDAQ.stop()
            print("Npixels", self.Npixels, 'block size', self.num_pixels_per_block, 'num_blocks', num_blocks)
            print("pixels remaining:", self.pixels_remaining)
            print("blocks_per_sec",1.0/ (self.scanDAQ.pixel_time*num_pixels_per_block))
            print("frames_per_sec",1.0/ (self.scanDAQ.pixel_time*self.Npixels))

            self.post_scan_cleanup()

            pass
        
    
    def update_display(self):
        x = self.scan_index_array.T
        self.display_image_map[x[0], x[1], x[2]] = self.display_pixels

        kk,jj, ii = self.scan_index_array[self.pixel_index]
        self.current_stage_pos_arrow.setPos(self.h_array[ii], self.v_array[jj])
        BaseRaster2DScan.update_display(self)
    
    
    ##### Callback functions
    def every_n_callback_func(self):
        new_data = self.scanDAQ.read_ai_chan_pixels(
            self.num_pixels_per_block)
        self.new_data_queue.append(new_data)
        #self.on_new_data(new_data)
        return 0
    
    def done_callback_func(self, status):
        self.task_done = True
        print("done", status)
        return 0
    
    def handle_new_data(self):
        while len(self.new_data_queue) > 0:
            # grab the next available data chunk
            #print('new_data_queue' + "[===] "*len(self.new_data_queue))
            new_data = self.new_data_queue.pop(0)
            self.on_new_data(new_data)
            if self.interrupt_measurement_called:
                break

    
    def on_new_data(self, new_data):
        self.set_progress(100*self.pixel_index / self.Npixels )
        #print('callback block', self.pixel_index, new_data.shape, 'remaining px', self.Npixels - self.pixel_index)
        new_data = new_data.reshape(-1,  self.scanDAQ.samples_per_pixel.val, self.scanDAQ.adc_chan_count).swapaxes(1,2)
        ii = self.pixel_index
        dii = num_new_pixels = new_data.shape[0]
        # average over samples
        new_data = new_data.mean(axis=2)
        #print('new_data', new_data.shape)

        #stuff into pixel data array
        #print('ii', ii, 'dii', dii,  (self.adc_pixels[ii: ii + dii]).shape)
        self.adc_pixels[ii: ii + dii] = new_data
        
        DISPLAY_CHAN =1
        self.display_pixels = self.adc_pixels[:,DISPLAY_CHAN]
        """        DISPLAY_CHAN = 1                    
        x = self.scan_index_array[ii:ii+dii,:].T
        x1 = self.scan_index_array[(ii+dii+1)%self.Npixels,:]
        self.display_image_map[x[0], x[1], x[2]] = self.adc_pixels[ii:ii+dii, DISPLAY_CHAN]
        """
        #self.display_image_map[x1[0], x1[1], x1[2]] = 1000.0
        #print("self.display_image_map[ self.scan_index_array[ii:ii+dii] ]", self.display_image_map[ self.scan_index_array[ii:ii+dii] ].shape)
        #print("self.adc_pixels[ii:ii+dii, DISPLAY_CHAN]", self.adc_pixels[ii:ii+dii, DISPLAY_CHAN])
        
        self.current_scan_index = self.scan_index_array[self.pixel_index]

        self.pixel_index += num_new_pixels
        
        self.pixel_index %= self.Npixels
        
        self.pixels_remaining = self.Npixels - self.pixel_index

    def pre_scan_setup(self):
        pass

    def post_scan_cleanup(self):
        pass