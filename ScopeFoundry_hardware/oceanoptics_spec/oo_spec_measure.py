import numpy as np
from ScopeFoundry import Measurement

class OOSpecLive(Measurement):

    name = "oo_spec_live"
    
    def setup(self):
        
        self.display_update_period = 0.050 #seconds

        #connect events
        self.gui.ui.oo_spec_acquire_cont_checkBox.stateChanged.connect(self.start_stop)
        
    def setup_figure(self):
        
        self.fig = self.gui.add_figure('oo_spec', self.gui.ui.oo_spec_plot_widget)
        
        ax = self.oo_spec_ax = self.fig.add_subplot(111)
        self.oo_spec_plotline, = ax.plot([1],[1])
        ax.set_xlabel("wavelengths (nm)")
        ax.set_ylabel("Laser Spectrum (counts)")        
        
    def _run(self):
        self.oo_spec = self.gui.oceanoptics_spec_hc.oo_spectrometer
        while not self.interrupt_measurement_called:    
            self.oo_spec.acquire_spectrum()
        
    
    def update_display(self):
        ax = self.oo_spec_ax
        self.oo_spec.spectrum[:10]=np.nan
        self.oo_spec.spectrum[-10:]=np.nan
        self.oo_spec_plotline.set_data(
                                   self.oo_spec.wavelengths,
                                   self.oo_spec.spectrum)
        ax.relim()
        ax.autoscale_view(scalex=True, scaley=True)
        self.fig.canvas.draw()       
