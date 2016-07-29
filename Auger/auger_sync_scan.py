from sem_sync_raster_measure import SemSyncRasterScan
import time
import numpy as np

class AugerSyncScan(SemSyncRasterScan):
    name = "AugerSyncScan"
    
    def single_scan_regular(self):
        #SemSyncRasterScan.single_scan_regular(self)
        t0 = time.time()
        #print self.name, "single_scan_regular"
        
        self.counter_dac_hc = self.app.hardware['Counter_DAC_FPGA_VI_HC']
        
        print "CtrOverflow before", self.counter_dac_hc.counter_dac.CtrOverflow()
        if self.counter_dac_hc.counter_dac.CtrOverflow():
            self.counter_dac_hc.settings['connected'] = False
            raise IOError("Counter Overflow, need to reset FPGA")
            #self.counter_dac_hc.connect()

        NUM_CHANS = self.counter_dac_hc.NUM_CHANS
        
        self.scanDAQ.sync_mode.update_value('regular')
        #self.scanDAQ.settings['ext_clock_enable'] = True
        self.scanDAQ.connect()
        self.scanDAQ.setup_io_with_data(self.scan_h_positions, -1*self.scan_v_positions)

        self.counter_dac_hc.settings['ext_trig_enable'] = False
        self.counter_dac_hc.settings['ext_trig_enable'] = True
        t0 = time.time()
        #print "before start"
        self.counter_dac_hc.engage_FIFO()
        time.sleep(0.010)
        self.scanDAQ.sync_analog_io.start()            
        
        #print "after start", time.time() - t0 
        #print "CtrOverflow after", self.counter_dac_hc.counter_dac.CtrOverflow()
        #self.counter_dac_hc.settings['ext_trig_enable'] = False

        self.auger_buf_list = []
        
        wait_time = 50.0/self.scanDAQ.settings['sample_rate']
        for i in range(self.Npixels/50):
            buf = self.counter_dac_hc.read_FIFO()
            #print "-->", buf.shape
            self.auger_buf_list.append(buf)
            time.sleep(wait_time)
            
        self.ai_data = self.scanDAQ.read_ai_chans()
        # TODO read Counters

        self.auger_buf_list.append(self.counter_dac_hc.read_FIFO())
        #self.counter_dac_hc.disengage_FIFO()
        #time.sleep(0.01)
        
        self.auger_buf = np.concatenate(self.auger_buf_list, axis=1)
        
        #self.display_image_map[self.scan_index_array] = self.ai_data[0,:]
        #self.display_image_map[0,:,:] = self.ai_data[:,1].reshape(self.settings['Nv'], self.settings['Nh'])
        #self.display_image_map[0,:,:] = self.auger_buf[:,:].sum(axis=0).reshape(self.settings['Nv'], self.settings['Nh'])
        #self.display_image_map[0,:,:] = self.auger_buf[:,:].sum(axis=0).reshape(self.settings['Nv'], self.settings['Nh'])
        
        # TODO save data
        
        self.scanDAQ.sync_analog_io.stop()
        #self.scanDAQ.sync_analog_io.close()
        
        #print self.name, "frame time", time.time() - t0, "num_pixels", self.Npixels
        _, depth = self.auger_buf.shape
        #if depth > 0:
        print self.auger_buf.shape
        #print self.auger_buf.sum(axis=0)
        
        #depth = 
        
        if depth > self.Npixels:
            depth = self.Npixels
            print "depth > px"
        
        filled_auger_buf = np.zeros(self.Npixels)
        print depth
        print filled_auger_buf.shape, self.auger_buf.shape
        #filled_auger_buf[0:depth] = self.auger_buf[0:7,-depth:].sum(axis=0)
        filled_auger_buf[0:depth] = np.bitwise_and(self.auger_buf[8,-depth:], 0x7FFFFFFF)
        time_info = np.bitwise_and(self.auger_buf[8,:], 0x7FFFFFFF)
        #filled_auger_buf = np.bitwise_and(self.auger_buf[8,:], 0x7FFFFFFF)
        
        print np.bitwise_and(self.auger_buf[8,:-depth], 0x7FFFFFFF)
        print filled_auger_buf[:5]
        print filled_auger_buf[-5:]
        print np.sum(filled_auger_buf > 9000)
        print time_info[time_info > 5000]
                
        self.display_image_map[0,:,:] = filled_auger_buf.reshape(self.settings['Nv'], self.settings['Nh'])
        #self.display_image_map[0,0,0] = 0
        #self.display_image_map[0,:,:] = self.ai_data[:,1].reshape(self.settings['Nv'], self.settings['Nh'])
        
        