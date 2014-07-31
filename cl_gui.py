'''
Created on Jul 23, 2014

'''

import sys, os
import time
import datetime
import numpy as np
import collections

from PySide import QtCore, QtGui, QtUiTools

import matplotlib
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar2

from matplotlib.figure import Figure

from logged_quantity import LoggedQuantity

from hardware_components.andor_ccd import AndorCCDHardwareComponent
from hardware_components.attocube_xy_stage import AttoCubeXYStage
from hardware_components.sem_detector_analog_input import SEMDetectorHardwareComponent


from measurement_components.andor_ccd_readout import \
                AndorCCDReadout, AndorCCDReadBackground

from measurement_components.atto_sample_scan import AttoSampleScan

class CLMicroscopeGUI(object):
    def __del__ ( self ): 
        self.ui = None

    def show(self): 
        #self.ui.exec_()
        self.ui.show()

    def __init__(self):
        self.logged_quantities = collections.OrderedDict()
        self.hardware_components = collections.OrderedDict()
        self.measurement_components = collections.OrderedDict()
        self.figs = collections.OrderedDict()

        # Load Qt UI from .ui file
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile("cl_gui.ui")
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.ui = ui_loader.load(ui_file)
        ui_file.close()

        # Add hardware components
        print "Adding Hardware Components"
        self.andor_ccd_hc = self.add_hardware_component(AndorCCDHardwareComponent(self))
        self.attocube_xy_stage = self.add_hardware_component(AttoCubeXYStage(self))
        self.sem_detector = self.add_hardware_component(SEMDetectorHardwareComponent(self))

        # Create the measurement objects
        print "Create Measurement objects"
        self.andor_ro_measure = self.add_measurement_component(AndorCCDReadout(self))
        self.andor_bg_measure = self.add_measurement_component(AndorCCDReadBackground(self))
        self.atto_sample_scan = self.add_measurement_component(AttoSampleScan(self))
        # Setup the figures         
        for name, measure in self.measurement_components.items():
            print "setting up figures for", name, "measurement", measure.name
            measure.setup_figure()
        
    def add_figure(self,name, widget):
            """creates a matplotlib figure attaches it to the qwidget specified
            (widget needs to have a layout set (preferably verticalLayout) 
            adds a figure to self.figs"""
            print "---adding figure", name, widget
            if name in self.figs:
                return self.figs[name]
            else:
                fig = Figure()
                fig.patch.set_facecolor('w')
                canvas = FigureCanvas(fig)
                nav    = NavigationToolbar2(canvas, self.ui)
                widget.layout().addWidget(canvas)
                widget.layout().addWidget(nav)
                canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
                canvas.setFocus()
                self.figs[name] = fig
                return fig
    
    def add_logged_quantity(self, name, **kwargs):
        lq = LoggedQuantity(name=name, **kwargs)
        self.logged_quantities[name] = lq
        return lq

    def add_hardware_component(self,hc):
        self.hardware_components[hc.name] = hc
        return hc
    
    def add_measurement_component(self, measure):
        assert not measure.name in self.measurement_components.keys()
        self.measurement_components[measure.name] = measure
        return measure

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("CL Microscope Control Application")
    
    gui = CLMicroscopeGUI()
    gui.show()
    
    sys.exit(app.exec_())