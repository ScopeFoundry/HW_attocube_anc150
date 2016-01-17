'''
Created on Feb 4, 2015

@author: Hao Wu
'''

from measurement_components.measurement import Measurement
import time
import numpy as np
import matplotlib.cm as cm
from equipment.image_display import ImageData
from PySide import QtGui, QtCore
from equipment.image_io import ChannelInfo
from equipment.image_io import Collection

class SemRasterSingleScan(Measurement):

    name = "sem_raster_single_scan"
    
    def setup(self):        
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        
        self.single_scan = self.add_logged_quantity("single_scan", dtype=int, 
                                                        ro=True, 
                                                        initial=1, 
                                                        vmin=0, 
                                                        vmax=1, 
                                                        unit='',
                                                        choices=[('Off',0),('On',1)])
        self.save_file = self.add_logged_quantity("save_file", dtype=int, 
                                                        ro=True, 
                                                        initial=1, 
                                                        vmin=0, 
                                                        vmax=1, 
                                                        unit='',
                                                        choices=[('Off',0),('On',1)])
        
        
        self.scanner=self.gui.sem_raster_scanner
        
        
        #connect events
        self.gui.ui.sem_raster_start_pushButton.clicked.connect(self.start)
        self.gui.ui.sem_raster_save_pushButton.clicked.connect(self.save_current_view)
        self.gui.ui.sem_raster_interrupt_pushButton.clicked.connect(self.interrupt)
        
        self.save_file.connect_bidir_to_widget(self.gui.ui.save_file_comboBox)
        
  
    def setup_figure(self):
        self.fig = self.gui.add_figure('main_display', self.gui.ui.sem_raster_plot_widget)

    def _run(self):
        from datetime import datetime
        '''
        connect to the scanner hardware component which set scan parameters
        '''
        if self.scanner.square.val==True:
            self.scanner.lines.update_value(self.scanner.points.val)
        self.scanner.connect()
        

        '''
        image_io contains the classes needed for saving and loading data
        The data is in HDF5 format
        Collection class correspond to one data collection run,
        it create an HDF5 file and Collection.update(dict({'name':data_frame}))
        stores each frames into the HDF5 file
        '''
        
        '''
        Turning on Continuous scan
        '''
        
        '''
        If save file flag is on, start save file routine
        '''
       
            
        
        self.images=ImageData(sync_object=self.scanner.sync_analog_io, 
                              ai_chans=self.scanner.input_channel_addresses.val,
                              ai_names=self.scanner.input_channel_names.val,
                              ctr_chans=self.scanner.counter_channel_addresses.val,
                              ctr_names=self.scanner.counter_channel_names.val,
                              num_pixels=self.scanner.num_pixels,
                              image_shape=self.scanner.raster_gen.shape(),
                              sample_per_point=self.scanner.sample_per_point.val,
                              timeout=self.scanner.timeout.val)
        
        if self.save_file.val==1:
            '''
            ChannelInfo contains the name of channel, and the dimension info,
            it is used in setting up channels during the creating of
            a Collection object
            '''
            image_dimension=(self.scanner.points.val,self.scanner.lines.val)
            ch_infos=[]
            for name in self.images._lookup_table:
                ch_infos.append(ChannelInfo(name,image_dimension))
            t=datetime.now()
            '''
            a file is named by a time stamp
            '''
            tname='data/img'+t.strftime('%Y-%m-%d-%H-%M-%S')
            self.collection=Collection(name=tname,
                                  create=True,
                                  initial_size=1,
                                  expansion_size=1,
                                  channel_infos=ch_infos)
            self.collection.save_measurement_component(self.dict_logged_quantity_val(self.logged_quantities), self.dict_logged_quantity_unit(self.logged_quantities))
            self.sem_remcon=self.gui.sem_remcon
            self.collection.save_hardware_component('sem_remcon', self.dict_logged_quantity_val(self.sem_remcon.logged_quantities), self.dict_logged_quantity_unit(self.sem_remcon.logged_quantities))
            
            
        if self.single_scan.val==1:
            self.scanner.sync_analog_io.out_data(self.scanner.xy_raster_volts)
            self.scanner.sync_analog_io.start()            
            self.images.read_all()
            self.update_display()
            if self.save_file.val==1:
                self.collection.update(self.images._images)

            self.scanner.sync_analog_io.stop()
            self.scanner.sync_analog_io.close()
        self.scanner.disconnect()
        if self.save_file.val==1:
            self.collection.close()
        
    def update_display(self):
        self.fig.load(self.images.get_by_name(self.scanner.main_channel.val))
        for window_name in self.scanner.display_windows:
            current_window=self.scanner.display_windows[window_name]
            current_window.image_view.load(self.images.get_by_name(self.scanner.display_window_channels[window_name].val))
    
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

    def save_current_view(self):
        dialog=QtGui.QFileDialog()
        dialog.setAcceptMode(dialog.AcceptSave)
        
        if dialog.exec_():
            fname=dialog.selectedFiles()[0]
            
            image_dimension=(self.scanner.points.val,self.scanner.lines.val)
            ch_infos=[]
            for name in self.images._lookup_table:
                ch_infos.append(ChannelInfo(name,image_dimension))

            collection=Collection(name=fname,
                                  create=True,
                                  initial_size=1,
                                  expansion_size=1,
                                  channel_infos=ch_infos)
            collection.save_measurement_component(self.dict_logged_quantity_val(self.logged_quantities), self.dict_logged_quantity_unit(self.logged_quantities))
            self.sem_remcon=self.gui.sem_remcon
            collection.save_hardware_component('sem_remcon', self.dict_logged_quantity_val(self.sem_remcon.logged_quantities), self.dict_logged_quantity_unit(self.sem_remcon.logged_quantities))
            collection.update(self.images._images)
            collection.close()
            
# if __name__=='__main__':
#     from base_gui import BaseMicroscopeGUI
#    
#     scan=SemRasterRepScan(gui)
#     resp=scan.get_measurement_logged_quantity()
#     print(resp)