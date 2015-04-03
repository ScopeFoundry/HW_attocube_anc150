'''
Created on Feb 4, 2015

@author: NIuser
'''

from measurement_components.measurement import Measurement
import time
import numpy as np
import matplotlib.cm as cm

class SemRasterRepScan(Measurement):

    name = "sem_raster_rep_scan"
    
    def setup(self):        
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        
        self.continuous_scan = self.add_logged_quantity("continuous_scan", dtype=int, 
                                                        ro=False, 
                                                        initial=0, 
                                                        vmin=0, 
                                                        vmax=1, 
                                                        unit='',
                                                        choices=[('Off',0),('On',1)])
        self.save_file = self.add_logged_quantity("save_file", dtype=int, 
                                                        ro=False, 
                                                        initial=0, 
                                                        vmin=0, 
                                                        vmax=1, 
                                                        unit='',
                                                        choices=[('Off',0),('On',1)])
        self.scanner=self.gui.sem_raster_scanner
        
        #connect events
        self.gui.ui.sem_raster_repscan_start_pushButton.clicked.connect(self.start)
        self.gui.ui.sem_raster_repscan_stop_pushButton.clicked.connect(self.interrupt)
        
        self.save_file.connect_bidir_to_widget(self.gui.ui.save_file_comboBox)
        
    def setup_figure(self):
        self.fig = self.gui.add_figure('sem_raster', self.gui.ui.sem_raster_plot_widget)

    def _run(self):
        from datetime import datetime
        '''
        connect to the scanner hardware component which set scan parameters
        '''
        self.scanner.connect()

        '''
        image_io contains the classes needed for saving and loading data
        The data is in HDF5 format
        Collection class correspond to one data collection run,
        it create an HDF5 file and Collection.update(dict({'name':data_frame}))
        stores each frames into the HDF5 file
        '''
        from equipment.image_io import ChannelInfo
        from equipment.image_io import Collection
        '''
        Turning on Continuous scan
        '''
        self.continuous_scan.val=1
        '''
        If save file flag is on, start save file routine
        '''
        if self.save_file.val==1:
            '''
            ChannelInfo contains the name of channel, and the dimension info,
            it is used in setting up channels during the creating of
            a Collection object
            '''
            image_dimension=(self.points.val,self.lines.val)
            ch_infos=[ChannelInfo('voltage',image_dimension),ChannelInfo('counter',image_dimension)]
            
            t=datetime.now()
            '''
            a file is named by a time stamp
            '''
            tname='data/'+t.strftime('%Y-%m-%d-%H-%M-%S')
            self.collection=Collection(name=tname,
                                  create=True,
                                  initial_size=100,
                                  expansion_size=100,
                                  channel_infos=ch_infos)
            
            '''
            all configurations from the measurement and hardware components can be saved
            '''
            self.collection.save_measurement_component(self.dict_logged_quantity_val(self.logged_quantities), self.dict_logged_quantity_unit(self.logged_quantities))
            self.sem_remcon=self.gui.sem_remcon
            self.collection.save_hardware_component('sem_remcon', self.dict_logged_quantity_val(self.sem_remcon.logged_quantities), self.dict_logged_quantity_unit(self.sem_remcon.logged_quantities))
        
        
        while self.continuous_scan.val==1:
            if self.interrupt_measurement_called:
                break
            self.scanner.sync_analog_io.out_data(self.scanner.xy_raster_volts)
            self.scanner.sync_analog_io.start()
            self.adc_data = self.scanner.sync_analog_io.read_adc_buffer(timeout=10)
            self.ctr_data=[]
            for i in xrange(self.scanner.ctr_num):
                self.ctr_data.append(self.scanner.sync_analog_io.read_ctr_buffer_diff(i,timeout=10))
            
            '''
            obtain input signal, average copies of samples and reshape it for image display
            '''
            in1 = self.adc_data[::3]

            if self.scanner.sample_per_point.val>1:
                '''
                average signal if oversampling is on
                '''
                in1=in1.reshape((self.scanner.num_pixels,self.scanner.sample_per_point.val))
                in1= in1.mean(axis=1)
                for i in xrange(self.scanner.ctr_num):
                    self.ctr_data[i]=self.ctr_data[i].reshape((self.scanner.num_pixels,self.scanner.sample_per_point.val))
                    self.ctr_data[i]= self.ctr_data[i].mean(axis=1)

            in1 = in1.reshape(self.scanner.raster_gen.shape())
            for i in xrange(self.scanner.ctr_num):
                self.ctr_data[i] = self.ctr_data[i].reshape(self.scanner.raster_gen.shape())
            if self.save_file.val==1:
                '''
                store data in each channel
                '''
                self.collection.update({'voltage':in1,'counter':self.ctr_data[0]})
            self.sem_image=[]
            self.sem_image.append(in1)
            
            for i in xrange(self.scanner.ctr_num):
                self.sem_image.append(self.ctr_data[i])
                
            self.scanner.sync_analog_io.stop()
        
        self.scanner.disconnect()
        if self.save_file.val==1:
            self.collection.close()
        
    def update_display(self):        
        #print "updating figure"
        #self.fig.clf()
        
        if not hasattr(self,'ax'):
            self.ax = self.fig.add_subplot(221)
            
        if not hasattr(self, 'img'):
            self.img = self.ax.imshow(self.sem_image[0],cmap = cm.Greys_r)
            
        if not hasattr(self,'ax2'):
            self.ax2 = self.fig.add_subplot(223)
            
        if not hasattr(self, 'img2'):
            self.img2 = self.ax2.imshow(self.sem_image[1],cmap = cm.Greys_r)
        
        if not hasattr(self,'ax3'):
            self.ax3 = self.fig.add_subplot(224)
            
        if not hasattr(self, 'img3'):
            self.img3 = self.ax3.imshow(self.sem_image[2],cmap = cm.Greys_r)
            
        self.img.set_data(self.sem_image[0])
        self.img2.set_data(self.sem_image[1])
        self.img3.set_data(self.sem_image[2])
        
        self.fig.canvas.draw()
    
    def get_hardware_logged_quantity(self,hardware):
        return hardware.logged_quantities
    
    def list_hardware_components(self):
        return self.gui.hardware_components
    
    def dict_logged_quantity_val(self,logged_quantities):
        val_dict=dict()
        for name in self.logged_quantities:
            val_dict[name]=self.logged_quantities[name].val
        return val_dict
    
    def dict_logged_quantity_unit(self,logged_quantities):
        val_dict=dict()
        for name in self.logged_quantities:
            val_dict[name]=self.logged_quantities[name].unit
        return val_dict

# if __name__=='__main__':
#     from base_gui import BaseMicroscopeGUI
#    
#     scan=SemRasterRepScan(gui)
#     resp=scan.get_measurement_logged_quantity()
#     print(resp)