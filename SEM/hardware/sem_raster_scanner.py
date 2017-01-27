'''
Created on Feb 4, 2015

@author: Hao Wu
'''
from hardware_components import HardwareComponent
try:
    from SEM.sem_equipment.raster_generator import RasterGenerator
    from equipment.NI_Daq import NI_SyncTaskSet
    from equipment.NI_CallBack import SyncCallBack
except Exception as err:
    print "could not load modules needed for AttoCubeECC100:", err
from PySide import QtCore, QtGui, QtUiTools
from equipment.image_display import ImageDisplay, ImageWindow, SetWindow


class SemRasterScanner(HardwareComponent):
    
    name = 'sem_raster_scanner'
    ui_filename='image_window.ui'
    
    def setup(self):
        self.display_update_period = 0.050 #seconds

        # Created logged quantities
        self.sync_mode=self.add_logged_quantity('sync_mode',initial='callback',
                                                dtype=str)
        
        self.callback_mode = self.add_logged_quantity("callback_mode", dtype=str, 
                                                    ro=False,
                                                    initial='line',
                                                    choices=[('Slow','line'),('Fast','block')])
        
        self.points = self.add_logged_quantity('points', initial=512,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=1e6,
                                                   unit='pixels')

        self.lines = self.add_logged_quantity('lines', initial=512,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=1,
                                                   vmax=1e6,
                                                   unit='pixels')
        
        self.visible_points = self.add_logged_quantity('visible_points', initial=512,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=14,
                                                   vmax=1e6,
                                                   unit='pixels')
        
        self.visible_lines = self.add_logged_quantity('visible_lines', initial=512,
                                                   dtype=int,
                                                   ro=False,
                                                   vmin=14,
                                                   vmax=1e6,
                                                   unit='pixels')

        self.square=self.add_logged_quantity('square', initial=1,
                                                   dtype=bool,
                                                   ro=False)

        lq_params = dict(  dtype=float, ro=False,
                           initial = 0,
                           vmin=-50,
                           vmax=50,
                           unit='%')
        self.xoffset = self.add_logged_quantity('xoffset', **lq_params)
        self.yoffset = self.add_logged_quantity('yoffset', **lq_params)

        lq_params = dict(  dtype=float, ro=False,
                           initial = 100,
                           vmin=0,
                           vmax=100,
                           unit='%')        
        self.xsize = self.add_logged_quantity("xsize", **lq_params)
        self.ysize = self.add_logged_quantity("ysize", **lq_params)
        
        self.angle = self.add_logged_quantity("angle", dtype=float, ro=False, initial=0, vmin=-180, vmax=180, unit="deg")
        
        self.scan_voltage = self.add_logged_quantity("scan_voltage", dtype=float, 
                                                    ro=False, 
                                                    initial=10.0, 
                                                    vmin=0, 
                                                    vmax=50.0,
                                                    unit='kV')
        
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
        
        
        
        self.ai_addreses=list()
        self.ai1_address=self.add_logged_quantity("ai1_address",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ai1')
        self.ai_addreses.append(self.ai1_address)
        
        self.ai2_address=self.add_logged_quantity("ai2_address",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ai2')
        self.ai_addreses.append(self.ai2_address)
        
        
        
        
        self.ai_names=list()
        self.ai1_name=self.add_logged_quantity("ai1_name",dtype=str,
                                                        ro=False,
                                                        initial='SE')
        self.ai_names.append(self.ai1_name)
        self.ai2_name=self.add_logged_quantity("ai2_name",dtype=str,
                                                        ro=False,
                                                        initial='')
        self.ai_names.append(self.ai2_name)
        
        
        self.input_channel_names= self.add_logged_quantity("input_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='SE')
        
        self.counter_channel_addresses= self.add_logged_quantity("counter_channel_addresses",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ctr0,X-6363/ctr1')
        
        
        self.ctr_addresses=list()
        self.ctr1_address=self.add_logged_quantity("ctr1_address",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ctr0')
        self.ctr_addresses.append(self.ctr1_address)
        
        self.ctr2_address=self.add_logged_quantity("ctr2_address",dtype=str,
                                                        ro=False,
                                                        initial='X-6363/ctr1')
        self.ctr_addresses.append(self.ctr2_address)
        
        
        self.ctr_names=list()
        self.ctr1_name=self.add_logged_quantity("ctr1_name",dtype=str,
                                                        ro=False,
                                                        initial='PMT1')
        self.ctr_names.append(self.ctr1_name)
        
        self.ctr2_name=self.add_logged_quantity("ctr2_name",dtype=str,
                                                        ro=False,
                                                        initial='PMT2')
        self.ctr_names.append(self.ctr2_name)
        
        self.counter_channel_names= self.add_logged_quantity("counter_channel_names",dtype=str,
                                                        ro=False,
                                                        initial='PMT,PMT2')
        
        self.counter_channel_terminals= self.add_logged_quantity("counter_channel_terminals",dtype=str,
                                                        ro=False,
                                                        initial='PFI0,PFI12')
        
        
        self.ctr_terminals=list()
        
        self.ctr1_terminal= self.add_logged_quantity("ctr1_terminal",dtype=str,
                                                        ro=False,
                                                        initial='PFI0')
        self.ctr_terminals.append(self.ctr1_terminal)
        
        self.ctr2_terminal= self.add_logged_quantity("ctr2_terminal",dtype=str,
                                                        ro=False,
                                                        initial='PFI12')
        self.ctr_terminals.append(self.ctr2_terminal)
        
        
        self.counter_unit=self.add_logged_quantity("counter_unite",dtype=str,
                                                        ro=False,
                                                        initial='count',
                                                        choices=[('count','count'),('Hz','Hz')])
        
        self.auto_blanking=self.add_logged_quantity('auto_blanking', initial=1,
                                                   dtype=bool,
                                                   ro=False)
        
        self.generate_choice_list()
        
        self.main_channel = self.add_logged_quantity("main_channel", dtype=str, 
                                                        ro=False, 
                                                        initial=self.name_choices[0][1], 
                                                        choices=self.name_choices)
        
        self.timeout= self.add_logged_quantity("timeout",dtype=float,
                                               ro=False,
                                               initial=999,
                                               vmin=1,
                                               vmax=1e5)
        
        self.remcon=self.app.hardware['sem_remcon']
#         self.display_windows=dict()
#         self.display_window_channels=dict()
#         self.display_windows_counter=0

        #connect events
        if False:
            self.visible_points.connect_bidir_to_widget(self.gui.ui.points_doubleSpinBox)
            self.visible_lines.connect_bidir_to_widget(self.gui.ui.lines_doubleSpinBox)
            self.square.connect_bidir_to_widget(self.gui.ui.square_checkBox)
            self.xoffset.connect_bidir_to_widget(self.gui.ui.xoffset_doubleSpinBox)
            self.yoffset.connect_bidir_to_widget(self.gui.ui.yoffset_doubleSpinBox)
            self.xsize.connect_bidir_to_widget(self.gui.ui.xsize_doubleSpinBox)
            self.ysize.connect_bidir_to_widget(self.gui.ui.ysize_doubleSpinBox)
            self.angle.connect_bidir_to_widget(self.gui.ui.angle_doubleSpinBox)
            self.sample_rate.connect_bidir_to_widget(self.gui.ui.sample_rate_doubleSpinBox)
            self.sample_per_point.connect_bidir_to_widget(self.gui.ui.sample_per_point_doubleSpinBox) 
            self.ms_per_unit.connect_bidir_to_widget(self.gui.ui.ms_per_unit_doubleSpinBox)
            self.unit_of_rate.connect_bidir_to_widget(self.gui.ui.unit_of_rate_comboBox)
            self.counter_unit.connect_bidir_to_widget(self.gui.ui.counter_unit_comboBox)      
            self.auto_blanking.connect_bidir_to_widget(self.gui.ui.auto_blanking_checkBox)
            self.ai1_name.connect_bidir_to_widget(self.gui.ui.ai1_name_lineEdit)
            self.ai2_name.connect_bidir_to_widget(self.gui.ui.ai2_name_lineEdit)
            self.ctr1_name.connect_bidir_to_widget(self.gui.ui.ctr1_name_lineEdit)
            self.ctr2_name.connect_bidir_to_widget(self.gui.ui.ctr2_name_lineEdit)
            self.callback_mode.connect_bidir_to_widget(self.gui.ui.callback_mode_comboBox)
            self.gui.ui.update_channel_pushButton.clicked.connect(self.update_channel)
        
    def connect(self):
        
        #if self.debug_mode.val: print "connecting to {}".format(self.name)
        from SEM.sem_equipment.rate_converter import RateConverter
        
        self.rate_converter=RateConverter(self.points.val,self.lines.val,self.sample_rate.val)
        self.sample_per_point.update_value(self.rate_converter.set_rate(self.ms_per_unit.val,self.unit_of_rate.val))
        
        
        self.scan_voltage.update_value(10.0)
        
        self.raster_gen = RasterGenerator(points=self.points.val, lines=self.lines.val,
                                          xmin=-self.scan_voltage.val, xmax = self.scan_voltage.val, ymin = -self.scan_voltage.val, ymax = self.scan_voltage.val,
                                          xoffset=self.xoffset.val/100.0, yoffset=self.yoffset.val/100.0,
                                          xsize=self.xsize.val, ysize=self.ysize.val,
                                          angle=self.angle.val)
        
        # need to update values based on clipping
        
        self.xy_raster_volts = self.raster_gen.data()
        self.num_pixels = self.raster_gen.count()
        self.num_samples= self.num_pixels *self.sample_per_point.val
        
        #setup tasks
        #while self.continuous_scan.val==1:
        if self.sync_mode.val=='regular':
            self.sync_analog_io = NI_SyncTaskSet(self.output_channel_addresses.val,self.input_channel_addresses.val,self.counter_channel_addresses.val.split(','),self.counter_channel_terminals.val.split(','))
        elif self.sync_mode.val=='callback':
            self.sync_analog_io= SyncCallBack(self.output_channel_addresses.val,self.input_channel_addresses.val,self.counter_channel_addresses.val.split(','),self.counter_channel_terminals.val.split(','))
      
        self.ctr_num=2
        '''
        from sample per point and sample rate, calculate the output(scan rate)
        '''
        self.output_rate.update_value(self.sample_rate.val/self.sample_per_point.val)
        
        self.generate_choice_list()
       
        
        #self.sync_analog_io.setup(rate_out=self.sample_rate.val, count_out=self.num_pixels, 
        #                          rate_in=self.sample_rate.val, count_in=self.num_pixels )
        if self.sync_mode.val=='regular':
            self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.num_samples),is_finite=True)
        else:
            if self.callback_mode.val=='line':
                self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.points.val*self.sample_per_point.val),is_finite=False)
            elif self.callback_mode.val=='block':
                self.sync_analog_io.setup(self.output_rate.val, int(self.num_pixels), self.sample_rate.val, int(self.lines.val*self.points.val*self.sample_per_point.val),is_finite=False)

    def disconnect(self):
        #disconnect logged quantities from hardware
        #for lq in self.logged_quantities.values():
        #    lq.hardware_read_func = None
        #    lq.hardware_set_func = None
        if hasattr(self,"sync_analog_io"):
            del self.sync_analog_io
        #disconnect hardware
        #self.nanodrive.close()
        
        # clean up hardware object
        #del self.nanodrive

#     def open_new_window(self):
# #         ui_loader = QtUiTools.QUiLoader()
# #         ui_file = QtCore.QFile(self.ui_filename)
# #         ui_file.open(QtCore.QFile.ReadOnly); 
# #         self.display_window=QtGui.QWidget()
# #         self.display_window.ui = ui_loader.load(ui_file)
# #         ui_file.close()
# #         self.image_view=ImageDisplay('display window', self.display_window.ui.plot_container)
# #         self.display_window.ui.show()
#         new_title='figure'+str(self.display_windows_counter)
#         self.display_windows[new_title]=ImageWindow(new_title)
#         self.display_window_channels[new_title]=self.add_logged_quantity(new_title, dtype=str, 
#                                                         ro=False, 
#                                                         initial=self.name_choices[0][1], 
#                                                         choices=self.name_choices)
#         self.display_window_channels[new_title].connect_bidir_to_widget(self.display_windows[new_title].ui.channel_comboBox)
#         self.display_windows_counter+=1
#         
#         
#     def open_set_window(self):
# #         ui_loader = QtUiTools.QUiLoader()
# #         ui_file = QtCore.QFile(self.ui_filename)
# #         ui_file.open(QtCore.QFile.ReadOnly); 
# #         self.display_window=QtGui.QWidget()
# #         self.display_window.ui = ui_loader.load(ui_file)
# #         ui_file.close()
# #         self.image_view=ImageDisplay('display window', self.display_window.ui.plot_container)
# #         self.display_window.ui.show()
#         new_title='Set Window'
#         self.set_window=SetWindow(self.gui,new_title)
#         self.set_window_channel=self.add_logged_quantity('set_window',dtype=str, 
#                                                         ro=False, 
#                                                         initial=self.name_choices[0][1], 
#                                                         choices=self.name_choices)
#         self.set_window_channel.connect_bidir_to_widget(self.set_window.ui.channel_comboBox)
#   
    def update_channel(self):
        if self.ai1_name.val=='':
            self.ai1_name.update_value("AI1")
        if self.ai2_name.val=='':
            self.input_channel_names.update_value(self.ai1_name.val)
            # FIXME hard coded device names
            #self.input_channel_addresses.update_value('X-6363/ai1')
            self.sample_rate.update_value(2000000)
        else:
            self.input_channel_names.update_value(self.ai1_name.val+','+self.ai2_name.val)
            # FIXME hard coded device names
            #self.input_channel_addresses.update_value('X-6363/ai1,X-6363/ai2')
            self.sample_rate.update_value(500000)
        
        counter_addresses=''
        counter_names=''
        counter_terminals=''
        
        if self.ctr1_name.val=='':
            self.ctr1_name.update_value("CTR1")
            
        for i in xrange(2):
            if self.ctr_names[i].val!='':
                counter_addresses=counter_addresses+self.ctr_addresses[i].val+','
                counter_names=counter_names+self.ctr_names[i].val+','
                counter_terminals=counter_terminals+self.ctr_terminals[i].val+','
        
        counter_addresses=counter_addresses[:-1]   
        counter_names=counter_names[:-1]
        counter_terminals=counter_terminals[:-1]   
        
        self.counter_channel_addresses.update_value(counter_addresses)
        self.counter_channel_names.update_value(counter_names)
        self.counter_channel_terminals.update_value(counter_terminals)
        
        self.generate_choice_list()
        self.update_choice_list()

    def generate_choice_list(self):
        self.name_choices=list()
        for name in self.input_channel_names.val.split(','):
            self.name_choices.append((name,name))
        for name in self.counter_channel_names.val.split(','):
            self.name_choices.append((name,name))
    
            
    def update_choice_list(self):
        if hasattr(self.gui,'set_window_channel'):
            self.gui.set_window_channel.change_choice_list(self.name_choices)
        if hasattr(self.gui,'display_window_channels'):
            for name in self.gui.display_window_channels:
                self.gui.display_window_channels[name].change_choice_list(self.name_choices)