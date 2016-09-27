from ScopeFoundry import Measurement, h5_io
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pyqtgraph as pg
import numpy as np

class PLImgLineScan(Measurement):
    
    name = "pl_img_linescan"
    
    hardware_requirements = ['attocube_xy_stage']
    hardware_optional = ['picoharp', 'apd']
    measurement_requirements = []
    
    def setup(self):
        
        kwargs = dict(dtype=float, vmin=-1e6, vmax=1e6, unit='nm')
        
        S = self.settings
        S.New('x0', **kwargs)
        S.New('x1', **kwargs)
        S.New('y0', **kwargs)
        S.New('y1', **kwargs)
        
        S.New('n_steps', dtype=int, vmin=1, initial=10)
        
        S.New('retrace', dtype=bool, initial=True)

        S.New('collect_apd', dtype=bool)
        S.New('collect_spectrum', dtype=bool)
        S.New('collect_lifetime', dtype=bool)
        
        
        # UI 
        self.ui_filename = sibling_path(__file__,"pl_img_linescan.ui")
        self.ui = load_qt_ui_file(self.ui_filename)
        self.ui.setWindowTitle(self.name)
        
        # UI event connections
        S.x0.connect_bidir_to_widget(self.ui.x0_doubleSpinBox)
        S.x1.connect_bidir_to_widget(self.ui.x1_doubleSpinBox)
        S.y0.connect_bidir_to_widget(self.ui.y0_doubleSpinBox)
        S.y1.connect_bidir_to_widget(self.ui.y1_doubleSpinBox)
        
        S.n_steps.connect_bidir_to_widget(self.ui.n_steps_doubleSpinBox)
        
        S.retrace.connect_bidir_to_widget(self.ui.retrace_checkBox)
        
        S.collect_apd.connect_bidir_to_widget(self.ui.collect_apd_checkBox)
        S.collect_spectrum.connect_bidir_to_widget(self.ui.collect_spectrum_checkBox)
        S.collect_lifetime.connect_bidir_to_widget(self.ui.collect_lifetime_checkBox)

        S.progress.connect_bidir_to_widget(self.ui.progressBar)

        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)
        
    def pre_run(self):
        S = self.settings
        # create arrays
        self.x_array = np.linspace(S['x0'], S['x1'], S['n_steps'])
        self.y_array = np.linspace(S['y0'], S['y1'], S['n_steps'])
        
        if S['retrace']:
            self.x_array = np.concatenate([self.x_array,self.x_array[::-1]])
            self.y_array = np.concatenate([self.y_array,self.y_array[::-1]])
        
        self.N = len(self.x_array)    
            
        self.stage = self.app.hardware['attocube_xy_stage']
        
        # data file
        self.h5file = h5_io.h5_base_file(self.app, measurement=self)
        H = self.h5measure = h5_io.h5_create_measurement_group(measurement=self, 
                                                               h5group=self.h5file, 
                                                               group_name=self.name)
        
        # Create acquisition arrays
        if S['collect_apd']:
            self.apd_counter = self.app.hardware.apd_counter
            self.apd_countrates = H.create_dataset('apd_countrates', self.N, dtype=float) # 'apd_countrate'
        if S['collect_spectrum']:
            self.spectra = H.create_dataset('spectra', (self.N, ccd_Nx), dtype=float) # 'apd_countrate'
        if S['collect_lifetime']:
            self.picoharp = self.app.hardware.picoharp
            self.time_traces = H.create_dataset('time_traces', 
                                                (self.N, self.picoharp.settings['histogram_channels']),
                                                dtype=int)
        
        


    def run(self):
        S = self.settings
        try:
            for ii in range(len(self.x_array)):
                if self.interrupt_measurement_called:
                    break
                x = self.x_array[ii]
                y = self.y_array[ii]
                
                # Move attocube stage to position
                self.stage.settings['x_target_position'] = x
                self.stage.settings['y_target_position'] = y
                
                # collect data from detectors
                if S['collect_apd']:
                    apd_count = self.apd_counter.settings.apd_count_rate.read_from_hardware()
                    self.apd_countrates[ii] = apd_count
                if S['collect_spectrum']:
                    pass
                if S['collect_lifetime']:
                    pass
                
                
        finally:
            # save data
            pass
    
    def post_run(self):
        pass

    def setup_figure(self):
        
        
        #self.clear_qt_attr('graph_layout')
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)


    def update_display(self):
        pass