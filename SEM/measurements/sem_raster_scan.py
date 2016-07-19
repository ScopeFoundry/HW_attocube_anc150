'''
Created on Feb 4, 2015

@author: Hao Wu
'''

from ScopeFoundry import Measurement
import time
from equipment.image_display import ImageData
from PySide import QtGui, QtCore
from equipment.image_io import ChannelInfo
from equipment.image_io import Collection
from SEM.sem_equipment.rate_converter import RateConverter
import os.path
import shutil

class Reporter(QtCore.QObject):
    progress=QtCore.Signal(int)
    done=QtCore.Signal(bool)
    
class ScanCheck(QtCore.QObject):
    progress=QtCore.Signal(int)
    done=QtCore.Signal(bool)
    
    def __init__(self,images,parent,delay=0.10):
        self.completed_channels=0
        self.delay=delay
        self.images=images
        self.parent=parent
        
    def wait(self):
        while self.images.finished==False and self.parent.stop_pushButton.isDown()==False and self.parent.gui.ui.isVisible() and self.parent.gui.ui.actionExit.isChecked()==False and self.parent.gui.ui.actionStop.isChecked()==False:
            self.parent.progress=self.images.progress
            time.sleep(self.delay)



    def stop(self):
        self.images.finished=True

class SemRasterScan(Measurement):

    name = "sem_raster_scan"
    
    def setup(self):        
        self.display_update_period = 0.050 #seconds

        # Created logged quantities

        self.scan_mode = self.add_logged_quantity("scan_mode", dtype=str, 
                                                        ro=False,
                                                        initial='image',
                                                        choices=[('image','image'),('movie','movie')])
        
        
        self.crop_mode = self.add_logged_quantity("crop_mode", dtype=bool, 
                                                    ro=False,
                                                    initial=1)
        
    
        
        self.recovery_time = self.add_logged_quantity("recovery_time", dtype=float, 
                                                    ro=True,
                                                    initial=0.07)
        
        
        self.scanner=self.gui.sem_raster_scanner
        
        self.scan_on=False
        
        if hasattr(self.gui,'sem_remcon'):
            self.sem_remcon=self.gui.sem_remcon
        
        #connect events
        self.gui.ui.sem_raster_start_pushButton.clicked.connect(self.start)
        self.stop_pushButton=self.gui.ui.sem_raster_interrupt_pushButton
        self.gui.ui.sem_raster_save_pushButton.clicked.connect(self.save)
        self.gui.ui.actionSave.triggered.connect(self.save)
        self.gui.ui.actionStart.triggered.connect(self.start)
        self.gui.ui.scan_mode_tabWidget.currentChanged.connect(self.select_scan_mode)
        
        self.progress_reporter=Reporter()
        self.progress_reporter.progress.connect(self.gui.ui.progressBar.setValue)
        #self.save_file.connect_bidir_to_widget(self.gui.ui.save_file_comboBox)
        self.gui.ui.sem_raster_interrupt_pushButton.setEnabled(False)
        self.gui.ui.sem_raster_save_pushButton.setEnabled(False)
        
  
    def setup_figure(self):
        pass
        #self.fig=self.gui.fig
        #self.fig = self.gui.add_figure('main_display', self.gui.ui.sem_raster_plot_widget)

    def _run(self):
        #Connect to RemCon and turn on External Scan for SEM
        self.scanner.update_channel()
        if hasattr(self,"sem_remcon"):
            if self.sem_remcon.connected.val:
                self.sem_remcon.remcon.write_external_scan(1)
        #Check to see if the scan area is set to square, if it is set the lines equal to points
        if self.scanner.square.val==True:
            self.scanner.visible_lines.update_value(self.scanner.visible_points.val)
       
    
        self.setup_scale()
        
        if self.scanner.auto_blanking.val:
            if hasattr(self,"sem_remcon"):
                if self.sem_remcon.connected.val:
                    self.sem_remcon.remcon.write_beam_blanking(0)
                    
        self.gui.ui.sem_raster_interrupt_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_save_pushButton.setEnabled(False)
        self.gui.ui.sem_raster_start_pushButton.setEnabled(False)
        self.gui.ui.actionStop.setChecked(False)
        self.gui.ui.scan_mode_tabWidget.setEnabled(False)
        
        self.rate_converter=RateConverter(self.scanner.points.val,self.scanner.lines.val,self.scanner.sample_rate.val)
        self.scanner.sample_per_point.update_value(self.rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val))
        self.ms_per_frame=self.rate_converter.ms_per_frame
        buff_size=self.scanner.points.val*self.scanner.lines.val*self.scanner.sample_per_point.val
        if buff_size>5.0e7:
            coeff=5.0e7/buff_size
            self.scanner.sample_rate.update_value(coeff*self.scanner.sample_rate.val)
            self.rate_converter=RateConverter(self.scanner.points.val,self.scanner.lines.val,self.scanner.sample_rate.val)
        self.scanner.sample_per_point.update_value(self.rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val))
            
        
        
        try:
            print("scan started")
            if self.scan_mode.val=="image":
                print("Acquiring Image")
                self.scanner.callback_mode.update_value('line')
                mode=self.select_single_scan_mode(self.rate_converter.ms_per_frame)
                self.single_scan(mode)
            elif self.scan_mode.val=="movie":
                print("Acquring Movie")
                self.continous_scan()
            print("scan done")
        except:
            pass
         
        self.gui.ui.sem_raster_start_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_save_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_interrupt_pushButton.setEnabled(False)
        self.gui.ui.scan_mode_tabWidget.setEnabled(True)
        
        self.progress=100
        self.progress_reporter.progress.emit(self.progress)
        self.progress_reporter.done.emit(True)
        if self.scanner.auto_blanking.val:
            if hasattr(self,"sem_remcon"):
                if self.sem_remcon.connected.val:
                    self.sem_remcon.beam_blanking.update_value(1)
        self.scanner.disconnect()
        
        if self.gui.autosave.val:
            self.sem_remcon.EHT.read_from_hardware()
            self.sem_remcon.select_aperture.read_from_hardware()
            self.auto_save()
        self.gui.ui.actionStop.setChecked(False)
        
    def setup_imagedata(self, mode='regular',collection=''):
            self.images=ImageData(sync_object=self.scanner.sync_analog_io, 
                                  ai_chans=self.scanner.input_channel_addresses.val,
                                  ai_names=self.scanner.input_channel_names.val,
                                  ctr_chans=self.scanner.counter_channel_addresses.val,
                                  ctr_names=self.scanner.counter_channel_names.val,
                                  num_pixels=self.scanner.num_pixels,
                                  image_shape=self.scanner.raster_gen.shape(),
                                  sample_per_point=self.scanner.sample_per_point.val,
                                  xpix=self.scanner.points.val,
                                  ypix=self.scanner.lines.val,
                                  xview=self.scanner.visible_points.val,
                                  yview=self.scanner.visible_lines.val,
                                  timeout=self.scanner.timeout.val,
                                  mode=mode,
                                  counter_unit=self.scanner.counter_unit.val,
                                  sample_rate=self.scanner.sample_rate.val,
                                  collection=collection)
        
    def setup_scale(self):
        self.magnification=1000
        if hasattr(self,"sem_remcon"):
            self.sem_remcon.magnification.read_from_hardware()
            self.magnification=float(self.sem_remcon.magnification.val)
        from equipment.SEM.scale_converter import ScaleConverter
        self.scale=ScaleConverter(1.0/1.045)
        self.element_size=[1.0,1.0,1.0]
        self.scale.read_parameters(self.magnification,self.scanner.xsize.val/100.0,self.scanner.ysize.val/100.0,self.scanner.points.val,self.scanner.lines.val)
        self.element_size=[1.0,self.scale.get_pixsize_x()/1000.0,self.scale.get_pixsize_y()/1000.0]
        if self.crop_mode.val:
            self.visible_rate_converter=RateConverter(self.scanner.visible_points.val,self.scanner.visible_lines.val,self.scanner.sample_rate.val)
            numsample=self.visible_rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val)
            pixel_time=self.visible_rate_converter.ms_per_pixel
            added_pixels=int(self.recovery_time.val*self.scanner.xsize.val/100/pixel_time)
            print(added_pixels)
        else:
            added_pixels=0
            
        self.scanner.points.update_value(self.scanner.visible_points.val+added_pixels)
        self.scanner.lines.update_value(self.scanner.visible_lines.val+added_pixels)
            
    def select_single_scan_mode(self,ms_per_frame):
        if ms_per_frame>2000000:
            return "callback"
        else:
            return "regular"
        
        
    def single_scan(self,mode="callback"):
        if mode=="callback":
            self.single_scan_callback()
        else:
            self.single_scan_regular()
    
    def continous_scan(self):
        mode=self.select_single_scan_mode(self.rate_converter.ms_per_frame)
        
        channel_names=self.scanner.input_channel_names.val.split(',')+self.scanner.counter_channel_names.val.split(',')
        image_dimension=(self.scanner.visible_points.val,self.scanner.visible_lines.val)
        ch_infos=[]
        
        for name in channel_names:
            ch_infos.append(ChannelInfo(name,image_dimension))

        if os.path.isfile('current_movie.hdf5'):
            os.remove('current_movie.hdf5')
        
        collection=Collection(name='current_movie',
                                create=True,
                                initial_size=20,
                                expansion_size=20,
                                channel_infos=ch_infos,element_size_um=self.element_size)
        if self.scanner.callback_mode.val=='line':
            while self.gui.ui.sem_raster_interrupt_pushButton.isDown()==False and self.gui.ui.actionExit.isChecked()==False and self.gui.ui.actionStop.isChecked()==False and self.gui.ui.isVisible():
                self.single_scan(mode)
                collection.update(self.images._images)
        elif self.scanner.callback_mode.val=='block':
            self.fast_movie_scan(collection)
        
        collection.close()
        
    def fast_movie_scan(self,collection):
        self.scanner.sync_mode.update_value('callback')
        self.scanner.connect()
        self.setup_imagedata('block_callback',collection=collection)    
        self.scan_check=ScanCheck(self.images,self,delay=0.05)
        self.scanner.sync_analog_io.out_data(self.scanner.xy_raster_volts)
        self.scanner.sync_analog_io.start()            
            
        self.scan_check.wait()
            
        self.scanner.sync_analog_io.stop()
        
        
        self.scanner.sync_analog_io.close()
        self.scan_on=False       
        
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
        self.scan_check=ScanCheck(self.images,self,delay=0.05) 

        self.scan_on=True
        self.scanner.sync_analog_io.out_data(self.scanner.xy_raster_volts)
        
        
            
            
        self.scanner.sync_analog_io.start()            
            
        self.scan_check.wait()
            
        self.scanner.sync_analog_io.stop()
        
        
        self.scanner.sync_analog_io.close()
        self.scan_on=False       
    
    def single_scan_regular(self):
        #connect to SEM scanner module, which calculates the voltage output,
        #create detector channels and creates the scanning task
        self.scanner.sync_mode.update_value('regular')
        self.scanner.connect()
        self.setup_imagedata("regular")
        self.scanner.sync_analog_io.out_data(self.scanner.xy_raster_volts)
        self.scanner.sync_analog_io.start()            
        self.images.read_all()

        self.scanner.sync_analog_io.stop()
        self.scanner.sync_analog_io.close()
        
    def update_display(self):
        #self.fig.load(data=self.images.get_by_name(self.scanner.main_channel.val),scale_size=self.scanner.points.val*0.2,scale_length=self.scale.get_pixsize_x()*self.scanner.points.val*0.2*(1e-9),scale_suffix='m')
        if self.scan_on:
            self.progress_reporter.progress.emit(int(self.progress*100))
   
        for window_name in self.gui.display_windows:
            current_window=self.gui.display_windows[window_name]
            current_window.image_view.load(data=self.images.get_by_name(self.gui.display_window_channels[window_name].val),
                                           scale_size=self.scanner.points.val*0.2,
                                           scale_length=self.scale.get_pixsize_x()*self.scanner.points.val*0.2*(1e-9),
                                           scale_suffix='m')
        
        
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
    
    def save(self):
        dialog=QtGui.QFileDialog()
        dialog.setAcceptMode(dialog.AcceptSave)
        
        if dialog.exec_():
            fname=dialog.selectedFiles()[0]
            
            if fname[-5:]=='.hdf5':
                fname=fname[:-5]
            elif fname[-4:]=='.txt':
                fname=fname[:-4]
                
                
            if os.path.isfile(fname+'.hdf5'):
                msg=QtGui.QMessageBox()
                msg.setText('File name exist, please choose a new file name!')
                msg.exec_()
                return None
            elif os.path.isfile(fname+'.txt'):
                msg=QtGui.QMessageBox()
                msg.setText('File name exist, please choose a new file name!')
                msg.exec_()
                return None
        
        self.save_current(fname)
    
    def save_current(self,fname):
        if self.scan_mode.val=="image":
            self.save_current_view(fname)
        elif self.scan_mode.val=="movie":
            self.save_current_movie(fname)
            
    def save_current_view(self,fname):
        
            
            self.save_meta(fname)
            image_dimension=(self.scanner.visible_points.val,self.scanner.visible_lines.val)
            ch_infos=[]
            for name in self.images._lookup_table:
                ch_infos.append(ChannelInfo(name,image_dimension))

            collection=Collection(name=fname,
                                  create=True,
                                  initial_size=1,
                                  expansion_size=1,
                                  channel_infos=ch_infos,element_size_um=self.element_size)
            
            collection.save_comment(self.comment)
            
            collection.update(self.images._images)
            collection.close()
    
    def save_current_movie(self,fname):
        self.save_meta(fname)
        shutil.copyfile('current_movie.hdf5',fname+'.hdf5')
    
    def save_meta(self,fname):
        self.comment=self.gui.ui.comment_TextEdit.toPlainText()
        with open(fname+'.txt','w') as text_file:
            text_file.write(self.convert_logged_quantity_string(self.sem_remcon.EHT)+'\n')
            text_file.write(self.convert_logged_quantity_string(self.sem_remcon.magnification)+'\n')
            text_file.write('Aperture\t'+self.sem_remcon.select_aperture.choices[self.sem_remcon.select_aperture.val-1][0]+'\n')
            text_file.write('Scan Rate\t'+str(self.scanner.ms_per_unit.val)+' '+str(self.scanner.unit_of_rate.choices[self.scanner.unit_of_rate.val-1][0])+'\n')
            text_file.write('Frame Rate\t'+str(self.ms_per_frame)+'ms'+'\n')
            text_file.write('Dimension\t'+str(self.element_size[1]*self.scanner.visible_points.val)+' by ' + str(self.element_size[2]*self.scanner.visible_lines.val)+'um ('+str(self.scanner.visible_points.val)+'x'+str(self.scanner.visible_lines.val)+' pixels)'+'\n')
            
            text_file.write(self.comment+'\n\n')
            text_file.write('pixel size:\n')
            text_file.write('x\t'+str(self.element_size[1])+'\tum\t'+'y\t'+str(self.element_size[2])+'\tum'+'\n')
            
            text_file.write('\n\n\n\n')

            text_file.write('scanner status:\n\n')
            for name in self.scanner.logged_quantities:
                text_file.write(self.convert_logged_quantity_string(self.scanner.logged_quantities[name])+'\n')
            
            text_file.write('\n\n\n\n')
             
            text_file.write('REMCON status:\n\n')
            for name in self.sem_remcon.logged_quantities:
                text_file.write(self.convert_logged_quantity_string(self.sem_remcon.logged_quantities[name])+'\n')
                
            text_file.write('Comments:\n')
            self.gui.settings_to_xml(fname+'.xml')

    @QtCore.Slot(int)
    def select_scan_mode(self,i):
        if i ==0:
            self.scan_mode.update_value("image")
        elif i==1:
            self.scan_mode.update_value("movie")
        else:
            pass

    def reset_scan(self):
        self.scanner.update_channel()
        if hasattr(self,"sem_remcon"):
            if self.sem_remcon.connected.val:
                self.sem_remcon.remcon.write_external_scan(1)
        #Check to see if the scan area is set to square, if it is set the lines equal to points
        if self.scanner.square.val==True:
            self.scanner.visible_lines.update_value(self.scanner.visible_points.val)
       
    
        self.setup_scale()
        
        if self.scanner.auto_blanking.val:
            if hasattr(self,"sem_remcon"):
                if self.sem_remcon.connected.val:
                    self.sem_remcon.remcon.write_beam_blanking(0)
                    
        self.gui.ui.sem_raster_interrupt_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_save_pushButton.setEnabled(False)
        self.gui.ui.sem_raster_start_pushButton.setEnabled(False)
        self.gui.ui.actionStop.setChecked(False)
        self.gui.ui.scan_mode_tabWidget.setEnabled(False)
        
        self.rate_converter=RateConverter(self.scanner.points.val,self.scanner.lines.val,self.scanner.sample_rate.val)
        self.scanner.sample_per_point.update_value(self.rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val))
        self.ms_per_frame=self.rate_converter.ms_per_frame
        buff_size=self.scanner.points.val*self.scanner.lines.val*self.scanner.sample_per_point.val
        if buff_size>5.0e7:
            coeff=5.0e7/buff_size
            self.scanner.sample_rate.update_value(coeff*self.scanner.sample_rate.val)
            self.rate_converter=RateConverter(self.scanner.points.val,self.scanner.lines.val,self.scanner.sample_rate.val)
        self.scanner.sample_per_point.update_value(self.rate_converter.set_rate(self.scanner.ms_per_unit.val,self.scanner.unit_of_rate.val))
            
        
        
        try:
            print("Acquiring Image")
            self.scanner.callback_mode.update_value('line')
            mode=self.select_single_scan_mode(self.rate_converter.ms_per_frame)
            self.single_scan(mode)
            print("scan done")
        except:
            pass
         
        self.gui.ui.sem_raster_start_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_save_pushButton.setEnabled(True)
        self.gui.ui.sem_raster_interrupt_pushButton.setEnabled(False)
        self.gui.ui.scan_mode_tabWidget.setEnabled(True)
        
        self.progress=100
        self.progress_reporter.progress.emit(self.progress)
        self.progress_reporter.done.emit(True)
        if self.scanner.auto_blanking.val:
            if hasattr(self,"sem_remcon"):
                if self.sem_remcon.connected.val:
                    self.sem_remcon.beam_blanking.update_value(1)
        self.scanner.disconnect()
        
        if self.gui.autosave.val:
            self.sem_remcon.EHT.read_from_hardware()
            self.sem_remcon.select_aperture.read_from_hardware()
            self.auto_save()
        self.gui.ui.actionStop.setChecked(False)
                            
    def auto_save(self):
        fname_header=self.gui.folder.val+'/'+self.gui.filename.val+'_'
        parameter=str(self.sem_remcon.magnification.val)+'X_'+str(self.sem_remcon.EHT.val)+'kV_'+str(self.sem_remcon.select_aperture.choices[self.sem_remcon.select_aperture.val-1][0])+'_'
        number=str(self.gui.filenumber.val)
        if self.gui.parameter_filename.val:
            fname=fname_header+parameter+number
        else:
            fname=fname_header+number
            
        if os.path.isfile(fname+'.hdf5') or os.path.isfile(fname+'.txt') or os.path.isfile(fname+'.xml'):
            self.gui.filenumber.update_value(self.gui.filenumber.val+1)
            self.auto_save()
        else:
            self.save_current(fname)
                
    def convert_logged_quantity_string(self,logged_quantity):
        if logged_quantity.unit==None:
            return logged_quantity.name + '\t'+ str(logged_quantity.val) +'' 
        else:
            return logged_quantity.name + '\t'+ str(logged_quantity.val) +'\t' + logged_quantity.unit

# if __name__=='__main__':
#     from base_gui import BaseMicroscopeGUI
#    
#     scan=SemRasterRepScan(gui)
#     resp=scan.get_measurement_logged_quantity()
#     print(resp)